from __future__ import annotations

from re import compile as regexp
from typing import TYPE_CHECKING, Sequence

import pytest

from semantic_release.commit_parser.scipy import tag_to_section
from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.enums import LevelBump

from tests.const import SUPPORTED_ISSUE_CLOSURE_PREFIXES

if TYPE_CHECKING:
    from semantic_release.commit_parser.scipy import ScipyCommitParser

    from tests.conftest import MakeCommitObjFn


unwordwrap = regexp(r"((?<!-)\n(?![\s*-]))")


def test_valid_scipy_parsed_chore_commits(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    scipy_chore_commit_parts: list[tuple[str, str, list[str]]],
    scipy_chore_commits: list[str],
):
    expected_parts = scipy_chore_commit_parts

    for i, full_commit_msg in enumerate(scipy_chore_commits):
        (commit_type, subject, commit_bodies) = expected_parts[i]
        commit_bodies = [unwordwrap.sub(" ", body).rstrip() for body in commit_bodies]
        expected_type = tag_to_section[commit_type]
        expected_descriptions = [
            subject,
            *[body.rstrip() for body in commit_bodies if body],
        ]
        expected_brk_desc: list[str] = []

        commit = make_commit_obj(full_commit_msg)
        result = default_scipy_parser.parse(commit)

        assert isinstance(result, ParsedCommit)
        assert LevelBump.NO_RELEASE is result.bump
        assert expected_type == result.type
        assert expected_descriptions == result.descriptions
        assert expected_brk_desc == result.breaking_descriptions
        assert result.scope is None


def test_valid_scipy_parsed_patch_commits(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    scipy_patch_commit_parts: list[tuple[str, str, list[str]]],
    scipy_patch_commits: list[str],
):
    expected_parts = scipy_patch_commit_parts

    for i, full_commit_msg in enumerate(scipy_patch_commits):
        (commit_type, subject, commit_bodies) = expected_parts[i]
        commit_bodies = [unwordwrap.sub(" ", body).rstrip() for body in commit_bodies]
        expected_type = tag_to_section[commit_type]
        expected_descriptions = [
            subject,
            *[body.rstrip() for body in commit_bodies if body],
        ]
        expected_brk_desc: list[str] = []

        commit = make_commit_obj(full_commit_msg)
        result = default_scipy_parser.parse(commit)

        assert isinstance(result, ParsedCommit)
        assert LevelBump.PATCH is result.bump
        assert expected_type == result.type
        assert expected_descriptions == result.descriptions
        assert expected_brk_desc == result.breaking_descriptions
        assert result.scope is None


def test_valid_scipy_parsed_minor_commits(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    scipy_minor_commit_parts: list[tuple[str, str, list[str]]],
    scipy_minor_commits: list[str],
):
    expected_parts = scipy_minor_commit_parts

    for i, full_commit_msg in enumerate(scipy_minor_commits):
        (commit_type, subject, commit_bodies) = expected_parts[i]
        commit_bodies = [unwordwrap.sub(" ", body).rstrip() for body in commit_bodies]
        expected_type = tag_to_section[commit_type]
        expected_descriptions = [
            subject,
            *[body for body in commit_bodies if body],
        ]
        expected_brk_desc: list[str] = []

        commit = make_commit_obj(full_commit_msg)
        result = default_scipy_parser.parse(commit)

        assert isinstance(result, ParsedCommit)
        assert LevelBump.MINOR is result.bump
        assert expected_type == result.type
        assert expected_descriptions == result.descriptions
        assert expected_brk_desc == result.breaking_descriptions
        assert result.scope is None


def test_valid_scipy_parsed_major_commits(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    scipy_major_commit_parts: list[tuple[str, str, list[str]]],
    scipy_major_commits: list[str],
):
    expected_parts = scipy_major_commit_parts

    for i, full_commit_msg in enumerate(scipy_major_commits):
        (commit_type, subject, commit_bodies) = expected_parts[i]
        commit_bodies = [unwordwrap.sub(" ", body).rstrip() for body in commit_bodies]
        expected_type = tag_to_section[commit_type]
        expected_descriptions = [
            subject,
            *[body for body in commit_bodies if body],
        ]
        brkg_prefix = "BREAKING CHANGE: "
        expected_brk_desc = [
            # TODO: Python 3.8 limitation, change to removeprefix() for 3.9+
            block[block.startswith(brkg_prefix) and len(brkg_prefix) :]
            # block.removeprefix("BREAKING CHANGE: ")
            for block in commit_bodies
            if block.startswith("BREAKING CHANGE")
        ]

        commit = make_commit_obj(full_commit_msg)
        result = default_scipy_parser.parse(commit)

        assert isinstance(result, ParsedCommit)
        assert LevelBump.MAJOR is result.bump
        assert expected_type == result.type
        assert expected_descriptions == result.descriptions
        assert expected_brk_desc == result.breaking_descriptions
        assert result.scope is None


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    # TODO: in v10, we will remove the merge request number from the subject line
    [
        # GitHub, Gitea style
        (
            "ENH: add new feature (#123)",
            "add new feature (#123)",
            "#123",
        ),
        # GitLab style
        (
            "BUG: fix regex in parser (!456)",
            "fix regex in parser (!456)",
            "!456",
        ),
        # BitBucket style
        (
            "ENH: add new feature (pull request #123)",
            "add new feature (pull request #123)",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        ("DEP: add dependency (#123)\n\nCloses: #400", "add dependency (#123)", "#123"),
        # None
        ("BUG: superfix", "superfix", ""),
        # None but includes an issue footer it should not be considered a linked merge request
        ("BUG: superfix\n\nCloses: #400", "superfix", ""),
    ],
)
def test_parser_return_linked_merge_request_from_commit_message(
    default_scipy_parser: ScipyCommitParser,
    message: str,
    subject: str,
    merge_request_number: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_scipy_parser.parse(make_commit_obj(message))
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
                f"ENH: add magic parser\n\n{footer}",
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
                f"ENH(parser): add magic parser\n\n{footer}",
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
                f"ENH(parser): add magic parser\n\n{footer}",
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
            "ENH(parser): add magic parser (#123)\n\nCloses: #555",
            ["#555"],
        ),
        # Does not grab an issue when there is only a GitHub PR reference in the subject
        ("ENH(parser): add magic parser (#123)", []),
        # Does not grab an issue when there is only a Bitbucket PR reference in the subject
        ("ENH(parser): add magic parser (pull request #123)", []),
    ],
)
def test_parser_return_linked_issues_from_commit_message(
    default_scipy_parser: ScipyCommitParser,
    message: str,
    linked_issues: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    result = default_scipy_parser.parse(make_commit_obj(message))
    assert isinstance(result, ParsedCommit)
    assert tuple(linked_issues) == result.linked_issues
