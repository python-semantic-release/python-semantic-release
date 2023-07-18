import json
import os
from textwrap import dedent

import git
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


@pytest.fixture
def toml_file_with_no_configuration_for_psr(tmp_path):
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

    yield path


@pytest.fixture
def json_file_with_no_configuration_for_psr(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"foo": [1, 2, 3]}))

    yield path


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_default_config_is_used_when_none_in_toml_config_file(
    cli_runner,
    toml_file_with_no_configuration_for_psr,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", str(toml_file_with_no_configuration_for_psr), "version"],
    )

    assert result.exit_code == 0


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_default_config_is_used_when_none_in_json_config_file(
    cli_runner,
    json_file_with_no_configuration_for_psr,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", str(json_file_with_no_configuration_for_psr), "version"],
    )

    assert result.exit_code == 0


@pytest.mark.usefixtures("repo_with_git_flow_angular_commits")
def test_errors_when_config_file_does_not_exist_and_passed_explicitly(
    cli_runner,
):
    result = cli_runner.invoke(
        main,
        ["--noop", "--config", "somenonexistantfile.123.txt", "version"],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.stderr


def test_uses_default_config_when_no_config_file_found(
    tmp_path,
    cli_runner,
):
    # We have to initialise an empty git repository, as the example projects
    # all have pyproject.toml configs which would be used by default
    repo = git.Repo.init(tmp_path)
    repo.git.branch("-M", "main")
    with repo.config_writer("repository") as config:
        config.set_value("user", "name", "semantic release testing")
        config.set_value("user", "email", "not_a_real@email.com")
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
