from unittest import TestCase

from semantic_release.pypi import upload_to_pypi

from . import mock


class PypiTests(TestCase):
    @mock.patch('semantic_release.pypi.run')
    @mock.patch('twine.commands.upload.upload')
    def test_upload_without_arguments(self, mock_upload, mock_run):
        upload_to_pypi()
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call('python setup.py sdist bdist_wheel'), mock.call('rm -rf build dist')]
        )
        mock_upload.assert_called_once_with(
            dists=['dist/*'],
            repository='pypi',
            sign=False,
            identity=None,
            username=None,
            password=None,
            comment=None,
            sign_with='gpg'
        )

    @mock.patch('semantic_release.pypi.run')
    @mock.patch('twine.commands.upload.upload')
    def test_upload_with_arguments(self, mock_upload, mock_run):
        upload_to_pypi(dists='sdist')
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call('python setup.py sdist'), mock.call('rm -rf build dist')]
        )
        self.assertTrue(mock_upload.called)
