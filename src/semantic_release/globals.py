"""Semantic Release Global Variables."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from semantic_release.enums import SemanticReleaseLogLevels

if TYPE_CHECKING:
    from logging import Logger

# GLOBAL VARIABLES
log_level: SemanticReleaseLogLevels = SemanticReleaseLogLevels.WARNING
"""int: Logging level for semantic-release"""

logger: Logger = getLogger(__package__)
"""Logger for semantic-release"""
