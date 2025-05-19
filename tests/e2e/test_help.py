from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.changelog import changelog
from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.commands.main import main
from semantic_release.cli.commands.publish import publish
from semantic_release.cli.commands.version import version

from tests.const import MAIN_PROG_NAME, SUCCESS_EXIT_CODE
from tests.fixtures.repos import repo_w_trunk_only_conventional_commits
from tests.util import assert_exit_code

if TYPE_CHECKING:
    from click import Command

    from tests.conftest import RunCliFn
    from tests.fixtures import UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult


# Define the expected exit code for the help command
HELP_EXIT_CODE = SUCCESS_EXIT_CODE


@pytest.mark.parametrize(
    "help_option", ("-h", "--help"), ids=lambda opt: opt.lstrip("-")
)
@pytest.mark.parametrize(
    "command",
    (main, changelog, generate_config, publish, version),
    ids=lambda cmd: cmd.name,
)
def test_help_no_repo(
    help_option: str,
    command: Command,
    run_cli: RunCliFn,
    change_to_ex_proj_dir: None,
):
    """
    Test that the help message is displayed even when the current directory is not a git repository
    and there is not a configuration file available.
    Documented issue #840
    """
    # Generate some expected output that should be specific per command
    cmd_usage = str.join(
        " ",
        list(
            filter(
                None,
                [
                    "Usage:",
                    MAIN_PROG_NAME,
                    command.name if command.name != "main" else "",
                    "[OPTIONS]",
                    "" if command.name != main.name else "COMMAND [ARGS]...",
                ],
            )
        ),
    )

    # Create the arguments list for subcommands unless its main
    args = list(
        filter(None, [command.name if command.name != main.name else "", help_option])
    )

    # Run the command with the help option
    result = run_cli(args, invoke_kwargs={"prog_name": MAIN_PROG_NAME})

    # Evaluate result
    assert_exit_code(HELP_EXIT_CODE, result, [MAIN_PROG_NAME, *args])
    assert cmd_usage in result.output


@pytest.mark.parametrize(
    "help_option", ("-h", "--help"), ids=lambda opt: opt.lstrip("-")
)
@pytest.mark.parametrize(
    "command",
    (main, changelog, generate_config, publish, version),
    ids=lambda cmd: cmd.name,
)
@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_help_valid_config(
    help_option: str,
    command: Command,
    run_cli: RunCliFn,
):
    """
    Test that the help message is displayed when the current directory is a git repository
    and there is a valid configuration file available.
    Documented issue #840
    """
    cmd_usage = str.join(
        " ",
        list(
            filter(
                None,
                [
                    "Usage:",
                    MAIN_PROG_NAME,
                    command.name if command.name != main.name else "",
                    "[OPTIONS]",
                    "" if command.name != main.name else "COMMAND [ARGS]...",
                ],
            )
        ),
    )

    # Create the arguments list for subcommands unless its main
    args = list(
        filter(None, [command.name if command.name != main.name else "", help_option])
    )

    # Run the command with the help option
    result = run_cli(args, invoke_kwargs={"prog_name": MAIN_PROG_NAME})

    # Evaluate result
    assert_exit_code(HELP_EXIT_CODE, result, [MAIN_PROG_NAME, *args])
    assert cmd_usage in result.output


@pytest.mark.parametrize(
    "help_option", ("-h", "--help"), ids=lambda opt: opt.lstrip("-")
)
@pytest.mark.parametrize(
    "command",
    (main, changelog, generate_config, publish, version),
    ids=lambda cmd: cmd.name,
)
@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_help_invalid_config(
    help_option: str,
    command: Command,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    """
    Test that the help message is displayed when the current directory is a git repository
    and there is an invalid configuration file available.
    Documented issue #840
    """
    # Update the configuration file to have an invalid value
    update_pyproject_toml("tool.semantic_release.remote.type", "invalidhvcs")

    # Generate some expected output that should be specific per command
    cmd_usage = str.join(
        " ",
        list(
            filter(
                None,
                [
                    "Usage:",
                    MAIN_PROG_NAME,
                    command.name if command.name != "main" else "",
                    "[OPTIONS]",
                    "" if command.name != main.name else "COMMAND [ARGS]...",
                ],
            )
        ),
    )

    # Create the arguments list for subcommands unless its main
    args = list(
        filter(None, [command.name if command.name != main.name else "", help_option])
    )

    # Run the command with the help option
    result = run_cli(args, invoke_kwargs={"prog_name": MAIN_PROG_NAME})

    # Evaluate result
    assert_exit_code(HELP_EXIT_CODE, result, [MAIN_PROG_NAME, *args])
    assert cmd_usage in result.output


@pytest.mark.parametrize(
    "help_option", ("-h", "--help"), ids=lambda opt: opt.lstrip("-")
)
@pytest.mark.parametrize(
    "command",
    (main, changelog, generate_config, publish, version),
    ids=lambda cmd: cmd.name,
)
@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_help_non_release_branch(
    help_option: str,
    command: Command,
    run_cli: RunCliFn,
    repo_result: BuiltRepoResult,
):
    """
    Test that the help message is displayed even when the current branch is not a release branch.
    Documented issue #840
    """
    # Create & checkout a non-release branch
    non_release_branch = repo_result["repo"].create_head("feature-branch")
    non_release_branch.checkout()

    # Generate some expected output that should be specific per command
    cmd_usage = str.join(
        " ",
        list(
            filter(
                None,
                [
                    "Usage:",
                    MAIN_PROG_NAME,
                    command.name if command.name != "main" else "",
                    "[OPTIONS]",
                    "" if command.name != main.name else "COMMAND [ARGS]...",
                ],
            )
        ),
    )

    # Create the arguments list for subcommands unless its main
    args = list(
        filter(None, [command.name if command.name != main.name else "", help_option])
    )

    # Run the command with the help option
    result = run_cli(args, invoke_kwargs={"prog_name": MAIN_PROG_NAME})

    # Evaluate result
    assert_exit_code(HELP_EXIT_CODE, result, [MAIN_PROG_NAME, *args])
    assert cmd_usage in result.output
