from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from semantic_release.commit_parser.emoji import EmojiCommitParser

    from tests.conftest import MakeCommitObjFn


@pytest.mark.parametrize(
    "commit_message, bump, type_, descriptions, breaking_descriptions",
    [
        # Major bump
        (
            ":boom: Breaking changes\n\nMore description\n\nEven more description",
            LevelBump.MAJOR,
            ":boom:",
            [":boom: Breaking changes", "More description", "Even more description"],
            ["More description", "Even more description"],
        ),
        # Minor bump
        (
            ":sparkles: Add a new feature\n\nSome description of the feature",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles: Add a new feature", "Some description of the feature"],
            [],
        ),
        # Patch bump
        (
            ":bug: Fixing a bug\n\nThe bug is finally gone!",
            LevelBump.PATCH,
            ":bug:",
            [":bug: Fixing a bug", "The bug is finally gone!"],
            [],
        ),
        # No release
        (
            ":pencil: Documentation changes",
            LevelBump.NO_RELEASE,
            "Other",
            [":pencil: Documentation changes"],
            [],
        ),
        # Multiple emojis
        (
            ":sparkles::pencil: Add a feature and document it",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles::pencil: Add a feature and document it"],
            [],
        ),
        # Emoji in description
        (
            ":sparkles: Add a new feature\n\n:boom: should not be detected",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles: Add a new feature", ":boom: should not be detected"],
            [],
        ),
    ],
)
def test_default_emoji_parser(
    default_emoji_parser: EmojiCommitParser,
    commit_message: str,
    bump: LevelBump,
    type_: str,
    descriptions: list[str],
    breaking_descriptions: list[str],
    make_commit_obj: MakeCommitObjFn,
):
    commit = make_commit_obj(commit_message)
    result = default_emoji_parser.parse(commit)

    assert isinstance(result, ParsedCommit)
    assert bump is result.bump
    assert type_ == result.type
    assert descriptions == result.descriptions
    assert breaking_descriptions == result.breaking_descriptions
