"""Build and manage distributions
"""
from invoke import run

from .settings import config


def build_dists():
    commands = config.get('semantic_release', 'build_commands')
    run(f'python setup.py {commands}')


def remove_dists(path: str):
    run(f'rm -rf {path}')
