from __future__ import annotations

import logging
from enum import IntEnum, unique


@unique
class LevelBump(IntEnum):
    """
    IntEnum representing valid types of bumps for a version.
    We use an IntEnum to enable ordering of levels.
    """

    NO_RELEASE = 0
    PRERELEASE_REVISION = 1
    PATCH = 2
    MINOR = 3
    MAJOR = 4

    def __str__(self) -> str:
        """
        Return the level name rather than 'LevelBump.<level>'
        E.g.
        >>> str(LevelBump.NO_RELEASE)
        'no_release'
        >>> str(LevelBump.MAJOR)
        'major'
        """
        return self.name.lower()

    @classmethod
    def from_string(cls, val: str) -> LevelBump:
        """
        Get the level from string representation. For backwards-compatibility,
        dashes are replaced with underscores so that:
        >>> LevelBump.from_string("no-release") == LevelBump.NO_RELEASE
        Equally,
        >>> LevelBump.from_string("minor") == LevelBump.MINOR
        """
        return cls[val.upper().replace("-", "_")]


class SemanticReleaseLogLevels(IntEnum):
    """IntEnum representing the log levels used by semantic-release."""

    FATAL = logging.FATAL
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    SILLY = 5

    def __str__(self) -> str:
        """
        Return the level name rather than 'SemanticReleaseLogLevels.<level>'
        E.g.
        >>> str(SemanticReleaseLogLevels.DEBUG)
        'DEBUG'
        >>> str(SemanticReleaseLogLevels.CRITICAL)
        'CRITICAL'
        """
        return self.name.upper()


logging.addLevelName(
    SemanticReleaseLogLevels.SILLY,
    str(SemanticReleaseLogLevels.SILLY),
)
