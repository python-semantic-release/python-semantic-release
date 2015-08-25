import re

from ..errors import UnknownCommitMessageStyleError
from ..settings import config
from .parser_helpers import parse_text_block

re_parser = re.compile(
    r'(?P<subject>[^\n]+)'
    r'(:?\n\n(?P<text>.+))?',
    re.DOTALL
)


def parse_commit_message(message):
    """
    Parses a commit message according to the 1.0 version of python-semantic-release. It expects
    a tag of some sort in the commit message and will use the rest of the first line as changelog
    content.

    :param message: A string of a commit message.
    :raises semantic_release.UnknownCommitMessageStyle: If it does not recognise the commit style
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    """

    match = re_parser.match(message)

    if not match:
        raise UnknownCommitMessageStyleError(
            'Unable to parse the given commit message: {0}'.format(message)
        )

    if config.get('semantic_release', 'minor_tag') in message:
        level = 'feature'

    elif config.get('semantic_release', 'fix_tag') in message:
        level = 'fix'
    else:
        raise UnknownCommitMessageStyleError(
            'Unable to parse the given commit message: {0}'.format(message)
        )

    subject = match.group('subject')
    if subject:
        subject = subject.replace(config.get('semantic_release', '{0}_tag'.format(level)), '')

    body, footer = parse_text_block(match.group('text'))

    return level, level, None, (subject.strip(), body.strip(), footer.strip())
