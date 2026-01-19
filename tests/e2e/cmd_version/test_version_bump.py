from __future__ import annotations

from datetime import timedelta
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
import tomlkit

# Limitation in pytest-lazy-fixture - see https://stackoverflow.com/a/69884019
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.commit_parser.conventional import ConventionalCommitParser
from semantic_release.commit_parser.emoji import EmojiCommitParser
from semantic_release.commit_parser.scipy import ScipyCommitParser

from tests.const import EXAMPLE_PROJECT_NAME, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures import (
    conventional_chore_commits,
    conventional_major_commits,
    conventional_minor_commits,
    conventional_patch_commits,
    emoji_chore_commits,
    emoji_major_commits,
    emoji_minor_commits,
    emoji_patch_commits,
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_alpha_prereleases_n_scipy_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits,
    repo_w_github_flow_w_feature_release_channel_conventional_commits,
    repo_w_initial_commit,
    repo_w_no_tags_conventional_commits,
    repo_w_no_tags_conventional_commits_w_zero_version,
    repo_w_no_tags_emoji_commits,
    repo_w_no_tags_scipy_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_emoji_commits,
    repo_w_trunk_only_n_prereleases_conventional_commits,
    repo_w_trunk_only_n_prereleases_emoji_commits,
    repo_w_trunk_only_n_prereleases_scipy_commits,
    repo_w_trunk_only_scipy_commits,
    scipy_chore_commits,
    scipy_major_commits,
    scipy_minor_commits,
    scipy_patch_commits,
)
from tests.util import (
    add_text_to_file,
    assert_successful_exit_code,
    dynamic_python_import,
    xdist_sort_hack,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from tests.conftest import GetStableDateNowFn, RunCliFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        GetExpectedVersionPyFileContentFn,
        UpdatePyprojectTomlFn,
    )
    from tests.fixtures.git_repo import BuiltRepoResult


@pytest.mark.parametrize(
    "repo_result, cli_args, next_release_version",
    [
        *(
            (
                lazy_fixture(
                    repo_w_no_tags_conventional_commits_w_zero_version.__name__
                ),
                cli_args,
                next_release_version,
            )
            for cli_args, next_release_version in (
                # New build-metadata forces a new release
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
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                cli_args,
                expected_stdout,
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name, values in {
                repo_w_trunk_only_conventional_commits.__name__: [
                    # New build-metadata forces a new release
                    (["--build-metadata", "build.12345"], "0.1.1+build.12345"),
                    # Forced version bump
                    (["--prerelease"], "0.1.1-rc.1"),
                    (["--patch"], "0.1.2"),
                    (["--minor"], "0.2.0"),
                    (["--major"], "1.0.0"),
                    # Forced version bump with --build-metadata
                    (
                        ["--patch", "--build-metadata", "build.12345"],
                        "0.1.2+build.12345",
                    ),
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
                ],
                repo_w_trunk_only_n_prereleases_conventional_commits.__name__: [
                    # New build-metadata forces a new release
                    (["--build-metadata", "build.12345"], "0.2.0+build.12345"),
                    # Forced version bump
                    # NOTE: There is already a 0.2.0-rc.1
                    (["--prerelease"], "0.2.0-rc.2"),
                    (["--patch"], "0.2.1"),
                    (["--minor"], "0.3.0"),
                    (["--major"], "1.0.0"),
                    # Forced version bump with --build-metadata
                    (
                        ["--patch", "--build-metadata", "build.12345"],
                        "0.2.1+build.12345",
                    ),
                    # Forced version bump with --as-prerelease
                    (["--prerelease", "--as-prerelease"], "0.2.0-rc.2"),
                    (["--patch", "--as-prerelease"], "0.2.1-rc.1"),
                    (["--minor", "--as-prerelease"], "0.3.0-rc.1"),
                    (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                    # Forced version bump with --as-prerelease and modified --prerelease-token
                    (
                        ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                        "0.2.1-beta.1",
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
                        "0.2.1-beta.1+build.12345",
                    ),
                ],
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__: [
                    # New build-metadata forces a new release
                    (["--build-metadata", "build.12345"], "1.1.0+build.12345"),
                    # Forced version bump
                    (["--prerelease"], "1.1.0-rc.1"),
                    (["--patch"], "1.1.1"),
                    (["--minor"], "1.2.0"),
                    (["--major"], "2.0.0"),
                    # Forced version bump with --build-metadata
                    (
                        ["--patch", "--build-metadata", "build.12345"],
                        "1.1.1+build.12345",
                    ),
                    # Forced version bump with --as-prerelease
                    (["--prerelease", "--as-prerelease"], "1.1.0-rc.1"),
                    (["--patch", "--as-prerelease"], "1.1.1-rc.1"),
                    (["--minor", "--as-prerelease"], "1.2.0-rc.1"),
                    (["--major", "--as-prerelease"], "2.0.0-rc.1"),
                    # Forced version bump with --as-prerelease and modified --prerelease-token
                    (
                        ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                        "1.1.1-beta.1",
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
                        "1.1.1-beta.1+build.12345",
                    ),
                ],
                repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__: [
                    # New build-metadata forces a new release
                    (["--build-metadata", "build.12345"], "1.2.0-alpha.2+build.12345"),
                    # Forced version bump
                    (["--prerelease"], "1.2.0-alpha.3"),
                    (["--patch"], "1.2.1"),
                    (["--minor"], "1.3.0"),
                    (["--major"], "2.0.0"),
                    # Forced version bump with --build-metadata
                    (
                        ["--patch", "--build-metadata", "build.12345"],
                        "1.2.1+build.12345",
                    ),
                    # Forced version bump with --as-prerelease
                    (["--prerelease", "--as-prerelease"], "1.2.0-alpha.3"),
                    (["--patch", "--as-prerelease"], "1.2.1-alpha.1"),
                    (["--minor", "--as-prerelease"], "1.3.0-alpha.1"),
                    (["--major", "--as-prerelease"], "2.0.0-alpha.1"),
                    # Forced version bump with --as-prerelease and modified --prerelease-token
                    (
                        ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                        "1.2.1-beta.1",
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
                        "1.2.1-beta.1+build.12345",
                    ),
                ],
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__: [
                    # New build-metadata forces a new release
                    (["--build-metadata", "build.12345"], "1.1.0+build.12345"),
                    # Forced version bump
                    (["--prerelease"], "1.1.0-rc.3"),
                    (["--patch"], "1.1.1"),
                    (["--minor"], "1.2.0"),
                    (["--major"], "2.0.0"),
                    # Forced version bump with --build-metadata
                    (
                        ["--patch", "--build-metadata", "build.12345"],
                        "1.1.1+build.12345",
                    ),
                    # Forced version bump with --as-prerelease
                    (["--prerelease", "--as-prerelease"], "1.1.0-rc.3"),
                    (["--patch", "--as-prerelease"], "1.1.1-rc.1"),
                    (["--minor", "--as-prerelease"], "1.2.0-rc.1"),
                    (["--major", "--as-prerelease"], "2.0.0-rc.1"),
                    # Forced version bump with --as-prerelease and modified --prerelease-token
                    (
                        ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                        "1.1.1-beta.1",
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
                        "1.1.1-beta.1+build.12345",
                    ),
                ],
            }.items()
            for (cli_args, expected_stdout) in values
        ],
    ],
)
def test_version_force_level(
    repo_result: BuiltRepoResult,
    cli_args: list[str],
    next_release_version: str,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    pyproject_toml_file: Path,
    changelog_md_file: Path,
    get_expected_version_py_file_content: GetExpectedVersionPyFileContentFn,
):
    # Force clean directory state before test (needed for the repo_w_no_tags)
    repo = repo_result["repo"]
    repo.git.reset("HEAD", hard=True)

    version_file = example_project_dir.joinpath(
        "src", EXAMPLE_PROJECT_NAME, "_version.py"
    )

    expected_changed_files = sorted(
        [
            str(changelog_md_file),
            str(pyproject_toml_file),
            str(version_file.relative_to(example_project_dir)),
        ]
    )

    expected_version_py_content = get_expected_version_py_file_content(
        next_release_version
    )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    pyproject_toml_before = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )

    # Modify the pyproject.toml to remove the version so we can compare it later
    pyproject_toml_before.get("tool", {}).get("poetry").pop("version")  # type: ignore[attr-defined]

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))
    differing_files = [
        # Make sure filepath uses os specific path separators
        str(Path(file))
        for file in str(repo.git.diff("HEAD", "HEAD~1", name_only=True)).splitlines()
    ]
    pyproject_toml_after = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    pyproj_version_after = (
        pyproject_toml_after.get("tool", {}).get("poetry", {}).pop("version")
    )

    # Load python module for reading the version (ensures the file is valid)
    actual_version_py_content = version_file.read_text()

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred

    # Changelog already reflects changes this should introduce
    assert expected_changed_files == differing_files

    # Compare pyproject.toml
    assert pyproject_toml_before == pyproject_toml_after
    assert next_release_version == pyproj_version_after

    # Compare _version.py
    assert expected_version_py_content == actual_version_py_content

    # Verify content is parsable & importable
    dynamic_version = dynamic_python_import(
        version_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    assert next_release_version == dynamic_version


# NOTE: There is a bit of a corner-case where if we are not doing a
# prerelease, we will get a full version based on already-released commits.
# So for example, commits that wouldn't trigger a release on a prerelease branch
# won't trigger a release if prerelease=true; however, when commits included in a
# prerelease branch are merged to a release branch, prerelease=False - so a feat commit
# which previously triggered a prerelease on a branch will subsequently trigger a full
# release when merged to a full release branch where prerelease=False.
# For this reason a couple of these test cases predict a new version even when the
# commits being added here don't induce a version bump.
@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            (
                # Default case should be a minor bump since last full release was 1.1.1
                # last tag is a prerelease 1.2.0-rc.2
                lazy_fixture(
                    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__
                ),
                lazy_fixture(conventional_minor_commits.__name__),
                False,
                "alpha",
                "1.2.0",
                "main",
            ),
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    [] if commit_messages is None else lazy_fixture(commit_messages),
                    prerelease,
                    prerelease_token,
                    expected_new_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                    # The last full release version was 1.1.1, so it's had a minor
                    # prerelease
                    (
                        repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                        "alpha",
                    ): [
                        (conventional_patch_commits.__name__, False, "1.1.2", None),
                        (
                            conventional_patch_commits.__name__,
                            True,
                            "1.1.2-alpha.1",
                            None,
                        ),
                        (
                            conventional_minor_commits.__name__,
                            True,
                            "1.2.0-alpha.3",
                            "feat/feature-4",  # branch
                        ),
                        (conventional_major_commits.__name__, False, "2.0.0", None),
                        (
                            conventional_major_commits.__name__,
                            True,
                            "2.0.0-alpha.1",
                            None,
                        ),
                    ],
                    # Latest version for repo_with_git_flow_and_release_channels is
                    # currently 1.1.0
                    (
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
                        "alpha",
                    ): [
                        (conventional_patch_commits.__name__, False, "1.1.1", None),
                        (
                            conventional_patch_commits.__name__,
                            True,
                            "1.1.1-alpha.1",
                            None,
                        ),
                        (conventional_minor_commits.__name__, False, "1.2.0", None),
                        (
                            conventional_minor_commits.__name__,
                            True,
                            "1.2.0-alpha.1",
                            None,
                        ),
                        (conventional_major_commits.__name__, False, "2.0.0", None),
                        (
                            conventional_major_commits.__name__,
                            True,
                            "2.0.0-alpha.1",
                            None,
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    expected_new_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ]
    ),
)
# TODO: add a github flow test case
def test_version_next_greater_than_version_one_conventional(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    [] if commit_messages is None else lazy_fixture(commit_messages),
                    prerelease,
                    prerelease_token,
                    expected_new_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                    # The last full release version was 1.1.1, so it's had a minor
                    # prerelease
                    (
                        repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, True, "1.2.0-alpha.2", "feat/feature-4")
                            for commits in (
                                None,
                                conventional_chore_commits.__name__,
                            )
                        ),
                        *(
                            (commits, False, "1.1.1", None)
                            for commits in (
                                None,
                                conventional_chore_commits.__name__,
                            )
                        ),
                    ],
                    # Latest version for repo_with_git_flow_and_release_channels is
                    # currently 1.1.0
                    (
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, prerelease, "1.1.0", None)
                            for prerelease in (True, False)
                            for commits in (
                                None,
                                conventional_chore_commits.__name__,
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    expected_new_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ]
    ),
)
def test_version_next_greater_than_version_one_no_bump_conventional(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            pytest.param(
                lazy_fixture(repo_fixture_name),
                [] if commit_messages is None else lazy_fixture(commit_messages),
                prerelease,
                prerelease_token,
                expected_new_version,
                "main" if branch_name is None else branch_name,
                marks=pytest.mark.comprehensive,
            )
            for (repo_fixture_name, prerelease_token), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_w_git_flow_w_alpha_prereleases_n_emoji_commits.__name__,
                    "alpha",
                ): [
                    (emoji_patch_commits.__name__, False, "1.1.2", None),
                    (
                        emoji_patch_commits.__name__,
                        True,
                        "1.1.2-alpha.1",
                        None,
                    ),
                    (
                        emoji_minor_commits.__name__,
                        False,
                        "1.2.0",
                        None,
                    ),
                    (
                        emoji_minor_commits.__name__,
                        True,
                        "1.2.0-alpha.3",
                        "feat/feature-4",  # branch
                    ),
                    (emoji_major_commits.__name__, False, "2.0.0", None),
                    (
                        emoji_major_commits.__name__,
                        True,
                        "2.0.0-alpha.1",
                        None,
                    ),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0
                (
                    repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits.__name__,
                    "alpha",
                ): [
                    (emoji_patch_commits.__name__, False, "1.1.1", None),
                    (
                        emoji_patch_commits.__name__,
                        True,
                        "1.1.1-alpha.1",
                        None,
                    ),
                    (emoji_minor_commits.__name__, False, "1.2.0", None),
                    (
                        emoji_minor_commits.__name__,
                        True,
                        "1.2.0-alpha.1",
                        None,
                    ),
                    (emoji_major_commits.__name__, False, "2.0.0", None),
                    (
                        emoji_major_commits.__name__,
                        True,
                        "2.0.0-alpha.1",
                        None,
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                expected_new_version,
                branch_name,
            ) in values  # type: ignore[attr-defined]
        ]
    ),
)
def test_version_next_greater_than_version_one_emoji(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    [] if commit_messages is None else lazy_fixture(commit_messages),
                    prerelease,
                    prerelease_token,
                    expected_new_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                    # The last full release version was 1.1.1, so it's had a minor
                    # prerelease
                    (
                        repo_w_git_flow_w_alpha_prereleases_n_emoji_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, True, "1.2.0-alpha.2", "feat/feature-4")
                            for commits in (
                                None,
                                emoji_chore_commits.__name__,
                            )
                        ),
                        *(
                            (commits, False, "1.1.1", None)
                            for commits in (
                                None,
                                emoji_chore_commits.__name__,
                            )
                        ),
                    ],
                    # Latest version for repo_with_git_flow_and_release_channels is
                    # currently 1.1.0
                    (
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, prerelease, "1.1.0", None)
                            for prerelease in (True, False)
                            for commits in (
                                None,
                                emoji_chore_commits.__name__,
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    expected_new_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ]
    ),
)
def test_version_next_greater_than_version_one_no_bump_emoji(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            pytest.param(
                lazy_fixture(repo_fixture_name),
                [] if commit_messages is None else lazy_fixture(commit_messages),
                prerelease,
                prerelease_token,
                expected_new_version,
                "main" if branch_name is None else branch_name,
                marks=pytest.mark.comprehensive,
            )
            for (repo_fixture_name, prerelease_token), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_w_git_flow_w_alpha_prereleases_n_scipy_commits.__name__,
                    "alpha",
                ): [
                    (scipy_patch_commits.__name__, False, "1.1.2", None),
                    (
                        scipy_patch_commits.__name__,
                        True,
                        "1.1.2-alpha.1",
                        None,
                    ),
                    (
                        scipy_minor_commits.__name__,
                        False,
                        "1.2.0",
                        None,
                    ),
                    (
                        scipy_minor_commits.__name__,
                        True,
                        "1.2.0-alpha.3",
                        "feat/feature-4",  # branch
                    ),
                    (scipy_major_commits.__name__, False, "2.0.0", None),
                    (
                        scipy_major_commits.__name__,
                        True,
                        "2.0.0-alpha.1",
                        None,
                    ),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0
                (
                    repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits.__name__,
                    "alpha",
                ): [
                    (scipy_patch_commits.__name__, False, "1.1.1", None),
                    (
                        scipy_patch_commits.__name__,
                        True,
                        "1.1.1-alpha.1",
                        None,
                    ),
                    (scipy_minor_commits.__name__, False, "1.2.0", None),
                    (
                        scipy_minor_commits.__name__,
                        True,
                        "1.2.0-alpha.1",
                        None,
                    ),
                    (scipy_major_commits.__name__, False, "2.0.0", None),
                    (
                        scipy_major_commits.__name__,
                        True,
                        "2.0.0-alpha.1",
                        None,
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                expected_new_version,
                branch_name,
            ) in values  # type: ignore[attr-defined]
        ],
    ),
)
def test_version_next_greater_than_version_one_scipy(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    [] if commit_messages is None else lazy_fixture(commit_messages),
                    prerelease,
                    prerelease_token,
                    expected_new_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                    # The last full release version was 1.1.1, so it's had a minor
                    # prerelease
                    (
                        repo_w_git_flow_w_alpha_prereleases_n_scipy_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, True, "1.2.0-alpha.2", "feat/feature-4")
                            for commits in (
                                None,
                                scipy_chore_commits.__name__,
                            )
                        ),
                        *(
                            (commits, False, "1.1.1", None)
                            for commits in (
                                None,
                                scipy_chore_commits.__name__,
                            )
                        ),
                    ],
                    # Latest version for repo_with_git_flow_and_release_channels is
                    # currently 1.1.0
                    (
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits.__name__,
                        "alpha",
                    ): [
                        *(
                            (commits, prerelease, "1.1.0", None)
                            for prerelease in (True, False)
                            for commits in (
                                None,
                                scipy_chore_commits.__name__,
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    expected_new_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ]
    ),
)
def test_version_next_greater_than_version_one_no_bump_scipy(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    run_cli: RunCliFn,
    file_in_repo: str,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


# ============================================================================= #
# Zero Dot version tests (ex. 0.x.y versions)
# ============================================================================= #


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            (
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                # Given the major_on_zero is False and the version is starting at 0.0.0,
                # the major level commits are limited to only causing a minor level bump
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                lazy_fixture(conventional_major_commits.__name__),
                False,
                "rc",
                False,
                True,
                "0.1.0",
                "main",
            ),
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    commit_messages,
                    prerelease,
                    "rc" if prerelease_token is None else prerelease_token,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                    # It's biggest change type is minor, so the next version should be 0.1.0
                    (
                        repo_w_no_tags_conventional_commits.__name__,
                        None,
                    ): [
                        *(
                            # when prerelease is False, & major_on_zero is False &
                            # allow_zero_version is True, the version should be
                            # 0.1.0, with the given commits
                            (commits, False, False, True, "0.1.0", None)
                            for commits in (
                                # Even when this test does not change anything, the base modification
                                # will be a minor change and thus the version will be bumped to 0.1.0
                                None,
                                # Non version bumping commits are absorbed into the previously detected minor bump
                                lazy_fixture(conventional_chore_commits.__name__),
                                # Patch commits are absorbed into the previously detected minor bump
                                lazy_fixture(conventional_patch_commits.__name__),
                                # Minor level commits are absorbed into the previously detected minor bump
                                lazy_fixture(conventional_minor_commits.__name__),
                                # Given the major_on_zero is False and the version is starting at 0.0.0,
                                # the major level commits are limited to only causing a minor level bump
                                # lazy_fixture(conventional_major_commits.__name__), # used as default
                            )
                        ),
                        # when prerelease is False, & major_on_zero is False, & allow_zero_version is True,
                        # the version should only be minor bumped when provided major commits because
                        # of the major_on_zero value
                        (
                            lazy_fixture(conventional_major_commits.__name__),
                            False,
                            False,
                            True,
                            "0.1.0",
                            None,
                        ),
                        # when prerelease is False, & major_on_zero is True & allow_zero_version is True,
                        # the version should be major bumped when provided major commits because
                        # of the major_on_zero value
                        (
                            lazy_fixture(conventional_major_commits.__name__),
                            False,
                            True,
                            True,
                            "1.0.0",
                            None,
                        ),
                        *(
                            # when prerelease is False, & allow_zero_version is False, the version should be
                            # 1.0.0, across the board because 0 is not a valid major version.
                            # major_on_zero is ignored as it is not relevant but tested for completeness
                            (commits, False, major_on_zero, False, "1.0.0", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(conventional_chore_commits.__name__),
                                lazy_fixture(conventional_patch_commits.__name__),
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                    ],
                    # Latest version for repo_with_single_branch is currently 0.1.1
                    # Note repo_with_single_branch isn't modelled with prereleases
                    (
                        repo_w_trunk_only_conventional_commits.__name__,
                        None,
                    ): [
                        *(
                            # when prerelease must be False, and allow_zero_version is True,
                            # the version is patch bumped because of the patch level commits
                            # regardless of the major_on_zero value
                            (
                                lazy_fixture(conventional_patch_commits.__name__),
                                False,
                                major_on_zero,
                                True,
                                "0.1.2",
                                None,
                            )
                            for major_on_zero in (True, False)
                        ),
                        *(
                            # when prerelease must be False, and allow_zero_version is True,
                            # the version is minor bumped because of the major_on_zero value=False
                            (commits, False, False, True, "0.2.0", None)
                            for commits in (
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                        # when prerelease must be False, and allow_zero_version is True,
                        # but the major_on_zero is True, then when a major level commit is given,
                        # the version should be bumped to the next major version
                        (
                            lazy_fixture(conventional_major_commits.__name__),
                            False,
                            True,
                            True,
                            "1.0.0",
                            None,
                        ),
                        *(
                            # when prerelease must be False, & allow_zero_version is False, the version should be
                            # 1.0.0, with any change regardless of major_on_zero
                            (commits, False, major_on_zero, False, "1.0.0", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(conventional_chore_commits.__name__),
                                lazy_fixture(conventional_patch_commits.__name__),
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                    ],
                    # Latest version for repo_with_single_branch_and_prereleases is
                    # currently 0.2.0
                    (
                        repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                        None,
                    ): [
                        # when allow_zero_version is True,
                        # prerelease is False, & major_on_zero is False, the version should be
                        # patch bumped as a prerelease version, when given patch level commits
                        (
                            lazy_fixture(conventional_patch_commits.__name__),
                            True,
                            False,
                            True,
                            "0.2.1-rc.1",
                            None,
                        ),
                        # when allow_zero_version is True,
                        # prerelease is False, & major_on_zero is False, the version should be
                        # patch bumped, when given patch level commits
                        (
                            lazy_fixture(conventional_patch_commits.__name__),
                            False,
                            False,
                            True,
                            "0.2.1",
                            None,
                        ),
                        *(
                            # when allow_zero_version is True,
                            # prerelease is True, & major_on_zero is False, the version should be
                            # minor bumped as a prerelease version, when given commits of a minor or major level
                            (commits, True, False, True, "0.3.0-rc.1", None)
                            for commits in (
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                        *(
                            # when allow_zero_version is True, prerelease is True, & major_on_zero
                            # is False, the version should be minor bumped, when given commits of a
                            # minor or major level because major_on_zero = False
                            (commits, False, False, True, "0.3.0", None)
                            for commits in (
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                        # when prerelease is True, & major_on_zero is True, and allow_zero_version
                        # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                        # given major level commits
                        (
                            lazy_fixture(conventional_major_commits.__name__),
                            True,
                            True,
                            True,
                            "1.0.0-rc.1",
                            None,
                        ),
                        # when prerelease is False, & major_on_zero is True, and allow_zero_version
                        # is True, the version should be bumped to 1.0.0, when given major level commits
                        (
                            lazy_fixture(conventional_major_commits.__name__),
                            False,
                            True,
                            True,
                            "1.0.0",
                            None,
                        ),
                        *(
                            # when prerelease is True, & allow_zero_version is False, the version should be
                            # bumped to 1.0.0 as a prerelease version, when given any/none commits
                            # because 0.x is no longer a valid version regardless of the major_on_zero value
                            (commits, True, major_on_zero, False, "1.0.0-rc.1", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(conventional_chore_commits.__name__),
                                lazy_fixture(conventional_patch_commits.__name__),
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                        *(
                            # when prerelease is True, & allow_zero_version is False, the version should be
                            # bumped to 1.0.0, when given any/none commits
                            # because 0.x is no longer a valid version regardless of the major_on_zero value
                            (commits, False, major_on_zero, False, "1.0.0", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                lazy_fixture(conventional_patch_commits.__name__),
                                lazy_fixture(conventional_minor_commits.__name__),
                                lazy_fixture(conventional_major_commits.__name__),
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ],
    ),
)
def test_version_next_w_zero_dot_versions_conventional(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    commit_messages,
                    prerelease,
                    "rc" if prerelease_token is None else prerelease_token,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_single_branch is currently 0.1.1
                    # Note repo_with_single_branch isn't modelled with prereleases
                    (
                        repo_w_trunk_only_conventional_commits.__name__,
                        None,
                    ): [
                        *(
                            # when prerelease must be False, and allow_zero_version is True,
                            # the version is not bumped because of non valuable changes regardless
                            # of the major_on_zero value
                            (commits, False, major_on_zero, True, "0.1.1", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(conventional_chore_commits.__name__),
                            )
                        ),
                    ],
                    # Latest version for repo_with_single_branch_and_prereleases is
                    # currently 0.2.0
                    (
                        repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                        None,
                    ): [
                        *(
                            # when allow_zero_version is True, the version is not bumped
                            # regardless of prerelease and major_on_zero values when given
                            # non valuable changes
                            (commits, prerelease, major_on_zero, True, "0.2.0", None)
                            for prerelease in (True, False)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(conventional_chore_commits.__name__),
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ],
    ),
)
def test_version_next_w_zero_dot_versions_no_bump_conventional(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            pytest.param(
                lazy_fixture(repo_fixture_name),
                commit_messages,
                prerelease,
                "rc" if prerelease_token is None else prerelease_token,
                major_on_zero,
                allow_zero_version,
                next_release_version,
                "main" if branch_name is None else branch_name,
                marks=pytest.mark.comprehensive,
            )
            for (repo_fixture_name, prerelease_token), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_w_no_tags_emoji_commits.__name__,
                    None,
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0", None)
                        for commits in (
                            # Even when this test does not change anything, the base modification
                            # will be a minor change and thus the version will be bumped to 0.1.0
                            None,
                            # Non version bumping commits are absorbed into the previously detected minor bump
                            lazy_fixture(emoji_chore_commits.__name__),
                            # Patch commits are absorbed into the previously detected minor bump
                            lazy_fixture(emoji_patch_commits.__name__),
                            # Minor level commits are absorbed into the previously detected minor bump
                            lazy_fixture(emoji_minor_commits.__name__),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    # when prerelease is False, & major_on_zero is False, & allow_zero_version is True,
                    # the version should only be minor bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        False,
                        True,
                        "0.1.0",
                        None,
                    ),
                    # when prerelease is False, & major_on_zero is True & allow_zero_version is True,
                    # the version should be major bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    repo_w_trunk_only_emoji_commits.__name__,
                    None,
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is patch bumped because of the patch level commits
                        # regardless of the major_on_zero value
                        (
                            lazy_fixture(emoji_patch_commits.__name__),
                            False,
                            major_on_zero,
                            True,
                            "0.1.2",
                            None,
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0", None)
                        for commits in (
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    # when prerelease must be False, and allow_zero_version is True,
                    # but the major_on_zero is True, then when a major level commit is given,
                    # the version should be bumped to the next major version
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is
                # currently 0.2.0
                (
                    repo_w_trunk_only_n_prereleases_emoji_commits.__name__,
                    None,
                ): [
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(emoji_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
                        None,
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped, when given patch level commits
                    (
                        lazy_fixture(emoji_patch_commits.__name__),
                        False,
                        False,
                        True,
                        "0.2.1",
                        None,
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1", None)
                        for commits in (
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True, prerelease is True, & major_on_zero
                        # is False, the version should be minor bumped, when given commits of a
                        # minor or major level because major_on_zero = False
                        (commits, False, False, True, "0.3.0", None)
                        for commits in (
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-rc.1",
                        None,
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                next_release_version,
                branch_name,
            ) in values  # type: ignore[attr-defined]
        ],
    ),
)
def test_version_next_w_zero_dot_versions_emoji(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    commit_messages,
                    prerelease,
                    "rc" if prerelease_token is None else prerelease_token,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_single_branch is currently 0.1.1
                    # Note repo_with_single_branch isn't modelled with prereleases
                    (
                        repo_w_trunk_only_emoji_commits.__name__,
                        None,
                    ): [
                        *(
                            # when prerelease must be False, and allow_zero_version is True,
                            # the version is not bumped because of non valuable changes regardless
                            # of the major_on_zero value
                            (commits, False, major_on_zero, True, "0.1.1", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(emoji_chore_commits.__name__),
                            )
                        ),
                    ],
                    # Latest version for repo_with_single_branch_and_prereleases is
                    # currently 0.2.0
                    (
                        repo_w_trunk_only_n_prereleases_emoji_commits.__name__,
                        None,
                    ): [
                        *(
                            # when allow_zero_version is True, the version is not bumped
                            # regardless of prerelease and major_on_zero values when given
                            # non valuable changes
                            (commits, prerelease, major_on_zero, True, "0.2.0", None)
                            for prerelease in (True, False)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(emoji_chore_commits.__name__),
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ],
    ),
)
def test_version_next_w_zero_dot_versions_no_bump_emoji(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            pytest.param(
                lazy_fixture(repo_fixture_name),
                commit_messages,
                prerelease,
                "rc" if prerelease_token is None else prerelease_token,
                major_on_zero,
                allow_zero_version,
                next_release_version,
                "main" if branch_name is None else branch_name,
                marks=pytest.mark.comprehensive,
            )
            for (repo_fixture_name, prerelease_token), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_w_no_tags_scipy_commits.__name__,
                    None,
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0", None)
                        for commits in (
                            # Even when this test does not change anything, the base modification
                            # will be a minor change and thus the version will be bumped to 0.1.0
                            None,
                            # Non version bumping commits are absorbed into the previously detected minor bump
                            lazy_fixture(scipy_chore_commits.__name__),
                            # Patch commits are absorbed into the previously detected minor bump
                            lazy_fixture(scipy_patch_commits.__name__),
                            # Minor level commits are absorbed into the previously detected minor bump
                            lazy_fixture(scipy_minor_commits.__name__),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    # when prerelease is False, & major_on_zero is False, & allow_zero_version is True,
                    # the version should only be minor bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        False,
                        True,
                        "0.1.0",
                        None,
                    ),
                    # when prerelease is False, & major_on_zero is True & allow_zero_version is True,
                    # the version should be major bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    repo_w_trunk_only_scipy_commits.__name__,
                    None,
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is patch bumped because of the patch level commits
                        # regardless of the major_on_zero value
                        (
                            lazy_fixture(scipy_patch_commits.__name__),
                            False,
                            major_on_zero,
                            True,
                            "0.1.2",
                            None,
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0", None)
                        for commits in (
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    # when prerelease must be False, and allow_zero_version is True,
                    # but the major_on_zero is True, then when a major level commit is given,
                    # the version should be bumped to the next major version
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is
                # currently 0.2.0
                (
                    repo_w_trunk_only_n_prereleases_scipy_commits.__name__,
                    None,
                ): [
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(scipy_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
                        None,
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped, when given patch level commits
                    (
                        lazy_fixture(scipy_patch_commits.__name__),
                        False,
                        False,
                        True,
                        "0.2.1",
                        None,
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1", None)
                        for commits in (
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True, prerelease is True, & major_on_zero
                        # is False, the version should be minor bumped, when given commits of a
                        # minor or major level because major_on_zero = False
                        (commits, False, False, True, "0.3.0", None)
                        for commits in (
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-rc.1",
                        None,
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                        None,
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, False, major_on_zero, False, "1.0.0", None)
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                next_release_version,
                branch_name,
            ) in values  # type: ignore[attr-defined]
        ],
    ),
)
def test_version_next_w_zero_dot_versions_scipy(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo_result",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            *[
                pytest.param(
                    lazy_fixture(repo_fixture_name),
                    commit_messages,
                    prerelease,
                    "rc" if prerelease_token is None else prerelease_token,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    "main" if branch_name is None else branch_name,
                    marks=pytest.mark.comprehensive,
                )
                for (repo_fixture_name, prerelease_token), values in {
                    # Latest version for repo_with_single_branch is currently 0.1.1
                    # Note repo_with_single_branch isn't modelled with prereleases
                    (
                        repo_w_trunk_only_scipy_commits.__name__,
                        None,
                    ): [
                        *(
                            # when prerelease must be False, and allow_zero_version is True,
                            # the version is not bumped because of non valuable changes regardless
                            # of the major_on_zero value
                            (commits, False, major_on_zero, True, "0.1.1", None)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(scipy_chore_commits.__name__),
                            )
                        ),
                    ],
                    # Latest version for repo_with_single_branch_and_prereleases is
                    # currently 0.2.0
                    (
                        repo_w_trunk_only_n_prereleases_scipy_commits.__name__,
                        None,
                    ): [
                        *(
                            # when allow_zero_version is True, the version is not bumped
                            # regardless of prerelease and major_on_zero values when given
                            # non valuable changes
                            (commits, prerelease, major_on_zero, True, "0.2.0", None)
                            for prerelease in (True, False)
                            for major_on_zero in (True, False)
                            for commits in (
                                None,
                                lazy_fixture(scipy_chore_commits.__name__),
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    prerelease,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    branch_name,
                ) in values  # type: ignore[attr-defined]
            ],
        ],
    ),
)
def test_version_next_w_zero_dot_versions_no_bump_scipy(
    repo_result: BuiltRepoResult,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (no release actions should have occurred when no bump)
    assert_successful_exit_code(result, cli_cmd)
    assert f"{next_release_version}\n" == result.stdout

    # No commit has been made
    assert head_sha_before == head_after.hexsha
    assert len(tags_set_difference) == 0  # No tag created
    assert mocked_git_fetch.call_count == 0  # no git fetch called
    assert mocked_git_push.call_count == 0  # no git push of tag or commit
    assert post_mocker.call_count == 0  # no vcs release


@pytest.mark.parametrize(
    str.join(
        " ,",
        [
            "repo_result",
            "commit_parser",
            "commit_messages",
            "prerelease",
            "prerelease_token",
            "major_on_zero",
            "allow_zero_version",
            "next_release_version",
            "branch_name",
        ],
    ),
    xdist_sort_hack(
        [
            (
                # Latest version for repo_w_initial_commit is currently 0.0.0
                # with no changes made it should be 0.0.0
                lazy_fixture(repo_w_initial_commit.__name__),
                ConventionalCommitParser.__name__.replace("CommitParser", "").lower(),
                None,
                False,
                "rc",
                False,
                True,
                "0.0.0",
                "main",
            ),
            *[
                pytest.param(
                    lazy_fixture(repo_w_initial_commit.__name__),
                    str.replace(parser_class_name, "CommitParser", "").lower(),
                    commit_messages,
                    prerelease,
                    prerelease_token,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                    "main",
                    marks=pytest.mark.comprehensive,
                )
                for prerelease_token, values in {
                    # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                    # It's biggest change type is minor, so the next version should be 0.1.0
                    "rc": [
                        *(
                            # when prerelease is False, major_on_zero is True & False, & allow_zero_version is True
                            # the version should be 0.0.0, when no distintive changes have been made since the
                            # start of the project
                            (commits, parser, prerelease, major_on_zero, True, "0.0.0")
                            for prerelease in (True, False)
                            for major_on_zero in (True, False)
                            for commits, parser in (
                                # No commits added, so base is just initial commit at 0.0.0
                                (None, ConventionalCommitParser.__name__),
                                # Chore like commits also don't trigger a version bump so it stays 0.0.0
                                (
                                    lazy_fixture(conventional_chore_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_chore_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_chore_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            (commits, parser, True, major_on_zero, True, "0.0.1-rc.1")
                            for major_on_zero in (True, False)
                            for commits, parser in (
                                # when prerelease is True & allow_zero_version is True, the version should be
                                # a patch bump as a prerelease version, because of the patch level commits
                                # major_on_zero is irrelevant here as we are only applying patch commits
                                (
                                    lazy_fixture(conventional_patch_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_patch_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_patch_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            (commits, parser, False, major_on_zero, True, "0.0.1")
                            for major_on_zero in (True, False)
                            for commits, parser in (
                                # when prerelease is False, & allow_zero_version is True, the version should be
                                # a patch bump because of the patch commits added
                                # major_on_zero is irrelevant here as we are only applying patch commits
                                (
                                    lazy_fixture(conventional_patch_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_patch_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_patch_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            (commits, parser, True, False, True, "0.1.0-rc.1")
                            for commits, parser in (
                                # when prerelease is False, & major_on_zero is False, the version should be
                                # a minor bump because of the minor commits added
                                (
                                    lazy_fixture(conventional_minor_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_minor_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_minor_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                # Given the major_on_zero is False and the version is starting at 0.0.0,
                                # the major level commits are limited to only causing a minor level bump
                                (
                                    lazy_fixture(conventional_major_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_major_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_major_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            (commits, parser, False, False, True, "0.1.0")
                            for commits, parser in (
                                # when prerelease is False,
                                # major_on_zero is False, & allow_zero_version is True
                                # the version should be a minor bump of 0.0.0
                                # because of the minor commits added and zero version is allowed
                                (
                                    lazy_fixture(conventional_minor_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_minor_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_minor_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                # Given the major_on_zero is False and the version is starting at 0.0.0,
                                # the major level commits are limited to only causing a minor level bump
                                (
                                    lazy_fixture(conventional_major_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_major_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_major_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            # when prerelease is True, & allow_zero_version is False, the version should be
                            # a prerelease version 1.0.0-rc.1, across the board when any valuable change
                            # is made because of the allow_zero_version is False, major_on_zero is ignored
                            # when allow_zero_version is False (but we still test it)
                            (commits, parser, True, major_on_zero, False, "1.0.0-rc.1")
                            for major_on_zero in (True, False)
                            for commits, parser in (
                                # parser doesn't matter here as long as it detects a NO_RELEASE on Initial Commit
                                (None, ConventionalCommitParser.__name__),
                                (
                                    lazy_fixture(conventional_chore_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_patch_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_minor_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_major_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_chore_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_patch_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_minor_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_major_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_chore_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_patch_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_minor_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_major_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                        *(
                            # when prerelease is True, & allow_zero_version is False, the version should be
                            # 1.0.0, across the board when any valuable change
                            # is made because of the allow_zero_version is False. major_on_zero is ignored
                            # when allow_zero_version is False (but we still test it)
                            (commits, parser, False, major_on_zero, False, "1.0.0")
                            for major_on_zero in (True, False)
                            for commits, parser in (
                                (None, ConventionalCommitParser.__name__),
                                (
                                    lazy_fixture(conventional_chore_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_patch_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_minor_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(conventional_major_commits.__name__),
                                    ConventionalCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_chore_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_patch_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_minor_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(emoji_major_commits.__name__),
                                    EmojiCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_chore_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_patch_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_minor_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                                (
                                    lazy_fixture(scipy_major_commits.__name__),
                                    ScipyCommitParser.__name__,
                                ),
                            )
                        ),
                    ],
                }.items()
                for (
                    commit_messages,
                    parser_class_name,
                    prerelease,
                    major_on_zero,
                    allow_zero_version,
                    next_release_version,
                ) in values  # type: ignore[attr-defined]
            ],
        ],
    ),
)
def test_version_next_w_zero_dot_versions_minimums(
    repo_result: BuiltRepoResult,
    commit_parser: str,
    commit_messages: list[str],
    prerelease: bool,
    prerelease_token: str,
    next_release_version: str,
    branch_name: str,
    major_on_zero: bool,
    allow_zero_version: bool,
    run_cli: RunCliFn,
    file_in_repo: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
):
    repo = repo_result["repo"]

    # setup: select the branch we desire for the next bump
    if repo.active_branch.name != branch_name:
        repo.heads[branch_name].checkout()

    # setup: update pyproject.toml with the necessary settings
    update_pyproject_toml("tool.semantic_release.commit_parser", commit_parser)
    update_pyproject_toml(
        "tool.semantic_release.allow_zero_version", allow_zero_version
    )
    update_pyproject_toml("tool.semantic_release.major_on_zero", major_on_zero)

    # setup: apply commits to the repo
    stable_now_datetime = stable_now_date()
    commit_timestamp_gen = (
        (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
        for i in count(step=1)
    )
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message, a=True, date=next(commit_timestamp_gen))
        # Fake an automated push to remote by updating the remote tracking branch
        repo.git.update_ref(
            f"refs/remotes/origin/{repo.active_branch.name}",
            repo.head.commit.hexsha,
        )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}

    # Derive the cli arguments based on parameter input
    prerelease_args = list(
        filter(
            None,
            [
                "--as-prerelease" if prerelease else "",
                *(["--prerelease-token", prerelease_token] if prerelease else []),
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *prerelease_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = cast("set[str]", set.difference(tags_after, tags_before))

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made (regardless of precommit)
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    assert len(tags_set_difference) == 1  # A tag has been created
    assert f"v{next_release_version}" in tags_set_difference

    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1  # vcs release creation occurred
