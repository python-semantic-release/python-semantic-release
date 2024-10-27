from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
import yaml

from semantic_release.cli.commands.main import main

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos.trunk_based_dev.repo_w_no_tags import (
    repo_with_no_tags_angular_commits,
)
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from click.testing import CliRunner

    from tests.fixtures.example_project import UpdatePyprojectTomlFn


@pytest.mark.usefixtures(repo_with_no_tags_angular_commits.__name__)
def test_stamp_version_variables_python(
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    new_version = "0.1.0"
    target_file = Path("src/example/_version.py")

    # Set configuration to modify the python file
    update_pyproject_toml(
        "tool.semantic_release.version_variables", [f"{target_file}:__version__"]
    )

    # Use the version command and prevent any action besides stamping the version
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-changelog",
        "--no-commit",
        "--no-tag",
    ]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Check the result
    assert_successful_exit_code(result, cli_cmd)

    # Load python module for reading the version (ensures the file is valid)
    spec = importlib.util.spec_from_file_location("example._version", str(target_file))
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore

    # Check the version was updated
    assert new_version == module.__version__


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

    # Use the version command and prevent any action besides stamping the version
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-changelog",
        "--no-commit",
        "--no-tag",
    ]

    # Act
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

    # Use the version command and prevent any action besides stamping the version
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-changelog",
        "--no-commit",
        "--no-tag",
    ]

    # Act
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

    # Use the version command and prevent any action besides stamping the version
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-changelog",
        "--no-commit",
        "--no-tag",
    ]

    # Act
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
