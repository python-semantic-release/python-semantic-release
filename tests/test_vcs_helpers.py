import os

import git
import pytest
from git import GitCommandError, Repo, TagObject

from semantic_release.errors import GitError, HvcsRepoParseError
from semantic_release.vcs_helpers import (
    check_repo,
    checkout,
    commit_new_version,
    config,
    get_commit_log,
    get_current_head_hash,
    get_last_version,
    get_repository_owner_and_name,
    get_version_from_tag,
    push_new_version,
    tag_new_version,
)

from . import mock, wrapped_config_get


@pytest.fixture
def mock_git(mocker):
    return mocker.patch("semantic_release.vcs_helpers.repo.git")


@mock.patch("semantic_release.vcs_helpers.repo", None)
def test_raises_error_when_invalid_repo():
    with pytest.raises(GitError):
        check_repo(lambda: None)()


def test_first_commit_is_not_initial_commit():
    assert next(get_commit_log()) != "Initial commit"


@pytest.mark.parametrize(
        'params', [

            # Basic usage:
            dict(
                version='1.0.0',
                config = dict(
                    version_variable='path:---',
                ),
                add_paths = [
                    'path',
                ],
                commit_args = dict(
                    m="1.0.0\n\nAutomatically generated by python-semantic-release",
                    author="semantic-release <semantic-release>",
                ),
            ),

            # With author:
            dict(
                version='1.0.0',
                config = dict(
                    version_variable='path:---',
                    commit_author='Alice <alice@example.com>',
                ),
                add_paths = [
                    'path',
                ],
                commit_args = dict(
                    m="1.0.0\n\nAutomatically generated by python-semantic-release",
                    author='Alice <alice@example.com>',
                ),
            ),

            # With multiple version paths:
            dict(
                version='1.0.0',
                config = dict(
                    version_variable=[
                        'path1:---',
                        'path2:---',
                    ]
                ),
                add_paths = [
                    'path1',
                    'path2',
                ],
                commit_args = dict(
                    m="1.0.0\n\nAutomatically generated by python-semantic-release",
                    author="semantic-release <semantic-release>",
                ),
            ),
        ]
)
def test_add_and_commit(mock_git, mocker, params):
    mocker.patch(
            "semantic_release.vcs_helpers.config.get",
            wrapped_config_get(**params['config'])
    )

    commit_new_version(params['version'])

    for path in params['add_paths']:
        mock_git.add.assert_any_call(path)

    mock_git.commit.assert_called_once_with(**params['commit_args'])


def test_tag_new_version(mock_git):
    tag_new_version("1.0.0")
    mock_git.tag.assert_called_with("-a", "v1.0.0", m="v1.0.0")


def test_push_new_version(mock_git):
    push_new_version()
    mock_git.push.assert_has_calls(
        [mock.call("origin", "master"), mock.call("--tags", "origin", "master"),]
    )


def test_push_new_version_with_custom_branch(mock_git):
    push_new_version(branch="release")
    mock_git.push.assert_has_calls(
        [mock.call("origin", "release"), mock.call("--tags", "origin", "release"),]
    )


@pytest.mark.parametrize(
    "origin_url,expected_result",
    [
        ("git@github.com:group/project.git", ("group", "project")),
        ("git@gitlab.example.com:group/project.git", ("group", "project")),
        (
            "git@gitlab.example.com:group/subgroup/project.git",
            ("group/subgroup", "project"),
        ),
        (
            "git@gitlab.example.com:group/subgroup/project",
            ("group/subgroup", "project"),
        ),
        (
            "git@gitlab.example.com:group/subgroup.with.dots/project",
            ("group/subgroup.with.dots", "project"),
        ),
        ("https://github.com/group/project.git", ("group", "project")),
        (
            "https://gitlab.example.com/group/subgroup/project.git",
            ("group/subgroup", "project"),
        ),
        (
            "https://gitlab.example.com/group/subgroup/project",
            ("group/subgroup", "project"),
        ),
        (
            "https://gitlab.example.com/group/subgroup/pro.ject",
            ("group/subgroup", "pro.ject"),
        ),
        (
            "https://gitlab.example.com/group/subgroup/pro.ject.git",
            ("group/subgroup", "pro.ject"),
        ),
        (
            "https://gitlab.example.com/firstname.lastname/project.git",
            ("firstname.lastname", "project"),
        ),
        (
            "https://gitlab-ci-token:MySuperToken@gitlab.example.com/group/project.git",
            ("group", "project"),
        ),
        (
            "https://gitlab-ci-token:MySuperToken@gitlab.example.com/group/subgroup/project.git",
            ("group/subgroup", "project"),
        ),
        (
            "https://gitlab-ci-token:MySuperToken@gitlab.example.com/group/sub.group/project.git",
            ("group/sub.group", "project"),
        ),
        ("bad_repo_url", HvcsRepoParseError),
    ],
)
def test_get_repository_owner_and_name(mocker, origin_url, expected_result):
    class FakeRemote:
        url = origin_url

    mocker.patch("git.repo.base.Repo.remote", return_value=FakeRemote())
    if isinstance(expected_result, tuple):
        assert get_repository_owner_and_name() == expected_result
    else:
        with pytest.raises(expected_result):
            get_repository_owner_and_name()


def test_get_current_head_hash(mocker):
    mocker.patch("git.objects.commit.Commit.name_rev", "commit-hash branch-name")
    assert get_current_head_hash() == "commit-hash"


@mock.patch("semantic_release.vcs_helpers.config.get", return_value="gitlab")
def test_push_should_not_print_auth_token(mock_gitlab, mock_git):
    mock_git.configure_mock(
        **{
            "push.side_effect": GitCommandError(
                "auth--token", 1, b"auth--token", b"auth--token"
            )
        }
    )
    with pytest.raises(GitError) as excinfo:
        push_new_version(auth_token="auth--token")
    assert "auth--token" not in str(excinfo)


def test_checkout_should_checkout_correct_branch(mock_git):
    checkout("a-branch")
    mock_git.checkout.assert_called_once_with("a-branch")


@pytest.mark.parametrize(
    "skip_tags,expected_result",
    [
        (None, "2.0.0"),
        (["v2.0.0"], "1.1.0"),
        (["v0.1.0", "v1.0.0", "v1.1.0", "v2.0.0"], None),
    ],
)
def test_get_last_version(skip_tags, expected_result):
    class FakeCommit:
        def __init__(self, com_date):
            self.committed_date = com_date

    class FakeTagObject:
        def __init__(self, tag_date):
            self.tagged_date = tag_date

    class FakeTag:
        def __init__(self, name, sha, date, is_tag_object):
            self.name = name
            self.tag = FakeTagObject(date)
            if is_tag_object:
                self.commit = TagObject(Repo(), sha)
            else:
                self.commit = FakeCommit(date)

    mock.patch("semantic_release.vcs_helpers.check_repo")
    git.repo.base.Repo.tags = mock.PropertyMock(
        return_value=[
            FakeTag("v0.1.0", "aaaaaaaaaaaaaaaaaaaa", 1, True),
            FakeTag("v2.0.0", "dddddddddddddddddddd", 4, True),
            FakeTag("badly_formatted", "eeeeeeeeeeeeeeeeeeee", 5, False),
            FakeTag("v1.1.0", "cccccccccccccccccccc", 3, True),
            FakeTag("v1.0.0", "bbbbbbbbbbbbbbbbbbbb", 2, False),
        ]
    )
    assert expected_result == get_last_version(skip_tags)


@pytest.mark.parametrize(
    "tag_name,expected_version",
    [("v0.1.0", "aaaaa"), ("v1.0.0", "bbbbb"), ("v2.0.0", None),],
)
def test_get_version_from_tag(tag_name, expected_version):
    class FakeCommit:
        def __init__(self, sha):
            self.hexsha = sha

    class FakeTag:
        def __init__(self, name, sha):
            self.name = name
            self.commit = FakeCommit(sha)

    mock.patch("semantic_release.vcs_helpers.check_repo")
    git.repo.base.Repo.tags = mock.PropertyMock(
        return_value=[
            FakeTag("v0.1.0", "aaaaa"),
            FakeTag("v1.0.0", "bbbbb"),
            FakeTag("v1.1.0", "ccccc"),
        ]
    )
    assert expected_version == get_version_from_tag(tag_name)
