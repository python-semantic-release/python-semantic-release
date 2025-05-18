from __future__ import annotations

from itertools import chain, zip_longest
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from semantic_release.commit_parser.scipy import ScipyCommitParser
from semantic_release.enums import LevelBump

if TYPE_CHECKING:
    from typing import Protocol

    from semantic_release.commit_parser.scipy import ScipyParserOptions

    class FormatScipyCommitFn(Protocol):
        def __call__(
            self, scipy_tag: str, subject: str, body_parts: list[str]
        ) -> str: ...


@pytest.fixture(scope="session")
def format_scipy_commit():
    def _format_scipy_commit(
        scipy_tag: str, subject: str, body_parts: list[str]
    ) -> str:
        body = str.join("\n\n", body_parts)
        return f"{scipy_tag}: {subject}\n\n{body}"

    return _format_scipy_commit


@pytest.fixture(scope="session")
def default_scipy_parser() -> ScipyCommitParser:
    return ScipyCommitParser()


@pytest.fixture(scope="session")
def default_scipy_parser_options(
    default_scipy_parser: ScipyCommitParser,
) -> ScipyParserOptions:
    return default_scipy_parser.get_default_options()


@pytest.fixture(scope="session")
def scipy_chore_commit_types(
    default_scipy_parser_options: ScipyParserOptions,
) -> list[str]:
    return [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v < LevelBump.PATCH
    ]


@pytest.fixture(scope="session")
def scipy_patch_commit_types(
    default_scipy_parser_options: ScipyParserOptions,
) -> list[str]:
    return [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.PATCH
    ]


@pytest.fixture(scope="session")
def scipy_minor_commit_types(
    default_scipy_parser_options: ScipyParserOptions,
) -> list[str]:
    return [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.MINOR
    ]


@pytest.fixture(scope="session")
def scipy_major_commit_types(
    default_scipy_parser_options: ScipyParserOptions,
) -> list[str]:
    return [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.MAJOR
    ]


@pytest.fixture(scope="session")
def scipy_nonparseable_commits() -> list[str]:
    return [
        "Initial Commit",
        "Merge pull request #14447 from AnirudhDagar/rename_ndimage_modules",
    ]


@pytest.fixture(scope="session")
def scipy_chore_subjects(scipy_chore_commit_types: list[str]) -> list[str]:
    subjects = {
        "BENCH": "disable very slow benchmark in optimize_milp.py",
        "DEV": "add unicode check to pre-commit-hook",
        "DOC": "change approx_fprime doctest (#20568)",
        "STY": "fixed ruff & mypy issues",
        "TST": "Skip Cython tests for editable installs",
        "REL": "set version to 1.0.0",
        "TEST": "Add Cython tests for editable installs",
    }
    # Test fixture modification failure prevention
    assert len(subjects.keys()) == len(scipy_chore_commit_types)
    return [subjects[k] for k in scipy_chore_commit_types]


@pytest.fixture(scope="session")
def scipy_patch_subjects(scipy_patch_commit_types: list[str]) -> list[str]:
    subjects = {
        "BLD": "move the optimize build steps earlier into the build sequence",
        "BUG": "Fix invalid default bracket selection in _bracket_minimum (#20563)",
        "MAINT": "optimize.linprog: fix bug when integrality is a list of all zeros (#20586)",
    }
    # Test fixture modification failure prevention
    assert len(subjects.keys()) == len(scipy_patch_commit_types)
    return [subjects[k] for k in scipy_patch_commit_types]


@pytest.fixture(scope="session")
def scipy_minor_subjects(scipy_minor_commit_types: list[str]) -> list[str]:
    subjects = {
        "ENH": "stats.ttest_1samp: add array-API support (#20545)",
        # "REV": "reverted a previous commit",
        "FEAT": "added a new feature",
    }
    # Test fixture modification failure prevention
    assert len(subjects.keys()) == len(scipy_minor_commit_types)
    return [subjects[k] for k in scipy_minor_commit_types]


@pytest.fixture(scope="session")
def scipy_major_subjects(scipy_major_commit_types: list[str]) -> list[str]:
    subjects = {
        "API": "dropped support for python 3.7",
        "DEP": "stats: switch kendalltau to kwarg-only, remove initial_lexsort",
    }
    # Test fixture modification failure prevention
    assert len(subjects.keys()) == len(scipy_major_commit_types)
    return [subjects[k] for k in scipy_major_commit_types]


@pytest.fixture(scope="session")
def scipy_brk_change_commit_bodies() -> list[list[str]]:
    brk_chg_msg = dedent(
        """
        BREAKING CHANGE: a description of what is now different
        with multiple lines
        """
    ).strip()

    one_line_desc = "resolves bug related to windows incompatiblity"

    return [
        # No regular change description
        [brk_chg_msg],
        # regular change description & breaking change message
        [one_line_desc, brk_chg_msg],
        # regular change description & breaking change message with footer
        [one_line_desc, brk_chg_msg, "Resolves: #666"],
    ]


@pytest.fixture(scope="session")
def scipy_nonbrking_commit_bodies() -> list[list[str]]:
    # a GitHub squash merge that preserved PR commit messages (all chore-like)
    github_squash_merge_body = str.join(
        "\n\n",
        [
            "* DOC: import ropy.transform to test for numpy error",
            "* DOC: lower numpy version",
            "* DOC: lower numpy version further",
            "* STY: resolve linting issues",
        ],
    )

    one_block_desc = dedent(
        """
        Bug spotted on Fedora, see https://src.fedoraproject.org/rpms/scipy/pull-request/22
        with an additional multiline description
        """
    ).strip()

    return [
        github_squash_merge_body.split("\n\n"),  # split into blocks
        # empty body
        [],
        [""],
        # formatted body (ie dependabot)
        dedent(
            """
            Bumps [package](https://github.com/namespace/project) from 3.5.3 to 4.1.1.
                - [Release notes](https://github.com/namespace/project/releases)
                - [Changelog](https://github.com/namespace/project/blob/4.x/CHANGES)
                - [Commits](https://github.com/namespace/project/commits/v4.1.1)

            ---
            updated-dependencies:
              - dependency-name: package
                dependency-type: direct:development
                update-type: version-update:semver-major
            """
        )
        .lstrip()
        .split("\n\n"),
        # 1 block description
        one_block_desc.split("\n\n"),
        # keywords
        ["[skip azp] [skip actions]"],
        # Resolving an issue on GitHub
        ["Resolves: #127"],
        [one_block_desc, "Closes: #1024"],
    ]


@pytest.fixture(scope="session")
def scipy_chore_commit_parts(
    scipy_chore_commit_types: list[str],
    scipy_chore_subjects: list[str],
    scipy_nonbrking_commit_bodies: list[list[str]],
) -> list[tuple[str, str, list[str]]]:
    # Test fixture modification failure prevention
    assert len(scipy_chore_commit_types) == len(scipy_chore_subjects)

    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        (commit_type, subject, commit_body_blocks)
        for commit_type, subject in zip(scipy_chore_commit_types, scipy_chore_subjects)
        for commit_body_blocks in scipy_nonbrking_commit_bodies
    ]


@pytest.fixture(scope="session")
def scipy_chore_commits(
    scipy_chore_commit_parts: list[tuple[str, str, list[str]]],
    format_scipy_commit: FormatScipyCommitFn,
) -> list[str]:
    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        format_scipy_commit(commit_type, subject, commit_body)
        for commit_type, subject, commit_body in scipy_chore_commit_parts
    ]


@pytest.fixture(scope="session")
def scipy_patch_commit_parts(
    scipy_patch_commit_types: list[str],
    scipy_patch_subjects: list[str],
    scipy_nonbrking_commit_bodies: list[list[str]],
) -> list[tuple[str, str, list[str]]]:
    # Test fixture modification failure prevention
    assert len(scipy_patch_commit_types) == len(scipy_patch_subjects)

    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        (commit_type, subject, commit_body_blocks)
        for commit_type, subject in zip(scipy_patch_commit_types, scipy_patch_subjects)
        for commit_body_blocks in scipy_nonbrking_commit_bodies
    ]


@pytest.fixture(scope="session")
def scipy_patch_commits(
    scipy_patch_commit_parts: list[tuple[str, str, list[str]]],
    format_scipy_commit: FormatScipyCommitFn,
) -> list[str]:
    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        format_scipy_commit(commit_type, subject, commit_body)
        for commit_type, subject, commit_body in scipy_patch_commit_parts
    ]


@pytest.fixture(scope="session")
def scipy_minor_commit_parts(
    scipy_minor_commit_types: list[str],
    scipy_minor_subjects: list[str],
    scipy_nonbrking_commit_bodies: list[list[str]],
) -> list[tuple[str, str, list[str]]]:
    # Test fixture modification failure prevention
    assert len(scipy_minor_commit_types) == len(scipy_minor_subjects)

    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        (commit_type, subject, commit_body_blocks)
        for commit_type, subject in zip(scipy_minor_commit_types, scipy_minor_subjects)
        for commit_body_blocks in scipy_nonbrking_commit_bodies
    ]


@pytest.fixture(scope="session")
def scipy_minor_commits(
    scipy_minor_commit_parts: list[tuple[str, str, list[str]]],
    format_scipy_commit: FormatScipyCommitFn,
) -> list[str]:
    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        format_scipy_commit(commit_type, subject, commit_body)
        for commit_type, subject, commit_body in scipy_minor_commit_parts
    ]


@pytest.fixture(scope="session")
def scipy_major_commit_parts(
    scipy_major_commit_types: list[str],
    scipy_major_subjects: list[str],
    scipy_brk_change_commit_bodies: list[list[str]],
) -> list[tuple[str, str, list[str]]]:
    # Test fixture modification failure prevention
    assert len(scipy_major_commit_types) == len(scipy_major_subjects)

    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        (commit_type, subject, commit_body_blocks)
        for commit_type, subject in zip(scipy_major_commit_types, scipy_major_subjects)
        for commit_body_blocks in scipy_brk_change_commit_bodies
    ]


@pytest.fixture(scope="session")
def scipy_major_commits(
    scipy_major_commit_parts: list[tuple[str, str, list[str]]],
    format_scipy_commit: FormatScipyCommitFn,
) -> list[str]:
    # build full commit messages with commit type prefix, subject, and body variant
    # for all body variants
    return [
        format_scipy_commit(commit_type, subject, commit_body)
        for commit_type, subject, commit_body in scipy_major_commit_parts
    ]


@pytest.fixture(scope="session")
def scipy_patch_mixed_commits(
    scipy_patch_commits: list[str],
    scipy_chore_commits: list[str],
) -> list[str]:
    return list(
        filter(
            None,
            chain.from_iterable(zip_longest(scipy_patch_commits, scipy_chore_commits)),
        )
    )


@pytest.fixture(scope="session")
def scipy_minor_mixed_commits(
    scipy_minor_commits: list[str],
    scipy_patch_commits: list[str],
    scipy_chore_commits: list[str],
) -> list[str]:
    return list(
        chain.from_iterable(
            zip_longest(
                scipy_minor_commits,
                scipy_patch_commits,
                scipy_chore_commits,
                fillvalue="uninteresting",
            )
        )
    )


@pytest.fixture(scope="session")
def scipy_major_mixed_commits(
    scipy_major_commits: list[str],
    scipy_minor_commits: list[str],
    scipy_patch_commits: list[str],
    scipy_chore_commits: list[str],
) -> list[str]:
    return list(
        filter(
            None,
            chain.from_iterable(
                zip_longest(
                    scipy_major_commits,
                    scipy_minor_commits,
                    scipy_patch_commits,
                    scipy_chore_commits,
                )
            ),
        )
    )
