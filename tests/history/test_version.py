import mock

import semantic_release
from semantic_release.history import (
    get_current_version,
    get_current_version_by_tag,
    get_new_version,
    get_previous_version,
    set_new_version,
)

from ..mocks import mock_version_file


def test_current_version_should_return_correct_version():
    assert get_current_version() == semantic_release.__version__


@mock.patch("semantic_release.history.get_last_version", return_value="last_version")
def test_current_version_should_return_git_version(mock_last_version):
    assert "last_version" == get_current_version_by_tag()


@mock.patch("semantic_release.history.config.get", return_value="tag")
@mock.patch("semantic_release.history.get_last_version", return_value=None)
def test_current_version_should_return_default_version(mock_config, mock_last_version):
    assert "0.0.0" == get_current_version()


class TestGetPreviousVersion:
    @mock.patch(
        "semantic_release.history.get_commit_log",
        lambda: [("211", "0.10.0"), ("13", "0.9.0")],
    )
    def test_should_return_correct_version(self):
        assert get_previous_version("0.10.0") == "0.9.0"

    @mock.patch(
        "semantic_release.history.get_commit_log",
        lambda: [("211", "0.10.0"), ("13", "0.9.0")],
    )
    def test_should_return_correct_version_with_v(self):
        assert get_previous_version("0.10.0") == "0.9.0"


class TestGetNewVersion:
    def test_major_bump(self):
        assert get_new_version("0.0.0", "major") == "1.0.0"
        assert get_new_version("0.1.0", "major") == "1.0.0"
        assert get_new_version("0.1.9", "major") == "1.0.0"
        assert get_new_version("10.1.0", "major") == "11.0.0"

    def test_minor_bump(self):
        assert get_new_version("0.0.0", "minor") == "0.1.0"
        assert get_new_version("1.2.0", "minor") == "1.3.0"
        assert get_new_version("1.2.1", "minor") == "1.3.0"
        assert get_new_version("10.1.0", "minor") == "10.2.0"

    def test_patch_bump(self):
        assert get_new_version("0.0.0", "patch") == "0.0.1"
        assert get_new_version("0.1.0", "patch") == "0.1.1"
        assert get_new_version("10.0.9", "patch") == "10.0.10"

    def test_none_bump(self):
        assert get_new_version("1.0.0", None) == "1.0.0"


@mock.patch("builtins.open", mock_version_file)
@mock.patch(
    "semantic_release.history.config.get", return_value="my_version_path:my_version_var"
)
def test_set_version(mock_config):
    set_new_version("X.Y.Z")

    handle_open = mock_version_file()
    mock_version_file.assert_any_call("my_version_path", mode="w")
    mock_version_file.assert_any_call("my_version_path", mode="r")
    handle_open.read.assert_called_once_with()
    handle_open.write.assert_called_once_with("my_version_var = 'X.Y.Z'")
    mock_version_file.reset_mock()
