from __future__ import annotations

from pathlib import Path
from re import compile as regexp
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.declarations.pattern import PatternVersionDeclaration
from semantic_release.version.version import Version

from tests.fixtures.git_repo import default_tag_format_str

if TYPE_CHECKING:
    from re import Pattern


def test_pattern_declaration_is_version_replacer():
    """
    Given the class PatternVersionDeclaration or an instance of it,
    When the class is evaluated as a subclass or an instance of,
    Then the evaluation is true
    """
    assert issubclass(PatternVersionDeclaration, IVersionReplacer)

    pattern_instance = PatternVersionDeclaration(
        "file", r"^version = (?P<version>.*)", VersionStampType.NUMBER_FORMAT
    )
    assert isinstance(pattern_instance, IVersionReplacer)


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
        for test_file in ["test_file"]
        for next_version in ["1.2.3"]
        for test_id, replacement_def, tag_format, starting_contents, resulting_contents in [
            (
                "Default number format for python string variable",
                f"{test_file}:__version__",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with single quotes
                """__version__ = '1.0.0'""",
                f"""__version__ = '{next_version}'""",
            ),
            (
                "Explicit number format for python string variable",
                f"{test_file}:__version__:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with single quotes
                """__version__ = '1.0.0'""",
                f"""__version__ = '{next_version}'""",
            ),
            (
                "Using default tag format for python string variable",
                f"{test_file}:__version__:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses equals separator with single quotes
                """__version__ = 'v1.0.0'""",
                f"""__version__ = 'v{next_version}'""",
            ),
            (
                "Using custom tag format for python string variable",
                f"{test_file}:__version__:{VersionStampType.TAG_FORMAT.value}",
                "module-v{version}",
                # Uses equals separator with double quotes
                '''__version__ = "module-v1.0.0"''',
                f'''__version__ = "module-v{next_version}"''',
            ),
            (
                # Based on https://github.com/python-semantic-release/python-semantic-release/issues/1156
                "Using default tag format for github actions uses-directive",
                f"{test_file}:repo/action-name:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses @ symbol separator without quotes or spaces
                """  uses: repo/action-name@v1.0.0""",
                f"""  uses: repo/action-name@v{next_version}""",
            ),
            (
                # Based on https://github.com/python-semantic-release/python-semantic-release/issues/1156
                "Using custom tag format for github actions uses-directive",
                f"{test_file}:repo/action-name:{VersionStampType.TAG_FORMAT.value}",
                "module-v{version}",
                # Uses @ symbol separator without quotes or spaces
                """  uses: repo/action-name@module-v1.0.0""",
                f"""  uses: repo/action-name@module-v{next_version}""",
            ),
            (
                # Based on https://github.com/python-semantic-release/python-semantic-release/issues/846
                "Using default tag format for multi-line yaml",
                f"{test_file}:newTag:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses colon separator without quotes
                dedent(
                    """\
                    # kustomization.yaml
                    images:
                      - name: repo/image
                        newTag: v1.0.0
                    """
                ),
                dedent(
                    f"""\
                    # kustomization.yaml
                    images:
                      - name: repo/image
                        newTag: v{next_version}
                    """
                ),
            ),
            (
                # Based on https://github.com/python-semantic-release/python-semantic-release/issues/846
                "Using custom tag format for multi-line yaml",
                f"{test_file}:newTag:{VersionStampType.TAG_FORMAT.value}",
                "module-v{version}",
                # Uses colon separator without quotes
                dedent(
                    """\
                    # kustomization.yaml
                    images:
                      - name: repo/image
                        newTag: module-v1.0.0
                    """
                ),
                dedent(
                    f"""\
                    # kustomization.yaml
                    images:
                      - name: repo/image
                        newTag: module-v{next_version}
                    """
                ),
            ),
            (
                "Explicit number format for python walrus string variable",
                f"{test_file}:version:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses walrus separator with single quotes
                """if version := '1.0.0': """,
                f"""if version := '{next_version}': """,
            ),
            (
                "Explicit number format for requirements.txt file with double equals",
                f"{test_file}:my-package:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses double equals separator
                """my-package == 1.0.0""",
                f"""my-package == {next_version}""",
            ),
            (
                "Using default number format for multi-line & quoted json",
                f"{test_file}:version:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses colon separator with double quotes
                dedent(
                    """\
                    {
                        "version": "1.0.0"
                    }
                    """
                ),
                dedent(
                    f"""\
                    {{
                        "version": "{next_version}"
                    }}
                    """
                ),
            ),
            (
                "Using default tag format for multi-line & quoted json",
                f"{test_file}:version:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses colon separator with double quotes
                dedent(
                    """\
                    {
                        "version": "v1.0.0"
                    }
                    """
                ),
                dedent(
                    f"""\
                    {{
                        "version": "v{next_version}"
                    }}
                    """
                ),
            ),
            (
                "Using default number format for c-macro style definition (see #1348)",
                f"{test_file}:APP_VERSION:{VersionStampType.NUMBER_FORMAT.value}",
                # irrelevant for this case
                lazy_fixture(default_tag_format_str.__name__),
                # Uses colon separator with double quotes
                dedent(
                    """\
                    #ifndef VERSION_H
                    #define VERSION_H

                    #define APP_VERSION "0.0.0"

                    #endif // VERSION_H
                    """
                ),
                dedent(
                    f"""\
                    #ifndef VERSION_H
                    #define VERSION_H

                    #define APP_VERSION "{next_version}"

                    #endif // VERSION_H
                    """
                ),
            ),
            (
                "Using default tag format for c-macro style definition (see #1348)",
                f"{test_file}:APP_VERSION:{VersionStampType.TAG_FORMAT.value}",
                lazy_fixture(default_tag_format_str.__name__),
                # Uses colon separator with double quotes
                dedent(
                    """\
                    #ifndef VERSION_H
                    #define VERSION_H

                    #define APP_VERSION "v0.0.0"

                    #endif // VERSION_H
                    """
                ),
                dedent(
                    f"""\
                    #ifndef VERSION_H
                    #define VERSION_H

                    #define APP_VERSION "v{next_version}"

                    #endif // VERSION_H
                    """
                ),
            ),
        ]
    ],
)
def test_pattern_declaration_from_definition(
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
    version_replacer = PatternVersionDeclaration.from_string_definition(
        replacement_def,
        tag_format,
    )

    # Act: apply version change
    actual_file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse(next_version, tag_format=tag_format),
        noop=False,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert resulting_contents == actual_contents
    assert expected_filepath == actual_file_modified


def test_pattern_declaration_no_file_change(
    default_tag_format_str: str,
    change_to_ex_proj_dir: None,
):
    """
    Given a configured stamp file is already up-to-date,
    When update_file_w_version() is called with the same version,
    Then the file is not modified and no path is returned
    """
    test_file = "test_file"
    expected_filepath = Path(test_file).resolve()
    next_version = Version.parse("1.2.3", tag_format=default_tag_format_str)
    starting_contents = f"""__version__ = '{next_version}'\n"""

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = PatternVersionDeclaration.from_string_definition(
        f"{test_file}:__version__:{VersionStampType.NUMBER_FORMAT.value}",
        tag_format=default_tag_format_str,
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


def test_pattern_declaration_error_on_missing_file(
    default_tag_format_str: str,
):
    # Initialization should not fail or do anything intensive
    version_replacer = PatternVersionDeclaration.from_string_definition(
        "nonexistent_file:__version__",
        tag_format=default_tag_format_str,
    )

    with pytest.raises(FileNotFoundError):
        version_replacer.update_file_w_version(
            new_version=Version.parse("1.2.3", tag_format=default_tag_format_str),
            noop=False,
        )


def test_pattern_declaration_no_version_in_file(
    default_tag_format_str: str,
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    expected_filepath = Path(test_file).resolve()
    starting_contents = """other content\n"""

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = PatternVersionDeclaration.from_string_definition(
        f"{test_file}:__version__:{VersionStampType.NUMBER_FORMAT.value}",
        tag_format=default_tag_format_str,
    )

    file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3", tag_format=default_tag_format_str),
        noop=False,
    )

    # Evaluate
    actual_contents = expected_filepath.read_text()
    assert file_modified is None
    assert starting_contents == actual_contents


def test_pattern_declaration_noop_is_noop(
    default_tag_format_str: str,
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    expected_filepath = Path(test_file).resolve()
    starting_contents = """__version__ = '1.0.0'\n"""

    # Setup: create file with initial contents
    expected_filepath.write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = PatternVersionDeclaration.from_string_definition(
        f"{test_file}:__version__:{VersionStampType.NUMBER_FORMAT.value}",
        tag_format=default_tag_format_str,
    )

    # Act: apply version change
    file_modified = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3", tag_format=default_tag_format_str),
        noop=True,
    )

    # Evaluate
    actual_contents = Path(test_file).read_text()
    assert starting_contents == actual_contents
    assert expected_filepath == file_modified


def test_pattern_declaration_noop_warning_on_missing_file(
    default_tag_format_str: str,
    capsys: pytest.CaptureFixture[str],
):
    version_replacer = PatternVersionDeclaration.from_string_definition(
        "nonexistent_file:__version__",
        tag_format=default_tag_format_str,
    )

    file_to_modify = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3", tag_format=default_tag_format_str),
        noop=True,
    )

    # Evaluate
    assert file_to_modify is None
    assert (
        "FILE NOT FOUND: cannot stamp version in non-existent file"
        in capsys.readouterr().err
    )


def test_pattern_declaration_noop_warning_on_no_version_in_file(
    default_tag_format_str: str,
    capsys: pytest.CaptureFixture[str],
    change_to_ex_proj_dir: None,
):
    test_file = "test_file"
    starting_contents = """other content\n"""

    # Setup: create file with initial contents
    Path(test_file).write_text(starting_contents)

    # Create Pattern Replacer
    version_replacer = PatternVersionDeclaration.from_string_definition(
        f"{test_file}:__version__:{VersionStampType.NUMBER_FORMAT.value}",
        tag_format=default_tag_format_str,
    )

    file_to_modify = version_replacer.update_file_w_version(
        new_version=Version.parse("1.2.3", tag_format=default_tag_format_str),
        noop=True,
    )

    # Evaluate
    assert file_to_modify is None
    assert (
        "VERSION PATTERN NOT FOUND: no version to stamp in file"
        in capsys.readouterr().err
    )


@pytest.mark.parametrize(
    "search_text, error_msg",
    [
        (
            search_text,
            error_msg,
        )
        for error_msg, search_text in [
            *[
                ("must use 'version' as a named group", s_text)
                for s_text in [
                    r"^version = (.*)$",
                    r"^version = (?P<Version>.*)",
                    r"(?P<vrsion>.*)",
                ]
            ],
            ("Invalid regular expression", r"*"),
        ]
    ],
)
def test_bad_version_regex_fails(search_text: str, error_msg: Pattern[str] | str):
    with pytest.raises(ValueError, match=error_msg):
        PatternVersionDeclaration(
            "doesn't matter", search_text, VersionStampType.NUMBER_FORMAT
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
                regexp(r"Invalid replacement definition .*, missing ':'"),
            ),
            (
                f"{Path(__file__)!s}:__version__:not_a_valid_version_type",
                "Invalid stamp type, must be one of:",
            ),
        ]
    ],
)
def test_pattern_declaration_w_invalid_definition(
    default_tag_format_str: str,
    replacement_def: str,
    error_msg: Pattern[str] | str,
):
    """
    check if PatternVersionDeclaration raises ValueError when loaded
    from invalid strings given in the config file
    """
    with pytest.raises(ValueError, match=error_msg):
        PatternVersionDeclaration.from_string_definition(
            replacement_def,
            default_tag_format_str,
        )
