import mock
import pytest

from semantic_release.history.logs import generate_changelog

from . import *


def test_should_generate_necessary_sections():
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **k: ALL_KINDS_OF_COMMIT_MESSAGES + [MAJOR2, UNKNOWN_STYLE],
    ):
        changelog = generate_changelog("0.0.0")
        assert len(changelog["feature"]) > 0
        assert len(changelog["fix"]) > 0
        assert len(changelog["breaking"]) > 0
        assert "documentation" not in changelog


def test_should_include_hash_in_section_contents():
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **k: ALL_KINDS_OF_COMMIT_MESSAGES,
    ):
        changelog = generate_changelog("0.0.0")
        assert changelog["breaking"][0][0] == MAJOR[0]
        assert changelog["feature"][0][0] == MINOR[0]
        assert changelog["fix"][0][0] == PATCH[0]


def test_should_only_read_until_given_version():
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **k: MAJOR_LAST_RELEASE_MINOR_AFTER,
    ):
        changelog = generate_changelog("1.1.0")
        assert len(changelog["breaking"]) == 0
        assert len(changelog["feature"]) > 0
        assert "fix" not in changelog
        assert "documentation" not in changelog


@pytest.mark.parametrize(
    "commit,expected_description",
    [
        (MAJOR, "Uses super-feature as default instead of dull-feature."),
        (MAJOR2, "Uses super-feature as default instead of dull-feature."),
        (
            MAJOR_MENTIONING_1_0_0,
            "Uses super-feature as default instead of dull-feature from v1.0.0.",
        ),
        (MAJOR_EXCL_WITH_FOOTER, "Another feature, another breaking change"),
        (MAJOR_EXCL_NOT_FOOTER, "Fix a big bug that everyone exploited"),
    ],
)
def test_should_get_right_breaking_description(commit, expected_description):
    with mock.patch(
        "semantic_release.history.logs.get_commit_log", lambda *a, **kw: [commit],
    ):
        changelog = generate_changelog("0.0.0")
        assert changelog["breaking"][0][1] == expected_description


def test_should_get_multiple_breaking_descriptions():
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **kw: [MAJOR_MULTIPLE_FOOTERS],
    ):
        changelog = generate_changelog("0.0.0")
        assert len(changelog["breaking"]) == 2
        assert changelog["breaking"][0][1] == "Breaking change 1"
        assert changelog["breaking"][1][1] == "Breaking change 2"


def test_messages_are_capitalized():
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **k: [("23", "fix(x): abCD")],
    ):
        changelog = generate_changelog("0.0.0")
        assert changelog["fix"][0][1] == "AbCD"
