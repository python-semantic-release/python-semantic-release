import re

import semver
from invoke import run

from .settings import config
from .vcs_helpers import get_commit_log

LEVELS = {
    1: 'patch',
    2: 'minor',
    3: 'major',
}


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

    for commit_message in get_commit_log():
        if current_version in commit_message:
            break
        if config.get('semantic_release', 'major_tag') in commit_message:
            changes.append(3)
        elif config.get('semantic_release', 'minor_tag') in commit_message:
            changes.append(2)
        elif config.get('semantic_release', 'patch_tag') in commit_message:
            changes.append(1)
        commit_count += 1

    if len(changes):
        bump = LEVELS[max(changes)]
    if config.getboolean('semantic_release', 'patch_without_tag') and commit_count:
        bump = 'patch'
    return bump


def get_current_version():
    """
    Finds the current version of the package in the current working directory.

    :return: A string with the version number.
    """
    return run('python setup.py --version', hide=True).stdout.strip()


def get_new_version(current_version, level_bump):
    """
    Calculates the next version based on the given bump level with semver.

    :param current_version: The version the package has now.
    :param level_bump: The level of the version number that should be bumped. Should be a `'major'`,
                       `'minor'` or `'patch'`.
    :return: A string with the next version number.
    """
    if not level_bump:
        return current_version
    return getattr(semver, 'bump_{0}'.format(level_bump))(current_version)


def set_new_version(new_version):
    """
    Replaces the version number in the correct place and writes the changed file to disk.

    :param new_version: The new version number as a string.
    :return: `True` if it succeeded.
    """
    filename, variable = config.get('semantic_release', 'version_variable').split(':')
    variable = variable.strip()
    with open(filename, mode='r') as fr:
        content = fr.read()

    content = re.sub(
        r'{} ?= ?["\']\d+\.\d+(?:\.\d+)?["\']'.format(variable),
        '{} = \'{}\''.format(variable, new_version),
        content
    )

    with open(filename, mode='w') as fw:
        fw.write(content)
    return True
