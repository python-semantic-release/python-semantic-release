from __future__ import annotations

from enum import Enum


class VersionStampType(str, Enum):
    """Enum for the type of version declaration"""

    # The version is a number format, e.g. 1.2.3
    NUMBER_FORMAT = "nf"

    TAG_FORMAT = "tf"
