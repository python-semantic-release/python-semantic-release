from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest

from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.enums import LevelBump

from tests.const import SUPPORTED_ISSUE_CLOSURE_PREFIXES

if TYPE_CHECKING:
    from semantic_release.commit_parser.emoji import EmojiCommitParser

    from tests.conftest import MakeCommitObjFn


@pytest.mark.parametrize(
    "commit_message, bump, type_, descriptions, breaking_descriptions",
    [
        # Major bump
        (
            ":boom: Breaking changes\n\nMore description\n\nEven more description",
            LevelBump.MAJOR,
            ":boom:",
            [":boom: Breaking changes", "More description", "Even more description"],
            ["More description", "Even more description"],
        ),
        # Minor bump
        (
            ":sparkles: Add a new feature\n\nSome description of the feature",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles: Add a new feature", "Some description of the feature"],
            [],
        ),
        # Patch bump
        (
            ":bug: Fixing a bug\n\nThe bug is finally gone!",
            LevelBump.PATCH,
            ":bug:",
            [":bug: Fixing a bug", "The bug is finally gone!"],
            [],
        ),
        # No release
        (
            ":pencil: Documentation changes",
            LevelBump.NO_RELEASE,
            "Other",
            [":pencil: Documentation changes"],
            [],
        ),
        # Multiple emojis
        (
            ":sparkles::pencil: Add a feature and document it",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles::pencil: Add a feature and document it"],
            [],
        ),
        # Emoji in description
        (
            ":sparkles: Add a new feature\n\n:boom: should not be detected",
            LevelBump.MINOR,
            ":sparkles:",
            [":sparkles: Add a new feature", ":boom: should not be detected"],
            [],
        ),
    ],
)
def test_default_emoji_parser(
    default_emoji_parser: EmojiCommitParser,
    commit_message: str,
    bump: LevelBump,
    type_: str,
    descriptions: list[str],
    breaking_descriptions: list[str],
    make_commit_obj: MakeCommitObjFn,
):
    commit = make_commit_obj(commit_message)
    result = default_emoji_parser.parse(commit)

    assert isinstance(result, ParsedCommit)
    assert bump is result.bump
    assert type_ == result.type
    assert descriptions == result.descriptions
    assert breaking_descriptions == result.breaking_descriptions


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    # TODO: in v10, we will remove the merge request number from the subject line
    [
        # GitHub, Gitea style
        (
            ":sparkles: add new feature (#123)",
            ":sparkles: add new feature (#123)",
            "#123",
        ),
        # GitLab style
        (
            ":bug: fix regex in parser (!456)",
            ":bug: fix regex in parser (!456)",
            "!456",
        ),
        # BitBucket style
        (
            ":sparkles: add new feature (pull request #123)",
            ":sparkles: add new feature (pull request #123)",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        (":bug: superfix (#123)\n\nCloses: #400", ":bug: superfix (#123)", "#123"),
        # None
        (":bug: superfix", ":bug: superfix", ""),
        # None but includes an issue footer it should not be considered a linked merge request
        (":bug: superfix\n\nCloses: #400", ":bug: superfix", ""),
    ],
)
def test_parser_return_linked_merge_request_from_commit_message(
    default_emoji_parser: EmojiCommitParser,
    message: str,
    subject: str,
    merge_request_number: str,
    make_commit_obj: MakeCommitObjFn,
):
    result = default_emoji_parser.parse(make_commit_obj(message))
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
                f":sparkles: (parser) add magic parser\n\n{footer}",
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
                f":sparkles: (parser) add magic parser\n\n{footer}",
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
                f":sparkles: (parser) add magic parser\n\n{footer}",
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
            ":sparkles: (parser) add magic parser (#123)\n\nCloses: #555",
            ["#555"],
        ),
        # Does not grab an issue when there is only a GitHub PR reference in the subject
        (":sparkles: (parser) add magic parser (#123)", []),
        # Does not grab an issue when there is only a Bitbucket PR reference in the subject
        (":sparkles: (parser) add magic parser (pull request #123)", []),
    ],
)
def test_parser_return_linked_issues_from_commit_message(
    default_emoji_parser: EmojiCommitParser,
    message: str,
    linked_issues: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    # Setup: Enable parsing of linked issues
    default_emoji_parser.options.parse_linked_issues = True

    # Action
    result = default_emoji_parser.parse(make_commit_obj(message))

    # Evaluate (expected -> actual)
    assert isinstance(result, ParsedCommit)
    assert tuple(linked_issues) == result.linked_issues
