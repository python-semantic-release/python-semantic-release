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

from semantic_release.errors import AssetUploadError
from semantic_release.hvcs.github import Github
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
def default_gh_client() -> Generator[Github, None, None]:
    remote_url = (
        f"git@{Github.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    )
    with mock.patch.dict(os.environ, {}, clear=True):
        yield Github(remote_url=remote_url)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "patched_os_environ",
            "hvcs_domain",
            "hvcs_api_domain",
            "expected_hvcs_domain",
            "expected_hvcs_api_url",
            "insecure",
        ],
    ),
    [
        (
            # Default values (GitHub Enterprise Cloud)
            {},
            None,
            None,
            "https://github.com",
            "https://api.github.com",
            False,
        ),
        (
            # Explicitly set default values (GitHub Enterprise Cloud)
            {},
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            "https://github.com",
            "https://api.github.com",
            False,
        ),
        (
            # Pull both locations from environment (GitHub Actions on Cloud)
            {
                "GITHUB_SERVER_URL": f"https://{Github.DEFAULT_DOMAIN}",
                "GITHUB_API_URL": f"https://{Github.DEFAULT_API_DOMAIN}",
            },
            None,
            None,
            "https://github.com",
            "https://api.github.com",
            False,
        ),
        (
            # Explicitly set custom values with full api path
            {},
            EXAMPLE_HVCS_DOMAIN,
            f"{EXAMPLE_HVCS_DOMAIN}{Github.DEFAULT_API_PATH_ONPREM}",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}{Github.DEFAULT_API_PATH_ONPREM}",
            False,
        ),
        (
            # Explicitly defined api as subdomain
            # POSSIBLY WRONG ASSUMPTION of Api path for GitHub Enterprise Server (On Prem)
            {},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://api.{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://api.{EXAMPLE_HVCS_DOMAIN}{Github.DEFAULT_API_PATH_ONPREM}",
            False,
        ),
        (
            # Custom domain with path prefix
            {},
            "special.custom.server/vcs",
            None,
            "https://special.custom.server/vcs",
            "https://special.custom.server/vcs/api/v3",
            False,
        ),
        (
            # Gather domain from environment & imply api domain from server domain
            {"GITHUB_SERVER_URL": "https://special.custom.server/"},
            None,
            None,
            "https://special.custom.server",
            "https://special.custom.server/api/v3",
            False,
        ),
        (
            # Pull both locations from environment (On-prem Actions Env)
            {
                "GITHUB_SERVER_URL": "https://special.custom.server/",
                "GITHUB_API_URL": "https://special.custom.server/api/v3",
            },
            None,
            None,
            "https://special.custom.server",
            "https://special.custom.server/api/v3",
            False,
        ),
        (
            # Ignore environment & use provided parameter value (ie from user config)
            # then infer api domain from the parameter value based on default GitHub configurations
            {"GITHUB_SERVER_URL": "https://special.custom.server/vcs/"},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            None,
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            False,
        ),
        (
            # Ignore environment & use provided parameter value (ie from user config)
            {"GITHUB_API_URL": "https://api.special.custom.server/"},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            False,
        ),
        (
            # Allow insecure http connections explicitly
            {},
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            True,
        ),
        (
            # Allow insecure http connections explicitly & imply insecure api domain
            {},
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            None,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            True,
        ),
        (
            # Infer insecure connection from user configuration
            {},
            EXAMPLE_HVCS_DOMAIN,
            EXAMPLE_HVCS_DOMAIN,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            True,
        ),
        (
            # Infer insecure connection from user configuration & imply insecure api domain
            {},
            EXAMPLE_HVCS_DOMAIN,
            None,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/api/v3",
            True,
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@{Github.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://{Github.DEFAULT_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_github_client_init(
    patched_os_environ: dict[str, str],
    hvcs_domain: str | None,
    hvcs_api_domain: str | None,
    expected_hvcs_domain: str,
    expected_hvcs_api_url: str,
    remote_url: str,
    token: str | None,
    insecure: bool,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Github(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
            allow_insecure=insecure,
        )

        # Evaluate (expected -> actual)
        assert expected_hvcs_domain == str(client.hvcs_domain)
        assert expected_hvcs_api_url == str(client.api_url)
        assert token == client.token
        assert remote_url == client._remote_url
        assert hasattr(client, "session")
        assert isinstance(getattr(client, "session", None), Session)


@pytest.mark.parametrize(
    "hvcs_domain, hvcs_api_domain, insecure",
    [
        # Bad base domain schemes
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", None, False),
        (f"ftp://{EXAMPLE_HVCS_DOMAIN}", None, True),
        # Unallowed insecure connections when base domain is insecure
        (f"http://{EXAMPLE_HVCS_DOMAIN}", None, False),
        # Bad API domain schemes
        (None, f"ftp://api.{EXAMPLE_HVCS_DOMAIN}", False),
        (None, f"ftp://api.{EXAMPLE_HVCS_DOMAIN}", True),
        # Unallowed insecure connections when api domain is insecure
        (None, f"http://{EXAMPLE_HVCS_DOMAIN}", False),
    ],
)
def test_github_client_init_with_invalid_scheme(
    hvcs_domain: str | None,
    hvcs_api_domain: str | None,
    insecure: bool,
):
    with pytest.raises(ValueError), mock.patch.dict(os.environ, {}, clear=True):
        Github(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            allow_insecure=insecure,
        )


@pytest.mark.parametrize(
    "patched_os_environ, expected_owner, expected_name",
    [
        ({}, None, None),
        ({"GITHUB_REPOSITORY": "path/to/repo/foo"}, "path/to/repo", "foo"),
    ],
)
def test_github_get_repository_owner_and_name(
    default_gh_client: Github,
    patched_os_environ: dict[str, str],
    expected_owner: str,
    expected_name: str,
):
    # expected results should be a tuple[namespace, repo_name]
    # when None, the default values are used which matches default_gh_client's setup
    expected_result = (
        expected_owner or EXAMPLE_REPO_OWNER,
        expected_name or EXAMPLE_REPO_NAME,
    )

    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        # Execute in mocked environment
        result = default_gh_client._get_repository_owner_and_name()

        # Evaluate (expected -> actual)
        assert expected_result == result


def test_compare_url(default_gh_client: Github):
    # Setup
    start_rev = "revA"
    end_rev = "revB"
    expected_url = "{server}/{owner}/{repo}/compare/{from_rev}...{to_rev}".format(
        server=default_gh_client.hvcs_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        from_rev=start_rev,
        to_rev=end_rev,
    )

    # Execute method under test
    actual_url = default_gh_client.compare_url(from_rev=start_rev, to_rev=end_rev)

    # Evaluate (expected -> actual)
    assert expected_url == actual_url


@pytest.mark.parametrize(
    "patched_os_environ, use_token, token, remote_url, expected_auth_url",
    [
        (
            {"GITHUB_ACTOR": "foo"},
            False,
            "",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            True,
            "",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {},
            False,
            "aabbcc",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {},
            True,
            "aabbcc",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"https://aabbcc@{Github.DEFAULT_DOMAIN}/custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            False,
            "aabbcc",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            True,
            "aabbcc",
            f"git@{Github.DEFAULT_DOMAIN}:custom/example.git",
            f"https://foo:aabbcc@{Github.DEFAULT_DOMAIN}/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gh_client: Github,
    patched_os_environ: dict[str, str],
    use_token: bool,
    token: str,
    remote_url: str,
    expected_auth_url: str,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        default_gh_client._remote_url = remote_url
        default_gh_client.token = token

        # Execute method under test & Evaluate (expected -> actual)
        assert expected_auth_url == default_gh_client.remote_url(use_token=use_token)


def test_commit_hash_url(default_gh_client: Github):
    sha = "hashashash"
    expected_url = "{server}/{owner}/{repo}/commit/{sha}".format(
        server=default_gh_client.hvcs_domain.url,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        sha=sha,
    )
    assert expected_url == default_gh_client.commit_hash_url(sha)


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
        actual_url = Github(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo/foo/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        ).commit_hash_url(sha)

    assert expected_url == actual_url


@pytest.mark.parametrize("issue_number", (666, "666", "#666"))
def test_issue_url(default_gh_client: Github, issue_number: str | int):
    expected_url = "{server}/{owner}/{repo}/issues/{issue_num}".format(
        server=default_gh_client.hvcs_domain.url,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        issue_num=str(issue_number).lstrip("#"),
    )
    assert expected_url == default_gh_client.issue_url(issue_num=issue_number)


@pytest.mark.parametrize("pr_number", (666, "666", "#666"))
def test_pull_request_url(default_gh_client: Github, pr_number: int | str):
    expected_url = "{server}/{owner}/{repo}/pull/{pr_number}".format(
        server=default_gh_client.hvcs_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        pr_number=str(pr_number).lstrip("#"),
    )
    actual_url = default_gh_client.pull_request_url(pr_number=pr_number)
    assert expected_url == actual_url


############
# Tests which need http response mocking
############


github_upload_url = f"https://uploads.{Github.DEFAULT_DOMAIN}"
github_matcher = re.compile(rf"^https://{Github.DEFAULT_DOMAIN}")
github_api_matcher = re.compile(rf"^https://{Github.DEFAULT_API_DOMAIN}")
github_upload_matcher = re.compile(rf"^{github_upload_url}")


@pytest.mark.parametrize("status_code", (200, 201))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_succeeds(
    default_gh_client: Github,
    mock_release_id: int,
    prerelease: bool,
    status_code: int,
):
    tag = "v1.0.0"
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gh_client.api_url,
        owner=default_gh_client.owner,
        repo_name=default_gh_client.repo_name,
    )
    expected_request_body = {
        "tag_name": tag,
        "name": tag,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": prerelease,
    }

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            github_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test
        actual_rtn_val = default_gh_client.create_release(
            tag, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == actual_rtn_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_fails(
    default_gh_client: Github,
    mock_release_id: int,
    prerelease: bool,
    status_code: int,
):
    tag = "v1.0.0"
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gh_client.api_url,
        owner=default_gh_client.owner,
        repo_name=default_gh_client.repo_name,
    )
    expected_request_body = {
        "tag_name": tag,
        "name": tag,
        "body": RELEASE_NOTES,
        "draft": False,
        "prerelease": prerelease,
    }

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            github_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test expecting an exeception to be raised
        with pytest.raises(HTTPError):
            default_gh_client.create_release(tag, RELEASE_NOTES, prerelease)

        # Evaluate (expected -> actual)
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize("token", (None, "super-token"))
def test_should_create_release_using_token_or_netrc(
    default_gh_client: Github,
    token: str | None,
    default_netrc_username: str,
    default_netrc_password: str,
    netrc_file: NetrcFileFn,
    clean_os_environment: dict[str, str],
):
    # Setup
    default_gh_client.token = token
    default_gh_client.session.auth = None if not token else TokenAuth(token)
    tag = "v1.0.0"
    expected_release_id = 1
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=default_gh_client.api_url,
        owner=default_gh_client.owner,
        repo_name=default_gh_client.repo_name,
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
    netrc = netrc_file(machine=default_gh_client.DEFAULT_API_DOMAIN)

    mocked_os_environ = {**clean_os_environment, "NETRC": netrc.name}

    # Monkeypatch to create the Mocked environment
    with requests_mock.Mocker(session=default_gh_client.session) as m, mock.patch.dict(
        os.environ, mocked_os_environ, clear=True
    ):
        # mock the response
        m.register_uri(
            "POST",
            github_api_matcher,
            json={"id": expected_release_id},
            status_code=201,
        )

        # Execute method under test
        ret_val = default_gh_client.create_release(tag, RELEASE_NOTES)

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
        client = Github(
            remote_url=f"git@{Github.DEFAULT_DOMAIN}:something/somewhere.git"
        )

        expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
            api_url=client.api_url,
            owner=client.owner,
            repo_name=client.repo_name,
        )

        with requests_mock.Mocker(session=client.session) as m:
            # mock the response
            m.register_uri("POST", github_api_matcher, json={"id": 1}, status_code=201)

            # Execute method under test
            rtn_val = client.create_release(tag, RELEASE_NOTES)

            # Evaluate (expected -> actual)
            assert expected_release_id == rtn_val
            assert m.called
            assert expected_num_requests == len(m.request_history)
            assert expected_http_method == m.last_request.method
            assert expected_request_url == m.last_request.url
            assert "Authorization" not in m.last_request.headers


@pytest.mark.parametrize("status_code", [201])
@pytest.mark.parametrize("mock_release_id", range(3))
def test_edit_release_notes_succeeds(
    default_gh_client: Github,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = (
        "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
            api_url=default_gh_client.api_url,
            owner=default_gh_client.owner,
            repo_name=default_gh_client.repo_name,
            release_id=mock_release_id,
        )
    )
    expected_request_body = {"body": RELEASE_NOTES}

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            github_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test
        rtn_val = default_gh_client.edit_release_notes(mock_release_id, RELEASE_NOTES)

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
    default_gh_client: Github, status_code: int, mock_release_id: int
):
    # Setup
    expected_num_requests = 1
    expected_http_method = "POST"
    expected_request_url = (
        "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
            api_url=default_gh_client.api_url,
            owner=default_gh_client.owner,
            repo_name=default_gh_client.repo_name,
            release_id=mock_release_id,
        )
    )
    expected_request_body = {"body": RELEASE_NOTES}

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri(
            "POST",
            github_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        # Execute method under test expecting an exception to be raised
        with pytest.raises(HTTPError):
            default_gh_client.edit_release_notes(mock_release_id, RELEASE_NOTES)

        # Evaluate (expected -> actual)
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url
        assert expected_request_body == m.last_request.json()


@pytest.mark.parametrize(
    "resp_payload, status_code, expected_result",
    [
        ({"id": 420, "status": "success"}, 200, 420),
        ({"error": "not found"}, 404, None),
        ({"error": "too many requests"}, 429, None),
        ({"error": "internal error"}, 500, None),
        ({"error": "temporarily unavailable"}, 503, None),
    ],
)
def test_get_release_id_by_tag(
    default_gh_client: Github,
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
            api_url=default_gh_client.api_url,
            owner=default_gh_client.owner,
            repo_name=default_gh_client.repo_name,
            tag=tag,
        )
    )

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri(
            "GET", github_api_matcher, json=resp_payload, status_code=status_code
        )

        # Execute method under test
        rtn_val = default_gh_client.get_release_id_by_tag(tag)

        # Evaluate (expected -> actual)
        assert expected_result == rtn_val
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_request_url == m.last_request.url


# Note - mocking as the logic for the create/update of a release
# is covered by testing above, no point re-testing.


@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(
    default_gh_client: Github,
    mock_release_id: int,
    prerelease: bool,
):
    tag = "v1.0.0"
    with mock.patch.object(
        default_gh_client,
        default_gh_client.create_release.__name__,
        return_value=mock_release_id,
    ) as mock_create_release, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=mock_release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client,
        default_gh_client.edit_release_notes.__name__,
        return_value=mock_release_id,
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gh_client.create_or_update_release(
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
    default_gh_client: Github,
    mock_release_id: int,
    prerelease: bool,
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found")
    not_found.response = Response()
    not_found.response.status_code = 404

    with mock.patch.object(
        default_gh_client,
        default_gh_client.create_release.__name__,
        side_effect=not_found,
    ) as mock_create_release, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=mock_release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client,
        default_gh_client.edit_release_notes.__name__,
        return_value=mock_release_id,
    ) as mock_edit_release_notes:
        # Execute in mock environment
        result = default_gh_client.create_or_update_release(
            tag, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        assert mock_release_id == result
        mock_create_release.assert_called_once()
        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_called_once_with(mock_release_id, RELEASE_NOTES)


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_no_release_for_tag(
    default_gh_client: Github,
    prerelease: bool,
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found")
    not_found.response = Response()
    not_found.response.status_code = 404

    with mock.patch.object(
        default_gh_client,
        default_gh_client.create_release.__name__,
        side_effect=not_found,
    ) as mock_create_release, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=None,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client,
        default_gh_client.edit_release_notes.__name__,
        return_value=None,
    ) as mock_edit_release_notes:
        # Execute in mock environment expecting an exception to be raised
        with pytest.raises(ValueError):
            default_gh_client.create_or_update_release(tag, RELEASE_NOTES, prerelease)

        mock_create_release.assert_called_once()
        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_not_called()


def test_asset_upload_url(default_gh_client: Github):
    release_id = 1
    expected_num_requests = 1
    expected_http_method = "GET"
    expected_asset_upload_request_url = (
        "{api_url}/repos/{owner}/{repo}/releases/{release_id}".format(
            api_url=default_gh_client.api_url,
            owner=default_gh_client.owner,
            repo=default_gh_client.repo_name,
            release_id=release_id,
        )
    )
    mocked_upload_url = (
        "{upload_domain}/repos/{owner}/{repo}/releases/{release_id}/assets".format(
            upload_domain=github_upload_url,
            owner=default_gh_client.owner,
            repo=default_gh_client.repo_name,
            release_id=release_id,
        )
    )
    # '{?name,label}' are added by github.com at least, maybe custom too
    # https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#get-a-release
    resp_payload = {
        "upload_url": mocked_upload_url + "{?name,label}",
        "status": "success",
    }

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the response
        m.register_uri("GET", github_api_matcher, json=resp_payload, status_code=200)

        # Execute method under test
        result = default_gh_client.asset_upload_url(release_id)

        # Evaluate (expected -> actual)
        assert mocked_upload_url == result
        assert m.called
        assert expected_num_requests == len(m.request_history)
        assert expected_http_method == m.last_request.method
        assert expected_asset_upload_request_url == m.last_request.url


@pytest.mark.parametrize("status_code", (200, 201))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.usefixtures(init_example_project.__name__)
def test_upload_release_asset_succeeds(
    default_gh_client: Github,
    example_changelog_md: Path,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    label = "abc123"
    urlparams = {"name": example_changelog_md.name, "label": label}
    release_upload_url = (
        "{upload_domain}/repos/{owner}/{repo}/releases/{release_id}/assets".format(
            upload_domain=github_upload_url,
            owner=default_gh_client.owner,
            repo=default_gh_client.repo_name,
            release_id=mock_release_id,
        )
    )
    expected_num_requests = 2
    expected_retrieve_upload_url_method = "GET"
    expected_upload_http_method = "POST"
    expected_upload_url = "{url}?{params}".format(
        url=release_upload_url,
        params=urlencode(urlparams),
    )
    expected_changelog = example_changelog_md.read_bytes()
    json_get_up_url = {
        "status": "ok",
        "upload_url": release_upload_url + "{?name,label}",
    }

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the responses
        m.register_uri(
            "POST",
            github_upload_matcher,
            json={"status": "ok"},
            status_code=status_code,
        )
        m.register_uri(
            "GET", github_api_matcher, json=json_get_up_url, status_code=status_code
        )

        # Execute method under test
        result = default_gh_client.upload_release_asset(
            release_id=mock_release_id,
            file=example_changelog_md.resolve(),
            label=label,
        )

        # Evaluate (expected -> actual)
        assert result is True
        assert m.called
        assert expected_num_requests == len(m.request_history)

        get_req, post_req = m.request_history

        assert expected_retrieve_upload_url_method == get_req.method
        assert expected_upload_http_method == post_req.method
        assert expected_upload_url == post_req.url
        assert expected_changelog == post_req.body


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.usefixtures(init_example_project.__name__)
def test_upload_release_asset_fails(
    default_gh_client: Github,
    example_changelog_md: Path,
    status_code: int,
    mock_release_id: int,
):
    # Setup
    label = "abc123"
    upload_url = "{up_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
        up_url=github_upload_url,
        owner=default_gh_client.owner,
        repo_name=default_gh_client.repo_name,
        release_id=mock_release_id,
    )
    json_get_up_url = {
        "status": "ok",
        "upload_url": upload_url,
    }

    with requests_mock.Mocker(session=default_gh_client.session) as m:
        # mock the responses
        m.register_uri(
            "POST",
            github_upload_matcher,
            json={"message": "error"},
            status_code=status_code,
        )
        m.register_uri("GET", github_api_matcher, json=json_get_up_url, status_code=200)

        # Execute method under test expecting an exception to be raised
        with pytest.raises(HTTPError):
            default_gh_client.upload_release_asset(
                release_id=mock_release_id,
                file=example_changelog_md.resolve(),
                label=label,
            )


# Note - mocking as the logic for uploading an asset
# is covered by testing above, no point re-testing.
def test_upload_dists_when_release_id_not_found(default_gh_client: Github):
    tag = "v1.0.0"
    path = "doesn't matter"
    expected_num_uploads = 0

    # Set up mock environment
    with mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=None,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client, default_gh_client.upload_release_asset.__name__
    ) as mock_upload_release_asset:
        # Execute method under test
        result = default_gh_client.upload_dists(tag, path)

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
    default_gh_client: Github,
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
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        side_effect=upload_statuses,
    ) as mock_upload_release_asset:
        # Execute method under test
        num_uploads = default_gh_client.upload_dists(tag, glob_pattern)

        # Evaluate (expected -> actual)
        assert expected_num_uploads == num_uploads
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        assert expected_files_uploaded == mock_upload_release_asset.call_args_list


@pytest.mark.parametrize(
    "status_code, error_message",
    [
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (400, "Bad Request"),
        (404, "Not Found"),
        (429, "Too Many Requests"),
        (500, "Internal Server Error"),
        (503, "Service Unavailable"),
    ],
)
def test_upload_dists_fails_with_http_error(
    default_gh_client: Github,
    status_code: int,
    error_message: str,
):
    """Given a release exists, when upload_release_asset raises HTTPError, then AssetUploadError is raised."""
    # Setup
    release_id = 123
    tag = "v1.0.0"
    files = ["dist/package-1.0.0.whl", "dist/package-1.0.0.tar.gz"]
    glob_pattern = "dist/*"
    expected_num_upload_attempts = len(files)

    # Create mock HTTPError with proper response
    http_error = HTTPError(error_message)
    http_error.response = Response()
    http_error.response.status_code = status_code
    http_error.response._content = error_message.encode()

    # Skip filesystem checks
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=files)

    # Set up mock environment
    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        side_effect=http_error,
    ) as mock_upload_release_asset:
        # Execute method under test expecting an exception to be raised
        with pytest.raises(AssetUploadError) as exc_info:
            default_gh_client.upload_dists(tag, glob_pattern)

        # Evaluate (expected -> actual)
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)

        # Should have attempted to upload all files even though they fail
        assert expected_num_upload_attempts == mock_upload_release_asset.call_count

        # Verify the error message contains useful information about failed uploads
        error_msg = str(exc_info.value)

        # Each file should be mentioned in the error message with status code
        for file in files:
            assert f"Failed to upload asset '{file}'" in error_msg
            assert f"(HTTP {status_code})" in error_msg


def test_upload_dists_fails_authentication_error_401(default_gh_client: Github):
    """Given a release exists, when upload fails with 401, then AssetUploadError is raised with auth context."""
    # Setup
    release_id = 456
    tag = "v2.0.0"
    files = ["dist/package-2.0.0.whl"]
    glob_pattern = "dist/*.whl"

    # Create mock HTTPError for authentication failure
    http_error = HTTPError("401 Client Error: Unauthorized")
    http_error.response = Response()
    http_error.response.status_code = 401
    http_error.response._content = b'{"message": "Bad credentials"}'

    # Skip filesystem checks
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=files)

    # Set up mock environment
    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ), mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        side_effect=http_error,
    ):
        # Execute method under test expecting an exception to be raised
        with pytest.raises(AssetUploadError) as exc_info:
            default_gh_client.upload_dists(tag, glob_pattern)

        # Verify the error message contains file, release information and status code
        error_msg = str(exc_info.value)
        assert "Failed to upload asset" in error_msg
        assert files[0] in error_msg
        assert "(HTTP 401)" in error_msg


def test_upload_dists_fails_forbidden_error_403(default_gh_client: Github):
    """Given a release exists, when upload fails with 403, then AssetUploadError is raised with permission context."""
    # Setup
    release_id = 789
    tag = "v3.0.0"
    files = ["dist/package-3.0.0.tar.gz"]
    glob_pattern = "dist/*.tar.gz"

    # Create mock HTTPError for forbidden access
    http_error = HTTPError("403 Client Error: Forbidden")
    http_error.response = Response()
    http_error.response.status_code = 403

    # Skip filesystem checks
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=files)

    # Set up mock environment
    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ), mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        side_effect=http_error,
    ):
        # Execute method under test expecting an exception to be raised
        with pytest.raises(AssetUploadError) as exc_info:
            default_gh_client.upload_dists(tag, glob_pattern)

        # Verify the error message contains file, release information and status code
        error_msg = str(exc_info.value)
        assert "Failed to upload asset" in error_msg
        assert f"Failed to upload asset '{files[0]}'" in error_msg
        assert "(HTTP 403)" in error_msg


def test_upload_dists_partial_failure(default_gh_client: Github):
    """Given multiple files to upload, when some succeed and some fail, then AssetUploadError is raised."""
    # Setup
    release_id = 999
    tag = "v4.0.0"
    files = [
        "dist/package-4.0.0.whl",
        "dist/package-4.0.0.tar.gz",
        "dist/package-4.0.0-py3-none-any.whl",
    ]
    glob_pattern = "dist/*"
    expected_num_upload_attempts = len(files)

    # Create mock HTTPError for the second file
    http_error = HTTPError("500 Server Error: Internal Server Error")
    http_error.response = Response()
    http_error.response.status_code = 500

    # Skip filesystem checks
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=files)

    # Set up mock environment - first upload succeeds, second fails, third fails
    upload_results = [True, http_error, http_error]

    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ), mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        side_effect=upload_results,
    ) as mock_upload_release_asset:
        # Execute method under test expecting an exception to be raised
        with pytest.raises(AssetUploadError) as exc_info:
            default_gh_client.upload_dists(tag, glob_pattern)

        # Verify all uploads were attempted
        assert expected_num_upload_attempts == mock_upload_release_asset.call_count

        # Verify the error message mentions the failed files with status code
        error_msg = str(exc_info.value)
        assert f"Failed to upload asset '{files[1]}'" in error_msg
        assert f"Failed to upload asset '{files[2]}'" in error_msg
        assert "(HTTP 500)" in error_msg


def test_upload_dists_all_succeed(default_gh_client: Github):
    """Given multiple files to upload, when all succeed, then return count of successful uploads."""
    # Setup
    release_id = 111
    tag = "v5.0.0"
    files = ["dist/package-5.0.0.whl", "dist/package-5.0.0.tar.gz"]
    glob_pattern = "dist/*"
    expected_num_uploads = len(files)

    # Skip filesystem checks
    mocked_isfile = mock.patch.object(os.path, "isfile", return_value=True)
    mocked_globber = mock.patch.object(glob, "glob", return_value=files)

    # Set up mock environment - all uploads succeed
    with mocked_globber, mocked_isfile, mock.patch.object(
        default_gh_client,
        default_gh_client.get_release_id_by_tag.__name__,
        return_value=release_id,
    ), mock.patch.object(
        default_gh_client,
        default_gh_client.upload_release_asset.__name__,
        return_value=True,
    ) as mock_upload_release_asset:
        # Execute method under test
        num_uploads = default_gh_client.upload_dists(tag, glob_pattern)

        # Evaluate (expected -> actual)
        assert expected_num_uploads == num_uploads
        assert expected_num_uploads == mock_upload_release_asset.call_count
