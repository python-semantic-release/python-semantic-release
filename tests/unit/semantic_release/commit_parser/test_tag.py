from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from semantic_release.commit_parser.token import ParsedCommit, ParseError
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from semantic_release.commit_parser.tag import TagCommitParser

    from tests.conftest import MakeCommitObjFn


text = (
    "This is an long explanatory part of a commit message. It should give "
    "some insight to the fix this commit adds to the codebase."
)
footer = "Closes #400"


def test_parser_raises_unknown_message_style(
    default_tag_parser: TagCommitParser, make_commit_obj: MakeCommitObjFn
):
    result = default_tag_parser.parse(make_commit_obj(""))
    assert isinstance(result, ParseError)


@pytest.mark.parametrize(
    "commit_message, bump, type_, descriptions",
    [
        (
            ":sparkles: Add new parser pattern\n\nBREAKING CHANGE:",
            LevelBump.MAJOR,
            "breaking",
            ["Add new parser pattern", "BREAKING CHANGE:"],
        ),
        (
            ":sparkles: Add emoji parser",
            LevelBump.MINOR,
            "feature",
            ["Add emoji parser"],
        ),
        (
            f":nut_and_bolt: Fix regex in angular parser\n\n{text}",
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser", text],
        ),
        (
            ":nut_and_bolt: Fix regex in angular parser",
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser"],
        ),
        (
            f":nut_and_bolt: Fix regex in angular parser\n\n{text}\n\n{footer}",
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser", text, footer],
        ),
    ],
)
def test_default_tag_parser(
    default_tag_parser: TagCommitParser,
    commit_message: str,
    bump: LevelBump,
    type_: str,
    descriptions: list[str],
    make_commit_obj: MakeCommitObjFn,
):
    commit = make_commit_obj(commit_message)
    result = default_tag_parser.parse(commit)

    assert isinstance(result, ParsedCommit)
    assert result.bump is bump
    assert result.type == type_
    assert result.descriptions == descriptions
