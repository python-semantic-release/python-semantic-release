from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path, PurePosixPath
from re import compile as regexp
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import tomlkit
from git import Actor
from pydantic import RootModel, ValidationError
from urllib3.util.url import parse_url

import semantic_release
from semantic_release.cli.config import (
    BranchConfig,
    ChangelogConfig,
    ChangelogOutputFormat,
    GlobalCommandLineOptions,
    HvcsClient,
    RawConfig,
    RuntimeContext,
    _known_hvcs,
)
from semantic_release.cli.util import load_raw_config_file
from semantic_release.commit_parser.conventional import ConventionalCommitParserOptions
from semantic_release.commit_parser.emoji import EmojiParserOptions
from semantic_release.commit_parser.scipy import ScipyParserOptions
from semantic_release.commit_parser.tag import TagParserOptions
from semantic_release.const import DEFAULT_COMMIT_AUTHOR
from semantic_release.enums import LevelBump
from semantic_release.errors import ParserLoadError

from tests.util import (
    CustomParserOpts,
    CustomParserWithNoOpts,
    CustomParserWithOpts,
    IncompleteCustomParser,
)

if TYPE_CHECKING:
    from typing import Any

    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuildRepoFn, BuiltRepoResult, CommitConvention


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
            RootModel(ConventionalCommitParserOptions()).model_dump(),
        ),  # default not provided -> means conventional
        ("conventional", RootModel(ConventionalCommitParserOptions()).model_dump()),
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
            "commit_parser": "conventional",
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
def test_commit_author_configurable(
    mock_env: dict[str, str],
    expected_author: str,
):
    with mock.patch.dict(os.environ, mock_env):
        raw = RawConfig.model_validate({})
        resulting_author = f"{raw.commit_author.name} <{raw.commit_author.email}>"
        assert expected_author == resulting_author


def test_commit_author_accepts_actor_instance():
    author = Actor(name="Foo Bar", email="foo@bar.com")
    raw = RawConfig(commit_author=author)
    assert author.name == raw.commit_author.name
    assert author.email == raw.commit_author.email


def test_commit_author_valid_dict_input():
    expected_name = "Foo Bar"
    expected_email = "foo@bar.com"
    raw = RawConfig.model_validate(
        {"commit_author": {"name": expected_name, "email": expected_email}}
    )
    assert expected_name == raw.commit_author.name
    assert expected_email == raw.commit_author.email


@pytest.mark.parametrize(
    "commit_author_str, expected_name, expected_email",
    [
        ("Foo Bar <foo@bar.com>", "Foo Bar", "foo@bar.com"),
        ("FooBar<foo@bar.com>", "FooBar", "foo@bar.com"),
        # only the first line of a multiline value is parsed
        ("Foo Bar <foo@bar.com>\nnot-part-of-the-author", "Foo Bar", "foo@bar.com"),
    ],
)
def test_commit_author_valid_string_formats(
    commit_author_str: str, expected_name: str, expected_email: str
):
    raw = RawConfig.model_validate({"commit_author": commit_author_str})
    assert expected_name == raw.commit_author.name
    assert expected_email == raw.commit_author.email


@pytest.mark.parametrize(
    "commit_author_dict, mock_env, expected_author",
    [
        (
            {"env": "PSR_TEST_COMMIT_AUTHOR_ENV"},
            {"PSR_TEST_COMMIT_AUTHOR_ENV": "Env Name <env@example.com>"},
            "Env Name <env@example.com>",
        ),
        (
            {
                "env": "PSR_TEST_COMMIT_AUTHOR_ENV",
                "default": "Default Name <default@example.com>",
            },
            {},
            "Default Name <default@example.com>",
        ),
        (
            {
                "env": "PSR_TEST_COMMIT_AUTHOR_ENV",
                "default_env": "PSR_TEST_COMMIT_AUTHOR_FALLBACK_ENV",
            },
            {
                "PSR_TEST_COMMIT_AUTHOR_FALLBACK_ENV": (
                    "Fallback Name <fallback@example.com>"
                )
            },
            "Fallback Name <fallback@example.com>",
        ),
    ],
)
def test_commit_author_resolves_env_config_var(
    commit_author_dict: dict[str, str],
    mock_env: dict[str, str],
    expected_author: str,
):
    with mock.patch.dict(os.environ, mock_env, clear=True):
        raw = RawConfig.model_validate({"commit_author": commit_author_dict})

    resulting_author = f"{raw.commit_author.name} <{raw.commit_author.email}>"
    assert expected_author == resulting_author


def test_commit_author_env_config_var_resolves_to_none_raises_type_error():
    # nested "with" kept separate for py38 compatibility (no parenthesized context managers)
    with mock.patch.dict(os.environ, {}, clear=True):  # noqa: SIM117
        with pytest.raises(TypeError, match="Invalid type for commit_author"):
            RawConfig.model_validate(
                {"commit_author": {"env": "PSR_TEST_COMMIT_AUTHOR_UNSET_ENV"}}
            )


@pytest.mark.parametrize("commit_author_dict", [{"env": 123}])
def test_commit_author_invalid_env_config_var(commit_author_dict: dict[str, int]):
    with pytest.raises(ValidationError, match="commit_author.env"):
        RawConfig.model_validate({"commit_author": commit_author_dict})


@pytest.mark.parametrize(
    "commit_author_dict, expected_err_msg",
    [
        (
            {"name": "Foo Bar"},
            "commit_author dict must contain 'name' and 'email' keys.",
        ),
        (
            {"email": "foo@bar.com"},
            "commit_author dict must contain 'name' and 'email' keys.",
        ),
        (
            {"name": 123, "email": "foo@bar.com"},
            "commit_author 'name' and 'email' must be strings.",
        ),
        (
            {"name": "  ", "email": "foo@bar.com"},
            "commit_author 'name' and 'email' cannot be empty.",
        ),
    ],
)
def test_commit_author_invalid_dict_input(
    commit_author_dict: dict[str, Any], expected_err_msg: str
):
    with pytest.raises(ValidationError, match=expected_err_msg):
        RawConfig.model_validate({"commit_author": commit_author_dict})


@pytest.mark.parametrize(
    "commit_author_str, expected_err_msg",
    [
        ("", "commit_author string cannot be empty."),
        ("   ", "commit_author string cannot be empty."),
        (
            "NoAngleBracketsHere",
            "commit_author string must be in the format 'Name <email>'.",
        ),
        (
            "<foo@bar.com>",
            "commit_author string must be in the format 'Name <email>'.",
        ),
        (
            "Foo Bar <>",
            "commit_author string must be in the format 'Name <email>'.",
        ),
    ],
)
def test_commit_author_invalid_string_input(
    commit_author_str: str, expected_err_msg: str
):
    with pytest.raises(ValidationError, match=expected_err_msg):
        RawConfig.model_validate({"commit_author": commit_author_str})


@pytest.mark.parametrize(
    "commit_author_val", [123, 12.3, ["Foo Bar", "foo@bar.com"], None]
)
def test_commit_author_invalid_type_input(commit_author_val: Any):
    # TypeError is not a pydantic-recognized validation exception, so it is not
    # wrapped into a ValidationError like the other invalid input cases above
    with pytest.raises(TypeError, match="Invalid type for commit_author"):
        RawConfig.model_validate({"commit_author": commit_author_val})


def test_commit_author_serialization():
    name_email_str = "Foo Bar <foo@bar.com>"
    raw = RawConfig.model_validate({"commit_author": name_email_str})
    serialized_author = raw.model_dump(mode="json").get("commit_author")
    assert name_email_str == serialized_author


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
        # Module:Class string
        f"{CustomParserWithNoOpts.__module__}:{CustomParserWithNoOpts.__name__}",
        f"{CustomParserWithOpts.__module__}:{CustomParserWithOpts.__name__}",
        # File path module:Class string
        f"{CustomParserWithNoOpts.__module__.replace('.', '/')}.py:{CustomParserWithNoOpts.__name__}",
        f"{CustomParserWithOpts.__module__.replace('.', '/')}.py:{CustomParserWithOpts.__name__}",
    ],
)
def test_load_valid_runtime_config_w_custom_parser(
    commit_parser: CommitConvention,
    build_configured_base_repo: BuildRepoFn,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    change_to_ex_proj_dir: None,
    request: pytest.FixtureRequest,
):
    fake_sys_modules = {**sys.modules}

    if ".py" in commit_parser:
        module_filepath = Path(commit_parser.split(":")[0])
        module_filepath.parent.mkdir(parents=True, exist_ok=True)
        module_filepath.parent.joinpath("__init__.py").touch()
        shutil.copy(
            src=str(request.config.rootpath / module_filepath),
            dst=str(module_filepath),
        )
        fake_sys_modules.pop(
            str(Path(module_filepath).with_suffix("")).replace(os.sep, ".")
        )

    build_configured_base_repo(
        example_project_dir,
        commit_type=commit_parser,
    )

    with mock.patch.dict(sys.modules, fake_sys_modules, clear=True):
        assert RuntimeContext.from_raw_config(
            RawConfig.model_validate(load_raw_config_file(example_pyproject_toml)),
            global_cli_options=GlobalCommandLineOptions(),
        )


@pytest.mark.parametrize(
    "commit_parser",
    [
        # Non-existant module
        "tests.missing_module:CustomParser",
        # Non-existant class
        f"{CustomParserWithOpts.__module__}:MissingCustomParser",
        # Incomplete class implementation
        f"{IncompleteCustomParser.__module__}:{IncompleteCustomParser.__name__}",
        # Non-existant module file
        "tests/missing_module.py:CustomParser",
        # Non-existant class in module file
        f"{CustomParserWithOpts.__module__.replace('.', '/')}.py:MissingCustomParser",
        # Incomplete class implementation in module file
        f"{IncompleteCustomParser.__module__.replace('.', '/')}.py:{IncompleteCustomParser.__name__}",
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
    "valid_patterns",
    [
        # Single entry
        [r"chore(?:\([^)]*?\))?: .+"],
        # Multiple entries
        [r"^\d+\.\d+\.\d+", r"Initial [Cc]ommit.*"],
    ],
)
def test_changelog_config_with_valid_exclude_commit_patterns(valid_patterns: list[str]):
    assert ChangelogConfig.model_validate(
        {
            "exclude_commit_patterns": valid_patterns,
        }
    )


@pytest.mark.parametrize(
    "invalid_patterns, index_of_invalid_pattern",
    [
        # Single entry, single incorrect
        (["*abc"], 0),
        # Two entries, second incorrect
        ([".*", "[a-z"], 1),
        # Two entries, first incorrect
        (["(.+", ".*"], 0),
    ],
)
def test_changelog_config_with_invalid_exclude_commit_patterns(
    invalid_patterns: list[str],
    index_of_invalid_pattern: int,
):
    with pytest.raises(
        ValidationError,
        match=regexp(
            str.join(
                "",
                [
                    r".*\bexclude_commit_patterns\[",
                    str(index_of_invalid_pattern),
                    r"\]: Invalid regular expression",
                ],
            ),
        ),
    ):
        ChangelogConfig.model_validate(
            {
                "exclude_commit_patterns": invalid_patterns,
            }
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


@pytest.mark.parametrize(
    "hvcs_type",
    [k.value for k in _known_hvcs],
)
def test_git_remote_url_w_insteadof_alias(
    repo_w_initial_commit: BuiltRepoResult,
    example_pyproject_toml: Path,
    example_git_https_url: str,
    hvcs_type: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    expected_url = parse_url(example_git_https_url)
    repo_name_suffix = PurePosixPath(expected_url.path or "").name
    insteadof_alias = "psr_test_insteadof"
    insteadof_value = expected_url.url.replace(repo_name_suffix, "")
    repo = repo_w_initial_commit["repo"]

    with repo.config_writer() as cfg:
        # Setup: define the insteadOf replacement value
        cfg.add_value(f'url "{insteadof_value}"', "insteadof", f"{insteadof_alias}:")

        # Setup: set the remote URL with an insteadOf alias
        cfg.set_value('remote "origin"', "url", f"{insteadof_alias}:{repo_name_suffix}")

    # Setup: set each supported HVCS client type
    update_pyproject_toml("tool.semantic_release.remote.type", hvcs_type)

    # Act: load the configuration (in clear environment)
    with mock.patch.dict(os.environ, {}, clear=True):
        # Essentially the same as CliContextObj._init_runtime_ctx()
        project_config = tomlkit.loads(
            example_pyproject_toml.read_text(encoding="utf-8")
        ).unwrap()

        runtime = RuntimeContext.from_raw_config(
            raw=RawConfig.model_validate(
                project_config.get("tool", {}).get("semantic_release", {}),
            ),
            global_cli_options=GlobalCommandLineOptions(),
        )

        # Trigger a function that calls helpers.parse_git_url()
        actual_url = runtime.hvcs_client.remote_url(use_token=False)

    # Evaluate: the remote URL should be the full URL
    assert expected_url.url == actual_url
