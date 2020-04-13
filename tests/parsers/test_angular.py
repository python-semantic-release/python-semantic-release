import pytest

from semantic_release.errors import UnknownCommitMessageStyleError
from semantic_release.history import angular_parser

text = (
    "This is an long explanatory part of a commit message. It should give "
    "some insight to the fix this commit adds to the codebase."
)
footer = "Closes #400"


def test_parser_raises_unknown_message_style():
    pytest.raises(UnknownCommitMessageStyleError, angular_parser, "")
    pytest.raises(
        UnknownCommitMessageStyleError,
        angular_parser,
        "feat(parser\n): Add new parser pattern",
    )


def test_parser_return_correct_bump_level():
    assert (
        angular_parser("feat(parsers): Add new parser pattern\n\nBREAKING CHANGE: ")[0]
        == 3
    )
    assert (
        angular_parser("feat(parsers)!: Add new parser pattern\n\nBREAKING CHANGE: ")[0]
        == 3
    )
    assert (
        angular_parser(
            "feat(parsers): Add new parser pattern\n\n"
            "New pattern is awesome\n\nBREAKING CHANGE: "
        )[0]
        == 3
    )
    assert (
        angular_parser(
            "feat(parsers): Add new parser pattern\n\nBREAKING-CHANGE: change !"
        )[0]
        == 3
    )
    assert angular_parser("feat(parser): Add emoji parser")[0] == 2
    assert angular_parser("fix(parser): Fix regex in angular parser")[0] == 1
    assert angular_parser("test(parser): Add a test for angular parser")[0] == 0
    assert angular_parser("feat(parser)!: Edit dat parsing stuff")[0] == 3
    assert angular_parser("fix!: Edit dat parsing stuff again")[0] == 3


def test_parser_return_type_from_commit_message():
    assert angular_parser("feat(parser): ...")[1] == "feature"
    assert angular_parser("fix(parser): ...")[1] == "fix"
    assert angular_parser("test(parser): ...")[1] == "test"
    assert angular_parser("docs(parser): ...")[1] == "documentation"
    assert angular_parser("style(parser): ...")[1] == "style"
    assert angular_parser("refactor(parser): ...")[1] == "refactor"
    assert angular_parser("chore(parser): ...")[1] == "chore"


def test_parser_return_scope_from_commit_message():
    assert angular_parser("chore(parser): ...")[2] == "parser"
    assert angular_parser("chore(a part): ...")[2] == "a part"
    assert angular_parser("chore(a_part): ...")[2] == "a_part"
    assert angular_parser("chore(a-part): ...")[2] == "a-part"
    assert angular_parser("chore(a.part): ...")[2] == "a.part"
    assert angular_parser("chore(a+part): ...")[2] == "a+part"
    assert angular_parser("chore(a&part): ...")[2] == "a&part"
    assert angular_parser("chore((part)): ...")[2] == "(part)"
    assert angular_parser("chore((p):rt): ...")[2] == "(p):rt"


def test_parser_return_subject_from_commit_message():
    assert angular_parser("feat(parser): Add emoji parser")[3][0] == "Add emoji parser"
    assert (
        angular_parser("fix(parser): Fix regex in angular parser")[3][0]
        == "Fix regex in angular parser"
    )
    assert (
        angular_parser("test(parser): Add a test for angular parser")[3][0]
        == "Add a test for angular parser"
    )


def test_parser_return_text_from_commit_message():
    assert (
        angular_parser("fix(parser): Fix regex in an parser\n\n{}".format(text))[3][1]
        == text
    )


def test_parser_return_footer_from_commit_message():
    commit = "fix(tox): Fix env \n\n{t[text]}\n\n{t[footer]}".format(t=globals())
    assert angular_parser(commit)[3][2] == footer


def test_parser_should_accept_message_without_scope():
    assert angular_parser("fix: superfix")[0] == 1
    assert angular_parser("fix: superfix")[3][0] == "superfix"
