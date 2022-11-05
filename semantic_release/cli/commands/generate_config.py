import json

import click
import tomlkit

from semantic_release.cli.config import RawConfig


@click.command(short_help="Generate semantic-release's default configuration")
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["toml", "json"], case_sensitive=False),
    default="toml",
    help="format for the config to be generated",
)
# A "--commit/--no-commit" option? Or is this better with the "--dry-run" flag?
# how about push/no-push?
def generate_config(fmt: str = "toml") -> None:
    """
    Generate default configuration for semantic-release, to help you get started
    quickly. You can inspect the defaults, write to a file and then edit according to
    your needs. For example, to append the default configuration to your pyproject.toml
    file, you can use the following command:

        semantic-release generate-config -f toml >> pyproject.toml
    """
    config = RawConfig().dict(exclude_none=True)
    if fmt == "toml":
        click.echo(tomlkit.dumps({"tool": {"semantic_release": config}}))
    elif fmt == "json":
        click.echo(json.dumps({"semantic_release": config}, indent=4))
