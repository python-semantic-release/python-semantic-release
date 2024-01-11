from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Actor, Repo

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.util import copy_dir_tree, shortuid

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Literal, Mapping, Protocol

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import ExProjectDir

    CommitConvention = Literal["angular", "emoji", "scipy", "tag"]
    VersionStr = str
    CommitMsg = str

    class RepoInitFn(Protocol):
        def __call__(self, remote_url: str | None = None) -> Repo:
            ...

    class ExProjectGitRepoFn(Protocol):
        def __call__(self) -> Repo:
            ...

    class GetVersionStringsFn(Protocol):
        def __call__(self) -> list[VersionStr]:
            ...

    class GetRepoDefinitionFn(Protocol):
        def __call__(self, commit_type: CommitConvention = "angular") -> Mapping[VersionStr, list[CommitMsg]]:
            ...

    class BuildRepoFn(Protocol):
        def __call__(
                self,
                git_repo_path: Path | str,
                commit_type: CommitConvention,
                tag_format_str: str | None = None,
            ) -> None:
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
    return f"git@example.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def example_git_https_url():
    return f"https://example.com/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}"


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

    Use the `git_repo_factory` fixture instead. This creates a default
    base repository, all settings can be changed later through the git
    repo factory fixture.
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
def git_repo_factory(
    cached_example_git_project: Path,
    example_project_dir: ExProjectDir,
) -> Generator[RepoInitFn, None, None]:
    repos: list[Repo] = []

    def git_repo(remote_url: str | None = None) -> Repo:
        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find cached git project files!")

        # Copy the cached git project to the current test's project dir
        copy_dir_tree(cached_example_git_project, example_project_dir)

        # Create Git Repo object for project
        repo = Repo(example_project_dir)

        # store the repo so we can close it later
        repos.append(repo)

        if remote_url is not None:
            # update the origin url if desired
            repo.remotes.origin.set_url(remote_url)

        return repo

    try:
        yield git_repo
    finally:
        for repo in repos:
            repo.close()


@pytest.fixture
def example_project_git_repo(example_project_dir: ExProjectDir) -> Generator[ExProjectGitRepoFn, None, None]:
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
