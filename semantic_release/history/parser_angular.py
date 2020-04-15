"""
Angular commit style parser

https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
import logging
import re
from typing import Tuple

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from .parser_helpers import ParsedCommit, parse_text_block, re_breaking

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
def parse_commit_message(message: str) -> Tuple[int, str, str, Tuple[str, str, str]]:
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
            "Unable to parse the given commit message: {}".format(message)
        )

    body, footer = parse_text_block(parsed.group("text"))

    # Check for mention of breaking changes
    level_bump = 0
    if parsed.group("break") or re_breaking.match(body) or re_breaking.match(footer):
        level_bump = 3  # Major

    # Set the bump level based on commit type
    if parsed.group("type") in MINOR_TYPES:
        level_bump = max([level_bump, 2])

    if parsed.group("type") in PATCH_TYPES:
        level_bump = max([level_bump, 1])

    return ParsedCommit(
        level_bump,
        TYPES[parsed.group("type")],
        parsed.group("scope"),
        (parsed.group("subject"), body, footer),
    )
