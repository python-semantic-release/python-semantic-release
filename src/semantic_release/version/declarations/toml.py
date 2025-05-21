from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, cast

import tomlkit
from deprecated.sphinx import deprecated
from dotty_dict import Dotty

from semantic_release.cli.util import noop_report
from semantic_release.globals import logger
from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.version import Version


class TomlVersionDeclaration(IVersionReplacer):
    def __init__(
        self, path: Path | str, search_text: str, stamp_format: VersionStampType
    ) -> None:
        self._content: str | None = None
        self._path = Path(path).resolve()
        self._stamp_format = stamp_format
        self._search_text = search_text

    @property
    def content(self) -> str:
        """A cached property that stores the content of the configured source file."""
        if self._content is None:
            logger.debug("No content stored, reading from source file %s", self._path)

            if not self._path.exists():
                raise FileNotFoundError(f"path {self._path!r} does not exist")

            self._content = self._path.read_text()

        return self._content

    @content.deleter
    def content(self) -> None:
        self._content = None

    @deprecated(
        version="9.20.0",
        reason="Function is unused and will be removed in a future release",
    )
    def parse(self) -> set[Version]:  # pragma: no cover
        """Look for the version in the source content"""
        content = self._load()
        maybe_version: str = content.get(self._search_text)  # type: ignore[return-value]
        if maybe_version is not None:
            logger.debug(
                "Found a key %r that looks like a version (%r)",
                self._search_text,
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
        if self._search_text in content:
            logger.info(
                "found %r in source file contents, replacing with %s",
                self._search_text,
                new_version,
            )
            content[self._search_text] = (
                new_version.as_tag()
                if self._stamp_format == VersionStampType.TAG_FORMAT
                else str(new_version)
            )

        return tomlkit.dumps(cast(Dict[str, Any], content))

    def _load(self) -> Dotty:
        """Load the content of the source file into a Dotty for easier searching"""
        return Dotty(tomlkit.loads(self.content))

    def update_file_w_version(
        self, new_version: Version, noop: bool = False
    ) -> Path | None:
        if noop:
            if not self._path.exists():
                noop_report(
                    f"FILE NOT FOUND: cannot stamp version in non-existent file {self._path!r}",
                )
                return None

            if self._search_text not in self._load():
                noop_report(
                    f"VERSION PATTERN NOT FOUND: no version to stamp in file {self._path!r}",
                )
                return None

            return self._path

        new_content = self.replace(new_version)
        if new_content == self.content:
            return None

        self._path.write_text(new_content)
        del self.content

        return self._path

    @classmethod
    def from_string_definition(cls, replacement_def: str) -> TomlVersionDeclaration:
        """
        create an instance of self from a string representing one item
        of the "version_toml" list in the configuration
        """
        parts = replacement_def.split(":", maxsplit=2)

        if len(parts) <= 1:
            raise ValueError(
                f"Invalid TOML replacement definition {replacement_def!r}, missing ':'"
            )

        if len(parts) == 2:
            # apply default version_type of "number_format" (ie. "1.2.3")
            parts = [*parts, VersionStampType.NUMBER_FORMAT.value]

        path, search_text, version_type = parts

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

        return cls(path, search_text, stamp_type)
