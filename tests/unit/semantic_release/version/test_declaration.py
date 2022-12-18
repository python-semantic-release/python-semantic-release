import difflib
from pathlib import Path
from textwrap import dedent
from unittest import mock

import pytest
from pytest_lazyfixture import lazy_fixture

from semantic_release.version.declaration import (
    PatternVersionDeclaration,
    TomlVersionDeclaration,
)
from semantic_release.version.version import Version

from tests.const import EXAMPLE_PROJECT_VERSION


def test_pyproject_toml_version_found(example_pyproject_toml):
    decl = TomlVersionDeclaration(
        example_pyproject_toml.resolve(), "tool.poetry.version"
    )
    versions = decl.parse()
    assert len(versions) == 1
    assert versions.pop() == Version.parse(EXAMPLE_PROJECT_VERSION)


def test_setup_cfg_version_found(example_setup_cfg):
    decl = PatternVersionDeclaration(
        example_setup_cfg.resolve(), r"^version *= *(?P<version>.*)$"
    )
    versions = decl.parse()
    assert len(versions) == 1
    assert versions.pop() == Version.parse(EXAMPLE_PROJECT_VERSION)


@pytest.mark.parametrize(
    "decl_cls, config_file, search_text",
    [
        (
            TomlVersionDeclaration,
            lazy_fixture("example_pyproject_toml"),
            "tool.poetry.version",
        ),
        (
            PatternVersionDeclaration,
            lazy_fixture("example_setup_cfg"),
            r"^version = (?P<version>.*)$",
        ),
    ],
)
def test_version_replace(decl_cls, config_file, search_text):
    new_version = Version(1, 0, 0)
    decl = decl_cls(config_file.resolve(), search_text)
    orig_content = decl.content
    new_content = decl.replace(new_version=new_version)
    decl.write(new_content)

    new_decl = decl_cls(config_file.resolve(), search_text)
    assert new_decl.parse() == {new_version}

    d = difflib.Differ()
    diff = list(
        d.compare(
            orig_content.splitlines(keepends=True),
            new_decl.content.splitlines(keepends=True),
        )
    )
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    assert len(removed) == 1
    assert len(added) == 1

    (removed_line,) = removed
    (added_line,) = added

    # Line is unchanged apart from new version added
    assert removed_line.replace(EXAMPLE_PROJECT_VERSION, str(new_version)) == added_line


@pytest.mark.parametrize(
    "search_text",
    [r"^version = (.*)$", r"^version = (?P<Version>.*)", r"(?P<vrsion>.*)"],
)
def test_bad_version_regex_fails(search_text):
    with mock.patch.object(Path, "exists") as mock_path_exists, pytest.raises(
        ValueError, match="must use 'version'"
    ):
        mock_path_exists.return_value = True
        PatternVersionDeclaration("doesn't matter", search_text)


def test_pyproject_toml_no_version(tmp_path):
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(
        dedent(
            """
            [tool.isort]
            profile = "black"
            """
        )
    )

    decl = TomlVersionDeclaration(pyproject_toml.resolve(), "tool.poetry.version")
    assert decl.parse() == set()


def test_setup_cfg_no_version(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        dedent(
            """
            [tool:isort]
            profile = black
            """
        )
    )

    decl = PatternVersionDeclaration(
        setup_cfg.resolve(), r"^version = (?P<version>.*)$"
    )
    assert decl.parse() == set()


@pytest.mark.parametrize(
    "decl_cls", (TomlVersionDeclaration, PatternVersionDeclaration)
)
def test_version_decl_error_on_missing_file(decl_cls):
    with pytest.raises(FileNotFoundError):
        decl_cls("/this/is/definitely/a/missing/path/asdfghjkl", "random search text")
