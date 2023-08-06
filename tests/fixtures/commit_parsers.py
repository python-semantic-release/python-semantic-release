import pytest

from semantic_release.commit_parser import (
    AngularCommitParser,
    EmojiCommitParser,
    TagCommitParser,
)

# Note scipy defined in ./scipy.py as already used there


@pytest.fixture
def default_angular_parser_options():
    return AngularCommitParser.parser_options()


@pytest.fixture
def default_angular_parser(default_angular_parser_options):
    return AngularCommitParser(options=default_angular_parser_options)


@pytest.fixture
def default_emoji_parser_options():
    return EmojiCommitParser.parser_options()


@pytest.fixture
def default_emoji_parser(default_emoji_parser_options):
    return EmojiCommitParser(options=default_emoji_parser_options)


@pytest.fixture
def default_tag_parser_options():
    return TagCommitParser.parser_options()


@pytest.fixture
def default_tag_parser(default_tag_parser_options):
    return TagCommitParser(options=default_tag_parser_options)
