import configparser
import os

DEFAULTS = {
    'major_tag': ':boom:',
    'minor_tag': ':sparkles:',
    'patch_tag': ':bug:',
}


def load_config():
    config = configparser.ConfigParser()
    with open(os.path.join(os.getcwd(), 'setup.cfg')) as f:
        config.read_file(f)
    settings = {}
    settings.update(DEFAULTS)
    settings.update(config._sections['semantic_release'])
    return settings
