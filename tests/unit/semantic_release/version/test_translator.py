import pytest

from semantic_release.const import SEMVER_REGEX
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

from tests.const import (
    A_FULL_VERSION_STRING,
    A_FULL_VERSION_STRING_WITH_BUILD_METADATA,
    A_PRERELEASE_VERSION_STRING,
)


@pytest.fixture
def a_full_version() -> Version:
    return Version.parse(A_FULL_VERSION_STRING)


@pytest.fixture
def a_prerelease_version() -> Version:
    return Version.parse(A_PRERELEASE_VERSION_STRING)


@pytest.fixture
def a_full_version_with_build_metadata() -> Version:
    return Version.parse(A_FULL_VERSION_STRING_WITH_BUILD_METADATA)


@pytest.mark.parametrize(
    "version_string",
    [
        A_FULL_VERSION_STRING,
        A_PRERELEASE_VERSION_STRING,
        A_FULL_VERSION_STRING_WITH_BUILD_METADATA,
        "3.2.3-alpha.dev3+local.12345",  # Pretty much as complex an example as there is
    ],
)
def test_succeeds_semver_regex_match(version_string: str):
    assert SEMVER_REGEX.fullmatch(
        version_string
    ), "a valid semantic version was not matched"


@pytest.mark.parametrize(
    "invalid_version_str",
    ["v1.2.3", "2.1", "3.1.1..3", "4.1.1.dev3"],  # PEP440 version
)
def test_invalid_semver_not_matched(invalid_version_str: str):
    assert SEMVER_REGEX.fullmatch(invalid_version_str) is None


@pytest.mark.parametrize("fmt", ["version", "{versioN}", "v{major}.{minor}.{patch}"])
def test_invalid_tag_format(fmt: str):
    with pytest.raises(ValueError) as err:
        VersionTranslator(tag_format=fmt)
    assert all(("tag_format" in str(err), "version" in str(err), fmt in str(err)))


@pytest.mark.parametrize(
    "version_string",
    [
        A_FULL_VERSION_STRING,
        A_PRERELEASE_VERSION_STRING,
        A_FULL_VERSION_STRING_WITH_BUILD_METADATA,
    ],
)
@pytest.mark.parametrize(
    "tag_format, prerelease_token",
    [
        ("v{version}", "dev"),
        ("v{version}", "alpha"),
        ("special-tagging-scheme-{version}", "rc"),
    ],
)
def test_translator_converts_versions_with_default_formatting_rules(
    version_string: str, tag_format: str, prerelease_token: str
):
    translator = VersionTranslator(
        tag_format=tag_format, prerelease_token=prerelease_token
    )

    expected_version_obj = Version.parse(
        version_string, prerelease_token=translator.prerelease_token
    )
    expected_tag = tag_format.format(version=version_string)
    actual_version_obj = translator.from_string(version_string)
    actual_tag = translator.str_to_tag(version_string)

    # These are important assumptions for formatting into source files/tags/etc
    assert version_string == str(actual_version_obj)
    assert expected_version_obj == actual_version_obj
    assert expected_tag == actual_tag
    assert expected_version_obj == (translator.from_tag(expected_tag) or "")
    assert version_string == str(translator.from_tag(actual_tag) or "")
