import pytest

# Limitation in pytest-lazy-fixture - see https://stackoverflow.com/a/69884019
from pytest import lazy_fixture

from semantic_release.version.algorithm import next_version
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

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
from tests.util import add_text_to_file, xdist_sort_hack

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
                # The last full release version was 1.1.1, so it's had a minor prerelease
                (
                    "repo_with_git_flow_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.2.0") for commits in ([], ["uninteresting"])),
                    (ANGULAR_COMMITS_PATCH, False, "1.2.0"),
                    (ANGULAR_COMMITS_PATCH, True, "1.2.0-alpha.3"),
                    (ANGULAR_COMMITS_MINOR, False, "1.2.0"),
                    (ANGULAR_COMMITS_MINOR, True, "1.2.0-alpha.3"),
                    (ANGULAR_COMMITS_MAJOR, False, "2.0.0"),
                    (ANGULAR_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor prerelease
                (
                    "repo_with_git_flow_and_release_channels_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.1.0") for commits in ([], ["uninteresting"])),
                    (ANGULAR_COMMITS_PATCH, False, "1.1.0"),
                    (ANGULAR_COMMITS_PATCH, True, "1.1.0-alpha.4"),
                    (ANGULAR_COMMITS_MINOR, False, "1.1.0"),
                    (ANGULAR_COMMITS_MINOR, True, "1.1.0-alpha.4"),
                    (ANGULAR_COMMITS_MAJOR, False, "2.0.0"),
                    (ANGULAR_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
def test_algorithm_no_zero_dot_versions_angular(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


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
                # The last full release version was 1.1.1, so it's had a minor prerelease
                (
                    "repo_with_git_flow_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.2.0") for commits in ([], ["uninteresting"])),
                    (EMOJI_COMMITS_PATCH, False, "1.2.0"),
                    (EMOJI_COMMITS_PATCH, True, "1.2.0-alpha.3"),
                    (EMOJI_COMMITS_MINOR, False, "1.2.0"),
                    (EMOJI_COMMITS_MINOR, True, "1.2.0-alpha.3"),
                    (EMOJI_COMMITS_MAJOR, False, "2.0.0"),
                    (EMOJI_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor prerelease
                (
                    "repo_with_git_flow_and_release_channels_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.1.0") for commits in ([], ["uninteresting"])),
                    (EMOJI_COMMITS_PATCH, False, "1.1.0"),
                    (EMOJI_COMMITS_PATCH, True, "1.1.0-alpha.4"),
                    (EMOJI_COMMITS_MINOR, False, "1.1.0"),
                    (EMOJI_COMMITS_MINOR, True, "1.1.0-alpha.4"),
                    (EMOJI_COMMITS_MAJOR, False, "2.0.0"),
                    (EMOJI_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
def test_algorithm_no_zero_dot_versions_emoji(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


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
                # The last full release version was 1.1.1, so it's had a minor prerelease
                (
                    "repo_with_git_flow_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.2.0") for commits in ([], ["uninteresting"])),
                    (lazy_fixture("scipy_commits_patch"), False, "1.2.0"),
                    (lazy_fixture("scipy_commits_patch"), True, "1.2.0-alpha.3"),
                    (lazy_fixture("scipy_commits_minor"), False, "1.2.0"),
                    (lazy_fixture("scipy_commits_minor"), True, "1.2.0-alpha.3"),
                    (lazy_fixture("scipy_commits_major"), False, "2.0.0"),
                    (lazy_fixture("scipy_commits_major"), True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor prerelease
                (
                    "repo_with_git_flow_and_release_channels_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.1.0") for commits in ([], ["uninteresting"])),
                    (lazy_fixture("scipy_commits_patch"), False, "1.1.0"),
                    (lazy_fixture("scipy_commits_patch"), True, "1.1.0-alpha.4"),
                    (lazy_fixture("scipy_commits_minor"), False, "1.1.0"),
                    (lazy_fixture("scipy_commits_minor"), True, "1.1.0-alpha.4"),
                    (lazy_fixture("scipy_commits_major"), False, "2.0.0"),
                    (lazy_fixture("scipy_commits_major"), True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
def test_algorithm_no_zero_dot_versions_scipy(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


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
                # The last full release version was 1.1.1, so it's had a minor prerelease
                (
                    "repo_with_git_flow_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.2.0-alpha.2")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.2.0") for commits in ([], ["uninteresting"])),
                    (TAG_COMMITS_PATCH, False, "1.2.0"),
                    (TAG_COMMITS_PATCH, True, "1.2.0-alpha.3"),
                    (TAG_COMMITS_MINOR, False, "1.2.0"),
                    (TAG_COMMITS_MINOR, True, "1.2.0-alpha.3"),
                    (TAG_COMMITS_MAJOR, False, "2.0.0"),
                    (TAG_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
                # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
                # The last full release version was 1.0.0, so it's had a minor prerelease
                (
                    "repo_with_git_flow_and_release_channels_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(prerelease_token="alpha"),
                ): [
                    *(
                        (commits, True, "1.1.0-alpha.3")
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *((commits, False, "1.1.0") for commits in ([], ["uninteresting"])),
                    (TAG_COMMITS_PATCH, False, "1.1.0"),
                    (TAG_COMMITS_PATCH, True, "1.1.0-alpha.4"),
                    (TAG_COMMITS_MINOR, False, "1.1.0"),
                    (TAG_COMMITS_MINOR, True, "1.1.0-alpha.4"),
                    (TAG_COMMITS_MAJOR, False, "2.0.0"),
                    (TAG_COMMITS_MAJOR, True, "2.0.0-alpha.1"),
                ],
            }.items()
            for (commit_messages, prerelease, expected_new_version) in values
        ]
    ),
)
@pytest.mark.parametrize("major_on_zero", [True, False])
def test_algorithm_no_zero_dot_versions_tag(
    repo,
    file_in_repo,
    commit_parser,
    translator,
    commit_messages,
    prerelease,
    expected_new_version,
    major_on_zero,
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


#####
# 0.x.y versions
#####


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, major_on_zero, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    "repo_with_no_tags_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            [],
                            ["uninteresting"],
                            ANGULAR_COMMITS_PATCH,
                            ANGULAR_COMMITS_MINOR,
                        )
                    ),
                    (ANGULAR_COMMITS_MAJOR, False, False, "0.1.0"),
                    (ANGULAR_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    "repo_with_single_branch_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (ANGULAR_COMMITS_PATCH, False, major_on_zero, "0.1.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_MINOR, False, major_on_zero, "0.2.0")
                        for major_on_zero in (True, False)
                    ),
                    (ANGULAR_COMMITS_MAJOR, False, False, "0.2.0"),
                    (ANGULAR_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
                (
                    "repo_with_single_branch_and_prereleases_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, prerelease, major_on_zero, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (ANGULAR_COMMITS_PATCH, False, major_on_zero, "0.2.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_PATCH, True, major_on_zero, "0.2.1-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_MINOR, True, major_on_zero, "0.3.0-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    (ANGULAR_COMMITS_MAJOR, False, True, "1.0.0"),
                    (ANGULAR_COMMITS_MAJOR, True, True, "1.0.0-rc.1"),
                    (ANGULAR_COMMITS_MAJOR, False, False, "0.3.0"),
                    (ANGULAR_COMMITS_MAJOR, True, False, "0.3.0-rc.1"),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
                # The last full release version was 0.2.0, so it's had a minor prerelease
                (
                    "repo_with_main_and_feature_branches_angular_commits",
                    "default_angular_parser",
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        (commits, True, major_on_zero, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (ANGULAR_COMMITS_PATCH, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_PATCH, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (ANGULAR_COMMITS_MINOR, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    (ANGULAR_COMMITS_MAJOR, False, True, "1.0.0"),
                    (ANGULAR_COMMITS_MAJOR, True, True, "1.0.0-beta.1"),
                    (ANGULAR_COMMITS_MAJOR, False, False, "0.3.0"),
                    # Note - since breaking changes are absorbed into the minor digit
                    # with major_on_zero = False, and that's already been incremented
                    # since the last full release, the breaking change here will only
                    # trigger a prerelease revision
                    (ANGULAR_COMMITS_MAJOR, True, False, "0.3.0-beta.2"),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            ) in values
        ]
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
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, major_on_zero, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    "repo_with_no_tags_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            [],
                            ["uninteresting"],
                            EMOJI_COMMITS_PATCH,
                            EMOJI_COMMITS_MINOR,
                        )
                    ),
                    (EMOJI_COMMITS_MAJOR, False, False, "0.1.0"),
                    (EMOJI_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    "repo_with_single_branch_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (EMOJI_COMMITS_PATCH, False, major_on_zero, "0.1.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_MINOR, False, major_on_zero, "0.2.0")
                        for major_on_zero in (True, False)
                    ),
                    (EMOJI_COMMITS_MAJOR, False, False, "0.2.0"),
                    (EMOJI_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
                (
                    "repo_with_single_branch_and_prereleases_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, prerelease, major_on_zero, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (EMOJI_COMMITS_PATCH, False, major_on_zero, "0.2.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_PATCH, True, major_on_zero, "0.2.1-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_MINOR, True, major_on_zero, "0.3.0-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    (EMOJI_COMMITS_MAJOR, False, True, "1.0.0"),
                    (EMOJI_COMMITS_MAJOR, True, True, "1.0.0-rc.1"),
                    (EMOJI_COMMITS_MAJOR, False, False, "0.3.0"),
                    (EMOJI_COMMITS_MAJOR, True, False, "0.3.0-rc.1"),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor prerelease
                (
                    "repo_with_main_and_feature_branches_emoji_commits",
                    "default_emoji_parser",
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        (commits, True, major_on_zero, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (EMOJI_COMMITS_PATCH, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_PATCH, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (EMOJI_COMMITS_MINOR, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    (EMOJI_COMMITS_MAJOR, False, True, "1.0.0"),
                    (EMOJI_COMMITS_MAJOR, True, True, "1.0.0-beta.1"),
                    (EMOJI_COMMITS_MAJOR, False, False, "0.3.0"),
                    # Note - since breaking changes are absorbed into the minor digit
                    # with major_on_zero = False, and that's already been incremented
                    # since the last full release, the breaking change here will only
                    # trigger a prerelease revision
                    (EMOJI_COMMITS_MAJOR, True, False, "0.3.0-beta.2"),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            ) in values
        ]
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
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, major_on_zero, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    "repo_with_no_tags_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            [],
                            ["uninteresting"],
                            lazy_fixture("scipy_commits_patch"),
                            lazy_fixture("scipy_commits_minor"),
                        )
                    ),
                    (lazy_fixture("scipy_commits_major"), False, False, "0.1.0"),
                    (lazy_fixture("scipy_commits_major"), False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    "repo_with_single_branch_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_patch"),
                            False,
                            major_on_zero,
                            "0.1.2",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_minor"),
                            False,
                            major_on_zero,
                            "0.2.0",
                        )
                        for major_on_zero in (True, False)
                    ),
                    (lazy_fixture("scipy_commits_major"), False, False, "0.2.0"),
                    (lazy_fixture("scipy_commits_major"), False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
                (
                    "repo_with_single_branch_and_prereleases_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, prerelease, major_on_zero, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_patch"),
                            False,
                            major_on_zero,
                            "0.2.1",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_patch"),
                            True,
                            major_on_zero,
                            "0.2.1-rc.1",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_minor"),
                            False,
                            major_on_zero,
                            "0.3.0",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_minor"),
                            True,
                            major_on_zero,
                            "0.3.0-rc.1",
                        )
                        for major_on_zero in (True, False)
                    ),
                    (lazy_fixture("scipy_commits_major"), False, True, "1.0.0"),
                    (lazy_fixture("scipy_commits_major"), True, True, "1.0.0-rc.1"),
                    (lazy_fixture("scipy_commits_major"), False, False, "0.3.0"),
                    (lazy_fixture("scipy_commits_major"), True, False, "0.3.0-rc.1"),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
                # The last full release version was 0.2.0, so it's had a minor prerelease
                (
                    "repo_with_main_and_feature_branches_scipy_commits",
                    "default_scipy_parser",
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        (commits, True, major_on_zero, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_patch"),
                            False,
                            major_on_zero,
                            "0.3.0",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_patch"),
                            True,
                            major_on_zero,
                            "0.3.0-beta.2",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_minor"),
                            False,
                            major_on_zero,
                            "0.3.0",
                        )
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (
                            lazy_fixture("scipy_commits_minor"),
                            True,
                            major_on_zero,
                            "0.3.0-beta.2",
                        )
                        for major_on_zero in (True, False)
                    ),
                    (lazy_fixture("scipy_commits_major"), False, True, "1.0.0"),
                    (lazy_fixture("scipy_commits_major"), True, True, "1.0.0-beta.1"),
                    (lazy_fixture("scipy_commits_major"), False, False, "0.3.0"),
                    # Note - since breaking changes are absorbed into the minor digit
                    # with major_on_zero = False, and that's already been incremented
                    # since the last full release, the breaking change here will only
                    # trigger a prerelease revision
                    (lazy_fixture("scipy_commits_major"), True, False, "0.3.0-beta.2"),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
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
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )


@pytest.mark.parametrize(
    "repo, commit_parser, translator, commit_messages,"
    "prerelease, major_on_zero, expected_new_version",
    xdist_sort_hack(
        [
            (
                lazy_fixture(repo_fixture_name),
                lazy_fixture(parser_fixture_name),
                translator,
                commit_messages,
                prerelease,
                major_on_zero,
                expected_new_version,
            )
            for (repo_fixture_name, parser_fixture_name, translator), values in {
                # Latest version for repo_with_no_tags is currently 0.0.0 (default)
                # It's biggest change type is minor, so the next version should be 0.1.0
                (
                    "repo_with_no_tags_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.0")
                        for major_on_zero in (True, False)
                        for commits in (
                            [],
                            ["uninteresting"],
                            TAG_COMMITS_PATCH,
                            TAG_COMMITS_MINOR,
                        )
                    ),
                    (TAG_COMMITS_MAJOR, False, False, "0.1.0"),
                    (TAG_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch is currently 0.1.1
                # Note repo_with_single_branch isn't modelled with prereleases
                (
                    "repo_with_single_branch_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, False, major_on_zero, "0.1.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (TAG_COMMITS_PATCH, False, major_on_zero, "0.1.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_MINOR, False, major_on_zero, "0.2.0")
                        for major_on_zero in (True, False)
                    ),
                    (TAG_COMMITS_MAJOR, False, False, "0.2.0"),
                    (TAG_COMMITS_MAJOR, False, True, "1.0.0"),
                ],
                # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
                (
                    "repo_with_single_branch_and_prereleases_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(),
                ): [
                    *(
                        (commits, prerelease, major_on_zero, "0.2.0")
                        for prerelease in (True, False)
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (TAG_COMMITS_PATCH, False, major_on_zero, "0.2.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_PATCH, True, major_on_zero, "0.2.1-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_MINOR, True, major_on_zero, "0.3.0-rc.1")
                        for major_on_zero in (True, False)
                    ),
                    (TAG_COMMITS_MAJOR, False, True, "1.0.0"),
                    (TAG_COMMITS_MAJOR, True, True, "1.0.0-rc.1"),
                    (TAG_COMMITS_MAJOR, False, False, "0.3.0"),
                    (TAG_COMMITS_MAJOR, True, False, "0.3.0-rc.1"),
                ],
                # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-beta.1.
                # The last full release version was 0.2.0, so it's had a minor prerelease
                (
                    "repo_with_main_and_feature_branches_tag_commits",
                    "default_tag_parser",
                    VersionTranslator(prerelease_token="beta"),
                ): [
                    *(
                        (commits, True, major_on_zero, "0.3.0-beta.1")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    # Models a merge of commits from the branch to the main branch, now
                    # that prerelease=False
                    *(
                        (commits, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                        for commits in ([], ["uninteresting"])
                    ),
                    *(
                        (TAG_COMMITS_PATCH, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_PATCH, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_MINOR, False, major_on_zero, "0.3.0")
                        for major_on_zero in (True, False)
                    ),
                    *(
                        (TAG_COMMITS_MINOR, True, major_on_zero, "0.3.0-beta.2")
                        for major_on_zero in (True, False)
                    ),
                    (TAG_COMMITS_MAJOR, False, True, "1.0.0"),
                    (TAG_COMMITS_MAJOR, True, True, "1.0.0-beta.1"),
                    (TAG_COMMITS_MAJOR, False, False, "0.3.0"),
                    # Note - since breaking changes are absorbed into the minor digit
                    # with major_on_zero = False, and that's already been incremented
                    # since the last full release, the breaking change here will only
                    # trigger a prerelease revision
                    (TAG_COMMITS_MAJOR, True, False, "0.3.0-beta.2"),
                ],
            }.items()
            for (
                commit_messages,
                prerelease,
                major_on_zero,
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
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(
        repo, translator, commit_parser, prerelease, major_on_zero
    )

    assert new_version == Version.parse(
        expected_new_version, prerelease_token=translator.prerelease_token
    )
