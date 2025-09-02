from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
from freezegun import freeze_time
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.changelog.context import ChangelogMode
from semantic_release.cli.config import ChangelogOutputFormat

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.example_project import (
    default_md_changelog_insertion_flag,
    default_rst_changelog_insertion_flag,
    example_changelog_md,
    example_changelog_rst,
)
from tests.fixtures.repos import (
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_alpha_prereleases_n_scipy_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits,
    repo_w_github_flow_w_default_release_channel_conventional_commits,
    repo_w_github_flow_w_default_release_channel_emoji_commits,
    repo_w_github_flow_w_default_release_channel_scipy_commits,
    repo_w_github_flow_w_feature_release_channel_conventional_commits,
    repo_w_github_flow_w_feature_release_channel_emoji_commits,
    repo_w_github_flow_w_feature_release_channel_scipy_commits,
    repo_w_no_tags_conventional_commits,
    repo_w_no_tags_conventional_commits_unmasked_initial_release,
    repo_w_no_tags_emoji_commits,
    repo_w_no_tags_scipy_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_emoji_commits,
    repo_w_trunk_only_n_prereleases_conventional_commits,
    repo_w_trunk_only_n_prereleases_emoji_commits,
    repo_w_trunk_only_n_prereleases_scipy_commits,
    repo_w_trunk_only_scipy_commits,
)
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from pathlib import Path

    from tests.conftest import (
        FormatDateStrFn,
        GetCachedRepoDataFn,
        GetStableDateNowFn,
        RunCliFn,
    )
    from tests.fixtures.example_project import UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        CommitConvention,
        GetCommitsFromRepoBuildDefFn,
        GetVersionsFromRepoBuildDefFn,
    )


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result, repo_fixture_name, tag_format",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            repo_w_trunk_only_conventional_commits.__name__,
            "v{version}",
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture),
                repo_fixture,
                "v{version}" if tag_format is None else tag_format,
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture, tag_format in [
                # Must have a previous release/tag
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        # repo_with_single_branch_conventional_commits.__name__, # default
                        repo_w_trunk_only_emoji_commits.__name__,
                        repo_w_trunk_only_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                        repo_w_trunk_only_n_prereleases_emoji_commits.__name__,
                        repo_w_trunk_only_n_prereleases_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_github_flow_w_default_release_channel_conventional_commits.__name__,
                        repo_w_github_flow_w_default_release_channel_emoji_commits.__name__,
                        repo_w_github_flow_w_default_release_channel_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                        repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
                        repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                        repo_w_git_flow_w_alpha_prereleases_n_emoji_commits.__name__,
                        repo_w_git_flow_w_alpha_prereleases_n_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits.__name__,
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        "submod-v{version}",
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__,
                    ]
                ],
            ]
        ],
    ],
)
def test_version_updates_changelog_w_new_version(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    tag_format: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    run_cli: RunCliFn,
    changelog_file: Path,
    insertion_flag: str,
    repo_fixture_name: str,
    stable_now_date: GetStableDateNowFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    """
    Given a previously released custom modified changelog file,
    When the version command is run with changelog.mode set to "update",
    Then the version is created and the changelog file is updated with new release info
        while maintaining the previously customized content
    """
    repo = repo_result["repo"]
    latest_tag = tag_format.format(
        version=get_versions_from_repo_build_def(repo_result["definition"])[-1]
    )

    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )

    # Custom text to maintain (must be different from the default)
    custom_text = "---{ls}{ls}Custom footer text{ls}".format(ls=os.linesep)

    # Capture expected changelog content
    with changelog_file.open(newline=os.linesep) as rfd:
        initial_changelog_parts = rfd.read().split(insertion_flag)

    expected_changelog_content = str.join(
        insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                os.linesep,
                [
                    initial_changelog_parts[1],
                    "",
                    custom_text,
                ],
            ),
        ],
    )

    # Reverse last release
    repo.git.tag("-d", latest_tag)
    repo.git.reset("--hard", "HEAD~1")

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Modify the current changelog with our custom text at bottom
    # Universal newlines is ok here since we are writing it back out
    # and not working with the os-specific insertion flag
    changelog_file.write_text(
        str.join(
            "\n",
            [
                changelog_file.read_text(),
                "",
                custom_text,
            ],
        )
    )

    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
        result = run_cli(cli_cmd[1:])

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_format, changelog_file, insertion_flag",
    [
        (
            ChangelogOutputFormat.MARKDOWN,
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT,
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result, repo_fixture_name",
    [
        (
            lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
            repo_w_no_tags_conventional_commits.__name__,
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture),
                repo_fixture,
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture in [
                # Must not have a single release/tag
                # repo_with_no_tags_conventional_commits.__name__, # default
                repo_w_no_tags_emoji_commits.__name__,
                repo_w_no_tags_scipy_commits.__name__,
            ]
        ],
    ],
)
def test_version_updates_changelog_wo_prev_releases(
    repo_result: BuiltRepoResult,
    repo_fixture_name: str,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_format: ChangelogOutputFormat,
    changelog_file: Path,
    insertion_flag: str,
    stable_now_date: GetStableDateNowFn,
    format_date_str: FormatDateStrFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    """
    Given the repository has no releases and the user has provided a initialized changelog,
    When the version command is run with changelog.mode set to "update",
    Then the version is created and the changelog file is updated with only an initial release statement
    """
    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )
    repo_build_date_str = format_date_str(now_datetime)

    # Custom text to maintain (must be different from the default)
    custom_text = "---{ls}{ls}Custom footer text{ls}".format(ls=os.linesep)

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    version = "v1.0.0"
    rst_version_header = f"{version} ({repo_build_date_str})"
    txt_after_insertion_flag = {
        ChangelogOutputFormat.MARKDOWN: str.join(
            os.linesep,
            [
                f"## {version} ({repo_build_date_str})",
                "",
                "- Initial Release",
            ],
        ),
        ChangelogOutputFormat.RESTRUCTURED_TEXT: str.join(
            os.linesep,
            [
                f".. _changelog-{version}:",
                "",
                rst_version_header,
                f"{'=' * len(rst_version_header)}",
                "",
                "* Initial Release",
            ],
        ),
    }

    # Capture and modify the current changelog content to become the expected output
    # We much use os.linesep here since the insertion flag is os-specific
    with changelog_file.open(newline=os.linesep) as rfd:
        initial_changelog_parts = rfd.read().split(insertion_flag)

    # content is os-specific because of the insertion flag & how we read the original file
    expected_changelog_content = str.join(
        insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                os.linesep,
                [
                    os.linesep,
                    txt_after_insertion_flag[changelog_format],
                    "",
                    custom_text,
                ],
            ),
        ],
    )

    # Grab the Unreleased changelog & create the initialized user changelog
    # force output to not perform any newline translations
    with changelog_file.open(mode="w", newline="") as wfd:
        wfd.write(
            str.join(
                insertion_flag,
                [initial_changelog_parts[0], f"{os.linesep * 2}{custom_text}"],
            )
        )
        wfd.flush()

    # Act
    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog footer is maintained and updated with Unreleased info
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_format, changelog_file, insertion_flag",
    [
        (
            ChangelogOutputFormat.MARKDOWN,
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT,
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result, repo_fixture_name",
    [
        pytest.param(
            lazy_fixture(repo_fixture),
            repo_fixture,
            marks=pytest.mark.comprehensive,
        )
        for repo_fixture in [
            # Must not have a single release/tag
            repo_w_no_tags_conventional_commits_unmasked_initial_release.__name__,
        ]
    ],
)
def test_version_updates_changelog_wo_prev_releases_n_unmasked_initial_release(
    repo_result: BuiltRepoResult,
    repo_fixture_name: str,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_format: ChangelogOutputFormat,
    changelog_file: Path,
    insertion_flag: str,
    stable_now_date: GetStableDateNowFn,
    format_date_str: FormatDateStrFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    """
    Given the repository has no releases and the user has provided a initialized changelog,
    When the version command is run with changelog.mode set to "update",
    Then the version is created and the changelog file is updated with new release info
    """
    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )
    repo_build_date_str = format_date_str(now_datetime)

    # Custom text to maintain (must be different from the default)
    custom_text = "---{ls}{ls}Custom footer text{ls}".format(ls=os.linesep)

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    version = "v1.0.0"
    rst_version_header = f"{version} ({repo_build_date_str})"
    search_n_replacements = {
        ChangelogOutputFormat.MARKDOWN: (
            "## Unreleased",
            f"## {version} ({repo_build_date_str})",
        ),
        ChangelogOutputFormat.RESTRUCTURED_TEXT: (
            ".. _changelog-unreleased:{ls}{ls}Unreleased{ls}{underline}".format(
                ls=os.linesep,
                underline="=" * len("Unreleased"),
            ),
            str.join(
                os.linesep,
                [
                    f".. _changelog-{version}:",
                    "",
                    rst_version_header,
                    f"{'=' * len(rst_version_header)}",
                ],
            ),
        ),
    }

    search_text = search_n_replacements[changelog_format][0]
    replacement_text = search_n_replacements[changelog_format][1]

    # Capture and modify the current changelog content to become the expected output
    # We much use os.linesep here since the insertion flag is os-specific
    with changelog_file.open(newline=os.linesep) as rfd:
        initial_changelog_parts = rfd.read().split(insertion_flag)

    # content is os-specific because of the insertion flag & how we read the original file
    expected_changelog_content = str.join(
        insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                os.linesep,
                [
                    initial_changelog_parts[1].replace(
                        search_text,
                        replacement_text,
                    ),
                    "",
                    custom_text,
                ],
            ),
        ],
    )

    # Grab the Unreleased changelog & create the initialized user changelog
    # force output to not perform any newline translations
    with changelog_file.open(mode="w", newline="") as wfd:
        wfd.write(
            str.join(
                insertion_flag,
                [initial_changelog_parts[0], f"{os.linesep * 2}{custom_text}"],
            )
        )
        wfd.flush()

    # Act
    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog footer is maintained and updated with Unreleased info
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file",
    [
        lazy_fixture(example_changelog_md.__name__),
        lazy_fixture(example_changelog_rst.__name__),
    ],
)
@pytest.mark.parametrize(
    "repo_result, repo_fixture_name, tag_format",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            repo_w_trunk_only_conventional_commits.__name__,
            "v{version}",
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture),
                repo_fixture,
                "v{version}" if tag_format is None else tag_format,
                marks=pytest.mark.comprehensive,
            )
            for repo_fixture, tag_format in [
                # Must have a previous release/tag
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        # repo_with_single_branch_conventional_commits.__name__, # default
                        repo_w_trunk_only_emoji_commits.__name__,
                        repo_w_trunk_only_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                        repo_w_trunk_only_n_prereleases_emoji_commits.__name__,
                        repo_w_trunk_only_n_prereleases_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_github_flow_w_default_release_channel_conventional_commits.__name__,
                        repo_w_github_flow_w_default_release_channel_emoji_commits.__name__,
                        repo_w_github_flow_w_default_release_channel_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                        repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
                        repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                        repo_w_git_flow_w_alpha_prereleases_n_emoji_commits.__name__,
                        repo_w_git_flow_w_alpha_prereleases_n_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        None,
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits.__name__,
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits.__name__,
                    ]
                ],
                *[
                    (
                        repo_fixture_name,
                        "submod-v{version}",
                    )
                    for repo_fixture_name in [
                        repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__,
                    ]
                ],
            ]
        ],
    ],
)
def test_version_initializes_changelog_in_update_mode_w_no_prev_changelog(
    repo_result: BuiltRepoResult,
    repo_fixture_name: str,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    tag_format: str,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
    stable_now_date: GetStableDateNowFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    """
    Given that the changelog file does not exist,
    When the version command is run with changelog.mode set to "update",
    Then the version is created and the changelog file is initialized
    with the default content.
    """
    repo = repo_result["repo"]
    latest_tag = tag_format.format(
        version=get_versions_from_repo_build_def(repo_result["definition"])[-1]
    )

    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )

    # Capture the expected changelog content
    expected_changelog_content = changelog_file.read_text()

    # Reverse last release
    repo.git.tag("-d", latest_tag)
    repo.git.reset("--hard", "HEAD~1")

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Remove any previous changelog to update
    os.remove(str(changelog_file.resolve()))

    # Act
    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_version_maintains_changelog_in_update_mode_w_no_flag(
    changelog_file: Path,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    insertion_flag: str,
):
    """
    Given that the changelog file exists but does not contain the insertion flag,
    When the version command is run with changelog.mode set to "update",
    Then the version is created but the changelog file is not updated.
    """
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Remove the insertion flag from the existing changelog
    with changelog_file.open(newline=os.linesep) as rfd:
        expected_changelog_content = rfd.read().replace(
            f"{insertion_flag}{os.linesep}",
            "",
            1,
        )
    # no newline translations
    with changelog_file.open("w", newline="") as wfd:
        wfd.write(expected_changelog_content)

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file",
    [
        lazy_fixture(example_changelog_md.__name__),
        lazy_fixture(example_changelog_rst.__name__),
    ],
)
@pytest.mark.parametrize(
    "repo_result, repo_fixture_name, commit_type, tag_format",
    [
        (
            lazy_fixture(repo_fixture),
            repo_fixture,
            repo_fixture.split("_")[-2],
            "v{version}",
        )
        for repo_fixture in [
            # Must have a previous release/tag
            repo_w_trunk_only_conventional_commits.__name__,
        ]
    ],
)
def test_version_updates_changelog_w_new_version_n_filtered_commit(
    repo_result: BuiltRepoResult,
    repo_fixture_name: str,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    commit_type: CommitConvention,
    tag_format: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    run_cli: RunCliFn,
    changelog_file: Path,
    stable_now_date: GetStableDateNowFn,
    get_commits_from_repo_build_def: GetCommitsFromRepoBuildDefFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    """
    Given a project that has a version bumping change but also an exclusion pattern for the same change type,
    When the version command is run,
    Then the version is created and the changelog file is updated with the excluded commit
        info anyway.
    """
    repo = repo_result["repo"]
    latest_version = get_versions_from_repo_build_def(repo_result["definition"])[-1]
    latest_tag = tag_format.format(version=latest_version)
    repo_definition = get_commits_from_repo_build_def(repo_result["definition"])

    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )

    # expected version bump commit (that should be in changelog)
    bumping_commit = repo_definition[str(latest_version)]["commits"][-1]
    expected_bump_message = bumping_commit["desc"].capitalize()

    # Capture the expected changelog content
    expected_changelog_content = changelog_file.read_text()

    # Reverse last release
    repo.git.tag("-d", latest_tag)
    repo.git.reset("--hard", "HEAD~1")

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.exclude_commit_patterns",
        [f"{bumping_commit['msg'].split(':', maxsplit=1)[0]}: .*"],
    )

    # Act
    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push", "--changelog"]
        result = run_cli(cli_cmd[1:])

    # Capture the new changelog content (os aware because of expected content)
    actual_content = changelog_file.read_text()

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert expected_changelog_content == actual_content

    for msg_part in expected_bump_message.split("\n\n"):
        assert msg_part.capitalize() in actual_content
