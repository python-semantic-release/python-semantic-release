"""Helpers to read settings from setup.cfg or pyproject.toml
"""
import configparser
import importlib
import logging
import os
from collections import UserDict
from functools import wraps
from os import getcwd
from typing import Callable, List

import tomlkit
from tomlkit.exceptions import TOMLKitError

from .errors import ImproperConfigurationError

logger = logging.getLogger(__name__)


def _config():
    cwd = getcwd()
    ini_paths = [
        os.path.join(os.path.dirname(__file__), "defaults.cfg"),
        os.path.join(cwd, "setup.cfg"),
    ]
    ini_config = _config_from_ini(ini_paths)

    toml_path = os.path.join(cwd, "pyproject.toml")
    toml_config = _config_from_pyproject(toml_path)

    # Cast to a UserDict so that we can mock the get() method.
    return UserDict({**ini_config, **toml_config})


def _config_from_ini(paths):
    parser = configparser.ConfigParser()
    parser.read(paths)

    flags = {
        "changelog_capitalize",
        "changelog_scope",
        "check_build_status",
        "commit_version_number",
        "patch_without_tag",
        "major_on_zero",
        "remove_dist",
        "upload_to_pypi",
        "upload_to_release",
    }

    # Iterate through the sections so that default values are applied
    # correctly.  See:
    # https://stackoverflow.com/questions/1773793/convert-configparser-items-to-dictionary
    config = {}
    for key, _ in parser.items("semantic_release"):
        if key in flags:
            config[key] = parser.getboolean("semantic_release", key)
        else:
            config[key] = parser.get("semantic_release", key)

    return config


def _config_from_pyproject(path):
    if os.path.isfile(path):
        try:
            with open(path, "r") as f:
                pyproject = tomlkit.loads(f.read())
            if pyproject:
                return pyproject.get("tool", {}).get("semantic_release", {})
        except TOMLKitError as e:
            logger.debug(f"Could not decode pyproject.toml: {e}")

    return {}


config = _config()


def current_commit_parser() -> Callable:
    """Get the currently-configured commit parser

    :raises ImproperConfigurationError: if ImportError or AttributeError is raised
    :returns: Commit parser
    """

    try:
        # All except the last part is the import path
        parts = config.get("commit_parser").split(".")
        module = ".".join(parts[:-1])
        # The final part is the name of the parse function
        return getattr(importlib.import_module(module), parts[-1])
    except (ImportError, AttributeError) as error:
        raise ImproperConfigurationError(f'Unable to import parser "{error}"')


def current_changelog_components() -> List[Callable]:
    """Get the currently-configured changelog components

    :raises ImproperConfigurationError: if ImportError or AttributeError is raised
    :returns: List of component functions
    """
    component_paths = config.get("changelog_components").split(",")
    components = list()

    for path in component_paths:
        try:
            # All except the last part is the import path
            parts = path.split(".")
            module = ".".join(parts[:-1])
            # The final part is the name of the component function
            components.append(getattr(importlib.import_module(module), parts[-1]))
        except (ImportError, AttributeError) as error:
            raise ImproperConfigurationError(
                f'Unable to import changelog component "{path}"'
            )

    return components


def overload_configuration(func):
    """This decorator gets the content of the "define" array and edits "config"
    according to the pairs of key/value.
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        if "define" in kwargs:
            for defined_param in kwargs["define"]:
                pair = defined_param.split("=", maxsplit=1)
                if len(pair) == 2:
                    config[str(pair[0])] = pair[1]
        return func(*args, **kwargs)

    return wrap
