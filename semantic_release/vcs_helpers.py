"""VCS Helpers
"""
import os
import re
from pathlib import PurePath
from typing import Optional, Tuple
from urllib.parse import urlsplit

import ndebug
from git import GitCommandError, InvalidGitRepositoryError, Repo, TagObject
from git.exc import BadName

from .errors import GitError, HvcsRepoParseError
from .settings import config

try:
    repo = Repo('.', search_parent_directories=True)
except InvalidGitRepositoryError:
    repo = None

debug = ndebug.create(__name__)


def check_repo():
    if not repo:
        raise GitError("Not in a valid git repository")


def get_commit_log(from_rev=None):
    """
    Yields all commit messages from last to first.
    """

    check_repo()
    rev = None
    if from_rev:
        try:
            repo.commit(from_rev)
            rev = '...{from_rev}'.format(from_rev=from_rev)
        except BadName:
            debug('Reference {} does not exist, considering all log'.format(from_rev))
    for commit in repo.iter_commits(rev):
        yield (commit.hexsha, commit.message)


def get_last_version(skip_tags=None) -> Optional[str]:
    """
    Return last version from repo tags.

    :return: A string contains version number.
    """

    debug('get_last_version skip_tags=', skip_tags)
    check_repo()
    skip_tags = skip_tags or []

    def version_finder(tag):
        if isinstance(tag.commit, TagObject):
            return tag.tag.tagged_date
        return tag.commit.committed_date

    for i in sorted(repo.tags, reverse=True, key=version_finder):
        if re.match(r'v\d+\.\d+\.\d+', i.name):
            if i.name in skip_tags:
                continue
            return i.name[1:]
    return None


def get_version_from_tag(tag_name: str) -> Optional[str]:
    """Get git hash from tag

    :param tag_name: Name of the git tag (i.e. 'v1.0.0')
    :return: sha1 hash of the commit
    """

    debug('get_version_from_tag({})'.format(tag_name))
    check_repo()
    for i in repo.tags:
        if i.name == tag_name:
            return i.commit.hexsha
    return None


def get_repository_owner_and_name() -> Tuple[str, str]:
    """
    Checks the origin remote to get the owner and name of the remote repository.

    :return: A tuple of the owner and name.
    """

    check_repo()
    url = repo.remote('origin').url
    split_url = urlsplit(url)
    path = split_url.netloc + split_url.path
    parts = re.search(r'[:/]([^:]+)/([^/]*?)(.git)?$', path)
    if not parts:
        raise HvcsRepoParseError
    debug('get_repository_owner_and_name', parts)
    return parts.group(1), parts.group(2)


def get_current_head_hash() -> str:
    """
    Gets the commit hash of the current HEAD.

    :return: A string with the commit hash.
    """

    check_repo()
    return repo.head.commit.name_rev.split(' ')[0]


def commit_new_version(version: str):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message.
    """

    check_repo()
    commit_message = config.get('semantic_release', 'commit_message')
    message = '{0}\n\n{1}'.format(version, commit_message)

    version_file = config.get('semantic_release', 'version_variable').split(':')[0]
    # get actual path to filename, to allow running cmd from subdir of git root
    version_filepath = PurePath(os.getcwd(), version_file).relative_to(repo.working_dir)

    repo.git.add(str(version_filepath))
    return repo.git.commit(m=message, author="semantic-release <semantic-release>")


def tag_new_version(version: str):
    """
    Creates a new tag with the version number prefixed with v.

    :param version: The version number used in the tag as a string.
    """

    check_repo()
    return repo.git.tag('-a', 'v{0}'.format(version), m='v{0}'.format(version))


def push_new_version(
    auth_token: str = None,
    owner: str = None,
    name: str = None,
    branch: str = 'master',
    domain: str = 'github.com',
):
    """
    Runs git push and git push --tags.

    :param auth_token: Authentication token used to push.
    :param owner: Organisation or user that owns the repository.
    :param name: Name of repository.
    :param branch: Branch to push to
    :param server_url: Name of the server. Will be used to identify a gitlab instance.
    :raises GitError: if GitCommandError is raised
    """

    check_repo()
    server = 'origin'
    if auth_token:
        token = auth_token
        if config.get('semantic_release', 'hvcs') == 'gitlab':
            token = 'gitlab-ci-token:' + token
        actor = os.environ.get('GITHUB_ACTOR')
        if actor:
            server = 'https://{actor}:{token}@{server_url}/{owner}/{name}.git'.format(
                token=token,
                server_url=domain,
                owner=owner,
                name=name,
                actor=actor
            )
        else:
            server = 'https://{token}@{server_url}/{owner}/{name}.git'.format(
                token=token,
                server_url=domain,
                owner=owner,
                name=name,
            )

    try:
        repo.git.push(server, branch)
        repo.git.push('--tags', server, branch)
    except GitCommandError as error:
        message = str(error)
        if auth_token:
            message = message.replace(auth_token, '[AUTH_TOKEN]')
        raise GitError(message)


def checkout(branch: str):
    """
    Checks out the given branch in the local repository.

    :param branch: The branch to checkout.
    """

    check_repo()
    return repo.git.checkout(branch)
