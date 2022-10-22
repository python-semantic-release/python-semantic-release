from typing import List, NamedTuple, TypeVar, Union

from git import Commit

from semantic_release.enums import LevelBump
from semantic_release.errors import CommitParseError


class ParsedCommit(NamedTuple):
    bump: LevelBump
    type: str
    scope: str
    descriptions: List[str]
    breaking_descriptions: List[str]
    commit: Commit


class ParseError(NamedTuple):
    commit: Commit
    error: str

    def raise_error(self):
        raise CommitParseError(self.error)


_T = TypeVar("_T", bound=ParsedCommit)
_E = TypeVar("_E", bound=ParseError)

ParseResult = Union[_T, _E]
