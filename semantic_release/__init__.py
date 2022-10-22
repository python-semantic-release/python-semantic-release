"""Semantic Release
"""
__version__ = "7.32.1"

from typing import List

from semantic_release.errors import (
    ImproperConfigurationError,
    SemanticReleaseBaseError,
    UnknownCommitMessageStyleError,
)


def setup_hook(argv: List[str]):
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and any(
        cmd in argv for cmd in ["version", "publish", "changelog"]
    ):
        from .cli import main

        main()
