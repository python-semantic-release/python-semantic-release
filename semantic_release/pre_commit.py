"""Run commands prior to the release commit
"""
import logging

from invoke import run

from .settings import config

logger = logging.getLogger(__name__)


def should_run_pre_commit():
    command = config.get("pre_commit_command")
    return bool(command)


def run_pre_commit():
    command = config.get("pre_commit_command")
    logger.debug(f"Running {command}")
    run(command)
