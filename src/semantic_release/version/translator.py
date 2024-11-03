from __future__ import annotations

import logging
import re

from semantic_release.const import SEMVER_REGEX
from semantic_release.helpers import check_tag_format
from semantic_release.version.version import Version

log = logging.getLogger(__name__)


class VersionTranslator:
    """
    Class to handle translation from Git tags into their corresponding Version
    instances.
    """

    _VERSION_REGEX = SEMVER_REGEX

    @classmethod
    def _invert_tag_format_to_re(cls, tag_format: str) -> re.Pattern[str]:
        r"""
        Unpick the "tag_format" format string and create a regex which can be used to
        convert a tag to a version string.

        The following relationship should always hold true:
        >>> version = "1.2.3-anything.1+at_all.1234"  # doesn't matter
        >>> tag_format = "v-anything_{version}_at-all"  # doesn't matter
        >>> inverted_format = VersionTranslator._invert_tag_format_to_re(tag_format)
        >>> tag = tag_format.format(version=version)
        >>> m = inverted_format.match(tag)
        >>> assert m is not None
        >>> assert m.expand(r"\g<version>") == version
        """
        pat = re.compile(
            tag_format.replace(r"{version}", r"(?P<version>.*)"),
            flags=re.VERBOSE,
        )
        log.debug("inverted tag_format %r to %r", tag_format, pat.pattern)
        return pat

    def __init__(
        self,
        tag_format: str = "v{version}",
        prerelease_token: str = "rc",  # noqa: S107
    ) -> None:
        check_tag_format(tag_format)
        self.tag_format = tag_format
        self.prerelease_token = prerelease_token
        self.from_tag_re = self._invert_tag_format_to_re(self.tag_format)

    def from_string(self, version_str: str) -> Version:
        """
        Return a Version instance from a string. Delegates directly to Version.parse,
        using the translator's own stored values for tag_format and prerelease
        """
        return Version.parse(
            version_str,
            tag_format=self.tag_format,
            prerelease_token=self.prerelease_token,
        )

    def from_tag(self, tag: str) -> Version | None:
        """
        Return a Version instance from a Git tag, if tag_format matches the format
        which would have generated the tag from a version. Otherwise return None.
        For example, a tag of 'v1.2.3' should be matched if `tag_format = 'v{version}`,
        but not if `tag_format = staging--v{version}`.
        """
        tag_match = self.from_tag_re.match(tag)
        if not tag_match:
            return None
        raw_version_str = tag_match.group("version")
        return self.from_string(raw_version_str)

    def str_to_tag(self, version_str: str) -> str:
        """Formats a version string into a tag name"""
        return self.tag_format.format(version=version_str)

    def __repr__(self) -> str:
        return (
            f"{type(self).__qualname__}(tag_format={self.tag_format}, "
            f"prerelease_token={self.prerelease_token})"
        )
