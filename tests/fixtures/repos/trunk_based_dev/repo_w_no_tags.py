from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.util import add_text_to_file

if TYPE_CHECKING:
    from git import Repo

    from tests.fixtures.example_project import UseParserFn
    from tests.fixtures.git_repo import RepoInitFn


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
