from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.hvcs.github import Github

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Protocol

    from click.testing import Result

    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuildRepoFromDefinitionFn, RepoActionConfigure

    class InitMirrorRepo4RebuildFn(Protocol):
        def __call__(
            self,
            mirror_repo_dir: Path,
            configuration_step: RepoActionConfigure,
        ) -> Path: ...

    class RunPSReleaseFn(Protocol):
        def __call__(
            self,
            next_version_str: str,
            git_repo: Repo,
        ) -> Result: ...


@pytest.fixture(scope="session")
def init_mirror_repo_for_rebuild(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
) -> InitMirrorRepo4RebuildFn:
    def _init_mirror_repo_for_rebuild(
        mirror_repo_dir: Path,
        configuration_step: RepoActionConfigure,
    ) -> Path:
        # Create the mirror repo directory
        mirror_repo_dir.mkdir(exist_ok=True, parents=True)

        # Initialize mirror repository
        build_repo_from_definition(
            dest_dir=mirror_repo_dir,
            repo_construction_steps=[configuration_step],
        )

        with Repo(mirror_repo_dir) as mirror_git_repo:
            # remove the default changelog files to enable Update Mode (new default of v10)
            mirror_git_repo.git.rm(str(changelog_md_file), force=True)
            mirror_git_repo.git.rm(str(changelog_rst_file), force=True)

        return mirror_repo_dir

    return _init_mirror_repo_for_rebuild


@pytest.fixture(scope="session")
def run_psr_release(
    run_cli: RunCliFn,
    changelog_rst_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> RunPSReleaseFn:
    base_version_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
    write_changelog_only_cmd = [
        *base_version_cmd,
        "--changelog",
        "--no-commit",
        "--no-tag",
        "--skip-build",
    ]

    def _run_psr_release(
        next_version_str: str,
        git_repo: Repo,
    ) -> Result:
        version_n_buildmeta = next_version_str.split("+", maxsplit=1)
        version_n_prerelease = version_n_buildmeta[0].split("-", maxsplit=1)

        build_metadata_args = (
            ["--build-metadata", version_n_buildmeta[-1]]
            if len(version_n_buildmeta) > 1
            else []
        )

        prerelease_args = (
            [
                "--as-prerelease",
                "--prerelease-token",
                version_n_prerelease[-1].split(".", maxsplit=1)[0],
            ]
            if len(version_n_prerelease) > 1
            else []
        )

        # Initial run to write the RST changelog
        # 1. configure PSR to write the RST changelog with the RST default insertion flag
        update_pyproject_toml(
            "tool.semantic_release.changelog.default_templates.changelog_file",
            str(changelog_rst_file),
        )
        cli_cmd = [*write_changelog_only_cmd, *prerelease_args, *build_metadata_args]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})
        assert_successful_exit_code(result, cli_cmd)

        # Reset the index in case PSR added anything to the index
        git_repo.git.reset("--mixed", "HEAD")

        # Add the changelog file to the git index but reset the working directory
        git_repo.git.add(str(changelog_rst_file))
        git_repo.git.checkout("--", ".")

        # Actual run to release & write the MD changelog
        cli_cmd = [
            *base_version_cmd,
            *prerelease_args,
            *build_metadata_args,
        ]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})
        assert_successful_exit_code(result, cli_cmd)

        return result

    return _run_psr_release
