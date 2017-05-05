import re

from git import GitCommandError, Repo

from .errors import GitError
from .settings import config

repo = Repo('.git', search_parent_directories=True)


def get_commit_log(from_rev=None):
    """
    Yields all commit messages from last to first.
    """
    rev = None
    if from_rev:
        rev = '...{from_rev}'.format(from_rev=from_rev)
    for commit in repo.iter_commits(rev):
        yield (commit.hexsha, commit.message)


def get_last_version():
    """
    return last version from repo tags

    :return: a string contains version number
    """
    for i in sorted(repo.tags, key=lambda x: x.commit.committed_date, reverse=True):
        if re.match('v\d+\.\d+\.\d+', i.name):
            return i.name[1:]


def get_version_from_tag(tag_name):
    for i in repo.tags:
        if i.name == tag_name:
            return i.commit.hexsha


def get_repository_owner_and_name():
    """
    Checks the origin remote to get the owner and name of the remote repository.

    :return: a tuple of the owner and name
    """
    url = repo.remote('origin').url
    parts = re.search(r'([^/:]+)/([^/]+).git$', url)

    return parts.group(1), parts.group(2)


def get_current_head_hash():
    """
    Gets the commit hash of the current HEAD.

    :return: a string with the commit hash.
    """
    return repo.head.commit.name_rev.split(' ')[0]


def commit_new_version(version):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message
    """
    repo.git.add(
        config.get('semantic_release', 'version_variable').split(':')[0])
    return repo.git.commit(m=version, author="semantic-release <semantic-release>")


def tag_new_version(version):
    """
    Creates a new tag with the version number prefixed with v.

    :param version: The version number used in the tag as a string.
    """
    return repo.git.tag('-a', 'v{0}'.format(version), m='v{0}'.format(version))


def push_new_version(gh_token=None, owner=None, name=None):
    """
    Runs git push and git push --tags
    :param gh_token: Github token used to push.
    :param owner: Organisation or user that owns the repository.
    :param name: Name of repository.
    """
    server = 'origin'
    if gh_token:
        server = 'https://{token}@{repo}'.format(
            token=gh_token,
            repo='github.com/{owner}/{name}.git'.format(owner=owner, name=name)
        )

    try:
        repo.git.push(server, 'master')
        repo.git.push('--tags', server, 'master')
    except GitCommandError as error:
        message = str(error)
        if gh_token:
            message = message.replace(gh_token, '[GH_TOKEN]')
        raise GitError(message)


def checkout(branch):
    """
    Checkout the given branch in the local repository.

    :param branch: The branch to checkout.
    """
    return repo.git.checkout(branch)
