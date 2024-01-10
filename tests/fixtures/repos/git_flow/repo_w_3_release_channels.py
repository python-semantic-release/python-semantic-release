from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.const import COMMIT_MESSAGE
from tests.util import add_text_to_file

if TYPE_CHECKING:
    from git import Repo

    from tests.fixtures.example_project import UpdatePyprojectTomlFn, UseParserFn
    from tests.fixtures.git_repo import RepoInitFn


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
