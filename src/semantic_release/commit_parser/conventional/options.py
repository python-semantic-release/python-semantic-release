from __future__ import annotations

from pydantic.dataclasses import dataclass

from semantic_release.commit_parser.angular import AngularParserOptions


@dataclass
class ConventionalCommitParserOptions(AngularParserOptions):
    """Options dataclass for the ConventionalCommitParser."""
