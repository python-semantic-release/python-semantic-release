from semantic_release.git_helpers import get_commit_log
from semantic_release.helpers import config

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
