from unittest import TestCase

from semantic_release.pypi import upload_to_pypi

from . import mock


class PypiTests(TestCase):
    @mock.patch('semantic_release.pypi.run')
    def test_upload_without_arguments(self, mock_run):
        upload_to_pypi(username='username', password='password')
        self.assertEqual(
            mock_run.call_args_list,
            [
                mock.call('rm -rf build dist'),
                mock.call('python setup.py sdist bdist_wheel'),
                mock.call('twine upload -u username -p password  dist/*'),
                mock.call('rm -rf build dist')
            ]
        )
