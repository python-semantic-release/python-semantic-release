from __future__ import annotations

from re import compile as regexp
from typing import TYPE_CHECKING

import pytest

from semantic_release.commit_parser.scipy import tag_to_section
from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from semantic_release.commit_parser.scipy import ScipyCommitParser

    from tests.conftest import MakeCommitObjFn


unwordwrap = regexp(r"((?<!-)\n(?![\s*-]))")


def test_valid_scipy_parsed_chore_commits(
    default_scipy_parser: ScipyCommitParser,
    make_commit_obj: MakeCommitObjFn,
    scipy_chore_commit_parts: list[list[str]],
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
        expected_brk_desc = []

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
    scipy_patch_commit_parts: list[list[str]],
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
        expected_brk_desc = []

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
    scipy_minor_commit_parts: list[list[str]],
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
        expected_brk_desc = []

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
    scipy_major_commit_parts: list[list[str]],
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
        expected_brk_desc = [
            block.removeprefix("BREAKING CHANGE: ")
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
