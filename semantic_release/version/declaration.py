import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Set, Union

import tomlkit
from dotty_dict import Dotty

from semantic_release.version.version import Version

logger = logging.getLogger(__name__)


class VersionDeclarationABC(ABC):
    def __init__(self, path: Union[Path, str], search_text: str) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"path {self.path.resolve()!r} does not exist")
        self.search_text = search_text
        self._content: Optional[str] = None

    @property
    def content(self) -> str:
        if self._content is None:
            self._content = self.path.read_text()
        return self._content

    @content.setter
    def _(self, _: Any) -> None:
        raise AttributeError("'content' cannot be set directly")

    @content.deleter
    def _(self) -> None:
        self._content = None

    @abstractmethod
    def parse(self) -> Set[Version]:
        """
        Return a set of the versions which can be parsed from the file.
        Because a source can match in multiple places, this method returns a
        set of matches. Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but enforcing that condition
        is not mandatory or expected.
        """

    @abstractmethod
    def replace(self, new_version: Version) -> str:
        """
        Update the versions.
        This method reads the underlying file, replaces each occurrence of the
        matched pattern, then writes the updated file.
        :param new_version: The new version number as a `Version` instance
        """

    def write(self, content: str) -> None:
        logger.debug("writing content to %r", self.path.resolve())
        self.path.write_text(content)
        self._content = None


class TomlVersionDeclaration(VersionDeclarationABC):
    def _load(self) -> Dotty:
        loaded = tomlkit.loads(self.content)
        return Dotty(loaded)

    def parse(self) -> Set[Version]:
        content = self._load()
        maybe_version = content.get(self.search_text)
        if maybe_version is not None:
            logger.debug("Found a string %r that looks like a version", maybe_version)
            valid_version = Version.parse(maybe_version)
            return {valid_version}
        # TODO: maybe raise error if not found?
        return set()

    def replace(self, new_version: Version) -> str:
        content = self._load()
        if self.search_text in content:
            content[self.search_text] = str(new_version)
        return tomlkit.dumps(content)


class PatternVersionDeclaration(VersionDeclarationABC):
    """
    Represent a version number in a particular file.
    The version number is identified by a regular expression.  Methods are
    provided both the read the version number from the file, and to update the
    file with a new version number.  Use the `load_version_patterns()` factory
    function to create the version patterns specified in the config files.
    """

    # The pattern should be a regular expression with a single group,
    # containing the version to replace.
    def parse(self) -> Set[Version]:
        """
        Return the versions matching this pattern.
        Because a pattern can match in multiple places, this method returns a
        set of matches.  Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but it falls on the caller
        to check for this condition.
        """
        versions = {
            Version.parse(m.group(1))
            for m in re.finditer(self.search_text, self.content, re.MULTILINE)
        }

        logger.debug(
            "Parsing current version: path=%r pattern=%r num_matches=%s",
            self.path.resolve(),
            self.search_text,
            len(versions),
        )
        return versions

    def replace(self, new_version: Version) -> str:
        """
        Update the versions.
        This method reads the underlying file, replaces each occurrence of the
        matched pattern, then writes the updated file.
        :param new_version: The new version number as a `Version` instance
        """
        n = 0

        def swap_version(m):
            nonlocal n
            n += 1
            s = m.string
            i, j = m.span()
            ii, jj = m.span(1)
            return s[i:ii] + str(new_version) + s[jj:j]

        new_content = re.sub(
            self.search_text, swap_version, self.content, flags=re.MULTILINE
        )

        logger.debug(
            "path=%r pattern=%r num_matches=%r", self.path, self.search_text, n
        )

        return new_content
