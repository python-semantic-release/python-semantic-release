from __future__ import annotations

import json
import sys
from typing import Literal

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
def generate_config(
    fmt: Literal["toml", "json"], is_pyproject_toml: bool = False
) -> None:
    """
    Generate default configuration for semantic-release, to help you get started
    quickly. You can inspect the defaults, write to a file and then edit according to
    your needs. For example, to append the default configuration to your pyproject.toml
    file, you can use the following command:

        semantic-release generate-config --pyproject >> pyproject.toml
    """
    # due to possible IntEnum values (which are not supported by tomlkit.dumps, see sdispater/tomlkit#237),
    # we must ensure the transformation of the model to a dict uses json serializable values
    config_dct = {
        "semantic_release": RawConfig().model_dump(mode="json", exclude_none=True)
    }

    if is_pyproject_toml:
        output = tomlkit.dumps({"tool": config_dct})

    elif fmt == "toml":
        output = tomlkit.dumps(config_dct)

    elif fmt == "json":
        output = json.dumps(config_dct, indent=4)

    else:
        raise ValueError(f"Unsupported format: {fmt}")

    # Write output directly to stdout buffer as UTF-8 bytes
    # This ensures consistent UTF-8 output on all platforms, especially Windows where
    # shell redirection (>, >>) defaults to the system encoding (e.g., UTF-16LE or cp1252)
    # By writing to sys.stdout.buffer, we bypass the encoding layer and guarantee UTF-8.
    try:
        sys.stdout.buffer.write(f"{output.strip()}\n".encode("utf-8"))  # noqa: UP012; allow explicit encoding declaration
        sys.stdout.buffer.flush()
    except (AttributeError, TypeError):
        # Fallback for environments without buffer (shouldn't happen in standard Python)
        click.echo(output)
