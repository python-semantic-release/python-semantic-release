import os
import platform
from unittest import TestCase

import toml
import jmespath
import tomlkit

from semantic_release.errors import ImproperConfigurationError
from semantic_release.history import parser_angular, get_current_version, set_new_version
from semantic_release.settings import _config, current_commit_parser

from . import mock, reset_config, wrapped_config_get
from .history.test_version import tmp_cwd

assert reset_config

# Set path to this directory
temp_dir = (
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")
    if platform.system() == "Windows"
    else "/tmp/"
)


@mock.patch("semantic_release.history.config.get",
            wrapped_config_get(version_variable="my_version_path/__init.py:__version__"), )
def test_toml_config_version_from_py_file_is_correct(tmp_cwd):
    os.makedirs(os.path.join(tmp_cwd, 'my_version_path'), exist_ok=True)
    dummy_py_file_with_version = os.path.join(tmp_cwd, 'my_version_path', "__init.py")
    py_file_with_version_content = """
    __version__ = "1.4.2"

    from .errors import UnknownCommitMessageStyleError  # noqa; noqa
    from .errors import ImproperConfigurationError, SemanticReleaseBaseError
    """
    with open(dummy_py_file_with_version, "w") as dummy_py_file:
        dummy_py_file.write(py_file_with_version_content)

    current_version1 = get_current_version()
    assert '1.4.2' == get_current_version()


class ConfigTests(TestCase):

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_config_version_from_toml_file_is_correct(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
        toml_conf_content = {
            "tool": {
                "poetry": {
                    "version": "0.1.2"
                },
                "semantic_release": {
                    "version_variable": 'pyproject.toml:tool.poetry.version',
                },
            },
        }
        with open(dummy_conf_path, "w") as dummy_conf_file:
            toml.dump(toml_conf_content, dummy_conf_file)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("version_variable"), "pyproject.toml:tool.poetry.version", )

        with open(dummy_conf_path, "r") as f:
            content = f.read()
        expected_version = jmespath.search('tool.poetry.version', tomlkit.loads(content))
        assert '0.1.2' == expected_version

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_config_version_from_py_file(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
        toml_conf_content = {
            "tool": {
                "semantic_release": {
                    "version_variable": 'semantic_release/__init__.py:__version__',
                },
            },
        }
        with open(dummy_conf_path, "w") as dummy_conf_file:
            toml.dump(toml_conf_content, dummy_conf_file)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("version_variable"), "semantic_release/__init__.py:__version__", )

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_config_version_from_toml_file(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
        toml_conf_content = {
            "tool": {
                "semantic_release": {
                    "version_variable": 'pyproject.toml:tool.poetry.version',
                },
            },
        }
        with open(dummy_conf_path, "w") as dummy_conf_file:
            toml.dump(toml_conf_content, dummy_conf_file)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("version_variable"), "pyproject.toml:tool.poetry.version", )

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
        self.assertEqual(config.get("upload_to_repository"), True)

    @mock.patch("semantic_release.settings.getcwd", return_value=temp_dir)
    def test_toml_override(self, mock_getcwd):
        # create temporary toml config file
        dummy_conf_path = os.path.join(temp_dir, "pyproject.toml")
        os.makedirs(os.path.dirname(dummy_conf_path), exist_ok=True)
        toml_conf_content = {
            "tool": {
                "foo": {"bar": "baz"},
                "semantic_release": {
                    "upload_to_repository": False,
                    "version_source": "tag",
                    "foo": "bar",
                },
            },
        }
        with open(dummy_conf_path, "w") as dummy_conf_file:
            toml.dump(toml_conf_content, dummy_conf_file)

        config = _config()
        mock_getcwd.assert_called_once_with()
        self.assertEqual(config.get("hvcs"), "github")
        self.assertEqual(config.get("upload_to_repository"), False)
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
        mock_debug.assert_called_once_with("Could not decode pyproject.toml")
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
