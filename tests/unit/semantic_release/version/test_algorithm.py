from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest
from git import Commit, Repo, TagReference

from semantic_release.enums import LevelBump
from semantic_release.version.algorithm import (
    _increment_version,
    _traverse_graph_for_commits,
    tags_and_versions,
)
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

from tests.fixtures.repos import repo_w_initial_commit

if TYPE_CHECKING:
    from typing import Sequence


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
def test_traverse_graph_for_commits():
    # Setup fake git graph
    """
    * merge commit 6 (start) [3636363]
    |\
    | * commit 5 [3535353]
    | * commit 4 [3434343]
    |/
    * commit 3 [3333333]
    * commit 2 [3232323]
    * commit 1 [3131313]
    * v1.0.0 [3030303]
    """
    repo = Repo()
    v1_commit = Commit(repo, binsha=b"0" * 20, parents=[])

    class TagReferenceOverride(TagReference):
        commit = v1_commit  # mocking the commit property

    v1_tag = TagReferenceOverride(repo, "refs/tags/v1.0.0", check_path=False)

    trunk = Commit(
        repo,
        binsha=b"3" * 20,
        parents=[
            Commit(
                repo,
                binsha=b"2" * 20,
                parents=[
                    Commit(repo, binsha=b"1" * 20, parents=[v1_commit]),
                ],
            ),
        ],
    )
    start_commit = Commit(
        repo,
        binsha=b"6" * 20,
        parents=[
            trunk,
            Commit(
                repo,
                binsha=b"5" * 20,
                parents=[
                    Commit(repo, binsha=b"4" * 20, parents=[trunk]),
                ],
            ),
        ],
    )

    commit_1 = trunk.parents[0].parents[0]
    commit_2 = trunk.parents[0]
    commit_3 = trunk
    commit_4 = start_commit.parents[1].parents[0]
    commit_5 = start_commit.parents[1]
    commit_6 = start_commit

    expected_commit_order = [
        commit_6.hexsha,
        commit_5.hexsha,
        commit_4.hexsha,
        commit_3.hexsha,
        commit_2.hexsha,
        commit_1.hexsha,
    ]

    # Execute
    with mock.patch.object(
        repo, repo.iter_commits.__name__, return_value=iter([v1_commit])
    ):
        actual_commit_order = [
            commit.hexsha
            for commit in _traverse_graph_for_commits(
                head_commit=start_commit,
                latest_release_tag_str=v1_tag.name,
            )
        ]

    # Verify
    assert expected_commit_order == actual_commit_order


@pytest.mark.parametrize(
    "tags, sorted_tags",
    [
        (
            ["v1.0.0", "v1.1.0", "v1.1.1"],
            ["v1.1.1", "v1.1.0", "v1.0.0"],
        ),
        (
            ["v1.1.0", "v1.0.0", "v1.1.1"],
            ["v1.1.1", "v1.1.0", "v1.0.0"],
        ),
        (
            ["v1.1.1", "v1.1.0", "v1.0.0"],
            ["v1.1.1", "v1.1.0", "v1.0.0"],
        ),
        # Examples from https://semver.org/#spec-item-11 (or inspired, where not all
        # version structures are supported)
        (
            ["v1.0.0", "v2.0.0", "v2.1.1", "v2.1.0"],
            ["v2.1.1", "v2.1.0", "v2.0.0", "v1.0.0"],
        ),
        (
            [
                "v1.0.0-rc.1",
                "v1.0.0-beta.2",
                "v1.0.0-beta.11",
                "v1.0.0-alpha.1",
                "v1.0.0-alpha.beta.1",
                "v1.0.0",
            ],
            [
                "v1.0.0",
                "v1.0.0-rc.1",
                "v1.0.0-beta.11",
                "v1.0.0-beta.2",
                "v1.0.0-alpha.beta.1",
                "v1.0.0-alpha.1",
            ],
        ),
    ],
)
def test_sorted_repo_tags_and_versions(tags: list[str], sorted_tags: list[str]):
    repo = Repo()
    translator = VersionTranslator()
    tagrefs = [repo.tag(tag) for tag in tags]
    actual = [t.name for t, _ in tags_and_versions(tagrefs, translator)]
    assert sorted_tags == actual


@pytest.mark.parametrize(
    "tag_format, invalid_tags, valid_tags",
    [
        pytest.param(
            tag_format,
            invalid_tags,
            valid_tags,
            id=test_id,
        )
        for test_id, tag_format, invalid_tags, valid_tags in [
            (
                "traditional-v-prefixed-versions",
                "v{version}",
                (
                    "0.3",  # no v-prefix
                    "test-v1.1.0",  # extra prefix
                    "v1.1.0-test-test",  # bad suffix
                ),
                [
                    "v1.0.0-rc.1",
                    "v1.0.0-beta.2",
                    "v1.0.0-beta.11",
                    "v1.0.0-alpha.1",
                    "v1.0.0-alpha.beta.1",
                    "v1.0.0",
                ],
            ),
            (
                "monorepo-style-versions",
                "pkg1-v{version}",
                (
                    "0.3",  # no pkg or version prefix
                    "v1.1.0",  # no pkg prefix
                    "pkg1-v1.1.0-test-test",  # bad suffix
                    "pkg2-v1.1.0",  # wrong package prefix
                ),
                [
                    "pkg1-v1.0.0-rc.1",
                    "pkg1-v1.0.0-beta.2",
                    "pkg1-v1.0.0-beta.11",
                    "pkg1-v1.0.0-alpha.1",
                    "pkg1-v1.0.0-alpha.beta.1",
                    "pkg1-v1.0.0",
                ],
            ),
        ]
    ],
)
def test_tags_and_versions_ignores_invalid_tags_as_versions(
    tag_format: str,
    invalid_tags: Sequence[str],
    valid_tags: Sequence[str],
):
    repo = Repo()
    translator = VersionTranslator(tag_format=tag_format)
    tagrefs = [repo.tag(tag) for tag in (*valid_tags, *invalid_tags)]
    actual = [t.name for t, _ in tags_and_versions(tagrefs, translator)]
    assert set(valid_tags) == set(actual)


@pytest.mark.parametrize(
    str.join(
        ", ",
        [
            "latest_version",
            "latest_full_version",
            "level_bump",
            "prerelease",
            "prerelease_token",
            "expected_version",
        ],
    ),
    [
        # NOTE: level_bump != LevelBump.NO_RELEASE, we return early in the
        # algorithm to discount this case
        # NOTE: you can only perform a PRERELEASE_REVISION bump on a previously
        # prerelease version and if you are requesting a prerelease
        (
            "1.0.1-rc.1",
            "1.0.0",
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
            "1.0.1-rc.2",
        ),
        *[
            (
                "1.0.0",
                "1.0.0",
                bump_level,
                prerelease,
                "rc",
                expected_version,
            )
            for bump_level, prerelease, expected_version in [
                (LevelBump.PATCH, False, "1.0.1"),
                (LevelBump.PATCH, True, "1.0.1-rc.1"),
                (LevelBump.MINOR, False, "1.1.0"),
                (LevelBump.MINOR, True, "1.1.0-rc.1"),
                (LevelBump.MAJOR, False, "2.0.0"),
                (LevelBump.MAJOR, True, "2.0.0-rc.1"),
            ]
        ],
        (
            "1.2.4-rc.1",
            "1.2.3",
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
            "1.2.4-rc.2",
        ),
        *[
            (
                "1.2.4-rc.1",
                "1.2.3",
                bump_level,
                prerelease,
                "rc",
                expected_version,
            )
            for bump_level, prerelease, expected_version in [
                (LevelBump.PATCH, False, "1.2.4"),
                (LevelBump.PATCH, True, "1.2.4-rc.2"),
                (LevelBump.MINOR, False, "1.3.0"),
                (LevelBump.MINOR, True, "1.3.0-rc.1"),
                (LevelBump.MAJOR, False, "2.0.0"),
                (LevelBump.MAJOR, True, "2.0.0-rc.1"),
            ]
        ],
        (
            "2.0.0-rc.1",
            "1.19.3",
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
            "2.0.0-rc.2",
        ),
        *[
            (
                "2.0.0-rc.1",
                "1.22.0",
                bump_level,
                prerelease,
                "rc",
                expected_version,
            )
            for bump_level, prerelease, expected_version in [
                (LevelBump.PATCH, False, "2.0.0"),
                (LevelBump.PATCH, True, "2.0.0-rc.2"),
                (LevelBump.MINOR, False, "2.0.0"),
                (LevelBump.MINOR, True, "2.0.0-rc.2"),
                (LevelBump.MAJOR, False, "2.0.0"),
                (LevelBump.MAJOR, True, "2.0.0-rc.2"),
            ]
        ],
    ],
)
def test_increment_version_no_major_on_zero(
    latest_version: str,
    latest_full_version: str,
    level_bump: LevelBump,
    prerelease: bool,
    prerelease_token: str,
    expected_version: str,
):
    actual = _increment_version(
        latest_version=Version.parse(latest_version),
        latest_full_version=Version.parse(latest_full_version),
        level_bump=level_bump,
        prerelease=prerelease,
        prerelease_token=prerelease_token,
        major_on_zero=False,
        allow_zero_version=True,
    )
    assert expected_version == str(actual)


@pytest.mark.parametrize(
    "latest_version, latest_full_version, level_bump, prerelease, prerelease_token",
    [
        # NOTE: level_bump != LevelBump.NO_RELEASE, we return early in the
        # algorithm to discount this case
        # NOTE: you can only perform a PRERELEASE_REVISION bump on a previously
        # prerelease version and if you are requesting a prerelease
        (
            "1.0.0",
            "1.0.0",
            LevelBump.PRERELEASE_REVISION,
            False,
            "rc",
        ),
        (
            "1.0.0",
            "1.0.0",
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
        ),
    ],
)
def test_increment_version_invalid_operation(
    latest_version: str,
    latest_full_version: str,
    level_bump: LevelBump,
    prerelease: bool,
    prerelease_token: str,
):
    with pytest.raises(ValueError):
        _increment_version(
            latest_version=Version.parse(latest_version),
            latest_full_version=Version.parse(latest_full_version),
            level_bump=level_bump,
            prerelease=prerelease,
            prerelease_token=prerelease_token,
            major_on_zero=False,
            allow_zero_version=True,
        )
