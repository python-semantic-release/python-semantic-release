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


def test_parser_returns_correct_bump_level(default_angular_parser):
    assert (
        default_angular_parser.parse(
            make_commit("feat(parsers): Add new parser pattern\n\nBREAKING CHANGE: ")
        ).bump
        is LevelBump.MAJOR
    )
    assert (
        default_angular_parser.parse(
            make_commit("feat(parsers)!: Add new parser pattern")
        ).bump
        is LevelBump.MAJOR
    )
    assert (
        default_angular_parser.parse(
            make_commit(
                "feat(parsers): Add new parser pattern\n\n"
                "New pattern is awesome\n\nBREAKING CHANGE: \n"
            )
        ).bump
        is LevelBump.MAJOR
    )
    assert (
        default_angular_parser.parse(
            make_commit(
                "feat(parsers): Add new parser pattern\n\nBREAKING-CHANGE: change !"
            )
        ).bump
        is LevelBump.MAJOR
    )
    assert (
        default_angular_parser.parse(make_commit("feat(parser): Add emoji parser")).bump
        is LevelBump.MINOR
    )
    assert (
        default_angular_parser.parse(
            make_commit("fix(parser): Fix regex in angular parser")
        ).bump
        is LevelBump.PATCH
    )
    assert (
        default_angular_parser.parse(
            make_commit("test(parser): Add a test for angular parser")
        ).bump
        is LevelBump.NO_RELEASE
    )
    assert (
        default_angular_parser.parse(
            make_commit("feat(parser)!: Edit dat parsing stuff")
        ).bump
        is LevelBump.MAJOR
    )
    assert (
        default_angular_parser.parse(make_commit("fix!: Edit dat parsing stuff again")).bump
        is LevelBump.MAJOR
    )


def test_parser_return_type_from_commit_message(default_angular_parser):
    assert (
        default_angular_parser.parse(make_commit("feat(parser): ...")).type == "feature"
    )
    assert default_angular_parser.parse(make_commit("fix(parser): ...")).type == "fix"
    assert default_angular_parser.parse(make_commit("test(parser): ...")).type == "test"
    assert (
        default_angular_parser.parse(make_commit("docs(parser): ...")).type
        == "documentation"
    )
    assert (
        default_angular_parser.parse(make_commit("style(parser): ...")).type == "style"
    )
    assert (
        default_angular_parser.parse(make_commit("refactor(parser): ...")).type
        == "refactor"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(parser): ...")).type == "chore"
    )


def test_parser_return_scope_from_commit_message(default_angular_parser):
    assert (
        default_angular_parser.parse(make_commit("chore(parser): ...")).scope
        == "parser"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a part): ...")).scope
        == "a part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a_part): ...")).scope
        == "a_part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a-part): ...")).scope
        == "a-part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a.part): ...")).scope
        == "a.part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a+part): ...")).scope
        == "a+part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore(a&part): ...")).scope
        == "a&part"
    )
    assert (
        default_angular_parser.parse(make_commit("chore((part)): ...")).scope
        == "(part)"
    )
    assert (
        default_angular_parser.parse(make_commit("chore((p):rt): ...")).scope
        == "(p):rt"
    )


def test_parser_return_subject_from_commit_message(default_angular_parser):
    assert (
        default_angular_parser.parse(
            make_commit("feat(parser): Add emoji parser")
        ).descriptions[0]
        == "Add emoji parser"
    )
    assert (
        default_angular_parser.parse(
            make_commit("fix(parser): Fix regex in angular parser")
        ).descriptions[0]
        == "Fix regex in angular parser"
    )
    assert (
        default_angular_parser.parse(
            make_commit("test(parser): Add a test for angular parser")
        ).descriptions[0]
        == "Add a test for angular parser"
    )


def test_parser_return_footer_from_commit_message(default_angular_parser):
    text = (
        "This is an long explanatory part of a commit message. It should give "
        "some insight to the fix this commit adds to the codebase."
    )
    footer = "Closes #400"
    commit = make_commit(
        "fix(tox): Fix env \n\n{text}\n\n{footer}".format_map(locals())
    )
    assert default_angular_parser.parse(commit).descriptions[1] == text
    assert default_angular_parser.parse(commit).descriptions[2] == footer


def test_parser_should_accept_message_without_scope(default_angular_parser):
    assert (
        default_angular_parser.parse(make_commit("fix: superfix")).bump
        is LevelBump.PATCH
    )
    assert (
        default_angular_parser.parse(make_commit("fix: superfix")).descriptions[0]
        == "superfix"
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
