import mock

from semantic_release.history.logs import get_github_compare_url, markdown_changelog


def test_github_compare_url():
    with mock.patch(
        "semantic_release.history.logs.get_repository_owner_and_name",
        return_value=["owner", "name"],
    ):
        assert (
            get_github_compare_url("1.0.0", "2.0.0")
            == "https://github.com/owner/name/compare/v1.0.0...v2.0.0"
        )


def test_should_output_all_sections():
    assert markdown_changelog(
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
            "fix": [("234", "Fix bug in super-feature")],
            "documentation": [("0", "Document super-feature")],
            "performance": [],
        },
    ) == (
        "\n"
        "### Feature\n"
        "* Add non-breaking super-feature (145)\n"
        "* Add super-feature (134)\n"
        "\n"
        "### Fix\n"
        "* Fix bug in super-feature (234)\n"
        "\n"
        "### Breaking\n"
        "* Uses super-feature as default instead of dull-feature. (21)\n"
        "\n"
        "### Documentation\n"
        "* Document super-feature (0)\n"
    )


def test_should_not_include_empty_sections():
    assert (
        markdown_changelog(
            "1.0.1",
            {
                "refactor": [],
                "breaking": [],
                "feature": [],
                "fix": [],
                "documentation": [],
                "performance": [],
            },
        )
        == ""
    )


def test_should_not_output_heading():
    assert "v1.0.1" not in markdown_changelog(
        "1.0.1",
        {
            "refactor": [],
            "breaking": [],
            "feature": [],
            "fix": [],
            "documentation": [],
            "performance": [],
        },
    )


def test_should_output_heading():
    assert "## v1.0.1\n" in markdown_changelog(
        "1.0.1",
        {
            "refactor": [],
            "breaking": [],
            "feature": [],
            "fix": [],
            "documentation": [],
            "performance": [],
        },
        header=True,
    )


def test_compare_url(mocker):
    mocker.patch("semantic_release.history.logs.config.getboolean", return_value=True)
    mocker.patch(
        "semantic_release.history.logs.get_repository_owner_and_name",
        return_value=["owner", "name"],
    )

    assert (
        "**[See all commits in this version]"
        "(https://github.com/owner/name/compare/v1.0.0...v2.0.0)**\n"
        in markdown_changelog(
            "2.0.0",
            {
                "refactor": [],
                "breaking": [],
                "feature": [],
                "fix": [],
                "documentation": [],
                "performance": [],
            },
            previous_version="1.0.0",
        )
    )
