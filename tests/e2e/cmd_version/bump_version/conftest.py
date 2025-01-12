from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest
from git import Repo

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Protocol

    from tests.fixtures.git_repo import BuildRepoFromDefinitionFn, RepoActionConfigure

    class InitMirrorRepo4RebuildFn(Protocol):
        def __call__(
            self,
            mirror_repo_dir: Path,
            configuration_step: RepoActionConfigure,
        ) -> Path: ...


@pytest.fixture(scope="session")
def init_mirror_repo_for_rebuild(
    default_changelog_md_template: Path,
    default_changelog_rst_template: Path,
    changelog_template_dir: Path,
    build_repo_from_definition: BuildRepoFromDefinitionFn,
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

        # Force custom changelog to be a copy of the default changelog (md and rst)
        shutil.copytree(
            src=default_changelog_md_template.parent,
            dst=mirror_repo_dir / changelog_template_dir,
            dirs_exist_ok=True,
        )
        shutil.copytree(
            src=default_changelog_rst_template.parent,
            dst=mirror_repo_dir / changelog_template_dir,
            dirs_exist_ok=True,
        )

        with Repo(mirror_repo_dir) as mirror_git_repo:
            mirror_git_repo.git.add(str(changelog_template_dir))

        return mirror_repo_dir

    return _init_mirror_repo_for_rebuild
