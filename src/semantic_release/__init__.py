"""Python Semantic Release"""

from __future__ import annotations

import importlib.metadata

from semantic_release.changelog.context import ChangelogMode
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.commit_parser import (
    CommitParser,
    ParsedCommit,
    ParseError,
    ParseResult,
    ParseResultType,
    ParserOptions,
)
from semantic_release.context import SemanticReleaseContext
from semantic_release.enums import LevelBump
from semantic_release.errors import (
    CommitParseError,
    DetachedHeadGitError,
    InvalidConfiguration,
    InvalidVersion,
    MissingGitRemote,
    NotAReleaseBranch,
    SemanticReleaseBaseError,
)
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab, HvcsBase
from semantic_release.operations import (
    build_release_history,
    compute_next_version,
    render_changelog,
    render_release_notes,
)
from semantic_release.version import (
    Version,
    VersionTranslator,
    next_version,
    tags_and_versions,
)

__version__ = importlib.metadata.version(f"python_{__package__}".replace("_", "-"))

__all__ = [
    "CommitParser",
    "ParsedCommit",
    "ParseError",
    "ParseResult",
    "ParseResultType",
    "ParserOptions",
    "LevelBump",
    "ChangelogMode",
    "SemanticReleaseBaseError",
    "CommitParseError",
    "DetachedHeadGitError",
    "InvalidConfiguration",
    "InvalidVersion",
    "MissingGitRemote",
    "NotAReleaseBranch",
    "Version",
    "VersionTranslator",
    "next_version",
    "tags_and_versions",
    "SemanticReleaseContext",
    "build_release_history",
    "render_changelog",
    "render_release_notes",
    "compute_next_version",
    "ReleaseHistory",
    "HvcsBase",
    "Github",
    "Gitlab",
    "Gitea",
    "Bitbucket",
]


def setup_hook(argv: list[str]) -> None:
    """
    A hook to be used in setup.py to enable `python setup.py publish`.

    :param argv: sys.argv
    """
    if len(argv) > 1 and any(
        cmd in argv for cmd in ["version", "publish", "changelog"]
    ):
        from semantic_release.cli.commands.main import main

        main()
