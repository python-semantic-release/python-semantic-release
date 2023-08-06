import base64
import glob
import os
import re
from unittest import mock
from urllib.parse import urlencode

import pytest
import requests_mock
from requests import HTTPError, Response, Session

from semantic_release.hvcs.gitea import Gitea
from semantic_release.hvcs.token_auth import TokenAuth

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER, RELEASE_NOTES
from tests.util import netrc_file


@pytest.fixture
def default_gitea_client():
    remote_url = f"git@gitea.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"
    return Gitea(remote_url=remote_url)


@pytest.mark.parametrize(
    (
        "patched_os_environ, hvcs_domain, hvcs_api_domain, "
        "expected_hvcs_domain, expected_hvcs_api_domain"
    ),
    [
        ({}, None, None, Gitea.DEFAULT_DOMAIN, Gitea.DEFAULT_API_DOMAIN),
        (
            {"GITEA_SERVER_URL": "https://special.custom.server/vcs/"},
            None,
            None,
            "special.custom.server/vcs/",
            Gitea.DEFAULT_API_DOMAIN,
        ),
        (
            {"GITEA_API_URL": "https://api.special.custom.server/"},
            None,
            None,
            Gitea.DEFAULT_DOMAIN,
            "api.special.custom.server/",
        ),
        (
            {"GITEA_SERVER_URL": "https://special.custom.server/vcs/"},
            "https://example.com",
            None,
            "https://example.com",
            Gitea.DEFAULT_API_DOMAIN,
        ),
        (
            {"GITEA_API_URL": "https://api.special.custom.server/"},
            None,
            "https://api.example.com",
            Gitea.DEFAULT_DOMAIN,
            "https://api.example.com",
        ),
    ],
)
@pytest.mark.parametrize(
    "remote_url",
    [
        f"git@gitea.com:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
        f"https://gitea.com/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git",
    ],
)
@pytest.mark.parametrize("token", ("abc123", None))
def test_gitea_client_init(
    patched_os_environ,
    hvcs_domain,
    hvcs_api_domain,
    expected_hvcs_domain,
    expected_hvcs_api_domain,
    remote_url,
    token,
):
    with mock.patch.dict(os.environ, patched_os_environ, clear=True):
        client = Gitea(
            remote_url=remote_url,
            hvcs_domain=hvcs_domain,
            hvcs_api_domain=hvcs_api_domain,
            token=token,
        )

        assert client.hvcs_domain == expected_hvcs_domain
        assert client.hvcs_api_domain == expected_hvcs_api_domain
        assert client.api_url == f"https://{client.hvcs_api_domain}"
        assert client.token == token
        assert client._remote_url == remote_url
        assert hasattr(client, "session")
        assert isinstance(getattr(client, "session", None), Session)


def test_gitea_get_repository_owner_and_name(default_gitea_client):
    assert (
        default_gitea_client._get_repository_owner_and_name()
        == super(Gitea, default_gitea_client)._get_repository_owner_and_name()
    )


@pytest.mark.parametrize(
    "use_token, token, _remote_url, expected",
    [
        (
            False,
            "",
            "git@gitea.com:custom/example.git",
            "git@gitea.com:custom/example.git",
        ),
        (
            True,
            "",
            "git@gitea.com:custom/example.git",
            "git@gitea.com:custom/example.git",
        ),
        (
            False,
            "aabbcc",
            "git@gitea.com:custom/example.git",
            "git@gitea.com:custom/example.git",
        ),
        (
            True,
            "aabbcc",
            "git@gitea.com:custom/example.git",
            "https://aabbcc@gitea.com/custom/example.git",
        ),
        (
            False,
            "aabbcc",
            "git@gitea.com:custom/example.git",
            "git@gitea.com:custom/example.git",
        ),
        (
            True,
            "aabbcc",
            "git@gitea.com:custom/example.git",
            "https://aabbcc@gitea.com/custom/example.git",
        ),
    ],
)
def test_remote_url(
    default_gitea_client,
    use_token,
    token,
    # TODO: linter thinks this is a fixture not a param - why?
    _remote_url,  # noqa: PT019
    expected,
):
    default_gitea_client._remote_url = _remote_url
    default_gitea_client.token = token
    assert default_gitea_client.remote_url(use_token=use_token) == expected


def test_commit_hash_url(default_gitea_client):
    sha = "hashashash"
    assert default_gitea_client.commit_hash_url(
        sha
    ) == "https://{domain}/{owner}/{repo}/commit/{sha}".format(
        domain=default_gitea_client.hvcs_domain,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        sha=sha,
    )


@pytest.mark.parametrize("pr_number", (420, "420"))
def test_pull_request_url(default_gitea_client, pr_number):
    assert default_gitea_client.pull_request_url(
        pr_number=pr_number
    ) == "https://{domain}/{owner}/{repo}/pulls/{pr_number}".format(
        domain=default_gitea_client.hvcs_domain,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        pr_number=pr_number,
    )


def test_asset_upload_url(default_gitea_client):
    assert default_gitea_client.asset_upload_url(
        release_id=420
    ) == "https://{domain}/repos/{owner}/{repo}/releases/{release_id}/assets".format(
        domain=default_gitea_client.hvcs_api_domain,
        owner=default_gitea_client.owner,
        repo=default_gitea_client.repo_name,
        release_id=420,
    )


############
# Tests which need http response mocking
############


gitea_matcher = re.compile(rf"^https://{Gitea.DEFAULT_DOMAIN}")
gitea_api_matcher = re.compile(rf"^https://{Gitea.DEFAULT_API_DOMAIN}")


@pytest.mark.parametrize("status_code", (201,))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_succeeds(
    default_gitea_client, status_code, prerelease, mock_release_id
):
    tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "POST",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )
        assert (
            default_gitea_client.create_release(tag, RELEASE_NOTES, prerelease)
            == mock_release_id
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases".format(
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
            )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": tag,
            "body": RELEASE_NOTES,
            "draft": False,
            "prerelease": prerelease,
        }


@pytest.mark.parametrize("status_code", (400, 409))
@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_release_fails(
    default_gitea_client, status_code, prerelease, mock_release_id
):
    tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "POST",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        with pytest.raises(HTTPError):
            default_gitea_client.create_release(tag, RELEASE_NOTES, prerelease)

        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases".format(
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
            )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": tag,
            "body": RELEASE_NOTES,
            "draft": False,
            "prerelease": prerelease,
        }


@pytest.mark.parametrize("token", (None, "super-token"))
def test_should_create_release_using_token_or_netrc(default_gitea_client, token):
    default_gitea_client.token = token
    default_gitea_client.session.auth = None if not token else TokenAuth(token)
    tag = "v1.0.0"

    # Note write netrc file with DEFAULT_DOMAIN not DEFAULT_API_DOMAIN as can't
    # handle /api/v1 in file
    with requests_mock.Mocker(session=default_gitea_client.session) as m, netrc_file(
        machine=default_gitea_client.DEFAULT_DOMAIN
    ) as netrc, mock.patch.dict(os.environ, {"NETRC": netrc.name}, clear=True):
        m.register_uri("POST", gitea_api_matcher, json={"id": 1}, status_code=201)
        assert default_gitea_client.create_release(tag, RELEASE_NOTES) == 1
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
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
            )
        )
        assert m.last_request.json() == {
            "tag_name": tag,
            "name": tag,
            "body": RELEASE_NOTES,
            "draft": False,
            "prerelease": False,
        }


def test_request_has_no_auth_header_if_no_token_or_netrc():
    with mock.patch.dict(os.environ, {}, clear=True):
        client = Gitea(remote_url="git@gitea.com:something/somewhere.git")

        with requests_mock.Mocker(session=client.session) as m:
            m.register_uri("POST", gitea_api_matcher, json={"id": 1}, status_code=201)
            assert client.create_release("v1.0.0", RELEASE_NOTES) == 1
            assert m.called
            assert len(m.request_history) == 1
            assert m.last_request.method == "POST"
            assert (
                m.last_request.url
                == f"{client.api_url}/repos/{client.owner}/{client.repo_name}/releases"
            )
            assert "Authorization" not in m.last_request.headers


@pytest.mark.parametrize(
    "resp_payload, status_code, expected",
    [
        ({"id": 420}, 200, 420),
        ({}, 404, None),
    ],
)
def test_get_release_id_by_tag(
    default_gitea_client, resp_payload, status_code, expected
):
    tag = "v1.0.0"
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "GET", gitea_api_matcher, json=resp_payload, status_code=status_code
        )
        assert default_gitea_client.get_release_id_by_tag(tag) == expected
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "GET"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases/tags/{tag}".format(
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
                tag=tag,
            )
        )


@pytest.mark.parametrize("status_code", [201])
@pytest.mark.parametrize("mock_release_id", range(3))
def test_edit_release_notes_succeeds(
    default_gitea_client, status_code, mock_release_id
):
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "PATCH",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )
        assert (
            default_gitea_client.edit_release_notes(mock_release_id, RELEASE_NOTES)
            == mock_release_id
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "PATCH"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
                release_id=mock_release_id,
            )
        )
        assert m.last_request.json() == {"body": RELEASE_NOTES}


@pytest.mark.parametrize("status_code", (400, 404, 429, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
def test_edit_release_notes_fails(default_gitea_client, status_code, mock_release_id):
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "PATCH",
            gitea_api_matcher,
            json={"id": mock_release_id},
            status_code=status_code,
        )

        with pytest.raises(HTTPError):
            default_gitea_client.edit_release_notes(mock_release_id, RELEASE_NOTES)

        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "PATCH"
        assert (
            m.last_request.url
            == "{api_url}/repos/{owner}/{repo_name}/releases/{release_id}".format(
                api_url=default_gitea_client.api_url,
                owner=default_gitea_client.owner,
                repo_name=default_gitea_client.repo_name,
                release_id=mock_release_id,
            )
        )
        assert m.last_request.json() == {"body": RELEASE_NOTES}


# Note - mocking as the logic for the create/update of a release
# is covered by testing above, no point re-testing.


@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(
    default_gitea_client,
    mock_release_id,
    prerelease,
):
    tag = "v1.0.0"
    with mock.patch.object(
        default_gitea_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gitea_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        mock_create_release.return_value = mock_release_id
        mock_get_release_id_by_tag.return_value = mock_release_id
        mock_edit_release_notes.return_value = mock_release_id
        assert (
            default_gitea_client.create_or_update_release(
                tag, RELEASE_NOTES, prerelease
            )
            == mock_release_id
        )
        mock_create_release.assert_called_once_with(tag, RELEASE_NOTES, prerelease)
        mock_get_release_id_by_tag.assert_not_called()
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("mock_release_id", range(3))
@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_succeeds(
    default_gitea_client,
    mock_release_id,
    prerelease,
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found", response=Response())
    not_found.response.status_code = 404
    with mock.patch.object(
        default_gitea_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gitea_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        mock_create_release.side_effect = not_found
        mock_get_release_id_by_tag.return_value = mock_release_id
        mock_edit_release_notes.return_value = mock_release_id
        assert (
            default_gitea_client.create_or_update_release(
                tag, RELEASE_NOTES, prerelease
            )
            == mock_release_id
        )
        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_called_once_with(mock_release_id, RELEASE_NOTES)


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_no_release_for_tag(
    default_gitea_client, prerelease
):
    tag = "v1.0.0"
    not_found = HTTPError("404 Not Found", response=Response())
    not_found.response.status_code = 404
    with mock.patch.object(
        default_gitea_client, "create_release"
    ) as mock_create_release, mock.patch.object(
        default_gitea_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, "edit_release_notes"
    ) as mock_edit_release_notes:
        mock_create_release.side_effect = not_found
        mock_get_release_id_by_tag.return_value = None
        mock_edit_release_notes.return_value = None

        with pytest.raises(ValueError):
            default_gitea_client.create_or_update_release(
                tag, RELEASE_NOTES, prerelease
            )

        mock_get_release_id_by_tag.assert_called_once_with(tag)
        mock_edit_release_notes.assert_not_called()


@pytest.mark.parametrize("status_code", (200, 201))
@pytest.mark.parametrize("mock_release_id", range(3))
def test_upload_asset_succeeds(
    default_gitea_client, example_changelog_md, status_code, mock_release_id
):
    urlparams = {"name": example_changelog_md.name}
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "POST", gitea_api_matcher, json={"status": "ok"}, status_code=status_code
        )
        assert (
            default_gitea_client.upload_asset(
                release_id=mock_release_id,
                file=example_changelog_md.resolve(),
                label="doesn't matter could be None",
            )
            is True
        )
        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert m.last_request.url == "{url}?{params}".format(
            url=default_gitea_client.asset_upload_url(mock_release_id),
            params=urlencode(urlparams),
        )

        # TODO: this feels brittle
        changelog_text = m.last_request.body.split(b"\r\n")[4]
        assert changelog_text == example_changelog_md.read_bytes()


@pytest.mark.parametrize("status_code", (400, 500, 503))
@pytest.mark.parametrize("mock_release_id", range(3))
def test_upload_asset_fails(
    default_gitea_client, example_changelog_md, status_code, mock_release_id
):
    urlparams = {"name": example_changelog_md.name}
    with requests_mock.Mocker(session=default_gitea_client.session) as m:
        m.register_uri(
            "POST", gitea_api_matcher, json={"status": "ok"}, status_code=status_code
        )

        with pytest.raises(HTTPError):
            default_gitea_client.upload_asset(
                release_id=mock_release_id,
                file=example_changelog_md.resolve(),
                label="doesn't matter could be None",
            )

        assert m.called
        assert len(m.request_history) == 1
        assert m.last_request.method == "POST"
        assert m.last_request.url == "{url}?{params}".format(
            url=default_gitea_client.asset_upload_url(mock_release_id),
            params=urlencode(urlparams),
        )

        # TODO: this feels brittle
        changelog_text = m.last_request.body.split(b"\r\n")[4]
        assert changelog_text == example_changelog_md.read_bytes()


# Note - mocking as the logic for uploading an asset
# is covered by testing above, no point re-testing.
def test_upload_dists_when_release_id_not_found(default_gitea_client):
    tag = "v1.0.0"
    path = "doesn't matter"
    with mock.patch.object(
        default_gitea_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, "upload_asset"
    ) as mock_upload_asset:
        mock_get_release_id_by_tag.return_value = None
        assert not default_gitea_client.upload_dists(tag, path)
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
    default_gitea_client, files, glob_pattern, upload_statuses, expected
):
    release_id = 420
    tag = "doesn't matter"
    with mock.patch.object(
        default_gitea_client, "get_release_id_by_tag"
    ) as mock_get_release_id_by_tag, mock.patch.object(
        default_gitea_client, "upload_asset"
    ) as mock_upload_asset, mock.patch.object(
        glob, "glob"
    ) as mock_glob_glob, mock.patch.object(
        os.path, "isfile"
    ) as mock_os_path_isfile:
        # Skip check as the files don't exist in filesystem
        mock_os_path_isfile.return_value = True

        matching_files = glob.fnmatch.filter(files, glob_pattern)
        mock_glob_glob.return_value = matching_files
        mock_get_release_id_by_tag.return_value = release_id

        mock_upload_asset.side_effect = upload_statuses
        assert default_gitea_client.upload_dists(tag, glob_pattern) == expected
        mock_get_release_id_by_tag.assert_called_once_with(tag=tag)
        assert [
            mock.call(release_id, fn) for fn in matching_files
        ] == mock_upload_asset.call_args_list
