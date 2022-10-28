"""
Angular commit style parser
https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
import logging
import re
from typing import Tuple

from git import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseError, ParseResult
from semantic_release.commit_parser.util import breaking_re, parse_paragraphs
from semantic_release.enums import LevelBump

log = logging.getLogger(__name__)


# types with long names in changelog
LONG_TYPE_NAMES = {
    "feat": "feature",
    "docs": "documentation",
    "perf": "performance",
}


@dataclass
class AngularParserOptions(ParserOptions):
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


class AngularCommitParser(CommitParser[ParseResult[ParsedCommit, ParseError]]):
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

    # TODO: maybe cache?
    def parse(self, commit: Commit) -> ParseResult[ParsedCommit, ParseError]:
        # Attempt to parse the commit message with a regular expression
        parsed = self.re_parser.match(commit.message)
        if not parsed:
            parse_error = ParseError(commit, "Unable to parse commit message")
            log.debug("Error parsing commit %r", commit.message)
            return parse_error
        parsed_break = parsed.group("break")
        parsed_scope = parsed.group("scope")
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

        if parsed_text:
            descriptions = parse_paragraphs(parsed_text)
        else:
            descriptions = []
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
            # TODO: maybe this isn't the right thing to do
            parsed_type = "breaking"
        elif parsed_type in self.options.minor_tags:
            level_bump = LevelBump.MINOR
        elif parsed_type in self.options.patch_tags:
            level_bump = LevelBump.PATCH
        else:
            level_bump = self.options.default_bump_level

        return ParsedCommit(
            bump=level_bump,
            type=LONG_TYPE_NAMES.get(parsed_type, parsed_type),
            scope=parsed_scope,
            descriptions=descriptions,
            breaking_descriptions=breaking_descriptions,
            commit=commit,
        )
