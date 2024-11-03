from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
import tomlkit
import yaml
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main

from tests.const import EXAMPLE_PROJECT_NAME, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos.trunk_based_dev.repo_w_no_tags import (
    repo_with_no_tags_angular_commits,
)
from tests.fixtures.repos.trunk_based_dev.repo_w_prereleases import (
    repo_with_single_branch_and_prereleases_angular_commits,
)
from tests.util import (
    assert_successful_exit_code,
    dynamic_python_import,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git import Repo

    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn


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
    "repo, expected_new_version",
    [
        (
            lazy_fixture(
                repo_with_single_branch_and_prereleases_angular_commits.__name__
            ),
            "0.3.0",
        )
    ],
)
def test_version_only_stamp_version(
    repo: Repo,
    expected_new_version: str,
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: MagicMock,
    example_pyproject_toml: Path,
    example_project_dir: ExProjectDir,
    example_changelog_md: Path,
    example_changelog_rst: Path,
) -> None:
    version_file = example_project_dir.joinpath(
        "src", EXAMPLE_PROJECT_NAME, "_version.py"
    )
    expected_changed_files = sorted(
        [
            "pyproject.toml",
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
    pyproject_toml_before["tool"]["poetry"].pop("version")  # type: ignore[attr-defined]

    # Act (stamp the version but also create the changelog)
    cli_cmd = [*VERSION_STAMP_CMD, "--minor"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name for tag in repo.tags}
    tags_set_difference = set.difference(tags_after, tags_before)
    differing_files = [
        # Make sure filepath uses os specific path separators
        str(Path(file))
        for file in str(repo.git.diff(name_only=True)).splitlines()
    ]
    pyproject_toml_after = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    pyproj_version_after = pyproject_toml_after["tool"]["poetry"].pop(  # type: ignore[attr-defined]
        "version"
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
    assert post_mocker.call_count == 0  # no vcs release creation occured

    # Files that should receive version change
    assert expected_changed_files == differing_files

    # Compare pyproject.toml
    assert pyproject_toml_before == pyproject_toml_after
    assert expected_new_version == pyproj_version_after

    # Compare _version.py
    assert expected_new_version == version_py_after
    assert version_py_before != version_py_after


# ============================================================================== #
#                     VERSION STAMP DIFFERENT CONTENT TYPES                      #
# ============================================================================== #


@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_stamp_version_variables_python(
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_project_dir: ExProjectDir,
) -> None:
    new_version = "0.1.0"
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
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Load python module for reading the version (ensures the file is valid)
    version_py_after = dynamic_python_import(
        target_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    # Check the version was updated
    assert new_version == version_py_after


@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_stamp_version_variables_yaml(
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    orig_version = "0.0.0"
    new_version = "0.1.0"
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
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_yaml_obj["version"]

    # Check the rest of the content is the same (by reseting the version & comparing)
    resulting_yaml_obj["version"] = orig_version

    assert yaml.safe_load(orig_yaml) == resulting_yaml_obj


@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_stamp_version_variables_yaml_cff(
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    orig_version = "0.0.0"
    new_version = "0.1.0"
    target_file = Path("CITATION.cff")
    # Derived format from python-semantic-release/python-semantic-release#962
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
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_yaml_obj = yaml.safe_load(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_yaml_obj["version"]

    # Check the rest of the content is the same (by reseting the version & comparing)
    resulting_yaml_obj["version"] = orig_version

    assert yaml.safe_load(orig_yaml) == resulting_yaml_obj


@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_stamp_version_variables_json(
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    orig_version = "0.0.0"
    new_version = "0.1.0"
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
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Read content
    resulting_json_obj = json.loads(target_file.read_text())

    # Check the version was updated
    assert new_version == resulting_json_obj["version"]

    # Check the rest of the content is the same (by reseting the version & comparing)
    resulting_json_obj["version"] = orig_version

    assert orig_json == resulting_json_obj
