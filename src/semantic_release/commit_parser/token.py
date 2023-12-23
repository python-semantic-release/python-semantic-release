from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, NoReturn, TypeVar, Union

from semantic_release.errors import CommitParseError

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit

    from semantic_release.enums import LevelBump


class ParsedMessageResult(NamedTuple):
    bump: LevelBump
    type: str
    category: str
    scope: str
    descriptions: tuple[str, ...]
    breaking_descriptions: tuple[str, ...] = ()
    linked_merge_request: str = ""
    include_in_changelog: bool = True


class ParsedCommit(NamedTuple):
    bump: LevelBump
    type: str
    scope: str
    descriptions: list[str]
    breaking_descriptions: list[str]
    commit: Commit
    linked_merge_request: str = ""
    include_in_changelog: bool = True

    @property
    def message(self) -> str:
        m = self.commit.message
        message_str = m.decode("utf-8") if isinstance(m, bytes) else m
        return message_str.replace("\r", "")

    @property
    def hexsha(self) -> str:
        return self.commit.hexsha

    @property
    def short_hash(self) -> str:
        return self.commit.hexsha[:7]

    @property
    def linked_pull_request(self) -> str:
        return self.linked_merge_request

    @staticmethod
    def from_parsed_message_result(
        commit: Commit, parsed_message_result: ParsedMessageResult
    ) -> ParsedCommit:
        return ParsedCommit(
            bump=parsed_message_result.bump,
            # TODO: breaking v10, swap back to type rather than category
            type=parsed_message_result.category,
            scope=parsed_message_result.scope,
            descriptions=list(parsed_message_result.descriptions),
            breaking_descriptions=list(parsed_message_result.breaking_descriptions),
            commit=commit,
            linked_merge_request=parsed_message_result.linked_merge_request,
            include_in_changelog=parsed_message_result.include_in_changelog,
        )


class ParseError(NamedTuple):
    commit: Commit
    error: str

    @property
    def message(self) -> str:
        m = self.commit.message
        message_str = m.decode("utf-8") if isinstance(m, bytes) else m
        return message_str.replace("\r", "")

    @property
    def hexsha(self) -> str:
        return self.commit.hexsha

    @property
    def short_hash(self) -> str:
        return self.commit.hexsha[:7]

    def raise_error(self) -> NoReturn:
        raise CommitParseError(self.error)


_T = TypeVar("_T", bound=ParsedCommit)
_E = TypeVar("_E", bound=ParseError)

# For extensions, this type can be used to build an alias
# for example CustomParseResult = ParseResultType[CustomParsedCommit, ParseError]
ParseResultType = Union[_T, _E]
ParseResult = ParseResultType[ParsedCommit, ParseError]
