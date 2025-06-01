from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, NamedTuple

import pytest
from git import Actor
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

from tests.const import COMMIT_MESSAGE, CONVENTIONAL_COMMITS_MINOR
from tests.fixtures import (
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits,
    repo_w_github_flow_w_feature_release_channel_conventional_commits,
    repo_w_no_tags_conventional_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_n_prereleases_conventional_commits,
)
from tests.util import add_text_to_file

if TYPE_CHECKING:
    from typing import Protocol

    from semantic_release.commit_parser.conventional import ConventionalCommitParser

    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        GetCommitsFromRepoBuildDefFn,
        RepoDefinition,
    )

    class CreateReleaseHistoryFromRepoDefFn(Protocol):
        def __call__(self, repo_def: RepoDefinition) -> FakeReleaseHistoryElements: ...

# NOTE: not testing parser correctness here, just that the right commits end up
# in the right places. So we only compare that the commits with the messages
# we anticipate are in the right place, rather than by hash
# So we are only using the conventional parser


# We are also currently only testing that the "elements" key of the releases
# is correct, i.e. the commits are in the right place - the other fields
# will need special attention of their own later
class FakeReleaseHistoryElements(NamedTuple):
    """
    A fake release history structure that abstracts away the Parser-specific
    logic and only focuses that the commit messages are in the correct order and place.

    Where generally a ParsedCommit object exists, here we just use the actual `commit.message`.
    """

    unreleased: dict[str, list[str]]
    released: dict[Version, dict[str, list[str]]]


@pytest.fixture(scope="session")
def create_release_history_from_repo_def() -> CreateReleaseHistoryFromRepoDefFn:
    def _create_release_history_from_repo_def(
        repo_def: RepoDefinition,
    ) -> FakeReleaseHistoryElements:
        # Organize the commits into the expected structure
        unreleased_history = {}
        released_history = {}
        for version_str, version_def in repo_def.items():
            commits_per_group: dict[str, list] = {
                "Unknown": [],
            }

            for commit in version_def["commits"]:
                if commit["category"] not in commits_per_group:
                    commits_per_group[commit["category"]] = []

                commits_per_group[commit["category"]].append(commit["msg"].strip())

            if version_str == "Unreleased":
                unreleased_history = commits_per_group
                continue

            # handle released versions
            version = Version.parse(version_str)

            # add the PSR version commit message
            commits_per_group["Unknown"].append(
                COMMIT_MESSAGE.format(version=version).strip()
            )

            # store the organized commits for this version
            released_history[version] = commits_per_group

        return FakeReleaseHistoryElements(
            unreleased=unreleased_history,
            released=released_history,
        )

    return _create_release_history_from_repo_def


@pytest.mark.parametrize(
    "repo_result",
    [
        # CONVENTIONAL parser
        lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in [
                repo_w_trunk_only_conventional_commits.__name__,
                repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                # This is not tested because currently unable to disern the commits that were squashed or not
                # repo_w_github_flow_w_default_release_channel_conventional_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_release_history(
    repo_result: BuiltRepoResult,
    default_conventional_parser: ConventionalCommitParser,
    file_in_repo: str,
    create_release_history_from_repo_def: CreateReleaseHistoryFromRepoDefFn,
    get_commits_from_repo_build_def: GetCommitsFromRepoBuildDefFn,
):
    repo = repo_result["repo"]
    expected_release_history = create_release_history_from_repo_def(
        get_commits_from_repo_build_def(
            repo_result["definition"],
            ignore_merge_commits=default_conventional_parser.options.ignore_merge_commits,
        )
    )
    expected_released_versions = sorted(
        map(str, expected_release_history.released.keys())
    )

    translator = VersionTranslator()
    # Nothing has unreleased commits currently
    history = ReleaseHistory.from_git_history(
        repo,
        translator,
        default_conventional_parser,  # type: ignore[arg-type]
    )
    released = history.released

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

    for commit_message in CONVENTIONAL_COMMITS_MINOR:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    expected_unreleased_messages = str.join(
        "\n---\n",
        sorted(
            [
                str(msg).strip()
                for bucket in [
                    CONVENTIONAL_COMMITS_MINOR[::-1],
                    *expected_release_history.unreleased.values(),
                ]
                for msg in bucket
            ]
        ),
    )

    # Now we should have some unreleased commits, and nothing new released
    new_history = ReleaseHistory.from_git_history(
        repo,
        translator,
        default_conventional_parser,  # type: ignore[arg-type]
    )
    new_unreleased = new_history.unreleased
    new_released = new_history.released

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
    "repo_result",
    [
        lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in [
                repo_w_trunk_only_conventional_commits.__name__,
                repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_release_history_releases(
    repo_result: BuiltRepoResult, default_conventional_parser: ConventionalCommitParser
):
    new_version = Version.parse("100.10.1")
    actor = Actor("semantic-release", "semantic-release")
    release_history = ReleaseHistory.from_git_history(
        repo=repo_result["repo"],
        translator=VersionTranslator(),
        commit_parser=default_conventional_parser,  # type: ignore[arg-type]
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
    "repo_result",
    [
        lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture_name in [
                repo_w_trunk_only_conventional_commits.__name__,
                repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
            ]
        ],
    ],
)
@pytest.mark.order("last")
def test_all_matching_repo_tags_are_released(
    repo_result: BuiltRepoResult, default_conventional_parser: ConventionalCommitParser
):
    repo = repo_result["repo"]
    translator = VersionTranslator()
    release_history = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=default_conventional_parser,  # type: ignore[arg-type]
    )

    for tag in repo.tags:
        assert translator.from_tag(tag.name) in release_history.released
