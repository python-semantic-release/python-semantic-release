"""Build and manage distributions
"""
import logging

from invoke import run

from .settings import config

logger = logging.getLogger(__name__)


def should_build():
    upload_pypi = config.get("upload_to_pypi")
    upload_release = config.get("upload_to_release")
    build_command = config.get("build_command")
    return bool(build_command and (upload_pypi or upload_release))


def should_remove_dist():
    remove_dist = config.get("remove_dist")
    return bool(remove_dist and should_build())


def build_dists():
    command = config.get("build_command")
    logger.info(f"Running {command}")
    run(command)


def remove_dists(path: str):
    command = f"rm -rf {path}"
    logger.debug(f"Running {command}")
    run(command)
