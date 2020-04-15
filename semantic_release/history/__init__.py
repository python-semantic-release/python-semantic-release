"""History
"""
import logging
import re
from typing import Optional

import semver

from ..errors import ImproperConfigurationError
from ..helpers import LoggedFunction
from ..settings import config
from ..vcs_helpers import get_commit_log, get_last_version
from .logs import evaluate_version_bump  # noqa

from .parser_angular import parse_commit_message as angular_parser  # noqa isort:skip
from .parser_tag import parse_commit_message as tag_parser  # noqa isort:skip

logger = logging.getLogger(__name__)


@LoggedFunction(logger)
def get_current_version_by_tag() -> str:
    """
    Find the current version of the package in the current working directory using git tags.

    :return: A string with the version number or 0.0.0 on failure.
    """
    version = get_last_version()
    if version:
        return version

    logger.debug("no version found, returning default of v0.0.0")
    return "0.0.0"


@LoggedFunction(logger)
def get_current_version_by_config_file() -> str:
    """
    Get current version from the version variable defined in the configuration.

    :return: A string with the current version number
    :raises ImproperConfigurationError: if version variable cannot be parsed
    """
    # Get the file and variable names from configuration
    filename, variable = config.get("semantic_release", "version_variable").split(":")
    variable = variable.strip()
    logger.debug(f"Looking for current version in {filename}, variable {variable}")

    with open(filename, "r") as fd:
        file_text = fd.read()
        # checks for variable in the format variable=version
        parts = re.search(
            r'^{0}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(variable), file_text, re.MULTILINE
        )
        # checks for variable in the format variable:version
        if not parts:
            parts = re.search(
                r'{0}\s*:\s*[\'"]([^\'"]*)[\'"]'.format(variable),
                file_text,
                re.MULTILINE,
            )
        if not parts:
            raise ImproperConfigurationError

        logger.debug(f"Regex matched version: {parts}")
        return parts.group(1)


def get_current_version() -> str:
    """
    Get current version from tag or version variable, depending on configuration.

    :return: A string with the current version number
    """
    if config.get("semantic_release", "version_source") == "tag":
        return get_current_version_by_tag()
    return get_current_version_by_config_file()


@LoggedFunction(logger)
def get_new_version(current_version: str, level_bump: str) -> str:
    """
    Calculate the next version based on the given bump level with semver.

    :param current_version: The version the package has now.
    :param level_bump: The level of the version number that should be bumped.
        Should be `'major'`, `'minor'` or `'patch'`.
    :return: A string with the next version number.
    """
    if not level_bump:
        logger.debug("No bump requested, returning input version")
        return current_version
    return getattr(semver, "bump_{0}".format(level_bump))(current_version)


@LoggedFunction(logger)
def get_previous_version(version: str) -> Optional[str]:
    """
    Return the version prior to the given version.

    :param version: A string with the version number.
    :return: A string with the previous version number.
    """
    found_version = False
    for commit_hash, commit_message in get_commit_log():
        logger.debug("Checking commit {}".format(commit_hash))
        if version in commit_message:
            found_version = True
            logger.debug('Found version in commit "{}"'.format(commit_message))
            continue

        if found_version:
            matches = re.match(r"v?(\d+.\d+.\d+)", commit_message)
            if matches:
                logger.debug("Version matches regex", commit_message)
                return matches.group(1).strip()

    return get_last_version([version, "v{}".format(version)])


def replace_version_string(content, variable, new_version):
    """
    Given the content of a file, find the version string and updates it.

    :param content: The file contents
    :param variable: The version variable name as a string
    :param new_version: The new version number as a string
    :return: A string with the updated version number
    """
    new_content = re.sub(
        r'({0} ?= ?["\'])\d+\.\d+(?:\.\d+)?(["\'])'.format(variable),
        r"\g<1>{0}\g<2>".format(new_version),
        content,
    )
    # The version string did not change because above regex did not match. Use : instead of =
    if new_content == content:
        new_content = re.sub(
            r'({0} ?: ?["\'])\d+\.\d+(?:\.\d+)?(["\'])'.format(variable),
            r"\g<1>{0}\g<2>".format(new_version),
            content,
        )
    return new_content


@LoggedFunction(logger)
def set_new_version(new_version: str) -> bool:
    """
    Replace the version number in the correct place and write the changed file to disk.

    :param new_version: The new version number as a string.
    :return: `True` if it succeeded.
    """
    # Read the contents of the file
    filename, variable = config.get("semantic_release", "version_variable").split(":")
    variable = variable.strip()
    with open(filename, mode="r") as fr:
        content = fr.read()

    # Update the version variable
    content = replace_version_string(content, variable, new_version)

    # Write the update back to the file
    with open(filename, mode="w") as fw:
        fw.write(content)

    return True
