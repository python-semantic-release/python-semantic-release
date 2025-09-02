from __future__ import annotations

import json
import subprocess
from pathlib import Path
from shutil import rmtree
from textwrap import dedent
from typing import TYPE_CHECKING

import git
import pytest
from click.testing import CliRunner
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release import __version__

from tests.const import MAIN_PROG_NAME, SUCCESS_EXIT_CODE, VERSION_SUBCMD
from tests.fixtures.repos import repo_w_no_tags_conventional_commits
from tests.util import assert_exit_code, assert_successful_exit_code

if TYPE_CHECKING:
    from tests.conftest import RunCliFn
    from tests.e2e.conftest import StripLoggingMessagesFn
    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult


@pytest.mark.parametrize(
    "project_script_name",
    [
        "python-semantic-release",
        "semantic-release",
        "psr",
    ],
)
def test_entrypoint_scripts(project_script_name: str):
    # Setup
    command = str.join(" ", [project_script_name, "--version"])
    expected_output = f"semantic-release, version {__version__}\n"

    # Act
    proc = subprocess.run(  # noqa: S602, PLW1510
        command, shell=True, text=True, capture_output=True
    )

    # Evaluate
    assert SUCCESS_EXIT_CODE == proc.returncode  # noqa: SIM300
    assert expected_output == proc.stdout
    assert not proc.stderr


def test_main_prints_version_and_exits(run_cli: RunCliFn):
    cli_cmd = [MAIN_PROG_NAME, "--version"]

    # Act
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert result.output == f"semantic-release, version {__version__}\n"


def test_main_no_args_passes_w_help_text():
    from semantic_release.cli.commands.main import main

    cli_cmd = [MAIN_PROG_NAME]
    result = CliRunner().invoke(main, prog_name=cli_cmd[0])
    assert_successful_exit_code(result, cli_cmd)
    assert "Usage: " in result.output


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)],
)
def test_not_a_release_branch_exit_code(
    repo_result: BuiltRepoResult, run_cli: RunCliFn
):
    # Run anything that doesn't trigger the help text
    repo_result["repo"].git.checkout("-b", "branch-does-not-exist")

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-commit"]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)],
)
def test_not_a_release_branch_exit_code_with_strict(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
):
    # Run anything that doesn't trigger the help text
    repo_result["repo"].git.checkout("-b", "branch-does-not-exist")

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD, "--no-commit"]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)],
)
def test_not_a_release_branch_detached_head_exit_code(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
):
    expected_err_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made"
    )

    # cause repo to be in detached head state without file changes
    repo_result["repo"].git.checkout("HEAD", "--detach")

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-commit"]
    result = run_cli(cli_cmd[1:])

    # detached head states should throw an error as release branches cannot be determined
    assert_exit_code(1, result, cli_cmd)
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


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_default_config_is_used_when_none_in_toml_config_file(
    run_cli: RunCliFn,
    toml_file_with_no_configuration_for_psr: Path,
):
    cli_cmd = [
        MAIN_PROG_NAME,
        "--noop",
        "--config",
        str(toml_file_with_no_configuration_for_psr),
        VERSION_SUBCMD,
    ]

    # Act
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_default_config_is_used_when_none_in_json_config_file(
    run_cli: RunCliFn,
    json_file_with_no_configuration_for_psr: Path,
):
    cli_cmd = [
        MAIN_PROG_NAME,
        "--noop",
        "--config",
        str(json_file_with_no_configuration_for_psr),
        VERSION_SUBCMD,
    ]

    # Act
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_errors_when_config_file_does_not_exist_and_passed_explicitly(
    run_cli: RunCliFn,
):
    cli_cmd = [
        MAIN_PROG_NAME,
        "--noop",
        "--config",
        "somenonexistantfile.123.txt",
        VERSION_SUBCMD,
    ]

    # Act
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert "does not exist" in result.stderr


@pytest.mark.usefixtures(repo_w_no_tags_conventional_commits.__name__)
def test_errors_when_config_file_invalid_configuration(
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    strip_logging_messages: StripLoggingMessagesFn,
    pyproject_toml_file: Path,
):
    # Setup
    update_pyproject_toml("tool.semantic_release.remote.type", "invalidType")
    cli_cmd = [MAIN_PROG_NAME, "--config", str(pyproject_toml_file), VERSION_SUBCMD]

    # Act
    result = run_cli(cli_cmd[1:])

    # preprocess results
    stderr_lines = strip_logging_messages(result.stderr).splitlines()

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert "1 validation error for RawConfig" in stderr_lines[0]
    assert "remote.type" in stderr_lines[1]


def test_uses_default_config_when_no_config_file_found(
    run_cli: RunCliFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    # We have to initialise an empty git repository, as the example projects
    # all have pyproject.toml configs which would be used by default
    with git.Repo.init(example_project_dir) as repo:
        rmtree(str(Path(repo.git_dir, "hooks")))

        repo.git.branch("-M", "main")

        with repo.config_writer("repository") as config:
            config.set_value("user", "name", "semantic release testing")
            config.set_value("user", "email", "not_a_real@email.com")
            config.set_value("commit", "gpgsign", False)
            config.set_value("tag", "gpgsign", False)

        repo.create_remote(name="origin", url="foo@barvcs.com:user/repo.git")
        repo.git.commit("-m", "feat: initial commit", "--allow-empty")

        cli_cmd = [MAIN_PROG_NAME, "--noop", VERSION_SUBCMD]

        # Act
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
