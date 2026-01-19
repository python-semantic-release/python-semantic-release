"""Utilities for command-line functionality"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent, indent
from typing import Any

import rich
import rich.markup
import tomlkit
from tomlkit.exceptions import TOMLKitError

from semantic_release.errors import InvalidConfiguration
from semantic_release.globals import logger


def rprint(msg: str) -> None:
    """Rich-prints to stderr so that redirection of command output isn't cluttered"""
    rich.print(msg, file=sys.stderr)


def noop_report(msg: str) -> None:
    """
    Rich-prints a msg with a standard prefix to report when an action is not being
    taken due to a "noop" flag
    """
    rprint(f"[bold cyan][:shield: NOP] {rich.markup.escape(msg)}")


def indented(msg: str, prefix: str = " " * 4) -> str:
    """
    Convenience function for text-formatting for the console.

    Ensures the least indented line of the msg string is indented by ``prefix`` with
    consistent alignment of the remainder of ``msg`` irrespective of the level of
    indentation in the Python source code
    """
    return indent(dedent(msg), prefix=prefix)


def parse_toml(raw_text: str) -> dict[Any, Any]:
    """
    Attempts to parse raw configuration for semantic_release
    using tomlkit.loads, raising InvalidConfiguration if the
    TOML is invalid or there's no top level "semantic_release"
    or "tool.semantic_release" keys
    """
    try:
        toml_text = tomlkit.loads(raw_text).unwrap()
    except TOMLKitError as exc:
        raise InvalidConfiguration(str(exc)) from exc

    # Look for [tool.semantic_release]
    cfg_text = toml_text.get("tool", {}).get("semantic_release")
    if cfg_text is not None:
        return cfg_text
    # Look for [semantic_release] or return {} if not found
    return toml_text.get("semantic_release", {})


def load_raw_config_file(config_file: Path | str) -> dict[Any, Any]:
    """
    Load raw configuration as a dict from the filename specified
    by config_filename, trying the following parsing methods:

    1. try to parse with tomli.load (guessing it's a TOML file)
    2. try to parse with json.load (guessing it's a JSON file)
    3. raise InvalidConfiguration if none of the above parsing
       methods work

    This function will also raise FileNotFoundError if it is raised
    while trying to read the specified configuration file
    """
    logger.info("Loading configuration from %s", config_file)
    raw_text = (Path() / config_file).resolve().read_text(encoding="utf-8-sig")
    try:
        logger.debug("Trying to parse configuration %s in TOML format", config_file)
        return parse_toml(raw_text)
    except InvalidConfiguration as e:
        logger.debug("Configuration %s is invalid TOML: %s", config_file, str(e))
        logger.debug("trying to parse %s as JSON", config_file)
        try:
            # could be a "parse_json" function but it's a one-liner here
            return json.loads(raw_text)["semantic_release"]
        except KeyError:
            # valid configuration, but no "semantic_release" or "tool.semantic_release"
            # top level key
            logger.debug(
                "configuration has no 'semantic_release' or 'tool.semantic_release' "
                "top-level key"
            )
            return {}
        except json.JSONDecodeError as jde:
            raise InvalidConfiguration(
                dedent(
                    f"""
                    None of the supported configuration parsers were able to parse
                    the configuration file {config_file}:
                    * TOML: {e!s}
                    * JSON: {jde!s}
                    """
                )
            ) from jde
