"""
Angular commit style parser

https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""
import logging
import re

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from ..settings import config
from .parser_helpers import ParsedCommit, parse_paragraphs, re_breaking

logger = logging.getLogger(__name__)

# Supported commit types for parsing
allowed_types = config.get('parser_angular_allowed_types').split(',')

# types with long names in changelog
TYPES = {
    "feat": "feature",
    "docs": "documentation",
    "perf": "performance",
}

re_parser = re.compile(
    r"(?P<type>" + "|".join(allowed_types) + ")"
    r"(?:\((?P<scope>[^\n]+)\))?"
    r"(?P<break>!)?: "
    r"(?P<subject>[^\n]+)"
    r"(:?\n\n(?P<text>.+))?",
    re.DOTALL,
)

MINOR_TYPES = config.get('parser_angular_minor_types').split(',')
PATCH_TYPES = config.get('parser_angular_patch_types').split(',')

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
    parsed_break   = parsed.group('break')
    parsed_scope   = parsed.group('scope')
    parsed_subject = parsed.group('subject')
    parsed_text    = parsed.group('text')
    parsed_type    = parsed.group('type')


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

    level_bump = int(config.get('parser_angular_default_level_bump'))
    if parsed_break or breaking_descriptions:
        level_bump = 3  # Major
    elif parsed_type in MINOR_TYPES:
        level_bump = 2  # Minor
    elif parsed_type in PATCH_TYPES:
        level_bump = 1  # Patch

    parsed_type_long = TYPES.get(parsed_type, parsed_type)
    # first param is the key you're getting from the dict,
    # second param is the default value
    # allows only putting types with a long name in the TYPES dict

    return ParsedCommit(
        level_bump,
        parsed_type_long,
        parsed_scope,
        descriptions,
        breaking_descriptions,
    )
