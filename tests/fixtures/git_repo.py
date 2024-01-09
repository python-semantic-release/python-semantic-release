from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Actor, Repo

from tests.const import COMMIT_MESSAGE, EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.util import add_text_to_file, copy_dir_tree, shortuid

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Protocol

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        UpdatePyprojectTomlFn,
        UseParserFn,
    )

    class RepoInitFn(Protocol):
        def __call__(self, remote_url: str | None = None) -> Repo:
            ...


@pytest.fixture(scope="session")
def commit_author():
    return Actor(name="semantic release testing", email="not_a_real@email.com")


@pytest.fixture
def file_in_repo():
    return f"file-{shortuid()}.txt"


@pytest.fixture
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
def repo_with_no_tags_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add much more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: more text")

    return git_repo


@pytest.fixture
def repo_with_no_tags_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add much more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: more text")

    return git_repo


@pytest.fixture
def repo_with_no_tags_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add much more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: more text")

    return git_repo


@pytest.fixture
def repo_with_no_tags_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add much more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: more text")

    return git_repo


@pytest.fixture
def repo_with_single_branch_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1"))
    git_repo.git.tag("v0.1.1", m="v0.1.1")

    assert git_repo.commit("v0.1.1").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1"))
    git_repo.git.tag("v0.1.1", m="v0.1.1")

    assert git_repo.commit("v0.1.1").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1"))
    git_repo.git.tag("v0.1.1", m="v0.1.1")

    assert git_repo.commit("v0.1.1").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1"))
    git_repo.git.tag("v0.1.1", m="v0.1.1")

    assert git_repo.commit("v0.1.1").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_and_prereleases_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_and_prereleases_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_and_prereleases_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_single_branch_and_prereleases_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha
    return git_repo


@pytest.fixture
def repo_with_main_and_feature_branches_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()
    update_pyproject_toml(
        "tool.semantic_release.branches.beta-testing",
        {"match": "beta.*", "prerelease": True, "prerelease_token": "beta"},
    )

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("beta_testing")
    git_repo.heads.beta_testing.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.3.0-beta.1"))
    git_repo.git.tag("v0.3.0-beta.1", m="v0.3.0-beta.1")

    assert git_repo.commit("v0.3.0-beta.1").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "beta_testing"
    return git_repo


@pytest.fixture
def repo_with_main_and_feature_branches_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("beta_testing")
    git_repo.heads.beta_testing.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.3.0-beta.1"))
    git_repo.git.tag("v0.3.0-beta.1", m="v0.3.0-beta.1")

    assert git_repo.commit("v0.3.0-beta.1").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "beta_testing"
    return git_repo


@pytest.fixture
def repo_with_main_and_feature_branches_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("beta_testing")
    git_repo.heads.beta_testing.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.3.0-beta.1"))
    git_repo.git.tag("v0.3.0-beta.1", m="v0.3.0-beta.1")

    assert git_repo.commit("v0.3.0-beta.1").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "beta_testing"
    return git_repo


@pytest.fixture
def repo_with_main_and_feature_branches_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0-rc.1"))
    git_repo.git.tag("v0.2.0-rc.1", m="v0.2.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.0"))
    git_repo.git.tag("v0.2.0", m="v0.2.0")

    assert git_repo.commit("v0.2.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("beta_testing")
    git_repo.heads.beta_testing.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.3.0-beta.1"))
    git_repo.git.tag("v0.3.0-beta.1", m="v0.3.0-beta.1")

    assert git_repo.commit("v0.3.0-beta.1").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "beta_testing"
    return git_repo


@pytest.fixture
def repo_with_git_flow_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()
    update_pyproject_toml(
        "tool.semantic_release.branches.features",
        {"match": "feat.*", "prerelease": True, "prerelease_token": "alpha"},
    )

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat!: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0"))
    git_repo.git.tag("v1.1.0", m="v1.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.1"))
    git_repo.git.tag("v1.1.1", m="v1.1.1")

    assert git_repo.commit("v1.1.1").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.1"))
    git_repo.git.tag("v1.2.0-alpha.1", m="v1.2.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (feature) add some missing text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.2"))
    git_repo.git.tag("v1.2.0-alpha.2", m="v1.2.0-alpha.2")

    assert git_repo.commit("v1.2.0-alpha.2").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":boom: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0"))
    git_repo.git.tag("v1.1.0", m="v1.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.1"))
    git_repo.git.tag("v1.1.1", m="v1.1.1")

    assert git_repo.commit("v1.1.1").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.1"))
    git_repo.git.tag("v1.2.0-alpha.1", m="v1.2.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: (feature) add some missing text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.2"))
    git_repo.git.tag("v1.2.0-alpha.2", m="v1.2.0-alpha.2")

    assert git_repo.commit("v1.2.0-alpha.2").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="API: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0"))
    git_repo.git.tag("v1.1.0", m="v1.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.1"))
    git_repo.git.tag("v1.1.1", m="v1.1.1")

    assert git_repo.commit("v1.1.1").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.1"))
    git_repo.git.tag("v1.2.0-alpha.1", m="v1.2.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: (feature) add some missing text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.2"))
    git_repo.git.tag("v1.2.0-alpha.2", m="v1.2.0-alpha.2")

    assert git_repo.commit("v1.2.0-alpha.2").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(
        m=":sparkles: add some more text\n\nBREAKING CHANGE: add some more text"
    )
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0"))
    git_repo.git.tag("v1.1.0", m="v1.1.0")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.1"))
    git_repo.git.tag("v1.1.1", m="v1.1.1")

    assert git_repo.commit("v1.1.1").hexsha == git_repo.head.commit.hexsha

    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.1"))
    git_repo.git.tag("v1.2.0-alpha.1", m="v1.2.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: (feature) add some missing text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-alpha.2"))
    git_repo.git.tag("v1.2.0-alpha.2", m="v1.2.0-alpha.2")

    assert git_repo.commit("v1.2.0-alpha.2").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_and_release_channels_angular_commits(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()
    update_pyproject_toml(
        "tool.semantic_release.branches.features",
        {"match": "feat.*", "prerelease": True, "prerelease_token": "alpha"},
    )

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat!: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "dev" has prerelease suffix of "rc"
    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.1"))
    git_repo.git.tag("v1.1.0-rc.1", m="v1.1.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.2"))
    git_repo.git.tag("v1.1.0-rc.2", m="v1.1.0-rc.2")

    assert git_repo.commit("v1.1.0-rc.2").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "feature" has prerelease suffix of "alpha"
    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.1"))
    git_repo.git.tag("v1.1.0-alpha.1", m="v1.1.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.2"))
    git_repo.git.tag("v1.1.0-alpha.2", m="v1.1.0-alpha.2")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.3"))
    git_repo.git.tag("v1.1.0-alpha.3", m="v1.1.0-alpha.3")

    assert git_repo.commit("v1.1.0-alpha.3").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_and_release_channels_angular_commits_using_tag_format(
    git_repo_factory: RepoInitFn,
    use_angular_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_angular_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("vpy0.1.0", m="vpy0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("vpy0.1.1-rc.1", m="vpy0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat!: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("vpy1.0.0-rc.1", m="vpy1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("vpy1.0.0", m="vpy1.0.0")

    assert git_repo.commit("vpy1.0.0").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "dev" has prerelease suffix of "rc"
    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.1"))
    git_repo.git.tag("vpy1.1.0-rc.1", m="vpy1.1.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.2"))
    git_repo.git.tag("vpy1.1.0-rc.2", m="vpy1.1.0-rc.2")

    assert git_repo.commit("vpy1.1.0-rc.2").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "feature" has prerelease suffix of "alpha"
    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.1"))
    git_repo.git.tag("vpy1.1.0-alpha.1", m="vpy1.1.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.2"))
    git_repo.git.tag("vpy1.1.0-alpha.2", m="vpy1.1.0-alpha.2")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="fix: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.3"))
    git_repo.git.tag("vpy1.1.0-alpha.3", m="vpy1.1.0-alpha.3")

    assert git_repo.commit("vpy1.1.0-alpha.3").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_and_release_channels_emoji_commits(
    git_repo_factory: RepoInitFn,
    use_emoji_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_emoji_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":boom: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "dev" has prerelease suffix of "rc"
    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.1"))
    git_repo.git.tag("v1.1.0-rc.1", m="v1.1.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.2"))
    git_repo.git.tag("v1.1.0-rc.2", m="v1.1.0-rc.2")

    assert git_repo.commit("v1.1.0-rc.2").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "feature" has prerelease suffix of "alpha"
    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.1"))
    git_repo.git.tag("v1.1.0-alpha.1", m="v1.1.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.2"))
    git_repo.git.tag("v1.1.0-alpha.2", m="v1.1.0-alpha.2")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":bug: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.3"))
    git_repo.git.tag("v1.1.0-alpha.3", m="v1.1.0-alpha.3")

    assert git_repo.commit("v1.1.0-alpha.3").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_and_release_channels_scipy_commits(
    git_repo_factory: RepoInitFn,
    use_scipy_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_scipy_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="API: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "dev" has prerelease suffix of "rc"
    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.1"))
    git_repo.git.tag("v1.1.0-rc.1", m="v1.1.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.2"))
    git_repo.git.tag("v1.1.0-rc.2", m="v1.1.0-rc.2")

    assert git_repo.commit("v1.1.0-rc.2").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "feature" has prerelease suffix of "alpha"
    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.1"))
    git_repo.git.tag("v1.1.0-alpha.1", m="v1.1.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="ENH: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.2"))
    git_repo.git.tag("v1.1.0-alpha.2", m="v1.1.0-alpha.2")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="MAINT: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.3"))
    git_repo.git.tag("v1.1.0-alpha.3", m="v1.1.0-alpha.3")

    assert git_repo.commit("v1.1.0-alpha.3").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo


@pytest.fixture
def repo_with_git_flow_and_release_channels_tag_commits(
    git_repo_factory: RepoInitFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    change_to_ex_proj_dir: None,
) -> Repo:
    git_repo = git_repo_factory()
    use_tag_parser()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="Initial commit")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.0"))
    git_repo.git.tag("v0.1.0", m="v0.1.0")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.1.1-rc.1"))
    git_repo.git.tag("v0.1.1-rc.1", m="v0.1.1-rc.1")

    # Do a prerelease
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(
        m=":sparkles: add some more text\n\nBREAKING CHANGE: add some more text"
    )
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0-rc.1"))
    git_repo.git.tag("v1.0.0-rc.1", m="v1.0.0-rc.1")

    # Do a full release
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.0.0"))
    git_repo.git.tag("v1.0.0", m="v1.0.0")

    assert git_repo.commit("v1.0.0").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "dev" has prerelease suffix of "rc"
    git_repo.create_head("dev")
    git_repo.heads.dev.checkout()

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.1"))
    git_repo.git.tag("v1.1.0-rc.1", m="v1.1.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: (dev) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-rc.2"))
    git_repo.git.tag("v1.1.0-rc.2", m="v1.1.0-rc.2")

    assert git_repo.commit("v1.1.0-rc.2").hexsha == git_repo.head.commit.hexsha

    # Suppose branch "feature" has prerelease suffix of "alpha"
    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.1"))
    git_repo.git.tag("v1.1.0-alpha.1", m="v1.1.0-alpha.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":sparkles: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.2"))
    git_repo.git.tag("v1.1.0-alpha.2", m="v1.1.0-alpha.2")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=":nut_and_bolt: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.1.0-alpha.3"))
    git_repo.git.tag("v1.1.0-alpha.3", m="v1.1.0-alpha.3")

    assert git_repo.commit("v1.1.0-alpha.3").hexsha == git_repo.head.commit.hexsha
    assert git_repo.active_branch.name == "feature"
    return git_repo
