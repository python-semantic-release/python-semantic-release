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

    (
        API,
        DEP,
        ENH,
        REV,
        BUG,
        MAINT,
        BENCH,
        BLD,
    )
    DEV, DOC, STY, TST, REL, FEAT, TEST

Supported Changelog Sections::

    breaking, feature, fix, Other, None

.. _`scipy-style`: https://docs.scipy.org/doc/scipy/reference/dev/contributor/development_workflow.html#writing-the-commit-message
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Tuple

from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseError, ParseResult
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from git.objects.commit import Commit

logger = logging.getLogger(__name__)


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    logger.debug(error)
    return ParseError(commit, error=error)


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
    major_tags: Tuple[str, ...] = ("API",)
    minor_tags: Tuple[str, ...] = ("DEP", "DEV", "ENH", "REV", "FEAT")
    patch_tags: Tuple[str, ...] = ("BLD", "BUG", "MAINT")
    allowed_tags: Tuple[str, ...] = (
        *major_tags,
        *minor_tags,
        *patch_tags,
        "BENCH",
        "DOC",
        "STY",
        "TST",
        "REL",
        "TEST",
    )
    default_level_bump: LevelBump = LevelBump.NO_RELEASE

    def __post_init__(self) -> None:
        self.tag_to_level = {tag: LevelBump.NO_RELEASE for tag in self.allowed_tags}
        for tag in self.patch_tags:
            self.tag_to_level[tag] = LevelBump.PATCH
        for tag in self.minor_tags:
            self.tag_to_level[tag] = LevelBump.MINOR
        for tag in self.major_tags:
            self.tag_to_level[tag] = LevelBump.MAJOR


class ScipyCommitParser(CommitParser[ParseResult, ScipyParserOptions]):
    """Parser for scipy-style commit messages"""

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = ScipyParserOptions

    def __init__(self, options: ScipyParserOptions | None = None) -> None:
        super().__init__(options)
        self.re_parser = re.compile(
            rf"(?P<tag>{_COMMIT_FILTER})?"
            r"(?:\((?P<scope>[^\n]+)\))?"
            r":? "
            r"(?P<subject>[^\n]+):?"
            r"(\n\n(?P<text>.*))?",
            re.DOTALL,
        )

    @staticmethod
    def get_default_options() -> ScipyParserOptions:
        return ScipyParserOptions()

    def parse(self, commit: Commit) -> ParseResult:
        message = str(commit.message)
        parsed = self.re_parser.match(message)

        if not parsed:
            return _logged_parse_error(
                commit, f"Unable to parse the given commit message: {message}"
            )

        if parsed.group("subject"):
            subject = parsed.group("subject")
        else:
            return _logged_parse_error(commit, f"Commit has no subject {message!r}")

        if parsed.group("text"):
            blocks = parsed.group("text").split("\n\n")
            blocks = [x for x in blocks if x]
            blocks.insert(0, subject)
        else:
            blocks = [subject]

        for tag in self.options.allowed_tags:
            if tag == parsed.group("tag"):
                section = tag_to_section.get(tag, "None")
                level_bump = self.options.tag_to_level.get(
                    tag, self.options.default_level_bump
                )
                logger.debug(
                    "commit %s introduces a %s level_bump",
                    commit.hexsha[:8],
                    level_bump,
                )
                break
        else:
            # some commits may not have a tag, e.g. if they belong to a PR that
            # wasn't squashed (for maintainability) ignore them
            section, level_bump = "None", self.options.default_level_bump
            logger.debug(
                "commit %s introduces a level bump of %s due to the default bump level",
                commit.hexsha[:8],
                level_bump,
            )

        # Look for descriptions of breaking changes
        migration_instructions = [
            block for block in blocks if block.startswith("BREAKING CHANGE")
        ]
        if migration_instructions:
            level_bump = LevelBump.MAJOR
            logger.debug(
                "commit %s upgraded to a %s level bump due to included migration instructions",
                commit.hexsha[:8],
                level_bump,
            )

        return ParsedCommit(
            bump=level_bump,
            type=section,
            scope=parsed.group("scope"),
            descriptions=blocks,
            breaking_descriptions=migration_instructions,
            commit=commit,
        )
