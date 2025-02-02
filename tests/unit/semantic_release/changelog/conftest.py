from __future__ import annotations

from datetime import timedelta
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from git import Commit, Object, Repo

from semantic_release.changelog.release_history import Release, ReleaseHistory
from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.enums import LevelBump
from semantic_release.version.version import Version

if TYPE_CHECKING:
    from git import Actor

    from tests.conftest import GetStableDateNowFn


@pytest.fixture
def artificial_release_history(
    commit_author: Actor,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    first_version = Version.parse("1.0.0")
    second_version = first_version.bump(LevelBump.MINOR)
    fix_commit_subject = "fix a problem"
    fix_commit_type = "fix"
    fix_commit_scope = "cli"

    fix_commit = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=f"{fix_commit_type}({fix_commit_scope}): {fix_commit_subject}",
    )

    fix_commit_parsed = ParsedCommit(
        bump=LevelBump.PATCH,
        type="fix",
        scope=fix_commit_scope,
        descriptions=[fix_commit_subject],
        breaking_descriptions=[],
        commit=fix_commit,
    )

    fix_commit_2_subject = "alphabetically first to solve a non-scoped problem"
    fix_commit_2_type = "fix"
    fix_commit_2_scope = ""

    fix_commit_2 = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=f"{fix_commit_2_type}: {fix_commit_2_subject}",
    )

    fix_commit_2_parsed = ParsedCommit(
        bump=LevelBump.PATCH,
        type="fix",
        scope=fix_commit_2_scope,
        descriptions=[fix_commit_2_subject],
        breaking_descriptions=[],
        commit=fix_commit_2,
    )

    fix_commit_3_subject = "alphabetically first to solve a scoped problem"
    fix_commit_3_type = "fix"
    fix_commit_3_scope = "cli"

    fix_commit_3 = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=f"{fix_commit_3_type}({fix_commit_3_scope}): {fix_commit_3_subject}",
    )

    fix_commit_3_parsed = ParsedCommit(
        bump=LevelBump.PATCH,
        type="fix",
        scope=fix_commit_3_scope,
        descriptions=[fix_commit_3_subject],
        breaking_descriptions=[],
        commit=fix_commit_3,
    )

    feat_commit_subject = "add a new feature"
    feat_commit_type = "feat"
    feat_commit_scope = "cli"

    feat_commit = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=f"{feat_commit_type}({feat_commit_scope}): {feat_commit_subject}",
    )

    feat_commit_parsed = ParsedCommit(
        bump=LevelBump.MINOR,
        type="feature",
        scope=feat_commit_scope,
        descriptions=[feat_commit_subject],
        breaking_descriptions=[],
        commit=feat_commit,
    )

    return ReleaseHistory(
        unreleased={"feature": [feat_commit_parsed]},
        released={
            second_version: Release(
                tagger=commit_author,
                committer=commit_author,
                tagged_date=current_datetime,
                elements={
                    # Purposefully inserted out of order, should be dictsorted in templates
                    "fix": [
                        # Purposefully inserted out of alphabetical order, should be sorted in templates
                        fix_commit_parsed,
                        fix_commit_2_parsed,  # has no scope
                        fix_commit_3_parsed,  # has same scope as 1
                    ],
                    "feature": [feat_commit_parsed],
                },
                version=second_version,
            ),
            first_version: Release(
                tagger=commit_author,
                committer=commit_author,
                tagged_date=current_datetime - timedelta(minutes=1),
                elements={"feature": [feat_commit_parsed]},
                version=first_version,
            ),
        },
    )


@pytest.fixture
def release_history_w_brk_change(
    artificial_release_history: ReleaseHistory,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    latest_version = next(iter(artificial_release_history.released.keys()))
    next_version = latest_version.bump(LevelBump.MAJOR)
    brk_commit_subject = "fix a problem"
    brk_commit_type = "fix"
    brk_commit_scope = "cli"
    brk_change_msg = "this is a breaking change"

    brk_commit = Commit(
        Repo("."),
        Object.NULL_BIN_SHA,
        message=str.join(
            "\n\n",
            [
                f"{brk_commit_type}({brk_commit_scope}): {brk_commit_subject}",
                f"BREAKING CHANGE: {brk_change_msg}",
            ],
        ),
    )

    brk_commit_parsed = ParsedCommit(
        bump=LevelBump.MAJOR,
        type=brk_commit_type,
        scope=brk_commit_scope,
        descriptions=[brk_commit_subject],
        breaking_descriptions=[brk_change_msg],
        commit=brk_commit,
    )

    return ReleaseHistory(
        unreleased={},
        released={
            next_version: Release(
                tagger=artificial_release_history.released[latest_version]["tagger"],
                committer=artificial_release_history.released[latest_version][
                    "committer"
                ],
                tagged_date=current_datetime,
                elements={"Bug Fixes": [brk_commit_parsed]},
                version=next_version,
            ),
            **artificial_release_history.released,
        },
    )


@pytest.fixture
def release_history_w_multiple_brk_changes(
    release_history_w_brk_change: ReleaseHistory,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    latest_version = next(iter(release_history_w_brk_change.released.keys()))
    brk_commit_subject = "adding a revolutionary feature"
    brk_commit_type = "feat"
    brk_change_msg = "The feature changes everything in a breaking way"

    brk_commit = Commit(
        Repo("."),
        Object.NULL_BIN_SHA,
        message=str.join(
            "\n\n",
            [
                f"{brk_commit_type}: {brk_commit_subject}",
                f"BREAKING CHANGE: {brk_change_msg}",
            ],
        ),
    )

    brk_commit_parsed = ParsedCommit(
        bump=LevelBump.MAJOR,
        type=brk_commit_type,
        scope="",  # No scope in this commit
        descriptions=[brk_commit_subject],
        breaking_descriptions=[brk_change_msg],
        commit=brk_commit,
    )

    return ReleaseHistory(
        unreleased={},
        released={
            **release_history_w_brk_change.released,
            # Replaces and inserts a new commit of different type with breaking changes
            latest_version: Release(
                tagger=release_history_w_brk_change.released[latest_version]["tagger"],
                committer=release_history_w_brk_change.released[latest_version][
                    "committer"
                ],
                tagged_date=current_datetime,
                elements={
                    **release_history_w_brk_change.released[latest_version]["elements"],
                    "Features": [brk_commit_parsed],
                },
                version=latest_version,
            ),
        },
    )


@pytest.fixture
def single_release_history(
    artificial_release_history: ReleaseHistory,
) -> ReleaseHistory:
    version = list(artificial_release_history.released.keys())[-1]
    return ReleaseHistory(
        unreleased={},
        released={
            version: artificial_release_history.released[version],
        },
    )


@pytest.fixture
def release_history_w_a_notice(
    artificial_release_history: ReleaseHistory,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    latest_version = next(iter(artificial_release_history.released.keys()))
    next_version = latest_version.bump(LevelBump.PATCH)
    notice_commit_subject = "deprecate a type"
    notice_commit_type = "refactor"
    notice_commit_scope = "cli"
    release_notice = dedent(
        """\
        This is a multline release notice that is made
        up of two lines.
        """
    )

    notice_commit = Commit(
        Repo("."),
        Object.NULL_BIN_SHA,
        message=str.join(
            "\n\n",
            [
                f"{notice_commit_type}({notice_commit_scope}): {notice_commit_subject}",
                f"NOTICE: {release_notice}",
            ],
        ),
    )

    notice_commit_parsed = ParsedCommit(
        bump=LevelBump.NO_RELEASE,
        type=notice_commit_type,
        scope=notice_commit_scope,
        descriptions=[notice_commit_subject],
        breaking_descriptions=[],
        release_notices=(release_notice.replace("\n", " ").strip(),),
        commit=notice_commit,
    )

    return ReleaseHistory(
        unreleased={},
        released={
            next_version: Release(
                tagger=artificial_release_history.released[latest_version]["tagger"],
                committer=artificial_release_history.released[latest_version][
                    "committer"
                ],
                tagged_date=current_datetime,
                elements={"Refactoring": [notice_commit_parsed]},
                version=next_version,
            ),
            **artificial_release_history.released,
        },
    )


@pytest.fixture
def release_history_w_notice_n_brk_change(
    artificial_release_history: ReleaseHistory,
    release_history_w_a_notice: ReleaseHistory,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    latest_version = next(iter(artificial_release_history.released.keys()))
    next_version = latest_version.bump(LevelBump.MAJOR)
    brk_commit_subject = "fix a problem"
    brk_commit_type = "fix"
    brk_commit_scope = "cli"
    brk_change_msg = "this is a breaking change"

    brk_commit = Commit(
        Repo("."),
        Object.NULL_BIN_SHA,
        message=str.join(
            "\n\n",
            [
                f"{brk_commit_type}({brk_commit_scope}): {brk_commit_subject}",
                f"BREAKING CHANGE: {brk_change_msg}",
            ],
        ),
    )

    brk_commit_parsed = ParsedCommit(
        bump=LevelBump.MAJOR,
        type=brk_commit_type,
        scope=brk_commit_scope,
        descriptions=[brk_commit_subject],
        breaking_descriptions=[brk_change_msg],
        commit=brk_commit,
    )

    last_notice_release = next(iter(release_history_w_a_notice.released.keys()))

    return ReleaseHistory(
        unreleased={},
        released={
            next_version: Release(
                tagger=artificial_release_history.released[latest_version]["tagger"],
                committer=artificial_release_history.released[latest_version][
                    "committer"
                ],
                tagged_date=current_datetime,
                elements={
                    "Bug Fixes": [brk_commit_parsed],
                    **release_history_w_a_notice.released[last_notice_release][
                        "elements"
                    ],
                },
                version=next_version,
            ),
            **artificial_release_history.released,
        },
    )


@pytest.fixture
def release_history_w_multiple_notices(
    release_history_w_a_notice: ReleaseHistory,
    stable_now_date: GetStableDateNowFn,
) -> ReleaseHistory:
    current_datetime = stable_now_date()
    latest_version = next(iter(release_history_w_a_notice.released.keys()))

    notice_commit_subject = "add a configurable feature"
    notice_commit_type = "feat"
    notice_commit_scope = "cli-config"
    release_notice = dedent(
        """\
        This is a multline release notice that is its own
        paragraph to detail the configurable feature.
        """
    )

    notice_commit = Commit(
        Repo("."),
        Object.NULL_BIN_SHA,
        message=str.join(
            "\n\n",
            [
                f"{notice_commit_type}({notice_commit_scope}): {notice_commit_subject}",
                f"NOTICE: {release_notice}",
            ],
        ),
    )

    notice_commit_parsed = ParsedCommit(
        bump=LevelBump.MINOR,
        type=notice_commit_type,
        scope=notice_commit_scope,
        descriptions=[notice_commit_subject],
        breaking_descriptions=[],
        release_notices=(release_notice.replace("\n", " ").strip(),),
        commit=notice_commit,
    )

    return ReleaseHistory(
        unreleased={},
        released={
            **release_history_w_a_notice.released,
            # Replaces and inserts a new commit of different type with breaking changes
            latest_version: Release(
                tagger=release_history_w_a_notice.released[latest_version]["tagger"],
                committer=release_history_w_a_notice.released[latest_version][
                    "committer"
                ],
                tagged_date=current_datetime,
                elements={
                    "Features": [notice_commit_parsed],
                    **release_history_w_a_notice.released[latest_version]["elements"],
                },
                version=latest_version,
            ),
        },
    )
