from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from semantic_release.cli.commands.main import main

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import repo_with_git_flow_angular_commits
from tests.util import actions_output_to_dict, assert_successful_exit_code

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner


@pytest.mark.usefixtures(repo_with_git_flow_angular_commits.__name__)
def test_version_writes_github_actions_output(
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    mock_output_file = tmp_path / "action.out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(mock_output_file.resolve()))

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Extract the output
    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert "released" in action_outputs
    assert action_outputs["released"] == "true"
    assert "version" in action_outputs
    assert action_outputs["version"] == "1.2.1"
    assert "tag" in action_outputs
    assert action_outputs["tag"] == "v1.2.1"
