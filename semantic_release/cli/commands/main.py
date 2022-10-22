import configparser
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import click
import tomlkit
from git import InvalidGitRepositoryError, Repo
from rich import print as rprint
from rich.logging import RichHandler

import semantic_release
from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.config import RawConfig, RuntimeContext
from semantic_release.errors import InvalidConfiguration

FORMAT = "[%(module)s:%(funcName)s]: %(message)s"

HELP_TEXT = """\
This program is really really awesome.
"""


def _read_toml(path: str) -> Dict[str, Any]:
    raw_text = (Path() / path).resolve().read_text()
    try:
        toml_text = tomlkit.loads(raw_text)
        return toml_text["tool"]["semantic_release"]
    except KeyError as exc:
        raise InvalidConfiguration(
            f"Missing key 'tool.semantic_release' in {path}"
        ) from exc
    except tomlkit.exceptions.TOMLKitError as exc:
        raise InvalidConfiguration(f"File {path!r} contains invalid TOML") from exc


def _read_ini(path: str) -> Dict[str, Any]:
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    try:
        return dict(parser.items("semantic_release"))
    except configparser.NoSectionError as exc:
        raise InvalidConfiguration(f"Missing key 'semantic_release' in {path}") from exc
    except configparser.ParsingError as exc:
        raise InvalidConfiguration(
            f"File {path!r} contains invalid ini-format configuration"
        ) from exc


@click.group(
    context_settings={
        "ignore_unknown_options": True,
        "allow_interspersed_args": True,
    },
    help=HELP_TEXT,
)
@click.option(
    "-v",
    "--verbosity",
    "verbosity",
    help="Set logging verbosity",
    default=0,
    count=True,
    show_default=True,
    type=click.IntRange(0, 2, clamp=True),
)
@click.version_option(
    version=semantic_release.__version__, prog_name="semantic-release"
)
@click.option(
    "-c",
    "--config",
    "config_file",
    help="Specify a configuration file for semantic-release to use",
    type=click.Path(exists=True),
)
@click.pass_context
def main(
    ctx: click.Context,
    config_file: Optional[str] = None,
    verbosity: int = 0,
    **kwargs: Any,
) -> None:
    #     if not ctx.args:
    #     print(HELP_TEXT)
    #     print(ctx.get_usage())
    #     ctx.exit(0)
    log_level = [logging.WARNING, logging.INFO, logging.DEBUG][verbosity]
    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    log = logging.getLogger(__name__)

    if ctx.invoked_subcommand == generate_config.name:
        # generate-config doesn't require any of the usual setup,
        # so exit out early and delegate to it
        log.debug("Forwarding to %s", generate_config.name)
        return

    rprint("The log level is:", log_level)
    rprint(f"[cyan bold]Main kwargs: {str(kwargs)}[/cyan bold]")
    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        ctx.fail("Not in a valid Git repository")

    try:
        if config_file and config_file.endswith(".toml"):
            config_text = _read_toml(config_file)
        elif config_file and config_file.endswith((".ini", ".cfg")):
            config_text = _read_ini(config_file)
        elif config_file:
            *_, suffix = config_file.split(".")
            print(ctx.get_usage())
            ctx.fail(f"{suffix!r} is not a supported configuration format")
        else:
            try:
                config_text = _read_toml("pyproject.toml")
            except (FileNotFoundError, InvalidConfiguration):
                try:
                    config_text = _read_ini("setup.cfg")
                except FileNotFoundError as exc:
                    raise InvalidConfiguration(
                        "Couldn't find either 'pyproject.toml' or 'setup.cfg'"
                    ) from exc

    except InvalidConfiguration as exc:
        ctx.fail(str(exc))

    raw_config = RawConfig.parse_obj(config_text)
    try:
        runtime = RuntimeContext.from_raw_config(raw_config, repo=repo)
    except InvalidConfiguration as exc:
        ctx.fail(str(exc))
    ctx.obj = runtime

    log.info("All done! :sparkles:")

    # Maybe if ctx.invoked_subcommand is None we do the default
    # of ctx.forward(version), ctx.forward(changelog), git add & git commit & git tag,
    # ctx.forward(publish)?
    # The other option is to get the user to do:
    # semantic-release version && \
    #     semantic-release changelog && \
    #     semantic-release publish
    # This might have the advantage of greater flexibility, though we should
    # ensure in this case we have environment variables for common options
    # and/or config?
    # The node impl. does just `npx semantic-release` though...
