from unittest import TestCase

import semantic_release
from semantic_release.history import evaluate_version_bump, get_current_version, get_new_version

from . import mock

MAJOR = ':boom: Breaking changes'
MINOR = ':sparkles: Add awesome feature'
PATCH = ':bug: Fix the annoying bug'
NO_TAG = 'Fix docs'

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

    @mock.patch('semantic_release.history.config.getboolean', lambda *x: True)
    @mock.patch('semantic_release.history.get_commit_log', lambda: [NO_TAG])
    def test_should_patch_without_tagged_commits(self):
        self.assertEqual(evaluate_version_bump('1.1.0'), 'patch')

    @mock.patch('semantic_release.history.config.getboolean', lambda *x: False)
    @mock.patch('semantic_release.history.get_commit_log', lambda: [NO_TAG])
    def test_should_return_none_without_tagged_commits(self):
        self.assertIsNone(evaluate_version_bump('1.1.0'))

    @mock.patch('semantic_release.history.get_commit_log', lambda: [])
    def test_should_return_none_without_commits(self):
        """
        Make sure that we do not release if there are no commits since last release.
        """
        with mock.patch('semantic_release.history.config.getboolean', lambda *x: True):
            self.assertIsNone(evaluate_version_bump('1.1.0'))

        with mock.patch('semantic_release.history.config.getboolean', lambda *x: False):
            self.assertIsNone(evaluate_version_bump('1.1.0'))


class GetCurrentVersionTests(TestCase):
    def test_should_return_correct_version(self):
        self.assertEqual(get_current_version(), semantic_release.__version__)


class GetNewVersionTests(TestCase):
    def test_major_bump(self):
        self.assertEqual(get_new_version('0.0.0', 'major'), '1.0.0')
        self.assertEqual(get_new_version('0.1.0', 'major'), '1.0.0')
        self.assertEqual(get_new_version('0.1.9', 'major'), '1.0.0')
        self.assertEqual(get_new_version('10.1.0', 'major'), '11.0.0')

    def test_minor_bump(self):
        self.assertEqual(get_new_version('0.0.0', 'minor'), '0.1.0')
        self.assertEqual(get_new_version('1.2.0', 'minor'), '1.3.0')
        self.assertEqual(get_new_version('1.2.1', 'minor'), '1.3.0')
        self.assertEqual(get_new_version('10.1.0', 'minor'), '10.2.0')

    def test_patch_bump(self):
        self.assertEqual(get_new_version('0.0.0', 'patch'), '0.0.1')
        self.assertEqual(get_new_version('0.1.0', 'patch'), '0.1.1')
        self.assertEqual(get_new_version('10.0.9', 'patch'), '10.0.10')

    def test_None_bump(self):
        self.assertEqual(get_new_version('1.0.0', None), '1.0.0')
