import re

from semantic_release.errors import UnknownCommitMessageStyle

re_parser = re.compile(
    r'(?P<type>feat|fix|docs|style|refactor|test|chore)'
    r'\((?P<scope>[\w _\-]+)\): '
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
        raise UnknownCommitMessageStyle(
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

    text = parsed.group('text')
    body = ''
    footer = ''
    if text:
        body = text.split('\n\n')[0]
        if len(text.split('\n\n')) == 2:
            footer = text.split('\n\n')[1]

    return (
        level_bump,
        TYPES[parsed.group('type')],
        parsed.group('scope'),
        (parsed.group('subject'), body.replace('\n', ' '), footer.replace('\n', ' '))
    )
