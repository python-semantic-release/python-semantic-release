from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main

from tests.const import (
    MAIN_PROG_NAME,
    NULL_HEX_SHA,
    VERSION_SUBCMD,
)
from tests.fixtures.commit_parsers import angular_minor_commits
from tests.fixtures.repos import (
    get_versions_for_trunk_only_repo_w_tags,
    repo_with_no_tags_angular_commits,
    repo_with_single_branch_angular_commits,
)
from tests.util import (
    add_text_to_file,
    assert_exit_code,
    assert_successful_exit_code,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.fixtures.git_repo import (
        GetVersionStringsFn,
        SimulateChangeCommitsNReturnChangelogEntryFn,
    )


@pytest.mark.parametrize(
    "repo, commits, force_args, next_release_version",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(angular_minor_commits.__name__),
            cli_args,
            next_release_version,
        )
        for cli_args, next_release_version in (
            # Dynamic version bump determination (based on commits)
            ([], "0.2.0"),
            # Dynamic version bump determination (based on commits) with build metadata
            (["--build-metadata", "build.12345"], "0.2.0+build.12345"),
            # Forced version bump
            (["--prerelease"], "0.1.1-rc.1"),
            (["--patch"], "0.1.2"),
            (["--minor"], "0.2.0"),
            (["--major"], "1.0.0"),
            # Forced version bump with --build-metadata
            (["--patch", "--build-metadata", "build.12345"], "0.1.2+build.12345"),
            # Forced version bump with --as-prerelease
            (["--prerelease", "--as-prerelease"], "0.1.1-rc.1"),
            (["--patch", "--as-prerelease"], "0.1.2-rc.1"),
            (["--minor", "--as-prerelease"], "0.2.0-rc.1"),
            (["--major", "--as-prerelease"], "1.0.0-rc.1"),
            # Forced version bump with --as-prerelease and modified --prerelease-token
            (
                ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                "0.1.2-beta.1",
            ),
            # Forced version bump with --as-prerelease and modified --prerelease-token
            # and --build-metadata
            (
                # TODO: Error, our current implementation does not support this
                [
                    "--patch",
                    "--as-prerelease",
                    "--prerelease-token",
                    "beta",
                    "--build-metadata",
                    "build.12345",
                ],
                "0.1.2-beta.1+build.12345",
            ),
        )
    ],
)
def test_version_print_next_version(
    repo: Repo,
    commits: list[str],
    force_args: list[str],
    next_release_version: str,
    file_in_repo: str,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a generic repository at the latest release version and a subsequent commit,
    When running the version command with the --print flag,
    Then the expected next version should be printed and exit without
    making any changes to the repository.

    Note: The point of this test is to only verify that the `--print` flag does not
    make any changes to the repository--not to validate if the next version is calculated
    correctly per the repository structure (see test_version_release &
    test_version_force_level for correctness).

    However, we do validate that --print & a force option and/or --as-prerelease options
    work together to print the next version correctly but not make a change to the repo.
    """
    # Make a commit to ensure we have something to release
    # otherwise the "no release will be made" logic will kick in first
    add_text_to_file(repo, file_in_repo)
    repo.git.commit(m=commits[-1], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print", *force_args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{next_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_print_last_released_prints_version(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    latest_release_version = get_repo_versions()[-1]

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo, get_repo_versions, commits",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
            lazy_fixture(angular_minor_commits.__name__),
        )
    ],
)
def test_version_print_last_released_prints_released_if_commits(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    commits: list[str],
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    file_in_repo: str,
):
    latest_release_version = get_repo_versions()[-1]

    # Make a commit so the head is not on the last release
    add_text_to_file(repo, file_in_repo)
    repo.git.commit(m=commits[0], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo",
    [lazy_fixture(repo_with_no_tags_angular_commits.__name__)],
)
def test_version_print_last_released_prints_nothing_if_no_tags(
    repo: Repo,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    caplog: pytest.LogCaptureFixture,
):
    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (no release actions should have occurred on print)
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == ""

    # must use capture log to see this, because we use the logger to print this message
    # not click's output
    assert "No release tags found." in caplog.text

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_print_last_released_on_detached_head(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    latest_release_version = get_repo_versions()[-1]

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_print_last_released_on_nonrelease_branch(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    latest_release_version = get_repo_versions()[-1]

    # Setup: put the repo on a non-release branch
    repo.create_head("next").checkout()

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_print_last_released_tag_on_detached_head(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    latest_release_tag = f"v{get_repo_versions()[-1]}"

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{latest_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo, get_repo_versions",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            lazy_fixture(get_versions_for_trunk_only_repo_w_tags.__name__),
        )
    ],
)
def test_version_print_last_released_tag_on_nonrelease_branch(
    repo: Repo,
    get_repo_versions: GetVersionStringsFn,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    last_version_tag = f"v{get_repo_versions()[-1]}"

    # Setup: put the repo on a non-release branch
    repo.create_head("next").checkout()

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert f"{last_version_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo",
    [lazy_fixture(repo_with_single_branch_angular_commits.__name__)],
)
def test_version_print_next_version_fails_on_detached_head(
    repo: Repo,
    cli_runner: CliRunner,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    expected_error_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made"
    )

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: make a commit to ensure we have something to release
    simulate_change_commits_n_rtn_changelog_entry(
        repo,
        [{"msg": "fix: make a patch fix to codebase", "sha": NULL_HEX_SHA}],
    )

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (expected -> actual)
    assert_exit_code(1, result, cli_cmd)
    assert not result.stdout
    assert f"{expected_error_msg}\n" == result.stderr

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0
