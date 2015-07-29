from unittest import TestCase, mock

from invoke.runner import Result

from semantic_release.git_helpers import (commit_new_version, get_commit_log, push_new_version,
                                          tag_new_version)


class GitHelpersTests(TestCase):

    def test_first_commit_is_not_initial_commit(self):
        self.assertNotEqual(next(get_commit_log()), 'Initial commit')

    @mock.patch('semantic_release.git_helpers.run',
                return_value=Result(stdout='', stderr='', pty='', exited=0))
    def test_add_and_commit(self, mock_run):
        commit_new_version('1.0.0')
        self.assertEqual(
            mock_run.call_args_list,
            [mock.call('git add semantic_release/__init__.py', hide=True),
             mock.call('git commit -m "1.0.0"', hide=True)]
        )

    @mock.patch('semantic_release.git_helpers.run')
    def test_tag_new_version(self, mock_run):
        tag_new_version('1.0.0')
        mock_run.assert_called_with('git tag v1.0.0 HEAD', hide=True)

    @mock.patch('semantic_release.git_helpers.run')
    def test_push_new_version(self, mock_run):
        push_new_version()
        mock_run.assert_called_with('git push && git push --tags', hide=True)
