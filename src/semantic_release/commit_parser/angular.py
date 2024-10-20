"""
Angular commit style parser
https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""

from __future__ import annotations

import logging
import re
from functools import reduce
from itertools import zip_longest
from re import compile as regexp
from typing import TYPE_CHECKING, Tuple

from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import breaking_re, parse_paragraphs
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from git.objects.commit import Commit


logger = logging.getLogger(__name__)


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    logger.debug(error)
    return ParseError(commit, error=error)


# TODO: Remove from here, allow for user customization instead via options
# types with long names in changelog
LONG_TYPE_NAMES = {
    "build": "build system",
    "ci": "continuous integration",
    "chore": "chores",
    "docs": "documentation",
    "feat": "features",
    "fix": "bug fixes",
    "perf": "performance improvements",
    "refactor": "refactoring",
    "style": "code style",
    "test": "testing",
}


@dataclass
class AngularParserOptions(ParserOptions):
    """Options dataclass for AngularCommitParser"""

    minor_tags: Tuple[str, ...] = ("feat",)
    patch_tags: Tuple[str, ...] = ("fix", "perf")
    allowed_tags: Tuple[str, ...] = (
        *minor_tags,
        *patch_tags,
        "build",
        "chore",
        "ci",
        "docs",
        "style",
        "refactor",
        "test",
    )
    default_bump_level: LevelBump = LevelBump.NO_RELEASE

    def __post_init__(self) -> None:
        self.tag_to_level: dict[str, LevelBump] = dict(
            [
                # we have to do a type ignore as zip_longest provides a type that is not specific enough
                # for our expected output. Due to the empty second array, we know the first is always longest
                # and that means no values in the first entry of the tuples will ever be a LevelBump.
                *zip_longest(self.allowed_tags, (), fillvalue=self.default_bump_level),  # type: ignore[list-item]
                *zip_longest(self.patch_tags, (), fillvalue=LevelBump.PATCH),  # type: ignore[list-item]
                *zip_longest(self.minor_tags, (), fillvalue=LevelBump.MINOR),  # type: ignore[list-item]
            ]
        )


class AngularCommitParser(CommitParser[ParseResult, AngularParserOptions]):
    """
    A commit parser for projects conforming to the angular style of conventional
    commits. See https://www.conventionalcommits.org/en/v1.0.0-beta.4/
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = AngularParserOptions

    def __init__(self, options: AngularParserOptions | None = None) -> None:
        super().__init__(options)
        all_possible_types = str.join("|", self.options.allowed_tags)
        self.re_parser = regexp(
            str.join(
                "",
                [
                    r"(?P<type>%s)" % all_possible_types,
                    r"(?:\((?P<scope>[^\n]+)\))?",
                    # TODO: remove ! support as it is not part of the angular commit spec (its part of conventional commits spec)
                    r"(?P<break>!)?:\s+",
                    r"(?P<subject>[^\n]+)",
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=re.DOTALL,
        )
        # GitHub & Gitea use (#123), GitLab uses (!123), and BitBucket uses (pull request #123)
        self.mr_selector = regexp(
            r"[\t ]\((?:pull request )?(?P<mr_number>[#!]\d+)\)[\t ]*$"
        )

    @staticmethod
    def get_default_options() -> AngularParserOptions:
        return AngularParserOptions()

    def commit_body_components_separator(
        self, accumulator: dict[str, list[str]], text: str
    ) -> dict[str, list[str]]:
        if match := breaking_re.match(text):
            accumulator["breaking_descriptions"].append(match.group(1) or "")
            # TODO: breaking change v10, removes breaking change footers from descriptions
            # return accumulator

        accumulator["descriptions"].append(text)
        return accumulator

    def parse_message(self, message: str) -> ParsedMessageResult | None:
        if not (parsed := self.re_parser.match(message)):
            return None

        parsed_break = parsed.group("break")
        parsed_scope = parsed.group("scope")
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(parsed_subject):
            linked_merge_request = mr_match.group("mr_number")
            # TODO: breaking change v10, removes PR number from subject/descriptions
            # expects changelog template to format the line accordingly
            # parsed_subject = self.pr_selector.sub("", parsed_subject).strip()

        body_components: dict[str, list[str]] = reduce(
            self.commit_body_components_separator,
            [
                # Insert the subject before the other paragraphs
                parsed_subject,
                *parse_paragraphs(parsed_text or ""),
            ],
            {
                "breaking_descriptions": [],
                "descriptions": [],
            },
        )

        level_bump = (
            LevelBump.MAJOR
            # TODO: remove parsed break support as it is not part of the angular commit spec (its part of conventional commits spec)
            if body_components["breaking_descriptions"] or parsed_break
            else self.options.tag_to_level.get(
                parsed_type, self.options.default_bump_level
            )
        )

        return ParsedMessageResult(
            bump=level_bump,
            type=parsed_type,
            category=LONG_TYPE_NAMES.get(parsed_type, parsed_type),
            scope=parsed_scope,
            descriptions=tuple(body_components["descriptions"]),
            breaking_descriptions=tuple(body_components["breaking_descriptions"]),
            linked_merge_request=linked_merge_request,
        )

    # Maybe this can be cached as an optimization, similar to how
    # mypy/pytest use their own caching directories, for very large commit
    # histories?
    # The problem is the cache likely won't be present in CI environments
    def parse(self, commit: Commit) -> ParseResult:
        """
        Attempt to parse the commit message with a regular expression into a
        ParseResult
        """
        if not (pmsg_result := self.parse_message(str(commit.message))):
            return _logged_parse_error(
                commit, f"Unable to parse commit message: {commit.message!r}"
            )

        logger.debug(
            "commit %s introduces a %s level_bump",
            commit.hexsha[:8],
            pmsg_result.bump,
        )

        return ParsedCommit.from_parsed_message_result(commit, pmsg_result)
