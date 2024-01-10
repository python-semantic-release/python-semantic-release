from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.const import COMMIT_MESSAGE
from tests.util import add_text_to_file

if TYPE_CHECKING:
    from git import Repo

    from tests.fixtures.example_project import UseParserFn
    from tests.fixtures.git_repo import RepoInitFn


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
