from __future__ import annotations
from enum import IntEnum, unique


@unique
class LevelBump(IntEnum):
    """
    IntEnum representing valid types of bumps for a version.
    We use an IntEnum to enable ordering of levels.
    """

    NO_RELEASE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3

    def __str__(self):
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
