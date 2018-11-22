"""VCS Helpers
"""
import re
from typing import Optional, Tuple

from git import GitCommandError, NoSuchPathError, Repo, TagObject

from .errors import GitError, HvcsRepoParseError
from .settings import config

try:
    REPO = Repo('.git', search_parent_directories=True)
except NoSuchPathError:
    REPO = None


def get_commit_log(from_rev=None):
    """
    Yields all commit messages from last to first.
    """

    rev = None
    if from_rev:
        rev = '...{from_rev}'.format(from_rev=from_rev)
    for commit in REPO.iter_commits(rev):
        yield (commit.hexsha, commit.message)


def get_last_version(skip_tags=None) -> Optional[str]:
    """
    return last version from repo tags

    :return: a string contains version number
    """
    skip_tags = skip_tags or []

    def version_finder(x):
        if isinstance(x.commit, TagObject):
            return x.tag.tagged_date
        return x.commit.committed_date

    for i in sorted(REPO.tags, reverse=True, key=version_finder):
        if re.match(r'v\d+\.\d+\.\d+', i.name):
            if i.name in skip_tags:
                continue
            return i.name[1:]
    return None


def get_version_from_tag(tag_name: str) -> Optional[str]:
    """Get version from tag

    :param tag_name: Name of the git tag (i.e. 'v1.0.0')
    :return: sha1 hash of the commit
    """
    for i in REPO.tags:
        if i.name == tag_name:
            return i.commit.hexsha
    return None


def get_repository_owner_and_name() -> Tuple[str, str]:
    """
    Checks the origin remote to get the owner and name of the remote repository.

    :return: a tuple of the owner and name
    :raises HvcsRepoParseError: if no regex matches are found in the repo url
    """

    url = REPO.remote('origin').url
    parts = re.search(r'([^/:]+)/([^/]+).git$', url)
    if not parts:
        raise HvcsRepoParseError
    return parts.group(1), parts.group(2)


def get_current_head_hash() -> str:
    """
    Gets the commit hash of the current HEAD.

    :return: a string with the commit hash.
    """

    return REPO.head.commit.name_rev.split(' ')[0]


def commit_new_version(version: str):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message
    """

    commit_message = config.get('semantic_release', 'commit_message')
    message = '{0}\n\n{1}'.format(version, commit_message)
    REPO.git.add(config.get('semantic_release', 'version_variable').split(':')[0])
    return REPO.git.commit(m=message, author="semantic-release <semantic-release>")


def tag_new_version(version: str):
    """
    Creates a new tag with the version number prefixed with v.

    :param version: The version number used in the tag as a string.
    """

    return REPO.git.tag('-a', 'v{0}'.format(version), m='v{0}'.format(version))


def push_new_version(gh_token: str = None, owner: str = None, name: str = None):
    """
    Runs git push and git push --tags
    :param gh_token: Github token used to push.
    :param owner: Organisation or user that owns the repository.
    :param name: Name of repository.
    :raises GitError: if GitCommandError is raised
    """

    server = 'origin'
    if gh_token:
        server = 'https://{token}@{repo}'.format(
            token=gh_token,
            repo='github.com/{owner}/{name}.git'.format(owner=owner, name=name)
        )

    try:
        REPO.git.push(server, 'master')
        REPO.git.push('--tags', server, 'master')
    except GitCommandError as error:
        message = str(error)
        if gh_token:
            message = message.replace(gh_token, '[GH_TOKEN]')
        raise GitError(message)


def checkout(branch: str):
    """
    Checkout the given branch in the local repository.

    :param branch: The branch to checkout.
    """

    return REPO.git.checkout(branch)
