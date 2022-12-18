from collections import namedtuple
from datetime import datetime

import pytest
from git import Actor
from pytest_lazyfixture import lazy_fixture

from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

from tests.const import ANGULAR_COMMITS_MINOR, COMMIT_MESSAGE
from tests.util import add_text_to_file

# NOTE: not testing parser correctness here, just that the right commits end up
# in the right places. So we only compare that the commits with the messages
# we anticipate are in the right place, rather than by hash
# So we are only using the angular parser

# We are also currently only testing that the "elements" key of the releases
# is correct, i.e. the commits are in the right place - the other fields
# will need special attention of their own later
FakeReleaseHistoryElements = namedtuple(
    "FakeReleaseHistoryElements", "unreleased released"
)


REPO_WITH_NO_TAGS_EXPECTED_RELEASE_HISTORY = FakeReleaseHistoryElements(
    unreleased={
        "feature": ["feat: add much more text\n"],
        "fix": ["fix: add some more text\n", "fix: more text\n"],
        "unknown": ["Initial commit\n"],
    },
    released={},
)

REPO_WITH_SINGLE_BRANCH_EXPECTED_RELEASE_HISTORY = FakeReleaseHistoryElements(
    unreleased={},
    released={
        Version.parse("0.1.0"): {
            "unknown": ["Initial commit\n", COMMIT_MESSAGE.format(version="0.1.0")],
        },
        Version.parse("0.1.1"): {
            "fix": ["fix: add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="0.1.1")],
        },
    },
)

REPO_WITH_SINGLE_BRANCH_AND_PRERELEASES_EXPECTED_RELEASE_HISTORY = (
    FakeReleaseHistoryElements(
        unreleased={},
        released={
            Version.parse("0.1.0"): {
                "unknown": ["Initial commit\n", COMMIT_MESSAGE.format(version="0.1.0")],
            },
            Version.parse("0.1.1-rc.1"): {
                "fix": ["fix: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.1.1-rc.1")],
            },
            Version.parse("0.2.0-rc.1"): {
                "feature": ["feat: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.2.0-rc.1")],
            },
            Version.parse("0.2.0"): {
                "feature": ["feat: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.2.0")],
            },
        },
    )
)

REPO_WITH_MAIN_AND_FEATURE_BRANCHES_EXPECTED_RELEASE_HISTORY = (
    FakeReleaseHistoryElements(
        unreleased={},
        released={
            Version.parse("0.1.0"): {
                "unknown": ["Initial commit\n", COMMIT_MESSAGE.format(version="0.1.0")],
            },
            Version.parse("0.1.1-rc.1"): {
                "fix": ["fix: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.1.1-rc.1")],
            },
            Version.parse("0.2.0-rc.1"): {
                "feature": ["feat: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.2.0-rc.1")],
            },
            Version.parse("0.2.0"): {
                "feature": ["feat: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.2.0")],
            },
            Version.parse("0.3.0-beta.1"): {
                "feature": ["feat: (feature) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.3.0-beta.1")],
            },
        },
    )
)

REPO_WITH_GIT_FLOW_EXPECTED_RELEASE_HISTORY = FakeReleaseHistoryElements(
    unreleased={},
    released={
        Version.parse("0.1.0"): {
            "unknown": ["Initial commit\n", COMMIT_MESSAGE.format(version="0.1.0")],
        },
        Version.parse("0.1.1-rc.1"): {
            "fix": ["fix: add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="0.1.1-rc.1")],
        },
        Version.parse("1.0.0-rc.1"): {
            "breaking": ["feat!: add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.0.0-rc.1")],
        },
        Version.parse("1.0.0"): {
            "feature": ["feat: add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.0.0")],
        },
        Version.parse("1.1.0"): {
            "feature": ["feat: (dev) add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.1.0")],
        },
        Version.parse("1.1.1"): {
            "fix": ["fix: (dev) add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.1.1")],
        },
        Version.parse("1.2.0-alpha.1"): {
            "feature": ["feat: (feature) add some more text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.2.0-alpha.1")],
        },
        Version.parse("1.2.0-alpha.2"): {
            "feature": ["feat: (feature) add some more text\n"],
            "fix": ["fix: (feature) add some missing text\n"],
            "unknown": [COMMIT_MESSAGE.format(version="1.2.0-alpha.2")],
        },
    },
)

REPO_WITH_GIT_FLOW_AND_RELEASE_CHANNELS_EXPECTED_RELEASE_HISTORY = (
    FakeReleaseHistoryElements(
        unreleased={},
        released={
            Version.parse("0.1.0"): {
                "unknown": ["Initial commit\n", COMMIT_MESSAGE.format(version="0.1.0")],
            },
            Version.parse("0.1.1-rc.1"): {
                "fix": ["fix: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="0.1.1-rc.1")],
            },
            Version.parse("1.0.0-rc.1"): {
                "breaking": ["feat!: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.0.0-rc.1")],
            },
            Version.parse("1.0.0"): {
                "feature": ["feat: add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.0.0")],
            },
            Version.parse("1.1.0-rc.1"): {
                "feature": ["feat: (dev) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.1.0-rc.1")],
            },
            Version.parse("1.1.0-rc.2"): {
                "fix": ["fix: (dev) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.1.0-rc.2")],
            },
            Version.parse("1.1.0-alpha.1"): {
                "feature": ["feat: (feature) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.1.0-alpha.1")],
            },
            Version.parse("1.1.0-alpha.2"): {
                "feature": ["feat: (feature) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.1.0-alpha.2")],
            },
            Version.parse("1.1.0-alpha.3"): {
                "fix": ["fix: (feature) add some more text\n"],
                "unknown": [COMMIT_MESSAGE.format(version="1.1.0-alpha.3")],
            },
        },
    )
)


@pytest.mark.parametrize(
    "repo, expected_release_history",
    [
        # ANGULAR parser
        (
            lazy_fixture("repo_with_no_tags_angular_commits"),
            REPO_WITH_NO_TAGS_EXPECTED_RELEASE_HISTORY,
        ),
        (
            lazy_fixture("repo_with_single_branch_angular_commits"),
            REPO_WITH_SINGLE_BRANCH_EXPECTED_RELEASE_HISTORY,
        ),
        (
            lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
            REPO_WITH_SINGLE_BRANCH_AND_PRERELEASES_EXPECTED_RELEASE_HISTORY,
        ),
        (
            lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
            REPO_WITH_MAIN_AND_FEATURE_BRANCHES_EXPECTED_RELEASE_HISTORY,
        ),
        (
            lazy_fixture("repo_with_git_flow_angular_commits"),
            REPO_WITH_GIT_FLOW_EXPECTED_RELEASE_HISTORY,
        ),
        (
            lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
            REPO_WITH_GIT_FLOW_AND_RELEASE_CHANNELS_EXPECTED_RELEASE_HISTORY,
        ),
    ],
)
def test_release_history(
    repo, default_angular_parser, expected_release_history, file_in_repo
):
    translator = VersionTranslator()
    # Nothing has unreleased commits currently
    _, released = ReleaseHistory.from_git_history(
        repo, translator, default_angular_parser
    )
    assert (
        expected_release_history.released.keys() == released.keys()
    ), "versions mismatched, missing: {missing}, extra: {extra}".format(
        missing=", ".join(
            map(str, expected_release_history.released.keys() - released.keys())
        ),
        extra=", ".join(
            map(str, released.keys() - expected_release_history.released.keys())
        ),
    )
    for k in expected_release_history.released:
        expected, actual = expected_release_history.released[k], released[k]["elements"]
        actual_released_messages = [
            res.commit.message for results in actual.values() for res in results
        ]
        assert all(
            msg in actual_released_messages
            for bucket in expected.values()
            for msg in bucket
        )

    for commit_message in ANGULAR_COMMITS_MINOR:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    # Now we should have some unreleased commits, and nothing new released
    new_unreleased, new_released = ReleaseHistory.from_git_history(
        repo, translator, default_angular_parser
    )
    actual_unreleased_messages = [
        res.commit.message for results in new_unreleased.values() for res in results
    ]
    assert all(
        msg in actual_unreleased_messages
        for bucket in [
            *expected_release_history.unreleased.values(),
            ANGULAR_COMMITS_MINOR,
        ]
        for msg in bucket
    )
    assert (
        new_released == released
    ), "something that shouldn't be considered release has been released"


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_release_history_releases(repo, default_angular_parser):
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
        },
        **release_history.released,
    }


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_all_matching_repo_tags_are_released(repo, default_angular_parser):
    translator = VersionTranslator()
    release_history = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=default_angular_parser,
    )

    for tag in repo.tags:
        assert translator.from_tag(tag.name) in release_history.released
