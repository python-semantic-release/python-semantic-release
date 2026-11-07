from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from semantic_release.hvcs.github import Github

from tests.const import VERSION_SUBCMD
from tests.util import add_text_to_file, assert_successful_exit_code

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from tests.conftest import RunCliFn
    from tests.fixtures.git_repo import BuiltRepoResult


@pytest.mark.parametrize("conventional_revert", [False, True])
@pytest.mark.parametrize(
    "reverts, remaining_fix, expected_version",
    [
        (1, False, "0.1.1"),
        (1, True, "0.1.2"),
        (2, False, "1.0.0"),
        (3, False, "0.1.1"),
    ],
)
def test_version_print_unreleased_revert_pairs(
    repo_w_trunk_only_conventional_commits: BuiltRepoResult,
    conventional_revert: bool,
    reverts: int,
    remaining_fix: bool,
    expected_version: str,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given an unreleased breaking change and real Git revert commits,
    When determining the next version,
    Then canceled pairs do not bump the version, and reverting a revert restores it.
    """
    repo = repo_w_trunk_only_conventional_commits["repo"]
    add_text_to_file(repo, file_in_repo)
    repo.git.commit(
        "-am", "feat: change the public API\n\nBREAKING CHANGE: remove the old API"
    )

    for _ in range(reverts):
        target = repo.head.commit.hexsha
        repo.git.revert("--no-edit", target)
        if conventional_revert:
            repo.git.commit(
                "--amend",
                "-m",
                f"revert: undo the previous change\n\nThis reverts commit {target}.",
            )

    if remaining_fix:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit("-am", "fix: correct an independent bug")

    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}
    result = run_cli(
        [VERSION_SUBCMD, "--print"], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"}
    )

    assert_successful_exit_code(result, [VERSION_SUBCMD, "--print"])
    assert result.stdout == f"{expected_version}\n"
    assert repo.head.commit.hexsha == head_before
    assert {tag.name for tag in repo.tags} == tags_before
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize("release_target", [False, True])
def test_version_revert_respects_release_boundary_and_forced_bump(
    repo_w_trunk_only_conventional_commits: BuiltRepoResult,
    release_target: bool,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a real revert and optionally a release containing its original change,
    When printing a forced patch version,
    Then the existing release boundary and forced bump are preserved.
    """
    repo = repo_w_trunk_only_conventional_commits["repo"]
    add_text_to_file(repo, file_in_repo)
    repo.git.commit("-am", "feat: introduce a feature")
    if release_target:
        repo.create_tag("v0.2.0", message="Release 0.2.0")
    repo.git.revert("--no-edit", "HEAD")

    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}
    args = [VERSION_SUBCMD, "--print", "--patch"]
    result = run_cli(args, env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    assert_successful_exit_code(result, args)
    assert result.stdout == ("0.2.1\n" if release_target else "0.1.2\n")
    assert repo.head.commit.hexsha == head_before
    assert {tag.name for tag in repo.tags} == tags_before
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


def test_version_does_not_release_canceled_change(
    repo_w_trunk_only_conventional_commits: BuiltRepoResult,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a breaking change canceled before release,
    When running the version command,
    Then no version commit, tag, push, or hosted release is created.
    """
    repo = repo_w_trunk_only_conventional_commits["repo"]
    add_text_to_file(repo, file_in_repo)
    repo.git.commit("-am", "feat: change API\n\nBREAKING CHANGE: remove API")
    repo.git.revert("--no-edit", "HEAD")
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}
    status_before = repo.git.status(short=True)

    args = [VERSION_SUBCMD, "--no-push", "--no-vcs-release"]
    result = run_cli(args, env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    assert_successful_exit_code(result, args)
    assert repo.head.commit.hexsha == head_before
    assert {tag.name for tag in repo.tags} == tags_before
    assert repo.git.status(short=True) == status_before
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


def test_reverting_released_feature_keeps_configured_bump(
    repo_w_trunk_only_conventional_commits: BuiltRepoResult,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a revert of an already released feature with a patch commit message,
    When printing the automatically determined next version,
    Then the configured patch bump is preserved.
    """
    repo = repo_w_trunk_only_conventional_commits["repo"]
    add_text_to_file(repo, file_in_repo)
    repo.git.commit("-am", "feat: introduce a released feature")
    target = repo.head.commit.hexsha
    repo.create_tag("v0.2.0", message="Release 0.2.0")
    repo.git.revert("--no-edit", target)
    repo.git.commit(
        "--amend",
        "-m",
        f"fix: revert released feature\n\nThis reverts commit {target}.",
    )

    args = [VERSION_SUBCMD, "--print"]
    result = run_cli(args, env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    assert_successful_exit_code(result, args)
    assert result.stdout == "0.2.1\n"
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize("squashed", [False, True])
def test_version_revert_through_merge_history(
    repo_w_trunk_only_conventional_commits: BuiltRepoResult,
    squashed: bool,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a reverted breaking change on a branch merged alongside a fix,
    When printing the next version,
    Then the remaining fix determines the release even across merged history.
    """
    repo = repo_w_trunk_only_conventional_commits["repo"]
    main_branch = repo.active_branch.name
    repo.git.checkout("-b", "reverted-feature")
    add_text_to_file(repo, file_in_repo)
    message = (
        "feat: change public API\n\nBREAKING CHANGE: remove API"
        if not squashed
        else "feat: change public API (#123)\n\n"
        "* feat: add another feature\n\n"
        "* fix: fix another issue\n\nBREAKING CHANGE: remove API"
    )
    repo.git.commit("-am", message)
    repo.git.revert("--no-edit", "HEAD")
    repo.git.checkout(main_branch)
    add_text_to_file(repo, file_in_repo)
    repo.git.commit("-am", "fix: correct another problem")
    repo.git.merge("--no-ff", "-m", "Merge reverted feature", "reverted-feature")

    args = [VERSION_SUBCMD, "--print"]
    result = run_cli(args, env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    assert_successful_exit_code(result, args)
    assert result.stdout == "0.1.2\n"
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0
