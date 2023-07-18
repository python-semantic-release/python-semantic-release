from __future__ import annotations

import logging
from pathlib import Path

import click
from click.core import ParameterSource
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
from semantic_release.cli.util import load_raw_config_file, rprint
from semantic_release.errors import InvalidConfiguration, NotAReleaseBranch

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
        noop=noop,
        verbosity=verbosity,
        config_file=config_file,
        strict=strict,
    )
    log.debug("global cli options: %s", cli_options)

    config_path = Path(config_file)
    # default no config loaded
    config_text = {}
    if not config_path.exists():
        if ctx.get_parameter_source("config_file") not in (
            ParameterSource.DEFAULT,
            ParameterSource.DEFAULT_MAP,
        ):
            ctx.fail(f"File {config_file} does not exist")

        log.info(
            "configuration file %s not found, using default configuration",
            config_file,
        )

    else:
        try:
            config_text = load_raw_config_file(config_path)
        except InvalidConfiguration as exc:
            ctx.fail(str(exc))

    raw_config = RawConfig.parse_obj(config_text)
    try:
        runtime = RuntimeContext.from_raw_config(
            raw_config, repo=repo, global_cli_options=cli_options
        )
    except NotAReleaseBranch as exc:
        rprint(f"[bold {'red' if strict else 'orange1'}]{str(exc)}")
        # If not strict, exit 0 so other processes can continue. For example, in
        # multibranch CI it might be desirable to run a non-release branch's pipeline
        # without specifying conditional execution of PSR based on branch name
        ctx.exit(2 if strict else 0)
    except InvalidConfiguration as exc:
        ctx.fail(str(exc))
    ctx.obj = runtime

    # This allows us to mask secrets in the logging
    # by applying it to all the configured handlers
    for handler in logging.getLogger().handlers:
        handler.addFilter(runtime.masker)
