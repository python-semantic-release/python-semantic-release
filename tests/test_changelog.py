import mock
import pytest

from semantic_release.changelog import markdown_changelog
from semantic_release.changelog.changelog import (
    add_pr_link,
    changelog_table,
    get_changelog_sections,
)
from semantic_release.changelog.compare import compare_url, get_github_compare_url

from . import wrapped_config_get


def test_markdown_changelog():
    assert markdown_changelog(
        "owner",
        "repo_name",
        "0",
        {
            "refactor": [("12", "Refactor super-feature")],
            "breaking": [
                ("21", "Uses super-feature as default instead of dull-feature.")
            ],
            "feature": [
                ("145", "Add non-breaking super-feature"),
                ("134", "Add super-feature"),
            ],
            "fix": [("234", "Fix bug in super-feature (#15)")],
            "documentation": [("0", "Document super-feature (#189)")],
            "performance": [],
        },
    ) == (
        # Expected output with the default configuration
        "### Feature\n"
        "* Add non-breaking super-feature ([`145`](https://github.com/owner/repo_name/"
        "commit/145))\n"
        "* Add super-feature ([`134`](https://github.com/owner/repo_name/commit/134))\n"
        "\n"
        "### Fix\n"
        "* Fix bug in super-feature ([#15](https://github.com/owner/repo_name/issues/15))"
        " ([`234`](https://github.com/owner/repo_name/"
        "commit/234))\n"
        "\n"
        "### Breaking\n"
        "* Uses super-feature as default instead of dull-feature."
        " ([`21`](https://github.com/owner/repo_name/commit/21))\n"
        "\n"
        "### Documentation\n"
        "* Document super-feature ([#189](https://github.com/owner/repo_name/issues/189))"
        " ([`0`](https://github.com/owner/repo_name/commit/0))"
    )


def test_markdown_changelog_gitlab():
    with mock.patch(
        "semantic_release.changelog.config.get", wrapped_config_get(hvcs="gitlab")
    ):
        assert markdown_changelog(
            "owner",
            "repo_name",
            "0",
            {
                "refactor": [("12", "Refactor super-feature")],
                "feature": [
                    ("145", "Add non-breaking super-feature (#1)"),
                    ("134", "Add super-feature"),
                ],
                "documentation": [("0", "Document super-feature (#189)")],
                "performance": [],
            },
        ) == (
            # Expected output with the default configuration
            "### Feature\n"
            "* Add non-breaking super-feature ([#1](https://gitlab.com/owner/"
            "repo_name/-/issues/1)) ([`145`](https://gitlab.com/owner/"
            "repo_name/-/commit/145))\n"
            "* Add super-feature ([`134`](https://gitlab.com/owner/repo_name/-/"
            "commit/134))\n"
            "\n"
            "### Documentation\n"
            "* Document super-feature ([#189](https://gitlab.com/owner/repo_name/"
            "-/issues/189)) ([`0`](https://gitlab.com/owner/repo_name/"
            "-/commit/0))"
        )


def test_changelog_table():
    assert changelog_table(
        "owner",
        "repo_name",
        {
            "feature": [("sha1", "commit1"), ("sha2", "commit2")],
            "fix": [("sha3", "commit3 (#123)")],
        },
        ["section1", "section2"],
    ) == (
        "| Type | Change |\n"
        "| --- | --- |\n"
        "| Feature | commit1 ([`sha1`](https://github.com/owner/repo_name/commit/sha1))"
        "<br>commit2 ([`sha2`](https://github.com/owner/repo_name/commit/sha2)) |\n"
        "| Fix | commit3 ([#123](https://github.com/owner/repo_name/issues/123))"
        " ([`sha3`](https://github.com/owner/repo_name/commit/sha3)) |\n"
    )


def test_should_not_output_heading():
    assert "v1.0.1" not in markdown_changelog(
        "owner",
        "repo_name",
        "1.0.1",
        {},
    )


def test_should_output_heading():
    assert "## v1.0.1\n" in markdown_changelog(
        "owner",
        "repo_name",
        "1.0.1",
        {},
        header=True,
    )


def test_get_changelog_sections():
    assert (
        len(
            list(
                get_changelog_sections(
                    {
                        "refactor": [0, 1, 2],
                        "breaking": [],
                        "feature": [],
                        "fix": [],
                        "documentation": [],
                        "performance": [],
                    },
                    ["breaking", "feature", "fix", "performance"],
                )
            )
        )
        == 0
    )


@pytest.mark.parametrize(
    "message,hvcs,expected_output",
    [
        (
            "test (#123)",
            "github",
            "test ([#123](https://github.com/owner/name/issues/123))",
        ),
        ("test without commit", "github", "test without commit"),
        ("test (#123) in middle", "github", "test (#123) in middle"),
        (
            "test (#123)",
            "gitlab",
            "test ([#123](https://gitlab.com/owner/name/-/issues/123))",
        ),
        ("test without commit", "gitlab", "test without commit"),
    ],
)
def test_add_pr_link(message, hvcs, expected_output):
    with mock.patch(
        "semantic_release.changelog.config.get", wrapped_config_get(hvcs=hvcs)
    ):
        assert add_pr_link("owner", "name", message) == expected_output


def test_github_compare_url():
    with mock.patch(
        "semantic_release.changelog.compare.get_repository_owner_and_name",
        return_value=["owner", "name"],
    ):
        assert (
            get_github_compare_url("1.0.0", "2.0.0")
            == "https://github.com/owner/name/compare/v1.0.0...v2.0.0"
        )


def test_compare_url():
    with mock.patch(
        "semantic_release.changelog.compare.get_repository_owner_and_name",
        return_value=["owner", "name"],
    ):
        assert compare_url(previous_version="1.0.0", version="2.0.0") == (
            "**[See all commits in this version]"
            "(https://github.com/owner/name/compare/v1.0.0...v2.0.0)**"
        )
