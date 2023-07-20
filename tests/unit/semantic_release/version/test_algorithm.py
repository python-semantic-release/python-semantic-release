import pytest
from git import Repo

from semantic_release.enums import LevelBump
from semantic_release.version.algorithm import _increment_version, tags_and_versions
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version


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
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.PRERELEASE_REVISION,
            False,
            "rc",
            Version.parse("1.0.0-rc.1"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.PRERELEASE_REVISION,
            True,
            "rc",
            Version.parse("1.0.0-rc.1"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.PATCH,
            False,
            "rc",
            Version.parse("1.0.1"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.PATCH,
            True,
            "rc",
            Version.parse("1.0.1-rc.1"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.MINOR,
            False,
            "rc",
            Version.parse("1.1.0"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.MINOR,
            True,
            "rc",
            Version.parse("1.1.0-rc.1"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.MAJOR,
            False,
            "rc",
            Version.parse("2.0.0"),
        ),
        (
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            Version.parse("1.0.0"),
            LevelBump.MAJOR,
            True,
            "rc",
            Version.parse("2.0.0-rc.1"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.PATCH,
            False,
            "rc",
            Version.parse("1.2.4"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.PATCH,
            True,
            "rc",
            Version.parse("1.2.4-rc.2"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.MINOR,
            False,
            "rc",
            Version.parse("1.3.0"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.MINOR,
            True,
            "rc",
            Version.parse("1.3.0-rc.1"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.MAJOR,
            False,
            "rc",
            Version.parse("2.0.0"),
        ),
        (
            Version.parse("1.2.4-rc.1"),
            Version.parse("1.2.0"),
            Version.parse("1.2.3"),
            LevelBump.MAJOR,
            True,
            "rc",
            Version.parse("2.0.0-rc.1"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.PATCH,
            False,
            "rc",
            Version.parse("2.0.0"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.PATCH,
            True,
            "rc",
            Version.parse("2.0.0-rc.2"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.MINOR,
            False,
            "rc",
            Version.parse("2.0.0"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.MINOR,
            True,
            "rc",
            Version.parse("2.0.0-rc.2"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.MAJOR,
            False,
            "rc",
            Version.parse("2.0.0"),
        ),
        (
            Version.parse("2.0.0-rc.1"),
            Version.parse("1.22.0"),
            Version.parse("1.19.3"),
            LevelBump.MAJOR,
            True,
            "rc",
            Version.parse("2.0.0-rc.2"),
        ),
    ],
)
def test_increment_version_no_major_on_zero(
    latest_version,
    latest_full_version,
    latest_full_version_in_history,
    level_bump,
    prerelease,
    prerelease_token,
    expected_version,
):
    actual = _increment_version(
        latest_version=latest_version,
        latest_full_version=latest_full_version,
        latest_full_version_in_history=latest_full_version_in_history,
        level_bump=level_bump,
        prerelease=prerelease,
        prerelease_token=prerelease_token,
        major_on_zero=False,
    )
    assert actual == expected_version
