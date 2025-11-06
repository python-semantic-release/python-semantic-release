from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs.github import Github

from tests.const import (
    MAIN_PROG_NAME,
    VERSION_SUBCMD,
)
from tests.fixtures.repos import (
    repo_w_no_tags_conventional_commits,
    repo_w_trunk_only_conventional_commits,
)
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from git import Repo
    from requests_mock import Mocker

    from tests.conftest import RunCliFn
    from tests.e2e.conftest import StripLoggingMessagesFn
    from tests.fixtures.example_project import GetWheelFileFn, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult, GetVersionsFromRepoBuildDefFn


# No-op shouldn't change based on the branching/merging of the repository
@pytest.mark.parametrize(
    "repo_result, next_release_version",
    # must use a repo that is ready for a release to prevent no release
    # logic from being triggered before the noop logic
    [(lazy_fixture(repo_w_no_tags_conventional_commits.__name__), "1.0.0")],
)
def test_version_noop_is_noop(
    repo_result: BuiltRepoResult,
    next_release_version: str,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    get_wheel_file: GetWheelFileFn,
):
    repo: Repo = repo_result["repo"]
    build_result_file = get_wheel_file(next_release_version)

    # Setup: reset any uncommitted changes (if any)
    repo.git.reset("--hard")

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--noop", VERSION_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha, "HEAD should not have changed"
    assert not tags_set_difference  # No tag created

    # no build result
    assert not build_result_file.exists()

    # no file changes (since no commit was made then just check for non-committed changes)
    assert not repo.git.status(short=True)

    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_no_git_verify(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    repo = repo_result["repo"]

    # setup: set configuration setting
    update_pyproject_toml("tool.semantic_release.no_git_verify", True)
    repo.git.commit(
        m="chore: adjust project configuration for --no-verify release commits", a=True
    )
    # Fake an automated push to remote by updating the remote tracking branch
    repo.git.update_ref(
        f"refs/remotes/origin/{repo.active_branch.name}",
        repo.head.commit.hexsha,
    )

    # setup: create executable pre-commit script
    precommit_hook = Path(repo.git_dir, "hooks", "pre-commit")
    precommit_hook.parent.mkdir(parents=True, exist_ok=True)
    precommit_hook.write_text(
        dedent(
            """\
            #!/bin/sh
            echo >&2 "Always fail pre-commit" && exit 1;
            """
        )
    )
    precommit_hook.chmod(0o754)

    # setup: set git configuration to have the pre-commit hook
    repo.git.config(
        "core.hookspath",
        str(precommit_hook.parent.relative_to(repo.working_dir)),
        local=True,
    )

    # Take measurement beforehand
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Execute
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch"]
    result = run_cli(cli_cmd[1:])

    # Take measurement after the command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)
    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]
    assert len(tags_set_difference) == 1  # A tag has been created
    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_version_on_nonrelease_branch(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    """
    Given repo is on a non-release branch,
    When running the version command,
    Then no version release should happen which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning a successful exit code
    """
    repo = repo_result["repo"]

    branch = repo.create_head("next").checkout()
    expected_error_msg = (
        f"branch '{branch.name}' isn't in any release groups; no release will be made\n"
    )
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stdout
    assert expected_error_msg == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    tags_after = sorted([tag.name for tag in repo.tags])
    assert repo_status_before == repo.git.status(short=True)
    assert head_before == repo.head.commit.hexsha
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_on_last_release(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    """
    Given repo is on the last release version,
    When running the version command,
    Then no version release should happen which means no code changes, no build, no commit,
    no tag, no push, and no vcs release creation while returning a successful exit code and
    printing the last release version
    """
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]
    expected_error_msg = (
        f"No release will be made, {latest_release_version} has already been released!"
    )

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = sorted([tag.name for tag in repo.tags])

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD]
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = sorted([tag.name for tag in repo.tags])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{latest_release_version}\n" == result.stdout
    assert f"{expected_error_msg}\n" == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert tags_before == tags_after
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)]
)
def test_version_only_tag_push(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
) -> None:
    """
    Given a repo with no tags,
    When running the version command with the `--no-commit` and `--tag` flags,
    Then a tag should be created on the current commit, pushed, and a release created.
    """
    repo = repo_result["repo"]

    # Setup
    head_before = repo.head.commit

    # Act
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-commit",
        "--tag",
    ]
    result = run_cli(cli_cmd[1:])

    # capture values after the command
    tag_after = repo.tags[-1].name
    head_after = repo.head.commit

    # Assert only tag was created, it was pushed and then release was created
    assert_successful_exit_code(result, cli_cmd)
    assert tag_after == "v1.0.0"
    assert head_before == head_after
    assert mocked_git_push.call_count == 1  # 0 for commit, 1 for tag
    assert post_mocker.call_count == 1
