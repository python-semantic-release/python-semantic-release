from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Actor, Repo

from tests.const import COMMIT_MESSAGE, EXAMPLE_HVCS_DOMAIN, EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.util import add_text_to_file, copy_dir_tree, shortuid

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Literal, Mapping, Protocol

    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn

    CommitConvention = Literal["angular", "emoji", "scipy", "tag"]
    VersionStr = str
    CommitMsg = str

    class BuildRepoFn(Protocol):
        def __call__(
            self,
            git_repo_path: Path | str,
            commit_type: CommitConvention,
            tag_format_str: str | None = None,
        ) -> None:
            ...

    class CommitNReturnChangelogEntryFn(Protocol):
        def __call__(
            self, git_repo: Repo, commit_msg: str, hvcs: HvcsBase
        ) -> str:
            ...

    class SimulateChangeCommitsNReturnChangelogEntryFn(Protocol):
        def __call__(
            self, git_repo: Repo, commit_msgs: list[CommitMsg], hvcs: HvcsBase
        ) -> list[CommitMsg]:
            ...

    class CreateReleaseFn(Protocol):
        def __call__(self, git_repo: Repo, version: str, tag_format: str = ...) -> None:
            ...

    class ExProjectGitRepoFn(Protocol):
        def __call__(self) -> Repo:
            ...

    class GetVersionStringsFn(Protocol):
        def __call__(self) -> list[VersionStr]:
            ...

    class GetRepoDefinitionFn(Protocol):
        def __call__(
            self, commit_type: CommitConvention = "angular"
        ) -> Mapping[VersionStr, list[CommitMsg]]:
            ...


@pytest.fixture(scope="session")
def commit_author():
    return Actor(name="semantic release testing", email="not_a_real@email.com")


@pytest.fixture(scope="session")
def default_tag_format_str() -> str:
    return "v{version}"


@pytest.fixture(scope="session")
def file_in_repo():
    return f"file-{shortuid()}.txt"


@pytest.fixture(scope="session")
def example_git_ssh_url():
    return f"git@{EXAMPLE_HVCS_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def example_git_https_url():
    return f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def create_release_tagged_commit(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> CreateReleaseFn:
    def _mimic_semantic_release_commit(
        git_repo: Repo,
        version: str,
        tag_format: str = default_tag_format_str,
    ) -> None:
        # stamp version into pyproject.toml
        update_pyproject_toml("tool.poetry.version", version)

        # commit --all files with version number commit message
        git_repo.git.commit(a=True, m=COMMIT_MESSAGE.format(version=version))

        # tag commit with version number
        tag_str = tag_format.format(version=version)
        git_repo.git.tag(tag_str, m=tag_str)

    return _mimic_semantic_release_commit


@pytest.fixture(scope="session")
def commit_n_rtn_changelog_entry() -> CommitNReturnChangelogEntryFn:
    def _commit_n_rtn_changelog_entry(
        git_repo: Repo, commit_msg: str, hvcs: HvcsBase
    ) -> str:
        # make commit with --all files
        git_repo.git.commit(a=True, m=commit_msg)

        # log commit in changelog format after commit action
        commit_sha = git_repo.head.commit.hexsha
        return str.join(" ", [
            str(git_repo.head.commit.message).strip(),
            f"([`{commit_sha[:7]}`]({hvcs.commit_hash_url(commit_sha)}))"
        ])

    return _commit_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def simulate_change_commits_n_rtn_changelog_entry(
    commit_n_rtn_changelog_entry: CommitNReturnChangelogEntryFn,
    file_in_repo: str,
) -> SimulateChangeCommitsNReturnChangelogEntryFn:
    def _simulate_change_commits_n_rtn_changelog_entry(
        git_repo: Repo, commit_msgs: list[str], hvcs: HvcsBase
    ) -> list[str]:
        changelog_entries = []
        for commit_msg in commit_msgs:
            add_text_to_file(git_repo, file_in_repo)
            changelog_entries.append(
                commit_n_rtn_changelog_entry(git_repo, commit_msg, hvcs)
            )
        return changelog_entries

    return _simulate_change_commits_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def cached_example_git_project(
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
    cached_example_project: Path,
    example_git_https_url: str,
    commit_author: Actor,
) -> Path:
    """
    Initializes an example project with git repo. DO NOT USE DIRECTLY.

    Use a `repo_*` fixture instead. This creates a default
    base repository, all settings can be changed later through from the
    example_project_git_repo fixture's return object and manual adjustment.
    """
    if not cached_example_project.exists():
        raise RuntimeError("Unable to find cached project files")

    cached_git_proj_path = (cached_files_dir / "example_git_project").resolve()

    # make a copy of the example project as a base
    copy_dir_tree(cached_example_project, cached_git_proj_path)

    # initialize git repo (open and close)
    # NOTE: We don't want to hold the repo object open for the entire test session,
    # the implementation on Windows holds some file descriptors open until close is called.
    with Repo.init(cached_git_proj_path) as repo:
        # Without this the global config may set it to "master", we want consistency
        repo.git.branch("-M", "main")
        with repo.config_writer("repository") as config:
            config.set_value("user", "name", commit_author.name)
            config.set_value("user", "email", commit_author.email)
            config.set_value("commit", "gpgsign", False)

        repo.create_remote(name="origin", url=example_git_https_url)

        # make sure all base files are in index to enable initial commit
        repo.index.add(("*", ".gitignore"))

        # TODO: initial commit!

    # trigger automatic cleanup of cache directory during teardown
    return teardown_cached_dir(cached_git_proj_path)


@pytest.fixture
def example_project_git_repo(
    example_project_dir: ExProjectDir,
) -> Generator[ExProjectGitRepoFn, None, None]:
    repos: list[Repo] = []

    # Must be a callable function to ensure files exist before repo is opened
    def _example_project_git_repo() -> Repo:
        if not example_project_dir.exists():
            raise RuntimeError("Unable to find example git project!")

        repo = Repo(example_project_dir)
        repos.append(repo)
        return repo

    try:
        yield _example_project_git_repo
    finally:
        for repo in repos:
            repo.close()
