from __future__ import annotations

from pathlib import Path
from re import compile as regexp
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.declarations.toml import TomlVersionDeclaration
from semantic_release.version.version import Version

from tests.fixtures.git_repo import default_tag_format_str

if TYPE_CHECKING:
    from re import Pattern


def test_toml_declaration_is_version_replacer():
    """
    Given the class TomlVersionDeclaration or an instance of it,
    When the class is evaluated as a subclass or an instance of,
    Then the evaluation is true
    """
    assert issubclass(TomlVersionDeclaration, IVersionReplacer)

    toml_instance = TomlVersionDeclaration(
        "file", "project.version", VersionStampType.NUMBER_FORMAT
    )
    assert isinstance(toml_instance, IVersionReplacer)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "replacement_def",
            "tag_format",
            "starting_contents",
            "resulting_contents",
            "next_version",
            "test_file",
        ],
    ),
    [
        pytest.param(
            replacement_def,
            tag_format,
            starting_contents,
            resulting_contents,
            next_version,
            test_file,
            id=test_id,
        )
        for test_file in ["test_file.toml"]
        for next_version in ["1.2.3"]
        for test_id, replacement_def, tag_format, starting_contents, resulting_contents in [
            (
                "Default number format for project.version",
                f"{test_file}:project.version",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with single quotes
                dedent(
                    """\
                    [project]
                    version = '1.0.0'
                    """
                ),
                dedent(
                    f"""\
                    [project]
                    version = "{next_version}"
                    """
                ),
            ),
            (
                "Explicit number format for project.version",
                f"{test_file}:project.version:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with double quotes
                dedent(
                    """\
                    [project]
                    version = "1.0.0"
                    """
                ),
                dedent(
                    f"""\
                    [project]
                    version = "{next_version}"
                    """
                ),
            ),
            (
                "Using default tag format for toml string variable",
                f"{test_file}:version:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with single quotes
                '''version = "v1.0.0"''',
                f'''version = "v{next_version}"''',
            ),
            (
                "Using custom tag format for toml string variable",
                f"{test_file}:version:{VersionStampType.TAG_FORMAT.value}",
                "module-v{version}",
                # Uses equals separator with double quotes
                '''version = "module-v1.0.0"''',
                f'''version = "module-v{next_version}"''',
            ),
        ]
    ],
)
def test_toml_declaration_from_definition(
    replacement_def: str,
    tag_format: str,
    starting_contents: str,
    resulting_contents: str,
    next_version: str,
    test_file: str,
    change_to_ex_proj_dir: None,
):
    """
    Given a file with a formatted version string,
    When update_file_w_version() is called with a new version,
    Then the file is updated with the new version string in the specified tag or number format

    Version variables can be separated by either "=", ":", "@", or ':=' with optional whitespace
    between operator and variable name. The variable name or values can also be wrapped in either
    single or double quotes.
    """
    # Setup: create file with initial contents
    expected_filepath = Path(test_file).resolve()
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = TomlVersionDeclaration.from_string_definition(replacement_def)

    # Act: apply version change
    actual_file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse(next_version, tag_format=tag_format),
        noop=False,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert resulting_contents == actual_contents
    assert expected_filepath == actual_file_modified


def test_toml_declaration_no_file_change(
    change_to_ex_proj_dir: None,
):
    """
    Given a configured stamp file is already up-to-date,
    When update_file_w_version() is called with the same version,
    Then the file is not modified and no path is returned
    """
    test_file = "test_file"
    next_version = Version.parse("1.2.3")
    starting_contents = dedent(
        f"""\
        [project]
        version = "{next_version}"
        """
    )

    # Setup: create file with initial contents
    Path(test_file).write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = TomlVersionDeclaration.from_string_definition(
        f"{test_file}:project.version:{VersionStampType.NUMBER_FORMAT.value}",
    )

    # Act: apply version change
    file_modified = version_replacer.update_file_w_version(
        new_version=next_version,
        noop=False,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert starting_contents == actual_contents
    assert file_modified is None


def test_toml_declaration_error_on_missing_file():
    # Initialization should not fail or do anything intensive
    version_replacer = TomlVersionDeclaration.from_string_definition(
        "nonexistent_file:version",
    )

    with pytest.raises(FileNotFoundError):
        version_replacer.update_file_w_version(
            new_version=Version.parse("1.2.3"),
            noop=False,
        )


def test_toml_declaration_no_version_in_file(
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    expected_filepath = Path(test_file).resolve()
    starting_contents = dedent(
        """\
        [project]
        name = "example"
        """
    )

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = TomlVersionDeclaration.from_string_definition(
        f"{test_file}:project.version:{VersionStampType.NUMBER_FORMAT.value}",
    )

    file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3"),
        noop=False,
    )

    # Evaluate
    actual_contents = expected_filepath.read_text()
    assert file_modified is None
    assert starting_contents == actual_contents


def test_toml_declaration_noop_is_noop(
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    expected_filepath = Path(test_file).resolve()
    starting_contents = dedent(
        """\
        [project]
        version = '1.0.0'
        """
    )

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = TomlVersionDeclaration.from_string_definition(
        f"{test_file}:project.version:{VersionStampType.NUMBER_FORMAT.value}",
    )

    # Act: apply version change
    file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3"),
        noop=True,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert starting_contents == actual_contents
    assert expected_filepath == file_modified


def test_toml_declaration_noop_warning_on_missing_file(
    capsys: pytest.CaptureFixture[str],
):
    version_replacer = TomlVersionDeclaration.from_string_definition(
        "nonexistent_file:version",
    )

    file_to_modify = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3"),
        noop=True,
    )

    # Evaluate
    assert file_to_modify is None
    assert (
        "FILE NOT FOUND: cannot stamp version in non-existent file"
        in capsys.readouterr().err
    )


def test_toml_declaration_noop_warning_on_no_version_in_file(
    capsys: pytest.CaptureFixture[str],
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    starting_contents = dedent(
        """\
        [project]
        name = "example"
        """
    )

    # Setup: create file with initial contents
    Path(test_file).write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = TomlVersionDeclaration.from_string_definition(
        f"{test_file}:project.version:{VersionStampType.NUMBER_FORMAT.value}",
    )

    file_to_modify = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3"),
        noop=True,
    )

    # Evaluate
    assert file_to_modify is None
    assert (
        "VERSION PATTERN NOT FOUND: no version to stamp in file"
        in capsys.readouterr().err
    )


@pytest.mark.parametrize(
    "replacement_def, error_msg",
    [
        pytest.param(
            replacement_def,
            error_msg,
            id=str(error_msg),
        )
        for replacement_def, error_msg in [
            (
                f"{Path(__file__)!s}",
                regexp(r"Invalid TOML replacement definition .*, missing ':'"),
            ),
            (
                f"{Path(__file__)!s}:tool.poetry.version:not_a_valid_version_type",
                "Invalid stamp type, must be one of:",
            ),
        ]
    ],
)
def test_toml_declaration_w_invalid_definition(
    replacement_def: str,
    error_msg: Pattern[str] | str,
):
    """
    check if TomlVersionDeclaration raises ValueError when loaded
    from invalid strings given in the config file
    """
    with pytest.raises(ValueError, match=error_msg):
        TomlVersionDeclaration.from_string_definition(replacement_def)
