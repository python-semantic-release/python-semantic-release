from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import shellingham
import tomlkit
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import repo_with_single_branch_angular_commits
from tests.util import assert_successful_exit_code, get_func_qual_name

if TYPE_CHECKING:
    from click.testing import CliRunner
    from git import Repo

    from tests.fixtures.example_project import GetWheelFileFn, UpdatePyprojectTomlFn


@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
@pytest.mark.parametrize(
    "shell",
    filter(
        None,
        [
            # because we will actually run the build command in this shell, we must ensure it exists
            "bash"
            if list(
                filter(
                    lambda sh_exe: Path(sh_exe).exists(),
                    ("/bin/bash", "/usr/bin/bash", "/usr/local/bin/bash"),
                )
            )
            else "",
            "zsh"
            if list(
                filter(
                    lambda sh_exe: Path(sh_exe).exists(),
                    ("/bin/zsh", "/usr/bin/zsh", "/usr/local/bin/zsh"),
                )
            )
            else "",
        ],
    )
    or ["sh"],
)
@pytest.mark.parametrize(
    "repo, cli_args, next_release_version",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            ["--patch"],
            "0.1.2",
        )
    ],
)
def test_version_runs_build_command(
    repo: Repo,
    cli_args: list[str],
    next_release_version: str,
    cli_runner: CliRunner,
    shell: str,
    get_wheel_file: GetWheelFileFn,
    example_pyproject_toml: Path,
    mocked_git_push: mock.MagicMock,
    post_mocker: mock.Mock,
):
    # Setup
    built_wheel_file = get_wheel_file(next_release_version)
    pyproject_config = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8"))
    build_command = pyproject_config["tool"]["semantic_release"]["build_command"]  # type: ignore[attr-defined]
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
    }

    # Wrap subprocess.run to capture the arguments to the call
    with mock.patch(
        get_func_qual_name(subprocess.run),
        wraps=subprocess.run,
    ) as patched_subprocess_run, mock.patch(
        get_func_qual_name(shellingham.detect_shell), return_value=(shell, shell)
    ), mock.patch.dict(os.environ, patched_os_environment, clear=True):
        # ACT: run & force a new version that will trigger the build command
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        patched_subprocess_run.assert_called_with(
            [shell, "-c", build_command],
            check=True,
            env={
                "NEW_VERSION": next_release_version,  # injected into environment
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

        assert built_wheel_file.exists()
        assert mocked_git_push.call_count == 2
        assert post_mocker.call_count == 1


@pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
@pytest.mark.parametrize("shell", ("powershell", "pwsh", "cmd"))
@pytest.mark.parametrize(
    "repo, cli_args, next_release_version",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            ["--patch"],
            "0.1.2",
        )
    ],
)
def test_version_runs_build_command_windows(
    repo: Repo,
    cli_args: list[str],
    next_release_version: str,
    cli_runner: CliRunner,
    shell: str,
    get_wheel_file: GetWheelFileFn,
    example_pyproject_toml: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_push: mock.MagicMock,
    post_mocker: mock.Mock,
):
    if shell == "cmd":
        build_result_file = get_wheel_file("%NEW_VERSION%")
        update_pyproject_toml(
            "tool.semantic_release.build_command",
            str.join(
                " && ",
                [
                    f"mkdir {build_result_file.parent}",
                    f"type nul > {build_result_file}",
                    f"echo 'Built distribution: {build_result_file}'",
                ],
            ),
        )

    # Setup
    built_wheel_file = get_wheel_file(next_release_version)
    pyproject_config = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8"))
    build_command = pyproject_config["tool"]["semantic_release"]["build_command"]  # type: ignore[attr-defined]
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

    # Wrap subprocess.run to capture the arguments to the call
    with mock.patch(
        get_func_qual_name(subprocess.run),
        wraps=subprocess.run,
    ) as patched_subprocess_run, mock.patch(
        get_func_qual_name(shellingham.detect_shell), return_value=(shell, shell)
    ), mock.patch.dict(os.environ, patched_os_environment, clear=True):
        # ACT: run & force a new version that will trigger the build command
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
        result = cli_runner.invoke(main, cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        patched_subprocess_run.assert_called_once_with(
            [shell, "/c" if shell == "cmd" else "-Command", build_command],
            check=True,
            env={
                "NEW_VERSION": next_release_version,  # injected into environment
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

        dist_file_exists = built_wheel_file.exists()
        assert dist_file_exists, f"\n  Expected wheel file to be created at {built_wheel_file}, but it does not exist."
        assert mocked_git_push.call_count == 2
        assert post_mocker.call_count == 1


@pytest.mark.parametrize(
    "repo, cli_args, next_release_version",
    [
        (
            lazy_fixture(repo_with_single_branch_angular_commits.__name__),
            ["--patch"],
            "0.1.2",
        )
    ],
)
def test_version_runs_build_command_w_user_env(
    repo: Repo,
    cli_args: list[str],
    next_release_version: str,
    cli_runner: CliRunner,
    example_pyproject_toml: Path,
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
    pyproject_config = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8"))
    build_command = pyproject_config["tool"]["semantic_release"]["build_command"]  # type: ignore[attr-defined]
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
        return_value=subprocess.CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run, mock.patch(
        get_func_qual_name(shellingham.detect_shell),
        return_value=("bash", "/usr/bin/bash"),
    ), mock.patch.dict(os.environ, patched_os_environment, clear=True):
        cli_cmd = [
            MAIN_PROG_NAME,
            VERSION_SUBCMD,
            *cli_args,
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
                "NEW_VERSION": next_release_version,  # injected into environment
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


@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_version_skips_build_command_with_skip_build(
    cli_runner: CliRunner,
    mocked_git_push: mock.MagicMock,
    post_mocker: mock.Mock,
):
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch", "--skip-build"]

    with mock.patch(
        get_func_qual_name(subprocess.run),
        return_value=subprocess.CompletedProcess(args=(), returncode=0),
    ) as patched_subprocess_run:
        # Act: force a new version
        result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    patched_subprocess_run.assert_not_called()

    assert mocked_git_push.call_count == 2
    assert post_mocker.call_count == 1
