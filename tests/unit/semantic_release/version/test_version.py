import operator
import random

import pytest

from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidVersion
from semantic_release.version.version import Version

random.seed(0)

EXAMPLE_VERSION_STRINGS = [
    "1.0.0",
    "0.1.0",
    "0.0.1",
    "1.2.3",
    "0.2.4",
    "2.6.15",
    "13.0.0",
    "4.26.3",
    "1.0.0-rc.1",
    "4.26.0-beta.3",
    "5.3.1+local.123456",
    "9.22.0-alpha.4+build.9999",
]


@pytest.mark.parametrize(
    "version_parts",
    # Major, minor, patch, prerelease_token, prerelease_revision, build_metadata
    [
        (1, 0, 0, "rc", None, ""),
        (0, 1, 0, "rc", None, ""),
        (0, 0, 1, "rc", None, ""),
        (1, 2, 3, "rc", None, ""),
        (0, 2, 4, "rc", None, ""),
        (2, 6, 15, "rc", None, ""),
        (13, 0, 0, "rc", None, ""),
        (4, 26, 3, "rc", None, ""),
        (1, 0, 0, "rc", 1, ""),
        (4, 26, 3, "beta", 3, ""),
        (5, 3, 1, "rc", None, "local.123456"),
        (9, 22, 0, "alpha", 4, "build.9999"),
        (17, 0, 3, "custom-token", 12, ""),
        (17, 0, 3, "custom-token-3-6-9", 12, ""),
        (17, 0, 3, "custom-token", 12, "build.9999"),
    ],
)
def test_version_parse_succeeds(version_parts):
    full = f"{version_parts[0]}.{version_parts[1]}.{version_parts[2]}"
    prerelease = f"-{version_parts[3]}.{version_parts[4]}" if version_parts[4] else ""
    build_metadata = f"+{version_parts[5]}" if version_parts[5] else ""
    version_str = f"{full}{prerelease}{build_metadata}"

    version = Version.parse(version_str)
    assert version.major == version_parts[0]
    assert version.minor == version_parts[1]
    assert version.patch == version_parts[2]
    assert version.prerelease_token == version_parts[3]
    assert version.prerelease_revision == version_parts[4]
    assert version.build_metadata == version_parts[5]
    assert str(version) == version_str


@pytest.mark.parametrize(
    "bad_version",
    [
        "v1.2.3",
        "2.3",
        "2.1.dev0",
        "2.1.4.post5",
        "alpha-1.2.3",
        "17.0.3-custom_token.12",
        "9",
        "4.1.2!-major",
        "%.*.?",
        "M2.m3.p1",
    ],
)
def test_version_parse_fails(bad_version):
    with pytest.raises(InvalidVersion, match=f"{bad_version!r}"):
        Version.parse(bad_version)


@pytest.fixture(params=EXAMPLE_VERSION_STRINGS)
def a_version(request):
    return Version.parse(request.param)


@pytest.mark.parametrize(
    "bad_format", ["non_unique_format", "case_sensitive_{Version}", "typo_{versione}"]
)
def test_tag_format_must_contain_version_field(a_version, bad_format):
    with pytest.raises(ValueError, match=f"Invalid tag_format {bad_format!r}"):
        a_version.tag_format = bad_format


@pytest.mark.parametrize(
    "tag_format",
    [
        "v{version}",
        "dev-{version}",
        "release-_-{version}",
        "{version}-final",
        "{version}-demo-{version}",
    ],
)
def test_change_tag_format_updates_as_tag_method(a_version, tag_format):
    a_version.tag_format = tag_format
    assert a_version.as_tag() == tag_format.format(version=str(a_version))


@pytest.mark.parametrize(
    "version_str, is_prerelease",
    [
        ("1.0.0", False),
        ("14.33.10", False),
        ("2.1.1-rc.1", True),
        ("65.1.2-alpha.4", True),
        ("17.0.3-custom-token.12", True),
        ("17.0.3-custom-token.12+20220101000000", True),
        ("4.2.4+zzzz9000", False),
    ],
)
def test_version_prerelease(version_str, is_prerelease):
    assert Version.parse(version_str).is_prerelease == is_prerelease


def test_version_eq_succeeds(a_version):
    assert a_version == a_version
    assert a_version == str(a_version)


@pytest.mark.parametrize(
    "lower_version, upper_version",
    [
        ("1.0.0", "1.0.1"),
        ("1.0.0", "1.1.0"),
        ("1.0.0", "1.1.1"),
        ("1.0.0", "2.0.0"),
        ("1.0.0-rc.1", "1.0.0"),
        ("1.0.0-rc.1", "1.0.0-rc.2"),
        ("1.0.0-alpha.1", "1.0.1-beta.1"),
        ("1.0.1", "2.0.0-rc.1"),
    ],
)
@pytest.mark.parametrize(
    "op",
    [
        operator.lt,
        operator.le,
        operator.ne,
        lambda left, right: left < right,
        lambda left, right: left <= right,
        lambda left, right: left != right,
    ],
)
def test_version_comparator_succeeds(lower_version, upper_version, op):
    left = Version.parse(lower_version)
    right = Version.parse(upper_version)
    # Test both on Version $op string and on Version $op Version
    assert op(left, right)
    assert op(left, str(right))


@pytest.mark.parametrize(
    "bad_input",
    [
        5,
        "foo-4.22",
        ["a", list, "of", 5, ("things",)],
        (1, 2, 3),
        {"foo": 12},
        "v2.3.4",
    ],
)
@pytest.mark.parametrize(
    "op",
    [
        operator.lt,
        operator.le,
        operator.gt,
        operator.ge,
    ],
)
def test_version_comparator_typeerror(bad_input, op):
    with pytest.raises(TypeError):
        op(Version.parse("1.4.5"), bad_input)


def test_version_equality(a_version):
    assert a_version == Version.parse(str(a_version))


@pytest.mark.parametrize(
    "left, right", [("1.2.3+local.3", "1.2.3"), ("2.1.1-rc.1+build.7777", "2.1.1-rc.1")]
)
def test_version_equality_when_build_metadata_lost(left, right):
    assert Version.parse(left) == Version.parse(right)


@pytest.mark.parametrize(
    "lower_version, upper_version, level",
    [
        ("1.0.0", "1.0.1", LevelBump.PATCH),
        ("1.0.0", "1.1.0", LevelBump.MINOR),
        ("1.0.0", "1.1.1", LevelBump.MINOR),
        ("1.0.0", "2.0.0", LevelBump.MAJOR),
        ("1.0.0-rc.1", "1.0.0", LevelBump.PRERELEASE_REVISION),
        ("1.0.1", "1.1.0-rc.1", LevelBump.MINOR),
        ("1.0.0-rc.1", "1.0.0-rc.2", LevelBump.PRERELEASE_REVISION),
        ("1.0.0-alpha.1", "1.0.1-beta.1", LevelBump.PATCH),
        ("1.0.1", "2.0.0-rc.1", LevelBump.MAJOR),
    ],
)
def test_version_difference(lower_version, upper_version, level):
    left = Version.parse(lower_version)
    right = Version.parse(upper_version)
    assert (left - right) is level
    assert (right - left) is level


@pytest.mark.parametrize(
    "bad_input",
    [
        5,
        "foo-4.22",
        ["a", list, "of", 5, ("things",)],
        (1, 2, 3),
        {"foo": 12},
        "v2.3.4",
    ],
)
def test_unimplemented_version_diff(bad_input):
    with pytest.raises(TypeError, match=r"unsupported operand type"):
        Version.parse("1.2.3") - bad_input


@pytest.mark.parametrize(
    "current_version, prerelease_token, expected_prerelease_version",
    [
        ("1.2.3", "rc", "1.2.3-rc.1"),
        ("1.1.1-rc.2", "rc", "1.1.1-rc.2"),
        ("2.0.0", "beta", "2.0.0-beta.1"),
        ("2.0.0-beta.1", "beta", "2.0.0-beta.1"),
    ],
)
def test_version_to_prerelease_defaults(
    current_version, prerelease_token, expected_prerelease_version
):
    assert Version.parse(current_version).to_prerelease(
        token=prerelease_token
    ) == Version.parse(expected_prerelease_version)


@pytest.mark.parametrize(
    "current_version, prerelease_token, revision, expected_prerelease_version",
    [
        ("1.2.3", "rc", 3, "1.2.3-rc.3"),
        ("1.1.1-rc.1", "rc", 3, "1.1.1-rc.3"),
        ("2.0.0", "beta", None, "2.0.0-beta.1"),
        ("2.0.0-beta.1", "beta", 4, "2.0.0-beta.4"),
    ],
)
def test_version_to_prerelease_with_params(
    current_version, prerelease_token, revision, expected_prerelease_version
):
    assert Version.parse(current_version).to_prerelease(
        token=prerelease_token, revision=revision
    ) == Version.parse(expected_prerelease_version)


@pytest.mark.parametrize(
    "current_version, expected_final_version",
    [
        ("1.2.3-rc.1", "1.2.3"),
        ("1.2.3", "1.2.3"),
        ("1.1.1-rc.2", "1.1.1"),
        ("2.0.0-beta.1", "2.0.0"),
        ("2.27.0", "2.27.0"),
    ],
)
def test_version_finalize_version(current_version, expected_final_version):
    v1 = Version.parse(current_version)
    assert v1.finalize_version() == Version.parse(
        expected_final_version, prerelease_token=v1.prerelease_token
    )


@pytest.mark.parametrize(
    "current_version, level, new_version",
    [
        ("1.2.3", LevelBump.NO_RELEASE, "1.2.3"),
        ("1.2.3", LevelBump.PRERELEASE_REVISION, "1.2.3-rc.1"),
        ("1.2.3", LevelBump.PATCH, "1.2.4"),
        ("1.2.3", LevelBump.MINOR, "1.3.0"),
        ("1.2.3", LevelBump.MAJOR, "2.0.0"),
        ("1.2.3-rc.1", LevelBump.NO_RELEASE, "1.2.3-rc.1"),
        ("1.2.3-rc.1", LevelBump.PRERELEASE_REVISION, "1.2.3-rc.2"),
        ("1.2.3-rc.1", LevelBump.PATCH, "1.2.4-rc.1"),
        ("1.2.3-rc.1", LevelBump.MINOR, "1.3.0-rc.1"),
        ("1.2.3-rc.1", LevelBump.MAJOR, "2.0.0-rc.1"),
    ],
)
def test_version_bump_succeeds(current_version, level, new_version):
    cv = Version.parse(current_version)
    nv = cv.bump(level)
    assert nv == Version.parse(new_version)
    assert cv + level == Version.parse(new_version)


@pytest.mark.parametrize("bad_level", [5, "patch", {"major": True}, [1, 1, 0, 0, 1], 1])
def test_version_bump_typeerror(bad_level):
    with pytest.raises(TypeError):
        Version.parse("1.2.3").bump(bad_level)


def test_version_hashable(a_version):
    _ = {a_version: 4}
    assert True


# NOTE: this might be a really good first candidate for hypothesis
@pytest.mark.parametrize(
    "major, minor, patch, prerelease_revision",
    [tuple(random.choice(range(1, 100)) for _ in range(4)) for _ in range(10)],
)
def test_prerelease_always_less_than_full(major, minor, patch, prerelease_revision):
    full = Version(major, minor, patch)
    pre = Version(major, minor, patch, prerelease_revision=prerelease_revision)
    assert pre < full
