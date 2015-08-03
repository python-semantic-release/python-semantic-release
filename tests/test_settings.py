from unittest import TestCase, mock

from semantic_release.settings import _config


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
        mock_getcwd.assert_called_once()
        self.assertEqual(config.get('semantic_release', 'major_tag'), ':boom:')
        self.assertEqual(config.get('semantic_release', 'minor_tag'), ':sparkles:')
        self.assertEqual(config.get('semantic_release', 'patch_tag'), ':bug:')
        self.assertFalse(config.getboolean('semantic_release', 'patch_without_tag'))
        self.assertFalse(config.getboolean('semantic_release', 'check_build_status'))
        self.assertEqual(config.get('semantic_release', 'hvcs'), 'github')
