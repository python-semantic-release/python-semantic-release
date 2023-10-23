from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, cast

import tomlkit
from dotty_dict import Dotty  # type: ignore[import]

from semantic_release.version.version import Version

log = logging.getLogger(__name__)


class VersionDeclarationABC(ABC):
    """
    ABC for classes representing a location in which a version is declared somewhere
    within the source tree of the repository
    """

    def __init__(self, path: Path | str, search_text: str) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"path {self.path.resolve()!r} does not exist")
        self.search_text = search_text
        self._content: str | None = None

    @property
    def content(self) -> str:
        """
        The content of the source file in which the version is stored. This property
        is cached in the instance variable _content
        """
        if self._content is None:
            log.debug(
                "No content stored, reading from source file %s", self.path.resolve()
            )
            self._content = self.path.read_text()
        return self._content

    # mypy doesn't like properties?
    @content.setter  # type: ignore[attr-defined]
    def _(self, _: Any) -> None:
        raise AttributeError("'content' cannot be set directly")

    @content.deleter  # type: ignore[attr-defined]
    def _(self) -> None:
        log.debug("resetting instance-stored source file contents")
        self._content = None

    @abstractmethod
    def parse(self) -> set[Version]:
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
        r"""
        Write new content back to the source path.
        Use alongside .replace():
        >>> class MyVD(VersionDeclarationABC):
        ...     def parse(self): ...
        ...     def replace(self, new_version: Version): ...
        ...     def write(self, content: str): ...

        >>> new_version = Version.parse("1.2.3")
        >>> vd = MyVD("path", r"__version__ = (?P<version>\d+\d+\d+)")
        >>> vd.write(vd.replace(new_version))
        """
        log.debug("writing content to %r", self.path.resolve())
        self.path.write_text(content)
        self._content = None


class TomlVersionDeclaration(VersionDeclarationABC):
    """VersionDeclarationABC implementation which manages toml-format source files."""

    def _load(self) -> Dotty:
        """Load the content of the source file into a Dotty for easier searching"""
        loaded = tomlkit.loads(self.content)
        return Dotty(loaded)

    def parse(self) -> set[Version]:
        """Look for the version in the source content"""
        content = self._load()
        maybe_version: str = content.get(self.search_text)  # type: ignore[return-value]
        if maybe_version is not None:
            log.debug(
                "Found a key %r that looks like a version (%r)",
                self.search_text,
                maybe_version,
            )
            valid_version = Version.parse(maybe_version)
            return {valid_version} if valid_version else set()
        # Maybe in future raise error if not found?
        return set()

    def replace(self, new_version: Version) -> str:
        """
        Replace the version in the source content with `new_version`, and return the
        updated content.
        """
        content = self._load()
        if self.search_text in content:
            log.info(
                "found %r in source file contents, replacing with %s",
                self.search_text,
                new_version,
            )
            content[self.search_text] = str(new_version)

        return tomlkit.dumps(cast(Dict[str, Any], content))


class PatternVersionDeclaration(VersionDeclarationABC):
    """
    VersionDeclarationABC implementation representing a version number in a particular
    file. The version number is identified by a regular expression, which should be
    provided in `search_text`.
    """

    _VERSION_GROUP_NAME = "version"

    def __init__(self, path: Path | str, search_text: str) -> None:
        super().__init__(path, search_text)
        self.search_re = re.compile(self.search_text, flags=re.MULTILINE)
        if self._VERSION_GROUP_NAME not in self.search_re.groupindex:
            raise ValueError(
                f"Invalid search text {self.search_text!r}; must use 'version' as a "
                "named group, for example (?P<version>...) . For more info on named "
                "groups see https://docs.python.org/3/library/re.html"
            )

    # The pattern should be a regular expression with a single group,
    # containing the version to replace.
    def parse(self) -> set[Version]:
        """
        Return the versions matching this pattern.
        Because a pattern can match in multiple places, this method returns a
        set of matches.  Generally, there should only be one element in this
        set (i.e. even if the version is specified in multiple places, it
        should be the same version in each place), but it falls on the caller
        to check for this condition.
        """
        versions = {
            Version.parse(m.group(self._VERSION_GROUP_NAME))
            for m in self.search_re.finditer(self.content, re.MULTILINE)
        }

        log.debug(
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

        def swap_version(m: re.Match[str]) -> str:
            nonlocal n
            n += 1
            s = m.string
            i, j = m.span()
            log.debug("match spans characters %s:%s", i, j)
            ii, jj = m.span(self._VERSION_GROUP_NAME)
            log.debug("version group spans characters %s:%s", ii, jj)
            return s[i:ii] + str(new_version) + s[jj:j]

        new_content, n_matches = self.search_re.subn(
            swap_version, self.content, re.MULTILINE
        )

        log.debug(
            "path=%r pattern=%r num_matches=%r", self.path, self.search_text, n_matches
        )

        return new_content
