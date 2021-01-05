from textwrap import dedent

import mock
import pytest

import semantic_release
from semantic_release.history import (
    ImproperConfigurationError,
    VersionPattern,
    get_current_version,
    get_current_version_by_tag,
    get_new_version,
    get_previous_version,
    load_version_patterns,
    set_new_version,
)

from .. import wrapped_config_get
from ..mocks import mock_version_file


@pytest.fixture
def tmp_cwd(tmp_path):
    import os

    try:
        orig_path = os.getcwd()
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(orig_path)


def test_current_version_should_return_correct_version():
    assert get_current_version() == semantic_release.__version__


@mock.patch("semantic_release.history.get_last_version", return_value="last_version")
def test_current_version_should_return_git_version(mock_last_version):
    assert "last_version" == get_current_version_by_tag()


@mock.patch(
    "semantic_release.history.config.get", wrapped_config_get(version_source="tag")
)
@mock.patch("semantic_release.history.get_last_version", return_value=None)
def test_current_version_should_return_default_version(mock_last_version):
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
        assert type(get_new_version("0.0.0", "minor")) is str
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


@mock.patch(
    "semantic_release.history.config.get",
    wrapped_config_get(version_variable="my_version_path:my_version_var"),
)
def test_set_version(tmp_cwd):
    path = tmp_cwd / "my_version_path"
    path.write_text("my_version_var = '1.2.3'")

    set_new_version("X.Y.Z")

    assert path.read_text() == "my_version_var = 'X.Y.Z'"


class TestVersionPattern:
    @pytest.mark.parametrize(
        "str, path, pattern",
        [
            (
                "path:__version__",
                "path",
                r'__version__ *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']',
            ),
        ],
    )
    def test_from_variable(self, str, path, pattern):
        p = VersionPattern.from_variable(str)
        assert p.path == path
        assert p.pattern == pattern

    @pytest.mark.parametrize(
        "str, path, pattern",
        [
            ("path:pattern", "path", r"pattern"),
            ("path:Version: {version}", "path", r"Version: (\d+\.\d+(?:\.\d+)?)"),
        ],
    )
    def test_from_pattern(self, str, path, pattern):
        p = VersionPattern.from_pattern(str)
        assert p.path == path
        assert p.pattern == pattern

    @pytest.mark.parametrize(
        "pattern, content, hits",
        [
            (r"(\d+)", "", set()),
            (r"(\d+)", "ab12", {"12"}),
            (r"(\d+)", "ab12 cd34", {"12", "34"}),
            (
                r"version = (\d+)",
                "version = 12\nnotversion = 34\nversion = 56not",
                {"12", "34", "56"},
            ),
            (
                r"^version = (\d+)$",
                "version = 12\nnotversion = 34\nversion = 56not",
                {"12"},
            ),
        ],
    )
    def test_parse(self, tmp_path, pattern, content, hits):
        path = tmp_path / "pyproject.toml"
        path.write_text(content)

        pattern = VersionPattern(str(path), pattern)
        assert pattern.parse() == hits

    @pytest.mark.parametrize(
        "pattern, old_content, new_content",
        [
            (r"(\d+)", "", ""),
            (r"(\d+)", "1", "-"),
            (r"(\d+)", "1b", "-b"),
            (r"(\d+)", "12", "-"),
            (r"(\d+)", "12b", "-b"),
            (r"(\d+)", "a", "a"),
            (r"(\d+)", "a1", "a-"),
            (r"(\d+)", "a1b", "a-b"),
            (r"(\d+)", "a12", "a-"),
            (r"(\d+)", "a12b", "a-b"),
            (r"(\d+)", "a12b3", "a-b-"),
            (r"(\d+)", "a12b3c", "a-b-c"),
            (r"(\d+)", "a12b34", "a-b-"),
            (r"(\d+)", "a12b34c", "a-b-c"),
            (r"a(\d+)", "a", "a"),
            (r"a(\d+)", "a1", "a-"),
            (r"a(\d+)", "a1b", "a-b"),
            (r"a(\d+)", "a12", "a-"),
            (r"a(\d+)", "a12b", "a-b"),
            (r"(\d+)b", "a", "a"),
            (r"(\d+)b", "a1", "a1"),
            (r"(\d+)b", "a1b", "a-b"),
            (r"(\d+)b", "a12", "a12"),
            (r"(\d+)b", "a12b", "a-b"),
        ],
    )
    def test_replace(self, tmp_path, pattern, old_content, new_content):
        path = tmp_path / "pyproject.toml"
        path.write_text(old_content)

        pattern = VersionPattern(str(path), pattern)
        pattern.replace("-")

        assert path.read_text() == new_content


@pytest.mark.parametrize(
    "params",
    [
        dict(
            pyproject="",
            error=True,
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        """,
            error=True,
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_variable = "path:__version__"
                        """,
            patterns=[
                ("path", r'__version__ *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']'),
            ],
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_variable = "path1:var1,path2:var2"
                        """,
            patterns=[
                ("path1", r'var1 *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']'),
                ("path2", r'var2 *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']'),
            ],
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_variable = [
                            "path1:var1",
                            "path2:var2"
                        ]
                        """,
            patterns=[
                ("path1", r'var1 *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']'),
                ("path2", r'var2 *[:=] *["\'](\d+\.\d+(?:\.\d+)?)["\']'),
            ],
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_pattern = "path:pattern"
                        """,
            patterns=[
                ("path", "pattern"),
            ],
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_pattern = "path1:pattern1,path2:pattern2"
                        """,
            patterns=[
                ("path1", "pattern1"),
                ("path2", "pattern2"),
            ],
        ),
        dict(
            pyproject="""\
                        [tool.semantic_release]
                        version_pattern = [
                            "path1:pattern1",
                            "path2:pattern2"
                        ]
                        """,
            patterns=[
                ("path1", "pattern1"),
                ("path2", "pattern2"),
            ],
        ),
    ],
)
def test_load_version_patterns(tmp_cwd, monkeypatch, params):
    import semantic_release.history
    import semantic_release.settings

    config = tmp_cwd / "pyproject.toml"
    config.write_text(dedent(params["pyproject"]))
    print(config.read_text())

    monkeypatch.setattr(
        semantic_release.history,
        "config",
        semantic_release.settings._config(),
    )

    if "error" in params:
        with pytest.raises(ImproperConfigurationError):
            load_version_patterns()

    else:
        patterns = load_version_patterns()
        pattern_tuples = [(x.path, x.pattern) for x in patterns]
        assert pattern_tuples == params["patterns"]
