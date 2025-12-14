from __future__ import annotations

import json
from os import linesep
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, cast

import pytest
import tomlkit
import yaml
from dotty_dict import Dotty
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.version.declarations.enum import VersionStampType

from tests.const import EXAMPLE_PROJECT_NAME, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos.trunk_based_dev.repo_w_no_tags import (
    repo_w_no_tags_conventional_commits,
)
from tests.fixtures.repos.trunk_based_dev.repo_w_prereleases import (
    repo_w_trunk_only_n_prereleases_conventional_commits,
)
from tests.util import (
    assert_successful_exit_code,
    dynamic_python_import,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult


VERSION_STAMP_CMD = [
    MAIN_PROG_NAME,
    VERSION_SUBCMD,
    "--no-commit",
    "--no-tag",
    "--skip-build",
    "--no-changelog",
]
"""Using the version command, prevent any action besides stamping the version"""


@pytest.mark.parametrize(
    "repo_result, expected_new_version",
    [
        (
            lazy_fixture(repo_w_trunk_only_n_prereleases_conventional_commits.__name__),
            "0.3.0",
        )
    ],
)
def test_version_only_stamp_version(
    repo_result: BuiltRepoResult,
    expected_new_version: str,
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: MagicMock,
    example_pyproject_toml: Path,
    example_project_dir: ExProjectDir,
    pyproject_toml_file: Path,
) -> None:
    repo = repo_result["repo"]
    version_file = example_project_dir.joinpath(
        "src", EXAMPLE_PROJECT_NAME, "_version.py"
    )
    expected_changed_files = sorted(
        [
            str(pyproject_toml_file),
            str(version_file.relative_to(example_project_dir)),
        ]
    )

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name for tag in repo.tags}
    version_py_before = dynamic_python_import(
        version_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    pyproject_toml_before = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )

    # Modify the pyproject.toml to remove the version so we can compare it later
    pyproject_toml_before.get("tool", {}).get("poetry", {}).pop("version")

    # Act (stamp the version but also create the changelog)
    cli_cmd = [*VERSION_STAMP_CMD, "--minor"]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)
    actual_staged_files = [
        # Make sure filepath uses os specific path separators
        str(Path(file))
        # Changed files should always be staged
        for file in cast("str", repo.git.diff(staged=True, name_only=True)).splitlines()
    ]
    pyproject_toml_after = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    pyproj_version_after = (
        pyproject_toml_after.get("tool", {}).get("poetry", {}).pop("version")
    )

    # Load python module for reading the version (ensures the file is valid)
    version_py_after = dynamic_python_import(
        version_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    # Evaluate (no release actions should be taken but version should be stamped from forced minor bump)
    assert_successful_exit_code(result, cli_cmd)

    assert head_sha_before == head_after.hexsha  # No commit should be made
    assert not tags_set_difference  # No tag should be created

    # no push as it should be turned off automatically
    assert mocked_git_push.call_count == 0
    assert post_mocker.call_count == 0  # no vcs release creation occurred

    # Files that should receive version change
    assert expected_changed_files == actual_staged_files

    # Compare pyproject.toml
    assert pyproject_toml_before == pyproject_toml_after
    assert expected_new_version == pyproj_version_after

    # Compare _version.py
    assert expected_new_version == version_py_after
    assert version_py_before != version_py_after


# ============================================================================== #
#                     VERSION STAMP DIFFERENT CONTENT TYPES                      #
# ============================================================================== #


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_python(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_project_dir: ExProjectDir,
) -> None:
    new_version = "1.0.0"
    target_file = example_project_dir.joinpath(
        "src", EXAMPLE_PROJECT_NAME, "_version.py"
    )

    # Set configuration to modify the python file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [f"{target_file.relative_to(example_project_dir)}:__version__"],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Load python module for reading the version (ensures the file is valid)
    version_py_after = dynamic_python_import(
        target_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    # Check the version was updated
    assert new_version == version_py_after


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_toml(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> None:
    orig_version = "0.0.0"
    new_version = "1.0.0"
    orig_release = default_tag_format_str.format(version=orig_version)
    new_release = default_tag_format_str.format(version=new_version)
    target_file = Path("example.toml")
    orig_toml = dedent(
        f"""\
        [package]
        name = "example"
        version = "{orig_version}"
        release = "{orig_release}"
        date-released = "1970-01-01"
        """
    )

    orig_toml_obj = Dotty(tomlkit.parse(orig_toml))

    # Write initial text in file
    target_file.write_text(orig_toml)

    # Set configuration to modify the yaml file
    update_pyproject_toml(
        "tool.semantic_release.version_toml",
        [
            f"{target_file}:package.version:{VersionStampType.NUMBER_FORMAT.value}",
            f"{target_file}:package.release:{VersionStampType.TAG_FORMAT.value}",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_toml_obj = Dotty(tomlkit.parse(target_file.read_text()))

    # Check the version was updated
    assert new_version == resulting_toml_obj["package.version"]
    assert new_release == resulting_toml_obj["package.release"]

    # Check the rest of the content is the same (by resetting the version & comparing)
    resulting_toml_obj["package.version"] = orig_version
    resulting_toml_obj["package.release"] = orig_release

    assert orig_toml_obj == resulting_toml_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_yaml(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("example.yml")
    orig_yaml = dedent(
        f"""\
        ---
        package: example
        version: {orig_version}
        date-released: 1970-01-01
        """
    )
    # Write initial text in file
    target_file.write_text(orig_yaml)

    # Set configuration to modify the yaml file
    update_pyproject_toml(
        "tool.semantic_release.version_variables", [f"{target_file}:version"]
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_yaml_obj["version"]

    # Check the rest of the content is the same (by resetting the version & comparing)
    resulting_yaml_obj["version"] = orig_version

    assert yaml.safe_load(orig_yaml) == resulting_yaml_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_yaml_cff(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """
    Given a yaml file with a top level version directive,
    When the version command is run,
    Then the version is updated in the file and the rest of the content is unchanged & parsable

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/962
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("CITATION.cff")
    orig_yaml = dedent(
        f"""\
        ---
        cff-version: 1.2.0
        message: "If you use this software, please cite it as below."
        authors:
            - family-names: Doe
              given-names: Jon
              orcid: https://orcid.org/1234-6666-2222-5555
        title: "My Research Software"
        version: {orig_version}
        date-released: 1970-01-01
        """
    )
    # Write initial text in file
    target_file.write_text(orig_yaml)

    # Set configuration to modify the yaml file
    update_pyproject_toml(
        "tool.semantic_release.version_variables", [f"{target_file}:version"]
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_yaml_obj["version"]

    # Check the rest of the content is the same (by resetting the version & comparing)
    resulting_yaml_obj["version"] = orig_version

    assert yaml.safe_load(orig_yaml) == resulting_yaml_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_json(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("plugins.json")
    orig_json = {
        "id": "test-plugin",
        "version": orig_version,
        "meta": {
            "description": "Test plugin",
        },
    }
    # Write initial text in file
    target_file.write_text(json.dumps(orig_json, indent=4))

    # Set configuration to modify the json file
    update_pyproject_toml(
        "tool.semantic_release.version_variables", [f"{target_file}:version"]
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_json_obj = json.loads(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_json_obj["version"]

    # Check the rest of the content is the same (by resetting the version & comparing)
    resulting_json_obj["version"] = orig_version

    assert orig_json == resulting_json_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_yaml_github_actions(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> None:
    """
    Given a yaml file with github actions 'uses:' directives which use @vX.Y.Z version declarations,
    When a version is stamped and configured to stamp the version using the tag format,
    Then the file is updated with the new version in the tag format

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/1156
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("combined.yml")
    action1_yaml_filepath = "my-org/my-actions/.github/workflows/action1.yml"
    action2_yaml_filepath = "my-org/my-actions/.github/workflows/action2.yml"
    orig_yaml = dedent(
        f"""\
        ---
        on:
          workflow_call:

        jobs:
          action1:
            uses: {action1_yaml_filepath}@{default_tag_format_str.format(version=orig_version)}
          action2:
            uses: {action2_yaml_filepath}@{default_tag_format_str.format(version=orig_version)}
        """
    )
    expected_action1_value = (
        f"{action1_yaml_filepath}@{default_tag_format_str.format(version=new_version)}"
    )
    expected_action2_value = (
        f"{action2_yaml_filepath}@{default_tag_format_str.format(version=new_version)}"
    )

    # Setup: Write initial text in file
    target_file.write_text(orig_yaml)

    # Setup: Set configuration to modify the yaml file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [
            f"{target_file}:{action1_yaml_filepath}:{VersionStampType.TAG_FORMAT.value}",
            f"{target_file}:{action2_yaml_filepath}:{VersionStampType.TAG_FORMAT.value}",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert expected_action1_value == resulting_yaml_obj["jobs"]["action1"]["uses"]
    assert expected_action2_value == resulting_yaml_obj["jobs"]["action2"]["uses"]

    # Check the rest of the content is the same (by setting the version & comparing)
    original_yaml_obj = yaml.safe_load(orig_yaml)
    original_yaml_obj["jobs"]["action1"]["uses"] = expected_action1_value
    original_yaml_obj["jobs"]["action2"]["uses"] = expected_action2_value

    assert original_yaml_obj == resulting_yaml_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_yaml_kustomization_container_spec(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> None:
    """
    Given a yaml file with directives that expect a vX.Y.Z version tag declarations,
    When a version is stamped and configured to stamp the version using the tag format,
    Then the file is updated with the new version in the tag format

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/846
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("kustomization.yaml")
    orig_yaml = dedent(
        f"""\
        images:
          - name: repo/image
            newTag: {default_tag_format_str.format(version=orig_version)}
        """
    )
    expected_new_tag_value = default_tag_format_str.format(version=new_version)

    # Setup: Write initial text in file
    target_file.write_text(orig_yaml)

    # Setup: Set configuration to modify the yaml file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [
            f"{target_file}:newTag:{VersionStampType.TAG_FORMAT.value}",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert expected_new_tag_value == resulting_yaml_obj["images"][0]["newTag"]

    # Check the rest of the content is the same (by resetting the version & comparing)
    original_yaml_obj = yaml.safe_load(orig_yaml)
    resulting_yaml_obj["images"][0]["newTag"] = original_yaml_obj["images"][0]["newTag"]

    assert original_yaml_obj == resulting_yaml_obj


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_file_replacement_number_format(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """
    Given a VERSION file with a version number,
    When a version is stamped and configured to replace the entire file with number format,
    Then the entire file content is replaced with the new version number

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/1375
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("VERSION")

    # Setup: Write initial text in file
    target_file.write_text(orig_version)

    # Setup: Set configuration to replace the entire file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [
            f"{target_file}:*:{VersionStampType.NUMBER_FORMAT.value}",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    with target_file.open(newline="") as rfd:
        resulting_content = rfd.read()

    # Check the version was updated (entire file should be just the version)
    assert f"{new_version}{linesep}" == resulting_content


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_file_replacement_tag_format(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> None:
    """
    Given a VERSION file with a version tag,
    When a version is stamped and configured to replace the entire file with tag format,
    Then the entire file content is replaced with the new version in tag format

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/1375
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("VERSION")
    orig_tag = default_tag_format_str.format(version=orig_version)
    expected_new_tag = default_tag_format_str.format(version=new_version)

    # Setup: Write initial text in file
    target_file.write_text(orig_tag)

    # Setup: Set configuration to replace the entire file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [
            f"{target_file}:*:{VersionStampType.TAG_FORMAT.value}",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    with target_file.open(newline="") as rfd:
        resulting_content = rfd.read()

    # Check the version was updated (entire file should be just the tag)
    assert f"{expected_new_tag}{linesep}" == resulting_content


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_stamp_version_variables_file_replacement_with_whitespace(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """
    Given a VERSION file with a version number and trailing whitespace,
    When a version is stamped and configured to replace the entire file,
    Then the entire file content is replaced with just the new version (no whitespace)

    Based on https://github.com/python-semantic-release/python-semantic-release/issues/1375
    """
    orig_version = "0.0.0"
    new_version = "1.0.0"
    target_file = Path("VERSION")

    # Setup: Write initial text in file with trailing whitespace
    target_file.write_text(f"  {orig_version}  \n")

    # Setup: Set configuration to replace the entire file
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        [
            f"{target_file}:*",
        ],
    )

    # Act
    cli_cmd = VERSION_STAMP_CMD
    result = run_cli(cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    with target_file.open(newline="") as rfd:
        resulting_content = rfd.read()

    # Check the version was updated (entire file should be just the version, only trailing newline)
    assert f"{new_version}{linesep}" == resulting_content
