import pytest

from semantic_release.commit_parser import (
    AngularCommitParser,
    AngularParserOptions,
    EmojiCommitParser,
    EmojiParserOptions,
    TagCommitParser,
    TagParserOptions,
)

# Note scipy defined in ./scipy.py as already used there


@pytest.fixture(scope="session")
def default_angular_parser() -> AngularCommitParser:
    return AngularCommitParser()


@pytest.fixture(scope="session")
def default_angular_parser_options(
    default_angular_parser: AngularCommitParser,
) -> AngularParserOptions:
    return default_angular_parser.get_default_options()


@pytest.fixture(scope="session")
def default_emoji_parser() -> EmojiCommitParser:
    return EmojiCommitParser()


@pytest.fixture(scope="session")
def default_emoji_parser_options(
    default_emoji_parser: EmojiCommitParser,
) -> EmojiParserOptions:
    return default_emoji_parser.get_default_options()


@pytest.fixture(scope="session")
def default_tag_parser() -> TagCommitParser:
    return TagCommitParser()


@pytest.fixture(scope="session")
def default_tag_parser_options(default_tag_parser: TagCommitParser) -> TagParserOptions:
    return default_tag_parser.get_default_options()
