import pytest
from git import Repo, Actor

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER, COMMIT_MESSAGE
from tests.helper import shortuid, add_text_to_file


@pytest.fixture
def commit_author():
    yield Actor(name="semantic release testing", email="not_a_real@email.com")


@pytest.fixture
def file_in_repo():
    yield f"file-{shortuid()}.txt"


@pytest.fixture(
    params=[
        f"git@example.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://example.com/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}",
    ]
)
def git_repo_factory(request, tmp_path_factory):
    def git_repo():
        repo_path = tmp_path_factory.mktemp(f"repo-{shortuid()}")
        repo = Repo.init(repo_path.resolve())
        # Without this the global config may set it to "master", we want consistency
        repo.git.branch("-M", "main")
        with repo.config_writer("repository") as config:
            config.set_value("user", "name", "semantic release testing")
            config.set_value("user", "email", "not_a_real@email.com")
        repo.create_remote(name="origin", url=request.param)
        return repo

    yield git_repo


@pytest.fixture
def repo_with_single_branch(git_repo_factory, file_in_repo):
    git_repo = git_repo_factory()
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


@pytest.fixture
def repo_with_single_branch_and_prereleases(git_repo_factory, file_in_repo):
    git_repo = git_repo_factory()
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


@pytest.fixture
def repo_with_main_and_feature_branches(git_repo_factory, file_in_repo):
    git_repo = git_repo_factory()

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

    git_repo.create_head("feature")
    git_repo.heads.feature.checkout()

    # Do a prerelease on the branch
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="0.2.1-rc.1"))
    git_repo.git.tag("v0.2.1-rc.1", m="v0.2.1-rc.1")

    assert git_repo.commit("v0.2.1-rc.1").hexsha == git_repo.head.commit.hexsha


@pytest.fixture
def repo_with_git_flow(git_repo_factory, file_in_repo):
    git_repo = git_repo_factory()

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
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-rc.1"))
    git_repo.git.tag("v1.2.0-rc.1", m="v1.2.0-rc.1")

    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m="feat: (feature) add some more text")
    add_text_to_file(git_repo, file_in_repo)
    git_repo.git.commit(m=COMMIT_MESSAGE.format(version="1.2.0-rc.2"))
    git_repo.git.tag("v1.2.0-rc.2", m="v1.2.0-rc.2")

    assert git_repo.commit("v1.2.0-rc.2").hexsha == git_repo.head.commit.hexsha


@pytest.fixture
def repo_with_git_flow_and_release_channels(git_repo_factory, file_in_repo):
    git_repo = git_repo_factory()

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

    assert git_repo.commit("v1.1.0-alpha.2").hexsha == git_repo.head.commit.hexsha
