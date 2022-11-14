"""VCS Helpers
"""
import logging
import os
import re
from datetime import date
from pathlib import Path, PurePath
from typing import List, Optional, Tuple
from urllib.parse import urlsplit

from git import GitCommandError, InvalidGitRepositoryError, Repo
from git.exc import BadName
from git.objects import TagObject

from .errors import GitError, HvcsRepoParseError
from .helpers import LoggedFunction
from .settings import config

_repo: Optional[Repo]
try:
    _repo = Repo(".", search_parent_directories=True)
except InvalidGitRepositoryError:
    _repo = None

logger = logging.getLogger(__name__)


def repo():
    if _repo is None:
        raise GitError("Not in a valid git repository")
    return _repo


def get_formatted_tag(version):
    """Get the version, formatted with `tag_format` config option"""
    tag_format = config.get("tag_format")
    return tag_format.format(version=version)


def get_formatted_commit(version: str) -> str:
    commit_subject = config.get("commit_subject")
    message = commit_subject.format(version=version)

    # Add an extended message if one is configured
    commit_message = config.get("commit_message")
    if commit_message:
        message += "\n\n"
        message += commit_message.format(version=version)

    return message


def get_commit_log(from_rev=None, to_rev=None):
    """Yield all commit messages from last to first."""
    if from_rev:
        from_rev = get_formatted_tag(from_rev)
        try:
            repo().commit(from_rev)
        except BadName:
            logger.debug(
                f"Reference {from_rev} does not exist, considering entire history"
            )
            from_rev = None
    if to_rev:
        to_rev = get_formatted_tag(to_rev)
        try:
            repo().commit(to_rev)
        except BadName:
            logger.debug(
                f"Reference {to_rev} does not exist, considering entire history until HEAD"
            )
            to_rev = None

    rev = None
    if from_rev and to_rev:
        rev = f"{to_rev}...{from_rev}"
    elif from_rev:
        rev = f"...{from_rev}"
    elif to_rev:
        rev = f"{to_rev}..."

    for commit in repo().iter_commits(rev):
        yield (commit.hexsha, commit.message.replace("\r\n", "\n"))


@LoggedFunction(logger)
def get_last_version(pattern, skip_tags=None) -> Optional[str]:
    """
    Find the latest version using repo tags.

    :return: A string containing a version number.
    """
    skip_tags = skip_tags or []

    def version_finder(tag):
        if isinstance(tag.commit, TagObject):
            return tag.tag.tagged_date
        return tag.commit.committed_date

    for i in sorted(repo().tags, reverse=True, key=version_finder):
        if i.name in skip_tags:
            continue

        match = re.search(pattern, i.name)
        if match:
            return match.group(1).strip()

    return None


@LoggedFunction(logger)
def get_repository_owner_and_name() -> Tuple[str, str]:
    """
    Check the 'origin' remote to get the owner and name of the remote repository.

    :return: A tuple of the owner and name.
    """
    # Gitlab-CI context
    if "CI_PROJECT_NAMESPACE" in os.environ and "CI_PROJECT_NAME" in os.environ:
        return os.environ["CI_PROJECT_NAMESPACE"], os.environ["CI_PROJECT_NAME"]

    # Github actions context
    if "GITHUB_REPOSITORY" in os.environ:
        owner, name = os.environ["GITHUB_REPOSITORY"].rsplit("/", 1)
        return owner, name

    # Local context
    url = repo().remote("origin").url
    split_url = urlsplit(url)
    # Select the owner and name as regex groups
    parts = re.search(r"[:/]([^:]+)/([^/]*?)(.git)?$", split_url.path)
    if not parts:
        raise HvcsRepoParseError

    return parts.group(1), parts.group(2)


def get_current_head_hash() -> str:
    """
    Get the commit hash of the current HEAD.

    :return: The commit hash.
    """
    return repo().head.commit.name_rev.split(" ")[0]


@LoggedFunction(logger)
def commit_new_version(version: str):
    """
    Commit the file containing the version number variable.

    The commit message will be generated from the configured template.

    :param version: Version number to be used in the commit message.
    """
    from .history import load_version_declarations

    commit_message = get_formatted_commit(version)
    commit_author = config.get(
        "commit_author",
        "semantic-release <semantic-release>",
    )

    for declaration in load_version_declarations():
        git_path: PurePath = PurePath(os.getcwd(), declaration.path).relative_to(repo().working_dir)  # type: ignore
        repo().git.add(str(git_path))

    return repo().git.commit(m=commit_message, author=commit_author)


@LoggedFunction(logger)
def update_changelog_file(version: str, content_to_add: str):
    """
    Update changelog file with changelog for the release.

    :param version: The release version number, as a string.
    :param content_to_add: The release notes for the version.
    """
    changelog_file = config.get("changelog_file")
    changelog_placeholder = config.get("changelog_placeholder")
    git_path = Path(os.getcwd(), changelog_file)
    if not git_path.exists() or git_path.read_text().strip() == "":
        original_content = f"# Changelog\n\n{changelog_placeholder}\n"
        logger.warning(f"Changelog file not found: {git_path} - creating it.")
    else:
        original_content = git_path.read_text()
    if (
        changelog_placeholder not in original_content
        and "# Changelog" in original_content
    ):
        original_content = original_content.replace(
            "# Changelog", f"# Changelog\n\n{changelog_placeholder}\n"
        )

    if changelog_placeholder not in original_content:
        logger.warning(
            f"Placeholder '{changelog_placeholder}' not found "
            f"in changelog file {git_path} - skipping change."
        )
        return

    updated_content = original_content.replace(
        changelog_placeholder,
        "\n".join(
            [
                changelog_placeholder,
                "",
                f"## v{version} ({date.today():%Y-%m-%d})",
                content_to_add,
            ]
        ),
    )
    git_path.write_text(updated_content)
    repo().git.add(str(git_path.relative_to(str(repo().working_dir))))


def get_changed_files(repo: Repo) -> List[str]:
    """
    Get untracked / dirty files in the given git repo().

    :param repo: Git repo to check.
    :return: A list of filenames.
    """
    untracked_files = repo.untracked_files
    dirty_files = [item.a_path for item in repo.index.diff(None)]
    return [*untracked_files, *dirty_files]


@LoggedFunction(logger)
def update_additional_files():
    """
    Add specified files to VCS, if they've changed.
    """
    changed_files = get_changed_files(repo())

    include_additional_files = config.get("include_additional_files")
    if include_additional_files:
        for filename in include_additional_files.split(","):
            if filename in changed_files:
                logger.debug(f"Updated file: {filename}")
                repo().git.add(filename)
            else:
                logger.warning(f"File {filename} shows no changes, cannot update it.")


@LoggedFunction(logger)
def tag_new_version(version: str):
    """
    Create a new tag with the version number, prefixed with v by default.

    :param version: The version number used in the tag as a string.
    """
    tag = get_formatted_tag(version)
    return repo().git.tag("-a", tag, m=tag)


@LoggedFunction(logger)
def push_new_version(
    auth_token: Optional[str] = None,
    owner: Optional[str] = None,
    name: Optional[str] = None,
    branch: str = "master",
    domain: str = "github.com",
):
    """
    Run git push and git push --tags.

    :param auth_token: Authentication token used to push.
    :param owner: Organisation or user that owns the repository.
    :param name: Name of repository.
    :param branch: Branch to push to
    :param server_url: Name of the server. Will be used to identify a gitlab instance.
    :raises GitError: if GitCommandError is raised
    """
    server = "origin"
    if auth_token:
        if not config.get("ignore_token_for_push"):
            token = auth_token
            if config.get("hvcs") == "gitlab":
                token = "gitlab-ci-token:" + token
            actor = os.environ.get("GITHUB_ACTOR")
            if actor:
                server = f"https://{actor}:{token}@{domain}/{owner}/{name}.git"
            else:
                server = f"https://{token}@{domain}/{owner}/{name}.git"
        else:
            logger.debug("Ignoring token for pushing to the repository.")

    try:
        repo().git.push(server, branch)
        repo().git.push("--tags", server, branch)
    except GitCommandError as error:
        message = str(error)
        if auth_token:
            message = message.replace(auth_token, "[AUTH_TOKEN]")
        raise GitError(message)


@LoggedFunction(logger)
def checkout(branch: str):
    """
    Check out the given branch in the local repository.

    :param branch: The branch to checkout.
    """
    return repo().git.checkout(branch)
