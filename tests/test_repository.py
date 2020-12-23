from unittest import TestCase

from semantic_release import ImproperConfigurationError
from semantic_release.repository import get_repository

from . import mock, wrapped_config_get


class RepositoryTests(TestCase):
    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict(
        "os.environ", {"PYPI_USERNAME": "username", "PYPI_PASSWORD": "password"}
    )
    def test_upload_with_password(self, mock_run):
        get_repository().upload()
        mock_run.assert_called_with("twine upload -u 'username' -p 'password' \"dist/*\"")

    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_token(self, mock_run):
        get_repository().upload()
        mock_run.assert_called_with("twine upload -u '__token__' -p 'pypi-x' \"dist/*\"")

    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict(
        "os.environ",
        {
            "PYPI_TOKEN": "pypi-x",
            "PYPI_USERNAME": "username",
            "PYPI_PASSWORD": "password",
            "REPOSITORY_USERNAME": "username",
            "REPOSITORY_PASSWORD": "password",
        },
    )
    def test_upload_prefers_token_over_password(self, mock_run):
        get_repository().upload()
        mock_run.assert_called_with("twine upload -u '__token__' -p 'pypi-x' \"dist/*\"")

    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_custom_path(self, mock_run):
        get_repository().upload(path="custom-dist")
        mock_run.assert_called_with("twine upload -u '__token__' -p 'pypi-x' \"custom-dist/*\"")

    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_custom_globs(self, mock_run):
        get_repository().upload(glob_patterns=["*.tar.gz", "*.whl"])
        mock_run.assert_called_with("twine upload -u '__token__' -p 'pypi-x' \"dist/*.tar.gz\" \"dist/*.whl\"")

    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "invalid"})
    def test_raises_error_when_token_invalid(self):
        with self.assertRaises(ImproperConfigurationError):
            get_repository()

    def test_raises_error_when_missing_credentials(self):
        with self.assertRaises(ImproperConfigurationError):
            get_repository()

    @mock.patch("semantic_release.repository.run")
    @mock.patch.dict("os.environ", {"REPOSITORY_USERNAME": "username", "REPOSITORY_PASSWORD": "password"})
    @mock.patch("semantic_release.repository.config.get", wrapped_config_get(repository_url='http://my-corp-repo'))
    def test_upload_with_a_custom_repository(self, mock_run):
        get_repository().upload()
        mock_run.assert_called_with(
            "twine upload -u 'username' -p 'password' --repository-url 'http://my-corp-repo' \"dist/*\"")

    @mock.patch.dict("os.environ", {"REPOSITORY_USERNAME": "username"})
    def test_raise_when_missing_password_for_corp_repository(self):
        with self.assertRaises(ImproperConfigurationError):
            get_repository()

