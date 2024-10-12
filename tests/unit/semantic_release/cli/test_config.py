from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import tomlkit
from pydantic import RootModel, ValidationError

import semantic_release
from semantic_release.cli.config import (
    BranchConfig,
    ChangelogConfig,
    ChangelogOutputFormat,
    GlobalCommandLineOptions,
    HvcsClient,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.util import load_raw_config_file
from semantic_release.commit_parser.angular import AngularParserOptions
from semantic_release.commit_parser.emoji import EmojiParserOptions
from semantic_release.commit_parser.scipy import ScipyParserOptions
from semantic_release.commit_parser.tag import TagParserOptions
from semantic_release.const import DEFAULT_COMMIT_AUTHOR
from semantic_release.enums import LevelBump
from semantic_release.errors import ParserLoadError

from tests.fixtures.repos import repo_with_no_tags_angular_commits
from tests.util import (
    CustomParserOpts,
    CustomParserWithNoOpts,
    CustomParserWithOpts,
    IncompleteCustomParser,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuildRepoFn


@pytest.mark.parametrize(
    "patched_os_environ, remote_config, expected_token",
    [
        (
            {"GH_TOKEN": "mytoken"},
            {"type": HvcsClient.GITHUB.value},
            "mytoken",
        ),
        (
            {"GITLAB_TOKEN": "mytoken"},
            {"type": HvcsClient.GITLAB.value},
            "mytoken",
        ),
        (
            {"GITEA_TOKEN": "mytoken"},
            {"type": HvcsClient.GITEA.value},
            "mytoken",
        ),
        (
            # default not provided -> means Github
            {"GH_TOKEN": "mytoken"},
            {},
            "mytoken",
        ),
        (
            {"CUSTOM_TOKEN": "mytoken"},
            {"type": HvcsClient.GITHUB.value, "token": {"env": "CUSTOM_TOKEN"}},
            "mytoken",
        ),
    ],
)
def test_load_hvcs_default_token(
    patched_os_environ: dict[str, str],
    remote_config: dict[str, Any],
    expected_token: str,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        raw_config = RawConfig.model_validate(
            {
                "remote": remote_config,
            }
        )

    assert expected_token == raw_config.remote.token


@pytest.mark.parametrize("remote_config", [{"type": "nonexistent"}])
def test_invalid_hvcs_type(remote_config: dict[str, Any]):
    with pytest.raises(ValidationError) as excinfo:
        RawConfig.model_validate(
            {
                "remote": remote_config,
            }
        )
    assert "remote.type" in str(excinfo.value)


@pytest.mark.parametrize(
    "commit_parser, expected_parser_opts",
    [
        (
            None,
            RootModel(AngularParserOptions()).model_dump(),
        ),  # default not provided -> means angular
        ("angular", RootModel(AngularParserOptions()).model_dump()),
        ("emoji", RootModel(EmojiParserOptions()).model_dump()),
        ("scipy", RootModel(ScipyParserOptions()).model_dump()),
        ("tag", RootModel(TagParserOptions()).model_dump()),
        (f"{CustomParserWithNoOpts.__module__}:{CustomParserWithNoOpts.__name__}", {}),
        (
            f"{CustomParserWithOpts.__module__}:{CustomParserWithOpts.__name__}",
            RootModel(CustomParserOpts()).model_dump(),
        ),
    ],
)
def test_load_default_parser_opts(
    commit_parser: str | None, expected_parser_opts: dict[str, Any]
):
    raw_config = RawConfig.model_validate(
        # Since TOML does not support NoneTypes, we need to not include the key
        {"commit_parser": commit_parser} if commit_parser else {}
    )
    assert expected_parser_opts == raw_config.commit_parser_options


def test_load_user_defined_parser_opts():
    user_defined_opts = {
        "allowed_tags": ["foo", "bar", "baz"],
        "minor_tags": ["bar"],
        "patch_tags": ["baz"],
        "default_bump_level": LevelBump.PATCH.value,
    }
    raw_config = RawConfig.model_validate(
        {
            "commit_parser": "angular",
            "commit_parser_options": user_defined_opts,
        }
    )
    assert user_defined_opts == raw_config.commit_parser_options


@pytest.mark.parametrize("commit_parser", [""])
def test_invalid_commit_parser_value(commit_parser: str):
    with pytest.raises(ValidationError) as excinfo:
        RawConfig.model_validate(
            {
                "commit_parser": commit_parser,
            }
        )
    assert "commit_parser" in str(excinfo.value)


def test_default_toml_config_valid(example_project_dir: ExProjectDir):
    default_config_file = example_project_dir / "default.toml"

    default_config_file.write_text(
        tomlkit.dumps(RawConfig().model_dump(mode="json", exclude_none=True))
    )

    written = default_config_file.read_text(encoding="utf-8")
    loaded = tomlkit.loads(written).unwrap()
    # Check that we can load it correctly
    parsed = RawConfig.model_validate(loaded)
    assert parsed
    # Check the re-loaded internal representation is sufficient
    # There is an issue with BaseModel.__eq__ that means
    # comparing directly doesn't work with parsed.dict(); this
    # is because of how tomlkit parsed toml


@pytest.mark.parametrize(
    "mock_env, expected_author",
    [
        ({}, DEFAULT_COMMIT_AUTHOR),
        ({"GIT_COMMIT_AUTHOR": "foo <foo>"}, "foo <foo>"),
    ],
)
@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_commit_author_configurable(
    example_pyproject_toml: Path,
    mock_env: dict[str, str],
    expected_author: str,
    change_to_ex_proj_dir: None,
):
    content = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8")).unwrap()

    with mock.patch.dict(os.environ, mock_env):
        raw = RawConfig.model_validate(content)
        runtime = RuntimeContext.from_raw_config(
            raw=raw,
            global_cli_options=GlobalCommandLineOptions(),
        )
        resulting_author = (
            f"{runtime.commit_author.name} <{runtime.commit_author.email}>"
        )
        assert expected_author == resulting_author


def test_load_valid_runtime_config(
    build_configured_base_repo: BuildRepoFn,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    change_to_ex_proj_dir: None,
):
    build_configured_base_repo(example_project_dir)

    # Wipe out any existing configuration options
    update_pyproject_toml(f"tool.{semantic_release.__name__}", {})

    runtime_ctx = RuntimeContext.from_raw_config(
        RawConfig.model_validate(load_raw_config_file(example_pyproject_toml)),
        global_cli_options=GlobalCommandLineOptions(),
    )

    # TODO: add more validation
    assert runtime_ctx


@pytest.mark.parametrize(
    "commit_parser",
    [
        f"{CustomParserWithNoOpts.__module__}:{CustomParserWithNoOpts.__name__}",
        f"{CustomParserWithOpts.__module__}:{CustomParserWithOpts.__name__}",
    ],
)
def test_load_valid_runtime_config_w_custom_parser(
    commit_parser: str,
    build_configured_base_repo: BuildRepoFn,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    change_to_ex_proj_dir: None,
):
    build_configured_base_repo(
        example_project_dir,
        commit_type=commit_parser,
    )

    runtime_ctx = RuntimeContext.from_raw_config(
        RawConfig.model_validate(load_raw_config_file(example_pyproject_toml)),
        global_cli_options=GlobalCommandLineOptions(),
    )
    assert runtime_ctx


@pytest.mark.parametrize(
    "commit_parser",
    [
        # Non-existant module
        "tests.missing_module:CustomParser",
        # Non-existant class
        f"{CustomParserWithOpts.__module__}:MissingCustomParser",
        # Incomplete class implementation
        f"{IncompleteCustomParser.__module__}:{IncompleteCustomParser.__name__}",
    ],
)
def test_load_invalid_custom_parser(
    commit_parser: str,
    build_configured_base_repo: BuildRepoFn,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
    change_to_ex_proj_dir: None,
):
    build_configured_base_repo(example_project_dir)

    # Wipe out any existing configuration options
    update_pyproject_toml(f"{pyproject_toml_config_option_parser}_options", {})

    # Insert invalid custom parser string into configuration
    update_pyproject_toml(pyproject_toml_config_option_parser, commit_parser)

    with pytest.raises(ParserLoadError):
        RuntimeContext.from_raw_config(
            RawConfig.model_validate(load_raw_config_file(example_pyproject_toml)),
            global_cli_options=GlobalCommandLineOptions(),
        )


def test_branch_config_with_plain_wildcard():
    branch_config = BranchConfig(
        match="*",
    )
    assert branch_config.match == ".*"


@pytest.mark.parametrize(
    "invalid_regex",
    [
        "*abc",
        "[a-z",
        "(.+",
        "{2,3}",
        "a{3,2}",
    ],
)
def test_branch_config_with_invalid_regex(invalid_regex: str):
    with pytest.raises(ValidationError):
        BranchConfig(
            match=invalid_regex,
        )


@pytest.mark.parametrize(
    "output_format, insertion_flag",
    [
        (
            ChangelogOutputFormat.MARKDOWN.value,
            "<!-- version list -->",
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT.value,
            f"..{os.linesep}    version list",
        ),
    ],
)
def test_changelog_config_default_insertion_flag(
    output_format: str,
    insertion_flag: str,
):
    changelog_config = ChangelogConfig.model_validate(
        {
            "default_templates": {
                "output_format": output_format,
            }
        }
    )

    assert changelog_config.insertion_flag == insertion_flag
