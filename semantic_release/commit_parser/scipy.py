"""
Parses commit messages using `scipy tags <scipy-style>`_ of the form::

    <tag>(<scope>): <subject>

    <body>


The elements <tag>, <scope> and <body> are optional. If no tag is present, the
commit will be added to the changelog section "None" and no version increment
will be performed.

While <scope> is supported here it isn't actually part of the scipy style.
If it is missing, parentheses around it are too. The commit should then be
of the form::

    <tag>: <subject>

    <body>

To communicate a breaking change add "BREAKING CHANGE" into the body at the
beginning of a paragraph. Fill this paragraph with information how to migrate
from the broken behavior to the new behavior. It will be added to the
"Breaking" section of the changelog.

Supported Tags::

    API, DEP, ENH, REV, BUG, MAINT, BENCH, BLD,
    DEV, DOC, STY, TST, REL, FEAT, TEST

Supported Changelog Sections::

    breaking, feature, fix, Other, None

.. _`scipy-style`: https://docs.scipy.org/doc/scipy/reference/dev/contributor/development_workflow.html#writing-the-commit-message
"""

import logging
import re
from dataclasses import dataclass
from typing import Tuple

from git import Commit

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseError, ParseResult
from semantic_release.enums import LevelBump

log = logging.getLogger(__name__)


tag_to_section = {
    "API": "breaking",
    "BENCH": "None",
    "BLD": "fix",
    "BUG": "fix",
    "DEP": "breaking",
    "DEV": "None",
    "DOC": "documentation",
    "ENH": "feature",
    "MAINT": "fix",
    "REV": "Other",
    "STY": "None",
    "TST": "None",
    "REL": "None",
    # strictly speaking not part of the standard
    "FEAT": "feature",
    "TEST": "None",
}

_COMMIT_FILTER = "|".join(tag_to_section)


@dataclass
class ScipyParserOptions(ParserOptions):
    allowed_tags: Tuple[str] = (
        "API",
        "DEP",
        "ENH",
        "REV",
        "BUG",
        "MAINT",
        "BENCH",
        "BLD",
        "DEV",
        "DOC",
        "STY",
        "TST",
        "REL",
        "FEAT",
        "TEST",
    )
    major_tags: Tuple[str] = ("API",)
    minor_tags: Tuple[str] = ("DEP", "DEV", "ENH", "REV", "FEAT")
    patch_tags: Tuple[str] = ("BLD", "BUG", "MAINT")
    default_level_bump: LevelBump = LevelBump.NO_RELEASE

    def __post_init__(self):
        self.tag_to_level = {tag: LevelBump.NO_RELEASE for tag in self.allowed_tags}
        for tag in self.patch_tags:
            self.tag_to_level[tag] = LevelBump.PATCH
        for tag in self.minor_tags:
            self.tag_to_level[tag] = LevelBump.MINOR
        for tag in self.major_tags:
            self.tag_to_level[tag] = LevelBump.MAJOR


class ScipyCommitParser(CommitParser[ParseResult[ParsedCommit, ParseError]]):
    """
    Parse a scipy-style commit message
    :param message: A string of a commit message.
    # :return: A tuple of (level to bump, type of change, scope of change, a tuple
    :return: A ParsedCommit
    with descriptions)
    :raises UnknownCommitMessageStyleError: if regular expression matching fails
    """

    parser_options = ScipyParserOptions

    def __init__(self, options: ScipyParserOptions) -> None:
        super().__init__(options)
        self.re_parser = re.compile(
            rf"(?P<tag>{_COMMIT_FILTER})?"
            r"(?:\((?P<scope>[^\n]+)\))?"
            r":? "
            r"(?P<subject>[^\n]+):?"
            r"(\n\n(?P<text>.*))?",
            re.DOTALL,
        )

    def parse(self, commit: Commit) -> ParseResult[ParsedCommit, ParseError]:

        message = commit.message
        parsed = self.re_parser.match(message)

        if not parsed:
            return ParseError(
                commit, f"Unable to parse the given commit message: {message}"
            )

        if parsed.group("subject"):
            subject = parsed.group("subject")
        else:
            parse_error = ParseError(commit, f"Commit has no subject {message!r}")
            log.debug("Error parsing commit %r, ignoring", commit.message)
            return parse_error

        if parsed.group("text"):
            blocks = parsed.group("text").split("\n\n")
            blocks = [x for x in blocks if not x == ""]
            blocks.insert(0, subject)
        else:
            blocks = [subject]

        for tag in self.options.allowed_tags:
            if tag == parsed.group("tag"):
                section = tag_to_section.get(tag, "None")
                level_bump = self.options.tag_to_level.get(
                    tag, self.options.default_level_bump
                )
                break
        else:
            # some commits may not have a tag, e.g. if they belong to a PR that
            # wasn't squashed (for maintainability) ignore them
            section, level_bump = "None", self.options.default_level_bump

        # Look for descriptions of breaking changes
        migration_instructions = [
            block for block in blocks if block.startswith("BREAKING CHANGE")
        ]
        if migration_instructions:
            level_bump = LevelBump.MAJOR

        return ParsedCommit(
            bump=level_bump,
            type=section,
            scope=parsed.group("scope"),
            descriptions=blocks,
            breaking_descriptions=migration_instructions,
            commit=commit,
        )
