import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_gitlab_should_pass_if_branch_is_master(monkeypatch):
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "master")

    assert ci_checks.gitlab("master")


def test_gitlab_should_pass_if_branch_is_correct(monkeypatch):
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "other-branch")

    assert ci_checks.gitlab("other-branch")


def test_gitlab_should_raise_ci_verification_error_for_wrong_branch(monkeypatch):
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "other-branch")

    with pytest.raises(CiVerificationError):
        ci_checks.gitlab("master")
