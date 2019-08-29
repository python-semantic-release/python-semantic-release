import os
from unittest import TestCase

import toml

from semantic_release.errors import ImproperConfigurationError
from semantic_release.history import parser_angular
from semantic_release.settings import _config, current_commit_parser

from . import mock, reset_config

assert reset_config


class ConfigTests(TestCase):

    def test_config(self):
        config = _config()
        self.assertEqual(
            config.get('semantic_release', 'version_variable'),
            'semantic_release/__init__.py:__version__'
        )

    @mock.patch('semantic_release.settings.getcwd', return_value='/tmp/')
    def test_defaults(self, mock_getcwd):
        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get('semantic_release', 'minor_tag'), ':sparkles:')
        self.assertEqual(config.get('semantic_release', 'fix_tag'), ':nut_and_bolt:')
        self.assertFalse(config.getboolean('semantic_release', 'patch_without_tag'))
        self.assertFalse(config.getboolean('semantic_release', 'check_build_status'))
        self.assertEqual(config.get('semantic_release', 'hvcs'), 'github')
        self.assertEqual(config.getboolean('semantic_release', 'upload_to_pypi'), True)

    @mock.patch('semantic_release.settings.getcwd', return_value='/tmp/')
    def test_toml_override(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = '/tmp/pyproject.toml'
        toml_conf_content = {
            'tool': {
                'foo': {'bar': 'baz'},
                'semantic_release': {
                    'upload_to_pypi': False,
                    'version_source': 'tag',
                    'foo': 'bar',
                },
            },
        }
        with open(dummy_conf_path, 'w') as dummy_conf_file:
            toml.dump(toml_conf_content, dummy_conf_file)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get('semantic_release', 'hvcs'), 'github')
        self.assertEqual(config.getboolean('semantic_release', 'upload_to_pypi'), False)
        self.assertEqual(config.get('semantic_release', 'version_source'), 'tag')
        self.assertEqual(config.get('semantic_release', 'foo'), 'bar')

        # delete temporary toml config file
        os.remove(dummy_conf_path)

    @mock.patch('semantic_release.settings.debug')
    @mock.patch('semantic_release.settings.getcwd', return_value='/tmp/')
    def test_no_raise_toml_error(self, mock_getcwd, mock_debug):
        # create temporary toml config file
        dummy_conf_path = '/tmp/pyproject.toml'
        bad_toml_conf_content = """
        TITLE OF BAD TOML
        [section]
        key = # BAD BECAUSE NO VALUE
        """
        with open(dummy_conf_path, 'w') as dummy_conf_file:
            dummy_conf_file.write(bad_toml_conf_content)

        _ = _config()
        mock_getcwd.assert_called_once_with()
        mock_debug.assert_called_once_with('Could not decode pyproject.toml')
        # delete temporary toml config file
        os.remove(dummy_conf_path)

    @mock.patch('semantic_release.settings.config.get', lambda *x: 'nonexistent.parser')
    def test_current_commit_parser_should_raise_error_if_parser_module_do_not_exist(self):
        self.assertRaises(ImproperConfigurationError, current_commit_parser)

    @mock.patch('semantic_release.settings.config.get', lambda *x: 'semantic_release.not_a_parser')
    def test_current_commit_parser_should_raise_error_if_parser_do_not_exist(self):
        self.assertRaises(ImproperConfigurationError, current_commit_parser)

    def test_current_commit_parser_should_return_correct_parser(self):
        self.assertEqual(current_commit_parser(), parser_angular.parse_commit_message)
