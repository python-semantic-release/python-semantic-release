import os
from unittest import mock

import pytest
from requests import Session

from semantic_release.hvcs.bitbucket import Bitbucket

from tests.const import EXAMPLE_HVCS_DOMAIN, EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER


@pytest.fixture
def default_bitbucket_client():
    remote_url = f"git@bitbucket.org:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    return Bitbucket(remote_url=remote_url)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "patched_os_environ",
            "hvcs_domain",
            "hvcs_api_domain",
            "expected_hvcs_domain",
            "expected_hvcs_api_domain",
        ],
    ),
    [
        # Default values (BitBucket Cloud)
        ({}, None, None, Bitbucket.DEFAULT_DOMAIN, Bitbucket.DEFAULT_API_DOMAIN),
        (
            # Explicitly set default values
            {},
            f"https://{Bitbucket.DEFAULT_DOMAIN}",
            f"https://{Bitbucket.DEFAULT_API_DOMAIN}",
            Bitbucket.DEFAULT_DOMAIN,
            Bitbucket.DEFAULT_API_DOMAIN
        ),
        (
            # Explicitly defined api
            {},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://api.{EXAMPLE_HVCS_DOMAIN}",
            EXAMPLE_HVCS_DOMAIN,
            f"api.{EXAMPLE_HVCS_DOMAIN}",
        ),
        (
            # Custom domain for on premise BitBucket Server (derive api endpoint)
            # No env vars as CI is handled by Bamboo or Jenkins Integration
            {},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            None,
            EXAMPLE_HVCS_DOMAIN,
            EXAMPLE_HVCS_DOMAIN,
        ),
        (
            # Custom domain with path prefix
            # No env vars as CI is handled by Bamboo or Jenkins (which require user defined defaults)
            {},
            "special.custom.server/bitbucket",
            None,
            "special.custom.server/bitbucket",
            "special.custom.server/bitbucket",
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@bitbucket.org:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://bitbucket.org/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_bitbucket_client_init(
    patched_os_environ,
    hvcs_domain,
    hvcs_api_domain,
    expected_hvcs_domain,
    expected_hvcs_api_domain,
    remote_url,
    token,
):
    # API paths are different in BitBucket Cloud (bitbucket.org) vs BitBucket Data Center
    expected_api_url = (
        f"https://{expected_hvcs_api_domain}/2.0"
        if expected_hvcs_domain == "bitbucket.org"
        else f"https://{expected_hvcs_api_domain}/rest/api/1.0"
    )

    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Bitbucket(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
        )

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
        ({"BITBUCKET_REPO_FULL_NAME": "path/to/repo/foo"}, "path/to/repo", "foo"),
    ],
)
def test_bitbucket_get_repository_owner_and_name(
    default_bitbucket_client, patched_os_environ, expected_owner, expected_name
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        if expected_owner is None and expected_name is None:
            assert (
                default_bitbucket_client._get_repository_owner_and_name()
                == super(
                    Bitbucket, default_bitbucket_client
                )._get_repository_owner_and_name()
            )
        else:
            assert default_bitbucket_client._get_repository_owner_and_name() == (
                expected_owner,
                expected_name,
            )


def test_compare_url(default_bitbucket_client):
    assert default_bitbucket_client.compare_url(
        from_rev="revA", to_rev="revB"
    ) == "https://{domain}/{owner}/{repo}/branches/compare/revA%0DrevB".format(
        domain=default_bitbucket_client.hvcs_domain,
        owner=default_bitbucket_client.owner,
        repo=default_bitbucket_client.repo_name,
    )


@pytest.mark.parametrize(
    "patched_os_environ, use_token, token, _remote_url, expected",
    [
        (
            {"BITBUCKET_USER": "foo"},
            False,
            "",
            "git@bitbucket.org:custom/example.git",
            "git@bitbucket.org:custom/example.git",
        ),
        (
            {},
            False,
            "aabbcc",
            "git@bitbucket.org:custom/example.git",
            "git@bitbucket.org:custom/example.git",
        ),
        (
            {},
            True,
            "aabbcc",
            "git@bitbucket.org:custom/example.git",
            "https://x-token-auth:aabbcc@bitbucket.org/custom/example.git",
        ),
        (
            {"BITBUCKET_USER": "foo"},
            False,
            "aabbcc",
            "git@bitbucket.org:custom/example.git",
            "git@bitbucket.org:custom/example.git",
        ),
        (
            {"BITBUCKET_USER": "foo"},
            True,
            "aabbcc",
            "git@bitbucket.org:custom/example.git",
            "https://foo:aabbcc@bitbucket.org/custom/example.git",
        ),
    ],
)
def test_remote_url(
    patched_os_environ,
    use_token,
    token,
    _remote_url,  # noqa: PT019
    expected,
    default_bitbucket_client,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        default_bitbucket_client._remote_url = _remote_url
        default_bitbucket_client.token = token
        assert default_bitbucket_client.remote_url(use_token=use_token) == expected


def test_commit_hash_url(default_bitbucket_client):
    sha = "244f7e11bcb1e1ce097db61594056bc2a32189a0"
    assert default_bitbucket_client.commit_hash_url(
        sha
    ) == "https://{domain}/{owner}/{repo}/commits/{sha}".format(
        domain=default_bitbucket_client.hvcs_domain,
        owner=default_bitbucket_client.owner,
        repo=default_bitbucket_client.repo_name,
        sha=sha,
    )


@pytest.mark.parametrize("pr_number", (420, "420"))
def test_pull_request_url(default_bitbucket_client, pr_number):
    assert default_bitbucket_client.pull_request_url(
        pr_number=pr_number
    ) == "https://{domain}/{owner}/{repo}/pull-requests/{pr_number}".format(
        domain=default_bitbucket_client.hvcs_domain,
        owner=default_bitbucket_client.owner,
        repo=default_bitbucket_client.repo_name,
        pr_number=pr_number,
    )
