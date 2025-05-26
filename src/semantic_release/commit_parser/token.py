from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, NoReturn, TypeVar, Union

from semantic_release.commit_parser.util import force_str
from semantic_release.errors import CommitParseError

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit

    from semantic_release.enums import LevelBump


class ParsedMessageResult(NamedTuple):
    """
    A read-only named tuple object representing the result from parsing a commit message.

    Essentially this is a data structure which holds the parsed information from a commit message
    without the actual commit object itself. Very helpful for unit testing.

    Most of the fields will replicate the fields of a
    :py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`
    """

    bump: LevelBump
    type: str
    category: str
    scope: str
    descriptions: tuple[str, ...]
    breaking_descriptions: tuple[str, ...] = ()
    release_notices: tuple[str, ...] = ()
    linked_issues: tuple[str, ...] = ()
    linked_merge_request: str = ""
    include_in_changelog: bool = True


class ParsedCommit(NamedTuple):
    """A read-only named tuple object representing the result of parsing a commit message."""

    bump: LevelBump
    """A LevelBump enum value indicating what type of change this commit introduces."""

    type: str
    """
    The type of the commit as a string, per the commit message style.

    This is up to the parser to implement; for example, the EmojiCommitParser
    parser fills this field with the emoji representing the most significant change for
    the commit.
    """

    scope: str
    """
    The scope, as a string, parsed from the commit.

    Generally an optional field based on the commit message style which means it very likely can be an empty string.
    Commit styles which do not have a meaningful concept of "scope" usually fill this field with an empty string.
    """

    descriptions: list[str]
    """
    A list of paragraphs from the commit message.

    Paragraphs are generally delimited by a double-newline since git commit messages are sometimes manually wordwrapped with
    a single newline, but this is up to the parser to implement.
    """

    breaking_descriptions: list[str]
    """
    A list of paragraphs which are deemed to identify and describe breaking changes by the parser.

    An example would be a paragraph which begins with the text ``BREAKING CHANGE:`` in the commit message but
    the parser gennerally strips the prefix and includes the rest of the paragraph in this list.
    """

    commit: Commit
    """The original commit object (a class defined by GitPython) that was parsed"""

    release_notices: tuple[str, ...] = ()
    """
    A tuple of release notices, which are additional information about the changes that affect the user.

    An example would be a paragraph which begins with the text ``NOTICE:`` in the commit message but
    the parser generally strips the prefix and includes the rest of the paragraph in this list.
    """

    linked_issues: tuple[str, ...] = ()
    """
    A tuple of issue numbers as strings, if the commit is contains issue references.

    If there are no issue references, this should be an empty tuple. Although, we generally
    refer to them as "issue numbers", it generally should be a string to adhere to the prefixes
    used by the VCS (ex. ``#`` for GitHub, GitLab, etc.) or issue tracker (ex. JIRA uses ``AAA-###``).
    """

    linked_merge_request: str = ""
    """
    A pull request or merge request definition, if the commit is labeled with a pull/merge request number.

    This is a string value which includes any special character prefix used by the VCS
    (e.g. ``#`` for GitHub, ``!`` for GitLab).
    """

    include_in_changelog: bool = True
    """
    A boolean value indicating whether this commit should be included in the changelog.

    This enables parsers to flag commits which are not user-facing or are otherwise not
    relevant to the changelog to be filtered out by PSR's internal algorithms.
    """

    @property
    def message(self) -> str:
        """
        A string representation of the commit message.

        This is a pass through property for convience to access the ``message``
        attribute of the ``commit`` object.

        If the message is of type ``bytes`` then it will be decoded to a ``UTF-8`` string.
        """
        return force_str(self.commit.message).replace("\r", "")

    @property
    def hexsha(self) -> str:
        """
        A hex representation of the hash value of the commit.

        This is a pass through property for convience to access the ``hexsha`` attribute of the ``commit``.
        """
        return self.commit.hexsha

    @property
    def short_hash(self) -> str:
        """A short representation of the hash value (in hex) of the commit."""
        return self.hexsha[:7]

    @property
    def linked_pull_request(self) -> str:
        """An alias to the linked_merge_request attribute."""
        return self.linked_merge_request

    def is_merge_commit(self) -> bool:
        return bool(len(self.commit.parents) > 1)

    @staticmethod
    def from_parsed_message_result(
        commit: Commit, parsed_message_result: ParsedMessageResult
    ) -> ParsedCommit:
        """A convience method to create a ParsedCommit object from a ParsedMessageResult object and a Commit object."""
        return ParsedCommit(
            bump=parsed_message_result.bump,
            # TODO: breaking v11, swap back to type rather than category
            type=parsed_message_result.category,
            scope=parsed_message_result.scope,
            descriptions=list(parsed_message_result.descriptions),
            breaking_descriptions=list(parsed_message_result.breaking_descriptions),
            commit=commit,
            release_notices=parsed_message_result.release_notices,
            linked_issues=parsed_message_result.linked_issues,
            linked_merge_request=parsed_message_result.linked_merge_request,
            include_in_changelog=parsed_message_result.include_in_changelog,
        )


class ParseError(NamedTuple):
    """A read-only named tuple object representing an error that occurred while parsing a commit message."""

    commit: Commit
    """The original commit object (a class defined by GitPython) that was parsed"""

    error: str
    """A string with a description for why the commit parsing failed."""

    @property
    def message(self) -> str:
        """
        A string representation of the commit message.

        This is a pass through property for convience to access the ``message``
        attribute of the ``commit`` object.

        If the message is of type ``bytes`` then it will be decoded to a ``UTF-8`` string.
        """
        return force_str(self.commit.message).replace("\r", "")

    @property
    def hexsha(self) -> str:
        """
        A hex representation of the hash value of the commit.

        This is a pass through property for convience to access the ``hexsha`` attribute of the ``commit``.
        """
        return self.commit.hexsha

    @property
    def short_hash(self) -> str:
        """A short representation of the hash value (in hex) of the commit."""
        return self.hexsha[:7]

    def is_merge_commit(self) -> bool:
        return bool(len(self.commit.parents) > 1)

    def raise_error(self) -> NoReturn:
        """A convience method to raise a CommitParseError with the error message."""
        raise CommitParseError(self.error)


_T = TypeVar("_T", bound=ParsedCommit)
_E = TypeVar("_E", bound=ParseError)

# For extensions, this type can be used to build an alias
# for example CustomParseResult = ParseResultType[CustomParsedCommit, ParseError]
ParseResultType = Union[_T, _E]
ParseResult = ParseResultType[ParsedCommit, ParseError]
