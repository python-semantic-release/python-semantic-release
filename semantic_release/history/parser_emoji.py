"""Commit parser which looks for emojis to determine the type of commit"""
import logging
import re
from typing import Optional

from ..helpers import LoggedFunction
from ..settings import config
from .parser_helpers import ParsedCommit, parse_paragraphs

logger = logging.getLogger(__name__)


@LoggedFunction(logger)
def parse_commit_message(
    message: str,
) -> ParsedCommit:
    """
    Parse a commit using an emoji in the subject line.

    When multiple emojis are encountered, the one with the highest bump
    level is used. If there are multiple emojis on the same level, the
    we use the one listed earliest in the configuration.

    If the message does not contain any known emojis, then the level to bump
    will be 0 and the type of change "Other". This parser never raises
    UnknownCommitMessageStyleError.

    Emojis are not removed from the description, and will appear alongside
    the commit subject in the changelog.

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    """

    subject = message.split("\n")[0]

    major = config.get("major_emoji").split(",")
    minor = config.get("minor_emoji").split(",")
    patch = config.get("patch_emoji").split(",")
    all_emojis = major + minor + patch

    # Loop over emojis from most important to least important
    # Therefore, we find the highest level emoji first
    primary_emoji = "Other"
    for emoji in all_emojis:
        if emoji in subject:
            primary_emoji = emoji
            break
    logger.debug(f"Selected {primary_emoji} as the primary emoji")

    # Find which level this commit was from
    level_bump = 0
    if primary_emoji in major:
        level_bump = 3
    elif primary_emoji in minor:
        level_bump = 2
    elif primary_emoji in patch:
        level_bump = 1

    # All emojis will remain part of the returned description
    descriptions = parse_paragraphs(message)
    return ParsedCommit(
        level_bump,
        primary_emoji,
        None,
        descriptions,
        descriptions[1:] if level_bump == 3 else [],
    )
