"""Build and manage distributions
"""
from invoke import run


def build_dists():
    run('python setup.py sdist bdist_wheel')


def remove_dists(path: str):
    run(f'rm -rf {path}')
