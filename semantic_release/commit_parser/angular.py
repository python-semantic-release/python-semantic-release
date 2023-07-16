"""
Angular commit style parser
https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
from __future__ import annotations

import logging
import re
from typing import Tuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseError, ParseResult
from semantic_release.commit_parser.util import breaking_re, parse_paragraphs
from semantic_release.enums import LevelBump

log = logging.getLogger(__name__)


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    log.debug(error)
    return ParseError(commit, error=error)


# types with long names in changelog
LONG_TYPE_NAMES = {
    "feat": "feature",
    "docs": "documentation",
    "perf": "performance",
}


@dataclass
class AngularParserOptions(ParserOptions):
    """
    Options dataclass for AngularCommitParser
    """

    allowed_tags: Tuple[str, ...] = (
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "style",
        "refactor",
        "test",
    )
    minor_tags: Tuple[str, ...] = ("feat",)
    patch_tags: Tuple[str, ...] = ("fix", "perf")
    default_bump_level: LevelBump = LevelBump.NO_RELEASE


class AngularCommitParser(CommitParser[ParseResult, AngularParserOptions]):
    """
    A commit parser for projects conforming to the angular style of conventional
    commits. See https://www.conventionalcommits.org/en/v1.0.0-beta.4/
    """

    parser_options = AngularParserOptions

    def __init__(self, options: AngularParserOptions) -> None:
        super().__init__(options)
        self.re_parser = re.compile(
            rf"""
            (?P<type>{"|".join(options.allowed_tags)})  # e.g. feat
            (?:\((?P<scope>[^\n]+)\))?  # or feat(parser)
            (?P<break>!)?:\s+  # breaking if feat!:
            (?P<subject>[^\n]+)  # commit subject
            (:?\n\n(?P<text>.+))?  # commit body
            """,
            flags=re.VERBOSE | re.DOTALL,
        )

    # Maybe this can be cached as an optimisation, similar to how
    # mypy/pytest use their own caching directories, for very large commit
    # histories?
    # The problem is the cache likely won't be present in CI environments
    def parse(self, commit: Commit) -> ParseResult:
        """
        Attempt to parse the commit message with a regular expression into a
        ParseResult
        """
        message = str(commit.message)
        parsed = self.re_parser.match(message)
        if not parsed:
            return _logged_parse_error(
                commit, f"Unable to parse commit message: {message}"
            )
        parsed_break = parsed.group("break")
        parsed_scope = parsed.group("scope")
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

        descriptions = parse_paragraphs(parsed_text) if parsed_text else []
        # Insert the subject before the other paragraphs
        descriptions.insert(0, parsed_subject)

        # Look for descriptions of breaking changes
        breaking_descriptions = [
            match.group(1)
            for match in (breaking_re.match(p) for p in descriptions[1:])
            if match
        ]

        if parsed_break or breaking_descriptions:
            level_bump = LevelBump.MAJOR
            parsed_type = "breaking"
        elif parsed_type in self.options.minor_tags:
            level_bump = LevelBump.MINOR
        elif parsed_type in self.options.patch_tags:
            level_bump = LevelBump.PATCH
        else:
            level_bump = self.options.default_bump_level
            log.debug(
                "commit %s introduces a level bump of %s due to the default_bump_level",
                commit.hexsha,
                level_bump,
            )
        log.debug("commit %s introduces a %s level_bump", commit.hexsha, level_bump)

        return ParsedCommit(
            bump=level_bump,
            type=LONG_TYPE_NAMES.get(parsed_type, parsed_type),
            scope=parsed_scope,
            descriptions=descriptions,
            breaking_descriptions=breaking_descriptions,
            commit=commit,
        )
