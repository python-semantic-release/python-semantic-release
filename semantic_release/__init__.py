"""Python Semantic Release
"""
from __future__ import annotations

from semantic_release.errors import (
    CommitParseError as CommitParseError,
    InvalidConfiguration as InvalidConfiguration,
    SemanticReleaseBaseError as SemanticReleaseBaseError,
)

__version__ = "8.0.0-alpha.1"


def setup_hook(argv: list[str]) -> None:
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and any(
        cmd in argv for cmd in ["version", "publish", "changelog"]
    ):
        from .cli import main

        main()
