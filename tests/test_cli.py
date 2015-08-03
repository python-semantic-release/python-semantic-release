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

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    @mock.patch('semantic_release.cli.get_new_version', return_value='2.0.0')
    @mock.patch('semantic_release.cli.evaluate_version_bump', return_value='major')
    @mock.patch('semantic_release.cli.get_current_version', return_value='1.2.3')
    def test_version_should_call_correct_functions(self, mock_current_version, mock_evaluate_bump,
                                                   mock_new_version, mock_set_new_version,
                                                   mock_commit_new_version, mock_tag_new_version):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        mock_current_version.assert_called_once_with()
        mock_evaluate_bump.assert_called_once_with('1.2.3', None)
        mock_new_version.assert_called_once_with('1.2.3', 'major')
        mock_set_new_version.assert_called_once_with('2.0.0')
        mock_commit_new_version.assert_called_once_with('2.0.0')
        mock_tag_new_version.assert_called_once_with('2.0.0')

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

    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_noop_mode(self, mock_set_new, mock_commit_new, mock_tag_new_version):
        result = self.runner.invoke(main, ['version', '--noop'])
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(mock_set_new.called)
        self.assertFalse(mock_commit_new.called)
        self.assertFalse(mock_tag_new_version.called)

    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    @mock.patch('semantic_release.cli.get_new_version', return_value='1.2.3')
    @mock.patch('semantic_release.cli.evaluate_version_bump', return_value=None)
    @mock.patch('semantic_release.cli.get_current_version', return_value='1.2.3')
    def test_version_no_change(self, mock_current_version, mock_evaluate_bump,
                               mock_new_version, mock_set_new_version,
                               mock_commit_new_version, mock_tag_new_version):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        mock_current_version.assert_called_once_with()
        mock_evaluate_bump.assert_called_once_with('1.2.3', None)
        mock_new_version.assert_called_once_with('1.2.3', None)
        self.assertFalse(mock_set_new_version.called)
        self.assertFalse(mock_commit_new_version.called)
        self.assertFalse(mock_tag_new_version.called)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    @mock.patch('semantic_release.cli.check_build_status', return_value=False)
    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_version_check_build_status_fails(self, mock_set_new, mock_commit_new,
                                              mock_tag_new_version, mock_check_build_status):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_check_build_status.called)
        self.assertFalse(mock_set_new.called)
        self.assertFalse(mock_commit_new.called)
        self.assertFalse(mock_tag_new_version.called)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    @mock.patch('semantic_release.cli.check_build_status', return_value=True)
    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_version_check_build_status_succeeds(self, mock_set_new, mock_commit_new,
                                                 mock_tag_new_version, mock_check_build_status):
        result = self.runner.invoke(main, ['version'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_check_build_status.called)
        self.assertTrue(mock_set_new.called)
        self.assertTrue(mock_commit_new.called)
        self.assertTrue(mock_tag_new_version.called)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    @mock.patch('semantic_release.cli.check_build_status')
    @mock.patch('semantic_release.cli.tag_new_version', None)
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version', None)
    @mock.patch('semantic_release.cli.set_new_version', None)
    def test_version_check_build_status_not_called_if_disabled(self, mock_check_build_status):
        self.runner.invoke(main, ['version'])
        self.assertFalse(mock_check_build_status.called)

    @mock.patch('semantic_release.cli.upload_to_pypi')
    @mock.patch('semantic_release.cli.push_new_version')
    @mock.patch('semantic_release.cli.version', return_value=False)
    def test_publish_should_do_nothing(self, mock_version, mock_push, mock_upload):
        result = self.runner.invoke(main, ['publish'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()
        self.assertFalse(mock_push.called)
        self.assertFalse(mock_upload.called)

    @mock.patch('semantic_release.cli.upload_to_pypi')
    @mock.patch('semantic_release.cli.push_new_version')
    @mock.patch('semantic_release.cli.version', return_value=True)
    def test_publish_should_call_functions(self, mock_version, mock_push, mock_upload):
        result = self.runner.invoke(main, ['publish'])
        self.assertEqual(result.exit_code, 0)
        mock_version.assert_called_once()
        mock_push.assert_called_once()
        mock_upload.assert_called_once()
