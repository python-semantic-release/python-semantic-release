import pytest

from semantic_release import __version__
from semantic_release.cli import main


def test_main_prints_version_and_exits(cli_runner):
    result = cli_runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"semantic-release, version {__version__}\n"


@pytest.mark.parametrize("args", [[], ["--help"]])
def test_main_prints_help_text(cli_runner, args):
    result = cli_runner.invoke(main, args)
    assert result.exit_code == 0


def test_not_a_release_branch_exit_code(repo_with_git_flow_angular_commits, cli_runner):
    # Run anything that doesn't trigger the help text
    repo_with_git_flow_angular_commits.git.checkout("-b", "branch-does-not-exist")
    result = cli_runner.invoke(main, ["version", "--no-commit"])
    assert result.exit_code == 0


def test_not_a_release_branch_exit_code_with_strict(
    repo_with_git_flow_angular_commits, cli_runner
):
    # Run anything that doesn't trigger the help text
    repo_with_git_flow_angular_commits.git.checkout("-b", "branch-does-not-exist")
    result = cli_runner.invoke(main, ["--strict", "version", "--no-commit"])
    assert result.exit_code != 0


@pytest.mark.usefixtures("example_empty_pyproject_toml")
def test_no_config_section_works_fine(repo_with_git_flow_angular_commits, cli_runner):
    # Don't generate an error when there is no semantic_release config section.
    repo_with_git_flow_angular_commits.git.checkout("-b", "branch-does-not-exist")
    result = cli_runner.invoke(
        main, ["--config", "empty.toml", "version", "--no-commit"]
    )
    assert result.exit_code == 0
