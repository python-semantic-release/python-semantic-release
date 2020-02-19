from unittest import TestCase

import semantic_release
from semantic_release.history import (evaluate_version_bump, get_current_version,
                                      get_current_version_by_tag, get_new_version,
                                      get_previous_version, replace_version_string, set_new_version)
from semantic_release.history.logs import generate_changelog, markdown_changelog

from . import mock
from .mocks import mock_version_file

MAJOR = (
    '221',
    'feat(x): Add super-feature\n\n'
    'BREAKING CHANGE: Uses super-feature as default instead of dull-feature.')
MAJOR2 = (
    '222',
    'feat(x): Add super-feature\n\nSome explanation\n\n'
    'BREAKING CHANGE: Uses super-feature as default instead of dull-feature.'
)
MAJOR_MENTIONING_1_0_0 = (
    '223',
    'feat(x): Add super-feature\n\nSome explanation\n\n'
    'BREAKING CHANGE: Uses super-feature as default instead of dull-feature from v1.0.0.'
)
MAJOR_EXCL_WITH_FOOTER = (
    '231',
    'feat(x)!: Add another feature\n\n'
    'BREAKING CHANGE: Another feature, another breaking change'
)
MAJOR_EXCL_NOT_FOOTER = (
    '232',
    'fix!: Fix a big bug that everyone exploited\n\nThis is the reason you should not exploit bugs'
)
MINOR = ('111', 'feat(x): Add non-breaking super-feature')
PATCH = ('24', 'fix(x): Fix bug in super-feature')
NO_TAG = ('191', 'docs(x): Add documentation for super-feature')
UNKNOWN_STYLE = ('7', 'random commits are the worst')

ALL_KINDS_OF_COMMIT_MESSAGES = [MINOR, MAJOR, MINOR, PATCH]
MINOR_AND_PATCH_COMMIT_MESSAGES = [MINOR, PATCH]
PATCH_COMMIT_MESSAGES = [PATCH, PATCH]
MAJOR_LAST_RELEASE_MINOR_AFTER = [MINOR, ('22', '1.1.0'), MAJOR]
MAJOR_MENTIONING_LAST_VERSION = [MAJOR_MENTIONING_1_0_0, ('22', '1.0.0'), MAJOR]

PATCH_WIHTOUT_TAG = ('semantic_release', 'patch_without_tag')


class EvaluateVersionBumpTest(TestCase):
    def test_major(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: ALL_KINDS_OF_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'major')

    def test_minor(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: MINOR_AND_PATCH_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'minor')

    def test_patch(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: PATCH_COMMIT_MESSAGES):
            self.assertEqual(evaluate_version_bump('0.0.0'), 'patch')

    def test_nothing_if_no_tag(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: [('', '...')]):
            self.assertIsNone(evaluate_version_bump('0.0.0'))

    def test_force(self):
        self.assertEqual(evaluate_version_bump('0.0.0', 'major'), 'major')
        self.assertEqual(evaluate_version_bump('0.0.0', 'minor'), 'minor')
        self.assertEqual(evaluate_version_bump('0.0.0', 'patch'), 'patch')

    def test_should_not_skip_commits_mentioning_other_commits(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: MAJOR_MENTIONING_LAST_VERSION):
            self.assertEqual(evaluate_version_bump('1.0.0'), 'major')

    @mock.patch('semantic_release.history.config.getboolean', lambda *x: x == PATCH_WIHTOUT_TAG)
    @mock.patch('semantic_release.history.logs.get_commit_log', lambda *a, **kw: [MINOR])
    def test_should_minor_with_patch_without_tag(self):
        self.assertEqual(evaluate_version_bump('1.1.0'), 'minor')

    @mock.patch('semantic_release.history.config.getboolean', lambda *x: x == PATCH_WIHTOUT_TAG)
    @mock.patch('semantic_release.history.logs.get_commit_log', lambda *a, **kw: [NO_TAG])
    def test_should_patch_without_tagged_commits(self):
        self.assertEqual(evaluate_version_bump('1.1.0'), 'patch')

    @mock.patch('semantic_release.history.config.getboolean', lambda *x: x != PATCH_WIHTOUT_TAG)
    @mock.patch('semantic_release.history.logs.get_commit_log', lambda *a, **kw: [NO_TAG])
    def test_should_return_none_without_tagged_commits(self):
        self.assertIsNone(evaluate_version_bump('1.1.0'))

    @mock.patch('semantic_release.history.logs.get_commit_log', lambda *a, **kw: [])
    def test_should_return_none_without_commits(self):
        """
        Make sure that we do not release if there are no commits since last release.
        """
        with mock.patch('semantic_release.history.config.getboolean', lambda *x: True):
            self.assertIsNone(evaluate_version_bump('1.1.0'))

        with mock.patch('semantic_release.history.config.getboolean', lambda *x: False):
            self.assertIsNone(evaluate_version_bump('1.1.0'))

    def test_version_bump_maintains_formatting(self):
        self.assertEqual(replace_version_string('ver="1.2.3"', 'ver', '1.2.4'), 'ver="1.2.4"')
        self.assertEqual(replace_version_string(
            "version = '1.2.3'", 'version', '1.2.4'),
            "version = '1.2.4'"
        )


class GenerateChangelogTests(TestCase):
    def test_should_generate_all_sections(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **k: ALL_KINDS_OF_COMMIT_MESSAGES + [MAJOR2, UNKNOWN_STYLE]):
            changelog = generate_changelog('0.0.0')
            self.assertIn('feature', changelog)
            self.assertIn('fix', changelog)
            self.assertIn('documentation', changelog)
            self.assertIn('breaking', changelog)
            self.assertGreater(len(changelog['feature']), 0)
            self.assertGreater(len(changelog['fix']), 0)
            self.assertGreater(len(changelog['breaking']), 0)

    def test_should_include_hash_in_section_contents(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **k: ALL_KINDS_OF_COMMIT_MESSAGES):
            changelog = generate_changelog('0.0.0')
            self.assertEqual(changelog['breaking'][0][0], MAJOR[0])
            self.assertEqual(changelog['feature'][0][0], MINOR[0])
            self.assertEqual(changelog['fix'][0][0], PATCH[0])

    def test_should_only_read_until_given_version(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **k: MAJOR_LAST_RELEASE_MINOR_AFTER):
            changelog = generate_changelog('1.1.0')
            self.assertGreater(len(changelog['feature']), 0)
            self.assertEqual(len(changelog['fix']), 0)
            self.assertEqual(len(changelog['documentation']), 0)
            self.assertEqual(len(changelog['breaking']), 0)

    def test_should_skip_style_changes(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **k: PATCH_COMMIT_MESSAGES + [('21', 'style(x): change x')]):
            changelog = generate_changelog('0.0.0')
            self.assertNotIn('style', changelog)

    def test_should_skip_chore_changes(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **kw: PATCH_COMMIT_MESSAGES + [('23', 'chore(x): change x')]):
            changelog = generate_changelog('0.0.0')
            self.assertNotIn('chore', changelog)

    def test_should_get_right_breaking_description(self):
        param_list = [
            (MAJOR, 'Uses super-feature as default instead of dull-feature.'),
            (MAJOR2, 'Uses super-feature as default instead of dull-feature.'),
            (
                MAJOR_MENTIONING_1_0_0,
                'Uses super-feature as default instead of dull-feature from v1.0.0.'
            ),
            (MAJOR_EXCL_WITH_FOOTER, 'Another feature, another breaking change'),
            (MAJOR_EXCL_NOT_FOOTER, 'Fix a big bug that everyone exploited'),
        ]
        for commit, expected_description in param_list:
            with mock.patch('semantic_release.history.logs.get_commit_log',
                            lambda *a, **kw: [commit]):
                with self.subTest(hash=commit[0]):
                    changelog = generate_changelog('0.0.0')
                    self.assertEqual(changelog['breaking'][0][1], expected_description)

    def test_messages_are_capitalized(self):
        with mock.patch('semantic_release.history.logs.get_commit_log',
                        lambda *a, **k: [('23', 'fix(x): abcd')]):
            changelog = generate_changelog('0.0.0')
            self.assertEqual(changelog['fix'][0][1], 'Abcd')


def test_current_version_should_return_correct_version():
    assert get_current_version() == semantic_release.__version__


@mock.patch('semantic_release.history.get_last_version', return_value='last_version')
def test_current_version_should_return_git_version(mock_last_version):
    assert 'last_version' == get_current_version_by_tag()


@mock.patch('semantic_release.history.config.get', return_value='tag')
@mock.patch('semantic_release.history.get_last_version', return_value=None)
def test_current_version_should_return_default_version(mock_config, mock_last_version):
    assert '0.0.0' == get_current_version()


class GetPreviousVersionTests(TestCase):

    @mock.patch('semantic_release.history.get_commit_log',
                lambda: [('211', '0.10.0'), ('13', '0.9.0')])
    def test_should_return_correct_version(self):
        self.assertEqual(get_previous_version('0.10.0'), '0.9.0')

    @mock.patch('semantic_release.history.get_commit_log',
                lambda: [('211', '0.10.0'), ('13', '0.9.0')])
    def test_should_return_correct_version_with_v(self):
        self.assertEqual(get_previous_version('0.10.0'), '0.9.0')


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

    def test_none_bump(self):
        self.assertEqual(get_new_version('1.0.0', None), '1.0.0')


class MarkdownChangelogTests(TestCase):
    def test_should_output_all_sections(self):
        markdown = markdown_changelog('0', {
            'refactor': [('12', 'Refactor super-feature')],
            'breaking': [('21', 'Uses super-feature as default instead of dull-feature.')],
            'feature': [('145', 'Add non-breaking super-feature'), ('134', 'Add super-feature')],
            'fix': [('234', 'Fix bug in super-feature')],
            'documentation': [('0', 'Document super-feature')],
            'performance': [],
        })
        self.assertEqual(
            markdown,
            '\n'
            '### Feature\n'
            '* Add non-breaking super-feature (145)\n'
            '* Add super-feature (134)\n'
            '\n'
            '### Fix\n'
            '* Fix bug in super-feature (234)\n'
            '\n'
            '### Breaking\n'
            '* Uses super-feature as default instead of dull-feature. (21)\n'
            '\n'
            '### Documentation\n'
            '* Document super-feature (0)\n'
        )

    def test_should_not_include_empty_sections(self):
        self.assertEqual(
            markdown_changelog(
                '1.0.1',
                {
                    'refactor': [],
                    'breaking': [],
                    'feature': [],
                    'fix': [],
                    'documentation': [],
                    'performance': [],
                },
            ),
            ''
        )

    def test_should_output_heading(self):
        self.assertIn(
            '## v1.0.1\n',
            markdown_changelog(
                '1.0.1',
                {
                    'refactor': [],
                    'breaking': [],
                    'feature': [],
                    'fix': [],
                    'documentation': [],
                    'performance': [],
                },
                header=True
            )
        )

    def test_should_not_output_heading(self):
        self.assertNotIn(
            'v1.0.1',
            markdown_changelog(
                '1.0.1',
                {
                    'refactor': [],
                    'breaking': [],
                    'feature': [],
                    'fix': [],
                    'documentation': [],
                    'performance': [],
                },
            )
        )


@mock.patch('builtins.open', mock_version_file)
@mock.patch('semantic_release.history.config.get', return_value='my_version_path:my_version_var')
def test_set_version(mock_config):

    set_new_version('X.Y.Z')

    handle_open = mock_version_file()
    mock_version_file.assert_any_call('my_version_path', mode='w')
    mock_version_file.assert_any_call('my_version_path', mode='r')
    handle_open.read.assert_called_once_with()
    handle_open.write.assert_called_once_with('my_version_var = \'X.Y.Z\'')
    mock_version_file.reset_mock()
