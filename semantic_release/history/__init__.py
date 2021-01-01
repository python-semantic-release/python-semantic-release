"""History
"""
import csv
import logging
import re
from typing import List, Optional, Set

import semver

from ..errors import ImproperConfigurationError
from ..helpers import LoggedFunction
from ..settings import config
from ..vcs_helpers import get_commit_log, get_last_version
from .logs import evaluate_version_bump  # noqa

from .parser_angular import parse_commit_message as angular_parser  # noqa isort:skip
from .parser_tag import parse_commit_message as tag_parser  # noqa isort:skip
from .parser_emoji import parse_commit_message as emoji_parser  # noqa isort:skip

logger = logging.getLogger(__name__)


class VersionPattern:
    """
    Represent a version number in a particular file.

    The version number is identified by a regular expression.  Methods are
    provided both the read the version number from the file, and to update the
    file with a new version number.  Use the `load_version_patterns()` factory
    function to create the version patterns specified in the config files.
    """

    version_regex = r"(\d+\.\d+(?:\.\d+)?)"

    # The pattern should be a regular expression with a single group,
    # containing the version to replace.
    def __init__(self, path: str, pattern: str):
        self.path = path
        self.pattern = pattern

    @classmethod
    def from_variable(cls, config_str: str):
        """
        Instantiate a `VersionPattern` from a string specifying a path and a
        variable name.
        """
        path, variable = config_str.split(":", 1)
        pattern = rf'{variable} *[:=] *["\']{cls.version_regex}["\']'
        return cls(path, pattern)

    @classmethod
    def from_pattern(cls, config_str: str):
        """
        Instantiate a `VersionPattern` from a string specifying a path and a
        regular expression matching the version number.
        """
        path, pattern = config_str.split(":", 1)
        pattern = pattern.format(version=cls.version_regex)
        return cls(path, pattern)

    def parse(self) -> Set[str]:
        """
        Return the versions matching this pattern.

        Because a pattern can match in multiple places, this method returns a
        set of matches.  Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but it falls on the caller
        to check for this condition.
        """
        with open(self.path, "r") as f:
            content = f.read()

        versions = {
            m.group(1) for m in re.finditer(self.pattern, content, re.MULTILINE)
        }

        logger.debug(
            f"Parsing current version: path={self.path!r} pattern={self.pattern!r} num_matches={len(versions)}"
        )
        return versions

    def replace(self, new_version: str):
        """
        Update the versions matching this pattern.

        This method reads the underlying file, replaces each occurrence of the
        matched pattern, then writes the updated file.

        :param new_version: The new version number as a string
        """
        n = 0
        with open(self.path, "r") as f:
            old_content = f.read()

        def swap_version(m):
            nonlocal n
            n += 1
            s = m.string
            i, j = m.span()
            ii, jj = m.span(1)
            return s[i:ii] + new_version + s[jj:j]

        new_content = re.sub(self.pattern, swap_version, old_content)

        logger.debug(
            f"Writing new version number: path={self.path!r} pattern={self.pattern!r} num_matches={n!r}"
        )

        with open(self.path, mode="w") as f:
            f.write(new_content)


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
    :raises ImproperConfigurationError: if either no versions are found, or
    multiple versions are found.
    """
    patterns = load_version_patterns()
    versions = set.union(*[x.parse() for x in patterns])

    if len(versions) == 0:
        raise ImproperConfigurationError(
            "no versions found in the configured locations"
        )
    if len(versions) != 1:
        version_strs = ", ".join(repr(x) for x in versions)
        raise ImproperConfigurationError(f"found conflicting versions: {version_strs}")

    version = versions.pop()
    logger.debug(f"Regex matched version: {version}")
    return version


def get_current_version() -> str:
    """
    Get current version from tag or version variable, depending on configuration.

    :return: A string with the current version number
    """
    if config.get("version_source") == "tag":
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
    return str(semver.VersionInfo.parse(current_version).next_version(part=level_bump))


@LoggedFunction(logger)
def get_previous_version(version: str) -> Optional[str]:
    """
    Return the version prior to the given version.

    :param version: A string with the version number.
    :return: A string with the previous version number.
    """
    found_version = False
    for commit_hash, commit_message in get_commit_log():
        logger.debug(f"Checking commit {commit_hash}")
        if version in commit_message:
            found_version = True
            logger.debug(f'Found version in commit "{commit_message}"')
            continue

        if found_version:
            matches = re.match(r"v?(\d+.\d+.\d+)", commit_message)
            if matches:
                logger.debug(f"Version matches regex {commit_message}")
                return matches.group(1).strip()

    return get_last_version([version, f"v{version}"])


@LoggedFunction(logger)
def set_new_version(new_version: str) -> bool:
    """
    Update the version number in each configured location.

    :param new_version: The new version number as a string.
    :return: `True` if it succeeded.
    """

    for pattern in load_version_patterns():
        pattern.replace(new_version)

    return True


def load_version_patterns() -> List[VersionPattern]:
    """
    Create the `VersionPattern` objects specified by the config file.
    """
    patterns = []

    def iter_fields(x):
        if not x:
            return
        if isinstance(x, list):
            yield from x
        else:
            # Split by commas, but allow the user to escape commas if
            # necessary.
            yield from next(csv.reader([x]))

    for version_var in iter_fields(config.get("version_variable")):
        pattern = VersionPattern.from_variable(version_var)
        patterns.append(pattern)
    for version_pat in iter_fields(config.get("version_pattern")):
        pattern = VersionPattern.from_pattern(version_pat)
        patterns.append(pattern)

    if not patterns:
        raise ImproperConfigurationError(
            "must specify either 'version_variable' or 'version_pattern'"
        )

    return patterns
