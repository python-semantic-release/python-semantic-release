import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_travis_should_pass_if_branch_is_master_and_no_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'master')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    assert ci_checks.travis()


def test_travis_should_pass_if_branch_is_correct_and_no_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    assert ci_checks.travis(branch='other-branch')


def test_travis_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    with pytest.raises(CiVerificationError):
        assert ci_checks.travis()


def test_travis_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', '42')

    with pytest.raises(CiVerificationError):
        assert ci_checks.travis()


def test_check_should_call_travis_with_correct_env_variable(mocker, monkeypatch):
    mock_travis = mocker.patch('semantic_release.ci_checks.travis')
    monkeypatch.setenv('TRAVIS', 'true')
    ci_checks.check('master')
    mock_travis.assert_called_once_with('master')
