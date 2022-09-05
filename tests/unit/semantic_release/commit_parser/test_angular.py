import pytest

from semantic_release.enums import LevelBump
from semantic_release.errors import UnknownCommitMessageStyleError
from semantic_release.commit_parser.angular import AngularCommitParser

from tests.unit.semantic_release.commit_parser.helper import make_commit


@pytest.fixture
def default_options():
    yield AngularCommitParser.parser_options()


@pytest.fixture
def default_angular_parser(default_options):
    yield AngularCommitParser(default_options)


def test_parser_raises_unknown_message_style(default_angular_parser):
    with pytest.raises(UnknownCommitMessageStyleError):
        default_angular_parser.parse(make_commit(""))

    with pytest.raises(UnknownCommitMessageStyleError):
        default_angular_parser.parse(
            make_commit("feat(parser\n): Add new parser pattern")
        )


@pytest.mark.parametrize(
    "commit_message, bump",
    [
        ("feat(parsers): Add new parser pattern\n\nBREAKING CHANGE: ", LevelBump.MAJOR),
        ("feat(parsers)!: Add new parser pattern", LevelBump.MAJOR),
        (
            "feat(parsers): Add new parser pattern\n\nNew pattern is awesome\n\nBREAKING CHANGE: \n",
            LevelBump.MAJOR,
        ),
        (
            "feat(parsers): Add new parser pattern\n\nBREAKING-CHANGE: change !",
            LevelBump.MAJOR,
        ),
        ("feat(parser): Add emoji parser", LevelBump.MINOR),
        ("fix(parser): Fix regex in angular parser", LevelBump.PATCH),
        ("test(parser): Add a test for angular parser", LevelBump.NO_RELEASE),
        ("feat(parser)!: Edit dat parsing stuff", LevelBump.MAJOR),
        ("fix!: Edit dat parsing stuff again", LevelBump.MAJOR),
        ("fix: superfix", LevelBump.PATCH),
    ],
)
def test_parser_returns_correct_bump_level(
    default_angular_parser, commit_message, bump
):
    assert default_angular_parser.parse(make_commit(commit_message)).bump is bump


@pytest.mark.parametrize(
    "message, type_",
    [
        ("feat(parser): ...", "feature"),
        ("fix(parser): ...", "fix"),
        ("test(parser): ...", "test"),
        ("docs(parser): ...", "documentation"),
        ("style(parser): ...", "style"),
        ("refactor(parser): ...", "refactor"),
        ("chore(parser): ...", "chore"),
    ],
)
def test_parser_return_type_from_commit_message(default_angular_parser, message, type_):
    assert default_angular_parser.parse(make_commit(message)).type == type_


@pytest.mark.parametrize(
    "message, scope",
    [
        ("chore(parser): ...", "parser"),
        ("chore(a part): ...", "a part"),
        ("chore(a_part): ...", "a_part"),
        ("chore(a-part): ...", "a-part"),
        ("chore(a.part): ...", "a.part"),
        ("chore(a+part): ...", "a+part"),
        ("chore(a&part): ...", "a&part"),
        ("chore((part)): ...", "(part)"),
        ("chore((p):rt): ...", "(p):rt"),
    ],
)
def test_parser_return_scope_from_commit_message(
    default_angular_parser, message, scope
):
    assert default_angular_parser.parse(make_commit(message)).scope == scope


_long_text = (
    "This is an long explanatory part of a commit message. It should give "
    "some insight to the fix this commit adds to the codebase."
)
_footer = "Closes #400"


@pytest.mark.parametrize(
    "message, descriptions",
    [
        ("feat(parser): Add emoji parser", ["Add emoji parser"]),
        ("fix(parser): Fix regex in angular parser", ["Fix regex in angular parser"]),
        (
            "test(parser): Add a test for angular parser",
            ["Add a test for angular parser"],
        ),
        (
            "fix(tox): Fix env \n\n{text}\n\n{footer}".format(
                text=_long_text, footer=_footer
            ),
            ["Fix env ", _long_text, _footer],
        ),
        ("fix: superfix", ["superfix"]),
    ],
)
def test_parser_return_subject_from_commit_message(
    default_angular_parser, message, descriptions
):
    assert (
        default_angular_parser.parse(make_commit(message)).descriptions == descriptions
    )


##############################
# test custom parser options #
##############################
def test_parser_custom_default_level():
    options = AngularCommitParser.parser_options(default_bump_level=LevelBump.MINOR)
    parser = AngularCommitParser(options)
    assert (
        parser.parse(make_commit("test(parser): Add a test for angular parser")).bump
        is LevelBump.MINOR
    )


def test_parser_custom_allowed_types():
    options = AngularCommitParser.parser_options(
        allowed_tags=(
            "custom",
            "build",
            "chore",
            "ci",
            "docs",
            "fix",
            "perf",
            "style",
            "refactor",
            "test",
        )
    )
    parser = AngularCommitParser(options)
    assert parser.parse(make_commit("custom: ...")).bump is LevelBump.NO_RELEASE
    assert parser.parse(make_commit("custom(parser): ...")).type == "custom"
    with pytest.raises(UnknownCommitMessageStyleError):
        parser.parse(make_commit("feat(parser): ..."))


def test_parser_custom_minor_tags():
    options = AngularCommitParser.parser_options(minor_tags=("docs",))
    parser = AngularCommitParser(options)
    assert parser.parse(make_commit("docs: write some docs")).bump is LevelBump.MINOR


def test_parser_custom_patch_tags():
    options = AngularCommitParser.parser_options(patch_tags=("test",))
    parser = AngularCommitParser(options)
    assert parser.parse(make_commit("test(this): added a test")).bump is LevelBump.PATCH
