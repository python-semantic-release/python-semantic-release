from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

import pytest
from git import Actor
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

from tests.const import ANGULAR_COMMITS_MINOR, COMMIT_MESSAGE
from tests.fixtures import (
    get_commits_for_git_flow_repo_w_3_release_channels,
    get_commits_for_git_flow_repo_with_2_release_channels,
    get_commits_for_github_flow_repo_w_feature_release_channel,
    get_commits_for_trunk_only_repo_w_no_tags,
    get_commits_for_trunk_only_repo_w_prerelease_tags,
    get_commits_for_trunk_only_repo_w_tags,
    repo_w_github_flow_w_feature_release_channel_angular_commits,
    repo_with_git_flow_and_release_channels_angular_commits,
    repo_with_git_flow_angular_commits,
    repo_with_no_tags_angular_commits,
    repo_with_single_branch_and_prereleases_angular_commits,
    repo_with_single_branch_angular_commits,
)
from tests.util import add_text_to_file

if TYPE_CHECKING:
    from typing import Protocol

    from git import Repo

    from semantic_release.commit_parser.angular import AngularCommitParser

    from tests.fixtures.git_repo import GetRepoDefinitionFn, RepoDefinition

    class CreateReleaseHistoryFromRepoDefFn(Protocol):
        def __call__(self, repo_def: RepoDefinition) -> FakeReleaseHistoryElements: ...

# NOTE: not testing parser correctness here, just that the right commits end up
# in the right places. So we only compare that the commits with the messages
# we anticipate are in the right place, rather than by hash
# So we are only using the angular parser


# We are also currently only testing that the "elements" key of the releases
# is correct, i.e. the commits are in the right place - the other fields
# will need special attention of their own later
class FakeReleaseHistoryElements(NamedTuple):
    unreleased: dict[str, list[str]]
    released: dict[Version, dict[str, list[str]]]


@pytest.fixture(scope="session")
def create_release_history_from_repo_def() -> CreateReleaseHistoryFromRepoDefFn:
    def _create_release_history_from_repo_def(
        repo_def: RepoDefinition,
    ) -> FakeReleaseHistoryElements:
        unreleased_history = {}
        released_history = {}

        for version_str, version_def in repo_def.items():
            # extract the commit messages
            commit_msgs = [
                # TODO: remove the newline when our release history strips whitespace from commit messages
                commit["msg"].strip() + "\n"
                for commit in version_def["commits"]
            ]

            commits_per_group: dict[str, list] = {
                "Unknown": [],
            }
            for group_def in version_def["changelog_sections"]:
                group_name = group_def["section"]
                commits_per_group[group_name] = [
                    commit_msgs[index] for index in group_def["i_commits"]
                ]

            if version_str == "Unreleased":
                unreleased_history = commits_per_group
                continue

            # handle released versions
            version = Version.parse(version_str)

            # add the PSR version commit message
            commits_per_group["Unknown"].append(COMMIT_MESSAGE.format(version=version))

            # store the organized commits for this version
            released_history[version] = commits_per_group

        return FakeReleaseHistoryElements(
            unreleased=unreleased_history,
            released=released_history,
        )

    return _create_release_history_from_repo_def


@pytest.mark.parametrize(
    "repo, get_repo_definition",
    [
        # ANGULAR parser
        (
            lazy_fixture(repo_with_no_tags_angular_commits.__name__),
            lazy_fixture(get_commits_for_trunk_only_repo_w_no_tags.__name__),
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                lazy_fixture(get_commits_for_repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name, get_commits_for_repo_fixture_name in [
                (
                    repo_with_single_branch_angular_commits.__name__,
                    get_commits_for_trunk_only_repo_w_tags.__name__,
                ),
                (
                    repo_with_single_branch_and_prereleases_angular_commits.__name__,
                    get_commits_for_trunk_only_repo_w_prerelease_tags.__name__,
                ),
                (
                    repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
                    get_commits_for_github_flow_repo_w_feature_release_channel.__name__,
                ),
                (
                    repo_with_git_flow_angular_commits.__name__,
                    get_commits_for_git_flow_repo_with_2_release_channels.__name__,
                ),
                (
                    repo_with_git_flow_and_release_channels_angular_commits.__name__,
                    get_commits_for_git_flow_repo_w_3_release_channels.__name__,
                ),
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_release_history(
    repo: Repo,
    default_angular_parser: AngularCommitParser,
    get_repo_definition: GetRepoDefinitionFn,
    file_in_repo: str,
    create_release_history_from_repo_def: CreateReleaseHistoryFromRepoDefFn,
):
    expected_release_history = create_release_history_from_repo_def(
        get_repo_definition("angular")
    )
    expected_released_versions = sorted(
        map(str, expected_release_history.released.keys())
    )

    translator = VersionTranslator()
    # Nothing has unreleased commits currently
    _, released = ReleaseHistory.from_git_history(
        repo, translator, default_angular_parser
    )

    actual_released_versions = sorted(map(str, released.keys()))
    assert expected_released_versions == actual_released_versions

    for k in expected_release_history.released:
        expected = expected_release_history.released[k]
        expected_released_messages = str.join(
            "\n---\n", sorted([msg for bucket in expected.values() for msg in bucket])
        )

        actual = released[k]["elements"]
        actual_released_messages = str.join(
            "\n---\n",
            sorted(
                [
                    str(res.commit.message)
                    for results in actual.values()
                    for res in results
                ]
            ),
        )
        assert expected_released_messages == actual_released_messages

    # PART 2: add some commits to the repo and check that they are in the right place

    for commit_message in ANGULAR_COMMITS_MINOR:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    expected_unreleased_messages = str.join(
        "\n---\n",
        sorted(
            [
                msg
                for bucket in [
                    ANGULAR_COMMITS_MINOR[::-1],
                    *expected_release_history.unreleased.values(),
                ]
                for msg in bucket
            ]
        ),
    )

    # Now we should have some unreleased commits, and nothing new released
    new_unreleased, new_released = ReleaseHistory.from_git_history(
        repo, translator, default_angular_parser
    )

    actual_unreleased_messages = str.join(
        "\n---\n",
        sorted(
            [
                str(res.commit.message)
                for results in new_unreleased.values()
                for res in results
            ]
        ),
    )

    assert expected_unreleased_messages == actual_unreleased_messages
    assert (
        new_released == released
    ), "something that shouldn't be considered release has been released"


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_with_no_tags_angular_commits.__name__),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in [
                repo_with_single_branch_angular_commits.__name__,
                repo_with_single_branch_and_prereleases_angular_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
                repo_with_git_flow_angular_commits.__name__,
                repo_with_git_flow_and_release_channels_angular_commits.__name__,
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_release_history_releases(
    repo: Repo, default_angular_parser: AngularCommitParser
):
    new_version = Version.parse("100.10.1")
    actor = Actor("semantic-release", "semantic-release")
    release_history = ReleaseHistory.from_git_history(
        repo=repo,
        translator=VersionTranslator(),
        commit_parser=default_angular_parser,
    )
    tagged_date = datetime.now()
    new_rh = release_history.release(
        new_version,
        committer=actor,
        tagger=actor,
        tagged_date=tagged_date,
    )

    assert new_rh is not release_history
    assert new_rh.unreleased == {}
    assert new_rh.released == {
        new_version: {
            "tagger": actor,
            "committer": actor,
            "tagged_date": tagged_date,
            "elements": release_history.unreleased,
            "version": new_version,
        },
        **release_history.released,
    }


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_with_no_tags_angular_commits.__name__),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in [
                repo_with_single_branch_angular_commits.__name__,
                repo_with_single_branch_and_prereleases_angular_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
                repo_with_git_flow_angular_commits.__name__,
                repo_with_git_flow_and_release_channels_angular_commits.__name__,
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_all_matching_repo_tags_are_released(
    repo: Repo, default_angular_parser: AngularCommitParser
):
    translator = VersionTranslator()
    release_history = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=default_angular_parser,
    )

    for tag in repo.tags:
        assert translator.from_tag(tag.name) in release_history.released
