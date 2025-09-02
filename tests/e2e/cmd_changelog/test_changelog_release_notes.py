from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures import lf as lazy_fixture

from tests.const import CHANGELOG_SUBCMD, EXAMPLE_PROJECT_LICENSE, MAIN_PROG_NAME
from tests.fixtures.repos import (
    repo_w_github_flow_w_default_release_channel_conventional_commits,
    repo_w_github_flow_w_feature_release_channel_conventional_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_emoji_commits,
    repo_w_trunk_only_scipy_commits,
)
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from requests_mock import Mocker

    from tests.conftest import GetCachedRepoDataFn, GetStableDateNowFn, RunCliFn
    from tests.fixtures.example_project import UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        GenerateDefaultReleaseNotesFromDefFn,
        GetCfgValueFromDefFn,
        GetHvcsClientFromRepoDefFn,
        GetVersionsFromRepoBuildDefFn,
        SplitRepoActionsByReleaseTagsFn,
    )


@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture_name)
        for repo_fixture_name in [
            repo_w_trunk_only_conventional_commits.__name__,
        ]
    ],
)
def test_changelog_latest_release_notes(
    repo_result: BuiltRepoResult,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    run_cli: RunCliFn,
    post_mocker: Mocker,
    split_repo_actions_by_release_tags: SplitRepoActionsByReleaseTagsFn,
    generate_default_release_notes_from_def: GenerateDefaultReleaseNotesFromDefFn,
):
    # Setup
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    repo_actions_per_version = split_repo_actions_by_release_tags(
        repo_definition=repo_def
    )
    all_versions = get_versions_from_repo_build_def(repo_def)
    latest_release_version = all_versions[-1]
    release_tag = tag_format_str.format(version=latest_release_version)

    expected_release_notes = generate_default_release_notes_from_def(
        version_actions=repo_actions_per_version[latest_release_version],
        hvcs=get_hvcs_client_from_repo_def(repo_def),
        previous_version=(all_versions[-2] if len(all_versions) > 1 else None),
        license_name=EXAMPLE_PROJECT_LICENSE,
        mask_initial_release=get_cfg_value_from_def(repo_def, "mask_initial_release"),
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, "--post-to-release-tag", release_tag]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None
    request_body = post_mocker.last_request.json()

    assert "body" in request_body
    actual_posted_notes = request_body["body"]

    assert expected_release_notes == actual_posted_notes


@pytest.mark.parametrize(
    "repo_result, mask_initial_release",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            True,
        ),
        pytest.param(
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            False,
            marks=pytest.mark.comprehensive,
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                mask_initial_release,
                marks=pytest.mark.comprehensive,
            )
            for mask_initial_release in [True, False]
            for repo_fixture_name in [
                repo_w_github_flow_w_default_release_channel_conventional_commits.__name__,
            ]
        ],
    ],
)
def test_changelog_previous_release_notes(
    repo_result: BuiltRepoResult,
    mask_initial_release: bool,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    run_cli: RunCliFn,
    post_mocker: Mocker,
    split_repo_actions_by_release_tags: SplitRepoActionsByReleaseTagsFn,
    generate_default_release_notes_from_def: GenerateDefaultReleaseNotesFromDefFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    # Setup
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]
    repo_actions_per_version = split_repo_actions_by_release_tags(
        repo_definition=repo_def
    )
    # Extract all versions except for the latest one
    all_prev_versions = get_versions_from_repo_build_def(repo_def)[:-1]
    latest_release_version = all_prev_versions[-1]
    release_tag = tag_format_str.format(version=latest_release_version)

    expected_release_notes = generate_default_release_notes_from_def(
        version_actions=repo_actions_per_version[latest_release_version],
        hvcs=get_hvcs_client_from_repo_def(repo_def),
        previous_version=(
            all_prev_versions[-2] if len(all_prev_versions) > 1 else None
        ),
        license_name=EXAMPLE_PROJECT_LICENSE,
        mask_initial_release=mask_initial_release,
    )

    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.mask_initial_release",
        mask_initial_release,
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, "--post-to-release-tag", release_tag]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None
    request_body = post_mocker.last_request.json()

    assert "body" in request_body
    actual_posted_notes = request_body["body"]

    assert expected_release_notes == actual_posted_notes


@pytest.mark.parametrize(
    "repo_result, repo_fixture_name, mask_initial_release, license_name",
    [
        (
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            repo_w_trunk_only_conventional_commits.__name__,
            True,
            "BSD-3-Clause",
        ),
        pytest.param(
            lazy_fixture(repo_w_trunk_only_conventional_commits.__name__),
            repo_w_trunk_only_conventional_commits.__name__,
            False,
            "BSD-3-Clause",
            marks=pytest.mark.comprehensive,
        ),
        *[
            pytest.param(
                lazy_fixture(repo_fixture_name),
                repo_fixture_name,
                mask_initial_release,
                "BSD-3-Clause",
                marks=pytest.mark.comprehensive,
            )
            for mask_initial_release in [True, False]
            for repo_fixture_name in [
                repo_w_trunk_only_emoji_commits.__name__,
                repo_w_trunk_only_scipy_commits.__name__,
                # Add more repos here if needed
                # github_flow had issues as its hard to generate the release notes from squash commits
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
            ]
        ],
    ],
)
def test_changelog_release_notes_license_change(
    repo_result: BuiltRepoResult,
    license_name: str,
    mask_initial_release: bool,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    run_cli: RunCliFn,
    post_mocker: Mocker,
    split_repo_actions_by_release_tags: SplitRepoActionsByReleaseTagsFn,
    generate_default_release_notes_from_def: GenerateDefaultReleaseNotesFromDefFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    repo_fixture_name: str,
    stable_now_date: GetStableDateNowFn,
    get_cached_repo_data: GetCachedRepoDataFn,
):
    # Setup
    repo_def = repo_result["definition"]
    tag_format_str: str = get_cfg_value_from_def(repo_def, "tag_format_str")  # type: ignore[assignment]

    if not (repo_build_data := get_cached_repo_data(repo_fixture_name)):
        pytest.fail("Repo build date not found in cache")

    repo_build_datetime = datetime.strptime(repo_build_data["build_date"], "%Y-%m-%d")
    now_datetime = stable_now_date().replace(
        year=repo_build_datetime.year,
        month=repo_build_datetime.month,
        day=repo_build_datetime.day,
    )

    repo_actions_per_version = split_repo_actions_by_release_tags(
        repo_definition=repo_def,
    )
    # Extract all versions
    all_versions = get_versions_from_repo_build_def(repo_def)
    assert len(all_versions) > 1
    latest_release_version = all_versions[-1]
    previous_release_version = all_versions[-2]
    latest_release_tag = tag_format_str.format(version=latest_release_version)
    prev_release_tag = tag_format_str.format(version=previous_release_version)

    expected_release_notes = generate_default_release_notes_from_def(
        version_actions=repo_actions_per_version[latest_release_version],
        hvcs=get_hvcs_client_from_repo_def(repo_def),
        previous_version=(previous_release_version if len(all_versions) > 1 else None),
        license_name=license_name,
        mask_initial_release=mask_initial_release,
    )

    expected_prev_release_notes = generate_default_release_notes_from_def(
        version_actions=repo_actions_per_version[previous_release_version],
        hvcs=get_hvcs_client_from_repo_def(repo_def),
        previous_version=(all_versions[-3] if len(all_versions) > 2 else None),
        license_name=EXAMPLE_PROJECT_LICENSE,
        mask_initial_release=mask_initial_release,
    )

    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.mask_initial_release",
        mask_initial_release,
    )
    update_pyproject_toml("project.license-expression", license_name)

    git_repo = repo_result["repo"]

    git_repo.git.commit(
        amend=True,
        a=True,
        no_edit=True,
        date=now_datetime.isoformat(timespec="seconds"),
    )

    with git_repo.git.custom_environment(
        GIT_COMMITTER_DATE=now_datetime.isoformat(timespec="seconds"),
    ):
        git_repo.git.tag(latest_release_tag, d=True)
        git_repo.git.tag(latest_release_tag, a=True, m=latest_release_tag)

    # Act
    cli_cmd = [
        MAIN_PROG_NAME,
        CHANGELOG_SUBCMD,
        "--post-to-release-tag",
        latest_release_tag,
    ]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None
    request_body = post_mocker.last_request.json()

    assert "body" in request_body
    actual_new_posted_notes = request_body["body"]

    assert expected_release_notes == actual_new_posted_notes

    # Generate the previous release notes
    cli_cmd = [
        MAIN_PROG_NAME,
        CHANGELOG_SUBCMD,
        "--post-to-release-tag",
        prev_release_tag,
    ]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert post_mocker.call_count == 2
    assert post_mocker.last_request is not None
    request_body = post_mocker.last_request.json()

    assert "body" in request_body
    actual_prev_posted_notes = request_body["body"]

    assert expected_prev_release_notes == actual_prev_posted_notes

    assert actual_prev_posted_notes != actual_new_posted_notes
