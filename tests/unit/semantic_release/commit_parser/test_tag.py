import pytest

from semantic_release.commit_parser.tag import TagCommitParser
from semantic_release.commit_parser.token import ParseError
from semantic_release.enums import LevelBump

from tests.unit.semantic_release.commit_parser.helper import make_commit


@pytest.fixture
def default_options():
    yield TagCommitParser.parser_options()


@pytest.fixture
def default_tag_parser(default_options):
    yield TagCommitParser(default_options)


text = (
    "This is an long explanatory part of a commit message. It should give "
    "some insight to the fix this commit adds to the codebase."
)
footer = "Closes #400"


def test_parser_raises_unknown_message_style(default_tag_parser):
    result = default_tag_parser.parse(make_commit(""))
    assert isinstance(result, ParseError)


@pytest.mark.parametrize(
    "commit_message, bump, type_, descriptions",
    [
        (
            ":sparkles: Add new parser pattern\n\nBREAKING CHANGE:",
            LevelBump.MAJOR,
            "breaking",
            ["Add new parser pattern", "BREAKING CHANGE:"],
        ),
        (
            ":sparkles: Add emoji parser",
            LevelBump.MINOR,
            "feature",
            ["Add emoji parser"],
        ),
        (
            ":nut_and_bolt: Fix regex in angular parser\n\n{text}".format(text=text),
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser", text],
        ),
        (
            ":nut_and_bolt: Fix regex in angular parser",
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser"],
        ),
        (
            ":nut_and_bolt: Fix regex in angular parser\n\n{text}\n\n{footer}".format(
                text=text, footer=footer
            ),
            LevelBump.PATCH,
            "fix",
            ["Fix regex in angular parser", text, footer],
        ),
    ],
)
def test_default_tag_parser(
    default_tag_parser, commit_message, bump, type_, descriptions
):
    commit = make_commit(commit_message)
    parsed = default_tag_parser.parse(commit)
    assert parsed.bump is bump
    assert parsed.type == type_
    assert parsed.descriptions == descriptions
