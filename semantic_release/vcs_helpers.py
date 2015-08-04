import re

from git import Repo
from invoke import run

from .settings import config


def get_commit_log():
    """
    Yields all commit messages from last to first.
    """
    repo = Repo('.git')
    for commit in repo.iter_commits():
        yield commit.message


def get_repository_owner_and_name():
    """
    Checks the origin remote to get the owner and name of the remote repository.

    :return: a tuple of the owner and name
    """
    url = Repo('.git').remote('origin').url
    parts = re.search(r'([^/:]+)/([^/]+).git$', url)

    return parts.group(1), parts.group(2)


def get_current_head_hash():
    """
    Gets the commit hash of the current HEAD.

    :return: a string with the commit hash.
    """
    return Repo('.git').head.commit.name_rev.split(' ')[0]


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
