import configparser
import os

config = configparser.ConfigParser()
config.read([
    os.path.join(os.path.dirname(__file__), 'defaults.cfg'),
    os.path.join(os.getcwd(), 'setup.cfg')
])
