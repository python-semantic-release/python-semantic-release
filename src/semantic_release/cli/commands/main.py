from __future__ import annotations

import importlib
import logging
from enum import Enum

# from typing import TYPE_CHECKING
import click
from rich.console import Console
from rich.logging import RichHandler

import semantic_release
from semantic_release import globals
from semantic_release.cli.cli_context import CliContextObj
from semantic_release.cli.config import GlobalCommandLineOptions
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import rprint
from semantic_release.enums import SemanticReleaseLogLevels

# if TYPE_CHECKING:
#     pass


FORMAT = "%(message)s"
LOG_LEVELS = [
    SemanticReleaseLogLevels.WARNING,
    SemanticReleaseLogLevels.INFO,
    SemanticReleaseLogLevels.DEBUG,
    SemanticReleaseLogLevels.SILLY,
]


class Cli(click.MultiCommand):
    """Root MultiCommand for the semantic-release CLI"""

    class SubCmds(Enum):
        """Subcommand import definitions"""

        # SUBCMD_FUNCTION_NAME => MODULE_WITH_FUNCTION
        CHANGELOG = f"{__package__}.changelog"
        GENERATE_CONFIG = f"{__package__}.generate_config"
        VERSION = f"{__package__}.version"
        PUBLISH = f"{__package__}.publish"

    def list_commands(self, _ctx: click.Context) -> list[str]:
        # Used for shell-completion
        return [subcmd.lower().replace("_", "-") for subcmd in Cli.SubCmds.__members__]

    def get_command(self, _ctx: click.Context, name: str) -> click.Command | None:
        subcmd_name = name.lower().replace("-", "_")
        try:
            subcmd_def: Cli.SubCmds = Cli.SubCmds.__dict__[subcmd_name.upper()]
            module_path = subcmd_def.value
            subcmd_module = importlib.import_module(module_path)
            return getattr(subcmd_module, subcmd_name)
        except (KeyError, ModuleNotFoundError, AttributeError):
            return None


@click.command(
    cls=Cli,
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
    type=click.IntRange(0, len(LOG_LEVELS) - 1, clamp=True),
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
    globals.log_level = LOG_LEVELS[verbosity]

    # Set up our pretty console formatter
    rich_handler = RichHandler(
        console=Console(stderr=True), rich_tracebacks=True, tracebacks_suppress=[click]
    )
    rich_handler.setFormatter(logging.Formatter(FORMAT, datefmt="[%X]"))

    # Set up logging with our pretty console formatter
    logger = globals.logger
    logger.handlers.clear()
    logger.filters.clear()
    logger.addHandler(rich_handler)
    logger.setLevel(globals.log_level)
    logger.debug("logging level set to: %s", logging.getLevelName(globals.log_level))

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
