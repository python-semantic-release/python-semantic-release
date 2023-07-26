"""Python Semantic Release
"""
from __future__ import annotations

from semantic_release.commit_parser import (
    CommitParser as CommitParser,
    ParsedCommit as ParsedCommit,
    ParseError as ParseError,
    ParseResult as ParseResult,
    ParseResultType as ParseResultType,
    ParserOptions as ParserOptions,
)
from semantic_release.enums import LevelBump as LevelBump
from semantic_release.errors import (
    CommitParseError as CommitParseError,
    InvalidConfiguration as InvalidConfiguration,
    InvalidVersion as InvalidVersion,
    SemanticReleaseBaseError as SemanticReleaseBaseError,
)
from semantic_release.version import (
    Version as Version,
    VersionTranslator as VersionTranslator,
    next_version as next_version,
    tags_and_versions as tags_and_versions,
)

__version__ = "8.0.4"


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
