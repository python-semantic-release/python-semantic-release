from __future__ import annotations

from os import linesep
from pathlib import Path

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.file import FileVersionDeclaration
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.version import Version

from tests.fixtures.example_project import change_to_ex_proj_dir
from tests.fixtures.git_repo import default_tag_format_str


def test_file_declaration_is_version_replacer():
    """
    Given the class FileVersionDeclaration or an instance of it,
    When the class is evaluated as a subclass or an instance of,
    Then the evaluation is true
    """
    assert issubclass(FileVersionDeclaration, IVersionReplacer)

    file_instance = FileVersionDeclaration("file", VersionStampType.NUMBER_FORMAT)
    assert isinstance(file_instance, IVersionReplacer)


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
        for test_file in ["VERSION"]
        for next_version in ["1.2.3"]
        for test_id, replacement_def, tag_format, starting_contents, resulting_contents in [
            (
                "Default number format for file replacement",
                f"{test_file}:*",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # File contains only version
                "1.0.0",
                f"{next_version}{linesep}",
            ),
            (
                "Explicit number format for file replacement",
                f"{test_file}:*:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # File contains only version
                "1.0.0",
                f"{next_version}{linesep}",
            ),
            (
                "Using default tag format for file replacement",
                f"{test_file}:*:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # File contains version with v-prefix
                "v1.0.0",
                f"v{next_version}{linesep}",
            ),
            (
                "Using custom tag format for file replacement",
                f"{test_file}:*:{VersionStampType.TAG_FORMAT.value}",
                "module-v{version}",
                # File contains version with custom prefix
                "module-v1.0.0",
                f"module-v{next_version}{linesep}",
            ),
            (
                "File with trailing newline",
                f"{test_file}:*",
                lazy_fixture(default_tag_format_str.__name__),
                # File contains version with newline
                "1.0.0\n",
                f"{next_version}{linesep}",
            ),
            (
                "File with whitespace",
                f"{test_file}:*",
                lazy_fixture(default_tag_format_str.__name__),
                # File contains version with whitespace
                "  1.0.0  \n",
                f"{next_version}{linesep}",
            ),
        ]
    ],
)
@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_file_declaration_from_definition(
    replacement_def: str,
    tag_format: str,
    starting_contents: str,
    resulting_contents: str,
    next_version: str,
    test_file: str,
):
    """
    Given a file with a version string as its content,
    When update_file_w_version() is called with a new version,
    Then the entire file is replaced with the new version string in the specified tag or number format
    """
    # Setup: create file with initial contents
    expected_filepath = Path(test_file).resolve()
    expected_filepath.write_text(starting_contents)

    # Create File Replacer
    version_replacer = FileVersionDeclaration.from_string_definition(replacement_def)

    # Act: apply version change
    actual_file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse(next_version, tag_format=tag_format),
        noop=False,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert resulting_contents == actual_contents
    assert expected_filepath == actual_file_modified


@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_file_declaration_no_file_change():
    """
    Given a configured stamp file is already up-to-date,
    When update_file_w_version() is called with the same version,
    Then the file is not modified and no path is returned
    """
    test_file = "VERSION"
    expected_filepath = Path(test_file).resolve()
    next_version = Version.parse("1.2.3")
    starting_contents = f"{next_version}{linesep}"

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create File Replacer
    version_replacer = FileVersionDeclaration.from_string_definition(
        f"{test_file}:*:{VersionStampType.NUMBER_FORMAT.value}",
    )

    # Act: apply version change
    file_modified = version_replacer.update_file_w_version(
        new_version=next_version,
        noop=False,
    )

    # Evaluate
    actual_contents = expected_filepath.read_text()
    assert starting_contents == actual_contents
    assert file_modified is None


@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_file_declaration_creates_when_missing_file():
    new_version = Version.parse("1.2.3")
    expected_contents = f"{new_version}{linesep}"
    missing_file_path = Path("nonexistent_file")

    # Ensure missing file does not exist before test
    if missing_file_path.exists():
        missing_file_path.unlink()

    # Create File Replacer
    version_replacer = FileVersionDeclaration.from_string_definition(
        f"{missing_file_path}:*",
    )

    # Act: apply version change
    version_replacer.update_file_w_version(
        new_version=new_version,
        noop=False,
    )

    # Evaluate
    assert missing_file_path.exists()
    actual_contents = missing_file_path.read_text()
    assert expected_contents == actual_contents


@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_file_declaration_noop_is_noop():
    test_file = "VERSION"
    expected_filepath = Path(test_file).resolve()
    starting_contents = "1.0.0"

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create File Replacer
    version_replacer = FileVersionDeclaration.from_string_definition(
        f"{test_file}:*:{VersionStampType.NUMBER_FORMAT.value}",
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


@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_file_declaration_noop_warning_on_missing_file(
    caplog: pytest.LogCaptureFixture,
):
    missing_file_name = Path("nonexistent_file")
    expected_warning = f"FILE NOT FOUND: file '{missing_file_name.resolve()}' does not exist but it will be created"
    version_replacer = FileVersionDeclaration.from_string_definition(
        f"{missing_file_name}:*",
    )

    file_to_modify = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3"),
        noop=True,
    )

    # Evaluate
    assert missing_file_name.resolve() == file_to_modify
    assert expected_warning in caplog.text


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
                "test_file",
                "Invalid replacement definition",
            ),
            (
                "test_file:*:not_a_valid_version_type",
                "Invalid stamp type, must be one of:",
            ),
            (
                "test_file:not_asterisk:nf",
                "Invalid pattern 'not_asterisk' for FileVersionDeclaration, expected '*'",
            ),
        ]
    ],
)
def test_file_declaration_w_invalid_definition(
    replacement_def: str,
    error_msg: str,
):
    """
    Check if FileVersionDeclaration raises ValueError when loaded
    from invalid strings given in the config file
    """
    with pytest.raises(ValueError, match=error_msg):
        FileVersionDeclaration.from_string_definition(replacement_def)
