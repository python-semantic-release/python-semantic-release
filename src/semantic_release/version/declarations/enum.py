from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass


class VersionStampType(str, Enum):
    """Enum for the type of version declaration"""

    # The version is a number format, e.g. 1.2.3
    NUMBER_FORMAT = "nf"

    TAG_FORMAT = "tf"


class UpdateStatus(Enum):
    FILE_NOT_FOUND = auto()
    VERSION_NOT_FOUND = auto()
    NOOP = auto()
    NO_CHANGE = auto()
    UPDATED = auto()


@dataclass
class UpdateResult:
    path: Path | None
    status: UpdateStatus
