"""
Angular commit style parser

https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
import logging
import re

from ..errors import ImproperConfigurationError, UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from ..settings import config
from .parser_helpers import ParsedCommit, parse_paragraphs, re_breaking

logger = logging.getLogger(__name__)


# types with long names in changelog
LONG_TYPE_NAMES = {
    "feat": "feature",
    "docs": "documentation",
    "perf": "performance",
}

LEVEL_BUMPS = {"no-release": 0, "patch": 1, "minor": 2, "major": 3}


@LoggedFunction(logger)
def parse_commit_message(message: str) -> ParsedCommit:
    """
    Parse a commit message according to the angular commit guidelines specification.

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    :raises UnknownCommitMessageStyleError: if regular expression matching fails
    """

    # loading these are here to make it easier to mock in tests
    allowed_types = config.get("parser_angular_allowed_types").split(",")
    minor_types = config.get("parser_angular_minor_types").split(",")
    patch_types = config.get("parser_angular_patch_types").split(",")
    re_parser = re.compile(
        r"(?P<type>" + "|".join(allowed_types) + ")"
        r"(?:\((?P<scope>[^\n]+)\))?"
        r"(?P<break>!)?: "
        r"(?P<subject>[^\n]+)"
        r"(:?\n\n(?P<text>.+))?",
        re.DOTALL,
    )

    # Attempt to parse the commit message with a regular expression
    parsed = re_parser.match(message)
    if not parsed:
        raise UnknownCommitMessageStyleError(
            f"Unable to parse the given commit message: {message}"
        )
    parsed_break = parsed.group("break")
    parsed_scope = parsed.group("scope")
    parsed_subject = parsed.group("subject")
    parsed_text = parsed.group("text")
    parsed_type = parsed.group("type")

    if parsed_text:
        descriptions = parse_paragraphs(parsed_text)
    else:
        descriptions = list()
    # Insert the subject before the other paragraphs
    descriptions.insert(0, parsed_subject)

    # Look for descriptions of breaking changes
    breaking_descriptions = [
        match.group(1)
        for match in (re_breaking.match(p) for p in descriptions[1:])
        if match
    ]

    default_level_bump = config.get("parser_angular_default_level_bump").lower()
    if default_level_bump not in LEVEL_BUMPS.keys():
        raise ImproperConfigurationError(
            f"{default_level_bump} is not a valid option for "
            f"parser_angular_default_level_bump.\n"
            f"valid options are: {', '.join(LEVEL_BUMPS.keys())}"
        )
    level_bump = LEVEL_BUMPS[default_level_bump]
    if parsed_break or breaking_descriptions:
        level_bump = 3  # Major
    elif parsed_type in minor_types:
        level_bump = 2  # Minor
    elif parsed_type in patch_types:
        level_bump = 1  # Patch

    parsed_type_long = LONG_TYPE_NAMES.get(parsed_type, parsed_type)
    # first param is the key you're getting from the dict,
    # second param is the default value
    # allows only putting types with a long name in the LONG_TYPE_NAMES dict

    return ParsedCommit(
        level_bump,
        parsed_type_long,
        parsed_scope,
        descriptions,
        breaking_descriptions,
    )
