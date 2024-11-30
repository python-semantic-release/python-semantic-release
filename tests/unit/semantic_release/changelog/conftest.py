from __future__ import annotations

from datetime import timedelta
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
