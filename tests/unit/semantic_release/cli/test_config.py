from unittest import mock

import pytest
import tomlkit

from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.const import DEFAULT_COMMIT_AUTHOR


def test_default_toml_config_valid(example_project):
    default_config_file = example_project / "default.toml"
    default_config_file.write_text(tomlkit.dumps(RawConfig().dict(exclude_none=True)))

    written = default_config_file.read_text(encoding="utf-8")
    loaded = tomlkit.loads(written)
    # Check that we can load it correctly
    parsed = RawConfig.parse_obj(loaded)
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
    example_project, repo_with_no_tags_angular_commits, mock_env, expected_author
):
    pyproject_toml = example_project / "pyproject.toml"
    content = tomlkit.loads(pyproject_toml.read_text(encoding="utf-8"))

    with mock.patch.dict("os.environ", mock_env) as patched_env:
        raw = RawConfig.parse_obj(content)
        runtime = RuntimeContext.from_raw_config(
            raw=raw,
            repo=repo_with_no_tags_angular_commits,
            global_cli_options=GlobalCommandLineOptions(),
        )
        assert (
            f"{runtime.commit_author.name} <{runtime.commit_author.email}>"
            == expected_author
        )
