import pytest

from semantic_release.commit_parser import (
    AngularCommitParser,
    AngularParserOptions,
    EmojiCommitParser,
    EmojiParserOptions,
)

from tests.const import (
    ANGULAR_COMMITS_CHORE,
    ANGULAR_COMMITS_MAJOR,
    ANGULAR_COMMITS_MINOR,
    ANGULAR_COMMITS_PATCH,
    EMOJI_COMMITS_CHORE,
    EMOJI_COMMITS_MAJOR,
    EMOJI_COMMITS_MINOR,
    EMOJI_COMMITS_PATCH,
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
def angular_major_commits():
    return ANGULAR_COMMITS_MAJOR


@pytest.fixture(scope="session")
def angular_minor_commits():
    return ANGULAR_COMMITS_MINOR


@pytest.fixture(scope="session")
def angular_patch_commits():
    return ANGULAR_COMMITS_PATCH


@pytest.fixture(scope="session")
def angular_chore_commits():
    return ANGULAR_COMMITS_CHORE


@pytest.fixture(scope="session")
def emoji_major_commits():
    return EMOJI_COMMITS_MAJOR


@pytest.fixture(scope="session")
def emoji_minor_commits():
    return EMOJI_COMMITS_MINOR


@pytest.fixture(scope="session")
def emoji_patch_commits():
    return EMOJI_COMMITS_PATCH


@pytest.fixture(scope="session")
def emoji_chore_commits():
    return EMOJI_COMMITS_CHORE
