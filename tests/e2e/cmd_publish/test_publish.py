from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from semantic_release.cli.commands.main import main
from semantic_release.hvcs import Github

from tests.const import MAIN_PROG_NAME, PUBLISH_SUBCMD
from tests.fixtures.repos import repo_with_single_branch_angular_commits
from tests.util import assert_exit_code, assert_successful_exit_code

if TYPE_CHECKING:
    from typing import Sequence

    from click.testing import CliRunner

    from tests.fixtures.git_repo import GetVersionStringsFn


@pytest.mark.parametrize("cmd_args", [(), ("--tag", "latest")])
@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_publish_latest_uses_latest_tag(
    cli_runner: CliRunner,
    cmd_args: Sequence[str],
    get_versions_for_trunk_only_repo_w_tags: GetVersionStringsFn,
):
    latest_tag = f"v{get_versions_for_trunk_only_repo_w_tags()[-1]}"
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


@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_publish_to_tag_uses_tag(
    cli_runner: CliRunner,
    get_versions_for_trunk_only_repo_w_tags: GetVersionStringsFn,
):
    # Testing a non-latest tag to distinguish from test_publish_latest_uses_latest_tag()
    previous_tag = f"v{get_versions_for_trunk_only_repo_w_tags()[-2]}"

    with mock.patch.object(Github, Github.upload_dists.__name__) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", previous_tag]

        # Act
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        mocked_upload_dists.assert_called_once_with(
            tag=previous_tag, dist_glob="dist/*"
        )


@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
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
