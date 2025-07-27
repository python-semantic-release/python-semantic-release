from __future__ import annotations

from itertools import zip_longest
from typing import Tuple

from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import ParserOptions
from semantic_release.enums import LevelBump


@dataclass
class ConventionalCommitParserOptions(ParserOptions):
    """Options dataclass for the ConventionalCommitParser."""

    minor_tags: Tuple[str, ...] = ("feat",)
    """Commit-type prefixes that should result in a minor release bump."""

    patch_tags: Tuple[str, ...] = ("fix", "perf")
    """Commit-type prefixes that should result in a patch release bump."""

    other_allowed_tags: Tuple[str, ...] = (
        "build",
        "chore",
        "ci",
        "docs",
        "style",
        "refactor",
        "test",
    )
    """Commit-type prefixes that are allowed but do not result in a version bump."""

    allowed_tags: Tuple[str, ...] = (
        *minor_tags,
        *patch_tags,
        *other_allowed_tags,
    )
    """
    All commit-type prefixes that are allowed.

    These are used to identify a valid commit message. If a commit message does not start with
    one of these prefixes, it will not be considered a valid commit message.
    """

    default_bump_level: LevelBump = LevelBump.NO_RELEASE
    """The minimum bump level to apply to valid commit message."""

    parse_squash_commits: bool = True
    """Toggle flag for whether or not to parse squash commits"""

    ignore_merge_commits: bool = True
    """Toggle flag for whether or not to ignore merge commits"""

    @property
    def tag_to_level(self) -> dict[str, LevelBump]:
        """A mapping of commit tags to the level bump they should result in."""
        return self._tag_to_level

    def __post_init__(self) -> None:
        self._tag_to_level: dict[str, LevelBump] = {
            str(tag): level
            for tag, level in [
                # we have to do a type ignore as zip_longest provides a type that is not specific enough
                # for our expected output. Due to the empty second array, we know the first is always longest
                # and that means no values in the first entry of the tuples will ever be a LevelBump. We
                # apply a str() to make mypy happy although it will never happen.
                *zip_longest(self.allowed_tags, (), fillvalue=self.default_bump_level),
                *zip_longest(self.patch_tags, (), fillvalue=LevelBump.PATCH),
                *zip_longest(self.minor_tags, (), fillvalue=LevelBump.MINOR),
            ]
            if "|" not in str(tag)
        }
