import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_travis_should_pass_if_branch_is_master_and_no_pr(monkeypatch):
    monkeypatch.setenv("TRAVIS_BRANCH", "master")
    monkeypatch.setenv("TRAVIS_PULL_REQUEST", "false")

    assert ci_checks.travis("master")


def test_travis_should_pass_if_branch_is_correct_and_no_pr(monkeypatch):
    monkeypatch.setenv("TRAVIS_BRANCH", "other-branch")
    monkeypatch.setenv("TRAVIS_PULL_REQUEST", "false")

    assert ci_checks.travis("other-branch")


def test_travis_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv("TRAVIS_BRANCH", "other-branch")
    monkeypatch.setenv("TRAVIS_PULL_REQUEST", "false")

    with pytest.raises(CiVerificationError):
        ci_checks.travis("master")


def test_travis_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv("TRAVIS_BRANCH", "other-branch")
    monkeypatch.setenv("TRAVIS_PULL_REQUEST", "42")

    with pytest.raises(CiVerificationError):
        ci_checks.travis("master")
