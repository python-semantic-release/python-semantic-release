"""Python Semantic Release"""

from __future__ import annotations

from semantic_release.commit_parser import (
    CommitParser,
    ParsedCommit,
    ParseError,
    ParseResult,
    ParseResultType,
    ParserOptions,
)
from semantic_release.enums import LevelBump
from semantic_release.errors import (
    CommitParseError,
    InvalidConfiguration,
    InvalidVersion,
    SemanticReleaseBaseError,
)
from semantic_release.version import (
    Version,
    VersionTranslator,
    next_version,
    tags_and_versions,
)

__version__ = "9.8.0"


def setup_hook(argv: list[str]) -> None:
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and any(
        cmd in argv for cmd in ["version", "publish", "changelog"]
    ):
        from semantic_release.cli import main

        main()
