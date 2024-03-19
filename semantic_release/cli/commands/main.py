from __future__ import annotations

import logging

# from typing import TYPE_CHECKING
import click
from rich.console import Console
from rich.logging import RichHandler

import semantic_release
from semantic_release.cli.commands.cli_context import CliContextObj
from semantic_release.cli.config import GlobalCommandLineOptions
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import rprint

# if TYPE_CHECKING:
#     pass


FORMAT = "[%(name)s] %(levelname)s %(module)s.%(funcName)s: %(message)s"


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
    type=click.Path(),
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
@click.option(
    "--strict",
    "strict",
    is_flag=True,
    default=False,
    help="Enable strict mode",
)
@click.pass_context
def main(
    ctx: click.Context,
    config_file: str = DEFAULT_CONFIG_FILE,
    verbosity: int = 0,
    noop: bool = False,
    strict: bool = False,
) -> None:
    """
    Python Semantic Release

    Automated Semantic Versioning based on version 2.0.0 of the Semantic Versioning
    specification, which can be found at https://semver.org/spec/v2.0.0.html.

    Detect the next semantically correct version for a project based on the Git
    history, create and publish a changelog to a remote VCS, build a project.

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
            ),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.debug("logging level set to: %s", logging.getLevelName(log_level))

    if noop:
        rprint(
            ":shield: [bold cyan]You are running in no-operation mode, because the "
            "'--noop' flag was supplied"
        )

    cli_options = GlobalCommandLineOptions(
        noop=noop, verbosity=verbosity, config_file=config_file, strict=strict
    )

    logger.debug("global cli options: %s", cli_options)

    ctx.obj = CliContextObj(ctx, logger, cli_options)
