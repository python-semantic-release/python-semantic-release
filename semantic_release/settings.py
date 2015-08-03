import configparser
import os
from os import getcwd


def _config():
    parser = configparser.ConfigParser()
    parser.read([
        os.path.join(os.path.dirname(__file__), 'defaults.cfg'),
        os.path.join(getcwd(), 'setup.cfg')
    ])
    return parser

config = _config()
