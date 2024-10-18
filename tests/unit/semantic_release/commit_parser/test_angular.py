from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from semantic_release.commit_parser.angular import (
    AngularCommitParser,
    AngularParserOptions,
)
from semantic_release.commit_parser.token import ParsedCommit, ParseError
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from tests.conftest import MakeCommitObjFn


def test_parser_raises_unknown_message_style(
    default_angular_parser: AngularCommitParser, make_commit_obj: MakeCommitObjFn
):
    assert isinstance(default_angular_parser.parse(make_commit_obj("")), ParseError)
    assert isinstance(
        default_angular_parser.parse(
            make_commit_obj("feat(parser\n): Add new parser pattern")
        ),
        ParseError,
    )


@pytest.mark.parametrize(
    "commit_message, bump",
    [
        ("feat(parsers): Add new parser pattern\n\nBREAKING CHANGE: ", LevelBump.MAJOR),
        ("feat(parsers)!: Add new parser pattern", LevelBump.MAJOR),
        (
            "feat(parsers): Add new parser pattern\n\nNew pattern is awesome\n\n"
            "BREAKING CHANGE: \n",
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
    default_angular_parser: AngularCommitParser,
    commit_message: str,
    bump: LevelBump,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(commit_message))
    assert isinstance(result, ParsedCommit)
    assert result.bump is bump


@pytest.mark.parametrize(
    "message, type_",
    [
        ("feat(parser): ...", "features"),
        ("fix(parser): ...", "bug fixes"),
        ("test(parser): ...", "testing"),
        ("docs(parser): ...", "documentation"),
        ("style(parser): ...", "code style"),
        ("refactor(parser): ...", "refactoring"),
        ("chore(parser): ...", "chores"),
    ],
)
def test_parser_return_type_from_commit_message(
    default_angular_parser: AngularCommitParser,
    message: str,
    type_: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert result.type == type_


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
    default_angular_parser: AngularCommitParser,
    message: str,
    scope: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert result.scope == scope


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
            f"fix(tox): Fix env \n\n{_long_text}\n\n{_footer}",
            ["Fix env ", _long_text, _footer],
        ),
        ("fix: superfix", ["superfix"]),
    ],
)
def test_parser_return_subject_from_commit_message(
    default_angular_parser: AngularCommitParser,
    message: str,
    descriptions: list[str],
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert result.descriptions == descriptions


##############################
# test custom parser options #
##############################
def test_parser_custom_default_level(make_commit_obj: MakeCommitObjFn):
    options = AngularParserOptions(default_bump_level=LevelBump.MINOR)
    parser = AngularCommitParser(options)
    result = parser.parse(
        make_commit_obj("test(parser): Add a test for angular parser")
    )
    assert isinstance(result, ParsedCommit)
    assert result.bump is LevelBump.MINOR


def test_parser_custom_allowed_types(make_commit_obj: MakeCommitObjFn):
    options = AngularParserOptions(
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

    res1 = parser.parse(make_commit_obj("custom: ..."))
    assert isinstance(res1, ParsedCommit)
    assert res1.bump is LevelBump.NO_RELEASE

    res2 = parser.parse(make_commit_obj("custom(parser): ..."))
    assert isinstance(res2, ParsedCommit)
    assert res2.type == "custom"

    assert isinstance(parser.parse(make_commit_obj("feat(parser): ...")), ParseError)


def test_parser_custom_minor_tags(make_commit_obj: MakeCommitObjFn):
    options = AngularParserOptions(minor_tags=("docs",))
    parser = AngularCommitParser(options)
    res = parser.parse(make_commit_obj("docs: write some docs"))
    assert isinstance(res, ParsedCommit)
    assert res.bump is LevelBump.MINOR


def test_parser_custom_patch_tags(make_commit_obj: MakeCommitObjFn):
    options = AngularParserOptions(patch_tags=("test",))
    parser = AngularCommitParser(options)
    res = parser.parse(make_commit_obj("test(this): added a test"))
    assert isinstance(res, ParsedCommit)
    assert res.bump is LevelBump.PATCH
