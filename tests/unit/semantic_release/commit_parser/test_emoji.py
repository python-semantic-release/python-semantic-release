import pytest

from semantic_release.commit_parser.emoji import EmojiCommitParser
from semantic_release.enums import LevelBump

from tests.unit.semantic_release.commit_parser.helper import make_commit


@pytest.fixture
def default_options():
    yield EmojiCommitParser.parser_options()


@pytest.fixture
def default_emoji_parser(default_options):
    yield EmojiCommitParser(default_options)


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
            ":sparkles: Add a new feature\n\n" "Some description of the feature",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles: Add a new feature", "Some description of the feature"],
            [],
        ),
        # Patch bump
        (
            ":bug: Fixing a bug\n\n" "The bug is finally gone!",
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
    default_emoji_parser,
    commit_message,
    bump,
    type_,
    descriptions,
    breaking_descriptions,
):
    commit = make_commit(commit_message)
    parsed = default_emoji_parser.parse(commit)
    assert parsed.bump is bump
    assert parsed.type == type_
    assert parsed.descriptions == descriptions
    assert parsed.breaking_descriptions == breaking_descriptions
