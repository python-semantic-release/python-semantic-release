from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
import tomlkit
from pydantic import RootModel, ValidationError

from semantic_release.cli.config import (
    EnvConfigVar,
    GlobalCommandLineOptions,
    HvcsClient,
    RawConfig,
    RuntimeContext,
)
from semantic_release.commit_parser.angular import AngularParserOptions
from semantic_release.commit_parser.emoji import EmojiParserOptions
from semantic_release.commit_parser.scipy import ScipyParserOptions
from semantic_release.commit_parser.tag import TagParserOptions
from semantic_release.const import DEFAULT_COMMIT_AUTHOR
from semantic_release.enums import LevelBump

from tests.util import CustomParserOpts

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

    from git import Repo

    from tests.fixtures.example_project import ExProjectDir


@pytest.mark.parametrize(
    "remote_config, expected_token",
    [
        ({"type": HvcsClient.GITHUB.value}, EnvConfigVar(env="GH_TOKEN")),
        ({"type": HvcsClient.GITLAB.value}, EnvConfigVar(env="GITLAB_TOKEN")),
        ({"type": HvcsClient.GITEA.value}, EnvConfigVar(env="GITEA_TOKEN")),
        ({}, EnvConfigVar(env="GH_TOKEN")),  # default not provided -> means Github
        (
            {"type": HvcsClient.GITHUB.value, "token": {"env": "CUSTOM_TOKEN"}},
            EnvConfigVar(env="CUSTOM_TOKEN"),
        ),
    ],
)
def test_load_hvcs_default_token(
    remote_config: dict[str, Any], expected_token: EnvConfigVar
):
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
        ("tests.util:CustomParserWithNoOpts", {}),
        ("tests.util:CustomParserWithOpts", RootModel(CustomParserOpts()).model_dump()),
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
def test_commit_author_configurable(
    example_pyproject_toml: Path,
    repo_with_no_tags_angular_commits: Repo,
    mock_env: dict[str, str],
    expected_author: str,
):
    content = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8")).unwrap()

    with mock.patch.dict("os.environ", mock_env):
        raw = RawConfig.model_validate(content)
        runtime = RuntimeContext.from_raw_config(
            raw=raw,
            repo=repo_with_no_tags_angular_commits,
            global_cli_options=GlobalCommandLineOptions(),
        )
        assert (
            f"{runtime.commit_author.name} <{runtime.commit_author.email}>"
            == expected_author
        )
