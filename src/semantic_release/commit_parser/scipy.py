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
from typing import TYPE_CHECKING, Tuple

from pydantic.dataclasses import dataclass

from semantic_release.commit_parser.angular import (
    AngularCommitParser,
    AngularParserOptions,
)
from semantic_release.commit_parser.token import (
    ParsedMessageResult,
    ParseError,
)
from semantic_release.enums import LevelBump

if TYPE_CHECKING:  # pragma: no cover
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


@dataclass
class ScipyParserOptions(AngularParserOptions):
    """
    Options dataclass for ScipyCommitParser

    Scipy-style commit messages follow the same format as Angular-style commit
    just with different tag names.
    """

    major_tags: Tuple[str, ...] = ("API",)
    """Commit-type prefixes that should result in a major release bump."""

    minor_tags: Tuple[str, ...] = ("DEP", "DEV", "ENH", "REV", "FEAT")
    """Commit-type prefixes that should result in a minor release bump."""

    patch_tags: Tuple[str, ...] = ("BLD", "BUG", "MAINT")
    """Commit-type prefixes that should result in a patch release bump."""

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
    """
    All commit-type prefixes that are allowed.

    These are used to identify a valid commit message. If a commit message does not start with
    one of these prefixes, it will not be considered a valid commit message.
    """

    # TODO: breaking v10, make consistent with AngularParserOptions
    default_level_bump: LevelBump = LevelBump.NO_RELEASE
    """The minimum bump level to apply to valid commit message."""

    def __post_init__(self) -> None:
        # TODO: breaking v10, remove as the name is now consistent
        self.default_bump_level = self.default_level_bump
        super().__post_init__()
        for tag in self.major_tags:
            self._tag_to_level[tag] = LevelBump.MAJOR


class ScipyCommitParser(AngularCommitParser):
    """Parser for scipy-style commit messages"""

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = ScipyParserOptions

    def __init__(self, options: ScipyParserOptions | None = None) -> None:
        super().__init__(options)

    @staticmethod
    def get_default_options() -> ScipyParserOptions:
        return ScipyParserOptions()

    def parse_message(self, message: str) -> ParsedMessageResult | None:
        return (
            None
            if not (pmsg_result := super().parse_message(message))
            else ParsedMessageResult(
                **{
                    **pmsg_result._asdict(),
                    "category": tag_to_section.get(pmsg_result.type, "None"),
                }
            )
        )
