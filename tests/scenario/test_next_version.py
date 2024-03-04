from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

# Limitation in pytest-lazy-fixture - see https://stackoverflow.com/a/69884019
from pytest_lazyfixture import lazy_fixture

from semantic_release.version.algorithm import next_version
from semantic_release.version.translator import VersionTranslator

from tests.const import (
    ANGULAR_COMMITS_MAJOR,
    ANGULAR_COMMITS_MINOR,
    ANGULAR_COMMITS_PATCH,
    EMOJI_COMMITS_MAJOR,
    EMOJI_COMMITS_MINOR,
    EMOJI_COMMITS_PATCH,
    TAG_COMMITS_MAJOR,
    TAG_COMMITS_MINOR,
    TAG_COMMITS_PATCH,
)
from tests.fixtures import (
    default_angular_parser,
    default_emoji_parser,
    default_scipy_parser,
    default_tag_parser,
    repo_w_github_flow_w_feature_release_channel_angular_commits,
    repo_w_github_flow_w_feature_release_channel_emoji_commits,
    repo_w_github_flow_w_feature_release_channel_scipy_commits,
    repo_w_github_flow_w_feature_release_channel_tag_commits,
    repo_with_git_flow_and_release_channels_angular_commits,
    repo_with_git_flow_and_release_channels_emoji_commits,
    repo_with_git_flow_and_release_channels_scipy_commits,
    repo_with_git_flow_and_release_channels_tag_commits,
    repo_with_git_flow_angular_commits,
    repo_with_git_flow_emoji_commits,
    repo_with_git_flow_scipy_commits,
    repo_with_git_flow_tag_commits,
    repo_with_no_tags_angular_commits,
    repo_with_no_tags_emoji_commits,
    repo_with_no_tags_scipy_commits,
    repo_with_no_tags_tag_commits,
    repo_with_single_branch_and_prereleases_angular_commits,
    repo_with_single_branch_and_prereleases_emoji_commits,
    repo_with_single_branch_and_prereleases_scipy_commits,
    repo_with_single_branch_and_prereleases_tag_commits,
    repo_with_single_branch_angular_commits,
    repo_with_single_branch_emoji_commits,
    repo_with_single_branch_scipy_commits,
    repo_with_single_branch_tag_commits,
    scipy_chore_commits,
    scipy_major_commits,
    scipy_minor_commits,
    scipy_patch_commits,
)
from tests.util import add_text_to_file, xdist_sort_hack

if TYPE_CHECKING:
    from git import Repo


@pytest.fixture
def angular_major_commits():
    return ANGULAR_COMMITS_MAJOR


@pytest.fixture
def angular_minor_commits():
    return ANGULAR_COMMITS_MINOR


@pytest.fixture
def angular_patch_commits():
    return ANGULAR_COMMITS_PATCH


@pytest.fixture
def angular_chore_commits() -> list[str]:
    return ["chore: change dev tool configuration"]


@pytest.fixture
def emoji_major_commits():
    return EMOJI_COMMITS_MAJOR


@pytest.fixture
def emoji_minor_commits():
    return EMOJI_COMMITS_MINOR


@pytest.fixture
def emoji_patch_commits():
    return EMOJI_COMMITS_PATCH


@pytest.fixture
def emoji_chore_commits() -> list[str]:
    return [":broom: change dev tool configuration"]


@pytest.fixture
def tag_patch_commits():
    return TAG_COMMITS_PATCH


@pytest.fixture
def tag_minor_commits():
    return TAG_COMMITS_MINOR


@pytest.fixture
def tag_major_commits():
    return TAG_COMMITS_MAJOR


@pytest.fixture
def tag_chore_commits() -> list[str]:
    return [":broom: change dev tool configuration"]


# TODO: it'd be nice to not hard-code the versions into
# this testing


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
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.2.0")
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(angular_patch_commits.__name__), False, "1.2.0"),
                    (
                        lazy_fixture(angular_patch_commits.__name__),
                        True,
                        "1.2.0-alpha.3",
                    ),
                    (lazy_fixture(angular_minor_commits.__name__), False, "1.2.0"),
                    (
                        lazy_fixture(angular_minor_commits.__name__),
                        True,
                        "1.2.0-alpha.3",
                    ),
                    (lazy_fixture(angular_major_commits.__name__), False, "2.0.0"),
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        True,
                        "2.0.0-alpha.1",
                    ),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_and_release_channels_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.1.0")
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(angular_patch_commits.__name__), False, "1.1.0"),
                    (
                        lazy_fixture(angular_patch_commits.__name__),
                        True,
                        "1.1.0-alpha.4",
                    ),
                    (lazy_fixture(angular_minor_commits.__name__), False, "1.1.0"),
                    (
                        lazy_fixture(angular_minor_commits.__name__),
                        True,
                        "1.1.0-alpha.4",
                    ),
                    (lazy_fixture(angular_major_commits.__name__), False, "2.0.0"),
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        True,
                        "2.0.0-alpha.1",
                    ),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
@pytest.mark.parametrize("allow_zero_version", [True, False])
def test_algorithm_no_zero_dot_versions_angular(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.2.0")
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(emoji_patch_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(emoji_patch_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(emoji_minor_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(emoji_minor_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(emoji_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(emoji_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_and_release_channels_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.1.0")
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(emoji_patch_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(emoji_patch_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(emoji_minor_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(emoji_minor_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(emoji_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(emoji_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
@pytest.mark.parametrize("allow_zero_version", [True, False])
def test_algorithm_no_zero_dot_versions_emoji(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-alpha.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.2.0")
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(scipy_patch_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(scipy_patch_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(scipy_minor_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(scipy_minor_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(scipy_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(scipy_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_and_release_channels_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.1.0")
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(scipy_patch_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(scipy_patch_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(scipy_minor_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(scipy_minor_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(scipy_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(scipy_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
@pytest.mark.parametrize("allow_zero_version", [True, False])
def test_algorithm_no_zero_dot_versions_scipy(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
                # The last full release version was 1.1.1, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.2.0")
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(tag_patch_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(tag_patch_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(tag_minor_commits.__name__), False, "1.2.0"),
                    (lazy_fixture(tag_minor_commits.__name__), True, "1.2.0-alpha.3"),
                    (lazy_fixture(tag_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(tag_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is
                # currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor
                # prerelease
                (
                    repo_with_git_flow_and_release_channels_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                        )
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, "1.1.0")
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                        )
                    ),
                    (lazy_fixture(tag_patch_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(tag_patch_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(tag_minor_commits.__name__), False, "1.1.0"),
                    (lazy_fixture(tag_minor_commits.__name__), True, "1.1.0-alpha.4"),
                    (lazy_fixture(tag_major_commits.__name__), False, "2.0.0"),
                    (lazy_fixture(tag_major_commits.__name__), True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
@pytest.mark.parametrize("allow_zero_version", [True, False])
def test_algorithm_no_zero_dot_versions_tag(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


#####
# 0.x.y versions
#####


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo",
            "commit_parser",
            "translator",
            "commit_messages",
            "prerelease",
            "major_on_zero",
            "allow_zero_version",
            "expected_new_version",
        ],
    ),
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_with_no_tags_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0")
                        for commits in (
                            # Even when this test does not change anything, the base modification
                            # will be a minor change and thus the version will be bumped to 0.1.0
                            None,
                            # Non version bumping commits are absorbed into the previously detected minor bump
                            lazy_fixture(angular_chore_commits.__name__),
                            # Patch commits are absorbed into the previously detected minor bump
                            lazy_fixture(angular_patch_commits.__name__),
                            # Minor level commits are absorbed into the previously detected minor bump
                            lazy_fixture(angular_minor_commits.__name__),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    # when prerelease is False, & major_on_zero is False, & allow_zero_version is True,
                    # the version should only be minor bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        False,
                        False,
                        True,
                        "0.1.0",
                    ),
                    # when prerelease is False, & major_on_zero is True & allow_zero_version is True,
                    # the version should be major bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    repo_with_single_branch_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is not bumped because of non valuable changes regardless
                        # of the major_on_zero value
                        (commits, False, major_on_zero, True, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is patch bumped because of the patch level commits
                        # regardless of the major_on_zero value
                        (
                            lazy_fixture(angular_patch_commits.__name__),
                            False,
                            major_on_zero,
                            True,
                            "0.1.2",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0")
                        for commits in (
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    # when prerelease must be False, and allow_zero_version is True,
                    # but the major_on_zero is True, then when a major level commit is given,
                    # the version should be bumped to the next major version
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is
                # currently 0.2.0
                (
                    repo_with_single_branch_and_prereleases_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when allow_zero_version is True, the version is not bumped
                        # regardless of prerelease and major_on_zero values when given
                        # non valuable changes
                        (commits, prerelease, major_on_zero, True, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(angular_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped, when given patch level commits
                    (
                        lazy_fixture(angular_patch_commits.__name__),
                        False,
                        False,
                        True,
                        "0.2.1",
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1")
                        for commits in (
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped, when given commits of a minor or major level because
                        # major_on_zero = False
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-rc.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently
                # 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor
                # prerelease
                (
                    repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
                    default_angular_parser.__name__,
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        # when prerelease is True, & major_on_zero is True & False,
                        # the version is not bumped because nothing of importance happened
                        (commits, True, major_on_zero, True, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                        )
                    ),
                    *(
                        (commits, True, False, True, "0.3.0-beta.2")
                        for commits in (
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given patch level commits
                            # because the last full release was 0.2.0 and the prior prerelease consumes the
                            # patch bump
                            lazy_fixture(angular_patch_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(angular_minor_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given new breaking changes
                            # because major_on_zero is false, the last full release was 0.2.0
                            # and the prior prerelease consumes the breaking changes
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    *(
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            # Even though we are not making any changes, and prerelease is
                            # off, we look at the last full version which is 0.2.0 and
                            # consider the previous minor commit to cause the bump to 0.3.0
                            None,
                            # same as None, but with a chore commit
                            lazy_fixture(angular_chore_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # patch bumped, when given patch level commits because last full version was 0.2.0
                            # and it was previously identified (from the prerelease) that a minor commit
                            # exists between 0.2.0 and now
                            lazy_fixture(angular_patch_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(angular_minor_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given new breaking changes because
                            # major_on_zero is false and last full version was 0.2.0
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits. The previous prerelease is ignored because of the major
                    # bump
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-beta.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(angular_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # as a prerelease value due to prerelease=True, across the board
                        # regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            lazy_fixture(angular_chore_commits.__name__),
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # across the board regardless of the major_on_zero value
                        (commits, False, True, False, "1.0.0")
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            # Same as above, even though our change does not trigger a bump normally
                            lazy_fixture(angular_chore_commits.__name__),
                            # Even though we apply more patch, minor, major commits, the previous
                            # minor commit (in the prerelase tag) triggers a higher bump &
                            # with allow_zero_version=False, and ignore prereleases, we bump to 1.0.0
                            lazy_fixture(angular_patch_commits.__name__),
                            lazy_fixture(angular_minor_commits.__name__),
                            lazy_fixture(angular_major_commits.__name__),
                        )
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            ) in values
        ],
    ),
)
def test_algorithm_with_zero_dot_versions_angular(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo",
            "commit_parser",
            "translator",
            "commit_messages",
            "prerelease",
            "major_on_zero",
            "allow_zero_version",
            "expected_new_version",
        ],
    ),
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_with_no_tags_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0")
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
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0")
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
                    repo_with_single_branch_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is not bumped because of non valuable changes regardless
                        # of the major_on_zero value
                        (commits, False, major_on_zero, True, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
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
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0")
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
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0")
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
                    repo_with_single_branch_and_prereleases_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when allow_zero_version is True, the version is not bumped
                        # regardless of prerelease and major_on_zero values when given
                        # non valuable changes
                        (commits, prerelease, major_on_zero, True, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(emoji_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
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
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1")
                        for commits in (
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped, when given commits of a minor or major level because
                        # major_on_zero = False
                        (commits, False, False, True, "0.3.0")
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
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1")
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
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently
                # 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor
                # prerelease
                (
                    repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
                    default_emoji_parser.__name__,
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        # when prerelease is True, & major_on_zero is True & False,
                        # the version is not bumped because nothing of importance happened
                        (commits, True, major_on_zero, True, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                        )
                    ),
                    *(
                        (commits, True, False, True, "0.3.0-beta.2")
                        for commits in (
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given patch level commits
                            # because the last full release was 0.2.0 and the prior prerelease consumes the
                            # patch bump
                            lazy_fixture(emoji_patch_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(emoji_minor_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given new breaking changes
                            # because major_on_zero is false, the last full release was 0.2.0
                            # and the prior prerelease consumes the breaking changes
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    *(
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            # Even though we are not making any changes, and prerelease is
                            # off, we look at the last full version which is 0.2.0 and
                            # consider the previous minor commit to cause the bump to 0.3.0
                            None,
                            # same as None, but with a chore commit
                            lazy_fixture(emoji_chore_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # patch bumped, when given patch level commits because last full version was 0.2.0
                            # and it was previously identified (from the prerelease) that a minor commit
                            # exists between 0.2.0 and now
                            lazy_fixture(emoji_patch_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(emoji_minor_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given new breaking changes because
                            # major_on_zero is false and last full version was 0.2.0
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits. The previous prerelease is ignored because of the major
                    # bump
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-beta.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(emoji_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # as a prerelease value due to prerelease=True, across the board
                        # regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            lazy_fixture(emoji_chore_commits.__name__),
                            lazy_fixture(emoji_patch_commits.__name__),
                            lazy_fixture(emoji_minor_commits.__name__),
                            lazy_fixture(emoji_major_commits.__name__),
                        )
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # across the board regardless of the major_on_zero value
                        (commits, False, True, False, "1.0.0")
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            # Same as above, even though our change does not trigger a bump normally
                            lazy_fixture(emoji_chore_commits.__name__),
                            # Even though we apply more patch, minor, major commits, the previous
                            # minor commit (in the prerelase tag) triggers a higher bump &
                            # with allow_zero_version=False, and ignore prereleases, we bump to 1.0.0
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
                expected_new_version,
            ) in values
        ],
    ),
)
def test_algorithm_with_zero_dot_versions_emoji(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo",
            "commit_parser",
            "translator",
            "commit_messages",
            "prerelease",
            "major_on_zero",
            "allow_zero_version",
            "expected_new_version",
        ],
    ),
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_with_no_tags_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0")
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
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0")
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
                    repo_with_single_branch_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is not bumped because of non valuable changes regardless
                        # of the major_on_zero value
                        (commits, False, major_on_zero, True, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
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
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0")
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
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0")
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
                    repo_with_single_branch_and_prereleases_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when allow_zero_version is True, the version is not bumped
                        # regardless of prerelease and major_on_zero values when given
                        # non valuable changes
                        (commits, prerelease, major_on_zero, True, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(scipy_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
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
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1")
                        for commits in (
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped, when given commits of a minor or major level because
                        # major_on_zero = False
                        (commits, False, False, True, "0.3.0")
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
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1")
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
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently
                # 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor
                # prerelease
                (
                    repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
                    default_scipy_parser.__name__,
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        # when prerelease is True, & major_on_zero is True & False,
                        # the version is not bumped because nothing of importance happened
                        (commits, True, major_on_zero, True, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                        )
                    ),
                    *(
                        (commits, True, False, True, "0.3.0-beta.2")
                        for commits in (
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given patch level commits
                            # because the last full release was 0.2.0 and the prior prerelease consumes the
                            # patch bump
                            lazy_fixture(scipy_patch_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(scipy_minor_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given new breaking changes
                            # because major_on_zero is false, the last full release was 0.2.0
                            # and the prior prerelease consumes the breaking changes
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    *(
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            # Even though we are not making any changes, and prerelease is
                            # off, we look at the last full version which is 0.2.0 and
                            # consider the previous minor commit to cause the bump to 0.3.0
                            None,
                            # same as None, but with a chore commit
                            lazy_fixture(scipy_chore_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # patch bumped, when given patch level commits because last full version was 0.2.0
                            # and it was previously identified (from the prerelease) that a minor commit
                            # exists between 0.2.0 and now
                            lazy_fixture(scipy_patch_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(scipy_minor_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given new breaking changes because
                            # major_on_zero is false and last full version was 0.2.0
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits. The previous prerelease is ignored because of the major
                    # bump
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-beta.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(scipy_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # as a prerelease value due to prerelease=True, across the board
                        # regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            lazy_fixture(scipy_chore_commits.__name__),
                            lazy_fixture(scipy_patch_commits.__name__),
                            lazy_fixture(scipy_minor_commits.__name__),
                            lazy_fixture(scipy_major_commits.__name__),
                        )
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # across the board regardless of the major_on_zero value
                        (commits, False, True, False, "1.0.0")
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            # Same as above, even though our change does not trigger a bump normally
                            lazy_fixture(scipy_chore_commits.__name__),
                            # Even though we apply more patch, minor, major commits, the previous
                            # minor commit (in the prerelase tag) triggers a higher bump &
                            # with allow_zero_version=False, and ignore prereleases, we bump to 1.0.0
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
                expected_new_version,
            ) in values
        ],
    ),
)
def test_algorithm_with_zero_dot_versions_scipy(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "repo",
            "commit_parser",
            "translator",
            "commit_messages",
            "prerelease",
            "major_on_zero",
            "allow_zero_version",
            "expected_new_version",
        ],
    ),
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    repo_with_no_tags_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease is False, & major_on_zero is False &
                        # allow_zero_version is True, the version should be
                        # 0.1.0, with the given commits
                        (commits, False, False, True, "0.1.0")
                        for commits in (
                            # Even when this test does not change anything, the base modification
                            # will be a minor change and thus the version will be bumped to 0.1.0
                            None,
                            # Non version bumping commits are absorbed into the previously detected minor bump
                            lazy_fixture(tag_chore_commits.__name__),
                            # Patch commits are absorbed into the previously detected minor bump
                            lazy_fixture(tag_patch_commits.__name__),
                            # Minor level commits are absorbed into the previously detected minor bump
                            lazy_fixture(tag_minor_commits.__name__),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    # when prerelease is False, & major_on_zero is False, & allow_zero_version is True,
                    # the version should only be minor bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        False,
                        False,
                        True,
                        "0.1.0",
                    ),
                    # when prerelease is False, & major_on_zero is True & allow_zero_version is True,
                    # the version should be major bumped when provided major commits because
                    # of the major_on_zero value
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is False, & allow_zero_version is False, the version should be
                        # 1.0.0, across the board because 0 is not a valid major version.
                        # major_on_zero is ignored as it is not relevant but tested for completeness
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    repo_with_single_branch_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is not bumped because of non valuable changes regardless
                        # of the major_on_zero value
                        (commits, False, major_on_zero, True, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in (None, lazy_fixture(tag_chore_commits.__name__))
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is patch bumped because of the patch level commits
                        # regardless of the major_on_zero value
                        (
                            lazy_fixture(tag_patch_commits.__name__),
                            False,
                            major_on_zero,
                            True,
                            "0.1.2",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        # when prerelease must be False, and allow_zero_version is True,
                        # the version is minor bumped because of the major_on_zero value=False
                        (commits, False, False, True, "0.2.0")
                        for commits in (
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    # when prerelease must be False, and allow_zero_version is True,
                    # but the major_on_zero is True, then when a major level commit is given,
                    # the version should be bumped to the next major version
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease must be False, & allow_zero_version is False, the version should be
                        # 1.0.0, with any change regardless of major_on_zero
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is
                # currently 0.2.0
                (
                    repo_with_single_branch_and_prereleases_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(),
                ): [
                    *(
                        # when allow_zero_version is True, the version is not bumped
                        # regardless of prerelease and major_on_zero values when given
                        # non valuable changes
                        (commits, prerelease, major_on_zero, True, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in (None, lazy_fixture(tag_chore_commits.__name__))
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped as a prerelease version, when given patch level commits
                    (
                        lazy_fixture(tag_patch_commits.__name__),
                        True,
                        False,
                        True,
                        "0.2.1-rc.1",
                    ),
                    # when allow_zero_version is True,
                    # prerelease is False, & major_on_zero is False, the version should be
                    # patch bumped, when given patch level commits
                    (
                        lazy_fixture(tag_patch_commits.__name__),
                        False,
                        False,
                        True,
                        "0.2.1",
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped as a prerelease version, when given commits of a minor or major level
                        (commits, True, False, True, "0.3.0-rc.1")
                        for commits in (
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    *(
                        # when allow_zero_version is True,
                        # prerelease is True, & major_on_zero is False, the version should be
                        # minor bumped, when given commits of a minor or major level because
                        # major_on_zero = False
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-rc.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0 as a prerelease version, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-rc.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    *(
                        # when prerelease is True, & allow_zero_version is False, the version should be
                        # bumped to 1.0.0, when given any/none commits
                        # because 0.x is no longer a valid version regardless of the major_on_zero value
                        (commits, False, major_on_zero, False, "1.0.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently
                # 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor
                # prerelease
                (
                    repo_w_github_flow_w_feature_release_channel_tag_commits.__name__,
                    default_tag_parser.__name__,
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        # when prerelease is True, & major_on_zero is True & False,
                        # the version is not bumped because nothing of importance happened
                        (commits, True, major_on_zero, True, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (None, lazy_fixture(tag_chore_commits.__name__))
                    ),
                    *(
                        (commits, True, False, True, "0.3.0-beta.2")
                        for commits in (
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given patch level commits
                            # because the last full release was 0.2.0 and the prior prerelease consumes the
                            # patch bump
                            lazy_fixture(tag_patch_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(tag_minor_commits.__name__),
                            # when prerelease is True, & major_on_zero is False, the version should be
                            # increment the next prerelease version, when given new breaking changes
                            # because major_on_zero is false, the last full release was 0.2.0
                            # and the prior prerelease consumes the breaking changes
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    *(
                        (commits, False, False, True, "0.3.0")
                        for commits in (
                            # Even though we are not making any changes, and prerelease is
                            # off, we look at the last full version which is 0.2.0 and
                            # consider the previous minor commit to cause the bump to 0.3.0
                            None,
                            # same as None, but with a chore commit
                            lazy_fixture(tag_chore_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # patch bumped, when given patch level commits because last full version was 0.2.0
                            # and it was previously identified (from the prerelease) that a minor commit
                            # exists between 0.2.0 and now
                            lazy_fixture(tag_patch_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given patch level commits because last full version was 0.2.0
                            lazy_fixture(tag_minor_commits.__name__),
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # minor bumped, when given new breaking changes because
                            # major_on_zero is false and last full version was 0.2.0
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    # when prerelease is True, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0 as a prerelease version, when
                    # given major level commits. The previous prerelease is ignored because of the major
                    # bump
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        True,
                        True,
                        True,
                        "1.0.0-beta.1",
                    ),
                    # when prerelease is False, & major_on_zero is True, and allow_zero_version
                    # is True, the version should be bumped to 1.0.0, when given major level commits
                    (
                        lazy_fixture(tag_major_commits.__name__),
                        False,
                        True,
                        True,
                        "1.0.0",
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # as a prerelease value due to prerelease=True, across the board
                        # regardless of the major_on_zero value
                        (commits, True, major_on_zero, False, "1.0.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            lazy_fixture(tag_chore_commits.__name__),
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                    *(
                        # Since allow_zero_version is False, the version should be 1.0.0
                        # across the board regardless of the major_on_zero value
                        (commits, False, True, False, "1.0.0")
                        for commits in (
                            # None & chore commits are absorbed into the previously detected minor bump
                            # and because 0 versions are not allowed
                            None,
                            # Same as above, even though our change does not trigger a bump normally
                            lazy_fixture(tag_chore_commits.__name__),
                            # Even though we apply more patch, minor, major commits, the previous
                            # minor commit (in the prerelase tag) triggers a higher bump &
                            # with allow_zero_version=False, and ignore prereleases, we bump to 1.0.0
                            lazy_fixture(tag_patch_commits.__name__),
                            lazy_fixture(tag_minor_commits.__name__),
                            lazy_fixture(tag_major_commits.__name__),
                        )
                    ),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            ) in values
        ],
    ),
)
def test_algorithm_with_zero_dot_versions_tag(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)


@pytest.mark.parametrize(
    str.join(
        " ,",
        [
            "repo",
            "commit_parser",
            "translator",
            "commit_messages",
            "prerelease",
            "major_on_zero",
            "allow_zero_version",
            "expected_new_version",
        ],
    ),
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_with_no_tags_tag_commits.__name__),
                lazy_fixture(parser_fixture_name),
                translator[0],
                commit_messages,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            )
            for translator, values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (VersionTranslator(),): [
                    *(
                        # when prerelease is False, major_on_zero is True & False, & allow_zero_version is True
                        # the version should be 0.0.0, when no distintive changes have been made since the
                        # start of the project
                        (commits, parser, prerelease, major_on_zero, True, "0.0.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits, parser in (
                            # No commits added, so base is just initial commit at 0.0.0
                            (None, default_tag_parser.__name__),
                            # Chore like commits also don't trigger a version bump so it stays 0.0.0
                            (
                                lazy_fixture(angular_chore_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_chore_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_chore_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_chore_commits.__name__),
                                default_tag_parser.__name__,
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
                                lazy_fixture(angular_patch_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_patch_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_patch_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_patch_commits.__name__),
                                default_tag_parser.__name__,
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
                                lazy_fixture(angular_patch_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_patch_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_patch_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_patch_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                        )
                    ),
                    *(
                        (commits, parser, True, False, True, "0.1.0-rc.1")
                        for commits, parser in (
                            # when prerelease is False, & major_on_zero is False, the version should be
                            # a minor bump because of the minor commits added
                            (
                                lazy_fixture(angular_minor_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_minor_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_minor_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_minor_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            (
                                lazy_fixture(angular_major_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_major_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_major_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_major_commits.__name__),
                                default_tag_parser.__name__,
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
                                lazy_fixture(angular_minor_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_minor_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_minor_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_minor_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            # Given the major_on_zero is False and the version is starting at 0.0.0,
                            # the major level commits are limited to only causing a minor level bump
                            (
                                lazy_fixture(angular_major_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_major_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_major_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_major_commits.__name__),
                                default_tag_parser.__name__,
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
                            (None, default_tag_parser.__name__),
                            (
                                lazy_fixture(angular_chore_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_patch_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_minor_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_major_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_chore_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_patch_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_minor_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_major_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_chore_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_patch_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_minor_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_major_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_chore_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_patch_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_minor_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_major_commits.__name__),
                                default_tag_parser.__name__,
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
                            (None, default_tag_parser.__name__),
                            (
                                lazy_fixture(angular_chore_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_patch_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_minor_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(angular_major_commits.__name__),
                                default_angular_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_chore_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_patch_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_minor_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(emoji_major_commits.__name__),
                                default_emoji_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_chore_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_patch_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_minor_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(scipy_major_commits.__name__),
                                default_scipy_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_chore_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_patch_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_minor_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                            (
                                lazy_fixture(tag_major_commits.__name__),
                                default_tag_parser.__name__,
                            ),
                        )
                    ),
                ],
            }.items()
            for (
                commit_messages,
                parser_fixture_name,
                prerelease,
                major_on_zero,
                allow_zero_version,
                expected_new_version,
            ) in values
        ],
    ),
)
def test_algorithm_with_zero_dot_versions_minimums(
    repo: Repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
    allow_zero_version,
):
    # Setup
    # Move tree down to the Initial Commit
    initial_commit = repo.git.log("--max-parents=0", "--format=%H").strip()
    repo.git.reset("--hard", initial_commit)

    for commit_message in commit_messages or []:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Action
    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero, allow_zero_version
    )

    # Verify
    assert expected_new_version == str(new_version)
