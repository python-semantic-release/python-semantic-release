"""Build and manage distributions
"""
import logging
import shutil

from invoke import run

from .settings import config

logger = logging.getLogger(__name__)


def should_build():
    upload_to_artifact_repository = config.get("upload_to_repository") and config.get(
        "upload_to_pypi"
    )
    upload_release = config.get("upload_to_release")
    build_command = config.get("build_command")
    build_command = build_command if build_command != "false" else False
    return bool(build_command and (upload_to_artifact_repository or upload_release))


def should_remove_dist():
    remove_dist = config.get("remove_dist")
    return bool(remove_dist and should_build())


def build_dists():
    command = config.get("build_command")
    logger.info(f"Running {command}")
    run(command)


def remove_dists(path: str):
    logger.debug(f"Removing build folder: `{path}`")
    shutil.rmtree(path, ignore_errors=True)
