from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic

from git import Commit

from semantic_release.commit_parser.token import ParseResult


class ParserOptions:
    """
    ParserOptions should accept the keyword arguments they are interested in
    from configuration and process them as desired, ultimately creating attributes
    on an instance which can be accessed by the corresponding commit parser. For example,
    >>> class MyParserOptions(BaseParserOptions):
            def __init__(self, message_prefix: str) -> None:
                self.prefix = message_prefix * 2

    >>> class MyCommitParser(AbstractCommitParser
            parser_options = MyParserOptions
            def parse(self, Commit):
                print(self.options.prefix)
                ...

    Any defaults that need to be set should also be done in this class too.
    Invalid options should be signalled by raising an ``InvalidOptionsException``
    within the ``__init__`` method of the options class.
    """

    def __init__(self, **_):
        pass


# TT = TokenType, a subclass of ParsedCommit
_TT = TypeVar("_TT", bound=ParseResult)


class CommitParser(ABC, Generic[_TT]):
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

    parser_options: Type[ParserOptions]

    def __init__(self, options: ParserOptions) -> None:
        self.options = options

    @abstractmethod
    def parse(self, commit: Commit) -> _TT:
        ...
