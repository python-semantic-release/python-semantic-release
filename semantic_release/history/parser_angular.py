import re

from ..errors import UnknownCommitMessageStyleError
from .parser_helpers import parse_text_block

re_parser = re.compile(
    r'(?P<type>feat|fix|docs|style|refactor|test|chore)'
    r'(?:\((?P<scope>[\w _\-]+)\))?: '
    r'(?P<subject>[^\n]+)'
    r'(:?\n\n(?P<text>.+))?',
    re.DOTALL
)

TYPES = {
    'feat': 'feature',
    'fix': 'fix',
    'test': 'test',
    'docs': 'documentation',
    'style': 'style',
    'refactor': 'refactor',
    'chore': 'chore',
}


def parse_commit_message(message):
    """
    Parses a commit message according to the angular commit guidelines specification.

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    """

    if not re_parser.match(message):
        raise UnknownCommitMessageStyleError(
            'Unable to parse the given commit message: {}'.format(message)
        )

    parsed = re_parser.match(message)
    level_bump = 0
    if parsed.group('text') and 'BREAKING CHANGE' in parsed.group('text'):
        level_bump = 3

    if parsed.group('type') == 'feat':
        level_bump = max([level_bump, 2])

    if parsed.group('type') == 'fix':
        level_bump = max([level_bump, 1])

    body, footer = parse_text_block(parsed.group('text'))

    return (
        level_bump,
        TYPES[parsed.group('type')],
        parsed.group('scope'),
        (parsed.group('subject'), body, footer)
    )
