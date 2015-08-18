import re

from semantic_release.errors import UnknownCommitMessageStyle

re_parser = re.compile(
    r'(?P<type>feat|fix|docs|style|refactor|test|chore)'
    r'\((?P<scope>[\w _\-]+)\): '
    r'(?P<subject>[^\n]+)'
    r'(?:\n\n'
    r'(?P<body>[^\n]+))?'
    r'(?:\n\n'
    r'(?P<footer>[^\n]+))?'
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
        raise UnknownCommitMessageStyle(
            'Unable to parse the given commit message: {}'.format(message)
        )

    parsed = re_parser.match(message)
    level_bump = 4
    if parsed.group('body') and 'BREAKING CHANGE' in parsed.group('body'):
        level_bump = 1

    if parsed.group('footer') and 'BREAKING CHANGE' in parsed.group('footer'):
        level_bump = 1

    if parsed.group('type') == 'feat':
        level_bump = min([level_bump, 2])

    if parsed.group('type') == 'fix':
        level_bump = min([level_bump, 2])

    return (
        level_bump,
        TYPES[parsed.group('type')],
        parsed.group('scope'),
        (parsed.group('subject'), parsed.group('body'), parsed.group('footer'))
    )
