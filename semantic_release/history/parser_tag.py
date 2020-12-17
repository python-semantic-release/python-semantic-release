"""Legacy commit parser from Python Semantic Release 1.0"""
import logging
import re
from typing import Optional

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from ..settings import config
from .parser_helpers import ParsedCommit, parse_paragraphs, re_breaking

logger = logging.getLogger(__name__)

re_parser = re.compile(r"(?P<subject>[^\n]+)" r"(:?\n\n(?P<text>.+))?", re.DOTALL)


@LoggedFunction(logger)
def parse_commit_message(
    message: str,
) -> ParsedCommit:
    """
    Parse a commit message according to the 1.0 version of python-semantic-release.

    It expects a tag of some sort in the commit message and will use the rest of the first line
    as changelog content.

    :param message: A string of a commit message.
    :raises UnknownCommitMessageStyleError: If it does not recognise the commit style
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    """

    # Attempt to parse the commit message with a regular expression
    parsed = re_parser.match(message)
    if not parsed:
        raise UnknownCommitMessageStyleError(
            f"Unable to parse the given commit message: {message}"
        )

    subject = parsed.group("subject")

    # Check tags for minor or patch
    if config.get("minor_tag") in message:
        level = "feature"
        level_bump = 2
        if subject:
            subject = subject.replace(config.get("minor_tag"), "")

    elif config.get("fix_tag") in message:
        level = "fix"
        level_bump = 1
        if subject:
            subject = subject.replace(config.get("fix_tag"), "")

    else:
        # We did not find any tags in the commit message
        raise UnknownCommitMessageStyleError(
            f"Unable to parse the given commit message: {message}"
        )

    if parsed.group("text"):
        descriptions = parse_paragraphs(parsed.group("text"))
    else:
        descriptions = list()
    descriptions.insert(0, subject.strip())

    # Look for descriptions of breaking changes
    breaking_descriptions = [
        match.group(1)
        for match in (re_breaking.match(p) for p in descriptions[1:])
        if match
    ]
    if breaking_descriptions:
        level = "breaking"
        level_bump = 3

    return ParsedCommit(level_bump, level, None, descriptions, breaking_descriptions)
