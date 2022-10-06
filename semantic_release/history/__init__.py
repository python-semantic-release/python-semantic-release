"""History
"""
import csv
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set, Union

import semver
import tomlkit
from dotty_dict import Dotty

from ..errors import ImproperConfigurationError
from ..helpers import LoggedFunction
from ..settings import config
from ..vcs_helpers import get_commit_log, get_formatted_tag, get_last_version
from .logs import evaluate_version_bump  # noqa

from .parser_angular import parse_commit_message as angular_parser  # noqa isort:skip
from .parser_emoji import parse_commit_message as emoji_parser  # noqa isort:skip
from .parser_scipy import parse_commit_message as scipy_parser  # noqa isort:skip
from .parser_tag import parse_commit_message as tag_parser  # noqa isort:skip

logger = logging.getLogger(__name__)


def get_prerelease_pattern():
    return rf"-{config.get('prerelease_tag')}\.\d+"


def get_pattern_with_commit_subject(pattern):
    escaped_commit_subject = re.escape(config.get("commit_subject"))
    return escaped_commit_subject.replace(r"\{version\}", pattern)


def get_version_pattern():
    prerelease_pattern = get_prerelease_pattern()
    return rf"(\d+\.\d+\.\d+({prerelease_pattern})?)"


def get_release_version_pattern():
    prerelease_pattern = get_prerelease_pattern()
    return rf"v?(\d+\.\d+\.\d+(?!.*{prerelease_pattern}))"


def get_commit_release_version_pattern():
    prerelease_pattern = get_prerelease_pattern()
    return get_pattern_with_commit_subject(
        rf"v?(\d+\.\d+\.\d+(?!.*{prerelease_pattern}))"
    )


class VersionDeclaration(ABC):
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    @staticmethod
    def from_toml(config_str: str):
        """
        Instantiate a `TomlVersionDeclaration` from a string specifying a path and a key
        matching the version number.
        """
        path, key = config_str.split(":", 1)
        return TomlVersionDeclaration(path, key)

    @staticmethod
    def from_variable(config_str: str):
        """
        Instantiate a `PatternVersionDeclaration` from a string specifying a path and a
        variable name.
        """
        path, variable = config_str.split(":", 1)
        version_pattern = get_version_pattern()
        pattern = rf'{variable} *[:=] *["\']{version_pattern}["\']'
        return PatternVersionDeclaration(path, pattern)

    @staticmethod
    def from_pattern(config_str: str):
        """
        Instantiate a `PatternVersionDeclaration` from a string specifying a path and a
        regular expression matching the version number.
        """
        path, pattern = config_str.split(":", 1)
        pattern = pattern.format(version=get_version_pattern())
        return PatternVersionDeclaration(path, pattern)

    @abstractmethod
    def parse(self) -> Set[str]:
        """
        Return the versions.

        Because a source can match in multiple places, this method returns a
        set of matches. Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but it falls on the caller
        to check for this condition.
        """

    @abstractmethod
    def replace(self, new_version: str):
        """
        Update the versions.

        This method reads the underlying file, replaces each occurrence of the
        matched pattern, then writes the updated file.

        :param new_version: The new version number as a string
        """


class TomlVersionDeclaration(VersionDeclaration):
    def __init__(self, path, key):
        super().__init__(path)
        self.key = key

    def _read(self) -> Dotty:
        toml_doc = tomlkit.loads(self.path.read_text())
        return Dotty(toml_doc)

    def parse(self) -> Set[str]:
        _config = self._read()
        if self.key in _config:
            return {_config.get(self.key)}
        return set()

    def replace(self, new_version: str) -> None:
        _config = self._read()
        if self.key in _config:
            _config[self.key] = new_version
            self.path.write_text(tomlkit.dumps(_config))


class PatternVersionDeclaration(VersionDeclaration):
    """
    Represent a version number in a particular file.

    The version number is identified by a regular expression.  Methods are
    provided both the read the version number from the file, and to update the
    file with a new version number.  Use the `load_version_patterns()` factory
    function to create the version patterns specified in the config files.
    """

    # The pattern should be a regular expression with a single group,
    # containing the version to replace.
    def __init__(self, path: str, pattern: str):
        super().__init__(path)
        self.pattern = pattern

    def parse(self) -> Set[str]:
        """
        Return the versions matching this pattern.

        Because a pattern can match in multiple places, this method returns a
        set of matches.  Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but it falls on the caller
        to check for this condition.
        """
        content = self.path.read_text()

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
        old_content = self.path.read_text()

        def swap_version(m):
            nonlocal n
            n += 1
            s = m.string
            i, j = m.span()
            ii, jj = m.span(1)
            return s[i:ii] + new_version + s[jj:j]

        new_content = re.sub(
            self.pattern, swap_version, old_content, flags=re.MULTILINE
        )

        logger.debug(
            f"Writing new version number: path={self.path!r} pattern={self.pattern!r} num_matches={n!r}"
        )

        self.path.write_text(new_content)


@LoggedFunction(logger)
def get_current_version_by_tag() -> str:
    """
    Find the current version of the package in the current working directory using git tags.

    :return: A string with the version number or 0.0.0 on failure.
    """
    version = get_last_version(pattern=get_version_pattern())
    if version:
        return version

    logger.debug("no version found, returning default of v0.0.0")
    return "0.0.0"


@LoggedFunction(logger)
def get_current_release_version_by_tag() -> str:
    """
    Find the current version of the package in the current working directory using git tags.

    :return: A string with the version number or 0.0.0 on failure.
    """
    version = get_last_version(pattern=get_release_version_pattern())
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
    declarations = load_version_declarations()
    versions = set.union(*[x.parse() for x in declarations])

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
    This can be either a release or prerelease version

    :return: A string with the current version number
    """
    if config.get("version_source") in ["tag", "tag_only"]:
        return get_current_version_by_tag()
    else:
        return get_current_version_by_config_file()


def get_current_release_version() -> str:
    """
    Get current release version from tag or commit message (no going back in config file),
    depending on configuration.
    This will return the current release version (NOT prerelease), instead of just the current version

    :return: A string with the current version number
    """
    if config.get("version_source") in ["tag", "tag_only"]:
        return get_current_release_version_by_tag()
    else:
        return get_current_release_version_by_commits()


@LoggedFunction(logger)
def get_new_version(
    current_version: str,
    current_release_version: str,
    level_bump: str,
    prerelease: bool = False,
    prerelease_patch: bool = True,
) -> str:
    """
    Calculate the next version based on the given bump level with semver.

    :param current_version: The version the package has now.
    :param level_bump: The level of the version number that should be bumped.
        Should be `'major'`, `'minor'` or `'patch'`.
    :param prerelease: Should the version bump be marked as a prerelease
    :return: A string with the next version number.
    """
    # pre or release version
    current_version_info = semver.VersionInfo.parse(current_version)
    # release version
    current_release_version_info = semver.VersionInfo.parse(current_release_version)

    # sanity check
    # if the current version is no prerelease, than
    # current_version and current_release_version must be the same
    if (
        not current_version_info.prerelease
        and current_version_info.compare(current_release_version_info) != 0
    ):
        raise ValueError(
            f"Error: Current version {current_version} and current release version {current_release_version} do not match!"
        )

    if level_bump:
        next_version_info = current_release_version_info.next_version(level_bump)
    elif prerelease:
        if prerelease_patch:
            # we do at least a patch for prereleases
            next_version_info = current_release_version_info.next_version("patch")
        elif current_version_info.compare(current_release_version_info) > 0:
            next_version_info = current_version_info
        else:
            next_version_info = current_release_version_info
    else:
        next_version_info = current_release_version_info

    if prerelease and (level_bump or prerelease_patch):
        next_raw_version = next_version_info.to_tuple()[:3]
        current_raw_version = current_version_info.to_tuple()[:3]

        if current_version_info.prerelease and next_raw_version == current_raw_version:
            # next version (based on commits) matches current prerelease version
            # bump prerelase
            next_prerelease_version_info = current_version_info.bump_prerelease(
                config.get("prerelease_tag")
            )
        else:
            # next version (based on commits) higher than current prerelease version
            # new prerelease based on next version
            next_prerelease_version_info = next_version_info.bump_prerelease(
                config.get("prerelease_tag")
            )

        return str(next_prerelease_version_info)
    else:
        # normal version bump
        return str(next_version_info)


@LoggedFunction(logger)
def get_previous_version(version: str) -> Optional[str]:
    """
    Return the version prior to the given version.

    :param version: A string with the version number.
    :return: A string with the previous version number.
    """
    version_pattern = get_version_pattern()

    found_version = False
    for commit_hash, commit_message in get_commit_log():
        logger.debug(f"Checking commit {commit_hash}")
        if version in commit_message:
            found_version = True
            logger.debug(f'Found version in commit "{commit_message}"')
            continue

        if found_version:
            match = re.search(version_pattern, commit_message)
            if match:
                logger.debug(f"Version matches regex {commit_message}")
                return match.group(1).strip()

    return get_last_version(
        pattern=version_pattern, skip_tags=[version, get_formatted_tag(version)]
    )


@LoggedFunction(logger)
def get_previous_release_version(version: str) -> Optional[str]:
    """
    Return the version prior to the given version.

    :param version: A string with the version number.
    :return: A string with the previous version number.
    """
    release_version_pattern = get_commit_release_version_pattern()

    found_version = False
    for commit_hash, commit_message in get_commit_log():
        logger.debug(f"Checking commit {commit_hash}")
        if version in commit_message:
            found_version = True
            logger.debug(f'Found version in commit "{commit_message}"')
            continue

        if found_version:
            match = re.search(release_version_pattern, commit_message)
            if match:
                logger.debug(f"Version matches regex {commit_message}")
                return match.group(1).strip()

    return get_last_version(
        pattern=release_version_pattern, skip_tags=[version, get_formatted_tag(version)]
    )


@LoggedFunction(logger)
def get_current_release_version_by_commits() -> str:
    """
    Return the current release version (NOT prerelease) version.

    :return: A string with the current version number.
    """
    release_version_re = re.compile(get_commit_release_version_pattern())

    for commit_hash, commit_message in get_commit_log():
        logger.debug(f"Checking commit {commit_hash}")
        match = release_version_re.match(commit_message)
        if match:
            logger.debug(f"Version matches regex {commit_message}")
            return match.group(1).strip()

    # nothing found, return the initial version
    return "0.0.0"


@LoggedFunction(logger)
def set_new_version(new_version: str) -> bool:
    """
    Update the version number in each configured location.

    :param new_version: The new version number as a string.
    :return: `True` if it succeeded.
    """

    for declaration in load_version_declarations():
        declaration.replace(new_version)

    return True


def load_version_declarations() -> List[VersionDeclaration]:
    """
    Create the `VersionDeclaration` objects specified by the config file.
    """
    declarations = []

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
        declaration = VersionDeclaration.from_variable(version_var)
        declarations.append(declaration)
    for version_pat in iter_fields(config.get("version_pattern")):
        declaration = VersionDeclaration.from_pattern(version_pat)
        declarations.append(declaration)
    for version_toml in iter_fields(config.get("version_toml")):
        declaration = VersionDeclaration.from_toml(version_toml)
        declarations.append(declaration)

    if not declarations:
        raise ImproperConfigurationError(
            "must specify either 'version_variable', 'version_pattern' or 'version_toml'"
        )

    return declarations
