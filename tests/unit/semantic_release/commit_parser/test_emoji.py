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


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    # TODO: in v10, we will remove the merge request number from the subject line
    [
        # GitHub, Gitea style
        (
            ":sparkles: add new feature (#123)",
            ":sparkles: add new feature (#123)",
            "#123",
        ),
        # GitLab style
        (
            ":bug: fix regex in parser (!456)",
            ":bug: fix regex in parser (!456)",
            "!456",
        ),
        # BitBucket style
        (
            ":sparkles: add new feature (pull request #123)",
            ":sparkles: add new feature (pull request #123)",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        (":bug: superfix (#123)\n\nCloses: #400", ":bug: superfix (#123)", "#123"),
        # None
        (":bug: superfix", ":bug: superfix", ""),
        # None but includes an issue footer it should not be considered a linked merge request
        (":bug: superfix\n\nCloses: #400", ":bug: superfix", ""),
    ],
)
def test_parser_return_linked_merge_request_from_commit_message(
    default_emoji_parser: EmojiCommitParser,
    message: str,
    subject: str,
    merge_request_number: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_emoji_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert merge_request_number == result.linked_merge_request
    assert subject == result.descriptions[0]
