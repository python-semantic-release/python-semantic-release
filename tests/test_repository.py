import os
from pathlib import Path
from unittest import TestCase, mock

import pytest
from twine import auth

from semantic_release import ImproperConfigurationError
from semantic_release.repository import ArtifactRepo
from tests import wrapped_config_get


def test_upload_enabled():
    assert ArtifactRepo.upload_enabled()


@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(upload_to_repository=False),
)
def test_upload_enabled_with_upload_to_repository_false():
    assert not ArtifactRepo.upload_enabled()


@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(upload_to_pypi=False),
)
def test_upload_enabled_with_upload_to_pypi_false():
    assert not ArtifactRepo.upload_enabled()


@mock.patch.dict(
    "os.environ",
    {"PYPI_USERNAME": "pypi-username", "PYPI_PASSWORD": "pypi-password"},
)
def test_repo_with_pypi_credentials():
    repo = ArtifactRepo(Path("dist"))
    assert repo.username == "pypi-username"
    assert repo.password == "pypi-password"


@mock.patch.dict(
    "os.environ",
    {
        "REPOSITORY_USERNAME": "repo-username",
        "REPOSITORY_PASSWORD": "repo-password",
    },
)
def test_repo_with_repository_credentials():
    repo = ArtifactRepo(Path("dist"))
    assert repo.username == "repo-username"
    assert repo.password == "repo-password"


@mock.patch.dict("os.environ", {"REPOSITORY_PASSWORD": "repo-password"})
def test_repo_with_repository_password_only():
    repo = ArtifactRepo(Path("dist"))
    assert repo.username == "__token__"
    assert repo.password == "repo-password"


@mock.patch("semantic_release.repository.Path.exists", return_value=True)
def test_repo_with_pypirc_file(mock_path_exists):
    repo = ArtifactRepo(Path("dist"))
    assert repo.username is None
    assert repo.password is None


@mock.patch("semantic_release.repository.Path.exists", return_value=False)
def test_repo_without_pypirc_file(mock_path_exists):
    with pytest.raises(ImproperConfigurationError) as cm:
        ArtifactRepo(Path("dist"))
    assert str(cm.value) == "Missing credentials for uploading to artifact repository"


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
def test_repo_prefers_repository_over_pypi():
    repo = ArtifactRepo(Path("dist"))
    assert repo.username == "repo-username"
    assert repo.password == "repo-password"


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
def test_repo_with_custom_dist_path(mock_handle_creds):
    repo = ArtifactRepo(Path("custom-dist"))
    assert repo.dists == [os.path.join("custom-dist", "*")]


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(dist_glob_patterns="*.tar.gz,*.whl"),
)
def test_repo_with_custom_dist_globs(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    assert repo.dists == [
        os.path.join("dist", "*.tar.gz"),
        os.path.join("dist", "*.whl"),
    ]


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(upload_to_pypi_glob_patterns="*.tar.gz,*.whl"),
)
def test_repo_with_custom_pypi_globs(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    assert repo.dists == [
        os.path.join("dist", "*.tar.gz"),
        os.path.join("dist", "*.whl"),
    ]


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(repository="testpypi"),
)
def test_repo_with_repo_name_testpypi(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    assert repo.repository_name == "testpypi"


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(repository="invalid"),
)
def test_raises_error_when_repo_name_invalid(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    with pytest.raises(
        ImproperConfigurationError, match="Upload to artifact repository has failed"
    ):
        repo.upload(noop=False, verbose=False, skip_existing=False)


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch(
    "semantic_release.repository.config.get",
    wrapped_config_get(repository_url="https://custom-repo"),
)
def test_repo_with_custom_repo_url(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    assert repo.repository_url == "https://custom-repo"


@mock.patch.dict("os.environ", {"REPOSITORY_URL": "https://custom-repo"})
@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
def test_repo_with_custom_repo_url_from_env(mock_handle_creds):
    repo = ArtifactRepo(Path("dist"))
    assert repo.repository_url == "https://custom-repo"


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
        "TWINE_CERT": "cert_bundle.crt",
    },
)
@mock.patch("semantic_release.repository.Path.is_file", return_value=True)
def test_upload_with_custom_settings(mock_is_file, mock_upload):
    repo = ArtifactRepo(Path("custom-dist"))
    repo.upload(
        noop=False, verbose=True, skip_existing=True, comment="distribution comment"
    )
    settings = mock_upload.call_args[1]["upload_settings"]
    assert isinstance(settings.auth, auth.Private)
    assert settings.comment == "distribution comment"
    assert settings.cacert == "cert_bundle.crt"
    assert settings.username == "repo-username"
    assert settings.password == "repo-password"
    assert settings.repository_config["repository"] == "https://custom-repo"
    assert settings.skip_existing
    assert settings.verbose
    assert mock_upload.called


@mock.patch.dict(
    "os.environ",
    {
        "TWINE_CERT": "cert_bundle.crt",
    },
)
@mock.patch("semantic_release.repository.Path.is_file", return_value=False)
@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
def test_upload_with_invalid_twine_cert(mock_is_file, mock_handle_creds):
    repo = ArtifactRepo(Path("custom-dist"))

    with pytest.raises(ImproperConfigurationError) as ex:
        repo.upload(noop=False, verbose=True, skip_existing=True)

    assert "TWINE_CERT env variable set, but file does not exist" in str(ex.value)


@mock.patch.object(ArtifactRepo, "_handle_credentials_init")
@mock.patch("semantic_release.repository.twine_upload")
def test_upload_with_noop(mock_upload, mock_handle_creds):
    ArtifactRepo(Path("dist")).upload(noop=True, verbose=False, skip_existing=False)
    assert not mock_upload.called


@mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-token"})
def test_repo_with_token_only(caplog):
    repo = ArtifactRepo(Path("dist"))
    assert (
        "Providing only password or token without username is deprecated"
        in caplog.messages
    )
    assert repo.username == "__token__"
    assert repo.password == "pypi-token"


@mock.patch.dict("os.environ", {"PYPI_PASSWORD": "pypi-password"})
def test_repo_with_pypi_password_only(caplog):
    repo = ArtifactRepo(Path("dist"))
    assert (
        "Providing only password or token without username is deprecated"
        in caplog.messages
    )
    assert repo.username == "__token__"
    assert repo.password == "pypi-password"
