"""Commit parser which looks for emojis to determine the type of commit"""

from __future__ import annotations

import logging
import re
from itertools import zip_longest
from re import compile as regexp
from typing import Tuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseResult,
)
from semantic_release.commit_parser.util import parse_paragraphs
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidParserOptions

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
    allowed_tags: Tuple[str, ...] = (
        *major_tags,
        *minor_tags,
        *patch_tags,
    )
    default_bump_level: LevelBump = LevelBump.NO_RELEASE

    def __post_init__(self) -> None:
        self.tag_to_level: dict[str, LevelBump] = {
            str(tag): level
            for tag, level in [
                # we have to do a type ignore as zip_longest provides a type that is not specific enough
                # for our expected output. Due to the empty second array, we know the first is always longest
                # and that means no values in the first entry of the tuples will ever be a LevelBump. We
                # apply a str() to make mypy happy although it will never happen.
                *zip_longest(self.allowed_tags, (), fillvalue=self.default_bump_level),
                *zip_longest(self.patch_tags, (), fillvalue=LevelBump.PATCH),
                *zip_longest(self.minor_tags, (), fillvalue=LevelBump.MINOR),
                *zip_longest(self.major_tags, (), fillvalue=LevelBump.MAJOR),
            ]
            if "|" not in str(tag)
        }


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

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = EmojiParserOptions

    def __init__(self, options: EmojiParserOptions | None = None) -> None:
        super().__init__(options)

        # Reverse the list of tags to ensure that the highest level tags are matched first
        emojis_in_precedence_order = list(self.options.tag_to_level.keys())[::-1]

        try:
            self.emoji_selector = regexp(
                r"(?P<type>%s)" % str.join("|", emojis_in_precedence_order)
            )
        except re.error as err:
            raise InvalidParserOptions(
                str.join(
                    "\n",
                    [
                        f"Invalid options for {self.__class__.__name__}",
                        "Unable to create regular expression from configured commit-types.",
                        "Please check the configured commit-types and remove or escape any regular expression characters.",
                    ],
                )
            ) from err

        # GitHub & Gitea use (#123), GitLab uses (!123), and BitBucket uses (pull request #123)
        self.mr_selector = regexp(
            r"[\t ]+\((?:pull request )?(?P<mr_number>[#!]\d+)\)[\t ]*$"
        )

    @staticmethod
    def get_default_options() -> EmojiParserOptions:
        return EmojiParserOptions()

    def parse_message(self, message: str) -> ParsedMessageResult:
        subject = message.split("\n", maxsplit=1)[0]

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(subject):
            linked_merge_request = mr_match.group("mr_number")
            # TODO: breaking change v10, removes PR number from subject/descriptions
            # expects changelog template to format the line accordingly
            # subject = self.mr_selector.sub("", subject).strip()

        # Search for emoji of the highest importance in the subject
        primary_emoji = (
            match.group("type")
            if (match := self.emoji_selector.search(subject))
            else "Other"
        )

        level_bump = self.options.tag_to_level.get(
            primary_emoji, self.options.default_bump_level
        )

        # All emojis will remain part of the returned description
        descriptions = tuple(parse_paragraphs(message))
        return ParsedMessageResult(
            bump=level_bump,
            type=primary_emoji,
            category=primary_emoji,
            scope="",  # TODO: add scope support
            # TODO: breaking change v10, removes breaking change footers from descriptions
            # descriptions=(
            #     descriptions[:1] if level_bump is LevelBump.MAJOR else descriptions
            # )
            descriptions=descriptions,
            breaking_descriptions=(
                descriptions[1:] if level_bump is LevelBump.MAJOR else ()
            ),
            linked_merge_request=linked_merge_request,
        )

    def parse(self, commit: Commit) -> ParseResult:
        """
        Attempt to parse the commit message with a regular expression into a
        ParseResult
        """
        pmsg_result = self.parse_message(str(commit.message))

        logger.debug(
            "commit %s introduces a %s level_bump",
            commit.hexsha[:8],
            pmsg_result.bump,
        )

        return ParsedCommit.from_parsed_message_result(commit, pmsg_result)
