from __future__ import annotations

import os
from unittest import mock

import pytest

from semantic_release.hvcs.bitbucket import Bitbucket

from tests.const import EXAMPLE_HVCS_DOMAIN, EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER


@pytest.fixture
def default_bitbucket_client():
    remote_url = (
        f"git@{Bitbucket.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    )
    return Bitbucket(remote_url=remote_url)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "patched_os_environ",
            "hvcs_domain",
            "hvcs_api_domain",
            "expected_hvcs_domain",
            "expected_api_url",
            "insecure",
        ],
    ),
    [
        # No env vars as CI is handled by Bamboo or Jenkins (which require user defined defaults)
        # API paths are different in BitBucket Cloud (bitbucket.org) vs BitBucket Data Center
        (
            # Default values (BitBucket Cloud)
            {},
            None,
            None,
            f"https://{Bitbucket.DEFAULT_DOMAIN}",
            Bitbucket.DEFAULT_API_URL_CLOUD,
            False,
        ),
        (
            # Explicitly set default values
            {},
            Bitbucket.DEFAULT_DOMAIN,
            Bitbucket.DEFAULT_API_URL_CLOUD,
            f"https://{Bitbucket.DEFAULT_DOMAIN}",
            Bitbucket.DEFAULT_API_URL_CLOUD,
            False,
        ),
        (
            # Explicitly set custom values with full api path
            {},
            EXAMPLE_HVCS_DOMAIN,
            f"{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            False,
        ),
        (
            # Explicitly defined api as subdomain
            # POSSIBLY WRONG ASSUMPTION of Api path for BitBucket Server
            {},
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://api.{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://api.{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            False,
        ),
        (
            # Custom domain for on premise BitBucket Server (derive api endpoint)
            {},
            EXAMPLE_HVCS_DOMAIN,
            None,
            f"https://{EXAMPLE_HVCS_DOMAIN}",
            f"https://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            False,
        ),
        (
            # Custom domain with path prefix
            {},
            "special.custom.server/bitbucket",
            None,
            "https://special.custom.server/bitbucket",
            "https://special.custom.server/bitbucket/rest/api/1.0",
            False,
        ),
        (
            # Allow insecure http connections explicitly
            {},
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            True,
        ),
        (
            # Allow insecure http connections explicitly & imply insecure api domain
            {},
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            None,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            True,
        ),
        (
            # Infer insecure connection from user configuration
            {},
            EXAMPLE_HVCS_DOMAIN,
            f"{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            True,
        ),
        (
            # Infer insecure connection from user configuration & imply insecure api domain
            {},
            EXAMPLE_HVCS_DOMAIN,
            None,
            f"http://{EXAMPLE_HVCS_DOMAIN}",
            f"http://{EXAMPLE_HVCS_DOMAIN}/rest/api/1.0",
            True,
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@{Bitbucket.DEFAULT_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://{Bitbucket.DEFAULT_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_bitbucket_client_init(
    patched_os_environ: dict[str, str],
    hvcs_domain: str | None,
    hvcs_api_domain: str | None,
    expected_hvcs_domain: str,
    expected_api_url: str,
    remote_url: str,
    token: str | None,
    insecure: bool,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Bitbucket(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
            allow_insecure=insecure,
        )

        assert expected_hvcs_domain == str(client.hvcs_domain)
        assert expected_api_url == str(client.api_url)
        assert token == client.token
        assert remote_url == client._remote_url


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
def test_bitbucket_client_init_with_invalid_scheme(
    hvcs_domain: str | None,
    hvcs_api_domain: str | None,
    insecure: bool,
):
    with pytest.raises(ValueError), mock.patch.dict(os.environ, {}, clear=True):
        Bitbucket(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            allow_insecure=insecure,
        )


@pytest.mark.parametrize(
    "patched_os_environ, expected_owner, expected_name",
    [
        ({}, None, None),
        ({"BITBUCKET_REPO_FULL_NAME": "path/to/repo/foo"}, "path/to/repo", "foo"),
    ],
)
def test_bitbucket_get_repository_owner_and_name(
    default_bitbucket_client: Bitbucket,
    patched_os_environ: dict[str, str],
    expected_owner: str,
    expected_name: str,
):
    # expected results should be a tuple[namespace, repo_name]
    # when None, the default values are used which matches default_bitbucket_client's setup
    expected_result = (
        expected_owner or EXAMPLE_REPO_OWNER,
        expected_name or EXAMPLE_REPO_NAME,
    )

    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        # Execute in mocked environment
        result = default_bitbucket_client._get_repository_owner_and_name()

        # Evaluate (expected -> actual)
        assert expected_result == result


def test_compare_url(default_bitbucket_client: Bitbucket):
    start_rev = "revA"
    end_rev = "revB"
    expected_url = (
        "{server}/{owner}/{repo}/branches/compare/{from_rev}%0D{to_rev}".format(
            server=default_bitbucket_client.hvcs_domain.url,
            owner=default_bitbucket_client.owner,
            repo=default_bitbucket_client.repo_name,
            from_rev=start_rev,
            to_rev=end_rev,
        )
    )
    actual_url = default_bitbucket_client.compare_url(
        from_rev=start_rev, to_rev=end_rev
    )
    assert expected_url == actual_url


@pytest.mark.parametrize(
    "patched_os_environ, use_token, token, remote_url, expected_auth_url",
    [
        (
            {"BITBUCKET_USER": "foo"},
            False,
            "",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {},
            False,
            "aabbcc",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {},
            True,
            "aabbcc",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
            f"https://x-token-auth:aabbcc@{Bitbucket.DEFAULT_DOMAIN}/custom/example.git",
        ),
        (
            {"BITBUCKET_USER": "foo"},
            False,
            "aabbcc",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
        ),
        (
            {"BITBUCKET_USER": "foo"},
            True,
            "aabbcc",
            f"git@{Bitbucket.DEFAULT_DOMAIN}:custom/example.git",
            f"https://foo:aabbcc@{Bitbucket.DEFAULT_DOMAIN}/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_bitbucket_client: Bitbucket,
    patched_os_environ: dict[str, str],
    use_token: bool,
    token: str,
    remote_url: str,
    expected_auth_url: str,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        default_bitbucket_client._remote_url = remote_url
        default_bitbucket_client.token = token
        assert expected_auth_url == default_bitbucket_client.remote_url(
            use_token=use_token
        )


def test_commit_hash_url(default_bitbucket_client: Bitbucket):
    sha = "244f7e11bcb1e1ce097db61594056bc2a32189a0"
    expected_url = "{server}/{owner}/{repo}/commits/{sha}".format(
        server=default_bitbucket_client.hvcs_domain,
        owner=default_bitbucket_client.owner,
        repo=default_bitbucket_client.repo_name,
        sha=sha,
    )
    assert expected_url == default_bitbucket_client.commit_hash_url(sha)


def test_commit_hash_url_w_custom_server():
    """
    Test the commit hash URL generation for a self-hosted Bitbucket server with prefix.

    ref: https://github.com/python-semantic-release/python-semantic-release/issues/1204
    """
    sha = "244f7e11bcb1e1ce097db61594056bc2a32189a0"
    expected_url = "{server}/{owner}/{repo}/commits/{sha}".format(
        server=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        owner="foo",
        repo=EXAMPLE_REPO_NAME,
        sha=sha,
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        actual_url = Bitbucket(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo/foo/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        ).commit_hash_url(sha)

    assert expected_url == actual_url


@pytest.mark.parametrize("pr_number", (666, "666", "#666"))
def test_pull_request_url(default_bitbucket_client: Bitbucket, pr_number: int | str):
    expected_url = "{server}/{owner}/{repo}/pull-requests/{pr_number}".format(
        server=default_bitbucket_client.hvcs_domain,
        owner=default_bitbucket_client.owner,
        repo=default_bitbucket_client.repo_name,
        pr_number=str(pr_number).lstrip("#"),
    )
    actual_url = default_bitbucket_client.pull_request_url(pr_number=pr_number)
    assert expected_url == actual_url
