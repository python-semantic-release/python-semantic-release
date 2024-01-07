from __future__ import annotations

import json
import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import git
import pytest

from semantic_release import __version__
from semantic_release.cli import main

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from git import Repo

    from tests.fixtures.example_project import UpdatePyprojectTomlFn


def test_main_prints_version_and_exits(cli_runner: CliRunner):
    result = cli_runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"semantic-release, version {__version__}\n"


@pytest.mark.parametrize("args", [[], ["--help"]])
def test_main_prints_help_text(cli_runner: CliRunner, args: list[str]):
    result = cli_runner.invoke(main, args)
    assert result.exit_code == 0


def test_not_a_release_branch_exit_code(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    # Run anything that doesn't trigger the help text
    repo_with_git_flow_angular_commits.git.checkout("-b", "branch-does-not-exist")
    result = cli_runner.invoke(main, ["version", "--no-commit"])
    assert result.exit_code == 0


def test_not_a_release_branch_exit_code_with_strict(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    # Run anything that doesn't trigger the help text
    repo_with_git_flow_angular_commits.git.checkout("-b", "branch-does-not-exist")
    result = cli_runner.invoke(main, ["--strict", "version", "--no-commit"])
    assert result.exit_code != 0


def test_not_a_release_branch_detached_head_exit_code(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    expected_err_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made"
    )

    # cause repo to be in detached head state without file changes
    repo_with_git_flow_angular_commits.git.checkout("HEAD", "--detach")
    result = cli_runner.invoke(main, ["version", "--no-commit"])

    # as non-strict, this will return success exit code
    assert result.exit_code == 0
    assert expected_err_msg in result.stderr


@pytest.fixture
def toml_file_with_no_configuration_for_psr(tmp_path: Path) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(
        dedent(
            r"""
            [project]
            name = "foo"
            version = "1.2.0"
            """
        )
    )

    return path


@pytest.fixture
def json_file_with_no_configuration_for_psr(tmp_path: Path) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"foo": [1, 2, 3]}))

    return path


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_default_config_is_used_when_none_in_toml_config_file(
    cli_runner: CliRunner,
    toml_file_with_no_configuration_for_psr: Path,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", str(toml_file_with_no_configuration_for_psr), "version"],
    )

    assert result.exit_code == 0


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_default_config_is_used_when_none_in_json_config_file(
    cli_runner: CliRunner,
    json_file_with_no_configuration_for_psr: Path,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", str(json_file_with_no_configuration_for_psr), "version"],
    )

    assert result.exit_code == 0


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_errors_when_config_file_does_not_exist_and_passed_explicitly(
    cli_runner: CliRunner,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", "somenonexistantfile.123.txt", "version"],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.stderr


@pytest.mark.usefixtures("repo_with_no_tags_angular_commits")
def test_errors_when_config_file_invalid_configuration(
    cli_runner: CliRunner, update_pyproject_toml: UpdatePyprojectTomlFn
):
    update_pyproject_toml("tool.semantic_release.remote.type", "invalidType")
    result = cli_runner.invoke(main, ["--config", "pyproject.toml", "version"])

    stderr_lines = result.stderr.splitlines()
    assert result.exit_code == 1
    assert "1 validation error for RawConfig" in stderr_lines[0]
    assert "remote.type" in stderr_lines[1]


def test_uses_default_config_when_no_config_file_found(
    tmp_path: Path,
    cli_runner: CliRunner,
):
    # We have to initialise an empty git repository, as the example projects
    # all have pyproject.toml configs which would be used by default
    repo = git.Repo.init(tmp_path)
    repo.git.branch("-M", "main")
    with repo.config_writer("repository") as config:
        config.set_value("user", "name", "semantic release testing")
        config.set_value("user", "email", "not_a_real@email.com")
        config.set_value("commit", "gpgsign", False)
    repo.create_remote(name="origin", url="foo@barvcs.com:user/repo.git")
    repo.git.commit("-m", "feat: initial commit", "--allow-empty")

    try:
        os.chdir(tmp_path)
        result = cli_runner.invoke(
            main,
            ["--noop", "version"],
        )

        assert result.exit_code == 0
    finally:
        repo.close()
