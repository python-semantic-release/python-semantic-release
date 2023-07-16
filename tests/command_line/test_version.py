from __future__ import annotations

import difflib
import filecmp
import re
import shutil
from subprocess import CompletedProcess
from unittest import mock

import pytest
import tomlkit
from pytest_lazyfixture import lazy_fixture

from semantic_release.cli import main, version

from tests.const import EXAMPLE_PROJECT_NAME
from tests.util import actions_output_to_dict, flatten_dircmp


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_version_noop_is_noop(tmp_path_factory, example_project, repo, cli_runner):
    # Make a commit to ensure we have something to release
    # otherwise the "no release will be made" logic will kick in first
    new_file = example_project / "temp.txt"
    new_file.write_text("noop version test")

    repo.git.add(str(new_file.resolve()))
    repo.git.commit(m="feat: temp new file")

    tempdir = tmp_path_factory.mktemp("test_noop")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)

    head_before = repo.head.commit
    tags_before = sorted(list(repo.tags), key=lambda tag: tag.name)

    result = cli_runner.invoke(main, ["--noop", version.name])

    tags_after = sorted(list(repo.tags), key=lambda tag: tag.name)
    head_after = repo.head.commit

    assert result.exit_code == 0
    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)

    differing_files = flatten_dircmp(dcmp)
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
                lazy_fixture("repo_with_no_tags_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.1.0"),
                (["--build-metadata", "build.12345"], "0.1.0+build.12345"),
                (["--patch"], "0.0.1"),
                (["--minor"], "0.1.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.0.1-rc.1"),
                (["--minor", "--prerelease"], "0.1.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.0.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_single_branch_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.1.2"),
                (["--build-metadata", "build.12345"], "0.1.2+build.12345"),
                (["--patch"], "0.1.2"),
                (["--minor"], "0.2.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.1.2-rc.1"),
                (["--minor", "--prerelease"], "0.2.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.1.2-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.2.1"),
                (["--build-metadata", "build.12345"], "0.2.1+build.12345"),
                (["--patch"], "0.2.1"),
                (["--minor"], "0.3.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.2.1-rc.1"),
                (["--minor", "--prerelease"], "0.3.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "0.3.0-beta.2"),
                (["--build-metadata", "build.12345"], "0.3.0-beta.2+build.12345"),
                (["--patch"], "0.3.1"),
                (["--minor"], "0.4.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.3.1-beta.1"),
                (["--minor", "--prerelease"], "0.4.0-beta.1"),
                (["--major", "--prerelease"], "1.0.0-beta.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.3.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_git_flow_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "1.2.0-alpha.3"),
                (["--build-metadata", "build.12345"], "1.2.0-alpha.3+build.12345"),
                (["--patch"], "1.2.1"),
                (["--minor"], "1.3.0"),
                (["--major"], "2.0.0"),
                (["--patch", "--prerelease"], "1.2.1-alpha.1"),
                (["--minor", "--prerelease"], "1.3.0-alpha.1"),
                (["--major", "--prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "1.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                ([], "1.1.0-alpha.4"),
                (["--build-metadata", "build.12345"], "1.1.0-alpha.4+build.12345"),
                (["--patch"], "1.1.1"),
                (["--minor"], "1.2.0"),
                (["--major"], "2.0.0"),
                (["--patch", "--prerelease"], "1.1.1-alpha.1"),
                (["--minor", "--prerelease"], "1.2.0-alpha.1"),
                (["--major", "--prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "1.1.1-beta.1",
                ),
            )
        ],
    ],
)
def test_version_print(
    repo, cli_args, expected_stdout, example_project, tmp_path_factory, cli_runner
):
    # Make a commit to ensure we have something to release
    # otherwise the "no release will be made" logic will kick in first
    new_file = example_project / "temp.txt"
    new_file.write_text("noop version test")

    repo.git.add(str(new_file.resolve()))
    repo.git.commit(m="fix: temp new file")

    tempdir = tmp_path_factory.mktemp("test_version_print")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)
    head_before = repo.head.commit
    tags_before = sorted(list(repo.tags), key=lambda tag: tag.name)

    result = cli_runner.invoke(main, [version.name, *cli_args, "--print"])

    tags_after = sorted(list(repo.tags), key=lambda tag: tag.name)
    head_after = repo.head.commit

    assert result.exit_code == 0
    assert tags_before == tags_after
    assert head_before == head_after
    assert result.stdout.rstrip("\n") == expected_stdout
    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)
    differing_files = flatten_dircmp(dcmp)
    assert not differing_files


@pytest.mark.parametrize(
    "repo",
    [
        # This project is yet to add any tags, so a release would be triggered
        # lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_version_already_released_no_push(repo, cli_runner):
    # In these tests, unless arguments are supplied then the latest version
    # has already been released, so we expect an exit code of 2 with the message
    # to indicate that no release will be made
    result = cli_runner.invoke(main, ["--strict", version.name, "--no-push"])
    assert result.exit_code == 2
    assert "no release will be made" in result.stderr.lower()


@pytest.mark.parametrize(
    "repo, cli_args, expected_new_version",
    [
        *[
            (
                lazy_fixture("repo_with_no_tags_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.1.0+build.12345"),
                (["--patch"], "0.0.1"),
                (["--minor"], "0.1.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.0.1-rc.1"),
                (["--minor", "--prerelease"], "0.1.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.0.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_single_branch_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.1.1+build.12345"),
                (["--patch"], "0.1.2"),
                (["--minor"], "0.2.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.1.2-rc.1"),
                (["--minor", "--prerelease"], "0.2.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.1.2-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.2.0+build.12345"),
                (["--patch"], "0.2.1"),
                (["--minor"], "0.3.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.2.1-rc.1"),
                (["--minor", "--prerelease"], "0.3.0-rc.1"),
                (["--major", "--prerelease"], "1.0.0-rc.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "0.3.0-beta.1+build.12345"),
                (["--patch"], "0.3.1"),
                (["--minor"], "0.4.0"),
                (["--major"], "1.0.0"),
                (["--patch", "--prerelease"], "0.3.1-beta.1"),
                (["--minor", "--prerelease"], "0.4.0-beta.1"),
                (["--major", "--prerelease"], "1.0.0-beta.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "0.3.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_git_flow_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "1.2.0-alpha.2+build.12345"),
                (["--patch"], "1.2.1"),
                (["--minor"], "1.3.0"),
                (["--major"], "2.0.0"),
                (["--patch", "--prerelease"], "1.2.1-alpha.1"),
                (["--minor", "--prerelease"], "1.3.0-alpha.1"),
                (["--major", "--prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "1.2.1-beta.1",
                ),
            )
        ],
        *[
            (
                lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
                cli_args,
                expected_stdout,
            )
            for cli_args, expected_stdout in (
                (["--build-metadata", "build.12345"], "1.1.0-alpha.3+build.12345"),
                (["--patch"], "1.1.1"),
                (["--minor"], "1.2.0"),
                (["--major"], "2.0.0"),
                (["--patch", "--prerelease"], "1.1.1-alpha.1"),
                (["--minor", "--prerelease"], "1.2.0-alpha.1"),
                (["--major", "--prerelease"], "2.0.0-alpha.1"),
                (
                    ["--patch", "--prerelease", "--prerelease-token", "beta"],
                    "1.1.1-beta.1",
                ),
            )
        ],
    ],
)
def test_version_no_push_force_level(
    repo,
    cli_args,
    expected_new_version,
    example_project,
    example_pyproject_toml,
    tmp_path_factory,
    cli_runner,
):
    tempdir = tmp_path_factory.mktemp("test_version")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)
    head_before = repo.head.commit
    tags_before = sorted(list(repo.tags), key=lambda tag: tag.name)

    result = cli_runner.invoke(main, [version.name, *cli_args, "--no-push"])

    tags_after = sorted(list(repo.tags), key=lambda tag: tag.name)
    head_after = repo.head.commit

    assert result.exit_code == 0

    assert set(tags_before) < set(tags_after)
    assert head_before != head_after  # A commit has been made
    assert head_before in repo.head.commit.parents

    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)
    differing_files = flatten_dircmp(dcmp)

    # Changelog already reflects changes this should introduce
    assert differing_files == [
        "pyproject.toml",
        f"src/{EXAMPLE_PROJECT_NAME}/__init__.py",
    ]

    # Compare pyproject.toml
    new_pyproject_toml = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    old_pyproject_toml = tomlkit.loads(
        (tempdir / "pyproject.toml").read_text(encoding="utf-8")
    )

    old_pyproject_toml["tool"]["poetry"].pop("version")  # type: ignore
    new_version = new_pyproject_toml["tool"]["poetry"].pop("version")  # type: ignore

    assert old_pyproject_toml == new_pyproject_toml
    assert new_version == expected_new_version

    # Compare __init__.py
    new_init_py = (
        (example_project / "src" / EXAMPLE_PROJECT_NAME / "__init__.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )
    old_init_py = (
        (tempdir / "src" / EXAMPLE_PROJECT_NAME / "__init__.py")
        .read_text(encoding="utf-8")
        .splitlines(keepends=True)
    )

    d = difflib.Differ()
    diff = list(d.compare(old_init_py, new_init_py))
    added = [line[2:] for line in diff if line.startswith("+ ")]
    removed = [line[2:] for line in diff if line.startswith("- ")]

    assert len(removed) == 1 and re.match('__version__ = ".*"', removed[0])
    assert added == [f'__version__ = "{expected_new_version}"\n']


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_version_build_metadata_triggers_new_version(repo, cli_runner):
    # Verify we get "no version to release" without build metadata
    no_metadata_result = cli_runner.invoke(
        main, ["--strict", version.name, "--no-push"]
    )
    assert no_metadata_result.exit_code == 2
    assert "no release will be made" in no_metadata_result.stderr.lower()

    metadata_suffix = "build.abc-12345"
    result = cli_runner.invoke(
        main, [version.name, "--no-push", "--build-metadata", metadata_suffix]
    )
    assert result.exit_code == 0
    assert repo.git.tag(l=f"*{metadata_suffix}")


def test_version_prints_current_version_if_no_new_version(
    repo_with_git_flow_angular_commits, cli_runner
):
    result = cli_runner.invoke(main, [version.name, "--no-push"])
    assert result.exit_code == 0
    assert "no release will be made" in result.stderr.lower()
    assert result.stdout == "1.2.0-alpha.2\n"


@pytest.mark.parametrize("shell", ("/usr/bin/bash", "/usr/bin/zsh", "powershell"))
def test_version_runs_build_command(
    repo_with_git_flow_angular_commits, cli_runner, example_pyproject_toml, shell
):
    config = tomlkit.loads(example_pyproject_toml.read_text(encoding="utf-8"))
    build_command = config["tool"]["semantic_release"]["build_command"]
    exe = shell.split("/")[-1]
    with mock.patch(
        "subprocess.run", return_value=CompletedProcess(args=(), returncode=0)
    ) as patched_subprocess_run, mock.patch(
        "shellingham.detect_shell", return_value=(exe, shell)
    ):
        result = cli_runner.invoke(
            main, [version.name, "--patch", "--no-push"]
        )  # force a new version
        assert result.exit_code == 0

        patched_subprocess_run.assert_called_once_with(
            [exe, "-c", build_command], check=True
        )


def test_version_skips_build_command_with_skip_build(
    repo_with_git_flow_angular_commits, cli_runner
):
    with mock.patch(
        "subprocess.run", return_value=CompletedProcess(args=(), returncode=0)
    ) as patched_subprocess_run:
        result = cli_runner.invoke(
            main, [version.name, "--patch", "--no-push", "--skip-build"]
        )  # force a new version
        assert result.exit_code == 0

        patched_subprocess_run.assert_not_called()


def test_version_writes_github_actions_output(
    repo_with_git_flow_angular_commits, cli_runner, monkeypatch, tmp_path
):
    mock_output_file = tmp_path / "action.out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(mock_output_file.resolve()))
    result = cli_runner.invoke(main, [version.name, "--patch", "--no-push"])
    assert result.exit_code == 0

    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )
    assert "released" in action_outputs
    assert action_outputs["released"] == "true"
    assert "version" in action_outputs
    assert action_outputs["version"] == "1.2.1"
    assert "tag" in action_outputs
    assert action_outputs["tag"] == "v1.2.1"


def test_version_exit_code_when_strict(repo_with_git_flow_angular_commits, cli_runner):
    result = cli_runner.invoke(main, ["--strict", version.name, "--no-push"])
    assert result.exit_code != 0


def test_version_exit_code_when_not_strict(
    repo_with_git_flow_angular_commits, cli_runner
):
    # Testing "no release will be made"
    result = cli_runner.invoke(main, [version.name, "--no-push"])
    assert result.exit_code == 0
