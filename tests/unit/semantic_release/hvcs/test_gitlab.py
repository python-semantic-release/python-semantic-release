from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING
from unittest import mock

import gitlab
import pytest

from semantic_release.hvcs.gitlab import Gitlab

from tests.const import (
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    RELEASE_NOTES,
)

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
    remote_url = (
        f"git@{Gitlab.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    )
    with mock.patch.dict(os.environ, {}, clear=True):
        yield Gitlab(remote_url=remote_url)


@pytest.mark.parametrize(
    "patched_os_environ, hvcs_domain, expected_hvcs_domain, insecure",
    # NOTE: GitLab does not have a different api domain
    [
        # Default values
        ({}, None, f"https://{Gitlab.DEFAULT_DOMAIN}", False),
        (
            # Gather domain from environment
            {"CI_SERVER_URL": "https://special.custom.server/"},
            None,
            "https://special.custom.server",
            False,
        ),
        (
            # Custom domain with path prefix (derives from environment)
            {"CI_SERVER_URL": "https://special.custom.server/vcs/"},
            None,
            "https://special.custom.server/vcs",
            False,
        ),
        (
            # Ignore environment & use provided parameter value (ie from user config)
            {
                "CI_SERVER_URL": "https://special.custom.server/",
                "CI_API_V4_URL": "https://special.custom.server/api/v3",
            },
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            False,
        ),
        (
            # Allow insecure http connections explicitly
            {},
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            True,
        ),
        (
            # Infer insecure connection from user configuration
            {},
            EXAMPLE_HVCS_DOMAIN,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            True,
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@{Gitlab.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://{Gitlab.DEFAULT_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_gitlab_client_init(
    patched_os_environ: dict[str, str],
    hvcs_domain: str | None,
    expected_hvcs_domain: str,
    remote_url: str,
    token: str | None,
    insecure: bool,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Gitlab(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            token=token,
            allow_insecure=insecure,
        )

        # Evaluate (expected -> actual)
        assert expected_hvcs_domain == client.hvcs_domain.url
        assert token == client.token
        assert remote_url == client._remote_url


@pytest.mark.parametrize(
    "hvcs_domain, insecure",
    [
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", False),
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", True),
        (f"http://{EXAMPLE_HVCS_DOMAIN}", False),
    ],
)
def test_gitlab_client_init_with_invalid_scheme(
    hvcs_domain: str,
    insecure: bool,
):
    with pytest.raises(ValueError), mock.patch.dict(os.environ, {}, clear=True):
        Gitlab(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=hvcs_domain,
            allow_insecure=insecure,
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
    "use_token, token, remote_url, expected_auth_url",
    [
        (
            False,
            "",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            True,
            "",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            False,
            "aabbcc",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            True,
            "aabbcc",
            f"git@{Gitlab.DEFAULT_DOMAIN}:custom/example.git",
            f"https://gitlab-ci-token:aabbcc@{Gitlab.DEFAULT_DOMAIN}/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gl_client: Gitlab,
    use_token: bool,
    token: str,
    remote_url: str,
    expected_auth_url: str,
):
    default_gl_client._remote_url = remote_url
    default_gl_client.token = token
    assert expected_auth_url == default_gl_client.remote_url(use_token=use_token)


def test_compare_url(default_gl_client: Gitlab):
    start_rev = "revA"
    end_rev = "revB"
    expected_url = "{server}/{owner}/{repo}/-/compare/{from_rev}...{to_rev}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        from_rev=start_rev,
        to_rev=end_rev,
    )
    actual_url = default_gl_client.compare_url(from_rev=start_rev, to_rev=end_rev)
    assert expected_url == actual_url


def test_commit_hash_url(default_gl_client: Gitlab):
    expected_url = "{server}/{owner}/{repo}/-/commit/{sha}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        sha=REF,
    )
    assert expected_url == default_gl_client.commit_hash_url(REF)


@pytest.mark.parametrize("issue_number", (420, "420"))
def test_issue_url(default_gl_client: Gitlab, issue_number: int | str):
    expected_url = "{server}/{owner}/{repo}/-/issues/{issue_num}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        issue_num=issue_number,
    )
    actual_url = default_gl_client.issue_url(issue_number=issue_number)
    assert expected_url == actual_url


@pytest.mark.parametrize("pr_number", (420, "420"))
def test_pull_request_url(default_gl_client: Gitlab, pr_number: int | str):
    expected_url = "{server}/{owner}/{repo}/-/merge_requests/{pr_number}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        pr_number=pr_number,
    )
    actual_url = default_gl_client.pull_request_url(pr_number=pr_number)
    assert expected_url == actual_url


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
