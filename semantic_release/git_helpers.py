from git import Repo
from invoke import run

from semantic_release.settings import config


def get_commit_log():
    """
    Yields all commit messages from last to first.
    """
    repo = Repo('.git')
    for commit in repo.iter_commits():
        yield commit.message


def commit_new_version(version):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message
    """
    command = 'git add {}'.format(config.get('semantic_release', 'version_variable').split(':')[0])
    add = run(command, hide=True)
    if add.ok:
        run('git commit -m "{}"'.format(version), hide=True)


def tag_new_version(version):
    """
    Creates a new tag with the version number prefixed with v.

    :param version: The version number used in the tag as a string.
    """
    return run('git tag v{} HEAD'.format(version), hide=True)


def push_new_version():
    """
    Runs git push and git push --tags
    """
    return run('git push && git push --tags', hide=True)
