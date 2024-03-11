import pytest
from git import Commit, Repo, TagReference

from semantic_release.enums import LevelBump
from semantic_release.version.algorithm import (
    _bfs_for_latest_version_in_history,
    _increment_version,
    tags_and_versions,
)
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version


def test_bfs_for_latest_version_in_history():
    # Setup fake git graph
    """
    * merge commit 6 (start)
    |\
    | * commit 5
    | * commit 4
    |/
    * commit 3
    * commit 2
    * commit 1
    * v1.0.0
    """
    repo = Repo()
    expected_version = Version.parse("1.0.0")
    v1_commit = Commit(repo, binsha=b"0" * 20)

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

    # Execute
    actual = _bfs_for_latest_version_in_history(
        start_commit,
        [
            (v1_tag, expected_version),
        ],
    )

    # Verify
    assert expected_version == actual


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
def test_sorted_repo_tags_and_versions(tags, sorted_tags):
    repo = Repo()
    translator = VersionTranslator()
    tagrefs = [repo.tag(tag) for tag in tags]
    actual = [t.name for t, _ in tags_and_versions(tagrefs, translator)]
    assert actual == sorted_tags


@pytest.mark.parametrize(
    "tag_format, invalid_tags, valid_tags",
    [
        (
            "v{version}",
            ("test-v1.1.0", "v1.1.0-test-test"),
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
            "v{version}",
            ("0.3", "0.4"),
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
            r"(\w+--)?v{version}",
            ("v1.1.0-test-test", "test_v1.1.0"),
            [
                "v1.0.0-rc.1",
                "test--v1.1.0",
                "v1.0.0-beta.2",
                "v1.0.0-beta.11",
                "v1.0.0-alpha.1",
                "v1.0.0-alpha.beta.1",
                "v1.0.0",
            ],
        ),
        (
            r"(?P<type>feature|fix)/v{version}--(?P<env>dev|stg|prod)",
            ("v1.1.0--test", "test_v1.1.0", "docs/v1.2.0--dev"),
            [
                "feature/v1.0.0-rc.1--dev",
                "fix/v1.1.0--stg",
                "feature/v1.0.0-beta.2--stg",
                "fix/v1.0.0-beta.11--dev",
                "fix/v1.0.0-alpha.1--dev",
                "feature/v1.0.0-alpha.beta.1--dev",
                "feature/v1.0.0--prod",
            ],
        ),
    ],
)
def test_tags_and_versions_ignores_invalid_tags_as_versions(
    tag_format, invalid_tags, valid_tags
):
    repo = Repo()
    translator = VersionTranslator(tag_format=tag_format)
    tagrefs = [repo.tag(tag) for tag in (*valid_tags, *invalid_tags)]
    actual = [t.name for t, _ in tags_and_versions(tagrefs, translator)]
    assert set(actual) == set(valid_tags)


@pytest.mark.parametrize(
    "latest_version, latest_full_version, latest_full_version_in_history, level_bump, "
    "prerelease, prerelease_token, expected_version",
    [
        # NOTE: level_bump != LevelBump.NO_RELEASE, we return early in the
        # algorithm to discount this case
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.PRERELEASE_REVISION,
            False,
            "rc",
            "1.0.0-rc.1",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
            "1.0.0-rc.1",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.PATCH,
            False,
            "rc",
            "1.0.1",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.PATCH,
            True,
            "rc",
            "1.0.1-rc.1",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.MINOR,
            False,
            "rc",
            "1.1.0",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.MINOR,
            True,
            "rc",
            "1.1.0-rc.1",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.MAJOR,
            False,
            "rc",
            "2.0.0",
        ),
        (
            "1.0.0",
            "1.0.0",
            "1.0.0",
            LevelBump.MAJOR,
            True,
            "rc",
            "2.0.0-rc.1",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.PATCH,
            False,
            "rc",
            "1.2.4",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.PATCH,
            True,
            "rc",
            "1.2.4-rc.2",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.MINOR,
            False,
            "rc",
            "1.3.0",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.MINOR,
            True,
            "rc",
            "1.3.0-rc.1",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.MAJOR,
            False,
            "rc",
            "2.0.0",
        ),
        (
            "1.2.4-rc.1",
            "1.2.0",
            "1.2.3",
            LevelBump.MAJOR,
            True,
            "rc",
            "2.0.0-rc.1",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.PATCH,
            False,
            "rc",
            "2.0.0",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.PATCH,
            True,
            "rc",
            "2.0.0-rc.2",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.MINOR,
            False,
            "rc",
            "2.0.0",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.MINOR,
            True,
            "rc",
            "2.0.0-rc.2",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.MAJOR,
            False,
            "rc",
            "2.0.0",
        ),
        (
            "2.0.0-rc.1",
            "1.22.0",
            "1.19.3",
            LevelBump.MAJOR,
            True,
            "rc",
            "2.0.0-rc.2",
        ),
    ],
)
def test_increment_version_no_major_on_zero(
    latest_version: str,
    latest_full_version: str,
    latest_full_version_in_history: str,
    level_bump: LevelBump,
    prerelease: bool,
    prerelease_token: str,
    expected_version: str,
):
    actual = _increment_version(
        latest_version=Version.parse(latest_version),
        latest_full_version=Version.parse(latest_full_version),
        latest_full_version_in_history=Version.parse(latest_full_version_in_history),
        level_bump=level_bump,
        prerelease=prerelease,
        prerelease_token=prerelease_token,
        major_on_zero=False,
        allow_zero_version=True,
    )
    assert expected_version == str(actual)
