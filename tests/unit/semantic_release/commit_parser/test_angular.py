from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest

from semantic_release.commit_parser.angular import (
    AngularCommitParser,
    AngularParserOptions,
)
from semantic_release.commit_parser.token import ParsedCommit, ParseError
from semantic_release.enums import LevelBump

from tests.const import SUPPORTED_ISSUE_CLOSURE_PREFIXES

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
_footer = "Closes: #400"


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


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    # TODO: in v10, we will remove the merge request number from the subject line
    [
        # GitHub, Gitea style
        (
            "feat(parser): add emoji parser (#123)",
            "add emoji parser (#123)",
            "#123",
        ),
        # GitLab style
        (
            "fix(parser): fix regex in angular parser (!456)",
            "fix regex in angular parser (!456)",
            "!456",
        ),
        # BitBucket style
        (
            "feat(parser): add emoji parser (pull request #123)",
            "add emoji parser (pull request #123)",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        ("fix: superfix (#123)\n\nCloses: #400", "superfix (#123)", "#123"),
        # None
        ("fix: superfix", "superfix", ""),
        # None but includes an issue footer it should not be considered a linked merge request
        ("fix: superfix\n\nCloses: #400", "superfix", ""),
    ],
)
def test_parser_return_linked_merge_request_from_commit_message(
    default_angular_parser: AngularCommitParser,
    message: str,
    subject: str,
    merge_request_number: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert merge_request_number == result.linked_merge_request
    assert subject == result.descriptions[0]


@pytest.mark.parametrize(
    "message, linked_issues",
    # TODO: in v10, we will remove the issue reference footers from the descriptions
    [
        *[
            # GitHub, Gitea, GitLab style
            (
                f"feat(parser): add magic parser\n\n{footer}",
                linked_issues,
            )
            for footer_prefix in SUPPORTED_ISSUE_CLOSURE_PREFIXES
            for footer, linked_issues in [
                # Single issue
                (
                    f"{footer_prefix.capitalize()}: #555",
                    ["#555"],
                ),  # Git Footer style (capitalized)
                (f"{footer_prefix.lower()}: #555", ["#555"]),  # lowercase prefix
                (f"{footer_prefix.upper()}: #555", ["#555"]),  # uppercase prefix
                # Mulitple issues (variant 1: list with one prefix, not supported by GitHub)
                (
                    f"{footer_prefix}: #555,#444",
                    ["#444", "#555"],
                ),  # Comma separated (w/o space)
                (
                    f"{footer_prefix}: #555, #444",
                    ["#444", "#555"],
                ),  # Comma separated (w/ space)
                (
                    f"{footer_prefix}: #555 , #444",
                    ["#444", "#555"],
                ),  # Comma separated (w/ extra space)
                (f"{footer_prefix}: #555 #444", ["#444", "#555"]),  # Space separated
                (
                    f"{footer_prefix}: #555;#444",
                    ["#444", "#555"],
                ),  # semicolon separated (w/o space)
                (
                    f"{footer_prefix}: #555; #444",
                    ["#444", "#555"],
                ),  # semicolon separated (w/ space)
                (
                    f"{footer_prefix}: #555 ; #444",
                    ["#444", "#555"],
                ),  # semicolon separated (w/ extra space)
                (
                    f"{footer_prefix}: #555/#444",
                    ["#444", "#555"],
                ),  # slash separated (w/o space)
                (
                    f"{footer_prefix}: #555/ #444",
                    ["#444", "#555"],
                ),  # slash separated (w/ space)
                (
                    f"{footer_prefix}: #555 / #444",
                    ["#444", "#555"],
                ),  # slash separated (w/ extra space)
                (
                    f"{footer_prefix}: #555&#444",
                    ["#444", "#555"],
                ),  # ampersand separated (w/o space)
                (
                    f"{footer_prefix}: #555& #444",
                    ["#444", "#555"],
                ),  # ampersand separated (w/ space)
                (
                    f"{footer_prefix}: #555 & #444",
                    ["#444", "#555"],
                ),  # ampersand separated (w/ extra space)
                (f"{footer_prefix}: #555 and #444", ["#444", "#555"]),  # and separated
                (
                    f"{footer_prefix}: #555, #444, and #333",
                    ["#333", "#444", "#555"],
                ),  # and separated
                # Mulitple issues (variant 2: multiple footers, supported by GitHub)
                (f"{footer_prefix}: #555\n{footer_prefix}: #444", ["#444", "#555"]),
                # More than 2 issues
                (
                    f"{footer_prefix}: #555, #444, #333",
                    ["#333", "#444", "#555"],
                ),
                # More than 2 issues (force numerical sort)
                (
                    f"{footer_prefix}: #555, #3333, #444",
                    ["#444", "#555", "#3333"],
                ),
                # Single issue listed multiple times
                (f"{footer_prefix}: #555, #555", ["#555"]),
                # Multiple footers with the same issue
                (f"{footer_prefix}: #555\n{footer_prefix}: #555", ["#555"]),
                # Multiple issues via multiple inline git footers
                (f"{footer_prefix}: #555, {footer_prefix}: #444", ["#444", "#555"]),
                # Multiple valid footers
                (
                    str.join(
                        "\n",
                        [
                            f"{footer_prefix}: #555",
                            "Signed-off-by: johndoe <johndoe@mail.com>",
                            f"{footer_prefix}: #444",
                        ],
                    ),
                    ["#444", "#555"],
                ),
                # ----------------------------------------- Invalid Sets ----------------------------------------- #
                # Must have colon because it is a git footer, these will not return a linked issue
                (f"{footer_prefix} #666", []),
                (f"{footer_prefix} #666, #777", []),
                # Invalid Multiple issues (although it is supported by GitHub, it is not supported by the parser)
                (f"{footer_prefix} #666, {footer_prefix} #777", []),
                # Invalid 'and' separation
                (f"{footer_prefix}: #666and#777", ["#666and#777"]),
                # Invalid prefix
                ("ref: #666", []),
                # body mentions an issue and has a different git footer
                (
                    "In #666, the devils in the details...\n\nSigned-off-by: johndoe <johndoe@mail.com>",
                    [],
                ),
            ]
        ],
        *[
            # JIRA style
            (
                f"feat(parser): add magic parser\n\n{footer}",
                linked_issues,
            )
            for footer_prefix in SUPPORTED_ISSUE_CLOSURE_PREFIXES
            for footer, linked_issues in [
                # Single issue
                (
                    f"{footer_prefix.capitalize()}: ABC-555",
                    ["ABC-555"],
                ),  # Git Footer style (capitalized)
                (f"{footer_prefix.lower()}: ABC-555", ["ABC-555"]),  # lowercase prefix
                (f"{footer_prefix.upper()}: ABC-555", ["ABC-555"]),  # uppercase prefix
                # Mulitple issues (variant 1: list with one prefix, not supported by GitHub)
                (
                    f"{footer_prefix}: ABC-555,ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # Comma separated (w/o space)
                (
                    f"{footer_prefix}: ABC-555, ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # Comma separated (w/ space)
                (
                    f"{footer_prefix}: ABC-555 , ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # Comma separated (w/ extra space)
                (
                    f"{footer_prefix}: ABC-555 ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # Space separated
                (
                    f"{footer_prefix}: ABC-555;ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # semicolon separated (w/o space)
                (
                    f"{footer_prefix}: ABC-555; ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # semicolon separated (w/ space)
                (
                    f"{footer_prefix}: ABC-555 ; ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # semicolon separated (w/ extra space)
                (
                    f"{footer_prefix}: ABC-555/ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # slash separated (w/o space)
                (
                    f"{footer_prefix}: ABC-555/ ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # slash separated (w/ space)
                (
                    f"{footer_prefix}: ABC-555 / ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # slash separated (w/ extra space)
                (
                    f"{footer_prefix}: ABC-555&ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # ampersand separated (w/o space)
                (
                    f"{footer_prefix}: ABC-555& ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # ampersand separated (w/ space)
                (
                    f"{footer_prefix}: ABC-555 & ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # ampersand separated (w/ extra space)
                (
                    f"{footer_prefix}: ABC-555 and ABC-444",
                    ["ABC-444", "ABC-555"],
                ),  # and separated
                (
                    f"{footer_prefix}: ABC-555, ABC-444, and ABC-333",
                    ["ABC-333", "ABC-444", "ABC-555"],
                ),  # and separated
                # Mulitple issues (variant 2: multiple footers, supported by GitHub)
                (
                    f"{footer_prefix}: ABC-555\n{footer_prefix}: ABC-444",
                    ["ABC-444", "ABC-555"],
                ),
                # More than 2 issues
                (
                    f"{footer_prefix}: ABC-555, ABC-444, ABC-333",
                    ["ABC-333", "ABC-444", "ABC-555"],
                ),
                # More than 2 issues (force numerical sort)
                (
                    f"{footer_prefix}: ABC-555, ABC-3333, ABC-444",
                    ["ABC-444", "ABC-555", "ABC-3333"],
                ),
                # Single issue listed multiple times
                (f"{footer_prefix}: ABC-555, ABC-555", ["ABC-555"]),
                # Multiple footers with the same issue
                (f"{footer_prefix}: ABC-555\n{footer_prefix}: ABC-555", ["ABC-555"]),
                # Multiple issues via multiple inline git footers
                (
                    f"{footer_prefix}: ABC-666, {footer_prefix}: ABC-777",
                    ["ABC-666", "ABC-777"],
                ),
                # Multiple valid footers
                (
                    str.join(
                        "\n",
                        [
                            f"{footer_prefix}: ABC-555",
                            "Signed-off-by: johndoe <johndoe@mail.com>",
                            f"{footer_prefix}: ABC-444",
                        ],
                    ),
                    ["ABC-444", "ABC-555"],
                ),
                # ----------------------------------------- Invalid Sets ----------------------------------------- #
                # Must have colon because it is a git footer, these will not return a linked issue
                (f"{footer_prefix} ABC-666", []),
                (f"{footer_prefix} ABC-666, ABC-777", []),
                # Invalid Multiple issues (although it is supported by GitHub, it is not supported by the parser)
                (f"{footer_prefix} ABC-666, {footer_prefix} ABC-777", []),
                # Invalid 'and' separation
                (f"{footer_prefix}: ABC-666andABC-777", ["ABC-666andABC-777"]),
                # Invalid prefix
                ("ref: ABC-666", []),
                # body mentions an issue and has a different git footer
                (
                    "In ABC-666, the devils in the details...\n\nSigned-off-by: johndoe <johndoe@mail.com>",
                    [],
                ),
            ]
        ],
        *[
            (
                f"feat(parser): add magic parser\n\n{footer}",
                linked_issues,
            )
            for footer, linked_issues in [
                # Multiple footers with the same issue but different prefixes
                ("Resolves: #555\nfix: #444", ["#444", "#555"]),
                # Whitespace padded footer
                ("  Resolves: #555\n", ["#555"]),
            ]
        ],
        (
            # Only grabs the issue reference when there is a GitHub PR reference in the subject
            "feat(parser): add magic parser (#123)\n\nCloses: #555",
            ["#555"],
        ),
        # Does not grab an issue when there is only a GitHub PR reference in the subject
        ("feat(parser): add magic parser (#123)", []),
        # Does not grab an issue when there is only a Bitbucket PR reference in the subject
        ("feat(parser): add magic parser (pull request #123)", []),
    ],
)
def test_parser_return_linked_issues_from_commit_message(
    default_angular_parser: AngularCommitParser,
    message: str,
    linked_issues: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    result = default_angular_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert tuple(linked_issues) == result.linked_issues


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
