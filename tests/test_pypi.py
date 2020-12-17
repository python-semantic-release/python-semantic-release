from unittest import TestCase

from semantic_release import ImproperConfigurationError
from semantic_release.pypi import upload_to_pypi

from . import mock


class PypiTests(TestCase):
    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict(
        "os.environ", {"PYPI_USERNAME": "username", "PYPI_PASSWORD": "password"}
    )
    def test_upload_with_password(self, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u 'username' -p 'password' \"dist/*\"")],
        )

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_token(self, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u '__token__' -p 'pypi-x' \"dist/*\"")],
        )

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict(
        "os.environ",
        {
            "PYPI_TOKEN": "pypi-x",
            "PYPI_USERNAME": "username",
            "PYPI_PASSWORD": "password",
        },
    )
    def test_upload_prefers_token_over_password(self, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u '__token__' -p 'pypi-x' \"dist/*\"")],
        )

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_custom_path(self, mock_run):
        upload_to_pypi(path="custom-dist")
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u '__token__' -p 'pypi-x' \"custom-dist/*\"")],
        )

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "pypi-x"})
    def test_upload_with_custom_globs(self, mock_run):
        upload_to_pypi(glob_patterns=["*.tar.gz", "*.whl"])
        self.assertEqual(
            mock_run.call_args_list,
            [
                mock.call(
                    "twine upload -u '__token__' -p 'pypi-x' \"dist/*.tar.gz\" \"dist/*.whl\""
                )
            ],
        )

    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "invalid"})
    def test_raises_error_when_token_invalid(self):
        with self.assertRaises(ImproperConfigurationError):
            upload_to_pypi()

    def test_raises_error_when_missing_credentials(self):
        with self.assertRaises(ImproperConfigurationError):
            upload_to_pypi()
