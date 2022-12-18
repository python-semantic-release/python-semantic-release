from __future__ import annotations

import json

import pytest
import tomlkit

from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.config import RawConfig


@pytest.mark.parametrize("args", [(), ("--format", "toml"), ("--format", "TOML")])
def test_generate_config_toml(cli_runner, args):
    result = cli_runner.invoke(generate_config, args)
    assert result.exit_code == 0
    assert (
        result.output.strip()
        == tomlkit.dumps(
            {"semantic_release": RawConfig().dict(exclude_none=True)}
        ).strip()
    )


@pytest.mark.parametrize("args", [("--format", "json"), ("--format", "JSON")])
def test_generate_config_json(cli_runner, args):
    result = cli_runner.invoke(generate_config, args)
    assert result.exit_code == 0
    assert (
        result.output.strip()
        == json.dumps(
            {"semantic_release": RawConfig().dict(exclude_none=True)}, indent=4
        ).strip()
    )


def test_generate_config_pyproject_toml(cli_runner):
    result = cli_runner.invoke(generate_config, ["--format", "toml", "--pyproject"])
    assert result.exit_code == 0
    assert (
        result.output.strip()
        == tomlkit.dumps(
            {"tool": {"semantic_release": RawConfig().dict(exclude_none=True)}}
        ).strip()
    )
