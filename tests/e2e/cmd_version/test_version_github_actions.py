from __future__ import annotations

import os
from datetime import timezone
from typing import TYPE_CHECKING, cast

import pytest
from freezegun import freeze_time
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from tests.const import EXAMPLE_PROJECT_LICENSE, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import (
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
)
from tests.util import actions_output_to_dict, assert_successful_exit_code

if TYPE_CHECKING:
    from semantic_release.hvcs.github import Github

    from tests.conftest import GetStableDateNowFn, RunCliFn
    from tests.fixtures.example_project import ExProjectDir
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
    [lazy_fixture(repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__)],
)
def test_version_writes_github_actions_output(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    example_project_dir: ExProjectDir,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    generate_default_release_notes_from_def: GenerateDefaultReleaseNotesFromDefFn,
    split_repo_actions_by_release_tags: SplitRepoActionsByReleaseTagsFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    stable_now_date: GetStableDateNowFn,
):
    mock_output_file = example_project_dir / "action.out"
    repo_def = repo_result["definition"]
    tag_format_str = cast(str, get_cfg_value_from_def(repo_def, "tag_format_str"))
    all_versions = get_versions_from_repo_build_def(repo_def)
    latest_release_version = all_versions[-1]
    release_tag = tag_format_str.format(version=latest_release_version)
    previous_version = all_versions[-2] if len(all_versions) > 1 else None
    hvcs_client = cast("Github", get_hvcs_client_from_repo_def(repo_def))
    repo_actions_per_version = split_repo_actions_by_release_tags(
        repo_definition=repo_def
    )
    expected_gha_output = {
        "released": str(True).lower(),
        "version": latest_release_version,
        "tag": release_tag,
        "link": hvcs_client.create_release_url(release_tag),
        "commit_sha": "0" * 40,
        "is_prerelease": str(latest_release_version.is_prerelease).lower(),
        "previous_version": str(previous_version) if previous_version else "",
        "release_notes": generate_default_release_notes_from_def(
            version_actions=repo_actions_per_version[latest_release_version],
            hvcs=hvcs_client,
            previous_version=previous_version,
            license_name=EXAMPLE_PROJECT_LICENSE,
            mask_initial_release=get_cfg_value_from_def(
                repo_def, "mask_initial_release"
            ),
        ),
    }

    # Remove the previous tag & version commit
    repo_result["repo"].git.tag(release_tag, delete=True)
    repo_result["repo"].git.reset("HEAD~1", hard=True)

    # Act
    with freeze_time(stable_now_date().astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push"]
        result = run_cli(
            cli_cmd[1:], env={"GITHUB_OUTPUT": str(mock_output_file.resolve())}
        )

    assert_successful_exit_code(result, cli_cmd)

    # Update the expected output with the commit SHA
    expected_gha_output["commit_sha"] = repo_result["repo"].head.commit.hexsha

    if not mock_output_file.exists():
        pytest.fail(
            f"Expected output file {mock_output_file} to be created, but it does not exist."
        )

    # Extract the output
    with open(mock_output_file, encoding="utf-8", newline=os.linesep) as rfd:
        action_outputs = actions_output_to_dict(rfd.read())

    # Evaluate
    expected_keys = set(expected_gha_output.keys())
    actual_keys = set(action_outputs.keys())
    key_difference = expected_keys.symmetric_difference(actual_keys)

    assert not key_difference, f"Unexpected keys found: {key_difference}"

    assert expected_gha_output["released"] == action_outputs["released"]
    assert expected_gha_output["version"] == action_outputs["version"]
    assert expected_gha_output["tag"] == action_outputs["tag"]
    assert expected_gha_output["is_prerelease"] == action_outputs["is_prerelease"]
    assert expected_gha_output["link"] == action_outputs["link"]
    assert expected_gha_output["previous_version"] == action_outputs["previous_version"]
    assert expected_gha_output["commit_sha"] == action_outputs["commit_sha"]
    assert expected_gha_output["release_notes"] == action_outputs["release_notes"]
