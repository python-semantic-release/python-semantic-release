from unittest import mock
from unittest.case import TestCase

from click.testing import CliRunner

from semantic_release.cli import main


class CLITests(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('semantic_release.cli.version')
    def test_main_should_call_correct_function(self, mock_version):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()

    @mock.patch('semantic_release.cli.set_new_version')
    @mock.patch('semantic_release.cli.get_new_version', return_value='2.0.0')
    @mock.patch('semantic_release.cli.evaluate_version_bump', return_value='major')
    @mock.patch('semantic_release.cli.get_current_version', return_value='1.2.3')
    def test_version_should_call_correct_functions(self, mock_current_version, mock_evaluate_bump,
                                                   mock_new_version, mock_set_new_version):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        mock_current_version.assert_called_once_with()
        mock_evaluate_bump.assert_called_once_with('1.2.3', None)
        mock_new_version.assert_called_once_with('1.2.3', 'major')
        mock_set_new_version.assert_called_once_with('2.0.0')

    @mock.patch('semantic_release.cli.version')
    def test_force_major(self, mock_version):
        result = self.runner.invoke(main, ['version', '--major'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'major')

    @mock.patch('semantic_release.cli.version')
    def test_force_minor(self, mock_version):
        result = self.runner.invoke(main, ['version', '--minor'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'minor')

    @mock.patch('semantic_release.cli.version')
    def test_force_patch(self, mock_version):
        result = self.runner.invoke(main, ['version', '--patch'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'patch')
