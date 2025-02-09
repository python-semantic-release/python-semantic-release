from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import tomlkit

from semantic_release.cli.commands.main import main
from semantic_release.cli.config import RawConfig

from tests.const import GENERATE_CONFIG_SUBCMD, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import repo_w_no_tags_conventional_commits
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

    from click.testing import CliRunner

    from tests.fixtures.example_project import ExProjectDir


@pytest.fixture
def raw_config_dict() -> dict[str, Any]:
    return RawConfig().model_dump(mode="json", exclude_none=True)


@pytest.mark.parametrize("args", [(), ("--format", "toml"), ("--format", "TOML")])
@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_generate_config_toml(
    cli_runner: CliRunner,
    args: tuple[str],
    raw_config_dict: dict[str, Any],
    example_project_dir: ExProjectDir,
):
    # Setup: Generate the expected configuration as a TOML string
    expected_config_as_str = tomlkit.dumps(
        {"semantic_release": raw_config_dict}
    ).strip()

    # Act: Print the generated configuration to stdout
    cli_cmd = [MAIN_PROG_NAME, GENERATE_CONFIG_SUBCMD, *args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the command ran successfully and that the output matches the expected configuration
    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()

    # Setup: Write the generated configuration to a file
    config_file = "releaserc.toml"
    example_project_dir.joinpath(config_file).write_text(result.output)

    # Act: Validate that the generated config is a valid configuration for PSR
    cli_cmd = [
        MAIN_PROG_NAME,
        "--noop",
        "--strict",
        "-c",
        config_file,
        VERSION_SUBCMD,
        "--print",
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the version command in noop mode ran successfully
    #   which means PSR loaded the configuration successfully
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.parametrize("args", [("--format", "json"), ("--format", "JSON")])
@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_generate_config_json(
    cli_runner: CliRunner,
    args: tuple[str],
    raw_config_dict: dict[str, Any],
    example_project_dir: ExProjectDir,
):
    # Setup: Generate the expected configuration as a JSON string
    expected_config_as_str = json.dumps(
        {"semantic_release": raw_config_dict}, indent=4
    ).strip()

    # Act: Print the generated configuration to stdout
    cli_cmd = [MAIN_PROG_NAME, GENERATE_CONFIG_SUBCMD, *args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the command ran successfully and that the output matches the expected configuration
    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()

    # Setup: Write the generated configuration to a file
    config_file = "releaserc.json"
    example_project_dir.joinpath(config_file).write_text(result.output)

    # Act: Validate that the generated config is a valid configuration for PSR
    cli_cmd = [
        MAIN_PROG_NAME,
        "--noop",
        "--strict",
        "-c",
        config_file,
        VERSION_SUBCMD,
        "--print",
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the version command in noop mode ran successfully
    #   which means PSR loaded the configuration successfully
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_generate_config_pyproject_toml(
    cli_runner: CliRunner,
    raw_config_dict: dict[str, Any],
    example_pyproject_toml: Path,
):
    # Setup: Generate the expected configuration as a TOML string according to PEP 518
    expected_config_as_str = tomlkit.dumps(
        {"tool": {"semantic_release": raw_config_dict}}
    ).strip()

    # Setup: Remove any current configuration from pyproject.toml
    pyproject_config = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8"))
    pyproject_config.get("tool", {}).pop("semantic_release", None)
    example_pyproject_toml.write_text(tomlkit.dumps(pyproject_config))

    # Act: Print the generated configuration to stdout
    cli_cmd = [
        MAIN_PROG_NAME,
        GENERATE_CONFIG_SUBCMD,
        "--format",
        "toml",
        "--pyproject",
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the command ran successfully and that the output matches the expected configuration
    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()

    # Setup: Write the generated configuration to a file
    example_pyproject_toml.write_text(
        str.join(
            "\n\n",
            [
                example_pyproject_toml.read_text(encoding="utf-8").strip(),
                result.output,
            ],
        )
    )

    # Act: Validate that the generated config is a valid configuration for PSR
    cli_cmd = [MAIN_PROG_NAME, "--noop", "--strict", VERSION_SUBCMD, "--print"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate: Check that the version command in noop mode ran successfully
    #   which means PSR loaded the configuration successfully
    assert_successful_exit_code(result, cli_cmd)
