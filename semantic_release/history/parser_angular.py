"""
Angular commit style parser

https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
import logging
import re

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from .parser_helpers import ParsedCommit, parse_paragraphs, re_breaking

logger = logging.getLogger(__name__)

# Supported commit types for parsing
TYPES = {
    "feat": "feature",
    "fix": "fix",
    "test": "test",
    "docs": "documentation",
    "style": "style",
    "refactor": "refactor",
    "build": "build",
    "ci": "ci",
    "perf": "performance",
    "chore": "chore",
}

re_parser = re.compile(
    r"(?P<type>" + "|".join(TYPES.keys()) + ")"
    r"(?:\((?P<scope>[^\n]+)\))?"
    r"(?P<break>!)?: "
    r"(?P<subject>[^\n]+)"
    r"(:?\n\n(?P<text>.+))?",
    re.DOTALL,
)

MINOR_TYPES = [
    "feat",
]

PATCH_TYPES = [
    "fix",
    "perf",
]


@LoggedFunction(logger)
def parse_commit_message(message: str) -> ParsedCommit:
    """
    Parse a commit message according to the angular commit guidelines specification.

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    :raises UnknownCommitMessageStyleError: if regular expression matching fails
    """
    # Attempt to parse the commit message with a regular expression
    parsed = re_parser.match(message)
    if not parsed:
        raise UnknownCommitMessageStyleError(
            f"Unable to parse the given commit message: {message}"
        )

    if parsed.group("text"):
        descriptions = parse_paragraphs(parsed.group("text"))
    else:
        descriptions = list()
    # Insert the subject before the other paragraphs
    descriptions.insert(0, parsed.group("subject"))

    # Look for descriptions of breaking changes
    breaking_descriptions = [
        match.group(1)
        for match in (re_breaking.match(p) for p in descriptions[1:])
        if match
    ]

    level_bump = 0
    if parsed.group("break") or breaking_descriptions:
        level_bump = 3  # Major
    elif parsed.group("type") in MINOR_TYPES:
        level_bump = 2  # Minor
    elif parsed.group("type") in PATCH_TYPES:
        level_bump = 1  # Patch

    return ParsedCommit(
        level_bump,
        TYPES[parsed.group("type")],
        parsed.group("scope"),
        descriptions,
        breaking_descriptions,
    )
