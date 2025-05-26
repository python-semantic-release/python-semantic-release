# ruff: noqa: SIM300
from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING, Iterable, Sequence

import pytest

from semantic_release.commit_parser.conventional import (
    ConventionalCommitParser,
    ConventionalCommitParserOptions,
)
from semantic_release.commit_parser.token import ParsedCommit, ParseError
from semantic_release.enums import LevelBump

from tests.const import SUPPORTED_ISSUE_CLOSURE_PREFIXES

if TYPE_CHECKING:
    from tests.conftest import MakeCommitObjFn


# NOTE: GitLab squash commits are not tested because by default
# they don't have any unique attributes of them and they are also
# fully customizable.
# See https://docs.gitlab.com/ee/user/project/merge_requests/commit_templates.html
# It also depends if Fast-Forward merge is enabled because that will
# define if there is a merge commit or not and with that likely no
# Merge Request Number included unless the user adds it.
# TODO: add the recommendation in the PSR documentation is to set your GitLab templates
# to mirror GitHub like references in the first subject line. Will Not matter
# if fast-forward merge is enabled or not.


@pytest.mark.parametrize(
    "commit_message", ["", "feat(parser\n): Add new parser pattern"]
)
def test_parser_raises_unknown_message_style(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(commit_message))
    assert isinstance(parsed_results, Iterable)
    for result in parsed_results:
        assert isinstance(result, ParseError)


@pytest.mark.parametrize(
    "commit_message, expected_commit_details",
    [
        pytest.param(
            commit_message,
            expected_commit_details,
            id=test_id,
        )
        for test_id, commit_message, expected_commit_details in [
            (
                "Single commit squashed via BitBucket PR resolution",
                dedent(
                    """\
                    Merged in feat/my-awesome-stuff  (pull request #10)

                    fix(release-config): some commit subject

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>
                    """
                ),
                [
                    None,
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                        "linked_merge_request": "#10",
                    },
                ],
            ),
            (
                "Multiple commits squashed via BitBucket PR resolution",
                dedent(
                    """\
                    Merged in feat/my-awesome-stuff  (pull request #10)

                    fix(release-config): some commit subject

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>

                    feat: implemented searching gizmos by keyword

                    docs(parser): add new parser pattern

                    fix(cli)!: changed option name

                    BREAKING CHANGE: A breaking change description

                    Closes: #555

                    invalid non-conventional formatted commit
                    """
                ),
                [
                    None,
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.MINOR,
                        "type": "features",
                        "descriptions": ["implemented searching gizmos by keyword"],
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.NO_RELEASE,
                        "type": "documentation",
                        "scope": "parser",
                        "descriptions": [
                            "add new parser pattern",
                        ],
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.MAJOR,
                        "type": "bug fixes",
                        "scope": "cli",
                        "descriptions": [
                            "changed option name",
                            # This is a bit unusual but its because there is no identifier that will
                            # identify this as a separate commit so it gets included in the previous commit
                            "invalid non-conventional formatted commit",
                        ],
                        "breaking_descriptions": [
                            "A breaking change description",
                        ],
                        "linked_issues": ("#555",),
                        "linked_merge_request": "#10",
                    },
                ],
            ),
        ]
    ],
)
def test_parser_squashed_commit_bitbucket_squash_style(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            **{
                **default_conventional_parser.options.__dict__,
                "parse_squash_commits": True,
            }
        )
    )

    # Build the commit object and parse it
    the_commit = make_commit_obj(commit_message)
    parsed_results = parser.parse(the_commit)

    # Validate the results
    assert isinstance(parsed_results, Iterable)
    assert (
        len(expected_commit_details) == len(parsed_results)
    ), f"Expected {len(expected_commit_details)} parsed results, but got {len(parsed_results)}"

    for result, expected in zip(parsed_results, expected_commit_details):
        if expected is None:
            assert isinstance(result, ParseError)
            continue

        assert isinstance(result, ParsedCommit)
        # Required
        assert expected["bump"] == result.bump
        assert expected["type"] == result.type
        # Optional
        assert expected.get("scope", "") == result.scope
        # TODO: v11 change to tuples
        assert expected.get("descriptions", []) == result.descriptions
        assert expected.get("breaking_descriptions", []) == result.breaking_descriptions
        assert expected.get("linked_issues", ()) == result.linked_issues
        assert expected.get("linked_merge_request", "") == result.linked_merge_request


@pytest.mark.parametrize(
    "commit_message, expected_commit_details",
    [
        pytest.param(
            commit_message,
            expected_commit_details,
            id=test_id,
        )
        for test_id, commit_message, expected_commit_details in [
            (
                "Single commit squashed via manual Git squash merge",
                dedent(
                    """\
                    Squashed commit of the following:

                    commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb
                    Author: author <author@not-an-email.com>
                    Date:   Sun Jan 19 12:05:23 2025 +0000

                        fix(release-config): some commit subject

                        An additional description

                        Second paragraph with multiple lines
                        that will be condensed

                        Resolves: #12
                        Signed-off-by: author <author@not-an-email.com>

                    """
                ),
                [
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                    }
                ],
            ),
            (
                "Multiple commits squashed via manual Git squash merge",
                dedent(
                    """\
                    Squashed commit of the following:

                    commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb
                    Author: author <author@not-an-email.com>
                    Date:   Sun Jan 19 12:05:23 2025 +0000

                        fix(release-config): some commit subject

                        An additional description

                        Second paragraph with multiple lines
                        that will be condensed

                        Resolves: #12
                        Signed-off-by: author <author@not-an-email.com>

                    commit 1f34769bf8352131ad6f4879b8c47becf3c7aa69
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        feat: implemented searching gizmos by keyword

                    commit b2334a64a11ef745a17a2a4034f651e08e8c45a6
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        docs(parser): add new parser pattern

                    commit 5f0292fb5a88c3a46e4a02bec35b85f5228e8e51
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        fix(cli)!: changed option name

                        BREAKING CHANGE: A breaking change description

                        Closes: #555

                    commit 2f314e7924be161cfbf220d3b6e2a6189a3b5609
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        invalid non-conventional formatted commit
                    """
                ),
                [
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                    },
                    {
                        "bump": LevelBump.MINOR,
                        "type": "features",
                        "descriptions": ["implemented searching gizmos by keyword"],
                    },
                    {
                        "bump": LevelBump.NO_RELEASE,
                        "type": "documentation",
                        "scope": "parser",
                        "descriptions": [
                            "add new parser pattern",
                        ],
                    },
                    {
                        "bump": LevelBump.MAJOR,
                        "type": "bug fixes",
                        "scope": "cli",
                        "descriptions": [
                            "changed option name",
                        ],
                        "breaking_descriptions": [
                            "A breaking change description",
                        ],
                        "linked_issues": ("#555",),
                    },
                    None,
                ],
            ),
        ]
    ],
)
def test_parser_squashed_commit_git_squash_style(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            **{
                **default_conventional_parser.options.__dict__,
                "parse_squash_commits": True,
            }
        )
    )

    # Build the commit object and parse it
    the_commit = make_commit_obj(commit_message)
    parsed_results = parser.parse(the_commit)

    # Validate the results
    assert isinstance(parsed_results, Iterable)
    assert (
        len(expected_commit_details) == len(parsed_results)
    ), f"Expected {len(expected_commit_details)} parsed results, but got {len(parsed_results)}"

    for result, expected in zip(parsed_results, expected_commit_details):
        if expected is None:
            assert isinstance(result, ParseError)
            continue

        assert isinstance(result, ParsedCommit)
        # Required
        assert expected["bump"] == result.bump
        assert expected["type"] == result.type
        # Optional
        assert expected.get("scope", "") == result.scope
        # TODO: v11 change to tuples
        assert expected.get("descriptions", []) == result.descriptions
        assert expected.get("breaking_descriptions", []) == result.breaking_descriptions
        assert expected.get("linked_issues", ()) == result.linked_issues
        assert expected.get("linked_merge_request", "") == result.linked_merge_request


@pytest.mark.parametrize(
    "commit_message, expected_commit_details",
    [
        pytest.param(
            commit_message,
            expected_commit_details,
            id=test_id,
        )
        for test_id, commit_message, expected_commit_details in [
            (
                "Single commit squashed via GitHub PR resolution",
                dedent(
                    """\
                    fix(release-config): some commit subject (#10)

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>
                    """
                ),
                [
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                        "linked_merge_request": "#10",
                    },
                ],
            ),
            (
                "Multiple commits squashed via GitHub PR resolution",
                dedent(
                    """\
                    fix(release-config): some commit subject (#10)

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>

                    * feat: implemented searching gizmos by keyword

                    * docs(parser): add new parser pattern

                    * fix(cli)!: changed option name

                    BREAKING CHANGE: A breaking change description

                    Closes: #555

                    * invalid non-conventional formatted commit
                    """
                ),
                [
                    {
                        "bump": LevelBump.PATCH,
                        "type": "bug fixes",
                        "scope": "release-config",
                        "descriptions": [
                            "some commit subject",
                            "An additional description",
                            "Second paragraph with multiple lines that will be condensed",
                            "Signed-off-by: author <author@not-an-email.com>",
                        ],
                        "linked_issues": ("#12",),
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.MINOR,
                        "type": "features",
                        "descriptions": ["implemented searching gizmos by keyword"],
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.NO_RELEASE,
                        "type": "documentation",
                        "scope": "parser",
                        "descriptions": [
                            "add new parser pattern",
                        ],
                        "linked_merge_request": "#10",
                    },
                    {
                        "bump": LevelBump.MAJOR,
                        "type": "bug fixes",
                        "scope": "cli",
                        "descriptions": [
                            "changed option name",
                            # This is a bit unusual but its because there is no identifier that will
                            # identify this as a separate commit so it gets included in the previous commit
                            "* invalid non-conventional formatted commit",
                        ],
                        "breaking_descriptions": [
                            "A breaking change description",
                        ],
                        "linked_issues": ("#555",),
                        "linked_merge_request": "#10",
                    },
                ],
            ),
        ]
    ],
)
def test_parser_squashed_commit_github_squash_style(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            **{
                **default_conventional_parser.options.__dict__,
                "parse_squash_commits": True,
            }
        )
    )

    # Build the commit object and parse it
    the_commit = make_commit_obj(commit_message)
    parsed_results = parser.parse(the_commit)

    # Validate the results
    assert isinstance(parsed_results, Iterable)
    assert (
        len(expected_commit_details) == len(parsed_results)
    ), f"Expected {len(expected_commit_details)} parsed results, but got {len(parsed_results)}"

    for result, expected in zip(parsed_results, expected_commit_details):
        if expected is None:
            assert isinstance(result, ParseError)
            continue

        assert isinstance(result, ParsedCommit)
        # Required
        assert expected["bump"] == result.bump
        assert expected["type"] == result.type
        # Optional
        assert expected.get("scope", "") == result.scope
        # TODO: v11 change to tuples
        assert expected.get("descriptions", []) == result.descriptions
        assert expected.get("breaking_descriptions", []) == result.breaking_descriptions
        assert expected.get("linked_issues", ()) == result.linked_issues
        assert expected.get("linked_merge_request", "") == result.linked_merge_request


@pytest.mark.parametrize(
    "commit_message, bump",
    [
        (
            "feat(parsers): add new parser pattern\n\nBREAKING CHANGE: change",
            LevelBump.MAJOR,
        ),
        ("feat(parsers)!: add new parser pattern", LevelBump.MAJOR),
        (
            "feat(parsers): add new parser pattern\n\nNew pattern is awesome\n\n"
            "BREAKING CHANGE: change \n",
            LevelBump.MAJOR,
        ),
        (
            "feat(parsers): add new parser pattern\n\nBREAKING-CHANGE: change !",
            LevelBump.MAJOR,
        ),
        ("feat(parser): add emoji parser", LevelBump.MINOR),
        ("fix(parser): fix regex in conventional parser", LevelBump.PATCH),
        ("test(parser): add a test for conventional parser", LevelBump.NO_RELEASE),
        ("feat(parser)!: edit data parsing stuff", LevelBump.MAJOR),
        ("fix!: edit data parsing stuff again", LevelBump.MAJOR),
        ("fix: superfix", LevelBump.PATCH),
    ],
)
def test_parser_returns_correct_bump_level(
    default_conventional_parser: ConventionalCommitParser,
    commit_message: str,
    bump: LevelBump,
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(commit_message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
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
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    type_: str,
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
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
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    scope: str,
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
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
        ("feat(parser): add emoji parser", ["add emoji parser"]),
        (
            "fix(parser): fix regex in conventional parser",
            ["fix regex in conventional parser"],
        ),
        (
            "test(parser): add a test for conventional parser",
            ["add a test for conventional parser"],
        ),
        (
            f"fix(tox): fix env \n\n{_long_text}\n\n{_footer}",
            ["fix env ", _long_text],
        ),
        ("fix: superfix", ["superfix"]),
    ],
)
def test_parser_return_subject_from_commit_message(
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    descriptions: list[str],
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert result.descriptions == descriptions


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    [
        # GitHub, Gitea style
        (
            "feat(parser): add emoji parser (#123)",
            "add emoji parser",
            "#123",
        ),
        # GitLab style
        (
            "fix(parser): fix regex in conventional parser (!456)",
            "fix regex in conventional parser",
            "!456",
        ),
        # BitBucket style
        (
            "feat(parser): add emoji parser (pull request #123)",
            "add emoji parser",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        ("fix: superfix (#123)\n\nCloses: #400", "superfix", "#123"),
        # None
        ("fix: superfix", "superfix", ""),
        # None but includes an issue footer it should not be considered a linked merge request
        ("fix: superfix\n\nCloses: #400", "superfix", ""),
    ],
)
def test_parser_return_linked_merge_request_from_commit_message(
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    subject: str,
    merge_request_number: str,
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert merge_request_number == result.linked_merge_request
    assert subject == result.descriptions[0]


@pytest.mark.parametrize(
    "message, linked_issues",
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
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    linked_issues: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert 1 == len(parsed_results)

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert tuple(linked_issues) == result.linked_issues


@pytest.mark.parametrize(
    "message, notices",
    [
        pytest.param(
            message,
            notices,
            id=test_id,
        )
        for test_id, message, notices in [
            (
                "single notice",
                dedent(
                    """\
                    fix(parser): fix regex in conventional parser

                    NOTICE: This is a notice
                    """
                ),
                ["This is a notice"],
            ),
            (
                "multiline notice",
                dedent(
                    """\
                    fix(parser): fix regex in conventional parser

                    NOTICE: This is a notice that is longer than
                    other notices
                    """
                ),
                ["This is a notice that is longer than other notices"],
            ),
            (
                "multiple notices",
                dedent(
                    """\
                    fix(parser): fix regex in conventional parser

                    NOTICE: This is a notice

                    NOTICE: This is a second notice
                    """
                ),
                ["This is a notice", "This is a second notice"],
            ),
            (
                "notice with other footer",
                dedent(
                    """\
                    fix(parser): fix regex in conventional parser

                    BREAKING CHANGE: This is a breaking change

                    NOTICE: This is a notice
                    """
                ),
                ["This is a notice"],
            ),
        ]
    ],
)
def test_parser_return_release_notices_from_commit_message(
    default_conventional_parser: ConventionalCommitParser,
    message: str,
    notices: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_conventional_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert tuple(notices) == result.release_notices

    full_description = str.join("\n\n", result.descriptions)
    full_notice = str.join("\n\n", result.release_notices)
    assert full_notice not in full_description


##############################
# test custom parser options #
##############################
def test_parser_custom_default_level(make_commit_obj: MakeCommitObjFn):
    options = ConventionalCommitParserOptions(default_bump_level=LevelBump.MINOR)
    parsed_results = ConventionalCommitParser(options).parse(
        make_commit_obj("test(parser): add a test for conventional parser")
    )

    assert isinstance(parsed_results, Iterable)

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert result.bump is LevelBump.MINOR


def test_parser_custom_allowed_types(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
):
    new_tag = "custom"
    custom_allowed_tags = [*default_conventional_parser.options.allowed_tags, new_tag]
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            allowed_tags=tuple(custom_allowed_tags),
        )
    )

    for commit_type, commit_msg in [
        (new_tag, f"{new_tag}: ..."),  # no scope
        (new_tag, f"{new_tag}(parser): ..."),  # with scope
        ("chores", "chore(parser): ..."),  # existing, non-release tag
    ]:
        parsed_results = parser.parse(make_commit_obj(commit_msg))
        assert isinstance(parsed_results, Iterable)

        result = next(iter(parsed_results))
        assert isinstance(result, ParsedCommit)
        assert result.type == commit_type
        assert result.bump is LevelBump.NO_RELEASE


def test_parser_custom_allowed_types_ignores_non_types(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
):
    banned_tag = "feat"
    custom_allowed_tags = [*default_conventional_parser.options.allowed_tags]
    custom_allowed_tags.remove(banned_tag)

    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            allowed_tags=tuple(custom_allowed_tags),
        )
    )

    parsed_results = parser.parse(make_commit_obj(f"{banned_tag}(parser): ..."))
    assert isinstance(parsed_results, Iterable)

    result = next(iter(parsed_results))
    assert isinstance(result, ParseError)


def test_parser_custom_minor_tags(make_commit_obj: MakeCommitObjFn):
    custom_minor_tag = "docs"
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(minor_tags=(custom_minor_tag,))
    )

    parsed_results = parser.parse(make_commit_obj(f"{custom_minor_tag}: ..."))
    assert isinstance(parsed_results, Iterable)

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert result.bump is LevelBump.MINOR


def test_parser_custom_patch_tags(make_commit_obj: MakeCommitObjFn):
    custom_patch_tag = "test"
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(patch_tags=(custom_patch_tag,))
    )

    parsed_results = parser.parse(make_commit_obj(f"{custom_patch_tag}: ..."))
    assert isinstance(parsed_results, Iterable)

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert result.bump is LevelBump.PATCH


def test_parser_ignore_merge_commit(
    default_conventional_parser: ConventionalCommitParser,
    make_commit_obj: MakeCommitObjFn,
):
    # Setup: Enable parsing of linked issues
    parser = ConventionalCommitParser(
        options=ConventionalCommitParserOptions(
            **{
                **default_conventional_parser.options.__dict__,
                "ignore_merge_commits": True,
            }
        )
    )

    base_commit = make_commit_obj("Merge branch 'fix/fix-feature' into 'main'")
    incomming_commit = make_commit_obj("feat: add a new feature")

    # Setup: Create a merge commit
    merge_commit = make_commit_obj("Merge branch 'feat/add-new-feature' into 'main'")
    merge_commit.parents = [base_commit, incomming_commit]

    # Action
    parsed_result = parser.parse(merge_commit)

    assert isinstance(parsed_result, ParseError)
    assert "Ignoring merge commit" in parsed_result.error
