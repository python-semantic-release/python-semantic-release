import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_semaphore_should_pass_if_branch_and_status_is_ok(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "master")
    monkeypatch.setenv("SEMAPHORE_THREAD_RESULT", "success")

    assert ci_checks.semaphore("master")


def test_semaphore_should_raise_ci_verification_error_if_branch_is_wrong(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "other-branch")
    monkeypatch.setenv("SEMAPHORE_THREAD_RESULT", "success")

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore("master")


def test_semaphore_should_raise_ci_verification_error_if_status_is_failed(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "master")
    monkeypatch.setenv("SEMAPHORE_THREAD_RESULT", "failed")

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore("master")


def test_semaphore_should_raise_ci_verification_error_if_pull_request_number_is_none(
    monkeypatch,
):
    monkeypatch.setenv("BRANCH_NAME", "master")
    monkeypatch.setenv("SEMAPHORE_THREAD_RESULT", "success")
    monkeypatch.setenv("PULL_REQUEST_NUMBER", "42")

    with pytest.raises(CiVerificationError):
        ci_checks.semaphore("master")
