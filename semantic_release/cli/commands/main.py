from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import click
import tomlkit
from git import InvalidGitRepositoryError
from git.repo.base import Repo
from rich.console import Console
from rich.logging import RichHandler

import semantic_release
from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import rprint
from semantic_release.errors import InvalidConfiguration

FORMAT = "[%(name)s] %(module)s:%(funcName)s: %(message)s"


def _read_toml(path: str) -> dict[str, Any]:
    raw_text = (Path() / path).resolve().read_text(encoding="utf-8")
    try:
        toml_text = tomlkit.loads(raw_text)
    except tomlkit.exceptions.TOMLKitError as exc:
        raise InvalidConfiguration(f"File {path!r} contains invalid TOML") from exc

    # Look for [tool.semantic_release]
    cfg_text = toml_text.get("tool", {}).get("semantic_release")
    if cfg_text is not None:
        return cfg_text
    # Look for [semantic_release]
    cfg_text = toml_text.get("semantic_release")
    if cfg_text is not None:
        return cfg_text

    raise InvalidConfiguration(
        f"Missing keys 'tool.semantic_release' or 'semantic_release' in {path}"
    )


@click.group(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.version_option(
    version=semantic_release.__version__,
    prog_name="semantic-release",
    help="Show the version of semantic-release and exit",
)
@click.option(
    "-c",
    "--config",
    "config_file",
    default=DEFAULT_CONFIG_FILE,
    help="Specify a configuration file for semantic-release to use",
    type=click.Path(exists=True),
)
@click.option("--noop", "noop", is_flag=True, help="Run semantic-release in no-op mode")
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    help="Set logging verbosity",
    default=0,
    count=True,
    show_default=True,
    type=click.IntRange(0, 2, clamp=True),
)
@click.pass_context
def main(
    ctx: click.Context,
    config_file: str = DEFAULT_CONFIG_FILE,
    verbosity: int = 0,
    noop: bool = False,
) -> None:
    """
    Python Semantic Release

    Automated Semantic Versioning based on version 2.0.0 of the Semantic Versioning
    specification, which can be found at https://semver.org/spec/v2.0.0.html.

    Detect the next semantically correct version for a project based on the Git
    history, create and publish a changelog to a remote VCS, build a project.

    If the project is written in Python, distributions can also be
    uploaded to a remote Python package repository using twine.

    For more information, visit https://python-semantic-release.readthedocs.io/
    """

    console = Console(stderr=True)

    log_level = [logging.WARNING, logging.INFO, logging.DEBUG][verbosity]
    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console, rich_tracebacks=True, tracebacks_suppress=[click]
            )
        ],
    )

    log = logging.getLogger(__name__)

    if ctx.invoked_subcommand == generate_config.name:
        # generate-config doesn't require any of the usual setup,
        # so exit out early and delegate to it
        log.debug("Forwarding to %s", generate_config.name)
        return

    log.debug("logging level set to: %s", logging.getLevelName(log_level))
    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        ctx.fail("Not in a valid Git repository")

    if noop:
        rprint(
            ":shield: [bold cyan]You are running in no-operation mode, because the "
            "'--noop' flag was supplied"
        )
    cli_options = GlobalCommandLineOptions(
        noop=noop, verbosity=verbosity, config_file=config_file
    )

    try:
        if config_file and config_file.endswith(".toml"):
            rprint(f"Loading TOML configuration from {config_file}")
            config_text = _read_toml(config_file)
        elif config_file and config_file.endswith(".json"):
            rprint(f"Loading JSON configuration from {config_file}")
            raw_text = (Path() / config_file).resolve().read_text(encoding="utf-8")
            config_text = json.loads(raw_text)["semantic_release"]
        elif config_file:
            *_, suffix = config_file.split(".")
            ctx.fail(f"{suffix!r} is not a supported configuration format")
    except (FileNotFoundError, InvalidConfiguration) as exc:
        ctx.fail(str(exc))

    raw_config = RawConfig.parse_obj(config_text)
    try:
        runtime = RuntimeContext.from_raw_config(
            raw_config, repo=repo, global_cli_options=cli_options
        )
    except InvalidConfiguration as exc:
        ctx.fail(str(exc))
    ctx.obj = runtime

    # This allows us to mask secrets in the logging
    # by applying it to all the configured handlers
    for handler in logging.getLogger().handlers:
        handler.addFilter(runtime.masker)
