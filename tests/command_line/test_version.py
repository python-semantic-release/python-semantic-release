from __future__ import annotations

import difflib
import filecmp
import os
import re
import shutil
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import tomlkit
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main
from semantic_release.hvcs.github import Github

from tests.const import (
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    MAIN_PROG_NAME,
    VERSION_SUBCMD,
)
from tests.fixtures import (
    repo_w_github_flow_w_feature_release_channel_angular_commits,
    repo_with_git_flow_and_release_channels_angular_commits,
    repo_with_git_flow_angular_commits,
    repo_with_no_tags_angular_commits,
    repo_with_single_branch_and_prereleases_angular_commits,
    repo_with_single_branch_angular_commits,
)
from tests.util import (
    actions_output_to_dict,
    assert_exit_code,
    assert_successful_exit_code,
    flatten_dircmp,
    get_func_qual_name,
    get_release_history_from_context,
    remove_dir_tree,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.command_line.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        UpdatePyprojectTomlFn,
        UseReleaseNotesTemplateFn,
    )
    from tests.fixtures.git_repo import SimulateChangeCommitsNReturnChangelogEntryFn


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_with_no_tags_angular_commits.__name__),
        lazy_fixture(repo_with_single_branch_angular_commits.__name__),
        lazy_fixture(repo_with_single_branch_and_prereleases_angular_commits.__name__),
        lazy_fixture(
            repo_w_github_flow_w_feature_release_channel_angular_commits.__name__
        ),
        lazy_fixture(repo_with_git_flow_angular_commits.__name__),
        lazy_fixture(repo_with_git_flow_and_release_channels_angular_commits.__name__),
    ],
)
def test_version_noop_is_noop(
    tmp_path_factory: pytest.TempPathFactory,
    example_project_dir: ExProjectDir,
    repo: Repo,
    cli_runner: CliRunner,
):
    # Make a commit to ensure we have something to release
    # otherwise the "no release will be made" logic will kick in first
    new_file = example_project_dir / "temp.txt"
    new_file.write_text("noop version test")

    repo.git.add(str(new_file.resolve()))
    repo.git.commit(m="feat: temp new file")

    tempdir = tmp_path_factory.mktemp("test_noop")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)

    head_before = repo.head.commit
    tags_before = sorted(repo.tags, key=lambda tag: tag.name)

    cli_cmd = [MAIN_PROG_NAME, "--noop", VERSION_SUBCMD]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Grab measurement values after the command
    tags_after = sorted(repo.tags, key=lambda tag: tag.name)
    head_after = repo.head.commit
    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)
    differing_files = flatten_dircmp(dcmp)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not differing_files
    assert tags_before == tags_after
    assert head_before == head_after


# NOTE: we are adding a "fix" commit in the test so with no args/no forcing,
# prerelease revisions get bumped for repos where the initial commit is a
# prerelease
@pytest.mark.parametrize(
    "repo, cli_args, expected_stdout",
    [
        *[
            (
                lazy_fixture(repo_with_no_tags_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.1.0"),
                (["--build-metadata", "build.12345"], "0.1.0+build.12345"),
                (["--prerelease"], "0.0.0-rc.1"),
                (["--patch"], "0.0.1"),
                (["--minor"], "0.1.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.0.0-rc.1"),
                (["--patch", "--as-prerelease"], "0.0.1-rc.1"),
                (["--minor", "--as-prerelease"], "0.1.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.0.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(repo_with_single_branch_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.1.2"),
                (["--build-metadata", "build.12345"], "0.1.2+build.12345"),
                (["--prerelease"], "0.1.1-rc.1"),
                (["--patch"], "0.1.2"),
                (["--minor"], "0.2.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.1.1-rc.1"),
                (["--patch", "--as-prerelease"], "0.1.2-rc.1"),
                (["--minor", "--as-prerelease"], "0.2.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.1.2-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    repo_with_single_branch_and_prereleases_angular_commits.__name__
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.2.1"),
                (["--build-metadata", "build.12345"], "0.2.1+build.12345"),
                # There is already a 0.2.0-rc.1
                (["--prerelease"], "0.2.0-rc.2"),
                (["--patch"], "0.2.1"),
                (["--minor"], "0.3.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.2.0-rc.2"),
                (["--patch", "--as-prerelease"], "0.2.1-rc.1"),
                (["--minor", "--as-prerelease"], "0.3.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    "repo_w_github_flow_w_feature_release_channel_angular_commits"
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.3.0-beta.2"),
                (["--build-metadata", "build.12345"], "0.3.0-beta.2+build.12345"),
                (["--prerelease"], "0.3.0-beta.2"),
                (["--patch"], "0.3.1"),
                (["--minor"], "0.4.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.3.0-beta.2"),
                (["--patch", "--as-prerelease"], "0.3.1-beta.1"),
                (["--minor", "--as-prerelease"], "0.4.0-beta.1"),
                (["--major", "--as-prerelease"], "1.0.0-beta.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "rc"],
                    "0.3.1-rc.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(repo_with_git_flow_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "1.2.0-alpha.3"),
                (["--build-metadata", "build.12345"], "1.2.0-alpha.3+build.12345"),
                (["--prerelease"], "1.2.0-alpha.3"),
                (["--patch"], "1.2.1"),
                (["--minor"], "1.3.0"),
                (["--major"], "2.0.0"),
                (["--prerelease", "--as-prerelease"], "1.2.0-alpha.3"),
                (["--patch", "--as-prerelease"], "1.2.1-alpha.1"),
                (["--minor", "--as-prerelease"], "1.3.0-alpha.1"),
                (["--major", "--as-prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "1.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    repo_with_git_flow_and_release_channels_angular_commits.__name__
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "1.1.0-alpha.4"),
                (["--build-metadata", "build.12345"], "1.1.0-alpha.4+build.12345"),
                (["--prerelease"], "1.1.0-alpha.4"),
                (["--patch"], "1.1.1"),
                (["--minor"], "1.2.0"),
                (["--major"], "2.0.0"),
                (["--prerelease", "--as-prerelease"], "1.1.0-alpha.4"),
                (["--patch", "--as-prerelease"], "1.1.1-alpha.1"),
                (["--minor", "--as-prerelease"], "1.2.0-alpha.1"),
                (["--major", "--as-prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "1.1.1-beta.1",
                ),
            )
        ],
    ],
)
def test_version_print(
    repo: Repo,
    cli_args: list[str],
    expected_stdout: str,
    example_project_dir: ExProjectDir,
    tmp_path_factory: pytest.TempPathFactory,
    cli_runner: CliRunner,
):
    # Make a commit to ensure we have something to release
    # otherwise the "no release will be made" logic will kick in first
    new_file = example_project_dir / "temp.txt"
    new_file.write_text("noop version test")

    repo.git.add(str(new_file.resolve()))
    repo.git.commit(m="fix: temp new file")

    tempdir = tmp_path_factory.mktemp("test_version_print")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)
    head_before = repo.head.commit
    tags_before = sorted(repo.tags, key=lambda tag: tag.name)

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args, "--print"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Grab measurement values after the command
    tags_after = sorted(repo.tags, key=lambda tag: tag.name)
    head_after = repo.head.commit
    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)
    differing_files = flatten_dircmp(dcmp)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert tags_before == tags_after
    assert head_before == head_after
    assert result.stdout.rstrip("\n") == expected_stdout
    assert not differing_files


@pytest.mark.parametrize(
    "repo",
    [
        # This project is yet to add any tags, so a release would be triggered
        # so excluding lazy_fixture(repo_with_no_tags_angular_commits.__name__),
        lazy_fixture(repo_with_single_branch_angular_commits.__name__),
        lazy_fixture(repo_with_single_branch_and_prereleases_angular_commits.__name__),
        lazy_fixture(
            repo_w_github_flow_w_feature_release_channel_angular_commits.__name__
        ),
        lazy_fixture(repo_with_git_flow_angular_commits.__name__),
        lazy_fixture(repo_with_git_flow_and_release_channels_angular_commits.__name__),
    ],
)
def test_version_already_released_no_push(repo: Repo, cli_runner: CliRunner):
    # In these tests, unless arguments are supplied then the latest version
    # has already been released, so we expect an exit code of 2 with the message
    # to indicate that no release will be made
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD, "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert "no release will be made" in result.stderr.lower()


@pytest.mark.parametrize(
    "repo, cli_args, expected_new_version",
    [
        *[
            (
                lazy_fixture(repo_with_no_tags_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.1.0+build.12345"),
                (["--prerelease"], "0.0.0-rc.1"),
                (["--patch"], "0.0.1"),
                (["--minor"], "0.1.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.0.0-rc.1"),
                (["--patch", "--as-prerelease"], "0.0.1-rc.1"),
                (["--minor", "--as-prerelease"], "0.1.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.0.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(repo_with_single_branch_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.1.1+build.12345"),
                (["--prerelease"], "0.1.1-rc.1"),
                (["--patch"], "0.1.2"),
                (["--minor"], "0.2.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.1.1-rc.1"),
                (["--patch", "--as-prerelease"], "0.1.2-rc.1"),
                (["--minor", "--as-prerelease"], "0.2.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.1.2-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    repo_with_single_branch_and_prereleases_angular_commits.__name__
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.2.0+build.12345"),
                # There is already a 0.2.0-rc.1
                (["--prerelease"], "0.2.0-rc.2"),
                (["--patch"], "0.2.1"),
                (["--minor"], "0.3.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.2.0-rc.2"),
                (["--patch", "--as-prerelease"], "0.2.1-rc.1"),
                (["--minor", "--as-prerelease"], "0.3.0-rc.1"),
                (["--major", "--as-prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "0.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    "repo_w_github_flow_w_feature_release_channel_angular_commits"
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.3.0-beta.1+build.12345"),
                (["--prerelease"], "0.3.0-beta.2"),
                (["--patch"], "0.3.1"),
                (["--minor"], "0.4.0"),
                (["--major"], "1.0.0"),
                (["--prerelease", "--as-prerelease"], "0.3.0-beta.2"),
                (["--patch", "--as-prerelease"], "0.3.1-beta.1"),
                (["--minor", "--as-prerelease"], "0.4.0-beta.1"),
                (["--major", "--as-prerelease"], "1.0.0-beta.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "rc"],
                    "0.3.1-rc.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(repo_with_git_flow_angular_commits.__name__),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "1.2.0-alpha.2+build.12345"),
                (["--prerelease"], "1.2.0-alpha.3"),
                (["--patch"], "1.2.1"),
                (["--minor"], "1.3.0"),
                (["--major"], "2.0.0"),
                (["--prerelease", "--as-prerelease"], "1.2.0-alpha.3"),
                (["--patch", "--as-prerelease"], "1.2.1-alpha.1"),
                (["--minor", "--as-prerelease"], "1.3.0-alpha.1"),
                (["--major", "--as-prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "1.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture(
                    repo_with_git_flow_and_release_channels_angular_commits.__name__
                ),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "1.1.0-alpha.3+build.12345"),
                (["--prerelease"], "1.1.0-alpha.4"),
                (["--patch"], "1.1.1"),
                (["--minor"], "1.2.0"),
                (["--major"], "2.0.0"),
                (["--prerelease", "--as-prerelease"], "1.1.0-alpha.4"),
                (["--patch", "--as-prerelease"], "1.1.1-alpha.1"),
                (["--minor", "--as-prerelease"], "1.2.0-alpha.1"),
                (["--major", "--as-prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--as-prerelease", "--prerelease-token", "beta"],
                    "1.1.1-beta.1",
                ),
            )
        ],
    ],
)
def test_version_no_push_force_level(
    repo: Repo,
    cli_args: list[str],
    expected_new_version: str,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    tmp_path_factory: pytest.TempPathFactory,
    cli_runner: CliRunner,
):
    tempdir = tmp_path_factory.mktemp("test_version")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)
    head_before = repo.head.commit
    tags_before = sorted(repo.tags, key=lambda tag: tag.name)

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args, "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Grab measurement values after the command
    tags_after = sorted(repo.tags, key=lambda tag: tag.name)
    head_after = repo.head.commit

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert set(tags_before) < set(tags_after)
    assert head_before != head_after  # A commit has been made
    assert head_before in repo.head.commit.parents

    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)
    differing_files = sorted(flatten_dircmp(dcmp))

    # Changelog already reflects changes this should introduce
    assert differing_files == sorted(
        [
            "CHANGELOG.md",
            "pyproject.toml",
            str(Path(f"src/{EXAMPLE_PROJECT_NAME}/_version.py")),
        ]
    )

    # Compare pyproject.toml
    new_pyproject_toml = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    old_pyproject_toml = tomlkit.loads(
        (tempdir / "pyproject.toml").read_text(encoding="utf-8")
    )

    old_pyproject_toml["tool"]["poetry"].pop("version")  # type: ignore[attr-defined]
    new_version = new_pyproject_toml["tool"]["poetry"].pop(  # type: ignore[attr-defined]  # type: ignore[attr-defined]
        "version"
    )

    assert old_pyproject_toml == new_pyproject_toml
    assert new_version == expected_new_version

    # Compare _version.py
    new_init_py = (
        (example_project_dir / "src" / EXAMPLE_PROJECT_NAME / "_version.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )
    old_init_py = (
        (tempdir / "src" / EXAMPLE_PROJECT_NAME / "_version.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )

    d = difflib.Differ()
    diff = list(d.compare(old_init_py, new_init_py))
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    assert len(removed) == 1
    assert re.match('__version__ = ".*"', removed[0])
    assert added == [f'__version__ = "{expected_new_version}"\n']


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_with_single_branch_angular_commits.__name__),
        lazy_fixture(repo_with_single_branch_and_prereleases_angular_commits.__name__),
        lazy_fixture(
            repo_w_github_flow_w_feature_release_channel_angular_commits.__name__
        ),
        lazy_fixture(repo_with_git_flow_angular_commits.__name__),
        lazy_fixture(repo_with_git_flow_and_release_channels_angular_commits.__name__),
    ],
)
def test_version_build_metadata_triggers_new_version(repo: Repo, cli_runner: CliRunner):
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD, "--no-push"]

    # Verify we get "no version to release" without build metadata
    no_metadata_result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate no version was released because metadata is required to release at this point
    assert_exit_code(2, no_metadata_result, cli_cmd)
    assert "no release will be made" in no_metadata_result.stderr.lower()

    metadata_suffix = "build.abc-12345"

    # Verify we get a new version with build metadata
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--no-push",
        "--build-metadata",
        metadata_suffix,
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert repo.git.tag(l=f"*{metadata_suffix}")


def test_version_prints_current_version_if_no_new_version(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert "no release will be made" in result.stderr.lower()
    assert result.stdout == "1.2.0-alpha.2\n"


def test_version_version_no_verify(
    repo_with_single_branch_angular_commits: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    # setup: set configuration setting
    update_pyproject_toml("tool.semantic_release.no_git_verify", True)
    repo_with_single_branch_angular_commits.git.commit(
        m="chore: adjust project configuration for --no-verify release commits", a=True
    )
    # create executable pre-commit script
    precommit_hook = Path(
        repo_with_single_branch_angular_commits.git_dir, "hooks", "pre-commit"
    )
    precommit_hook.parent.mkdir(parents=True, exist_ok=True)
    precommit_hook.write_text(
        dedent(
            """\
            #!/bin/sh
            echo >&2 "Always fail pre-commit" && exit 1;
            """
        )
    )
    precommit_hook.chmod(0o754)
    repo_with_single_branch_angular_commits.git.config(
        "core.hookspath",
        str(
            precommit_hook.parent.relative_to(
                repo_with_single_branch_angular_commits.working_dir
            )
        ),
        local=True,
    )

    # Take measurement beforehand
    head_before = repo_with_single_branch_angular_commits.head.commit

    # Execute
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-tag", "--no-push"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Take measurement after the command
    head_after = repo_with_single_branch_angular_commits.head.commit

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert head_before != head_after  # A commit has been made
    assert head_before in repo_with_single_branch_angular_commits.head.commit.parents


@pytest.mark.parametrize("shell", ("/usr/bin/bash", "/usr/bin/zsh"))
def test_version_runs_build_command(
    repo_with_git_flow_angular_commits: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    shell: str,
):
    # Setup
    build_command = "bash -c \"echo 'hello world'\""
    update_pyproject_toml("tool.semantic_release.build_command", build_command)
    exe = shell.split("/")[-1]
    patched_os_environment = {
        "CI": "true",
        "PATH": os.getenv("PATH", ""),
        "HOME": "/home/username",
        "VIRTUAL_ENV": "./.venv",
        # Simulate that all CI's are set
        "GITHUB_ACTIONS": "true",
        "GITLAB_CI": "true",
        "GITEA_ACTIONS": "true",
        "BITBUCKET_REPO_FULL_NAME": "python-semantic-release/python-semantic-release.git",
        "PSR_DOCKER_GITHUB_ACTION": "true",
        # Windows
        "ALLUSERSAPPDATA": "C:\\ProgramData",
        "ALLUSERSPROFILE": "C:\\ProgramData",
        "APPDATA": "C:\\Users\\Username\\AppData\\Roaming",
        "COMMONPROGRAMFILES": "C:\\Program Files\\Common Files",
        "COMMONPROGRAMFILES(X86)": "C:\\Program Files (x86)\\Common Files",
        "DEFAULTUSERPROFILE": "C:\\Users\\Default",
        "HOMEPATH": "\\Users\\Username",
        "PATHEXT": ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC",
        "PROFILESFOLDER": "C:\\Users",
        "PROGRAMFILES": "C:\\Program Files",
        "PROGRAMFILES(X86)": "C:\\Program Files (x86)",
        "SYSTEM": "C:\\Windows\\System32",
        "SYSTEM16": "C:\\Windows\\System16",
        "SYSTEM32": "C:\\Windows\\System32",
        "SYSTEMDRIVE": "C:",
        "SYSTEMROOT": "C:\\Windows",
        "TEMP": "C:\\Users\\Username\\AppData\\Local\\Temp",
        "TMP": "C:\\Users\\Username\\AppData\\Local\\Temp",
        "USERPROFILE": "C:\\Users\\Username",
        "USERSID": "S-1-5-21-1234567890-123456789-123456789-1234",
        "USERNAME": "Username",  # must include for python getpass.getuser() on windows
        "WINDIR": "C:\\Windows",
    }

    # Mock out subprocess.run
    with mock.patch(
        get_func_qual_name(subprocess.run),
        return_value=CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run, mock.patch(
        "shellingham.detect_shell", return_value=(exe, shell)
    ), mock.patch("sys.platform", "linux"), mock.patch.dict(
        os.environ, patched_os_environment, clear=True
    ):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push"]

        # ACT: run & force a new version that will trigger the build command
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        patched_subprocess_run.assert_called_once_with(
            [exe, "-c", build_command],
            check=True,
            env={
                "NEW_VERSION": "1.2.1",  # injected into environment
                "CI": patched_os_environment["CI"],
                "BITBUCKET_CI": "true",  # Converted
                "GITHUB_ACTIONS": patched_os_environment["GITHUB_ACTIONS"],
                "GITEA_ACTIONS": patched_os_environment["GITEA_ACTIONS"],
                "GITLAB_CI": patched_os_environment["GITLAB_CI"],
                "HOME": patched_os_environment["HOME"],
                "PATH": patched_os_environment["PATH"],
                "VIRTUAL_ENV": patched_os_environment["VIRTUAL_ENV"],
                "PSR_DOCKER_GITHUB_ACTION": patched_os_environment[
                    "PSR_DOCKER_GITHUB_ACTION"
                ],
            },
        )


@pytest.mark.parametrize("shell", ("powershell", "pwsh", "cmd"))
def test_version_runs_build_command_windows(
    repo_with_git_flow_angular_commits: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    shell: str,
):
    # Setup
    build_command = "bash -c \"echo 'hello world'\""
    update_pyproject_toml("tool.semantic_release.build_command", build_command)
    exe = shell.split("/")[-1]
    patched_os_environment = {
        "CI": "true",
        "PATH": os.getenv("PATH", ""),
        "HOME": "/home/username",
        "VIRTUAL_ENV": "./.venv",
        # Simulate that all CI's are set
        "GITHUB_ACTIONS": "true",
        "GITLAB_CI": "true",
        "GITEA_ACTIONS": "true",
        "BITBUCKET_REPO_FULL_NAME": "python-semantic-release/python-semantic-release.git",
        "PSR_DOCKER_GITHUB_ACTION": "true",
        # Windows
        "ALLUSERSAPPDATA": "C:\\ProgramData",
        "ALLUSERSPROFILE": "C:\\ProgramData",
        "APPDATA": "C:\\Users\\Username\\AppData\\Roaming",
        "COMMONPROGRAMFILES": "C:\\Program Files\\Common Files",
        "COMMONPROGRAMFILES(X86)": "C:\\Program Files (x86)\\Common Files",
        "DEFAULTUSERPROFILE": "C:\\Users\\Default",
        "HOMEPATH": "\\Users\\Username",
        "PATHEXT": ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC",
        "PROFILESFOLDER": "C:\\Users",
        "PROGRAMFILES": "C:\\Program Files",
        "PROGRAMFILES(X86)": "C:\\Program Files (x86)",
        "SYSTEM": "C:\\Windows\\System32",
        "SYSTEM16": "C:\\Windows\\System16",
        "SYSTEM32": "C:\\Windows\\System32",
        "SYSTEMDRIVE": "C:",
        "SYSTEMROOT": "C:\\Windows",
        "TEMP": "C:\\Users\\Username\\AppData\\Local\\Temp",
        "TMP": "C:\\Users\\Username\\AppData\\Local\\Temp",
        "USERPROFILE": "C:\\Users\\Username",
        "USERSID": "S-1-5-21-1234567890-123456789-123456789-1234",
        "USERNAME": "Username",  # must include for python getpass.getuser() on windows
        "WINDIR": "C:\\Windows",
    }

    # Mock out subprocess.run
    with mock.patch(
        get_func_qual_name(subprocess.run),
        return_value=CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run, mock.patch(
        "shellingham.detect_shell", return_value=(exe, shell)
    ), mock.patch("sys.platform", "win32"), mock.patch.dict(
        os.environ, patched_os_environment, clear=True
    ):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push"]

        # ACT: run & force a new version that will trigger the build command
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        patched_subprocess_run.assert_called_once_with(
            [exe, "/c" if shell == "cmd" else "-Command", build_command],
            check=True,
            env={
                "NEW_VERSION": "1.2.1",  # injected into environment
                "CI": patched_os_environment["CI"],
                "BITBUCKET_CI": "true",  # Converted
                "GITHUB_ACTIONS": patched_os_environment["GITHUB_ACTIONS"],
                "GITEA_ACTIONS": patched_os_environment["GITEA_ACTIONS"],
                "GITLAB_CI": patched_os_environment["GITLAB_CI"],
                "HOME": patched_os_environment["HOME"],
                "PATH": patched_os_environment["PATH"],
                "VIRTUAL_ENV": patched_os_environment["VIRTUAL_ENV"],
                "PSR_DOCKER_GITHUB_ACTION": patched_os_environment[
                    "PSR_DOCKER_GITHUB_ACTION"
                ],
                # Windows
                "ALLUSERSAPPDATA": patched_os_environment["ALLUSERSAPPDATA"],
                "ALLUSERSPROFILE": patched_os_environment["ALLUSERSPROFILE"],
                "APPDATA": patched_os_environment["APPDATA"],
                "COMMONPROGRAMFILES": patched_os_environment["COMMONPROGRAMFILES"],
                "COMMONPROGRAMFILES(X86)": patched_os_environment[
                    "COMMONPROGRAMFILES(X86)"
                ],
                "DEFAULTUSERPROFILE": patched_os_environment["DEFAULTUSERPROFILE"],
                "HOMEPATH": patched_os_environment["HOMEPATH"],
                "PATHEXT": patched_os_environment["PATHEXT"],
                "PROFILESFOLDER": patched_os_environment["PROFILESFOLDER"],
                "PROGRAMFILES": patched_os_environment["PROGRAMFILES"],
                "PROGRAMFILES(X86)": patched_os_environment["PROGRAMFILES(X86)"],
                "SYSTEM": patched_os_environment["SYSTEM"],
                "SYSTEM16": patched_os_environment["SYSTEM16"],
                "SYSTEM32": patched_os_environment["SYSTEM32"],
                "SYSTEMDRIVE": patched_os_environment["SYSTEMDRIVE"],
                "SYSTEMROOT": patched_os_environment["SYSTEMROOT"],
                "TEMP": patched_os_environment["TEMP"],
                "TMP": patched_os_environment["TMP"],
                "USERPROFILE": patched_os_environment["USERPROFILE"],
                "USERSID": patched_os_environment["USERSID"],
                "WINDIR": patched_os_environment["WINDIR"],
            },
        )


def test_version_runs_build_command_w_user_env(
    repo_with_git_flow_angular_commits: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    # Setup
    patched_os_environment = {
        "CI": "true",
        "PATH": os.getenv("PATH", ""),
        "HOME": "/home/username",
        "VIRTUAL_ENV": "./.venv",
        # Windows
        "USERNAME": "Username",  # must include for python getpass.getuser() on windows
        # Simulate that all CI's are set
        "GITHUB_ACTIONS": "true",
        "GITLAB_CI": "true",
        "GITEA_ACTIONS": "true",
        "BITBUCKET_REPO_FULL_NAME": "python-semantic-release/python-semantic-release.git",
        "PSR_DOCKER_GITHUB_ACTION": "true",
        # User environment variables (varying passthrough results)
        "MY_CUSTOM_VARIABLE": "custom",
        "IGNORED_VARIABLE": "ignore_me",
        "OVERWRITTEN_VAR": "initial",
        "SET_AS_EMPTY_VAR": "not_empty",
    }
    build_command = "bash -c \"echo 'hello world'\""
    update_pyproject_toml("tool.semantic_release.build_command", build_command)
    update_pyproject_toml(
        "tool.semantic_release.build_command_env",
        [
            # Includes arbitrary whitespace which will be removed
            " MY_CUSTOM_VARIABLE ",  # detect and pass from environment
            " OVERWRITTEN_VAR = overrided",  # pass hardcoded value which overrides environment
            " SET_AS_EMPTY_VAR = ",  # keep variable initialized but as empty string
            " HARDCODED_VAR=hardcoded ",  # pass hardcoded value that doesn't override anything
            "VAR_W_EQUALS = a-var===condition",  # only splits on 1st equals sign
            "=ignored-invalid-named-var",  # TODO: validation error instead, but currently just ignore
        ],
    )

    # Mock out subprocess.run
    with mock.patch(
        get_func_qual_name(subprocess.run),
        return_value=CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run, mock.patch(
        "shellingham.detect_shell", return_value=("bash", "/usr/bin/bash")
    ), mock.patch.dict(os.environ, patched_os_environment, clear=True):
        cli_cmd = [
            MAIN_PROG_NAME,
            VERSION_SUBCMD,
            "--patch",
            "--no-commit",
            "--no-tag",
            "--no-changelog",
            "--no-push",
        ]

        # ACT: run & force a new version that will trigger the build command
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        # [1] Make sure it did not error internally
        assert_successful_exit_code(result, cli_cmd)

        # [2] Make sure the subprocess was called with the correct environment
        patched_subprocess_run.assert_called_once_with(
            ["bash", "-c", build_command],
            check=True,
            env={
                "NEW_VERSION": "1.2.1",  # injected into environment
                "CI": patched_os_environment["CI"],
                "BITBUCKET_CI": "true",  # Converted
                "GITHUB_ACTIONS": patched_os_environment["GITHUB_ACTIONS"],
                "GITEA_ACTIONS": patched_os_environment["GITEA_ACTIONS"],
                "GITLAB_CI": patched_os_environment["GITLAB_CI"],
                "HOME": patched_os_environment["HOME"],
                "PATH": patched_os_environment["PATH"],
                "VIRTUAL_ENV": patched_os_environment["VIRTUAL_ENV"],
                "PSR_DOCKER_GITHUB_ACTION": patched_os_environment[
                    "PSR_DOCKER_GITHUB_ACTION"
                ],
                "MY_CUSTOM_VARIABLE": patched_os_environment["MY_CUSTOM_VARIABLE"],
                "OVERWRITTEN_VAR": "overrided",
                "SET_AS_EMPTY_VAR": "",
                "HARDCODED_VAR": "hardcoded",
                # Note that IGNORED_VARIABLE is not here.
                "VAR_W_EQUALS": "a-var===condition",
            },
        )


def test_version_skips_build_command_with_skip_build(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--no-push", "--skip-build"]

    with mock.patch(
        get_func_qual_name(subprocess.run),
        return_value=CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run:
        # Act: force a new version
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        patched_subprocess_run.assert_not_called()


def test_version_writes_github_actions_output(
    repo_with_git_flow_angular_commits: Repo,
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


def test_version_exit_code_when_strict(
    repo_with_git_flow_angular_commits: Repo, cli_runner: CliRunner
):
    cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD, "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)


def test_version_exit_code_when_not_strict(
    repo_with_git_flow_angular_commits: Repo,
    cli_runner: CliRunner,
):
    """Testing 'no release will be made'"""
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-push"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)


@pytest.mark.parametrize(
    "is_strict, exit_code", [(True, 2), (False, 0)], ids=["strict", "non-strict"]
)
def test_version_on_nonrelease_branch(
    repo_with_single_branch_angular_commits: Repo,
    cli_runner: CliRunner,
    is_strict: bool,
    exit_code: int,
):
    branch = repo_with_single_branch_angular_commits.create_head("next")
    branch.checkout()
    expected_error_msg = (
        f"branch '{branch.name}' isn't in any release groups; no release will be made\n"
    )

    # Act
    cli_cmd = list(
        filter(None, [MAIN_PROG_NAME, "--strict" if is_strict else "", VERSION_SUBCMD])
    )
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_exit_code(exit_code, result, cli_cmd)
    assert not result.stdout
    assert expected_error_msg == result.stderr


def test_custom_release_notes_template(
    mocked_git_push: MagicMock,
    repo_with_no_tags_angular_commits: Repo,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    post_mocker: Mocker,
    cli_runner: CliRunner,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    # TODO: Improve test validity... a lot of testing via its own internal functions

    # Setup
    use_release_notes_template()
    runtime_context_with_no_tags = retrieve_runtime_context(
        repo_with_no_tags_angular_commits
    )
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--skip-build", "--vcs-release"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])
    release_history = get_release_history_from_context(runtime_context_with_no_tags)
    tag = repo_with_no_tags_angular_commits.tags[-1].name

    release_version = runtime_context_with_no_tags.version_translator.from_tag(tag)
    if release_version is None:
        raise ValueError(f"Could not translate tag '{tag}' to version")

    release = release_history.released[release_version]

    expected_release_notes = (
        runtime_context_with_no_tags.template_environment.from_string(
            EXAMPLE_RELEASE_NOTES_TEMPLATE
        ).render(version=release_version, release=release)
    )

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None
    assert post_mocker.last_request.json()["body"] == expected_release_notes


def test_version_tag_only_push(
    mocked_git_push: MagicMock,
    repo_with_no_tags_angular_commits: Repo,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    cli_runner: CliRunner,
) -> None:
    # Setup
    retrieve_runtime_context(repo_with_no_tags_angular_commits)
    head_before = repo_with_no_tags_angular_commits.head.commit

    # Act
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--tag",
        "--no-commit",
        "--skip-build",
        "--no-vcs-release",
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # capture values after the command
    tag_after = repo_with_no_tags_angular_commits.tags[-1].name
    head_after = repo_with_no_tags_angular_commits.head.commit

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert tag_after == "v0.1.0"
    assert head_before == head_after
    assert mocked_git_push.call_count == 1  # 0 for commit, 1 for tag


def test_version_only_update_files_no_git_actions(
    mocked_git_push: MagicMock,
    repo_with_single_branch_and_prereleases_angular_commits: Repo,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    cli_runner: CliRunner,
    tmp_path_factory: pytest.TempPathFactory,
    example_pyproject_toml: Path,
    example_project_dir: ExProjectDir,
    example_changelog_md: Path,
) -> None:
    # Setup
    retrieve_runtime_context(repo_with_single_branch_and_prereleases_angular_commits)
    # Remove the previously created changelog to allow for it to be generated
    example_changelog_md.unlink()

    # Arrange
    expected_new_version = "0.3.0"
    tempdir = tmp_path_factory.mktemp("test_version")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir), dst=tempdir)

    head_before = repo_with_single_branch_and_prereleases_angular_commits.head.commit
    tags_before = repo_with_single_branch_and_prereleases_angular_commits.tags

    # Act
    cli_cmd = [
        MAIN_PROG_NAME,
        VERSION_SUBCMD,
        "--minor",
        "--no-tag",
        "--no-commit",
        "--skip-build",
    ]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # capture values after the command
    tags_after = repo_with_single_branch_and_prereleases_angular_commits.tags
    head_after = repo_with_single_branch_and_prereleases_angular_commits.head.commit

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert tags_before == tags_after
    assert head_before == head_after
    # no push as it should be turned off automatically
    assert mocked_git_push.call_count == 0

    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)
    differing_files = sorted(flatten_dircmp(dcmp))

    # Files that should receive version change
    expected_changed_files = sorted(
        [
            "CHANGELOG.md",
            "pyproject.toml",
            str(Path(f"src/{EXAMPLE_PROJECT_NAME}/_version.py")),
        ]
    )
    assert expected_changed_files == differing_files

    # Compare pyproject.toml
    new_pyproject_toml = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    old_pyproject_toml = tomlkit.loads(
        (tempdir / "pyproject.toml").read_text(encoding="utf-8")
    )

    old_pyproject_toml["tool"]["poetry"].pop("version")  # type: ignore[attr-defined]
    new_version = new_pyproject_toml["tool"]["poetry"].pop(  # type: ignore[attr-defined]  # type: ignore[attr-defined]
        "version"
    )

    assert old_pyproject_toml == new_pyproject_toml
    assert new_version == expected_new_version

    # Compare _version.py
    new_version_py = (
        (example_project_dir / "src" / EXAMPLE_PROJECT_NAME / "_version.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )
    old_version_py = (
        (tempdir / "src" / EXAMPLE_PROJECT_NAME / "_version.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )

    d = difflib.Differ()
    diff = list(d.compare(old_version_py, new_version_py))
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    assert len(removed) == 1
    assert re.match('__version__ = ".*"', removed[0])
    assert added == [f'__version__ = "{expected_new_version}"\n']


def test_version_print_last_released_prints_version(
    repo_with_single_branch_tag_commits: Repo, cli_runner: CliRunner
):
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == "0.1.1\n"


def test_version_print_last_released_prints_released_if_commits(
    repo_with_single_branch_tag_commits: Repo,
    example_project_dir: ExProjectDir,
    cli_runner: CliRunner,
):
    new_file = example_project_dir / "temp.txt"
    new_file.write_text("test --print-last-released")

    repo_with_single_branch_tag_commits.git.add(str(new_file.resolve()))
    repo_with_single_branch_tag_commits.git.commit(m="fix: temp new file")

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == "0.1.1\n"


def test_version_print_last_released_prints_nothing_if_no_tags(
    caplog, repo_with_no_tags_angular_commits: Repo, cli_runner: CliRunner
):
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert result.stdout == ""
    assert "No release tags found." in caplog.text


def test_version_print_last_released_on_detached_head(
    cli_runner: CliRunner,
    repo_with_single_branch_tag_commits: Repo,
):
    last_version = "0.1.1"
    repo_with_single_branch_tag_commits.git.checkout("HEAD", detach=True)

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert last_version == result.stdout.rstrip()


def test_version_print_last_released_on_nonrelease_branch(
    cli_runner: CliRunner,
    repo_with_single_branch_tag_commits: Repo,
):
    last_version = "0.1.1"
    repo_with_single_branch_tag_commits.create_head("next").checkout()

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert last_version == result.stdout.rstrip()


def test_version_print_last_released_tag_on_detached_head(
    cli_runner: CliRunner,
    repo_with_single_branch_tag_commits: Repo,
):
    last_version = "v0.1.1"
    repo_with_single_branch_tag_commits.git.checkout("HEAD", detach=True)

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert last_version == result.stdout.rstrip()


def test_version_print_last_released_tag_on_nonrelease_branch(
    cli_runner: CliRunner,
    repo_with_single_branch_tag_commits: Repo,
):
    last_version_tag = "v0.1.1"
    repo_with_single_branch_tag_commits.create_head("next").checkout()

    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print-last-released-tag"]

    # Act
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_successful_exit_code(result, cli_cmd)
    assert not result.stderr
    assert last_version_tag == result.stdout.rstrip()


def test_version_print_next_version_fails_on_detached_head(
    cli_runner: CliRunner,
    example_git_ssh_url: str,
    repo_with_single_branch_tag_commits: Repo,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
):
    # Setup
    repo_with_single_branch_tag_commits.git.checkout("HEAD", detach=True)
    simulate_change_commits_n_rtn_changelog_entry(
        repo_with_single_branch_tag_commits,
        ["fix: make a patch fix to codebase"],
        Github(example_git_ssh_url),
    )
    expected_error_msg = (
        "Detached HEAD state cannot match any release groups; no release will be made\n"
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--print"]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate (expected -> actual)
    assert_exit_code(1, result, cli_cmd)
    assert not result.stdout
    assert expected_error_msg == result.stderr
