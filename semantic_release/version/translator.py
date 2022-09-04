from __future__ import annotations
import re
import string
from typing import Optional, Union

from semver import VersionInfo as Version

# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER_REGEX = re.compile(
    r"""
    (?P<major>0|[1-9]\d*)
    \.
    (?P<minor>0|[1-9]\d*)
    \.
    (?P<patch>0|[1-9]\d*)
    (?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
    (?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?
    """,
    flags=re.VERBOSE,
)


class VersionTranslator:
    _VERSION_REGEX = SEMVER_REGEX

    @staticmethod
    def _check_tag_format(tag_format: str) -> None:
        if "version" not in (f[1] for f in string.Formatter().parse(tag_format)):
            raise ValueError(
                f"Invalid tag_format {tag_format!r}, must use 'version' as a format key"
            )

    @classmethod
    def _invert_tag_format_to_re(cls, tag_format: str) -> str:
        return re.compile(
            tag_format.replace(
                r"{version}", r"(?P<version>.*)"
            ),
            flags=re.VERBOSE,
        )

    def __init__(
        self, tag_format: str = "v{version}", prerelease_suffix: Optional[str] = "rc"
    ) -> None:
        self._check_tag_format(tag_format)
        self.tag_format = tag_format
        self.prerelease_suffix = prerelease_suffix
        self.from_tag_re = self._invert_tag_format_to_re(self.tag_format)

    def from_string(self, version_str: str) -> Version:
        return Version.parse(version_str)

    def from_tag(self, tag: str) -> Version:
        raw_version_str = self.from_tag_re.match(tag).group("version")
        m = self._VERSION_REGEX.fullmatch(raw_version_str)
        if not m:
            raise ValueError(
                f"Tag {tag!r} doesn't match tag format {self.tag_format!r}"
            )
        return Version.parse(m.string)

    def to_tag(self, version: Union[Version, str]) -> str:
        return self.tag_format.format(version=str(version))
