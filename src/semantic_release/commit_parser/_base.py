from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from semantic_release.commit_parser.token import ParseResultType

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit


class ParserOptions(dict):
    """
    ParserOptions should accept the keyword arguments they are interested in
    from configuration and process them as desired, ultimately creating attributes
    on an instance which can be accessed by the corresponding commit parser.

    For example:
    >>> class MyParserOptions(ParserOptions):
    ...     def __init__(self, message_prefix: str) -> None:
    ...         self.prefix = message_prefix * 2

    >>> class MyCommitParser(AbstractCommitParser):
    ...     parser_options = MyParserOptions
    ...
    ...     def parse(self, Commit):
    ...         print(self.options.prefix)
    ...         ...

    Any defaults that need to be set should also be done in this class too.
    Invalid options should be signalled by raising an ``InvalidOptionsException``
    within the ``__init__`` method of the options class.

    A dataclass is also well suited to this; if type-checking of input is desired,
    a ``pydantic.dataclasses.dataclass`` works well and is used internally
    by python-semantic-release. Parser options are not validated in the configuration
    and passed directly to the appropriate class to handle.
    """

    def __init__(self, **_: Any) -> None:
        pass


# TT = TokenType, a subclass of ParsedCommit
_TT = TypeVar("_TT", bound=ParseResultType)
_OPTS = TypeVar("_OPTS", bound=ParserOptions)


class CommitParser(ABC, Generic[_TT, _OPTS]):
    """
    Abstract base class for all commit parsers. Custom commit parsers should inherit
    from this class.

    A class-level ``parser_options`` attribute should be set to a subclass of
    ``BaseParserOptions``; this will be used to provide the default options to the
    parser. Note that a nested class can be used directly, if preferred:

    >>> class MyParser(CommitParser):
            @dataclass
            class parser_options(ParserOptions):
                allowed_types: Tuple[str] = ("feat", "fix", "docs")
                major_types: Tuple[str] = ("breaking",)
                minor_types: Tuple[str] = ("fix", "patch")
                ...
            def __init__(self, options: parser_options) -> None:
                ...
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options: type[ParserOptions] = ParserOptions

    def __init__(self, options: _OPTS | None = None) -> None:
        self.options: _OPTS = (
            options if options is not None else self.get_default_options()
        )

    # TODO: BREAKING CHANGE v11, add abstract method for all custom parsers
    # @staticmethod
    # @abstractmethod
    def get_default_options(self) -> _OPTS:
        return self.parser_options()  # type: ignore[return-value]

    @abstractmethod
    def parse(self, commit: Commit) -> _TT | list[_TT]: ...
