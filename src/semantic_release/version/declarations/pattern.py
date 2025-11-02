from __future__ import annotations

from pathlib import Path
from re import (
    MULTILINE,
    compile as regexp,
    error as RegExpError,  # noqa: N812
    escape as regex_escape,
)
from typing import TYPE_CHECKING

from deprecated.sphinx import deprecated

from semantic_release.cli.util import noop_report
from semantic_release.const import SEMVER_REGEX
from semantic_release.globals import logger
from semantic_release.version.declarations.enum import VersionStampType
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.version import Version

if TYPE_CHECKING:  # pragma: no cover
    from re import Match


class VersionSwapper:
    """Callable to replace a version number in a string with a new version number."""

    def __init__(self, new_version_str: str, group_match_name: str) -> None:
        self.version_str = new_version_str
        self.group_match_name = group_match_name

    def __call__(self, match: Match[str]) -> str:
        i, j = match.span()
        ii, jj = match.span(self.group_match_name)
        return f"{match.string[i:ii]}{self.version_str}{match.string[jj:j]}"


class PatternVersionDeclaration(IVersionReplacer):
    """
    VersionDeclarationABC implementation representing a version number in a particular
    file. The version number is identified by a regular expression, which should be
    provided in `search_text`.
    """

    _VERSION_GROUP_NAME = "version"

    def __init__(
        self, path: Path | str, search_text: str, stamp_format: VersionStampType
    ) -> None:
        self._content: str | None = None
        self._path = Path(path).resolve()
        self._stamp_format = stamp_format

        try:
            self._search_pattern = regexp(search_text, flags=MULTILINE)
        except RegExpError as err:
            raise ValueError(
                f"Invalid regular expression for search text: {search_text!r}"
            ) from err

        if self._VERSION_GROUP_NAME not in self._search_pattern.groupindex:
            raise ValueError(
                str.join(
                    " ",
                    [
                        f"Invalid search text {search_text!r}; must use",
                        f"'{self._VERSION_GROUP_NAME}' as a named group, for example",
                        f"(?P<{self._VERSION_GROUP_NAME}>...) . For more info on named",
                        "groups see https://docs.python.org/3/library/re.html",
                    ],
                )
            )

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
            for m in self._search_pattern.finditer(self.content)
        }

        logger.debug(
            "Parsing current version: path=%r pattern=%r num_matches=%s",
            self._path.resolve(),
            self._search_pattern,
            len(versions),
        )
        return versions

    def replace(self, new_version: Version) -> str:
        """
        Replace the version in the source content with `new_version`, and return
        the updated content.

        :param new_version: The new version number as a `Version` instance
        """
        new_content, n_matches = self._search_pattern.subn(
            VersionSwapper(
                new_version_str=(
                    new_version.as_tag()
                    if self._stamp_format == VersionStampType.TAG_FORMAT
                    else str(new_version)
                ),
                group_match_name=self._VERSION_GROUP_NAME,
            ),
            self.content,
        )

        logger.debug(
            "path=%r pattern=%r num_matches=%r",
            self._path,
            self._search_pattern,
            n_matches,
        )

        return new_content

    def update_file_w_version(
        self, new_version: Version, noop: bool = False
    ) -> Path | None:
        if noop:
            if not self._path.exists():
                noop_report(
                    f"FILE NOT FOUND: cannot stamp version in non-existent file {self._path}",
                )
                return None

            if len(self._search_pattern.findall(self.content)) < 1:
                noop_report(
                    f"VERSION PATTERN NOT FOUND: no version to stamp in file {self._path}",
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
    def from_string_definition(
        cls, replacement_def: str, tag_format: str
    ) -> PatternVersionDeclaration:
        """
        create an instance of self from a string representing one item
        of the "version_variables" list in the configuration
        """
        parts = replacement_def.split(":", maxsplit=2)

        if len(parts) <= 1:
            raise ValueError(
                f"Invalid replacement definition {replacement_def!r}, missing ':'"
            )

        if len(parts) == 2:
            # apply default version_type of "number_format" (ie. "1.2.3")
            parts = [*parts, VersionStampType.NUMBER_FORMAT.value]

        path, variable, version_type = parts

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

        # DEFAULT: naked (no v-prefixed) semver version
        value_replace_pattern_str = (
            f"(?P<{cls._VERSION_GROUP_NAME}>{SEMVER_REGEX.pattern})"
        )

        if version_type == VersionStampType.TAG_FORMAT.value:
            tag_parts = tag_format.strip().split(r"{version}", maxsplit=1)
            value_replace_pattern_str = str.join(
                "",
                [
                    f"(?P<{cls._VERSION_GROUP_NAME}>",
                    regex_escape(tag_parts[0]),
                    SEMVER_REGEX.pattern,
                    (regex_escape(tag_parts[1]) if len(tag_parts) > 1 else ""),
                    ")",
                ],
            )

        search_text = str.join(
            "",
            [
                # Supports optional matching quotations around variable name
                # Negative lookbehind to ensure we don't match part of a variable name
                f"""(?x)(?P<quote1>['"])?(?<![\\w.-]){regex_escape(variable)}(?P=quote1)?""",
                # Supports walrus, equals sign, double-equals, colon, or @ as assignment operator
                # ignoring whitespace separation. Also allows a space as the separator for c-macro style definitions.
                r"\s*(:=|==|[:=@ ])\s*",
                # Supports optional matching quotations around a version pattern (tag or raw format)
                f"""(?P<quote2>['"])?{value_replace_pattern_str}(?P=quote2)?""",
            ],
        )

        return cls(path, search_text, stamp_type)
