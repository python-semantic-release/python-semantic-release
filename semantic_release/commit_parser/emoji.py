"""Commit parser which looks for emojis to determine the type of commit"""
import logging
from typing import Tuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseResult
from semantic_release.commit_parser.util import parse_paragraphs
from semantic_release.enums import LevelBump

logger = logging.getLogger(__name__)


@dataclass
class EmojiParserOptions(ParserOptions):
    major_tags: Tuple[str, ...] = (":boom:",)
    minor_tags: Tuple[str, ...] = (
        ":sparkles:",
        ":children_crossing:",
        ":lipstick:",
        ":iphone:",
        ":egg:",
        ":chart_with_upwards_trend:",
    )
    patch_tags: Tuple[str, ...] = (
        ":ambulance:",
        ":lock:",
        ":bug:",
        ":zap:",
        ":goal_net:",
        ":alien:",
        ":wheelchair:",
        ":speech_balloon:",
        ":mag:",
        ":apple:",
        ":penguin:",
        ":checkered_flag:",
        ":robot:",
        ":green_apple:",
    )
    default_bump_level: LevelBump = LevelBump.NO_RELEASE


class EmojiCommitParser(CommitParser[ParseResult, EmojiParserOptions]):
    """
    Parse a commit using an emoji in the subject line.
    When multiple emojis are encountered, the one with the highest bump
    level is used. If there are multiple emojis on the same level, the
    we use the one listed earliest in the configuration.
    If the message does not contain any known emojis, then the level to bump
    will be 0 and the type of change "Other". This parser never raises
    UnknownCommitMessageStyleError.
    Emojis are not removed from the description, and will appear alongside
    the commit subject in the changelog.
    """

    parser_options = EmojiParserOptions

    def parse(self, commit: Commit) -> ParseResult:
        all_emojis = (
            self.options.major_tags + self.options.minor_tags + self.options.patch_tags
        )

        message = str(commit.message)
        subject = message.split("\n")[0]

        # Loop over emojis from most important to least important
        # Therefore, we find the highest level emoji first
        primary_emoji = "Other"
        for emoji in all_emojis:
            if emoji in subject:
                primary_emoji = emoji
                break
        logger.debug("Selected %s as the primary emoji", primary_emoji)

        # Find which level this commit was from
        level_bump = LevelBump.NO_RELEASE
        if primary_emoji in self.options.major_tags:
            level_bump = LevelBump.MAJOR
        elif primary_emoji in self.options.minor_tags:
            level_bump = LevelBump.MINOR
        elif primary_emoji in self.options.patch_tags:
            level_bump = LevelBump.PATCH

        # All emojis will remain part of the returned description
        descriptions = parse_paragraphs(message)
        return ParsedCommit(
            bump=level_bump,
            type=primary_emoji,
            scope="",
            descriptions=descriptions,
            breaking_descriptions=(
                descriptions[1:] if level_bump is LevelBump.MAJOR else []
            ),
            commit=commit,
        )
