"""Logs
"""
from typing import Optional

import ndebug

from ..errors import UnknownCommitMessageStyleError
from ..settings import config, current_commit_parser
from ..vcs_helpers import get_commit_log
from .parser_helpers import re_breaking

debug = ndebug.create(__name__)

LEVELS = {
    1: 'patch',
    2: 'minor',
    3: 'major',
}

# Sections which will be shown in the Markdown changelog.
# This is NOT related to supported commit types.
CHANGELOG_SECTIONS = [
    'feature',
    'fix',
    'breaking',
    'documentation',
    'performance',
]


def evaluate_version_bump(current_version: str, force: str = None) -> Optional[str]:
    """
    Read git log since the last release to decide if we should make a major, minor or patch release.

    :param current_version: A string with the current version number.
    :param force: A string with the bump level that should be forced.
    :return: A string with either major, minor or patch if there should be a release.
             If no release is necessary, None will be returned.
    """
    debug('evaluate_version_bump("{}", "{}")'.format(current_version, force))
    if force:
        return force

    bump = None

    changes = []
    commit_count = 0

    for _hash, commit_message in get_commit_log('v{0}'.format(current_version)):
        if commit_message.startswith(current_version):
            # Stop once we reach the current version
            # (we are looping in the order of newest -> oldest)
            debug('"{}" is commit for {}. breaking loop'.format(commit_message, current_version))
            break

        commit_count += 1

        # Attempt to parse this commit using the currently-configured parser
        try:
            message = current_commit_parser()(commit_message)
            # Add the bump level that this commit requires
            changes.append(message[0])
        except UnknownCommitMessageStyleError as err:
            debug('ignored commit', err)
            pass

    debug(f'commit_count={commit_count}')

    if changes:
        # Select the largest required bump level from the commits we parsed
        level = max(changes)
        if level in LEVELS:
            bump = LEVELS[level]
            debug(f'Evaluated {bump}({level}) from {changes}')
        else:
            debug(f'Unknown level {level}')

    if (
        config.getboolean('semantic_release', 'patch_without_tag') and
        commit_count > 0 and
        bump is None
    ):
        bump = 'patch'
        debug(f'Changing bump to patch based on config patch_without_tag')

    debug(f'evaluate_version_bump returned {bump}')
    return bump


def generate_changelog(from_version: str, to_version: str = None) -> dict:
    """
    Parse a changelog dictionary for the given version.

    :param from_version: The version before where the changelog starts.
                         The changelog will be generated from the commit after this one.
    :param to_version: The last version included in the changelog.
    :return: A dict with changelog sections and commits
    """
    debug('generate_changelog("{}", "{}")'.format(from_version, to_version))
    changes: dict = {
        'feature': [],
        'fix': [],
        'documentation': [],
        'refactor': [],
        'breaking': [],
        'performance': [],
    }

    rev = None
    if from_version:
        rev = 'v{0}'.format(from_version)

    found_the_release = to_version is None
    for _hash, commit_message in get_commit_log(rev):
        if not found_the_release:
            # Skip until we find the last commit in this release
            # (we are looping in the order of newest -> oldest)
            if to_version and to_version not in commit_message:
                continue
            else:
                found_the_release = True

        if from_version is not None and from_version in commit_message:
            # We reached the previous release
            break

        try:
            message = current_commit_parser()(commit_message)
            if message[1] not in changes:
                continue

            changes[message[1]].append((_hash, message[3][0].capitalize()))

            # Handle breaking change message
            parts = None
            if message[0] == 3:
                # parse footer (standard)
                if message[3][2] and 'BREAKING CHANGE' in message[3][2]:
                    parts = re_breaking.match(message[3][2])
                # parse body (not standard, kept for backwards compatibility)
                elif message[3][1] and 'BREAKING CHANGE' in message[3][1]:
                    parts = re_breaking.match(message[3][1])

                if parts:
                    breaking_description = parts.group(1)
                else:
                    breaking_description = message[3][0]

                changes['breaking'].append((_hash, breaking_description))

        except UnknownCommitMessageStyleError as err:
            debug('Ignoring', err)
            pass

    return changes


def markdown_changelog(version: str, changelog: dict, header: bool = False) -> str:
    """
    Generate a markdown version of the changelog.

    :param version: A string with the version number.
    :param changelog: A parsed changelog dict from generate_changelog.
    :param header: A boolean that decides whether a version number header should be included.
    :return: The markdown formatted changelog.
    """
    debug('markdown_changelog(version="{}", header={}, changelog=...)'.format(version, header))
    output = ''
    if header:
        # Add a heading with the version number
        output += '## v{0}\n'.format(version)

    for section in CHANGELOG_SECTIONS:
        if not changelog[section]:
            # This section does not have any commits
            continue

        # Add a header for the section
        output += '\n### {0}\n'.format(section.capitalize())
        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            output += '* {0} ({1})\n'.format(item[1], item[0])

    return output
