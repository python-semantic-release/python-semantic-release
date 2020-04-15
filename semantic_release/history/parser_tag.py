"""Legacy commit parser from Python Semantic Release 1.0"""
import logging
import re
from typing import Optional, Tuple

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from ..settings import config
from .parser_helpers import ParsedCommit, parse_text_block

logger = logging.getLogger(__name__)

re_parser = re.compile(r"(?P<subject>[^\n]+)" r"(:?\n\n(?P<text>.+))?", re.DOTALL)


@LoggedFunction(logger)
def parse_commit_message(
    message: str,
) -> Tuple[int, str, Optional[str], Tuple[str, str, str]]:
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
            "Unable to parse the given commit message: {0}".format(message)
        )

    subject = parsed.group("subject")

    # Check tags for minor or patch
    if config.get("semantic_release", "minor_tag") in message:
        level = "feature"
        level_bump = 2
        if subject:
            subject = subject.replace(config.get("semantic_release", "minor_tag"), "")

    elif config.get("semantic_release", "fix_tag") in message:
        level = "fix"
        level_bump = 1
        if subject:
            subject = subject.replace(config.get("semantic_release", "fix_tag"), "")

    else:
        # We did not find any tags in the commit message
        raise UnknownCommitMessageStyleError(
            "Unable to parse the given commit message: {0}".format(message)
        )

    if parsed.group("text") and "BREAKING CHANGE" in parsed.group("text"):
        level = "breaking"
        level_bump = 3

    body, footer = parse_text_block(parsed.group("text"))
    descriptions = (subject.strip(), body.strip(), footer.strip())
    return ParsedCommit(level_bump, level, None, descriptions)
