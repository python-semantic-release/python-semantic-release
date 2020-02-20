from unittest import TestCase

from semantic_release import ImproperConfigurationError
from semantic_release.pypi import upload_to_pypi

from . import mock


class PypiTests(TestCase):
    @mock.patch('semantic_release.pypi.run')
    def test_upload_without_arguments(self, mock_run):
        upload_to_pypi(username='username', password='password')
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u 'username' -p 'password'  \"dist/*\"")]
        )

    @mock.patch('semantic_release.pypi.run')
    def test_upload_with_custom_path(self, mock_run):
        upload_to_pypi(path='custom-dist', username='username', password='password')
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call("twine upload -u 'username' -p 'password'  \"custom-dist/*\"")]
        )

    def test_raises_error_when_missing_credentials(self):
        with self.assertRaises(ImproperConfigurationError):
            upload_to_pypi()
