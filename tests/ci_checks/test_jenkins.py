import pytest

from semantic_release import ci_checks
from semantic_release.errors import CiVerificationError


def test_jenkins_should_pass_if_url_set_branch_master_no_pr(monkeypatch):
    monkeypatch.setenv("JENKINS_URL", "http://custom.jenkins.int.com")
    monkeypatch.setenv("BRANCH_NAME", "master")

    assert ci_checks.jenkins("master")


def test_jenkins_should_pass_if_url_set_if_branch_correct_no_pr(monkeypatch):
    monkeypatch.setenv("JENKINS_URL", "http://custom.jenkins.int.com")
    monkeypatch.setenv("GIT_BRANCH", "foo-bar")

    assert ci_checks.jenkins("foo-bar")


def test_jenkins_should_raise_ci_verification_error_no_url(monkeypatch):
    monkeypatch.setenv("BRANCH_NAME", "foo-bar")

    with pytest.raises(CiVerificationError):
        assert ci_checks.jenkins("foo-bar")


def test_jenkins_should_raise_ci_verification_error_for_pr(monkeypatch):
    monkeypatch.setenv("JENKINS_URL", "http://custom.jenkins.int.com")
    monkeypatch.setenv("BRANCH_NAME", "foo-bar")
    monkeypatch.setenv("CHANGE_ID", "1")

    with pytest.raises(CiVerificationError):
        assert ci_checks.jenkins("foo-bar")
