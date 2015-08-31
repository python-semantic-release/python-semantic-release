from unittest.case import TestCase

from click.testing import CliRunner

from semantic_release.cli import main

from . import mock


class CLITests(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('semantic_release.cli.version')
    def test_main_should_call_correct_function(self, mock_version):
        result = self.runner.invoke(main, ['version'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level=None)
        self.assertEqual(result.exit_code, 0)

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
        mock_current_version.assert_called_once_with()
        mock_evaluate_bump.assert_called_once_with('1.2.3', None)
        mock_new_version.assert_called_once_with('1.2.3', 'major')
        mock_set_new_version.assert_called_once_with('2.0.0')
        mock_commit_new_version.assert_called_once_with('2.0.0')
        mock_tag_new_version.assert_called_once_with('2.0.0')
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.version')
    def test_force_major(self, mock_version):
        result = self.runner.invoke(main, ['version', '--major'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level='major')
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'major')
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.version')
    def test_force_minor(self, mock_version):
        result = self.runner.invoke(main, ['version', '--minor'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level='minor')
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'minor')
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.version')
    def test_force_patch(self, mock_version):
        result = self.runner.invoke(main, ['version', '--patch'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level='patch')
        self.assertEqual(mock_version.call_args_list[0][1]['force_level'], 'patch')
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_noop_mode(self, mock_set_new, mock_commit_new, mock_tag_new_version):
        result = self.runner.invoke(main, ['version', '--noop'])
        self.assertFalse(mock_set_new.called)
        self.assertFalse(mock_commit_new.called)
        self.assertFalse(mock_tag_new_version.called)
        self.assertEqual(result.exit_code, 0)

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
        mock_current_version.assert_called_once_with()
        mock_evaluate_bump.assert_called_once_with('1.2.3', None)
        mock_new_version.assert_called_once_with('1.2.3', None)
        self.assertFalse(mock_set_new_version.called)
        self.assertFalse(mock_commit_new_version.called)
        self.assertFalse(mock_tag_new_version.called)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    @mock.patch('semantic_release.cli.check_build_status', return_value=False)
    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_version_check_build_status_fails(self, mock_set_new, mock_commit_new,
                                              mock_tag_new_version, mock_check_build_status):
        result = self.runner.invoke(main, ['version'])
        self.assertTrue(mock_check_build_status.called)
        self.assertFalse(mock_set_new.called)
        self.assertFalse(mock_commit_new.called)
        self.assertFalse(mock_tag_new_version.called)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    @mock.patch('semantic_release.cli.check_build_status', return_value=True)
    @mock.patch('semantic_release.cli.tag_new_version')
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version')
    @mock.patch('semantic_release.cli.set_new_version')
    def test_version_check_build_status_succeeds(self, mock_set_new, mock_commit_new,
                                                 mock_tag_new_version, mock_check_build_status):
        result = self.runner.invoke(main, ['version'])
        self.assertTrue(mock_check_build_status.called)
        self.assertTrue(mock_set_new.called)
        self.assertTrue(mock_commit_new.called)
        self.assertTrue(mock_tag_new_version.called)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    @mock.patch('semantic_release.cli.check_build_status')
    @mock.patch('semantic_release.cli.tag_new_version', None)
    @mock.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    @mock.patch('semantic_release.cli.commit_new_version', None)
    @mock.patch('semantic_release.cli.set_new_version', None)
    def test_version_check_build_status_not_called_if_disabled(self, mock_check_build_status):
        self.runner.invoke(main, ['version'])
        self.assertFalse(mock_check_build_status.called)

    @mock.patch('semantic_release.cli.post_changelog')
    @mock.patch('semantic_release.cli.upload_to_pypi')
    @mock.patch('semantic_release.cli.push_new_version')
    @mock.patch('semantic_release.cli.version', return_value=False)
    def test_publish_should_do_nothing(self, mock_version, mock_push, mock_upload, mock_log):
        result = self.runner.invoke(main, ['publish'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level=None)
        self.assertFalse(mock_push.called)
        self.assertFalse(mock_upload.called)
        self.assertFalse(mock_log.called)
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.post_changelog')
    @mock.patch('semantic_release.cli.upload_to_pypi')
    @mock.patch('semantic_release.cli.push_new_version')
    @mock.patch('semantic_release.cli.version', return_value=True)
    @mock.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    @mock.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    @mock.patch('semantic_release.cli.check_token', lambda: True)
    def test_publish_should_call_functions(self, mock_version, mock_push, mock_upload, mock_log):
        result = self.runner.invoke(main, ['publish'])
        mock_version.assert_called_once_with(noop=False, post=False, force_level=None)
        mock_push.assert_called_once_with()
        mock_upload.assert_called_once_with()
        mock_log.assert_called_once_with('relekang', 'python-semantic-release', '2.0.0', 'CHANGES')
        self.assertEqual(result.exit_code, 0)

    @mock.patch('semantic_release.cli.post_changelog', lambda *x: True)
    @mock.patch('semantic_release.cli.upload_to_pypi')
    @mock.patch('semantic_release.cli.push_new_version', lambda *x: True)
    @mock.patch('semantic_release.cli.version', lambda: True)
    @mock.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    @mock.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    @mock.patch('semantic_release.cli.check_token', lambda: True)
    @mock.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    def test_publish_should_not_upload_to_pypi_if_option_is_false(self, mock_upload):
        self.runner.invoke(main, ['publish'])
        self.assertFalse(mock_upload.called)

    @mock.patch('semantic_release.cli.changelog', return_value=True)
    def test_changelog_should_call_functions(self, mock_changelog):
        result = self.runner.invoke(main, ['changelog'])
        self.assertEqual(result.exit_code, 0)
        mock_changelog.assert_called_once_with(noop=False, post=False, force_level=None)
