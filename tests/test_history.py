from unittest import TestCase, mock

from semantic_release.history import evaluate_version_bump

MAJOR = ':boom: Breaking changes'
MINOR = ':sparkles: Add awesome feature'
PATCH = ':bug: Fix the annoying bug'

ALL_KINDS_OF_COMMIT_MESSAGES = [MINOR, MAJOR, MINOR, PATCH]
MINOR_AND_PATCH_COMMIT_MESSAGES = [MINOR, PATCH]
PATCH_COMMIT_MESSAGES = [PATCH, PATCH]
MAJOR_LAST_RELEASE_MINOR_AFTER = [MINOR, '1.1.0', MAJOR]


class EvaluateVersionBumpTest(TestCase):
    def test_major(self):
        with mock.patch('semantic_release.history.get_commit_log',
                        lambda: ALL_KINDS_OF_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'major')

    def test_minor(self):
        with mock.patch('semantic_release.history.get_commit_log',
                        lambda: MINOR_AND_PATCH_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'minor')

    def test_patch(self):
        with mock.patch('semantic_release.history.get_commit_log', lambda: PATCH_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'patch')

    def test_nothing_if_no_tag(self):
        with mock.patch('semantic_release.history.get_commit_log', lambda: ['', '...']):
            self.assertIsNone(evaluate_version_bump('0.0.0'))

    def test_force(self):
        self.assertEqual(evaluate_version_bump('0.0.0', 'major'), 'major')
        self.assertEqual(evaluate_version_bump('0.0.0', 'minor'), 'minor')
        self.assertEqual(evaluate_version_bump('0.0.0', 'patch'), 'patch')

    def test_should_account_for_commits_earlier_than_last_commit(self):
        with mock.patch('semantic_release.history.get_commit_log',
                        lambda: MAJOR_LAST_RELEASE_MINOR_AFTER):
            self.assertEqual(evaluate_version_bump('1.1.0'), 'minor')
