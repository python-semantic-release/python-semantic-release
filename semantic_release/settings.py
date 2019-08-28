"""Settings
"""
import configparser
import importlib
import os
from os import getcwd
from typing import Callable

import ndebug
import toml

from .errors import ImproperConfigurationError

debug = ndebug.create(__name__)


def _config():
    parser = configparser.ConfigParser()
    current_dir = getcwd()
    parser.read([
        os.path.join(os.path.dirname(__file__), 'defaults.cfg'),
        os.path.join(current_dir, 'setup.cfg')
    ])
    toml_conf_path = os.path.join(current_dir, 'pyproject.toml')
    if os.path.isfile(toml_conf_path):
        with open(toml_conf_path, 'r') as pyproject_toml:
            try:
                pyproject_toml = toml.load(pyproject_toml)
                for key, value in (pyproject_toml.get('tool', {})
                                                 .get('semantic_release', {})
                                                 .items()):
                    parser['semantic_release'][key] = str(value)
            except toml.TomlDecodeError:
                debug("Could not decode pyproject.toml")

    return parser


config = _config()


def current_commit_parser() -> Callable:
    """Current commit parser

    :raises ImproperConfigurationError: if ImportError or AttributeError is raised
    """

    try:
        parts = config.get('semantic_release', 'commit_parser').split('.')
        module = '.'.join(parts[:-1])
        return getattr(importlib.import_module(module), parts[-1])
    except (ImportError, AttributeError) as error:
        raise ImproperConfigurationError('Unable to import parser "{}"'.format(error))
