from __future__ import annotations

from typing import TYPE_CHECKING

from semantic_release.commit_parser import ParsedCommit
from semantic_release.version.version import LevelBump

if TYPE_CHECKING:
    from tests.conftest import MakeCommitObjFn


def test_parsed_commit_computed_properties(make_commit_obj: MakeCommitObjFn):
    message = "feat(parser): Add new parser pattern"
    commit = make_commit_obj(message)

    parsed_commit = ParsedCommit(
        bump=LevelBump.MINOR,
        type="feature",
        scope="parser",
        descriptions=["Add new parser pattern"],
        breaking_descriptions=[],
        commit=commit,
    )

    assert message == parsed_commit.message
    assert commit.hexsha == parsed_commit.hexsha
    assert commit.hexsha[:7] == parsed_commit.short_hash
