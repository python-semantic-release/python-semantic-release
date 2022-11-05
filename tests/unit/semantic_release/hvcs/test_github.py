import base64
import glob
import mimetypes
import os
import re
from unittest import mock
from urllib.parse import urlencode

import pytest
import requests_mock
from requests import Session

from semantic_release.hvcs.github import Github
from semantic_release.hvcs.token_auth import TokenAuth

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.helper import netrc_file


@pytest.fixture
def default_gh_client():
    remote_url = f"git@github.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    yield Github(remote_url=remote_url)


@pytest.mark.parametrize(
    (
        "patched_os_environ, hvcs_domain, hvcs_api_domain, token_var, "
        "expected_hvcs_domain, expected_hvcs_api_domain, expected_token"
    ),
    [
        ({}, None, None, "", Github.DEFAULT_DOMAIN, Github.DEFAULT_API_DOMAIN, None),
        (
            {"GITHUB_SERVER_URL": "https://special.custom.server/vcs/"},
            None,
            None,
            "",
            "special.custom.server/vcs/",
            Github.DEFAULT_API_DOMAIN,
            None,
        ),
        (
            {"GITHUB_API_URL": "https://api.special.custom.server/"},
            None,
            None,
            "",
            Github.DEFAULT_DOMAIN,
            "api.special.custom.server/",
            None,
        ),
        (
            {},
            None,
            None,
            "GH_TOKEN",
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            None,
        ),
        (
            {"GL_TOKEN": "abc123"},
            None,
            None,
            "GH_TOKEN",
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            None,
        ),
        (
            {"GITEA_TOKEN": "abc123"},
            None,
            None,
            "GH_TOKEN",
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            None,
        ),
        (
            {"GH_TOKEN": "aabbcc"},
            None,
            None,
            "GH_TOKEN",
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            "aabbcc",
        ),
        (
            {"PSR__GIT_TOKEN": "aabbcc"},
            None,
            None,
            "PSR__GIT_TOKEN",
            Github.DEFAULT_DOMAIN,
            Github.DEFAULT_API_DOMAIN,
            "aabbcc",
        ),
        (
            {"GITHUB_SERVER_URL": "https://special.custom.server/vcs/"},
            "https://example.com",
            None,
            "",
            "https://example.com",
            Github.DEFAULT_API_DOMAIN,
            None,
        ),
        (
            {"GITHUB_API_URL": "https://api.special.custom.server/"},
            None,
            "https://api.example.com",
            "",
            Github.DEFAULT_DOMAIN,
            "https://api.example.com",
            None,
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@github.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://github.com/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
def test_github_client_init(
    patched_os_environ,
    hvcs_domain,
    hvcs_api_domain,
    token_var,
    expected_hvcs_domain,
    expected_hvcs_api_domain,
    expected_token,
    remote_url,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Github(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token_var=token_var,
        )

        assert client.hvcs_domain == expected_hvcs_domain
        assert client.hvcs_api_domain == expected_hvcs_api_domain
        assert client.api_url == f"https://{client.hvcs_api_domain}"
        assert client.token == expected_token
        assert client._remote_url == remote_url
        assert hasattr(client, "session") and isinstance(
            getattr(client, "session", None), Session
        )


@pytest.mark.parametrize(
    "patched_os_environ, expected_owner, expected_name",
    [
        ({}, None, None),
        ({"GITHUB_REPOSITORY": "path/to/repo/foo"}, "path/to/repo", "foo"),
    ],
)
def test_github_get_repository_owner_and_name(
    default_gh_client, patched_os_environ, expected_owner, expected_name
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        if expected_owner is None and expected_name is None:
            assert (
                default_gh_client._get_repository_owner_and_name()
                == super(Github, default_gh_client)._get_repository_owner_and_name()
            )
        else:
            assert default_gh_client._get_repository_owner_and_name() == (
                expected_owner,
                expected_name,
            )


def test_compare_url(default_gh_client):
    assert default_gh_client.compare_url(
        from_rev="revA", to_rev="revB"
    ) == "https://{domain}/{owner}/{repo}/compare/revA...revB".format(
        domain=default_gh_client.hvcs_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
    )


@pytest.mark.parametrize(
    "patched_os_environ, use_token, token, _remote_url, expected",
    [
        (
            {"GITHUB_ACTOR": "foo"},
            False,
            "",
            "git@github.com:custom/example.git",
            "git@github.com:custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            True,
            "",
            "git@github.com:custom/example.git",
            "git@github.com:custom/example.git",
        ),
        (
            {},
            False,
            "aabbcc",
            "git@github.com:custom/example.git",
            "git@github.com:custom/example.git",
        ),
        (
            {},
            True,
            "aabbcc",
            "git@github.com:custom/example.git",
            "https://aabbcc@github.com/custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            False,
            "aabbcc",
            "git@github.com:custom/example.git",
            "git@github.com:custom/example.git",
        ),
        (
            {"GITHUB_ACTOR": "foo"},
            True,
            "aabbcc",
            "git@github.com:custom/example.git",
            "https://foo:aabbcc@github.com/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gh_client,
    patched_os_environ,
    use_token,
    token,
    _remote_url,
    expected,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        default_gh_client._remote_url = _remote_url
        default_gh_client.token = token
        assert default_gh_client.remote_url(use_token=use_token) == expected


def test_commit_hash_url(default_gh_client):
    sha = "hashashash"
    assert default_gh_client.commit_hash_url(
        sha
    ) == "https://{domain}/{owner}/{repo}/commit/{sha}".format(
        domain=default_gh_client.hvcs_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        sha=sha,
    )


@pytest.mark.parametrize("pr_number", (420, "420"))
def test_pull_request_url(default_gh_client, pr_number):
    assert default_gh_client.pull_request_url(
        pr_number=pr_number
    ) == "https://{domain}/{owner}/{repo}/issues/{pr_number}".format(
        domain=default_gh_client.hvcs_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        pr_number=pr_number,
    )


def test_asset_upload_url(default_gh_client):
    assert default_gh_client.asset_upload_url(
        release_id=420
    ) == "https://{domain}/repos/{owner}/{repo}/releases/{release_id}/assets".format(
        domain=default_gh_client.hvcs_api_domain,
        owner=default_gh_client.owner,
        repo=default_gh_client.repo_name,
        release_id=420,
    )


############
# Tests which need http response mocking
############


github_matcher = re.compile(rf"^https://{Github.DEFAULT_DOMAIN}")
github_api_matcher = re.compile(rf"^https://{Github.DEFAULT_API_DOMAIN}")


@pytest.mark.parametrize(
    "resp_payload, status_code, expected",
    [
        ({"state": "success"}, 200, True),
        ({"state": "pending"}, 200, False),
        ({"state": "failed"}, 200, False),
        ({"error": "not found"}, 404, False),
        ({"error": "too many requests"}, 429, False),
        ({"error": "internal error"}, 500, False),
        ({"error": "temporarily unavailable"}, 503, False),
    ],
)
def test_check_build_status(default_gh_client, resp_payload, status_code, expected):
    ref = "refA"
    with requests_mock.Mocker(session=default_gh_client.session) as m:
        m.register_uri(
            "GET", github_api_matcher, json=resp_payload, status_code=status_code
        )
        assert default_gh_client.check_build_status(ref) == expected
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "GET"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/commits/{ref}/status".format(
                api_url=default_gh_client.api_url,
                owner=default_gh_client.owner,
                repo_name=default_gh_client.repo_name,
                ref=ref,
            )
        )


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, True),
        (201, True),
        (400, False),
        (404, False),
        (429, False),
        (500, False),
        (503, False),
    ],
)
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release(default_gh_client, status_code, prerelease, expected):
    tag = "v1.0.0"
    changelog = "# TODO: Changelog"
    with requests_mock.Mocker(session=default_gh_client.session) as m:
        m.register_uri(
            "POST", github_api_matcher, json={"status": "ok"}, status_code=status_code
        )
        assert default_gh_client.create_release(tag, changelog, prerelease) == expected
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases".format(
                api_url=default_gh_client.api_url,
                owner=default_gh_client.owner,
                repo_name=default_gh_client.repo_name,
            )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": tag,
            "body": changelog,
            "draft": False,
            "prerelease": prerelease,
        }


@pytest.mark.parametrize("token", (None, "super-token"))
def test_should_create_release_using_token_or_netrc(default_gh_client, token):
    default_gh_client.token = token
    default_gh_client.session.auth = None if not token else TokenAuth(token)
    tag = "v1.0.0"
    changelog = "# TODO: Changelog"
    with requests_mock.Mocker(session=default_gh_client.session) as m, netrc_file(
        machine=default_gh_client.DEFAULT_API_DOMAIN
    ) as netrc, mock.patch.dict(os.environ, {"NETRC": netrc.name}, clear=True):

        m.register_uri("POST", github_api_matcher, json={}, status_code=201)
        assert default_gh_client.create_release(tag, changelog)
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        if not token:
            assert {
                "Authorization": "Basic "
                + base64.encodebytes(
                    f"{netrc.login_username}:{netrc.login_password}".encode()
                )
                .decode("ascii")
                .strip()
            }.items() <= m.last_request.headers.items()
        else:
            assert {
                "Authorization": f"token {token}"
            }.items() <= m.last_request.headers.items()
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases".format(
                api_url=default_gh_client.api_url,
                owner=default_gh_client.owner,
                repo_name=default_gh_client.repo_name,
            )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": tag,
            "body": changelog,
            "draft": False,
            "prerelease": False,
        }


def test_request_has_no_auth_header_if_no_token_or_netrc():
    with mock.patch.dict(os.environ, {}, clear=True):
        client = Github(remote_url="git@github.com:something/somewhere.git")

        with requests_mock.Mocker(session=client.session) as m:
            m.register_uri("POST", github_api_matcher, json={}, status_code=201)
            assert client.create_release("v1.0.0", "# TODO: Changelog")
            assert m.called
            assert len(m.request_history) == 1
            assert m.last_request.method == "POST"
            assert (
                m.last_request.url
                == "{api_url}/repos/{owner}/{repo_name}/releases".format(
                    api_url=client.api_url,
                    owner=client.owner,
                    repo_name=client.repo_name,
                )
            )
            assert "Authorization" not in m.last_request.headers


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (201, True),
        (400, False),
        (404, False),
        (429, False),
        (500, False),
        (503, False),
    ],
)
def test_edit_release_changelog(default_gh_client, status_code, expected):
    release_id = 420
    changelog = "# TODO: Changelog"
    with requests_mock.Mocker(session=default_gh_client.session) as m:
        m.register_uri("POST", github_api_matcher, json={}, status_code=status_code)
        assert default_gh_client.edit_release_changelog(420, changelog) == expected
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
                api_url=default_gh_client.api_url,
                owner=default_gh_client.owner,
                repo_name=default_gh_client.repo_name,
                release_id=release_id,
            )
        )
        assert m.last_request.json() == {"body": changelog}


@pytest.mark.parametrize(
    "resp_payload, status_code, expected",
    [
        ({"id": 420, "status": "success"}, 200, 420),
        ({"error": "not found"}, 404, None),
        ({"error": "too many requests"}, 429, None),
        ({"error": "internal error"}, 500, None),
        ({"error": "temporarily unavailable"}, 503, None),
    ],
)
def test_get_release_id_by_tag(default_gh_client, resp_payload, status_code, expected):
    tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gh_client.session) as m:
        m.register_uri(
            "GET", github_api_matcher, json=resp_payload, status_code=status_code
        )
        assert default_gh_client.get_release_id_by_tag(tag) == expected
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "GET"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases/tags/{tag}".format(
                api_url=default_gh_client.api_url,
                owner=default_gh_client.owner,
                repo_name=default_gh_client.repo_name,
                tag=tag,
            )
        )


# Note - mocking as the logic for the create/update of a release
# is covered by testing above, no point re-testing.
@pytest.mark.parametrize(
    "create_release_success, release_id, edit_release_success, expected",
    [
        (True, 420, True, True),
        (True, 420, False, True),
        (False, 420, True, True),
        (False, 420, False, False),
        (False, None, True, False),
        (False, None, False, False),
    ],
)
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release(
    default_gh_client,
    create_release_success,
    release_id,
    edit_release_success,
    prerelease,
    expected,
):
    tag = "v1.0.0"
    changelog = "# TODO: Changelog"
    with mock.patch.object(
        default_gh_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gh_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client, "edit_release_changelog"
    ) as mock_edit_release_changelog:
        mock_create_release.return_value = create_release_success
        mock_get_release_id_by_tag.return_value = release_id
        mock_edit_release_changelog.return_value = edit_release_success
        # client = Github(remote_url="git@github.com:something/somewhere.git")
        assert (
            default_gh_client.create_or_update_release(tag, changelog, prerelease)
            == expected
        )
        mock_create_release.assert_called_once_with(tag, changelog, prerelease)
        if not create_release_success:
            mock_get_release_id_by_tag.assert_called_once_with(tag)
        if not create_release_success and release_id:
            mock_edit_release_changelog.assert_called_once_with(release_id, changelog)
        elif not create_release_success and not release_id:
            mock_edit_release_changelog.assert_not_called()


@pytest.mark.parametrize(
    "status_code, expected",
    [
        (200, True),
        (201, True),
        (400, False),
        (404, False),
        (429, False),
        (500, False),
        (503, False),
    ],
)
def test_upload_asset(default_gh_client, example_changelog_md, status_code, expected):
    release_id = 420
    label = "abc123"
    urlparams = {"name": example_changelog_md.name, "label": label}
    with requests_mock.Mocker(session=default_gh_client.session) as m:
        m.register_uri(
            "POST", github_api_matcher, json={"status": "ok"}, status_code=status_code
        )
        assert (
            default_gh_client.upload_asset(
                release_id=release_id, file=example_changelog_md.resolve(), label=label
            )
            == expected
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert m.last_request.url == "{url}?{params}".format(
            url=default_gh_client.asset_upload_url(release_id),
            params=urlencode(urlparams),
        )

        # Check if content-type header was correctly set according to
        # mimetypes - not retesting guessing functionality
        assert {
            "Content-Type": mimetypes.guess_type(
                example_changelog_md.resolve(), strict=False
            )[0]
            or "application/octet-stream"
        }.items() <= m.last_request.headers.items()
        assert m.last_request.body == example_changelog_md.read_bytes()


# Note - mocking as the logic for uploading an asset
# is covered by testing above, no point re-testing.
def test_upload_dists_when_release_id_not_found(default_gh_client):
    tag = "v1.0.0"
    path = "doesn't matter"
    with mock.patch.object(
        default_gh_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client, "upload_asset"
    ) as mock_upload_asset:
        mock_get_release_id_by_tag.return_value = None
        assert not default_gh_client.upload_dists(tag, path)
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        mock_upload_asset.assert_not_called()


@pytest.mark.parametrize(
    "files, glob_pattern, upload_statuses, expected",
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
    default_gh_client, files, glob_pattern, upload_statuses, expected
):
    release_id = 420
    tag = "doesn't matter"
    with mock.patch.object(
        default_gh_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gh_client, "upload_asset"
    ) as mock_upload_asset, mock.patch.object(
        glob, "glob"
    ) as mock_glob_glob, mock.patch.object(
        os.path, "isfile"
    ) as mock_os_path_isfile:
        # Skip check as the filenames deliberately don't exists for testing
        mock_os_path_isfile.return_value = True

        matching_files = glob.fnmatch.filter(files, glob_pattern)
        mock_glob_glob.return_value = matching_files
        mock_get_release_id_by_tag.return_value = release_id

        mock_upload_asset.side_effect = upload_statuses
        assert default_gh_client.upload_dists(tag, glob_pattern) == expected
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        assert [
            mock.call(release_id, fn) for fn in matching_files
        ] == mock_upload_asset.call_args_list
