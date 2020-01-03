"""Angular commit style commit parser
"""
import re
from typing import Tuple

import ndebug

from ..errors import UnknownCommitMessageStyleError
from .parser_helpers import parse_text_block, re_breaking

debug = ndebug.create(__name__)

TYPES = {
    'feat': 'feature',
    'fix': 'fix',
    'test': 'test',
    'docs': 'documentation',
    'style': 'style',
    'refactor': 'refactor',
    'build': 'build',
    'ci': 'ci',
    'perf': 'performance',
    'chore': 'chore',
}

re_parser = re.compile(
    r'(?P<type>' + '|'.join(TYPES.keys()) + ')'
    r'(?:\((?P<scope>[^\n]+)\))?'
    r'(?P<break>!)?: '
    r'(?P<subject>[^\n]+)'
    r'(:?\n\n(?P<text>.+))?',
    re.DOTALL
)

MINOR_TYPES = [
    'feat',
]

PATCH_TYPES = [
    'fix',
    'perf',
]


def parse_commit_message(message: str) -> Tuple[int, str, str, Tuple[str, str, str]]:
    """
    Parses a commit message according to the angular commit guidelines specification.

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    :raises UnknownCommitMessageStyleError: if regular expression matching fails
    """
    parsed = re_parser.match(message)
    if not parsed:
        raise UnknownCommitMessageStyleError(
            'Unable to parse the given commit message: {}'.format(message)
        )

    body, footer = parse_text_block(parsed.group('text'))

    level_bump = 0
    if parsed.group('break') or re_breaking.match(body) or re_breaking.match(footer):
        level_bump = 3

    if parsed.group('type') in MINOR_TYPES:
        level_bump = max([level_bump, 2])

    if parsed.group('type') in PATCH_TYPES:
        level_bump = max([level_bump, 1])

    if debug.enabled:
        debug('parse_commit_message -> ({}, {}, {}, {})'.format(
            level_bump,
            TYPES[parsed.group('type')],
            parsed.group('scope'),
            (parsed.group('subject'), body, footer)
        ))
    return (
        level_bump,
        TYPES[parsed.group('type')],
        parsed.group('scope'),
        (parsed.group('subject'), body, footer)
    )
