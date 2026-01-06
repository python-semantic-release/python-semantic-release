from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from deprecated.sphinx import deprecated

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from semantic_release.version.version import Version


class IVersionReplacer(metaclass=ABCMeta):
    """
    Interface for subclasses that replace a version string in a source file.

    Methods generally have a base implementation are implemented here but
    likely just provide a not-supported message but return gracefully

    This class cannot be instantiated directly but must be inherited from
    and implement the designated abstract methods.
    """

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        # Validate that the subclass implements all of the abstract methods.
        # This supports isinstance and issubclass checks.
        return bool(
            cls is IVersionReplacer
            and all(
                bool(hasattr(subclass, method) and callable(getattr(subclass, method)))
                for method in IVersionReplacer.__abstractmethods__
            )
        )

    @deprecated(
        version="9.20.0",
        reason="Function is unused and will be removed in a future release",
    )
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
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def replace(self, new_version: Version) -> str:
        """
        Replace the version in the source content with `new_version`, and return
        the updated content.

        :param new_version: The new version number as a `Version` instance
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def update_file_w_version(
        self, new_version: Version, noop: bool = False
    ) -> Path | None:
        """
        This method reads the underlying file, replaces each occurrence of the
        matched pattern, then writes the updated file.

        :param new_version: The new version number as a `Version` instance
        """
        raise NotImplementedError  # pragma: no cover
