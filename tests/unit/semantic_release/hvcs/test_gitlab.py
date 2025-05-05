from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest import mock

import gitlab
import gitlab.exceptions
import gitlab.mixins
import gitlab.v4.objects
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


# Note: there's nothing special about the value of these variables,
# they're just constants for easier consistency with the faked objects
A_GOOD_TAG = "v1.2.3"
A_BAD_TAG = "v2.1.1-rc.1"
A_LOCKED_TAG = "v0.9.0"
A_MISSING_TAG = "v1.0.0+missing"
# But note this is the only ref we're making a "fake" commit for, so
# tests which need to query the remote for "a" ref, the exact sha for
# which doesn't matter, all use this constant
REF = "hashashash"


@pytest.fixture
def default_gl_project(example_git_https_url: str):
    return gitlab.Gitlab(url=example_git_https_url).projects.get(
        f"{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}", lazy=True
    )


@pytest.fixture
def default_gl_client(
    example_git_https_url: str,
    default_gl_project: gitlab.v4.objects.Project,
) -> Generator[Gitlab, None, None]:
    gitlab_client = Gitlab(remote_url=example_git_https_url)

    # make sure that when project tries to get the project instance, we return the mock
    # that we control
    project_get_mock = mock.patch.object(
        gitlab_client._client.projects,
        gitlab_client._client.projects.get.__name__,
        return_value=default_gl_project,
    )

    env_mock = mock.patch.dict(os.environ, {}, clear=True)

    with project_get_mock, env_mock:
        yield gitlab_client


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
    example_git_https_url: str,
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
        result = Gitlab(
            remote_url=example_git_https_url,
        )._get_repository_owner_and_name()

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
    use_token: bool,
    token: str,
    remote_url: str,
    expected_auth_url: str,
):
    with mock.patch.dict(os.environ, {}, clear=True):
        gl_client = Gitlab(remote_url=remote_url, token=token)

    assert expected_auth_url == gl_client.remote_url(use_token=use_token)


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


def test_commit_hash_url_w_custom_server():
    """
    Test the commit hash URL generation for a self-hosted Bitbucket server with prefix.

    ref: https://github.com/python-semantic-release/python-semantic-release/issues/1204
    """
    sha = "244f7e11bcb1e1ce097db61594056bc2a32189a0"
    expected_url = "{server}/{owner}/{repo}/-/commit/{sha}".format(
        server=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        owner="foo",
        repo=EXAMPLE_REPO_NAME,
        sha=sha,
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        actual_url = Gitlab(
            remote_url=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo/foo/{EXAMPLE_REPO_NAME}.git",
            hvcs_domain=f"https://{EXAMPLE_HVCS_DOMAIN}/projects/demo-foo",
        ).commit_hash_url(sha)

    assert expected_url == actual_url


@pytest.mark.parametrize("issue_number", (666, "666", "#666"))
def test_issue_url(default_gl_client: Gitlab, issue_number: int | str):
    expected_url = "{server}/{owner}/{repo}/-/issues/{issue_num}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        issue_num=str(issue_number).lstrip("#"),
    )
    actual_url = default_gl_client.issue_url(issue_num=issue_number)
    assert expected_url == actual_url


@pytest.mark.parametrize("pr_number", (666, "666", "!666"))
def test_pull_request_url(default_gl_client: Gitlab, pr_number: int | str):
    expected_url = "{server}/{owner}/{repo}/-/merge_requests/{pr_number}".format(
        server=default_gl_client.hvcs_domain.url,
        owner=default_gl_client.owner,
        repo=default_gl_client.repo_name,
        pr_number=str(pr_number).lstrip("!"),
    )
    actual_url = default_gl_client.pull_request_url(pr_number=pr_number)
    assert expected_url == actual_url


@pytest.mark.parametrize("tag", (A_GOOD_TAG, A_LOCKED_TAG))
def test_create_release_succeeds(
    default_gl_client: Gitlab, default_gl_project: gitlab.v4.objects.Project, tag: str
):
    with mock.patch.object(
        default_gl_project.releases,
        default_gl_project.releases.create.__name__,
    ) as mocked_create_release:
        result = default_gl_client.create_release(tag, RELEASE_NOTES)

        assert tag == result
        mocked_create_release.assert_called_once_with(
            {
                "name": tag,
                "tag_name": tag,
                "tag_message": tag,
                "description": RELEASE_NOTES,
            }
        )


def test_create_release_fails_with_bad_tag(
    default_gl_client: Gitlab,
    default_gl_project: gitlab.v4.objects.Project,
):
    bad_request = gitlab.GitlabCreateError("401 Unauthorized")
    mock_failed_create = mock.patch.object(
        default_gl_project.releases,
        default_gl_project.releases.create.__name__,
        side_effect=bad_request,
    )
    with mock_failed_create, pytest.raises(gitlab.GitlabCreateError):
        default_gl_client.create_release(A_BAD_TAG, RELEASE_NOTES)


@pytest.mark.parametrize("tag", (A_GOOD_TAG, A_LOCKED_TAG))
def test_update_release_succeeds(default_gl_client: Gitlab, tag: str):
    fake_release_obj = gitlab.v4.objects.ProjectReleaseManager(
        default_gl_client._client
    ).get(tag, lazy=True)
    fake_release_obj._attrs["name"] = tag

    with mock.patch.object(
        gitlab.mixins.SaveMixin,
        gitlab.mixins.SaveMixin.save.__name__,
    ) as mocked_update_release:
        release_id = default_gl_client.edit_release_notes(
            fake_release_obj, RELEASE_NOTES
        )

        assert tag == release_id
        mocked_update_release.assert_called_once()
        assert RELEASE_NOTES == fake_release_obj.description  # noqa: SIM300


def test_update_release_fails_with_missing_tag(
    default_gl_client: Gitlab,
    default_gl_project: gitlab.v4.objects.Project,
):
    fake_release_obj = gitlab.v4.objects.ProjectRelease(
        default_gl_project.manager,
        {"id": A_MISSING_TAG, "name": A_MISSING_TAG},
        lazy=True,
    )
    mocked_update_release = mock.patch.object(
        gitlab.mixins.SaveMixin,
        gitlab.mixins.SaveMixin.save.__name__,
        side_effect=gitlab.GitlabUpdateError,
    )

    with mocked_update_release, pytest.raises(gitlab.GitlabUpdateError):
        default_gl_client.edit_release_notes(fake_release_obj, RELEASE_NOTES)


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_succeeds(
    default_gl_client: Gitlab, prerelease: bool
):
    with mock.patch.object(
        default_gl_client,
        default_gl_client.create_release.__name__,
        return_value=A_GOOD_TAG,
    ) as mock_create_release, mock.patch.object(
        default_gl_client,
        default_gl_client.edit_release_notes.__name__,
        return_value=A_GOOD_TAG,
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


def test_get_release_id_by_tag(
    default_gl_client: Gitlab,
    default_gl_project: gitlab.v4.objects.Project,
):
    dummy_release = default_gl_project.releases.get(A_GOOD_TAG, lazy=True)

    with mock.patch.object(
        default_gl_project.releases,
        default_gl_project.releases.get.__name__,
        return_value=dummy_release,
    ) as mocked_get_release_id:
        result = default_gl_client.get_release_by_tag(A_GOOD_TAG)

        assert dummy_release == result
        mocked_get_release_id.assert_called_once_with(A_GOOD_TAG)


def test_get_release_id_by_tag_fails(
    default_gl_client: Gitlab,
    default_gl_project: gitlab.v4.objects.Project,
):
    mocked_get_release_id = mock.patch.object(
        default_gl_project.releases,
        default_gl_project.releases.get.__name__,
        side_effect=gitlab.exceptions.GitlabAuthenticationError,
    )

    with pytest.raises(
        gitlab.exceptions.GitlabAuthenticationError
    ), mocked_get_release_id:
        default_gl_client.get_release_by_tag(A_GOOD_TAG)


def test_get_release_id_by_tag_not_found(
    default_gl_client: Gitlab,
    default_gl_project: gitlab.v4.objects.Project,
):
    mocked_get_release_id = mock.patch.object(
        default_gl_project.releases,
        default_gl_project.releases.get.__name__,
        side_effect=gitlab.exceptions.GitlabGetError,
    )

    with mocked_get_release_id:
        result = default_gl_client.get_release_by_tag(A_GOOD_TAG)

    assert result is None


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_succeeds(
    default_gl_client: Gitlab,
    prerelease: bool,
):
    bad_request = gitlab.GitlabCreateError("400 Bad Request")
    expected_release_obj = gitlab.v4.objects.ProjectRelease(
        gitlab.v4.objects.ProjectManager(default_gl_client._client),
        {"commit": {"id": "1"}, "name": A_GOOD_TAG},
        lazy=True,
    )

    with mock.patch.object(
        default_gl_client,
        default_gl_client.create_release.__name__,
        side_effect=bad_request,
    ), mock.patch.object(
        default_gl_client,
        default_gl_client.get_release_by_tag.__name__,
        return_value=expected_release_obj,
    ), mock.patch.object(
        default_gl_client,
        default_gl_client.edit_release_notes.__name__,
        return_value=A_GOOD_TAG,
    ) as mock_edit_release_notes:
        # Execute in mock environment
        default_gl_client.create_or_update_release(
            A_GOOD_TAG, RELEASE_NOTES, prerelease
        )

        # Evaluate (expected -> actual)
        mock_edit_release_notes.assert_called_once_with(
            release=expected_release_obj, release_notes=RELEASE_NOTES
        )


@pytest.mark.parametrize("prerelease", (True, False))
def test_create_or_update_release_when_create_fails_and_update_fails(
    default_gl_client: Gitlab,
    prerelease: bool,
):
    bad_request = gitlab.GitlabCreateError("400 Bad Request")
    not_found = gitlab.GitlabUpdateError("404 Not Found")
    fake_release_obj = gitlab.v4.objects.ProjectRelease(
        gitlab.v4.objects.ProjectManager(default_gl_client._client),
        {"commit": {"id": "1"}, "name": A_GOOD_TAG},
        lazy=True,
    )

    create_release_patch = mock.patch.object(
        default_gl_client,
        default_gl_client.create_release.__name__,
        side_effect=bad_request,
    )
    edit_release_notes_patch = mock.patch.object(
        default_gl_client,
        default_gl_client.edit_release_notes.__name__,
        side_effect=not_found,
    )
    get_release_by_id_patch = mock.patch.object(
        default_gl_client,
        default_gl_client.get_release_by_tag.__name__,
        return_value=fake_release_obj,
    )

    # Execute in mocked environment expecting a GitlabUpdateError to be raised
    with create_release_patch, edit_release_notes_patch, get_release_by_id_patch:  # noqa: SIM117
        with pytest.raises(gitlab.GitlabUpdateError):
            default_gl_client.create_or_update_release(
                A_GOOD_TAG, RELEASE_NOTES, prerelease
            )
