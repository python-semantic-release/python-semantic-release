"""Settings
"""
import configparser
import importlib
import os
from os import getcwd
from typing import Callable

from .errors import ImproperConfigurationError


def _config():
    parser = configparser.ConfigParser()
    parser.read([
        os.path.join(os.path.dirname(__file__), 'defaults.cfg'),
        os.path.join(getcwd(), 'setup.cfg')
    ])
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
