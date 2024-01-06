import os
import re
from contextlib import contextmanager
from unittest import mock

import gitlab
import pytest
import requests_mock
from requests import Session, HTTPError

from semantic_release.hvcs.gitlab_ci import GitlabCi

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER, RELEASE_NOTES

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

MINIMUM_ENV_EXPECTED = {
    "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
    "CI_SERVER_URL": "https://gitlab.example.com",
    "CI_SERVER_HOST": "gitlab.example.com",
    "CI_PROJECT_ID": "42",
    "CI_JOB_TOKEN": "NOT_A_REAL_TOKEN",
    "CI_PROJECT_NAMESPACE": EXAMPLE_REPO_OWNER,
    "CI_PROJECT_NAME": EXAMPLE_REPO_NAME,
}


@pytest.fixture
def default_gl_client():
    with mock.patch.dict(os.environ, MINIMUM_ENV_EXPECTED, clear=True):
        remote_url = f"git@gitlab.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
        return GitlabCi(remote_url=remote_url)


@pytest.mark.parametrize(
    (
            "patched_os_environ, hvcs_domain, hvcs_api_domain, "
            "expected_hvcs_domain, expected_hvcs_api_domain"
    ),
    [
        (
                {**MINIMUM_ENV_EXPECTED},
                None,
                None,
                "gitlab.example.com",
                "gitlab.example.com",
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
        client = GitlabCi(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
        )

        assert client.hvcs_domain == expected_hvcs_domain
        assert client.hvcs_api_domain == expected_hvcs_api_domain
        assert client.api_url == patched_os_environ.get("CI_API_V4_URL")
        assert client.token == patched_os_environ.get("CI_JOB_TOKEN")
        assert client._remote_url == remote_url
        assert hasattr(client, "session")
        assert isinstance(getattr(client, "session", None), Session)


@pytest.mark.parametrize(
    "patched_os_environ, expected_owner, expected_name",
    [
        (MINIMUM_ENV_EXPECTED, EXAMPLE_REPO_OWNER, EXAMPLE_REPO_NAME),
        (
                {**MINIMUM_ENV_EXPECTED, "CI_PROJECT_NAMESPACE": "path/to/repo", "CI_PROJECT_NAME": "foo"},
                "path/to/repo",
                "foo",
        ),
    ],
)
def test_gitlab_get_repository_owner_and_name(
    patched_os_environ, expected_owner, expected_name
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        gl_client = GitlabCi(remote_url="doesn't matter it's not used")
        if expected_owner is None and expected_name is None:
            assert (
                    gl_client._get_repository_owner_and_name()
                    == super(GitlabCi, gl_client)._get_repository_owner_and_name()
            )
        else:
            assert gl_client._get_repository_owner_and_name() == (
                expected_owner,
                expected_name,
            )


def test_compare_url(default_gl_client):
    assert default_gl_client.compare_url(
        from_rev="revA", to_rev="revB"
    ) == "https://{domain}/{owner}/{repo}/-/compare/revA...revB".format(
        domain=default_gl_client.hvcs_domain,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
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
                "git@gitlab.com:custom/example.git",
        ),
    ],
)
def test_remote_url(
        default_gl_client,
        use_token,
        token,
        # TODO: linter thinks this is a fixture not a param - why?
        _remote_url,  # noqa: PT019
        expected,
):
    default_gl_client._remote_url = _remote_url
    default_gl_client.token = token
    assert default_gl_client.remote_url(use_token=use_token) == expected


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


GITLAB_API_MATCHER = re.compile(rf"^https://gitlab.example.com")


@pytest.mark.parametrize("status_code", (200, 201))
@pytest.mark.parametrize("tag", ("v0.1.0", "v1.0.0"))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_succeeds(default_gl_client, status_code, prerelease, tag):
    with requests_mock.Mocker(session=default_gl_client.session) as m:
        m.register_uri(
            "POST",
            GITLAB_API_MATCHER,
            json={"tag": tag},
            status_code=status_code,
        )
        assert (
                default_gl_client.create_release(tag, RELEASE_NOTES, prerelease)
                == tag
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert (
                m.last_request.url
                == "{api_url}/projects/{project_id}/releases".format(
            api_url=default_gl_client.api_url,
            project_id=default_gl_client.project_id, )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": f"Release {tag}",
            "description": RELEASE_NOTES,
        }


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_fails(default_gl_client, prerelease, status_code):
    tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gl_client.session) as m:
        m.register_uri(
            "POST", GITLAB_API_MATCHER, status_code=status_code
        )

        with pytest.raises(HTTPError):
            default_gl_client.create_release(tag, RELEASE_NOTES, prerelease)

            assert m.called
            assert len(m.request_history) == 1
            assert m.last_request.method == "POST"
            assert (
                    m.last_request.url
                    == "{api_url}/projects/{project_id}/releases".format(
                api_url=default_gl_client.api_url,
                project_id=default_gl_client.project_id, )
            )
            assert m.last_request.json() == {
                "tag_name": tag,
                "name": f"Release {tag}",
                "description": RELEASE_NOTES,
            }


def test_not_running_in_gitlab_ci():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            GitlabCi(remote_url="git@github.com:something/somewhere.git")


@pytest.mark.parametrize("status_code", [201])
@pytest.mark.parametrize("mock_tag", ("v0.1.0", "v1.0.0"))
def test_edit_release_notes_succeeds(default_gl_client, status_code, mock_tag):
    with requests_mock.Mocker(session=default_gl_client.session) as m:
        m.register_uri(
            "PUT",
            GITLAB_API_MATCHER,
            json={"tag": mock_tag},
            status_code=status_code,
        )
        assert (
                default_gl_client.edit_release_notes(mock_tag, RELEASE_NOTES)
                == mock_tag
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "PUT"
        assert (
                m.last_request.url
                == "{api_url}/projects/{project_id}/releases/{mock_tag}".format(
            api_url=default_gl_client.api_url,
            project_id=default_gl_client.project_id,
            mock_tag=mock_tag
            )
        )


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
def test_edit_release_notes_fails(default_gl_client, status_code):
    mock_tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gl_client.session) as m:
        m.register_uri(
            "PUT", GITLAB_API_MATCHER, status_code=status_code
        )

        with pytest.raises(HTTPError):
            default_gl_client.edit_release_notes(mock_tag, RELEASE_NOTES)

        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "PUT"
        assert (
                m.last_request.url
                == "{api_url}/projects/{project_id}/releases/{mock_tag}".format(
                api_url=default_gl_client.api_url,
                project_id=default_gl_client.project_id,
                mock_tag=mock_tag
            )
        )
        assert m.last_request.json() == {"description": RELEASE_NOTES}


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(default_gl_client, prerelease):

    with mock.patch.object(
            default_gl_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gl_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        mock_create_release.return_value = A_GOOD_TAG
        mock_edit_release_notes.return_value = A_GOOD_TAG
        assert (
                default_gl_client.create_or_update_release(
                    A_GOOD_TAG, RELEASE_NOTES, prerelease
                )
                == A_GOOD_TAG
        )
        mock_create_release.assert_called_once_with(
            tag=A_GOOD_TAG, release_notes=RELEASE_NOTES, prerelease=prerelease
        )
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_succeeds(default_gl_client, prerelease):
    bad_request = HTTPError("400 Bad Request")
    with mock.patch.object(
            default_gl_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gl_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        # TODO: not sure what the error code would be for an existing tag.
        mock_create_release.side_effect = bad_request
        mock_edit_release_notes.return_value = A_GOOD_TAG
        assert (
                default_gl_client.create_or_update_release(
                    A_GOOD_TAG, RELEASE_NOTES, prerelease
                )
                == A_GOOD_TAG
        )
        mock_edit_release_notes.assert_called_once_with(
            release_id=A_GOOD_TAG, release_notes=RELEASE_NOTES
        )


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_fails(default_gl_client, prerelease
):
    bad_request = HTTPError("400 Bad Request")
    not_found = HTTPError("404 Not Found")
    with mock.patch.object(
            default_gl_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gl_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        mock_create_release.side_effect = bad_request
        mock_edit_release_notes.side_effect = not_found

        with pytest.raises(HTTPError):
            default_gl_client.create_or_update_release(
                A_GOOD_TAG, RELEASE_NOTES, prerelease
            )
