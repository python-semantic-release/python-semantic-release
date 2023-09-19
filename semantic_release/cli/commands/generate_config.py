from __future__ import annotations

import json

import click
import tomlkit

from semantic_release.cli.config import RawConfig


@click.command(
    short_help="Generate semantic-release's default configuration",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["toml", "json"], case_sensitive=False),
    default="toml",
    help="format for the config to be generated",
)
@click.option(
    "--pyproject",
    "is_pyproject_toml",
    is_flag=True,
    help=(
        "Add TOML configuration under 'tool.semantic_release' instead of "
        "'semantic_release'"
    ),
)
def generate_config(fmt: str = "toml", is_pyproject_toml: bool = False) -> None:
    """
    Generate default configuration for semantic-release, to help you get started
    quickly. You can inspect the defaults, write to a file and then edit according to
    your needs. For example, to append the default configuration to your pyproject.toml
    file, you can use the following command:

        semantic-release generate-config -f toml >> pyproject.toml
    """
    config = RawConfig().model_dump(exclude_none=True)

    config_dct = {"semantic_release": config}
    if is_pyproject_toml and fmt == "toml":
        config_dct = {"tool": config_dct}

    if fmt == "toml":
        click.echo(tomlkit.dumps(config_dct))

    elif fmt == "json":
        click.echo(json.dumps(config_dct, indent=4))
