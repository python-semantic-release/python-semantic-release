"""Helpers to read settings from setup.cfg or pyproject.toml
"""
import configparser
import importlib
import os
from functools import wraps
from os import getcwd
from typing import Callable

import ndebug
import toml

from .errors import ImproperConfigurationError

debug = ndebug.create(__name__)


def _config():
    # Read setup.cfg, falling back to defaults.cfg
    current_dir = getcwd()
    parser = configparser.ConfigParser()
    parser.read([
        os.path.join(os.path.dirname(__file__), 'defaults.cfg'),
        os.path.join(current_dir, 'setup.cfg')
    ])

    toml_conf_path = os.path.join(current_dir, 'pyproject.toml')
    if os.path.isfile(toml_conf_path):
        # Overwrite with any settings from pyproject.toml
        with open(toml_conf_path, 'r') as pyproject_toml:
            try:
                pyproject_toml = toml.load(pyproject_toml)
                pyproject_toml_settings = (
                    pyproject_toml.get('tool', {})
                    .get('semantic_release', {})
                    .items()
                )
                for key, value in pyproject_toml_settings:
                    parser['semantic_release'][key] = str(value)
            except toml.TomlDecodeError:
                debug("Could not decode pyproject.toml")

    return parser


config = _config()


def current_commit_parser() -> Callable:
    """Get the currently-configured commit parser

    :raises ImproperConfigurationError: if ImportError or AttributeError is raised
    :returns: Commit parser
    """

    try:
        # All except the last part is the import path
        parts = config.get('semantic_release', 'commit_parser').split('.')
        module = '.'.join(parts[:-1])
        # The final part is the name of the parse function
        return getattr(importlib.import_module(module), parts[-1])
    except (ImportError, AttributeError) as error:
        raise ImproperConfigurationError('Unable to import parser "{}"'.format(error))


def overload_configuration(func):
    """This decorator gets the content of the "define" array and edits "config"
    according to the pairs of key/value.
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'define' in kwargs:
            for defined_param in kwargs['define']:
                pair = defined_param.split('=', maxsplit=1)
                if len(pair) == 2:
                    config['semantic_release'][str(pair[0])] = str(pair[1])
        return func(*args, **kwargs)

    return wrap
