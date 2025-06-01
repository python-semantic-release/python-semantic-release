# ruff: noqa: SIM300
from __future__ import annotations

from re import compile as regexp
from textwrap import dedent
from typing import TYPE_CHECKING, Iterable, Sequence

import pytest

from semantic_release.commit_parser.scipy import (
    ScipyCommitParser,
    ScipyParserOptions,
)
from semantic_release.commit_parser.token import ParsedCommit, ParseError
from semantic_release.enums import LevelBump

from tests.const import SUPPORTED_ISSUE_CLOSURE_PREFIXES

if TYPE_CHECKING:
    from tests.conftest import MakeCommitObjFn


unwordwrap = regexp(r"((?<!-)\n(?![\s*-]))")


@pytest.mark.parametrize(
    "commit_message", ["", "feat(parser\n): Add new parser pattern"]
)
def test_parser_raises_unknown_message_style(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
):
    parsed_results = default_scipy_parser.parse(make_commit_obj(commit_message))
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
                "Chore Type: Benchmark related",
                dedent(
                    """\
                    BENCH:optimize_milp.py: add new benchmark

                    Benchmarks the performance of the MILP solver
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "optimize_milp.py",
                    "descriptions": [
                        "add new benchmark",
                        "Benchmarks the performance of the MILP solver",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Chore Type: Dev Tool Related",
                dedent(
                    """\
                    DEV: add unicode check to pre-commit hook
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "",
                    "descriptions": [
                        "add unicode check to pre-commit hook",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Chore Type: documentation related",
                dedent(
                    """\
                    DOC: change approx_fprime doctest (#20568)
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "documentation",
                    "scope": "",
                    "descriptions": [
                        "change approx_fprime doctest",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "#20568",
                },
            ),
            (
                "Chore Type: style related",
                dedent(
                    """\
                    STY: fixed ruff & mypy issues
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "",
                    "descriptions": [
                        "fixed ruff & mypy issues",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Chore Type: Test related",
                dedent(
                    """\
                    TST: Skip Cython tests for editable installs
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "",
                    "descriptions": [
                        "Skip Cython tests for editable installs",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Chore Type: Test related",
                dedent(
                    """\
                    TEST: Skip Cython tests for editable installs
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "",
                    "descriptions": [
                        "Skip Cython tests for editable installs",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Chore Type: Release related",
                dedent(
                    """\
                    REL: set version to 1.0.0
                    """
                ),
                {
                    "bump": LevelBump.NO_RELEASE,
                    "type": "none",
                    "scope": "",
                    "descriptions": [
                        "set version to 1.0.0",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Patch Type: Build related",
                dedent(
                    """\
                    BLD: move the optimize build steps earlier into the build sequence
                    """
                ),
                {
                    "bump": LevelBump.PATCH,
                    "type": "fix",
                    "scope": "",
                    "descriptions": [
                        "move the optimize build steps earlier into the build sequence",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Patch Type: Bug fix",
                dedent(
                    """\
                    BUG: Fix invalid default bracket selection in _bracket_minimum (#20563)
                    """
                ),
                {
                    "bump": LevelBump.PATCH,
                    "type": "fix",
                    "scope": "",
                    "descriptions": [
                        "Fix invalid default bracket selection in _bracket_minimum",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "#20563",
                },
            ),
            (
                "Patch Type: Maintenance",
                dedent(
                    """\
                    MAINT: optimize.linprog: fix bug when integrality is a list of all zeros (#20586)

                    This is a bug fix for the linprog function in the optimize module.

                    Closes: #555
                    """
                ),
                {
                    "bump": LevelBump.PATCH,
                    "type": "fix",
                    "scope": "optimize.linprog",
                    "descriptions": [
                        "fix bug when integrality is a list of all zeros",
                        "This is a bug fix for the linprog function in the optimize module.",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": ("#555",),
                    "linked_merge_request": "#20586",
                },
            ),
            (
                "Feature Type: Enhancement",
                dedent(
                    """\
                    ENH: stats.ttest_1samp: add array-API support (#20545)

                    Closes: #1444
                    """
                ),
                {
                    "bump": LevelBump.MINOR,
                    "type": "feature",
                    "scope": "stats.ttest_1samp",
                    "descriptions": [
                        "add array-API support",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": ("#1444",),
                    "linked_merge_request": "#20545",
                },
            ),
            # (
            #     NOT CURRENTLY SUPPORTED
            #     "Feature Type: Revert",
            #     dedent(
            #         """\
            #         REV: revert "ENH: add new feature (#20545)"
            #         This reverts commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb.
            #         """
            #     ),
            #     {
            #         "bump": LevelBump.MINOR,
            #         "type": "other",
            #         "scope": "",
            #         "descriptions": [
            #             'revert "ENH: add new feature (#20545)"',
            #             "This reverts commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb.",
            #         ],
            #         "breaking_descriptions": [],
            #         "linked_issues": (),
            #         "linked_merge_request": "",
            #     },
            # ),
            (
                "Feature Type: FEAT",
                dedent(
                    """\
                    FEAT: add new feature (#20545)
                    """
                ),
                {
                    "bump": LevelBump.MINOR,
                    "type": "feature",
                    "scope": "",
                    "descriptions": [
                        "add new feature",
                    ],
                    "breaking_descriptions": [],
                    "linked_issues": (),
                    "linked_merge_request": "#20545",
                },
            ),
            (
                "Breaking Type: API",
                dedent(
                    """\
                    API: dropped support for Python 3.7

                    Users of Python 3.7 should use version 1.0.0 or try to upgrade to Python 3.8
                    or later to continue using this package.
                    """
                ),
                {
                    "bump": LevelBump.MAJOR,
                    "type": "breaking",
                    "scope": "",
                    "descriptions": [
                        "dropped support for Python 3.7",
                    ],
                    "breaking_descriptions": [
                        "Users of Python 3.7 should use version 1.0.0 or try to upgrade to Python 3.8 or later to continue using this package.",
                    ],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
            (
                "Breaking Type: Deprecate",
                dedent(
                    """\
                    DEP: deprecated the limprog function

                    The linprog function is deprecated and will be removed in a future release.
                    Use the new linprog2 function instead.
                    """
                ),
                {
                    "bump": LevelBump.MAJOR,
                    "type": "breaking",
                    "scope": "",
                    "descriptions": [
                        "deprecated the limprog function",
                    ],
                    "breaking_descriptions": [
                        "The linprog function is deprecated and will be removed in a future release. Use the new linprog2 function instead.",
                    ],
                    "linked_issues": (),
                    "linked_merge_request": "",
                },
            ),
        ]
    ],
)
def test_scipy_parser_parses_commit_message(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: dict | None,
):
    # Setup: Enable squash commit parsing
    parser = ScipyCommitParser(
        options=ScipyParserOptions(
            **{
                **default_scipy_parser.options.__dict__,
                "parse_squash_commits": False,
            }
        )
    )

    # Build the commit object and parse it
    the_commit = make_commit_obj(commit_message)
    parsed_results = parser.parse(the_commit)

    # Validate the results
    assert isinstance(parsed_results, Iterable)
    assert 1 == len(
        parsed_results
    ), f"Expected 1 parsed result, but got {len(parsed_results)}"

    result = next(iter(parsed_results))

    if expected_commit_details is None:
        assert isinstance(result, ParseError)
        return

    assert isinstance(result, ParsedCommit)
    # Required
    assert expected_commit_details["bump"] == result.bump
    assert expected_commit_details["type"] == result.type
    # Optional
    assert expected_commit_details.get("scope", "") == result.scope
    # TODO: v11 change to tuples
    assert expected_commit_details.get("descriptions", []) == result.descriptions
    assert (
        expected_commit_details.get("breaking_descriptions", [])
        == result.breaking_descriptions
    )
    assert expected_commit_details.get("linked_issues", ()) == result.linked_issues
    assert (
        expected_commit_details.get("linked_merge_request", "")
        == result.linked_merge_request
    )


@pytest.mark.parametrize(
    "message, subject, merge_request_number",
    [
        # GitHub, Gitea style
        (
            "ENH: add new feature (#123)",
            "add new feature",
            "#123",
        ),
        # GitLab style
        (
            "BUG: fix regex in parser (!456)",
            "fix regex in parser",
            "!456",
        ),
        # BitBucket style
        (
            "ENH: add new feature (pull request #123)",
            "add new feature",
            "#123",
        ),
        # Both a linked merge request and an issue footer (should return the linked merge request)
        ("DEP: add dependency (#123)\n\nCloses: #400", "add dependency", "#123"),
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
    parsed_results = default_scipy_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert merge_request_number == result.linked_merge_request
    assert subject == result.descriptions[0]


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

                    BUG: release-config: some commit subject

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
                        "type": "fix",
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

                    BUG:release-config: some commit subject

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>

                    ENH: implemented searching gizmos by keyword

                    DOC: parser: add new parser pattern

                    API:cli: changed option name

                    A breaking change description

                    Closes: #555

                    invalid non-conventional formatted commit
                    """
                ),
                [
                    None,
                    {
                        "bump": LevelBump.PATCH,
                        "type": "fix",
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
                        "type": "feature",
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
                        "type": "breaking",
                        "scope": "cli",
                        "descriptions": [
                            "changed option name",
                        ],
                        "breaking_descriptions": [
                            "A breaking change description",
                            # This is a bit unusual but its because there is no identifier that will
                            # identify this as a separate commit so it gets included in the previous commit
                            "invalid non-conventional formatted commit",
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
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ScipyCommitParser(
        options=ScipyParserOptions(
            **{
                **default_scipy_parser.options.__dict__,
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

                        BUG: release-config: some commit subject

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
                        "type": "fix",
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

                        BUG: release-config: some commit subject

                        An additional description

                        Second paragraph with multiple lines
                        that will be condensed

                        Resolves: #12
                        Signed-off-by: author <author@not-an-email.com>

                    commit 1f34769bf8352131ad6f4879b8c47becf3c7aa69
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        ENH: implemented searching gizmos by keyword

                    commit b2334a64a11ef745a17a2a4034f651e08e8c45a6
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        DOC: parser: add new parser pattern

                    commit 5f0292fb5a88c3a46e4a02bec35b85f5228e8e51
                    Author: author <author@not-an-email.com>
                    Date:   Sat Jan 18 10:13:53 2025 +0000

                        API:cli: changed option name

                        A breaking change description

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
                        "type": "fix",
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
                        "type": "feature",
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
                        "type": "breaking",
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
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ScipyCommitParser(
        options=ScipyParserOptions(
            **{
                **default_scipy_parser.options.__dict__,
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
                    BUG: release-config: some commit subject (#10)

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
                        "type": "fix",
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
                    BUG: release-config: some commit subject (#10)

                    An additional description

                    Second paragraph with multiple lines
                    that will be condensed

                    Resolves: #12
                    Signed-off-by: author <author@not-an-email.com>

                    * ENH: implemented searching gizmos by keyword

                    * DOC: parser: add new parser pattern

                    * API:cli: changed option name

                      A breaking change description

                      Closes: #555

                    * invalid non-conventional formatted commit
                    """
                ),
                [
                    {
                        "bump": LevelBump.PATCH,
                        "type": "fix",
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
                        "type": "feature",
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
                        "type": "breaking",
                        "scope": "cli",
                        "descriptions": [
                            "changed option name",
                        ],
                        "breaking_descriptions": [
                            "A breaking change description",
                            # This is a bit unusual but its because there is no identifier that will
                            # identify this as a separate commit so it gets included in the previous commit
                            "* invalid non-conventional formatted commit",
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
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    commit_message: str,
    expected_commit_details: Sequence[dict | None],
):
    # Setup: Enable squash commit parsing
    parser = ScipyCommitParser(
        options=ScipyParserOptions(
            **{
                **default_scipy_parser.options.__dict__,
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
    "message, linked_issues",
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
                f"ENH: parser: add magic parser\n\n{footer}",
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
                f"ENH: parser: add magic parser\n\n{footer}",
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
            "ENH: parser: add magic parser (#123)\n\nCloses: #555",
            ["#555"],
        ),
        # Does not grab an issue when there is only a GitHub PR reference in the subject
        ("ENH: parser: add magic parser (#123)", []),
        # Does not grab an issue when there is only a Bitbucket PR reference in the subject
        ("ENH: parser: add magic parser (pull request #123)", []),
    ],
)
def test_parser_return_linked_issues_from_commit_message(
    default_scipy_parser: ScipyCommitParser,
    message: str,
    linked_issues: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_scipy_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

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
                    BUG:parser: fix regex in scipy parser

                    NOTICE: This is a notice
                    """
                ),
                ["This is a notice"],
            ),
            (
                "multiline notice",
                dedent(
                    """\
                    BUG:parser: fix regex in scipy parser

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
                    BUG:parser: fix regex in scipy parser

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
                    BUG:parser: fix regex in scipy parser

                    This is a breaking change

                    NOTICE: This is a notice
                    """
                ),
                ["This is a notice"],
            ),
        ]
    ],
)
def test_parser_return_release_notices_from_commit_message(
    default_scipy_parser: ScipyCommitParser,
    message: str,
    notices: Sequence[str],
    make_commit_obj: MakeCommitObjFn,
):
    parsed_results = default_scipy_parser.parse(make_commit_obj(message))

    assert isinstance(parsed_results, Iterable)
    assert len(parsed_results) == 1

    result = next(iter(parsed_results))
    assert isinstance(result, ParsedCommit)
    assert tuple(notices) == result.release_notices

    full_description = str.join("\n\n", result.descriptions)
    full_notice = str.join("\n\n", result.release_notices)
    assert full_notice not in full_description


def test_parser_ignore_merge_commit(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
):
    # Setup: Enable parsing of linked issues
    parser = ScipyCommitParser(
        options=ScipyParserOptions(
            **{
                **default_scipy_parser.options.__dict__,
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
