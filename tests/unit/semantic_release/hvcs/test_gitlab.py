from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest import mock

import gitlab
import pytest
from requests import Session

from semantic_release.hvcs.gitlab import Gitlab

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER, RELEASE_NOTES

if TYPE_CHECKING:
    from typing import Generator

gitlab.Gitlab("")  # instantiation necessary to discover gitlab ProjectManager

# Note: there's nothing special about the value of these variables,
# they're just constants for easier consistency with the faked objects
A_GOOD_TAG = "v1.2.3"
A_BAD_TAG = "v2.1.1-rc.1"
A_LOCKED_TAG = "v0.9.0"
A_MISSING_TAG = "v1.0.0+missing"
AN_EXISTING_TAG = "v2.3.4+existing"
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
            if tag in (A_GOOD_TAG, AN_EXISTING_TAG):
                return self._Tag()
            if tag == A_LOCKED_TAG:
                return self._Tag(locked=True)
            raise gitlab.exceptions.GitlabGetError()

        class _Tag:
            def __init__(self, locked=False):
                self.locked = locked

            def set_release_description(self, _):
                if self.locked:
                    raise gitlab.exceptions.GitlabUpdateError()

    class _Releases:
        def __init__(self):
            pass

        def create(self, input_):
            if (
                input_["name"]
                and input_["tag_name"]
                and input_["tag_name"] in (A_GOOD_TAG, A_LOCKED_TAG)
            ):
                return self._Release()
            raise gitlab.exceptions.GitlabCreateError()

        def update(self, tag, _):
            if tag == A_MISSING_TAG:
                raise gitlab.exceptions.GitlabUpdateError()
            return self._Release()

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
def default_gl_client() -> Generator[Gitlab, None, None]:
    remote_url = f"git@gitlab.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    with mock.patch.dict(os.environ, {}, clear=True):
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

        expected_api_url = patched_os_environ.get(
            "CI_SERVER_URL", f"https://{client.hvcs_api_domain}"
        )

        # Evaluate (expected -> actual)
        assert expected_hvcs_domain == client.hvcs_domain
        assert expected_hvcs_api_domain == client.hvcs_api_domain
        assert expected_api_url == client.api_url
        assert token == client.token
        assert remote_url == client._remote_url
        assert hasattr(client, "session")
        assert isinstance(getattr(client, "session", None), Session)


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
    default_gl_client: Gitlab,
    patched_os_environ: dict[str, str],
    expected_owner: str | None,
    expected_name: str | None,
):
    # expected results should be a tuple[namespace, repo_name] and if both are None,
    # then the default value from GitLab class should be used
    expected_result = (expected_owner, expected_name)
    if expected_owner is None and expected_name is None:
        expected_result = super(
            Gitlab, default_gl_client
        )._get_repository_owner_and_name()

    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        # Execute in mocked environment
        result = default_gl_client._get_repository_owner_and_name()

        # Evaluate (expected -> actual)
        assert expected_result == result


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
    default_gl_client: Gitlab,
    use_token: bool,
    token: str,
    # TODO: linter thinks this is a fixture not a param - why?
    _remote_url: str,  # noqa: PT019
    expected: str,
):
    default_gl_client._remote_url = _remote_url
    default_gl_client.token = token
    assert expected == default_gl_client.remote_url(use_token=use_token)


def test_compare_url(default_gl_client: Gitlab):
    start_rev = "revA"
    end_rev = "revB"
    expected_url = (
        "https://{domain}/{owner}/{repo}/-/compare/{from_rev}...{to_rev}".format(
            domain=default_gl_client.hvcs_domain,
            owner=default_gl_client.owner,
            repo=default_gl_client.repo_name,
            from_rev=start_rev,
            to_rev=end_rev,
        )
    )
    actual_url = default_gl_client.compare_url(from_rev=start_rev, to_rev=end_rev)
    assert expected_url == actual_url


def test_commit_hash_url(default_gl_client: Gitlab):
    expected_url = "https://{domain}/{owner}/{repo}/-/commit/{sha}".format(
        domain=default_gl_client.hvcs_domain,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        sha=REF,
    )
    assert expected_url == default_gl_client.commit_hash_url(REF)


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


@pytest.mark.parametrize("tag", (A_GOOD_TAG, A_LOCKED_TAG))
def test_create_release_succeeds(default_gl_client: Gitlab, tag):
    with mock_gitlab():
        assert tag == default_gl_client.create_release(tag, RELEASE_NOTES)


def test_create_release_fails_with_bad_tag(default_gl_client: Gitlab):
    with mock_gitlab(), pytest.raises(gitlab.GitlabCreateError):
        default_gl_client.create_release(A_BAD_TAG, RELEASE_NOTES)


@pytest.mark.parametrize("tag", (A_GOOD_TAG, A_LOCKED_TAG))
def test_update_release_succeeds(default_gl_client: Gitlab, tag: str):
    with mock_gitlab():
        assert tag == default_gl_client.edit_release_notes(tag, RELEASE_NOTES)


def test_update_release_fails_with_missing_tag(default_gl_client: Gitlab):
    with mock_gitlab(), pytest.raises(gitlab.GitlabUpdateError):
        default_gl_client.edit_release_notes(A_MISSING_TAG, RELEASE_NOTES)


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(
    default_gl_client: Gitlab, prerelease: bool
):
    with mock.patch.object(
        default_gl_client, "create_release", return_value=A_GOOD_TAG
    ) as mock_create_release, mock.patch.object(
        default_gl_client, "edit_release_notes", return_value=A_GOOD_TAG
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gl_client.create_or_update_release(
            A_GOOD_TAG, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert A_GOOD_TAG == result  # noqa: SIM300
        mock_create_release.assert_called_once_with(
            tag=A_GOOD_TAG, release_notes=RELEASE_NOTES, prerelease=prerelease
        )
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_succeeds(
    default_gl_client: Gitlab, prerelease: bool
):
    bad_request = gitlab.GitlabCreateError("400 Bad Request")
    with mock.patch.object(
        default_gl_client, "create_release", side_effect=bad_request
    ), mock.patch.object(
        default_gl_client, "edit_release_notes", return_value=A_GOOD_TAG
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gl_client.create_or_update_release(
            A_GOOD_TAG, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert A_GOOD_TAG == result  # noqa: SIM300
        mock_edit_release_notes.assert_called_once_with(
            release_id=A_GOOD_TAG, release_notes=RELEASE_NOTES
        )


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_fails(
    default_gl_client: Gitlab, prerelease: bool
):
    bad_request = gitlab.GitlabCreateError("400 Bad Request")
    not_found = gitlab.GitlabUpdateError("404 Not Found")
    create_release_patch = mock.patch.object(
        default_gl_client, "create_release", side_effect=bad_request
    )
    edit_release_notes_patch = mock.patch.object(
        default_gl_client, "edit_release_notes", side_effect=not_found
    )

    # Execute in mocked environment expecting a GitlabUpdateError to be raised
    with create_release_patch, edit_release_notes_patch:
        with pytest.raises(gitlab.GitlabUpdateError):
            default_gl_client.create_or_update_release(
                A_GOOD_TAG, RELEASE_NOTES, prerelease
            )
