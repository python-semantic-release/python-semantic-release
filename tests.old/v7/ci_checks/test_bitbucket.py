import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_bitbucket_should_pass_if_branch_is_master_and_no_pr(monkeypatch):
    monkeypatch.setenv("BITBUCKET_BRANCH", "master")
    monkeypatch.setenv("BITBUCKET_PR_ID", "")

    assert ci_checks.bitbucket("master")


def test_bitbucket_should_pass_if_branch_is_correct_and_no_pr(monkeypatch):
    monkeypatch.setenv("BITBUCKET_BRANCH", "other-branch")
    monkeypatch.setenv("BITBUCKET_PR_ID", "")

    assert ci_checks.bitbucket("other-branch")


def test_bitbucket_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv("BITBUCKET_BRANCH", "other-branch")
    monkeypatch.setenv("BITBUCKET_PR_ID", "")

    with pytest.raises(CiVerificationError):
        ci_checks.bitbucket("master")


def test_bitbucket_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv("BITBUCKET_BRANCH", "other-branch")
    monkeypatch.setenv("BITBUCKET_PR_ID", "http://the-url-of-the-pr")

    with pytest.raises(CiVerificationError):
        ci_checks.bitbucket("master")
