from __future__ import annotations

import fnmatch
import glob
import os
import re
from typing import TYPE_CHECKING
from unittest import mock
from urllib.parse import urlencode

import pytest
import requests_mock
from requests import HTTPError, Response, Session
from requests.auth import _basic_auth_str

from semantic_release.hvcs.gitea import Gitea
from semantic_release.hvcs.token_auth import TokenAuth

from tests.const import (
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    RELEASE_NOTES,
)
from tests.fixtures.example_project import init_example_project

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator

    from tests.conftest import NetrcFileFn


@pytest.fixture
def default_gitea_client() -> Generator[Gitea, None, None]:
    remote_url = (
        f"git@{Gitea.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    )
    with mock.patch.dict(os.environ, {}, clear=True):
        yield Gitea(remote_url=remote_url)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "patched_os_environ",
            "hvcs_domain",
            "expected_hvcs_domain",
            "insecure",
        ],
    ),
    # NOTE: Gitea does not have a different api domain
    [
        # Default values
        ({}, None, f"https://{Gitea.DEFAULT_DOMAIN}", False),
        (
            # Gather domain from environment
            {"GITEA_SERVER_URL": "https://special.custom.server/"},
            None,
            "https://special.custom.server",
            False,
        ),
        (
            # Custom domain with path prefix (derives from environment)
            {"GITEA_SERVER_URL": "https://special.custom.server/vcs/"},
            None,
            "https://special.custom.server/vcs",
            False,
        ),
        (
            # Ignore environment & use provided parameter value (ie from user config)
            {"GITEA_SERVER_URL": "https://special.custom.server/"},
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
        f"git@{Gitea.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://{Gitea.DEFAULT_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_gitea_client_init(
    patched_os_environ: dict[str, str],
    hvcs_domain: str | None,
    expected_hvcs_domain: str,
    remote_url: str,
    token: str | None,
    insecure: bool,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Gitea(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            token=token,
            allow_insecure=insecure,
        )

        # Evaluate (expected -> actual)
        assert expected_hvcs_domain == client.hvcs_domain.url
        assert f"{expected_hvcs_domain}/api/v1" == str(client.api_url)
        assert token == client.token
        assert remote_url == client._remote_url
        assert hasattr(client, "session")
        assert isinstance(getattr(client, "session", None), Session)


@pytest.mark.parametrize(
    "hvcs_domain, insecure",
    [
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", False),
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", True),
        (f"http://{EXAMPLE_HVCS_DOMAIN}", False),
    ],
)
def test_gitea_client_init_with_invalid_scheme(hvcs_domain: str, insecure: bool):
    with pytest.raises(ValueError), mock.patch.dict(os.environ, {}, clear=True):
        Gitea(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=hvcs_domain,
            allow_insecure=insecure,
        )


def test_gitea_get_repository_owner_and_name(default_gitea_client: Gitea):
    expected_result = (EXAMPLE_REPO_OWNER, EXAMPLE_REPO_NAME)

    # Execute method under test
    result = default_gitea_client._get_repository_owner_and_name()

    # Evaluate (expected -> actual)
    assert expected_result == result


@pytest.mark.parametrize(
    "use_token, token, remote_url, expected_auth_url",
    [
        (
            False,
            "",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            True,
            "",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            False,
            "aabbcc",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            True,
            "aabbcc",
            f"git@{Gitea.DEFAULT_DOMAIN}:custom/example.git",
            f"https://aabbcc@{Gitea.DEFAULT_DOMAIN}/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gitea_client: Gitea,
    use_token: bool,
    token: str,
    remote_url: str,
    expected_auth_url: str,
):
    default_gitea_client._remote_url = remote_url
    default_gitea_client.token = token
    assert expected_auth_url == default_gitea_client.remote_url(use_token=use_token)


def test_commit_hash_url(default_gitea_client: Gitea):
    sha = "hashashash"
    expected_url = "{server}/{owner}/{repo}/commit/{sha}".format(
        server=default_gitea_client.hvcs_domain.url,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        sha=sha,
    )
    assert expected_url == default_gitea_client.commit_hash_url(sha)


def test_commit_hash_url_w_custom_server():
    """
    Test the commit hash URL generation for a self-hosted Bitbucket server with prefix.

    ref: https://github.com/python-semantic-release/python-semantic-release/issues/1204
    """
    sha = "244f7e11bcb1e1ce097db61594056bc2a32189a0"
    expected_url = "{server}/{owner}/{repo}/commit/{sha}".format(
        server=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        owner="foo",
        repo=EXAMPLE_REPO_NAME,
        sha=sha,
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        actual_url = Gitea(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo/foo/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        ).commit_hash_url(sha)

    assert expected_url == actual_url


@pytest.mark.parametrize("issue_number", (666, "666", "#666"))
def test_issue_url(default_gitea_client: Gitea, issue_number: int | str):
    expected_url = "{server}/{owner}/{repo}/issues/{issue_number}".format(
        server=default_gitea_client.hvcs_domain.url,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        issue_number=str(issue_number).lstrip("#"),
    )
    assert expected_url == default_gitea_client.issue_url(issue_num=issue_number)


@pytest.mark.parametrize("pr_number", (666, "666", "#666"))
def test_pull_request_url(default_gitea_client: Gitea, pr_number: int | str):
    expected_url = "{server}/{owner}/{repo}/pulls/{pr_number}".format(
        server=default_gitea_client.hvcs_domain.url,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        pr_number=str(pr_number).lstrip("#"),
    )
    actual_url = default_gitea_client.pull_request_url(pr_number=pr_number)
    assert expected_url == actual_url


@pytest.mark.parametrize("release_id", (42, 666))
def test_asset_upload_url(default_gitea_client: Gitea, release_id: int):
    expected_url = "{server}/repos/{owner}/{repo}/releases/{release_id}/assets".format(
        server=default_gitea_client.api_url,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        release_id=release_id,
    )
    actual_url = default_gitea_client.asset_upload_url(release_id=release_id)
    assert expected_url == actual_url


############
# Tests which need http response mocking
############


gitea_matcher = re.compile(rf"^https://{Gitea.DEFAULT_DOMAIN}")
gitea_api_matcher = re.compile(
    rf"^https://{Gitea.DEFAULT_DOMAIN}{Gitea.DEFAULT_API_PATH}"
)


@pytest.mark.parametrize("status_code", [201])
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_succeeds(
    default_gitea_client: Gitea,
    mock_release_id: int,
    prerelease: bool,
    status_code: int,
):
    tag = "v1.0.0"
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gitea_client.api_url,
        owner=default_gitea_client.owner,
        repo_name=default_gitea_client.repo_name,
    )
    expected_request_body = {
        "tag_name": tag,
        "name": tag,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": prerelease,
    }

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test
        actual_rtn_val = default_gitea_client.create_release(
            tag, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == actual_rtn_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize("status_code", (400, 409))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_fails(
    default_gitea_client: Gitea,
    mock_release_id: int,
    prerelease: bool,
    status_code: int,
):
    tag = "v1.0.0"
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gitea_client.api_url,
        owner=default_gitea_client.owner,
        repo_name=default_gitea_client.repo_name,
    )
    expected_request_body = {
        "tag_name": tag,
        "name": tag,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": prerelease,
    }

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test expecting an exeception to be raised
        with pytest.raises(HTTPError):
            default_gitea_client.create_release(tag, RELEASE_NOTES, prerelease)

        # Evaluate (expected -> actual)
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize("token", (None, "super-token"))
def test_should_create_release_using_token_or_netrc(
    default_gitea_client: Gitea,
    token: str | None,
    default_netrc_username: str,
    default_netrc_password: str,
    netrc_file: NetrcFileFn,
    clean_os_environment: dict[str, str],
):
    # Setup
    default_gitea_client.token = token
    default_gitea_client.session.auth = None if not token else TokenAuth(token)
    tag = "v1.0.0"
    expected_release_id = 1
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gitea_client.api_url,
        owner=default_gitea_client.owner,
        repo_name=default_gitea_client.repo_name,
    )
    expected_request_body = {
        "tag_name": tag,
        "name": tag,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": False,
    }

    expected_request_headers = set(
        (
            {"Authorization": f"token {token}"}
            if token
            else {
                "Authorization": _basic_auth_str(
                    default_netrc_username, default_netrc_password
                )
            }
        ).items()
    )

    # create netrc file
    # NOTE: write netrc file with DEFAULT_DOMAIN not DEFAULT_API_DOMAIN as can't
    #       handle /api/v1 in file
    netrc = netrc_file(machine=default_gitea_client.DEFAULT_DOMAIN)

    mocked_os_environ = {**clean_os_environment, "NETRC": netrc.name}

    # Monkeypatch to create the Mocked environment
    with requests_mock.Mocker(
        session=default_gitea_client.session
    ) as m, mock.patch.dict(os.environ, mocked_os_environ, clear=True):
        # mock the response
        m.register_uri(
            "POST", gitea_api_matcher, json={"id": expected_release_id}, status_code=201
        )

        # Execute method under test
        ret_val = default_gitea_client.create_release(tag, RELEASE_NOTES)

        # Evaluate (expected -> actual)
        assert expected_release_id == ret_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()

        # calculate the match between expected and actual headers
        # We are not looking for an exact match, just that the headers we must have exist
        shared_headers = expected_request_headers.intersection(
            set(m.last_request.headers.items())
        )
        assert expected_request_headers == shared_headers, str.join(
            os.linesep,
            [
                "Actual headers are missing some of the expected headers",
                f"Matching: {shared_headers}",
                f"Missing: {expected_request_headers - shared_headers}",
                f"Extra: {set(m.last_request.headers.items()) - expected_request_headers}",
            ],
        )


def test_request_has_no_auth_header_if_no_token_or_netrc():
    tag = "v1.0.0"
    expected_release_id = 1
    expected_num_requests = 1
    expected_http_method = "POST"

    with mock.patch.dict(os.environ, {}, clear=True):
        client = Gitea(remote_url=f"git@{Gitea.DEFAULT_DOMAIN}:something/somewhere.git")

        expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
            api_url=client.api_url,
            owner=client.owner,
            repo_name=client.repo_name,
        )

        with requests_mock.Mocker(session=client.session) as m:
            # mock the response
            m.register_uri("POST", gitea_api_matcher, json={"id": 1}, status_code=201)

            # Execute method under test
            ret_val = client.create_release(tag, RELEASE_NOTES)

            # Evaluate (expected -> actual)
            assert expected_release_id == ret_val
            assert m.called
            assert expected_num_requests == len(m.request_history)
            assert expected_http_method == m.last_request.method
            assert expected_request_url == m.last_request.url
            assert "Authorization" not in m.last_request.headers


@pytest.mark.parametrize(
    "resp_payload, status_code, expected_result",
    [
        ({"id": 420}, 200, 420),
        ({}, 404, None),
    ],
)
def test_get_release_id_by_tag(
    default_gitea_client: Gitea,
    resp_payload: dict[str, int],
    status_code: int,
    expected_result: int | None,
):
    # Setup
    tag = "v1.0.0"
    expected_num_requests = 1
    expected_http_method = "GET"
    expected_request_url = (
        "{api_url}/repos/{owner}/{repo_name}/releases/tags/{tag}".format(
            api_url=default_gitea_client.api_url,
            owner=default_gitea_client.owner,
            repo_name=default_gitea_client.repo_name,
            tag=tag,
        )
    )

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "GET", gitea_api_matcher, json=resp_payload, status_code=status_code
        )

        # Execute method under test
        rtn_val = default_gitea_client.get_release_id_by_tag(tag)

        # Evaluate (expected -> actual)
        assert expected_result == rtn_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url


@pytest.mark.parametrize("status_code", [201])
@pytest.mark.parametrize("mock_release_id", range(3))
def test_edit_release_notes_succeeds(
    default_gitea_client: Gitea,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    expected_num_requests = 1
    expected_http_method = "PATCH"
    expected_request_url = (
        "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
            api_url=default_gitea_client.api_url,
            owner=default_gitea_client.owner,
            repo_name=default_gitea_client.repo_name,
            release_id=mock_release_id,
        )
    )
    expected_request_body = {"body": RELEASE_NOTES}

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "PATCH",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test
        rtn_val = default_gitea_client.edit_release_notes(
            mock_release_id, RELEASE_NOTES
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == rtn_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
def test_edit_release_notes_fails(
    default_gitea_client: Gitea,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    expected_num_requests = 1
    expected_http_method = "PATCH"
    expected_request_url = (
        "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
            api_url=default_gitea_client.api_url,
            owner=default_gitea_client.owner,
            repo_name=default_gitea_client.repo_name,
            release_id=mock_release_id,
        )
    )
    expected_request_body = {"body": RELEASE_NOTES}

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "PATCH",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test expecting an exception to be raised
        with pytest.raises(HTTPError):
            default_gitea_client.edit_release_notes(mock_release_id, RELEASE_NOTES)

        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


# Note - mocking as the logic for the create/update of a release
# is covered by testing above, no point re-testing.


@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(
    default_gitea_client: Gitea,
    mock_release_id: int,
    prerelease: bool,
):
    tag = "v1.0.0"
    with mock.patch.object(
        default_gitea_client,
        default_gitea_client.create_release.__name__,
        return_value=mock_release_id,
    ) as mock_create_release, mock.patch.object(
        default_gitea_client,
        default_gitea_client.get_release_id_by_tag.__name__,
        return_value=mock_release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client,
        default_gitea_client.edit_release_notes.__name__,
        return_value=mock_release_id,
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gitea_client.create_or_update_release(
            tag, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == result
        mock_create_release.assert_called_once_with(tag, RELEASE_NOTES, prerelease)
        mock_get_release_id_by_tag.assert_not_called()
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_succeeds(
    default_gitea_client: Gitea,
    mock_release_id: int,
    prerelease: bool,
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found")
    not_found.response = Response()
    not_found.response.status_code = 404

    with mock.patch.object(
        default_gitea_client,
        default_gitea_client.create_release.__name__,
        side_effect=not_found,
    ) as mock_create_release, mock.patch.object(
        default_gitea_client,
        default_gitea_client.get_release_id_by_tag.__name__,
        return_value=mock_release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client,
        default_gitea_client.edit_release_notes.__name__,
        return_value=mock_release_id,
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gitea_client.create_or_update_release(
            tag, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == result
        mock_create_release.assert_called_once()
        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_called_once_with(mock_release_id, RELEASE_NOTES)


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_no_release_for_tag(
    default_gitea_client: Gitea,
    prerelease: bool,
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found")
    not_found.response = Response()
    not_found.response.status_code = 404

    with mock.patch.object(
        default_gitea_client,
        default_gitea_client.create_release.__name__,
        side_effect=not_found,
    ) as mock_create_release, mock.patch.object(
        default_gitea_client,
        default_gitea_client.get_release_id_by_tag.__name__,
        return_value=None,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client,
        default_gitea_client.edit_release_notes.__name__,
        return_value=None,
    ) as mock_edit_release_notes:
        # Execute in mock environment expecting an exception to be raised
        with pytest.raises(ValueError):
            default_gitea_client.create_or_update_release(
                tag, RELEASE_NOTES, prerelease
            )

        mock_create_release.assert_called_once()
        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("status_code", (200, 201))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.usefixtures(init_example_project.__name__)
def test_upload_release_asset_succeeds(
    default_gitea_client: Gitea,
    example_changelog_md: Path,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    urlparams = {"name": example_changelog_md.name}
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{url}?{params}".format(
        url=default_gitea_client.asset_upload_url(mock_release_id),
        params=urlencode(urlparams),
    )
    expected_changelog = example_changelog_md.read_bytes()

    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "POST", gitea_api_matcher, json={"status": "ok"}, status_code=status_code
        )
        result = default_gitea_client.upload_release_asset(
            release_id=mock_release_id,
            file=example_changelog_md.resolve(),
            label="doesn't matter could be None",
        )

        # Evaluate (expected -> actual)
        assert result is True
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_changelog in m.last_request.body


@pytest.mark.parametrize("status_code", (400, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.usefixtures(init_example_project.__name__)
def test_upload_release_asset_fails(
    default_gitea_client: Gitea,
    example_changelog_md: Path,
    status_code: int,
    mock_release_id: int,
):
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        # mock the response
        m.register_uri(
            "POST", gitea_api_matcher, json={"status": "error"}, status_code=status_code
        )

        # Execute method under test expecting an exception to be raised
        with pytest.raises(HTTPError):
            default_gitea_client.upload_release_asset(
                release_id=mock_release_id,
                file=example_changelog_md.resolve(),
                label="doesn't matter could be None",
            )


# Note - mocking as the logic for uploading an asset
# is covered by testing above, no point re-testing.
def test_upload_dists_when_release_id_not_found(default_gitea_client: Gitea):
    tag = "v1.0.0"
    path = "doesn't matter"
    expected_num_uploads = 0

    # Set up mock environment
    with mock.patch.object(
        default_gitea_client,
        default_gitea_client.get_release_id_by_tag.__name__,
        return_value=None,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, default_gitea_client.upload_release_asset.__name__
    ) as mock_upload_release_asset:
        # Execute method under test
        result = default_gitea_client.upload_dists(tag, path)

        # Evaluate
        assert expected_num_uploads == result
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        mock_upload_release_asset.assert_not_called()


@pytest.mark.parametrize(
    "files, glob_pattern, upload_statuses, expected_num_uploads",
    [
        (["foo.zip", "bar.whl"], "*.zip", [True], 1),
        (["foo.whl", "foo.egg", "foo.tar.gz"], "foo.*", [True, True, True], 3),
        # What if not built?
        ([], "*", [], 0),
        # What if wrong directory/other stuff in output dir/subfolder?
        (["specialconfig.yaml", "something.whl", "desc.md"], "*.yaml", [True], 1),
        (["specialconfig.yaml", "something.whl", "desc.md"], "*.md", [True], 1),
    ],
)
def test_upload_dists_when_release_id_found(
    default_gitea_client: Gitea,
    files: list[str],
    glob_pattern: str,
    upload_statuses: list[bool],
    expected_num_uploads: int,
):
    release_id = 420
    tag = "doesn't matter"
    matching_files = fnmatch.filter(files, glob_pattern)
    expected_files_uploaded = [mock.call(release_id, fn) for fn in matching_files]

    # Skip check as the files don't exist in filesystem
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=matching_files)

    # Set up mock environment
    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gitea_client,
        default_gitea_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client,
        default_gitea_client.upload_release_asset.__name__,
        side_effect=upload_statuses,
    ) as mock_upload_release_asset:
        # Execute method under test
        num_uploads = default_gitea_client.upload_dists(tag, glob_pattern)

        # Evaluate (expected -> actual)
        assert expected_num_uploads == num_uploads
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        assert expected_files_uploaded == mock_upload_release_asset.call_args_list
