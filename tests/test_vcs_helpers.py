import pytest
from git import GitCommandError

from semantic_release.errors import GitError
from semantic_release.vcs_helpers import (checkout, commit_new_version, get_commit_log,
                                          get_current_head_hash, get_repository_owner_and_name,
                                          push_new_version, tag_new_version)

from . import mock


@pytest.fixture
def mock_git(mocker):
    return mocker.patch('semantic_release.vcs_helpers.repo.git')


def test_first_commit_is_not_initial_commit():
    assert next(get_commit_log()) != 'Initial commit'


def test_add_and_commit(mock_git):
    commit_new_version('1.0.0')
    mock_git.add.assert_called_once_with('semantic_release/__init__.py')
    mock_git.commit.assert_called_once_with(m='1.0.0', author="semantic-release <semantic-release>")


def test_tag_new_version(mock_git):
    tag_new_version('1.0.0')
    mock_git.tag.assert_called_with('-a', 'v1.0.0', m='v1.0.0')


def test_push_new_version(mock_git):
    push_new_version()
    mock_git.push.assert_has_calls([
        mock.call('origin', 'master'),
        mock.call('--tags', 'origin', 'master'),
    ])


def test_get_repository_owner_and_name():
    assert get_repository_owner_and_name()[0] == 'relekang'
    assert get_repository_owner_and_name()[1] == 'python-semantic-release'


def test_get_current_head_hash(mocker):
    mocker.patch('git.objects.commit.Commit.name_rev', 'commit-hash branch-name')
    assert get_current_head_hash() == 'commit-hash'


def test_push_should_not_print_gh_token(mock_git):
    mock_git.configure_mock(**{
        'push.side_effect': GitCommandError('gh--token', 1, b'gh--token', b'gh--token')
    })
    with pytest.raises(GitError) as excinfo:
        push_new_version(gh_token='gh--token')
    assert 'gh--token' not in str(excinfo)


def test_checkout_should_checkout_correct_branch(mock_git):
    checkout('a-branch')
    mock_git.checkout.assert_called_once_with('a-branch')
