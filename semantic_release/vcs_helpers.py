import re

from git import Repo
from invoke import run, Failure

from .errors import GitError
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


def push_new_version(gh_token=None, owner=None, name=None):
    """
    Runs git push and git push --tags
    """
    command = 'git push --follow-tags origin $(git rev-parse --abbrev-ref HEAD)'
    if gh_token:
        command = 'git push --follow-tags "https://{token}@{repo}" {branch}'.format(
            branch='$(git rev-parse --abbrev-ref HEAD)',
            token=gh_token,
            repo='github.com/{owner}/{name}.git'.format(owner=owner, name=name)
        )
    try:
        return run(command, hide=True)
    except Failure as error:
        message = error.result
        if gh_token:
            message = message.replace(gh_token, '[GH_TOKEN]')
        raise GitError(message)
