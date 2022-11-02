"""Semantic Release
"""
__version__ = "7.32.2"

from typing import List

from semantic_release.errors import (
    InvalidConfiguration as InvalidConfiguration,
    SemanticReleaseBaseError as SemanticReleaseBaseError,
    CommitParseError as CommitParseError,
)


def setup_hook(argv: List[str]) -> None:
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and any(
        cmd in argv for cmd in ["version", "publish", "changelog"]
    ):
        from .cli import main

        main()
