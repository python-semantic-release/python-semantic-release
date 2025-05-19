from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import (
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
)
from tests.util import actions_output_to_dict, assert_successful_exit_code

if TYPE_CHECKING:
    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import ExProjectDir


@pytest.mark.usefixtures(
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__
)
def test_version_writes_github_actions_output(
    run_cli: RunCliFn,
    example_project_dir: ExProjectDir,
):
    mock_output_file = example_project_dir / "action.out"

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push"]
    result = run_cli(
        cli_cmd[1:], env={"GITHUB_OUTPUT": str(mock_output_file.resolve())}
    )
    assert_successful_exit_code(result, cli_cmd)

    if not mock_output_file.exists():
        pytest.fail(
            f"Expected output file {mock_output_file} to be created, but it does not exist."
        )

    # Extract the output
    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )

    # Evaluate
    assert "released" in action_outputs
    assert action_outputs["released"] == "true"
    assert "version" in action_outputs
    assert action_outputs["version"] == "1.2.1"
    assert "tag" in action_outputs
    assert action_outputs["tag"] == "v1.2.1"
