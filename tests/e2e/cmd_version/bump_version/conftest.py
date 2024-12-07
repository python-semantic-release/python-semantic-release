from __future__ import annotations

import os
import shutil
from re import IGNORECASE, compile as regexp
from typing import TYPE_CHECKING

import pytest
from git import Repo

if TYPE_CHECKING:
    from pathlib import Path
    from re import Pattern
    from typing import Protocol

    from tests.fixtures.git_repo import BuildRepoFromDefinitionFn, RepoActionConfigure

    class GetSanitizedMdChangelogContentFn(Protocol):
        def __call__(self, repo_dir: Path) -> str: ...

    class GetSanitizedRstChangelogContentFn(Protocol):
        def __call__(self, repo_dir: Path) -> str: ...

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


@pytest.fixture(scope="session")
def long_hash_pattern() -> Pattern:
    return regexp(r"\b([0-9a-f]{40})\b", IGNORECASE)


@pytest.fixture(scope="session")
def short_hash_pattern() -> Pattern:
    return regexp(r"\b([0-9a-f]{7})\b", IGNORECASE)


@pytest.fixture(scope="session")
def get_sanitized_rst_changelog_content(
    changelog_rst_file: Path,
    default_rst_changelog_insertion_flag: str,
    long_hash_pattern: Pattern,
    short_hash_pattern: Pattern,
) -> GetSanitizedRstChangelogContentFn:
    rst_short_hash_link_pattern = regexp(r"(_[0-9a-f]{7})\b", IGNORECASE)

    def _get_sanitized_rst_changelog_content(repo_dir: Path) -> str:
        # TODO: v10 change -- default turns to update so this is not needed
        # Because we are in init mode, the insertion flag is not present in the changelog
        # we must take it out manually because our repo generation fixture includes it automatically
        with (repo_dir / changelog_rst_file).open(newline=os.linesep) as rfd:
            # use os.linesep here because the insertion flag is os-specific
            # but convert the content to universal newlines for comparison
            changelog_content = (
                rfd.read()
                .replace(f"{default_rst_changelog_insertion_flag}{os.linesep}", "")
                .replace("\r", "")
            )

        changelog_content = long_hash_pattern.sub("0" * 40, changelog_content)
        changelog_content = short_hash_pattern.sub("0" * 7, changelog_content)
        return rst_short_hash_link_pattern.sub(f'_{"0" * 7}', changelog_content)

    return _get_sanitized_rst_changelog_content


@pytest.fixture(scope="session")
def get_sanitized_md_changelog_content(
    changelog_md_file: Path,
    default_md_changelog_insertion_flag: str,
    long_hash_pattern: Pattern,
    short_hash_pattern: Pattern,
) -> GetSanitizedMdChangelogContentFn:
    def _get_sanitized_md_changelog_content(repo_dir: Path) -> str:
        # TODO: v10 change -- default turns to update so this is not needed
        # Because we are in init mode, the insertion flag is not present in the changelog
        # we must take it out manually because our repo generation fixture includes it automatically
        with (repo_dir / changelog_md_file).open(newline=os.linesep) as rfd:
            # use os.linesep here because the insertion flag is os-specific
            # but convert the content to universal newlines for comparison
            changelog_content = (
                rfd.read()
                .replace(f"{default_md_changelog_insertion_flag}{os.linesep}", "")
                .replace("\r", "")
            )

        changelog_content = long_hash_pattern.sub("0" * 40, changelog_content)

        return short_hash_pattern.sub("0" * 7, changelog_content)

    return _get_sanitized_md_changelog_content
