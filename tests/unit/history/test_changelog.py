import mock
import pytest

from semantic_release.history.logs import generate_changelog

from .. import wrapped_config_get
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
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **kw: [commit],
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


@pytest.mark.parametrize(
    "commit,commit_type,expected",
    [
        (MAJOR, "feature", "**x:** Add super-feature"),
        (MINOR, "feature", "**x:** Add non-breaking super-feature"),
        (PATCH, "fix", "**x:** Fix bug in super-feature"),
    ],
)
def test_scope_is_included_in_changelog(commit, commit_type, expected):
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **kw: [commit],
    ):
        changelog = generate_changelog("0.0.0")
        assert changelog[commit_type][0][1] == expected


@mock.patch(
    "semantic_release.history.logs.get_commit_log",
    lambda *a, **k: [("24", "fix: Fix another bug")],
)
def test_scope_is_omitted_with_empty_scope():
    changelog = generate_changelog("0.0.0")
    assert changelog["fix"][0][1] == "Fix another bug"


@mock.patch(
    "semantic_release.history.config.get", wrapped_config_get(changelog_scope=False)
)
@pytest.mark.parametrize(
    "commit,commit_type",
    [
        (MAJOR, "feature"),
        (MINOR, "feature"),
        (PATCH, "fix"),
    ],
)
def test_scope_included_in_changelog_configurable(commit, commit_type):
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **kw: [commit],
    ):
        changelog = generate_changelog("0.0.0")
        assert "**x:**" not in changelog[commit_type][0][1]


@mock.patch(
    "semantic_release.history.logs.get_commit_log",
    lambda *a, **k: [("23", "fix(x): abCD"), ("23", "fix: abCD")],
)
@pytest.mark.parametrize(
    "commit,config_setting,expected_description",
    [
        (("23", "fix(x): abCD"), True, "**x:** AbCD"),
        (("23", "fix(x): abCD"), False, "**x:** abCD"),
        (("23", "fix: abCD"), True, "AbCD"),
        (("23", "fix: abCD"), False, "abCD"),
    ],
)
def test_message_capitalization_is_configurable(
    commit, config_setting, expected_description
):
    with mock.patch(
        "semantic_release.history.logs.get_commit_log",
        lambda *a, **kw: [commit],
    ):

        with mock.patch(
            "semantic_release.history.config.get",
            wrapped_config_get(changelog_capitalize=config_setting),
        ):
            changelog = generate_changelog("0.0.0")
            assert changelog["fix"][0][1] == expected_description
