"""Build and manage distributions
"""
from invoke import run

from .settings import config


def build_dists():
    command = config.get('semantic_release', 'build_command')
    run(command)


def remove_dists(path: str):
    run(f'rm -rf {path}')
