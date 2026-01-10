"""Tests for PyGithub integration in GitHub HVCS"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from github import Auth, Github as GithubClient, GithubException
from github.GitRelease import GitRelease
from github.Repository import Repository
from requests import Session

from semantic_release.errors import (
    AssetUploadError,
    IncompleteReleaseError,
    UnexpectedResponse,
)
from semantic_release.hvcs.github import Github

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def default_github_url() -> str:
    """Default GitHub remote URL for testing"""
    return "git@github.com:owner/repo.git"


@pytest.fixture
def github_enterprise_url() -> str:
    """GitHub Enterprise remote URL for testing"""
    return "git@ghe.company.com:owner/repo.git"


@pytest.fixture
def mock_github_client(mocker: MockerFixture) -> MagicMock:
    """Mock PyGithub Github client"""
    return mocker.MagicMock(spec=GithubClient)


@pytest.fixture
def mock_repository(mocker: MockerFixture) -> MagicMock:
    """Mock PyGithub Repository object"""
    return mocker.MagicMock(spec=Repository)


@pytest.fixture
def mock_release(mocker: MockerFixture) -> MagicMock:
    """Mock PyGithub GitRelease object"""
    mock_rel = mocker.MagicMock(spec=GitRelease)
    mock_rel.id = 12345
    mock_rel.title = "v1.0.0"
    mock_rel.draft = False
    mock_rel.prerelease = False
    mock_rel.upload_url = (
        "https://uploads.github.com/repos/owner/repo/releases/12345/assets{?name,label}"
    )
    return mock_rel


@pytest.fixture
def default_token() -> str:
    """Default test token"""
    return "test_token_123"


class TestGithubInitialization:
    """Tests for GitHub HVCS initialization with PyGithub"""

    def test_init_with_default_github_domain(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
    ) -> None:
        """Given default github.com, when initializing, then PyGithub client uses default API domain"""
        mock_github_constructor = mocker.patch(
            "semantic_release.hvcs.github.GithubClient"
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Verify PyGithub client was created with correct parameters
        mock_github_constructor.assert_called_once()
        call_kwargs = mock_github_constructor.call_args[1]

        # Should have Auth.Token
        assert isinstance(call_kwargs["auth"], Auth.Token)
        # Should use default (None) for github.com
        assert call_kwargs["base_url"] is None

        # Verify other attributes
        assert github_hvcs.token == default_token
        assert github_hvcs.owner == "owner"
        assert github_hvcs.repo_name == "repo"

    def test_init_with_github_enterprise_domain(
        self,
        github_enterprise_url: str,
        default_token: str,
        mocker: MockerFixture,
    ) -> None:
        """Given GHE domain, when initializing, then PyGithub client uses custom API URL"""
        mock_github_constructor = mocker.patch(
            "semantic_release.hvcs.github.GithubClient"
        )

        github_hvcs = Github(
            remote_url=github_enterprise_url,
            hvcs_domain="https://ghe.company.com",
            token=default_token,
        )

        # Verify PyGithub client was created with custom base_url
        mock_github_constructor.assert_called_once()
        call_kwargs = mock_github_constructor.call_args[1]

        # Should have Auth.Token
        assert isinstance(call_kwargs["auth"], Auth.Token)
        # Should use custom API URL for GHE
        assert call_kwargs["base_url"] == "https://ghe.company.com/api/v3"

        # Verify attributes
        assert github_hvcs.token == default_token
        assert github_hvcs.owner == "owner"
        assert github_hvcs.repo_name == "repo"

    def test_init_without_token(
        self,
        default_github_url: str,
        mocker: MockerFixture,
    ) -> None:
        """Given no token, when initializing, then PyGithub client has no auth"""
        mock_github_constructor = mocker.patch(
            "semantic_release.hvcs.github.GithubClient"
        )

        github_hvcs = Github(remote_url=default_github_url, token=None)

        # Verify PyGithub client was created without auth
        mock_github_constructor.assert_called_once()
        call_kwargs = mock_github_constructor.call_args[1]
        assert call_kwargs["auth"] is None

        # Verify token is None
        assert github_hvcs.token is None

    def test_init_maintains_requests_session_backward_compatibility(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
    ) -> None:
        """Given initialization, when creating Github HVCS, then requests session is still created for backward compatibility"""
        mocker.patch("semantic_release.hvcs.github.GithubClient")

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Verify requests session still exists (backward compatibility)
        assert isinstance(github_hvcs.session, Session)

    def test_init_with_github_actions_env_vars(
        self,
        mocker: MockerFixture,
        default_token: str,
    ) -> None:
        """Given GITHUB_* env vars, when initializing, then they are used for configuration"""
        mocker.patch("semantic_release.hvcs.github.GithubClient")
        mocker.patch.dict(
            os.environ,
            {
                "GITHUB_REPOSITORY": "test-owner/test-repo",
                "GITHUB_SERVER_URL": "https://github.com",
            },
        )

        github_hvcs = Github(
            remote_url="git@github.com:owner/repo.git",
            token=default_token,
        )

        # Should use environment variables for owner/repo
        assert github_hvcs.owner == "test-owner"
        assert github_hvcs.repo_name == "test-repo"


class TestGithubRepositoryProperty:
    """Tests for lazy-loading repository property"""

    def test_repo_property_lazy_loads_repository(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given first access to repo, when property is called, then repository is loaded and cached"""
        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # First access should load the repository
        repo = github_hvcs.repo

        mock_github_client.get_repo.assert_called_once_with("owner/repo")
        assert repo == mock_repository

    def test_repo_property_caches_repository(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given repository already loaded, when accessing repo again, then cached value is used"""
        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Access repo multiple times
        repo1 = github_hvcs.repo
        repo2 = github_hvcs.repo
        repo3 = github_hvcs.repo

        # Should only call get_repo once (cached)
        mock_github_client.get_repo.assert_called_once()
        assert repo1 == repo2 == repo3 == mock_repository

    def test_repo_property_raises_on_github_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
    ) -> None:
        """Given GithubException when loading repo, when accessing repo property, then exception is raised"""
        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.side_effect = GithubException(
            status=403,
            data={"message": "Not authorized"},
            headers={},
        )

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Should raise GithubException
        with pytest.raises(GithubException) as exc_info:
            _ = github_hvcs.repo

        assert exc_info.value.status == 403


class TestGithubCreateRelease:
    """Tests for create_release() method with PyGithub"""

    def test_create_release_successfully(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given valid parameters, when creating release, then PyGithub creates release and returns ID"""
        mock_repository.create_git_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_release(
            tag="v1.0.0",
            release_notes="Test release notes",
            prerelease=False,
        )

        mock_repository.create_git_release.assert_called_once_with(
            tag="v1.0.0",
            name="v1.0.0",
            message="Test release notes",
            draft=False,
            prerelease=False,
        )
        assert release_id == 12345

    def test_create_release_as_prerelease(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given prerelease=True, when creating release, then prerelease flag is set"""
        mock_repository.create_git_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_release(
            tag="v1.0.0-beta.1",
            release_notes="Beta release",
            prerelease=True,
        )

        call_kwargs = mock_repository.create_git_release.call_args[1]
        assert call_kwargs["prerelease"] is True
        assert release_id == 12345

    def test_create_release_with_assets(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
        tmp_path,
    ) -> None:
        """Given assets list, when creating release, then assets are uploaded"""
        # Create test asset file
        test_asset = tmp_path / "test_asset.txt"
        test_asset.write_text("test content")

        mock_repository.create_git_release.return_value = mock_release
        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_release(
            tag="v1.0.0",
            release_notes="Release with assets",
            prerelease=False,
            assets=[str(test_asset)],
        )

        # Should create release and upload asset
        mock_repository.create_git_release.assert_called_once()
        mock_release.upload_asset.assert_called_once()
        assert release_id == 12345

    def test_create_release_noop_mode(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given noop=True, when creating release, then no API calls are made"""
        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_release(
            tag="v1.0.0",
            release_notes="Test",
            noop=True,
        )

        # Should not create release in noop mode
        mock_repository.create_git_release.assert_not_called()
        assert release_id == -1

    def test_create_release_raises_on_github_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given GithubException, when creating release, then UnexpectedResponse is raised"""
        mock_repository.create_git_release.side_effect = GithubException(
            status=422,
            data={"message": "Validation Failed"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        with pytest.raises(UnexpectedResponse) as exc_info:
            github_hvcs.create_release(
                tag="v1.0.0",
                release_notes="Test",
            )

        assert "Failed to create release" in str(exc_info.value)

    def test_create_release_with_asset_upload_failure(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
        tmp_path,
    ) -> None:
        """Given asset upload fails, when creating release, then IncompleteReleaseError is raised"""
        # Create test asset file
        test_asset = tmp_path / "test_asset.txt"
        test_asset.write_text("test content")

        mock_repository.create_git_release.return_value = mock_release
        mock_repository.get_release.return_value = mock_release
        mock_release.upload_asset.side_effect = GithubException(
            status=500,
            data={"message": "Upload failed"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        with pytest.raises(IncompleteReleaseError) as exc_info:
            github_hvcs.create_release(
                tag="v1.0.0",
                release_notes="Release with failing asset",
                assets=[str(test_asset)],
            )

        assert "Failed to upload asset" in str(exc_info.value)


class TestGithubGetReleaseIdByTag:
    """Tests for get_release_id_by_tag() method with PyGithub"""

    def test_get_release_id_by_tag_found(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given existing release, when getting by tag, then release ID is returned"""
        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.get_release_id_by_tag("v1.0.0")

        mock_repository.get_release.assert_called_once_with("v1.0.0")
        assert release_id == 12345

    def test_get_release_id_by_tag_not_found(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given non-existent release, when getting by tag, then None is returned"""
        mock_repository.get_release.side_effect = GithubException(
            status=404,
            data={"message": "Not Found"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.get_release_id_by_tag("v9.9.9")

        assert release_id is None

    def test_get_release_id_by_tag_other_error(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given non-404 GithubException, when getting by tag, then UnexpectedResponse is raised"""
        mock_repository.get_release.side_effect = GithubException(
            status=500,
            data={"message": "Internal Server Error"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        with pytest.raises(UnexpectedResponse) as exc_info:
            github_hvcs.get_release_id_by_tag("v1.0.0")

        assert "Failed to get release by tag" in str(exc_info.value)


class TestGithubEditReleaseNotes:
    """Tests for edit_release_notes() method with PyGithub"""

    def test_edit_release_notes_successfully(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given valid release ID and notes, when editing, then release is updated"""
        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.edit_release_notes(
            release_id=12345,
            release_notes="Updated release notes",
        )

        mock_repository.get_release.assert_called_once_with(12345)
        mock_release.update_release.assert_called_once_with(
            name=mock_release.title,
            message="Updated release notes",
            draft=mock_release.draft,
            prerelease=mock_release.prerelease,
        )
        assert release_id == 12345

    def test_edit_release_notes_raises_on_github_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given GithubException, when editing release, then UnexpectedResponse is raised"""
        mock_repository.get_release.side_effect = GithubException(
            status=404,
            data={"message": "Not Found"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        with pytest.raises(UnexpectedResponse) as exc_info:
            github_hvcs.edit_release_notes(
                release_id=99999,
                release_notes="Updated notes",
            )

        assert "Failed to edit release" in str(exc_info.value)


class TestGithubAssetUploadUrl:
    """Tests for asset_upload_url() method with PyGithub"""

    def test_asset_upload_url_found(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given valid release ID, when getting upload URL, then URL is returned"""
        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        upload_url = github_hvcs.asset_upload_url(12345)

        mock_repository.get_release.assert_called_once_with(12345)
        assert (
            upload_url
            == "https://uploads.github.com/repos/owner/repo/releases/12345/assets"
        )

    def test_asset_upload_url_not_found(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ) -> None:
        """Given non-existent release, when getting upload URL, then None is returned"""
        mock_repository.get_release.side_effect = GithubException(
            status=404,
            data={"message": "Not Found"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        upload_url = github_hvcs.asset_upload_url(99999)

        assert upload_url is None


class TestGithubUploadReleaseAsset:
    """Tests for upload_release_asset() method with PyGithub"""

    def test_upload_release_asset_successfully(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
        tmp_path,
    ) -> None:
        """Given valid asset file, when uploading, then asset is uploaded via PyGithub"""
        # Create test asset file
        test_asset = tmp_path / "test.tar.gz"
        test_asset.write_bytes(b"test content")

        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        result = github_hvcs.upload_release_asset(
            release_id=12345,
            file=str(test_asset),
            label="Test Asset",
        )

        mock_repository.get_release.assert_called_once_with(12345)
        mock_release.upload_asset.assert_called_once()

        call_kwargs = mock_release.upload_asset.call_args[1]
        assert call_kwargs["path"] == str(test_asset)
        assert call_kwargs["label"] == "Test Asset"
        # Content type detection can vary by system (application/x-tar or application/gzip)
        assert call_kwargs["content_type"] in ["application/gzip", "application/x-tar"]
        assert result is True

    def test_upload_release_asset_without_label(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
        tmp_path,
    ) -> None:
        """Given no label, when uploading asset, then filename is used as label"""
        test_asset = tmp_path / "my_package.whl"
        test_asset.write_bytes(b"wheel content")

        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        result = github_hvcs.upload_release_asset(
            release_id=12345,
            file=str(test_asset),
        )

        call_kwargs = mock_release.upload_asset.call_args[1]
        assert call_kwargs["label"] == "my_package.whl"
        assert call_kwargs["content_type"] == "application/octet-stream"
        assert result is True

    def test_upload_release_asset_raises_on_github_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
        tmp_path,
    ) -> None:
        """Given upload fails, when uploading asset, then AssetUploadError is raised"""
        test_asset = tmp_path / "test.txt"
        test_asset.write_text("test")

        mock_repository.get_release.return_value = mock_release
        mock_release.upload_asset.side_effect = GithubException(
            status=500,
            data={"message": "Upload failed"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        with pytest.raises(AssetUploadError) as exc_info:
            github_hvcs.upload_release_asset(
                release_id=12345,
                file=str(test_asset),
            )

        assert "Failed to upload" in str(exc_info.value)


class TestGithubCreateOrUpdateRelease:
    """Tests for create_or_update_release() workflow with PyGithub"""

    def test_create_or_update_creates_new_release(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given no existing release, when creating or updating, then new release is created"""
        mock_repository.create_git_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_or_update_release(
            tag="v1.0.0",
            release_notes="New release",
        )

        # Should create new release
        mock_repository.create_git_release.assert_called_once()
        assert release_id == 12345

    def test_create_or_update_updates_existing_release(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
        mock_release: MagicMock,
    ) -> None:
        """Given existing release, when creating or updating, then release is updated"""
        # Simulate create failing with conflict, then update succeeds
        mock_repository.create_git_release.side_effect = GithubException(
            status=409,
            data={"message": "Already exists"},
            headers={},
        )
        mock_repository.get_release.return_value = mock_release

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository

        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        release_id = github_hvcs.create_or_update_release(
            tag="v1.0.0",
            release_notes="Updated release notes",
        )

        # Should attempt create, then get and update
        mock_repository.create_git_release.assert_called_once()
        # get_release is called twice: once to get by tag, once to edit by ID
        assert mock_repository.get_release.call_count == 2
        # First call gets by tag
        assert mock_repository.get_release.call_args_list[0][0] == ("v1.0.0",)
        # Second call gets by ID for updating
        assert mock_repository.get_release.call_args_list[1][0] == (12345,)
        mock_release.update_release.assert_called_once()
        assert release_id == 12345


# ============================================================================
# Test Issue/PR Announcement Methods
# ============================================================================


class TestGithubPostComment:
    """Tests for post_comment() method"""

    def test_post_comment_success(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given valid issue_id and body, when posting comment, then comment is created and ID returned"""
        # Arrange
        issue_id = 123
        comment_body = "Test comment body"
        expected_comment_id = 789

        mock_issue = MagicMock()
        mock_comment = MagicMock()
        mock_comment.id = expected_comment_id
        mock_issue.create_comment.return_value = mock_comment
        mock_repository.get_issue.return_value = mock_issue

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act
        result = github_hvcs.post_comment(issue_id, comment_body)

        # Assert
        mock_repository.get_issue.assert_called_once_with(issue_id)
        mock_issue.create_comment.assert_called_once_with(comment_body)
        assert result == expected_comment_id

    def test_post_comment_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given GithubException when posting comment, when method called, then UnexpectedResponse raised"""
        # Arrange
        issue_id = 123
        comment_body = "Test comment"

        mock_repository.get_issue.side_effect = GithubException(
            status=403,
            data={"message": "Forbidden"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act & Assert
        with pytest.raises(
            UnexpectedResponse, match="Failed to post comment to issue 123"
        ):
            github_hvcs.post_comment(issue_id, comment_body)


class TestGithubCheckIssueState:
    """Tests for check_issue_state() method"""

    def test_check_issue_state_open(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given open issue, when checking state, then 'open' is returned"""
        # Arrange
        issue_id = 456
        mock_issue = MagicMock()
        mock_issue.state = "open"
        mock_repository.get_issue.return_value = mock_issue

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act
        result = github_hvcs.check_issue_state(issue_id)

        # Assert
        mock_repository.get_issue.assert_called_once_with(issue_id)
        assert result == "open"

    def test_check_issue_state_closed(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given closed issue, when checking state, then 'closed' is returned"""
        # Arrange
        issue_id = 789
        mock_issue = MagicMock()
        mock_issue.state = "closed"
        mock_repository.get_issue.return_value = mock_issue

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act
        result = github_hvcs.check_issue_state(issue_id)

        # Assert
        mock_repository.get_issue.assert_called_once_with(issue_id)
        assert result == "closed"

    def test_check_issue_state_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given GithubException when checking state, when method called, then UnexpectedResponse raised"""
        # Arrange
        issue_id = 999
        mock_repository.get_issue.side_effect = GithubException(
            status=404,
            data={"message": "Not Found"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act & Assert
        with pytest.raises(
            UnexpectedResponse, match="Failed to get state of issue 999"
        ):
            github_hvcs.check_issue_state(issue_id)


class TestGithubAddLabelsToIssue:
    """Tests for add_labels_to_issue() method"""

    def test_add_labels_to_issue_success(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given valid issue_id and labels, when adding labels, then labels are added successfully"""
        # Arrange
        issue_id = 111
        labels = ["bug", "enhancement"]
        mock_issue = MagicMock()
        mock_repository.get_issue.return_value = mock_issue

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act
        github_hvcs.add_labels_to_issue(issue_id, labels)

        # Assert
        mock_repository.get_issue.assert_called_once_with(issue_id)
        mock_issue.add_to_labels.assert_called_once_with("bug", "enhancement")

    def test_add_labels_to_issue_single_label(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given single label, when adding labels, then single label is added"""
        # Arrange
        issue_id = 222
        labels = ["released"]
        mock_issue = MagicMock()
        mock_repository.get_issue.return_value = mock_issue

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act
        github_hvcs.add_labels_to_issue(issue_id, labels)

        # Assert
        mock_repository.get_issue.assert_called_once_with(issue_id)
        mock_issue.add_to_labels.assert_called_once_with("released")

    def test_add_labels_to_issue_exception(
        self,
        default_github_url: str,
        default_token: str,
        mocker: MockerFixture,
        mock_repository: MagicMock,
    ):
        """Given GithubException when adding labels, when method called, then UnexpectedResponse raised"""
        # Arrange
        issue_id = 333
        labels = ["invalid-label"]
        mock_repository.get_issue.side_effect = GithubException(
            status=422,
            data={"message": "Validation Failed"},
            headers={},
        )

        mock_github_client = mocker.MagicMock()
        mock_github_client.get_repo.return_value = mock_repository
        mocker.patch(
            "semantic_release.hvcs.github.GithubClient",
            return_value=mock_github_client,
        )

        github_hvcs = Github(
            remote_url=default_github_url,
            token=default_token,
        )

        # Act & Assert
        with pytest.raises(
            UnexpectedResponse, match="Failed to add labels to issue 333"
        ):
            github_hvcs.add_labels_to_issue(issue_id, labels)
