import re

from ..errors import UnknownCommitMessageStyleError
from ..settings import config, current_commit_parser
from ..vcs_helpers import get_commit_log

LEVELS = {
    1: 'patch',
    2: 'minor',
    3: 'major',
}

CHANGELOG_SECTIONS = ['feature', 'fix', 'breaking', 'documentation']

re_breaking = re.compile('BREAKING CHANGE: (.*)')


def evaluate_version_bump(current_version, force=None):
    """
    Reads git log since last release to find out if should be a major, minor or patch release.

    :param current_version: A string with the current version number.
    :param force: A string with the bump level that should be forced.
    :return: A string with either major, minor or patch if there should be a release. If no release
             is necessary None will be returned.
    """
    if force:
        return force

    bump = None

    changes = []
    commit_count = 0

    for _hash, commit_message in get_commit_log('v{0}'.format(current_version)):
        if (current_version in commit_message and
                config.get('semantic_release', 'version_source') == 'commit'):
            break
        try:
            message = current_commit_parser()(commit_message)
            changes.append(message[0])
        except UnknownCommitMessageStyleError:
            pass

        commit_count += 1

    if changes:
        level = max(changes)
        if level in LEVELS:
            bump = LEVELS[level]
    if config.getboolean('semantic_release', 'patch_without_tag') and commit_count:
        bump = 'patch'
    return bump


def generate_changelog(from_version, to_version=None):
    """
    Generates a changelog for the given version.

    :param from_version: The last version not in the changelog. The changelog
                         will be generated from the commit after this one.
    :param to_version: The last version in the changelog.
    :return: a dict with different changelog sections
    """

    changes = {'feature': [], 'fix': [],
               'documentation': [], 'refactor': [], 'breaking': []}

    found_the_release = to_version is None

    rev = None
    if from_version:
        rev = 'v{0}'.format(from_version)

    for _hash, commit_message in get_commit_log(rev):
        if not found_the_release:
            if to_version and to_version not in commit_message:
                continue
            else:
                found_the_release = True

        if from_version is not None and from_version in commit_message:
            break

        try:
            message = current_commit_parser()(commit_message)
            if message[1] not in changes:
                continue

            changes[message[1]].append((_hash, message[3][0]))

            if message[3][1] and 'BREAKING CHANGE' in message[3][1]:
                changes['breaking'].append(
                    re_breaking.match(message[3][1]).group(1))

            if message[3][2] and 'BREAKING CHANGE' in message[3][2]:
                changes['breaking'].append(
                    re_breaking.match(message[3][2]).group(1))

        except UnknownCommitMessageStyleError:
            pass

    return changes


def markdown_changelog(version, changelog, header=False):
    """
    Generates a markdown version of the changelog. Takes a parsed changelog dict from
    generate_changelog.

    :param version: A string with the version number.
    :param changelog: A dict from generate_changelog.
    :param header: A boolean that decides whether a header should be included or not.
    :return: The markdown formatted changelog.
    """
    output = ''
    if header:
        output += '## v{0}\n'.format(version)

    for section in CHANGELOG_SECTIONS:
        if not changelog[section]:
            continue

        output += '\n### {0}\n'.format(section.capitalize())
        for item in changelog[section]:
            output += '* {0} ({1})\n'.format(item[1], item[0])

    return output
