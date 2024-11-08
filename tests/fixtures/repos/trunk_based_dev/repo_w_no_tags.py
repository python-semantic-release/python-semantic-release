from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.cli.config import ChangelogOutputFormat

from tests.const import EXAMPLE_HVCS_DOMAIN
from tests.util import copy_dir_tree, temporary_working_directory

if TYPE_CHECKING:
    from pathlib import Path

    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import ExProjectDir
    from tests.fixtures.git_repo import (
        BaseRepoVersionDef,
        BuildRepoFn,
        CommitConvention,
        ExProjectGitRepoFn,
        ExtractRepoDefinitionFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        RepoDefinition,
        SimulateChangeCommitsNReturnChangelogEntryFn,
        SimulateDefaultChangelogCreationFn,
        TomlSerializableTypes,
        VersionStr,
    )


@pytest.fixture(scope="session")
def get_commits_for_trunk_only_repo_w_no_tags(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
) -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "Unreleased": {
            "changelog_sections": {
                # ORDER matters here since greater than 1 commit, changelogs sections are alphabetized
                # But value is ultimately defined by the commits, which means the commits are
                # referenced by index value
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [3, 1]},
                    {"section": "Features", "i_commits": [2]},
                    {"section": "Unknown", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [3, 1]},
                    {"section": ":sparkles:", "i_commits": [2]},
                    {"section": "Other", "i_commits": [0]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [2]},
                    {"section": "Fix", "i_commits": [3, 1]},
                    {"section": "Unknown", "i_commits": [0]},
                ],
            },
            "commits": [
                {
                    "angular": "Initial commit",
                    "emoji": "Initial commit",
                    "scipy": "Initial commit",
                },
                {
                    "angular": "fix: correct some text",
                    "emoji": ":bug: correct some text",
                    "scipy": "MAINT: correct some text",
                },
                {
                    "angular": "feat: add much more text",
                    "emoji": ":sparkles: add much more text",
                    "scipy": "ENH: add much more text",
                },
                {
                    "angular": "fix: correct some text",
                    "emoji": ":bug: correct some text",
                    "scipy": "MAINT: correct some text",
                },
            ],
        },
    }

    def _get_commits_for_trunk_only_repo_w_no_tags(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition, commit_type
        )

    return _get_commits_for_trunk_only_repo_w_no_tags


@pytest.fixture(scope="session")
def get_versions_for_trunk_only_repo_w_no_tags(
    get_commits_for_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_trunk_only_repo_w_no_tags() -> list[VersionStr]:
        return list(get_commits_for_trunk_only_repo_w_no_tags().keys())

    return _get_versions_for_trunk_only_repo_w_no_tags


@pytest.fixture(scope="session")
def build_trunk_only_repo_w_no_tags(
    get_commits_for_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
) -> BuildRepoFn:
    def _build_trunk_only_repo_w_no_tags(
        dest_dir: Path | str,
        commit_type: CommitConvention = "angular",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
    ) -> tuple[Path, HvcsBase]:
        repo_dir, hvcs = build_configured_base_repo(
            dest_dir,
            commit_type=commit_type,
            hvcs_client_name=hvcs_client_name,
            hvcs_domain=hvcs_domain,
            tag_format_str=tag_format_str,
            extra_configs=extra_configs,
        )

        repo_def = get_commits_for_trunk_only_repo_w_no_tags(commit_type)
        versions = (key for key in repo_def)
        next_version = next(versions)
        next_version_def = repo_def[next_version]

        with temporary_working_directory(repo_dir), Repo(".") as git_repo:
            # Run set up commits
            next_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo,
                next_version_def["commits"],
            )

            # write expected Markdown changelog
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
            )

            # write expected RST changelog
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

        return repo_dir, hvcs

    return _build_trunk_only_repo_w_no_tags


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_with_no_tags_angular_commits(
    build_trunk_only_repo_w_no_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_no_tags_angular_commits.__name__
    )
    build_trunk_only_repo_w_no_tags(cached_repo_path, "angular")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_with_no_tags_emoji_commits(
    build_trunk_only_repo_w_no_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_no_tags_emoji_commits.__name__
    )
    build_trunk_only_repo_w_no_tags(cached_repo_path, "emoji")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_with_no_tags_scipy_commits(
    build_trunk_only_repo_w_no_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_no_tags_scipy_commits.__name__
    )
    build_trunk_only_repo_w_no_tags(cached_repo_path, "scipy")
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_with_no_tags_angular_commits(
    cached_repo_with_no_tags_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_no_tags_angular_commits.exists():
        raise RuntimeError("Unable to find cached repo!")
    copy_dir_tree(cached_repo_with_no_tags_angular_commits, example_project_dir)
    return example_project_git_repo()


@pytest.fixture
def repo_with_no_tags_emoji_commits(
    cached_repo_with_no_tags_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_no_tags_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repo!")
    copy_dir_tree(cached_repo_with_no_tags_emoji_commits, example_project_dir)
    return example_project_git_repo()


@pytest.fixture
def repo_with_no_tags_scipy_commits(
    cached_repo_with_no_tags_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_no_tags_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repo!")
    copy_dir_tree(cached_repo_with_no_tags_scipy_commits, example_project_dir)
    return example_project_git_repo()
