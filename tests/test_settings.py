from unittest import TestCase, mock

from semantic_release.settings import config


class ConfigTests(TestCase):
    def test_config(self):
        self.assertEqual(
            config.get('semantic_release', 'version_variable'),
            'semantic_release/__init__.py:__version__'
        )

    @mock.patch('os.getcwd', '/tmp/')
    def test_defaults(self):
        self.assertEqual(config.get('semantic_release', 'major_tag'), ':boom:')
        self.assertEqual(config.get('semantic_release', 'minor_tag'), ':sparkles:')
        self.assertEqual(config.get('semantic_release', 'patch_tag'), ':bug:')
        self.assertFalse(config.getboolean('semantic_release', 'patch_without_tag'))
