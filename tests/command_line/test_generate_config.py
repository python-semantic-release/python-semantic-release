from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import tomlkit

from semantic_release.cli.commands.main import main
from semantic_release.cli.config import RawConfig

from tests.const import GENERATE_CONFIG_SUBCMD, MAIN_PROG_NAME
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from typing import Any

    from tests.command_line.conftest import CliRunner


@pytest.fixture
def raw_config_dict() -> dict[str, Any]:
    return RawConfig().model_dump(mode="json", exclude_none=True)


@pytest.mark.parametrize("args", [(), ("--format", "toml"), ("--format", "TOML")])
def test_generate_config_toml(
    cli_runner: CliRunner, args: tuple[str], raw_config_dict: dict[str, Any]
):
    expected_config_as_str = tomlkit.dumps(
        {"semantic_release": raw_config_dict}
    ).strip()

    cli_cmd = [MAIN_PROG_NAME, GENERATE_CONFIG_SUBCMD, *args]

    result = cli_runner.invoke(main, cli_cmd[1:])

    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()


@pytest.mark.parametrize("args", [("--format", "json"), ("--format", "JSON")])
def test_generate_config_json(
    cli_runner: CliRunner, args: tuple[str], raw_config_dict: dict[str, Any]
):
    expected_config_as_str = json.dumps(
        {"semantic_release": raw_config_dict}, indent=4
    ).strip()

    cli_cmd = [MAIN_PROG_NAME, GENERATE_CONFIG_SUBCMD, *args]

    result = cli_runner.invoke(main, cli_cmd[1:])

    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()


def test_generate_config_pyproject_toml(
    cli_runner: CliRunner, raw_config_dict: dict[str, Any]
):
    expected_config_as_str = tomlkit.dumps(
        {"tool": {"semantic_release": raw_config_dict}}
    ).strip()

    cli_cmd = [
        MAIN_PROG_NAME,
        GENERATE_CONFIG_SUBCMD,
        "--format",
        "toml",
        "--pyproject",
    ]

    result = cli_runner.invoke(main, cli_cmd[1:])

    assert_successful_exit_code(result, cli_cmd)
    assert expected_config_as_str == result.output.strip()
