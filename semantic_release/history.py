from semantic_release.git_helpers import get_commit_log
from semantic_release.helpers import load_config

LEVELS = {
    1: 'patch',
    2: 'minor',
    3: 'major',
}


def evaluate_version_bump(current_version, force=None):
    if force:
        return force
    bump = None

    changes = []

    for commit_message in get_commit_log():
        if current_version in commit_message:
            break
        if load_config()['major_tag'] in commit_message:
            changes.append(3)
        elif load_config()['minor_tag'] in commit_message:
            changes.append(2)
        elif load_config()['patch_tag'] in commit_message:
            changes.append(1)

    if len(changes):
        bump = LEVELS[max(changes)]
    return bump
