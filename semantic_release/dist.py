"""Build and manage distributions
"""
from invoke import run
import logging

from .settings import config


logger = logging.getLogger(__name__)


def build_dists():
    command = config.get("semantic_release", "build_command")
    logger.info(f'Running {command}')
    run(command)


def remove_dists(path: str):
    command = f"rm -rf {path}"
    logger.debug(f'Running {command}')
    run(command)
