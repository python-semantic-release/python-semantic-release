from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs.github import Github

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import repo_w_trunk_only_conventional_commits
from tests.util import assert_exit_code

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from tests.conftest import RunCliFn
    from tests.e2e.conftest import StripLoggingMessagesFn
    from tests.fixtures.git_repo import BuiltRepoResult, GetVersionsFromRepoBuildDefFn


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_already_released_when_strict(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    """
    Given repo has no new changes since the last release,
    When running the version command in strict mode,
    Then no version release should happen, which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning an exit code of 2.
    """
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]
    expected_error_msg = f"[bold orange1]No release will be made, {latest_release_version} has already been released!"

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = sorted([tag.name for tag in repo.tags])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert f"{latest_release_version}\n" == result.stdout
    assert f"{expected_error_msg}\n" == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_version_on_nonrelease_branch_when_strict(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    """
    Given repo is on a non-release branch,
    When running the version command in strict mode,
    Then no version release should happen which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning an exit code of 2.
    """
    repo = repo_result["repo"]

    # Setup
    branch = repo.create_head("next").checkout()
    expected_error_msg = (
        f"branch '{branch.name}' isn't in any release groups; no release will be made\n"
    )
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert not result.stdout
    assert expected_error_msg == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    tags_after = sorted([tag.name for tag in repo.tags])
    assert repo_status_before == repo.git.status(short=True)
    assert head_before == repo.head.commit.hexsha
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0
