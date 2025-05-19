"""Legacy commit parser from Python Semantic Release 1.0"""

from __future__ import annotations

import re

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseError, ParseResult
from semantic_release.commit_parser.util import breaking_re, parse_paragraphs
from semantic_release.enums import LevelBump
from semantic_release.globals import logger

re_parser = re.compile(r"(?P<subject>[^\n]+)" + r"(:?\n\n(?P<text>.+))?", re.DOTALL)


@dataclass
class TagParserOptions(ParserOptions):
    minor_tag: str = ":sparkles:"
    patch_tag: str = ":nut_and_bolt:"


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    logger.debug(error)
    return ParseError(commit, error=error)


class TagCommitParser(CommitParser[ParseResult, TagParserOptions]):
    """
    Parse a commit message according to the 1.0 version of python-semantic-release.
    It expects a tag of some sort in the commit message and will use the rest of the
    first line as changelog content.
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = TagParserOptions

    @staticmethod
    def get_default_options() -> TagParserOptions:
        return TagParserOptions()

    def parse(self, commit: Commit) -> ParseResult | list[ParseResult]:
        message = str(commit.message)

        # Attempt to parse the commit message with a regular expression
        parsed = re_parser.match(message)
        if not parsed:
            return _logged_parse_error(
                commit, error=f"Unable to parse the given commit message: {message!r}"
            )

        subject = parsed.group("subject")

        # Check tags for minor or patch
        if self.options.minor_tag in message:
            level = "feature"
            level_bump = LevelBump.MINOR
            if subject:
                subject = subject.replace(self.options.minor_tag, "")

        elif self.options.patch_tag in message:
            level = "fix"
            level_bump = LevelBump.PATCH
            if subject:
                subject = subject.replace(self.options.patch_tag, "")

        else:
            # We did not find any tags in the commit message
            return _logged_parse_error(
                commit, error=f"Unable to parse the given commit message: {message!r}"
            )

        if parsed.group("text"):
            descriptions = parse_paragraphs(parsed.group("text"))
        else:
            descriptions = []
        descriptions.insert(0, subject.strip())

        # Look for descriptions of breaking changes
        breaking_descriptions = [
            match.group(1)
            for match in (breaking_re.match(p) for p in descriptions[1:])
            if match
        ]
        if breaking_descriptions:
            level = "breaking"
            level_bump = LevelBump.MAJOR
            logger.debug(
                "commit %s upgraded to a %s level_bump due to included breaking descriptions",
                commit.hexsha[:8],
                level_bump,
            )

        logger.debug(
            "commit %s introduces a %s level_bump", commit.hexsha[:8], level_bump
        )

        return ParsedCommit(
            bump=level_bump,
            type=level,
            scope="",
            descriptions=descriptions,
            breaking_descriptions=breaking_descriptions,
            commit=commit,
        )
