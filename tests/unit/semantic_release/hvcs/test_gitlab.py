import os
from contextlib import contextmanager
from unittest import mock

import gitlab
import pytest
from requests import Session

from semantic_release.hvcs.gitlab import Gitlab

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER

gitlab.Gitlab("")  # instantiation necessary to discover gitlab ProjectManager

# Note: there's nothing special about the value of these variables,
# they're just constants for easier consistency with the faked objects
A_GOOD_TAG = "v1.2.3"
A_BAD_TAG = "v2.1.1-rc.1"
A_LOCKED_TAG = "v0.9.0"
# But note this is the only ref we're making a "fake" commit for, so
# tests which need to query the remote for "a" ref, the exact sha for
# which doesn't matter, all use this constant
REF = "hashashash"


class _GitlabProject:
    def __init__(self, status):
        self.commits = {REF: self._Commit(status)}
        self.tags = self._Tags()
        self.releases = self._Releases()

    class _Commit:
        def __init__(self, status):
            self.statuses = self._Statuses(status)

        class _Statuses:
            def __init__(self, status):
                if status == "pending":
                    self.jobs = [
                        {
                            "name": "good_job",
                            "status": "passed",
                            "allow_failure": False,
                        },
                        {
                            "name": "slow_job",
                            "status": "pending",
                            "allow_failure": False,
                        },
                    ]
                elif status == "failure":
                    self.jobs = [
                        {
                            "name": "good_job",
                            "status": "passed",
                            "allow_failure": False,
                        },
                        {"name": "bad_job", "status": "failed", "allow_failure": False},
                    ]
                elif status == "allow_failure":
                    self.jobs = [
                        {
                            "name": "notsobad_job",
                            "status": "failed",
                            "allow_failure": True,
                        },
                        {
                            "name": "good_job2",
                            "status": "passed",
                            "allow_failure": False,
                        },
                    ]
                elif status == "success":
                    self.jobs = [
                        {
                            "name": "good_job1",
                            "status": "passed",
                            "allow_failure": True,
                        },
                        {
                            "name": "good_job2",
                            "status": "passed",
                            "allow_failure": False,
                        },
                    ]

            def list(self):
                return self.jobs

    class _Tags:
        def __init__(self):
            pass

        def get(self, tag):
            if tag == A_GOOD_TAG:
                return self._Tag()
            elif tag == A_LOCKED_TAG:
                return self._Tag(locked=True)
            else:
                raise gitlab.exceptions.GitlabGetError

        class _Tag:
            def __init__(self, locked=False):
                self.locked = locked

            def set_release_description(self, release_notes):
                if self.locked:
                    raise gitlab.exceptions.GitlabUpdateError

    class _Releases:
        def __init__(self):
            pass

        def create(self, input_):
            if input_["name"] and input_["tag_name"]:
                if input_["tag_name"] in (A_GOOD_TAG, A_LOCKED_TAG):
                    return self._Release()
            raise gitlab.exceptions.GitlabCreateError

        class _Release:
            def __init__(self, locked=False):
                pass


@contextmanager
def mock_gitlab(status: str = "success"):
    with mock.patch("gitlab.Gitlab.auth"), mock.patch(
        "gitlab.v4.objects.ProjectManager",
        return_value={
            f"{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}": _GitlabProject(status)
        },
    ):
        yield


@pytest.fixture
def default_gl_client():
    remote_url = f"git@gitlab.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    yield Gitlab(remote_url=remote_url)


@pytest.mark.parametrize(
    (
        "patched_os_environ, hvcs_domain, hvcs_api_domain, "
        "expected_hvcs_domain, expected_hvcs_api_domain"
    ),
    [
        ({}, None, None, Gitlab.DEFAULT_DOMAIN, Gitlab.DEFAULT_DOMAIN),
        (
            {"CI_SERVER_URL": "https://special.custom.server/vcs/"},
            None,
            None,
            "special.custom.server/vcs",
            "special.custom.server/vcs",
        ),
        (
            {"CI_SERVER_HOST": "api.special.custom.server/"},
            None,
            None,
            "api.special.custom.server/",
            "api.special.custom.server/",
        ),
        (
            {"CI_SERVER_URL": "https://special.custom.server/vcs/"},
            "example.com",
            None,
            "example.com",
            "example.com",
        ),
        (
            {"CI_SERVER_URL": "https://api.special.custom.server/"},
            None,
            "api.example.com",
            "api.special.custom.server",
            "api.example.com",
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@gitlab.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://gitlab.com/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_gitlab_client_init(
    patched_os_environ,
    hvcs_domain,
    hvcs_api_domain,
    expected_hvcs_domain,
    expected_hvcs_api_domain,
    remote_url,
    token,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Gitlab(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
        )

        assert client.hvcs_domain == expected_hvcs_domain
        assert client.hvcs_api_domain == expected_hvcs_api_domain
        assert client.api_url == patched_os_environ.get(
            "CI_SERVER_URL", f"https://{client.hvcs_api_domain}"
        )
        assert client.token == token
        assert client._remote_url == remote_url
        assert hasattr(client, "session") and isinstance(
            getattr(client, "session", None), Session
        )


@pytest.mark.parametrize(
    "patched_os_environ, expected_owner, expected_name",
    [
        ({}, None, None),
        (
            {"CI_PROJECT_NAMESPACE": "path/to/repo", "CI_PROJECT_NAME": "foo"},
            "path/to/repo",
            "foo",
        ),
    ],
)
def test_gitlab_get_repository_owner_and_name(
    default_gl_client, patched_os_environ, expected_owner, expected_name
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        if expected_owner is None and expected_name is None:
            assert (
                default_gl_client._get_repository_owner_and_name()
                == super(Gitlab, default_gl_client)._get_repository_owner_and_name()
            )
        else:
            assert default_gl_client._get_repository_owner_and_name() == (
                expected_owner,
                expected_name,
            )


@pytest.mark.parametrize(
    "use_token, token, _remote_url, expected",
    [
        (
            False,
            "",
            "git@gitlab.com:custom/example.git",
            "git@gitlab.com:custom/example.git",
        ),
        (
            True,
            "",
            "git@gitlab.com:custom/example.git",
            "git@gitlab.com:custom/example.git",
        ),
        (
            False,
            "aabbcc",
            "git@gitlab.com:custom/example.git",
            "git@gitlab.com:custom/example.git",
        ),
        (
            True,
            "aabbcc",
            "git@gitlab.com:custom/example.git",
            "https://gitlab-ci-token:aabbcc@gitlab.com/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gl_client,
    use_token,
    token,
    _remote_url,
    expected,
):
    default_gl_client._remote_url = _remote_url
    default_gl_client.token = token
    assert default_gl_client.remote_url(use_token=use_token) == expected


def test_compare_url(default_gl_client):
    assert default_gl_client.compare_url(
        from_rev="revA", to_rev="revB"
    ) == "https://{domain}/{owner}/{repo}/-/compare/revA...revB".format(
        domain=default_gl_client.hvcs_domain,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
    )


def test_commit_hash_url(default_gl_client):
    assert default_gl_client.commit_hash_url(
        REF
    ) == "https://{domain}/{owner}/{repo}/-/commit/{sha}".format(
        domain=default_gl_client.hvcs_domain,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        sha=REF,
    )


@pytest.mark.parametrize("pr_number", (420, "420"))
def test_pull_request_url(default_gl_client, pr_number):
    assert default_gl_client.pull_request_url(
        pr_number=pr_number
    ) == "https://{domain}/{owner}/{repo}/-/issues/{pr_number}".format(
        domain=default_gl_client.hvcs_domain,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        pr_number=pr_number,
    )


@pytest.mark.parametrize(
    "tag, expected",
    [
        (A_GOOD_TAG, True),
        (A_LOCKED_TAG, True),
        (A_BAD_TAG, False),
    ],
)
def test_create_release(default_gl_client, tag, expected):
    release_notes = "# TODO: Release Notes"
    with mock_gitlab():
        assert default_gl_client.create_release(tag, release_notes) == expected
