from __future__ import annotations

import logging
import re

from semantic_release.const import SEMVER_REGEX
from semantic_release.helpers import check_tag_format
from semantic_release.version.version import Version

log = logging.getLogger(__name__)


class VersionTranslator:
    _VERSION_REGEX = SEMVER_REGEX

    @classmethod
    def _invert_tag_format_to_re(cls, tag_format: str) -> re.Pattern[str]:
        pat = re.compile(
            tag_format.replace(r"{version}", r"(?P<version>.*)"),
            flags=re.VERBOSE,
        )
        log.debug("inverted tag_format %r to %r", tag_format, pat.pattern)
        return pat

    def __init__(
        self, tag_format: str = "v{version}", prerelease_token: str = "rc"
    ) -> None:
        check_tag_format(tag_format)
        self.tag_format = tag_format
        self.prerelease_token = prerelease_token
        self.from_tag_re = self._invert_tag_format_to_re(self.tag_format)

    def from_string(self, version_str: str) -> Version:
        return Version.parse(
            version_str,
            tag_format=self.tag_format,
            prerelease_token=self.prerelease_token,
        )

    def from_tag(self, tag: str) -> Version:
        tag_match = self.from_tag_re.match(tag)
        if not tag_match:
            raise ValueError(
                f"Tag {tag!r} doesn't match tag format {self.tag_format!r}"
            )
        raw_version_str = tag_match.group("version")
        m = self._VERSION_REGEX.fullmatch(raw_version_str)
        if not m:
            raise ValueError(
                f"Tag {tag!r} doesn't match tag format {self.tag_format!r}"
            )
        return self.from_string(m.string)

    def str_to_tag(self, version_str: str) -> str:
        return self.tag_format.format(version=version_str)
