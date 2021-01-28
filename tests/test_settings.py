import os
import platform
from textwrap import dedent
from unittest import TestCase

from semantic_release.errors import ImproperConfigurationError
from semantic_release.history import parser_angular
from semantic_release.settings import _config, current_commit_parser

from . import mock, reset_config

assert reset_config


# Set path to this directory
temp_dir = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")
    if platform.system() == "Windows"
    else "/tmp/"
)


class ConfigTests(TestCase):
    def test_config(self):
        config = _config()
        self.assertEqual(
            config.get("version_variable"),
            "semantic_release/__init__.py:__version__",
        )

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_defaults(self, mock_getcwd):
        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("minor_tag"), ":sparkles:")
        self.assertEqual(config.get("fix_tag"), ":nut_and_bolt:")
        self.assertFalse(config.get("patch_without_tag"))
        self.assertTrue(config.get("major_on_zero"))
        self.assertFalse(config.get("check_build_status"))
        self.assertEqual(config.get("hvcs"), "github")
        self.assertEqual(config.get("upload_to_pypi"), True)

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_override(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
        toml_conf_content = """
[tool.foo]
bar = "baz"
[tool.semantic_release]
upload_to_pypi = false
version_source = "tag"
foo = "bar"
"""
        with open(dummy_conf_path, "w") as dummy_conf_file:
            dummy_conf_file.write(toml_conf_content)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("hvcs"), "github")
        self.assertEqual(config.get("upload_to_pypi"), False)
        self.assertEqual(config.get("version_source"), "tag")
        self.assertEqual(config.get("foo"), "bar")

        # delete temporary toml config file
        os.remove(dummy_conf_path)

    @mock.patch("semantic_release.settings.logger.debug")
    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_no_raise_toml_error(self, mock_getcwd, mock_debug):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        bad_toml_conf_content = """\
        TITLE OF BAD TOML
        [section]
        key = # BAD BECAUSE NO VALUE
        """
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)

        with open(dummy_conf_path, "w") as dummy_conf_file:
            dummy_conf_file.write(bad_toml_conf_content)

        _ = _config()
        mock_getcwd.assert_called_once_with()
        mock_debug.assert_called_once_with(
            'Could not decode pyproject.toml: Invalid key "TITLE OF BAD TOML" at line 1 col 25'
        )
        # delete temporary toml config file
        os.remove(dummy_conf_path)

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_no_psr_section(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        toml_conf_content = dedent(
            """
            [tool.foo]
            bar = "baz"
            """
        )
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)

        with open(dummy_conf_path, "w") as dummy_conf_file:
            dummy_conf_file.write(toml_conf_content)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("hvcs"), "github")
        # delete temporary toml config file
        os.remove(dummy_conf_path)

    @mock.patch("semantic_release.settings.config.get", lambda *x: "nonexistent.parser")
    def test_current_commit_parser_should_raise_error_if_parser_module_do_not_exist(
        self,
    ):
        self.assertRaises(ImproperConfigurationError, current_commit_parser)

    @mock.patch(
        "semantic_release.settings.config.get",
        lambda *x: "semantic_release.not_a_parser",
    )
    def test_current_commit_parser_should_raise_error_if_parser_do_not_exist(self):
        self.assertRaises(ImproperConfigurationError, current_commit_parser)

    def test_current_commit_parser_should_return_correct_parser(self):
        self.assertEqual(current_commit_parser(), parser_angular.parse_commit_message)
