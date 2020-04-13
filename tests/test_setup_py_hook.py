from unittest import TestCase

from semantic_release import setup_hook

from . import mock


class SetupPyHookTests(TestCase):
    @mock.patch("semantic_release.cli.main")
    def test_setup_hook_should_not_call_main_if_to_few_args(self, mock_main):
        setup_hook(["setup.py"])
        self.assertFalse(mock_main.called)

    @mock.patch("semantic_release.cli.main")
    def test_setup_hook_should_call_main(self, mock_main):
        setup_hook(["setup.py", "publish"])
        self.assertTrue(mock_main.called)
