from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs.github import Github

from tests.const import (
    MAIN_PROG_NAME,
    VERSION_SUBCMD,
)
from tests.fixtures.commit_parsers import (
    conventional_minor_commits,
    default_conventional_parser,
)
from tests.fixtures.git_repo import get_commit_def_of_conventional_commit
from tests.fixtures.repos import (
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format,
    repo_w_no_tags_conventional_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_conventional_commits_using_tag_format,
)
from tests.fixtures.repos.trunk_based_dev.repo_w_no_tags import (
    repo_w_no_tags_conventional_commits_using_tag_format,
    repo_w_no_tags_conventional_commits_w_zero_version,
)
from tests.util import (
    add_text_to_file,
    assert_exit_code,
    assert_successful_exit_code,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from semantic_release.commit_parser._base import CommitParser, ParserOptions
    from semantic_release.commit_parser.token import ParseResult

    from tests.conftest import RunCliFn
    from tests.e2e.conftest import StripLoggingMessagesFn
    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        GetCfgValueFromDefFn,
        GetCommitDefFn,
        GetVersionsFromRepoBuildDefFn,
        SimulateChangeCommitsNReturnChangelogEntryFn,
    )


@pytest.mark.parametrize(
    "repo_result, commits, force_args, next_release_version",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            lazy_fixture(conventional_minor_commits.__name__),
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
    repo_result: BuiltRepoResult,
    commits: list[str],
    force_args: list[str],
    next_release_version: str,
    file_in_repo: str,
    run_cli: RunCliFn,
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
    repo = repo_result["repo"]

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
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, commits, force_args, next_release_version",
    [
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                lazy_fixture(conventional_minor_commits.__name__),
                cli_args,
                next_release_version,
                marks=marks if marks else [],
            )
            for repo_fixture_name, marks in (
                (repo_w_trunk_only_conventional_commits.__name__, None),
                (
                    repo_w_trunk_only_conventional_commits_using_tag_format.__name__,
                    pytest.mark.comprehensive,
                ),
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
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                [],
                cli_args,
                next_release_version,
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in (
                repo_w_no_tags_conventional_commits_w_zero_version.__name__,
            )
            for cli_args, next_release_version in (
                # Dynamic version bump determination (based on commits)
                ([], "0.1.0"),
                # Dynamic version bump determination (based on commits) with build metadata
                (["--build-metadata", "build.12345"], "0.1.0+build.12345"),
                # Forced version bump
                (["--prerelease"], "0.0.0-rc.1"),
                (["--patch"], "0.0.1"),
                (["--minor"], "0.1.0"),
                (["--major"], "1.0.0"),
                # Forced version bump with --build-metadata
                (["--patch", "--build-metadata", "build.12345"], "0.0.1+build.12345"),
                # Forced version bump with --as-prerelease
                (["--prerelease", "--as-prerelease"], "0.0.0-rc.1"),
                (["--patch", "--as-prerelease"], "0.0.1-rc.1"),
                (["--minor", "--as-prerelease"], "0.1.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                # Forced version bump with --as-prerelease and modified --prerelease-token
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.0.1-beta.1",
                ),
                # Forced version bump with --as-prerelease and modified --prerelease-token
                # and --build-metadata
                (
                    [
                        "--patch",
                        "--as-prerelease",
                        "--prerelease-token",
                        "beta",
                        "--build-metadata",
                        "build.12345",
                    ],
                    "0.0.1-beta.1+build.12345",
                ),
            )
        ],
    ],
)
def test_version_print_tag_prints_next_tag(
    repo_result: BuiltRepoResult,
    commits: list[str],
    force_args: list[str],
    next_release_version: str,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a generic repository at the latest release version and a subsequent commit,
    When running the version command with the --print-tag flag,
    Then the expected next release tag should be printed and exit without
    making any changes to the repository.

    Note: The point of this test is to only verify that the `--print-tag` flag does not
    make any changes to the repository--not to validate if the next version is calculated
    correctly per the repository structure (see test_version_release &
    test_version_force_level for correctness).

    However, we do validate that --print-tag & a force option and/or --as-prerelease options
    work together to print the next release tag correctly but not make a change to the repo.
    """
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    next_release_tag = tag_format_str.format(version=next_release_version)

    if len(commits) > 1:
        # Make a commit to ensure we have something to release
        # otherwise the "no release will be made" logic will kick in first
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commits[-1], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-tag", *force_args]
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, commits, force_args, next_release_version",
    [
        pytest.param(
            lazy_fixture(repo_fixture_name),
            [],
            cli_args,
            next_release_version,
            marks=pytest.mark.comprehensive,
        )
        for repo_fixture_name in (
            repo_w_no_tags_conventional_commits.__name__,
            repo_w_no_tags_conventional_commits_using_tag_format.__name__,
        )
        for cli_args, next_release_version in (
            # Dynamic version bump determination (based on commits)
            ([], "1.0.0"),
            # Dynamic version bump determination (based on commits) with build metadata
            (["--build-metadata", "build.12345"], "1.0.0+build.12345"),
            # Forced version bump
            (["--prerelease"], "0.0.0-rc.1"),
            (["--patch"], "0.0.1"),
            (["--minor"], "0.1.0"),
            (["--major"], "1.0.0"),
            # Forced version bump with --build-metadata
            (["--patch", "--build-metadata", "build.12345"], "0.0.1+build.12345"),
            # Forced version bump with --as-prerelease
            (["--prerelease", "--as-prerelease"], "0.0.0-rc.1"),
            (["--patch", "--as-prerelease"], "0.0.1-rc.1"),
            (["--minor", "--as-prerelease"], "0.1.0-rc.1"),
            (["--major", "--as-prerelease"], "1.0.0-rc.1"),
            # Forced version bump with --as-prerelease and modified --prerelease-token
            (
                ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                "0.0.1-beta.1",
            ),
            # Forced version bump with --as-prerelease and modified --prerelease-token
            # and --build-metadata
            (
                [
                    "--patch",
                    "--as-prerelease",
                    "--prerelease-token",
                    "beta",
                    "--build-metadata",
                    "build.12345",
                ],
                "0.0.1-beta.1+build.12345",
            ),
        )
    ],
)
def test_version_print_tag_prints_next_tag_no_zero_versions(
    repo_result: BuiltRepoResult,
    commits: list[str],
    force_args: list[str],
    next_release_version: str,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    file_in_repo: str,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    """
    Given a generic repository at the latest release version and a subsequent commit,
    When running the version command with the --print-tag flag,
    Then the expected next release tag should be printed and exit without
    making any changes to the repository.

    Note: The point of this test is to only verify that the `--print-tag` flag does not
    make any changes to the repository--not to validate if the next version is calculated
    correctly per the repository structure (see test_version_release &
    test_version_force_level for correctness).

    However, we do validate that --print-tag & a force option and/or --as-prerelease options
    work together to print the next release tag correctly but not make a change to the repo.
    """
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    next_release_tag = tag_format_str.format(version=next_release_version)

    if len(commits) > 1:
        # Make a commit to ensure we have something to release
        # otherwise the "no release will be made" logic will kick in first
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commits[-1], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-tag", *force_args]
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_print_last_released_prints_version(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, commits",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            lazy_fixture(conventional_minor_commits.__name__),
        )
    ],
)
def test_version_print_last_released_prints_released_if_commits(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    commits: list[str],
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    file_in_repo: str,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]

    # Make a commit so the head is not on the last release
    add_text_to_file(repo, file_in_repo)
    repo.git.commit(m=commits[0], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)],
)
def test_version_print_last_released_prints_nothing_if_no_tags(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    repo = repo_result["repo"]

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred on print)
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == ""
    assert "No release tags found." in result.stderr

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_print_last_released_on_detached_head(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)],
)
def test_version_print_last_released_on_nonrelease_branch(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    latest_release_version = get_versions_from_repo_build_def(
        repo_result["definition"]
    )[-1]

    # Setup: put the repo on a non-release branch
    repo.create_head("next").checkout()

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_version}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
        pytest.param(
            lazy_fixture(
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__
            ),
            marks=pytest.mark.comprehensive,
        ),
    ],
)
def test_version_print_last_released_tag_prints_correct_tag(
    repo_result: BuiltRepoResult,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    latest_release_version = get_versions_from_repo_build_def(repo_def)[-1]
    latest_release_tag = tag_format_str.format(version=latest_release_version)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, commits",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            lazy_fixture(conventional_minor_commits.__name__),
        ),
        pytest.param(
            lazy_fixture(
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__
            ),
            lazy_fixture(conventional_minor_commits.__name__),
            marks=pytest.mark.comprehensive,
        ),
    ],
)
def test_version_print_last_released_tag_prints_released_if_commits(
    repo_result: BuiltRepoResult,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    commits: list[str],
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    file_in_repo: str,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    latest_release_version = get_versions_from_repo_build_def(repo_def)[-1]
    latest_release_tag = tag_format_str.format(version=latest_release_version)

    # Make a commit so the head is not on the last release
    add_text_to_file(repo, file_in_repo)
    repo.git.commit(m=commits[0], a=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)],
)
def test_version_print_last_released_tag_prints_nothing_if_no_tags(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
):
    repo = repo_result["repo"]

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred on print)
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == ""
    assert "No release tags found." in result.stderr

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
        pytest.param(
            lazy_fixture(
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__
            ),
            marks=pytest.mark.comprehensive,
        ),
    ],
)
def test_version_print_last_released_tag_on_detached_head(
    repo_result: BuiltRepoResult,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    latest_release_version = get_versions_from_repo_build_def(repo_def)[-1]
    latest_release_tag = tag_format_str.format(version=latest_release_version)

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{latest_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha  # No commit has been made
    assert not tags_set_difference  # No tag created
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
        pytest.param(
            lazy_fixture(
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__
            ),
            marks=pytest.mark.comprehensive,
        ),
    ],
)
def test_version_print_last_released_tag_on_nonrelease_branch(
    repo_result: BuiltRepoResult,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    latest_release_version = get_versions_from_repo_build_def(repo_def)[-1]
    last_release_tag = tag_format_str.format(version=latest_release_version)

    # Setup: put the repo on a non-release branch
    repo.create_head("next").checkout()

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not strip_logging_messages(result.stderr)
    assert f"{last_release_tag}\n" == result.stdout

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_sha_before == head_after.hexsha
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, get_commit_def_fn, default_parser",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            lazy_fixture(get_commit_def_of_conventional_commit.__name__),
            lazy_fixture(default_conventional_parser.__name__),
        )
    ],
)
def test_version_print_next_version_fails_on_detached_head(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    get_commit_def_fn: GetCommitDefFn[CommitParser[ParseResult, ParserOptions]],
    default_parser: CommitParser[ParseResult, ParserOptions],
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    expected_error_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made"
    )

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: make a commit to ensure we have something to release
    simulate_change_commits_n_rtn_changelog_entry(
        repo,
        [get_commit_def_fn("fix: make a patch fix to codebase", parser=default_parser)],
    )

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_exit_code(1, result, cli_cmd)
    assert not result.stdout
    assert f"{expected_error_msg}\n" == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0


@pytest.mark.parametrize(
    "repo_result, get_commit_def_fn, default_parser",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            lazy_fixture(get_commit_def_of_conventional_commit.__name__),
            lazy_fixture(default_conventional_parser.__name__),
        )
    ],
)
def test_version_print_next_tag_fails_on_detached_head(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    get_commit_def_fn: GetCommitDefFn[CommitParser[ParseResult, ParserOptions]],
    default_parser: CommitParser[ParseResult, ParserOptions],
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    strip_logging_messages: StripLoggingMessagesFn,
):
    repo = repo_result["repo"]
    expected_error_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made"
    )

    # Setup: put the repo in a detached head state
    repo.git.checkout("HEAD", detach=True)

    # Setup: make a commit to ensure we have something to release
    simulate_change_commits_n_rtn_changelog_entry(
        repo,
        [get_commit_def_fn("fix: make a patch fix to codebase", parser=default_parser)],
    )

    # Setup: take measurement before running the version command
    repo_status_before = repo.git.status(short=True)
    head_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-tag"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    repo_status_after = repo.git.status(short=True)
    head_after = repo.head.commit.hexsha
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (expected -> actual)
    assert_exit_code(1, result, cli_cmd)
    assert not result.stdout
    assert f"{expected_error_msg}\n" == strip_logging_messages(result.stderr)

    # assert nothing else happened (no code changes, no commit, no tag, no push, no vcs release)
    assert repo_status_before == repo_status_after
    assert head_before == head_after
    assert not tags_set_difference
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0
