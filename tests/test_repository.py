from pathlib import Path
from unittest import TestCase, mock

import pytest
from twine import auth

from semantic_release import ImproperConfigurationError
from semantic_release.repository import ArtifactRepo
from tests import wrapped_config_get

import os


class RepositoryTests(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_upload_enabled(self):
        self.assertTrue(ArtifactRepo.upload_enabled())

    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(upload_to_repository=False),
    )
    def test_upload_enabled_with_upload_to_repository_false(self):
        self.assertFalse(ArtifactRepo.upload_enabled())

    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(upload_to_pypi=False),
    )
    def test_upload_enabled_with_upload_to_pypi_false(self):
        self.assertFalse(ArtifactRepo.upload_enabled())

    @mock.patch.dict(
        "os.environ",
        {"PYPI_USERNAME": "pypi-username", "PYPI_PASSWORD": "pypi-password"},
    )
    def test_repo_with_pypi_credentials(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.username, "pypi-username")
        self.assertEqual(repo.password, "pypi-password")

    @mock.patch.dict(
        "os.environ",
        {
            "REPOSITORY_USERNAME": "repo-username",
            "REPOSITORY_PASSWORD": "repo-password",
        },
    )
    def test_repo_with_repository_credentials(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.username, "repo-username")
        self.assertEqual(repo.password, "repo-password")

    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-token"})
    def test_repo_with_token_only(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertIn(
            "Providing only password or token without username is deprecated",
            self._caplog.messages,
        )
        self.assertEqual(repo.username, "__token__")
        self.assertEqual(repo.password, "pypi-token")

    @mock.patch.dict("os.environ", {"PYPI_PASSWORD": "pypi-password"})
    def test_repo_with_pypi_password_only(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertIn(
            "Providing only password or token without username is deprecated",
            self._caplog.messages,
        )
        self.assertEqual(repo.username, "__token__")
        self.assertEqual(repo.password, "pypi-password")

    @mock.patch.dict("os.environ", {"REPOSITORY_PASSWORD": "repo-password"})
    def test_repo_with_repository_password_only(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.username, "__token__")
        self.assertEqual(repo.password, "repo-password")

    @mock.patch("semantic_release.repository.Path.exists", return_value=True)
    def test_repo_with_pypirc_file(self, mock_path_exists):
        repo = ArtifactRepo(Path("dist"))
        self.assertIsNone(repo.username)
        self.assertIsNone(repo.password)

    @mock.patch("semantic_release.repository.Path.exists", return_value=False)
    def test_repo_without_pypirc_file(self, mock_path_exists):
        with self.assertRaises(ImproperConfigurationError) as cm:
            ArtifactRepo(Path("dist"))
        self.assertEqual(
            str(cm.exception),
            "Missing credentials for uploading to artifact repository",
        )

    @mock.patch.dict(
        "os.environ",
        {
            "PYPI_TOKEN": "pypi-token",
            "PYPI_USERNAME": "pypi-username",
            "PYPI_PASSWORD": "pypi-password",
            "REPOSITORY_USERNAME": "repo-username",
            "REPOSITORY_PASSWORD": "repo-password",
        },
    )
    def test_repo_prefers_repository_over_pypi(self):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.username, "repo-username")
        self.assertEqual(repo.password, "repo-password")

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    def test_repo_with_custom_dist_path(self, mock_handle_creds):
        repo = ArtifactRepo(Path("custom-dist"))
        self.assertEqual(repo.dists, [os.path.join("custom-dist", "*")])

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(dist_glob_patterns="*.tar.gz,*.whl"),
    )
    def test_repo_with_custom_dist_globs(self, mock_handle_creds):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.dists, [os.path.join("dist", "*.tar.gz"), os.path.join("dist", "*.whl")])

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(upload_to_pypi_glob_patterns="*.tar.gz,*.whl"),
    )
    def test_repo_with_custom_pypi_globs(self, mock_handle_creds):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.dists, [os.path.join("dist", "*.tar.gz"), os.path.join("dist", "*.whl")])

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(repository="testpypi"),
    )
    def test_repo_with_repo_name_testpypi(self, mock_handle_creds):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.repository_name, "testpypi")

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(repository="invalid"),
    )
    def test_raises_error_when_repo_name_invalid(self, mock_handle_creds):
        repo = ArtifactRepo(Path("dist"))
        with self.assertRaises(
            ImproperConfigurationError, msg="Upload to artifact repository has failed"
        ):
            repo.upload(noop=False, verbose=False, skip_existing=False)

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(repository_url="https://custom-repo"),
    )
    def test_repo_with_custom_repo_url(self, mock_handle_creds):
        repo = ArtifactRepo(Path("dist"))
        self.assertEqual(repo.repository_url, "https://custom-repo")

    @mock.patch("semantic_release.repository.twine_upload")
    @mock.patch(
        "semantic_release.repository.config.get",
        wrapped_config_get(
            dist_glob_patterns="*.tar.gz,*.whl", repository_url="https://custom-repo"
        ),
    )
    @mock.patch.dict(
        "os.environ",
        {
            "REPOSITORY_USERNAME": "repo-username",
            "REPOSITORY_PASSWORD": "repo-password",
        },
    )
    def test_upload_with_custom_settings(self, mock_upload):
        repo = ArtifactRepo(Path("custom-dist"))
        repo.upload(
            noop=False, verbose=True, skip_existing=True, comment="distribution comment"
        )
        settings = mock_upload.call_args[1]["upload_settings"]
        self.assertIsInstance(settings.auth, auth.Private)
        self.assertEqual(settings.comment, "distribution comment")
        self.assertEqual(settings.username, "repo-username")
        self.assertEqual(settings.password, "repo-password")
        self.assertEqual(
            settings.repository_config["repository"], "https://custom-repo"
        )
        self.assertTrue(settings.skip_existing)
        self.assertTrue(settings.verbose)
        self.assertTrue(mock_upload.called)

    @mock.patch.object(ArtifactRepo, "_handle_credentials_init")
    @mock.patch("semantic_release.repository.twine_upload")
    def test_upload_with_noop(self, mock_upload, mock_handle_creds):
        ArtifactRepo(Path("dist")).upload(noop=True, verbose=False, skip_existing=False)
        self.assertFalse(mock_upload.called)
