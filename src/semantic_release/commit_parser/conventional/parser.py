from __future__ import annotations

from semantic_release.commit_parser.angular import AngularCommitParser
from .options import ConventionalCommitParserOptions


class ConventionalCommitParser(AngularCommitParser):
    """
    A commit parser for projects conforming to the conventional commits specification.

    See https://www.conventionalcommits.org/en/v1.0.0/
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = ConventionalCommitParserOptions

    def __init__(self, options: ConventionalCommitParserOptions | None = None) -> None:
        super().__init__(options)

    @staticmethod
    def get_default_options() -> ConventionalCommitParserOptions:
        return ConventionalCommitParserOptions()
