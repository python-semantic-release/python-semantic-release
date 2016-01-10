import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_check_should_call_travis_with_correct_env_variable(mocker, monkeypatch):
    mock_travis = mocker.patch('semantic_release.ci_checks.travis')
    monkeypatch.setenv('TRAVIS', 'true')
    ci_checks.check('master')
    mock_travis.assert_called_once_with('master')


def test_check_should_call_semaphore_with_correct_env_variable(mocker, monkeypatch):
    mock_semaphore = mocker.patch('semantic_release.ci_checks.semaphore')
    monkeypatch.setenv('SEMAPHORE', 'true')
    ci_checks.check('master')
    mock_semaphore.assert_called_once_with('master')


def test_check_should_call_frigg_with_correct_env_variable(mocker, monkeypatch):
    mock_frigg = mocker.patch('semantic_release.ci_checks.frigg')
    monkeypatch.setenv('FRIGG', 'true')
    ci_checks.check('master')
    mock_frigg.assert_called_once_with('master')


def test_travis_should_pass_if_branch_is_master_and_no_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'master')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    assert ci_checks.travis('master')


def test_travis_should_pass_if_branch_is_correct_and_no_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    assert ci_checks.travis('other-branch')


def test_travis_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', 'false')

    with pytest.raises(CiVerificationError):
        ci_checks.travis('master')


def test_travis_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv('TRAVIS_BRANCH', 'other-branch')
    monkeypatch.setenv('TRAVIS_PULL_REQUEST', '42')

    with pytest.raises(CiVerificationError):
        ci_checks.travis('master')


def test_semaphore_should_pass_if_branch_and_status_is_ok(monkeypatch):
    monkeypatch.setenv('BRANCH_NAME', 'master')
    monkeypatch.setenv('SEMAPHORE_THREAD_RESULT', 'success')

    assert ci_checks.semaphore('master')


def test_semaphore_should_raise_ci_verification_error_if_branch_is_wrong(monkeypatch):
    monkeypatch.setenv('BRANCH_NAME', 'other-branch')
    monkeypatch.setenv('SEMAPHORE_THREAD_RESULT', 'success')

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore('master')


def test_semaphore_should_raise_ci_verification_error_if_status_is_failed(monkeypatch):
    monkeypatch.setenv('BRANCH_NAME', 'master')
    monkeypatch.setenv('SEMAPHORE_THREAD_RESULT', 'failed')

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore('master')


def test_semaphore_should_raise_ci_verification_error_if_pull_request_number_is_none(monkeypatch):
    monkeypatch.setenv('BRANCH_NAME', 'master')
    monkeypatch.setenv('SEMAPHORE_THREAD_RESULT', 'success')
    monkeypatch.setenv('PULL_REQUEST_NUMBER', '42')

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore('master')


def test_frigg_should_pass_if_branch_is_master_and_no_pr(monkeypatch):
    monkeypatch.setenv('FRIGG_BUILD_BRANCH', 'master')
    monkeypatch.delenv('FRIGG_PULL_REQUEST', raising=False)

    assert ci_checks.frigg('master')


def test_frigg_should_pass_if_branch_is_correct_and_no_pr(monkeypatch):
    monkeypatch.setenv('FRIGG_BUILD_BRANCH', 'other-branch')
    monkeypatch.delenv('FRIGG_PULL_REQUEST', raising=False)

    assert ci_checks.frigg('other-branch')


def test_frigg_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv('FRIGG_BUILD_BRANCH', 'other-branch')
    monkeypatch.delenv('FRIGG_PULL_REQUEST', raising=False)

    with pytest.raises(CiVerificationError):
        ci_checks.frigg('master')


def test_frigg_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv('FRIGG_BUILD_BRANCH', 'other-branch')
    monkeypatch.setenv('FRIGG_PULL_REQUEST', '42')

    with pytest.raises(CiVerificationError):
        ci_checks.frigg('master')
