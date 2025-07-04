from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import (
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
)
from tests.util import actions_output_to_dict, assert_successful_exit_code

if TYPE_CHECKING:
    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import ExProjectDir
    from tests.fixtures.git_repo import BuiltRepoResult


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__)],
)
def test_version_writes_github_actions_output(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    example_project_dir: ExProjectDir,
):
    mock_output_file = example_project_dir / "action.out"
    expected_gha_output = {
        "released": str(True).lower(),
        "version": "1.2.1",
        "tag": "v1.2.1",
        "commit_sha": "0" * 40,
        "is_prerelease": str(False).lower(),
    }

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push"]
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
    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )

    # Evaluate
    expected_keys = set(expected_gha_output.keys())
    actual_keys = set(action_outputs.keys())
    key_difference = expected_keys.symmetric_difference(actual_keys)

    assert not key_difference, f"Unexpected keys found: {key_difference}"

    assert expected_gha_output["released"] == action_outputs["released"]
    assert expected_gha_output["version"] == action_outputs["version"]
    assert expected_gha_output["tag"] == action_outputs["tag"]
    assert expected_gha_output["is_prerelease"] == action_outputs["is_prerelease"]
    assert expected_gha_output["commit_sha"] == action_outputs["commit_sha"]
