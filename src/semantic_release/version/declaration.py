from __future__ import annotations

# TODO: Remove v11
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from deprecated.sphinx import deprecated

from semantic_release.globals import logger
from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.file import FileVersionDeclaration
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.declarations.pattern import PatternVersionDeclaration
from semantic_release.version.declarations.toml import TomlVersionDeclaration

if TYPE_CHECKING:  # pragma: no cover
    from semantic_release.version.version import Version


# Globals
__all__ = [
    "FileVersionDeclaration",
    "IVersionReplacer",
    "PatternVersionDeclaration",
    "TomlVersionDeclaration",
    "VersionDeclarationABC",
    "VersionStampType",
]


@deprecated(
    version="9.20.0",
    reason=str.join(
        " ",
        [
            "Refactored to composition paradigm using the new IVersionReplacer interface.",
            "This class will be removed in a future release",
        ],
    ),
)
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
            logger.debug(
                "No content stored, reading from source file %s", self.path.resolve()
            )
            self._content = self.path.read_text()
        return self._content

    @content.deleter
    def content(self) -> None:
        logger.debug("resetting instance-stored source file contents")
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
        logger.debug("writing content to %r", self.path.resolve())
        self.path.write_text(content)
        self._content = None
