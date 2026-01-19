"""Commit parser which looks for emojis to determine the type of commit"""

from __future__ import annotations

import re
from functools import reduce
from itertools import zip_longest
from re import compile as regexp
from textwrap import dedent
from typing import Tuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import (
    deep_copy_commit,
    force_str,
    parse_paragraphs,
)
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidParserOptions
from semantic_release.globals import logger
from semantic_release.helpers import sort_numerically, text_reducer


@dataclass
class EmojiParserOptions(ParserOptions):
    """Options dataclass for EmojiCommitParser"""

    major_tags: Tuple[str, ...] = (":boom:",)
    """Commit-type prefixes that should result in a major release bump."""

    minor_tags: Tuple[str, ...] = (
        ":sparkles:",
        ":children_crossing:",
        ":lipstick:",
        ":iphone:",
        ":egg:",
        ":chart_with_upwards_trend:",
    )
    """Commit-type prefixes that should result in a minor release bump."""

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
    """Commit-type prefixes that should result in a patch release bump."""

    other_allowed_tags: Tuple[str, ...] = (
        ":checkmark:",
        ":construction_worker:",
        ":memo:",
        ":recycle:",
    )
    """Commit-type prefixes that are allowed but do not result in a version bump."""

    allowed_tags: Tuple[str, ...] = (
        *major_tags,
        *minor_tags,
        *patch_tags,
        *other_allowed_tags,
    )
    """All commit-type prefixes that are allowed."""

    default_bump_level: LevelBump = LevelBump.NO_RELEASE
    """The minimum bump level to apply to valid commit message."""

    parse_linked_issues: bool = False
    """
    Whether to parse linked issues from the commit message.

    Issue identification is not defined in the Gitmoji specification, so this parser
    will not attempt to parse issues by default. If enabled, the parser will use the
    same identification as GitHub, GitLab, and BitBucket use for linking issues, which
    is to look for a git commit message footer starting with "Closes:", "Fixes:",
    or "Resolves:" then a space, and then the issue identifier. The line prefix
    can be singular or plural and it is not case-sensitive but must have a colon and
    a whitespace separator.
    """

    parse_squash_commits: bool = True
    """Toggle flag for whether or not to parse squash commits"""

    ignore_merge_commits: bool = True
    """Toggle flag for whether or not to ignore merge commits"""

    @property
    def tag_to_level(self) -> dict[str, LevelBump]:
        """A mapping of commit tags to the level bump they should result in."""
        return self._tag_to_level

    def __post_init__(self) -> None:
        self._tag_to_level: dict[str, LevelBump] = {
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
            highest_emoji_pattern = regexp(
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

        self.emoji_selector = regexp(
            str.join(
                "",
                [
                    f"^{highest_emoji_pattern.pattern}",
                    r"(?:\((?P<scope>[^)]+)\))?:?",
                ],
            )
        )

        # GitHub & Gitea use (#123), GitLab uses (!123), and BitBucket uses (pull request #123)
        self.mr_selector = regexp(
            r"[\t ]+\((?:pull request )?(?P<mr_number>[#!]\d+)\)[\t ]*$"
        )

        self.issue_selector = regexp(
            str.join(
                "",
                [
                    r"^(?:clos(?:e|es|ed|ing)|fix(?:es|ed|ing)?|resolv(?:e|es|ed|ing)|implement(?:s|ed|ing)?):",
                    r"[\t ]+(?P<issue_predicate>.+)[\t ]*$",
                ],
            ),
            flags=re.MULTILINE | re.IGNORECASE,
        )

        self.notice_selector = regexp(r"^NOTICE: (?P<notice>.+)$")

        self.filters = {
            "typo-extra-spaces": (regexp(r"(\S)  +(\S)"), r"\1 \2"),
            "git-header-commit": (
                regexp(r"^[\t ]*commit [0-9a-f]+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-header-author": (
                regexp(r"^[\t ]*Author: .+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-header-date": (
                regexp(r"^[\t ]*Date: .+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-squash-heading": (
                regexp(
                    r"^[\t ]*Squashed commit of the following:.*$\n?",
                    flags=re.MULTILINE,
                ),
                "",
            ),
            "git-squash-commit-prefix": (
                regexp(
                    str.join(
                        "",
                        [
                            r"^(?:[\t ]*[*-][\t ]+|[\t ]+)?",  # bullet points or indentation
                            highest_emoji_pattern.pattern
                            + r"(\W)",  # prior to commit type
                        ],
                    ),
                    flags=re.MULTILINE,
                ),
                # move commit type to the start of the line
                r"\1\2",
            ),
        }

    @staticmethod
    def get_default_options() -> EmojiParserOptions:
        return EmojiParserOptions()

    def commit_body_components_separator(
        self, accumulator: dict[str, list[str]], text: str
    ) -> dict[str, list[str]]:
        if (match := self.notice_selector.match(text)) and (
            notice := match.group("notice")
        ):
            accumulator["notices"].append(notice)
            return accumulator

        if self.options.parse_linked_issues and (
            match := self.issue_selector.search(text)
        ):
            predicate = regexp(r",? and | *[,;/& ] *").sub(
                ",", match.group("issue_predicate") or ""
            )
            # Almost all issue trackers use a number to reference an issue so
            # we use a simple regexp to validate the existence of a number which helps filter out
            # any non-issue references that don't fit our expected format
            has_number = regexp(r"\d+")
            new_issue_refs: set[str] = set(
                filter(
                    lambda issue_str, validator=has_number: validator.search(issue_str),  # type: ignore[arg-type]
                    predicate.split(","),
                )
            )
            if new_issue_refs:
                accumulator["linked_issues"] = sort_numerically(
                    set(accumulator["linked_issues"]).union(new_issue_refs)
                )
                return accumulator

        # Prevent appending duplicate descriptions
        if text not in accumulator["descriptions"]:
            accumulator["descriptions"].append(text)

        return accumulator

    def parse_message(self, message: str) -> ParsedMessageResult:
        msg_parts = message.split("\n", maxsplit=1)
        subject = msg_parts[0]
        msg_body = msg_parts[1] if len(msg_parts) > 1 else ""

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(subject):
            linked_merge_request = mr_match.group("mr_number")
            subject = self.mr_selector.sub("", subject).strip()

        # Search for emoji of the highest importance in the subject
        match = self.emoji_selector.search(subject)
        primary_emoji = match.group("type") if match else "Other"
        parsed_scope = (match.group("scope") if match else None) or ""

        level_bump = self.options.tag_to_level.get(
            primary_emoji, self.options.default_bump_level
        )

        # All emojis will remain part of the returned description
        body_components: dict[str, list[str]] = reduce(
            self.commit_body_components_separator,
            [
                subject,
                *parse_paragraphs(msg_body),
            ],
            {
                "descriptions": [],
                "notices": [],
                "linked_issues": [],
            },
        )

        descriptions = tuple(body_components["descriptions"])

        return ParsedMessageResult(
            bump=level_bump,
            type=primary_emoji,
            category=primary_emoji,
            scope=parsed_scope,
            descriptions=(
                descriptions[:1] if level_bump is LevelBump.MAJOR else descriptions
            ),
            breaking_descriptions=(
                descriptions[1:] if level_bump is LevelBump.MAJOR else ()
            ),
            release_notices=tuple(body_components["notices"]),
            linked_issues=tuple(body_components["linked_issues"]),
            linked_merge_request=linked_merge_request,
        )

    @staticmethod
    def is_merge_commit(commit: Commit) -> bool:
        return len(commit.parents) > 1

    def parse_commit(self, commit: Commit) -> ParseResult:
        return ParsedCommit.from_parsed_message_result(
            commit, self.parse_message(force_str(commit.message))
        )

    def parse(self, commit: Commit) -> ParseResult | list[ParseResult]:
        """
        Parse a commit message

        If the commit message is a squashed merge commit, it will be split into
        multiple commits, each of which will be parsed separately. Single commits
        will be returned as a list of a single ParseResult.
        """
        if self.options.ignore_merge_commits and self.is_merge_commit(commit):
            err_msg = "Ignoring merge commit: %s" % commit.hexsha[:8]
            logger.debug(err_msg)
            return ParseError(commit, err_msg)

        separate_commits: list[Commit] = (
            self.unsquash_commit(commit)
            if self.options.parse_squash_commits
            else [commit]
        )

        # Parse each commit individually if there were more than one
        parsed_commits: list[ParseResult] = list(
            map(self.parse_commit, separate_commits)
        )

        def add_linked_merge_request(
            parsed_result: ParseResult, mr_number: str
        ) -> ParseResult:
            return (
                parsed_result
                if not isinstance(parsed_result, ParsedCommit)
                else ParsedCommit(
                    **{
                        **parsed_result._asdict(),
                        "linked_merge_request": mr_number,
                    }
                )
            )

        # TODO: improve this for other VCS systems other than GitHub & BitBucket
        # Github works as the first commit in a squash merge commit has the PR number
        # appended to the first line of the commit message
        lead_commit = next(iter(parsed_commits))

        if isinstance(lead_commit, ParsedCommit) and lead_commit.linked_merge_request:
            # If the first commit has linked merge requests, assume all commits
            # are part of the same PR and add the linked merge requests to all
            # parsed commits
            parsed_commits = [
                lead_commit,
                *map(
                    lambda parsed_result, mr=lead_commit.linked_merge_request: (  # type: ignore[misc]
                        add_linked_merge_request(parsed_result, mr)
                    ),
                    parsed_commits[1:],
                ),
            ]

        return parsed_commits

    def unsquash_commit(self, commit: Commit) -> list[Commit]:
        # GitHub EXAMPLE:
        # ✨(changelog): add autofit_text_width filter to template environment (#1062)
        #
        # This change adds an equivalent style formatter that can apply a text alignment
        # to a maximum width and also maintain an indent over paragraphs of text
        #
        # * 🌐 Support Japanese language
        #
        # * ✅(changelog-context): add test cases to check autofit_text_width filter use
        #
        # `git merge --squash` EXAMPLE:
        # Squashed commit of the following:
        #
        # commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb
        # Author: codejedi365 <codejedi365@gmail.com>
        # Date:   Sun Oct 13 12:05:23 2024 -0000
        #
        #     ⚡️ (homepage): Lazyload home screen images
        #
        #
        # Return a list of artificial commits (each with a single commit message)
        return [
            # create a artificial commit object (copy of original but with modified message)
            Commit(
                **{
                    **deep_copy_commit(commit),
                    "message": commit_msg,
                }
            )
            for commit_msg in self.unsquash_commit_message(force_str(commit.message))
        ] or [commit]

    def unsquash_commit_message(self, message: str) -> list[str]:
        normalized_message = message.replace("\r", "").strip()

        # split by obvious separate commits (applies to manual git squash merges)
        obvious_squashed_commits = self.filters["git-header-commit"][0].split(
            normalized_message
        )

        separate_commit_msgs: list[str] = reduce(
            lambda all_msgs, msgs: all_msgs + msgs,
            map(self._find_squashed_commits_in_str, obvious_squashed_commits),
            [],
        )

        return list(filter(None, separate_commit_msgs))

    def _find_squashed_commits_in_str(self, message: str) -> list[str]:
        separate_commit_msgs: list[str] = []
        current_msg = ""

        for paragraph in filter(None, message.strip().split("\n\n")):
            # Apply filters to normalize the paragraph
            clean_paragraph = reduce(text_reducer, self.filters.values(), paragraph)

            # remove any filtered (and now empty) paragraphs (ie. the git headers)
            if not clean_paragraph.strip():
                continue

            # Check if the paragraph is the start of a new emoji commit
            if not self.emoji_selector.search(clean_paragraph):
                if not separate_commit_msgs and not current_msg:
                    # if there are no separate commit messages and no current message
                    # then this is the first commit message
                    current_msg = dedent(clean_paragraph)
                    continue

                # append the paragraph as part of the previous commit message
                if current_msg:
                    current_msg += f"\n\n{dedent(clean_paragraph)}"
                # else: drop the paragraph
                continue

            # Since we found the start of the new commit, store any previous commit
            # message separately and start the new commit message
            if current_msg:
                separate_commit_msgs.append(current_msg)

            current_msg = clean_paragraph

        return [*separate_commit_msgs, current_msg]
