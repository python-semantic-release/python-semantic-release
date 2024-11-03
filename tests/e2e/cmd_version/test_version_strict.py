from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import (
    get_versions_for_trunk_only_repo_w_tags,
    repo_with_single_branch_angular_commits,
)
from tests.util import assert_exit_code

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.fixtures.git_repo import GetVersionStringsFn


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_already_released_when_strict(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given repo has no new changes since the last release,
    When running the version command in strict mode,
    Then no version release should happen, which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning an exit code of 2.
    """
    latest_release_version = get_repo_versions()[-1]
    expected_error_msg = f"[bold orange1]No release will be made, {latest_release_version} has already been released!"

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = sorted([tag.name for tag in repo.tags])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert f"{latest_release_version}\n" == result.stdout
    assert f"{expected_error_msg}\n" == result.stderr

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo", [lazy_fixture(repo_with_single_branch_angular_commits.__name__)]
)
def test_version_on_nonrelease_branch_when_strict(
    repo: Repo,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given repo is on a non-release branch,
    When running the version command in strict mode,
    Then no version release should happen which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning an exit code of 2.
    """
    branch = repo.create_head("next").checkout()
    expected_error_msg = (
        f"branch '{branch.name}' isn't in any release groups; no release will be made\n"
    )
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert not result.stdout
    assert expected_error_msg == result.stderr

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    tags_after = sorted([tag.name for tag in repo.tags])
    assert repo_status_before == repo.git.status(short=True)
    assert head_before == repo.head.commit.hexsha
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0
