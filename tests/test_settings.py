from unittest import TestCase

from semantic_release.settings import load_config


class ConfigTests(TestCase):

    def test_load_config(self):
        config = load_config()
        self.assertIn('version_variable', config)
        self.assertIn('major_tag', config)
        self.assertIn('minor_tag', config)
        self.assertIn('patch_tag', config)
