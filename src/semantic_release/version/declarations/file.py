from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from deprecated.sphinx import deprecated

from semantic_release.globals import logger
from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer

if TYPE_CHECKING:  # pragma: no cover
    from semantic_release.version.version import Version


class FileVersionDeclaration(IVersionReplacer):
    """
    IVersionReplacer implementation that replaces the entire file content
    with the version string.

    This is useful for files that contain only a version number, such as
    VERSION files or similar single-line version storage files.
    """

    def __init__(self, path: Path | str, stamp_format: VersionStampType) -> None:
        self._content: str | None = None
        self._path = Path(path).resolve()
        self._stamp_format = stamp_format

    @property
    def content(self) -> str:
        """A cached property that stores the content of the configured source file."""
        if self._content is None:
            logger.debug("No content stored, reading from source file %s", self._path)

            if not self._path.exists():
                logger.debug(
                    f"path {self._path!r} does not exist, assuming empty content"
                )
                self._content = ""
            else:
                self._content = self._path.read_text()

        return self._content

    @content.deleter
    def content(self) -> None:
        self._content = None

    @deprecated(
        version="10.6.0",
        reason="Function is unused and will be removed in a future release",
    )
    def parse(self) -> set[Version]:
        raise NotImplementedError  # pragma: no cover

    def replace(self, new_version: Version) -> str:
        """
        Replace the file content with the new version string.

        :param new_version: The new version number as a `Version` instance
        :return: The new content (just the version string)
        """
        new_content = (
            new_version.as_tag()
            if self._stamp_format == VersionStampType.TAG_FORMAT
            else str(new_version)
        )

        logger.debug(
            "Replacing entire file content: path=%r old_content=%r new_content=%r",
            self._path,
            self.content.strip(),
            new_content,
        )

        return new_content

    def update_file_w_version(
        self, new_version: Version, noop: bool = False
    ) -> Path | None:
        if noop:
            if not self._path.exists():
                logger.warning(
                    f"FILE NOT FOUND: file '{self._path}' does not exist but it will be created"
                )

            return self._path

        new_content = self.replace(new_version)
        if new_content == self.content.strip():
            return None

        self._path.write_text(f"{new_content}\n")
        del self.content

        return self._path

    @classmethod
    def from_string_definition(cls, replacement_def: str) -> FileVersionDeclaration:
        """
        Create an instance of self from a string representing one item
        of the "version_variables" list in the configuration.

        This method expects a definition in the format:
        "file:*:format_type"

        where:
        - file is the path to the file
        - * is the literal asterisk character indicating file replacement
        - format_type is either "nf" (number format) or "tf" (tag format)
        """
        parts = replacement_def.split(":", maxsplit=2)

        if len(parts) <= 1:
            raise ValueError(
                f"Invalid replacement definition {replacement_def!r}, missing ':'"
            )

        if len(parts) == 2:
            # apply default version_type of "number_format" (ie. "1.2.3")
            parts = [*parts, VersionStampType.NUMBER_FORMAT.value]

        path, pattern, version_type = parts

        # Validate that the pattern is exactly "*"
        if pattern != "*":
            raise ValueError(
                f"Invalid pattern {pattern!r} for FileVersionDeclaration, expected '*'"
            )

        try:
            stamp_type = VersionStampType(version_type)
        except ValueError as err:
            raise ValueError(
                str.join(
                    " ",
                    [
                        "Invalid stamp type, must be one of:",
                        str.join(", ", [e.value for e in VersionStampType]),
                    ],
                )
            ) from err

        return cls(path, stamp_type)
