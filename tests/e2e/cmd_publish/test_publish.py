from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main
from semantic_release.hvcs import Github

from tests.const import MAIN_PROG_NAME, PUBLISH_SUBCMD
from tests.fixtures.repos import repo_w_trunk_only_conventional_commits
from tests.util import assert_exit_code, assert_successful_exit_code

if TYPE_CHECKING:
    from typing import Sequence

    from click.testing import CliRunner

    from tests.fixtures.git_repo import BuiltRepoResult, GetVersionsFromRepoBuildDefFn


@pytest.mark.parametrize("cmd_args", [(), ("--tag", "latest")])
@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_publish_latest_uses_latest_tag(
    repo_result: BuiltRepoResult,
    cli_runner: CliRunner,
    cmd_args: Sequence[str],
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    latest_version = get_versions_from_repo_build_def(repo_result["definition"])[-1]
    latest_tag = f"v{latest_version}"

    with mock.patch.object(
        Github,
        Github.upload_dists.__name__,
    ) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, *cmd_args]

        # Act
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        mocked_upload_dists.assert_called_once_with(tag=latest_tag, dist_glob="dist/*")


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_publish_to_tag_uses_tag(
    repo_result: BuiltRepoResult,
    cli_runner: CliRunner,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    # Testing a non-latest tag to distinguish from test_publish_latest_uses_latest_tag()
    previous_version = get_versions_from_repo_build_def(repo_result["definition"])[-2]
    previous_tag = f"v{previous_version}"

    with mock.patch.object(Github, Github.upload_dists.__name__) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", previous_tag]

        # Act
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        mocked_upload_dists.assert_called_once_with(
            tag=previous_tag, dist_glob="dist/*"
        )


@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_publish_fails_on_nonexistant_tag(cli_runner: CliRunner):
    non_existant_tag = "nonexistant-tag"

    with mock.patch.object(Github, Github.upload_dists.__name__) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", non_existant_tag]

        # Act
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_exit_code(1, result, cli_cmd)
        assert (
            f"Tag '{non_existant_tag}' not found in local repository!" in result.stderr
        )
        mocked_upload_dists.assert_not_called()
