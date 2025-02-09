import pytest

from semantic_release.commit_parser import (
    ConventionalCommitParser,
    ConventionalCommitParserOptions,
    EmojiCommitParser,
    EmojiParserOptions,
)

from tests.const import (
    CONVENTIONAL_COMMITS_CHORE,
    CONVENTIONAL_COMMITS_MAJOR,
    CONVENTIONAL_COMMITS_MINOR,
    CONVENTIONAL_COMMITS_PATCH,
    EMOJI_COMMITS_CHORE,
    EMOJI_COMMITS_MAJOR,
    EMOJI_COMMITS_MINOR,
    EMOJI_COMMITS_PATCH,
)

# Note scipy defined in ./scipy.py as already used there


@pytest.fixture(scope="session")
def default_conventional_parser() -> ConventionalCommitParser:
    return ConventionalCommitParser()


@pytest.fixture(scope="session")
def default_conventional_parser_options(
    default_conventional_parser: ConventionalCommitParser,
) -> ConventionalCommitParserOptions:
    return default_conventional_parser.get_default_options()


@pytest.fixture(scope="session")
def default_emoji_parser() -> EmojiCommitParser:
    return EmojiCommitParser()


@pytest.fixture(scope="session")
def default_emoji_parser_options(
    default_emoji_parser: EmojiCommitParser,
) -> EmojiParserOptions:
    return default_emoji_parser.get_default_options()


@pytest.fixture(scope="session")
def conventional_major_commits():
    return CONVENTIONAL_COMMITS_MAJOR


@pytest.fixture(scope="session")
def conventional_minor_commits():
    return CONVENTIONAL_COMMITS_MINOR


@pytest.fixture(scope="session")
def conventional_patch_commits():
    return CONVENTIONAL_COMMITS_PATCH


@pytest.fixture(scope="session")
def conventional_chore_commits():
    return CONVENTIONAL_COMMITS_CHORE


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
