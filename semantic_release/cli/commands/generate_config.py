import click
import tomlkit

from semantic_release.cli.config import RawConfig


@click.command()
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["toml"], case_sensitive=False),
    default="toml",
    help="format for the config to be generated",
)
# A "--commit/--no-commit" option? Or is this better with the "--dry-run" flag?
# how about push/no-push?
def generate_config(fmt: str = "toml") -> None:
    """
    This is the magic generate-config function that will bootstrap you a config file
    Use as follows:

    semantic-release generate-config -f toml >> pyproject.toml
    """
    config = RawConfig().dict(exclude_none=True)
    if fmt == "toml":
        print(tomlkit.dumps({"tool": {"semantic_release": config}}))
