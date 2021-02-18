import os
import tempfile
from unittest import TestCase

from semantic_release import ImproperConfigurationError
from semantic_release.pypi import upload_to_pypi

from . import mock, wrapped_config_get


class PypiTests(TestCase):
    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict(
        "os.environ",
        {"PYPI_USERNAME": "username", "PYPI_PASSWORD": "password", "HOME": "/tmp/1234"},
    )
    def test_upload_with_password(self, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u 'username' -p 'password' \"dist/*\"")],
        )

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict(
        "os.environ",
        {"PYPI_USERNAME": "username", "PYPI_PASSWORD": "password", "HOME": "/tmp/1234"},
    )
    @mock.patch(
        "semantic_release.pypi.config.get", wrapped_config_get(repository="corp-repo")
    )
    def test_upload_with_repository(self, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [
                mock.call(
                    "twine upload -u 'username' -p 'password' -r 'corp-repo' \"dist/*\""
                )
            ],
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

    @mock.patch("semantic_release.pypi.run")
    @mock.patch.dict("os.environ", {})
    def test_upload_with_pypirc_file_exists(self, mock_run):
        tmpdir = tempfile.mkdtemp()
        os.environ["HOME"] = tmpdir
        with open(os.path.join(tmpdir, ".pypirc"), "w") as pypirc_fp:
            pypirc_fp.write("hello")
        upload_to_pypi(path="custom-dist")
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call('twine upload  "custom-dist/*"')],
        )

    @mock.patch.dict("os.environ", {"PYPI_TOKEN": "invalid"})
    def test_raises_error_when_token_invalid(self):
        with self.assertRaises(ImproperConfigurationError):
            upload_to_pypi()

    @mock.patch.dict("os.environ", {"HOME": "/tmp/1234"})
    def test_raises_error_when_missing_credentials(self):
        with self.assertRaises(ImproperConfigurationError):
            upload_to_pypi()
