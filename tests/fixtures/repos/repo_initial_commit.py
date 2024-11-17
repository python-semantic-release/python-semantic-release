from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.cli.config import ChangelogOutputFormat

import tests.conftest
import tests.const
import tests.util
from tests.const import EXAMPLE_HVCS_DOMAIN, INITIAL_COMMIT_MESSAGE
from tests.util import temporary_working_directory

if TYPE_CHECKING:
    from semantic_release.hvcs import HvcsBase

    from tests.conftest import GetMd5ForSetOfFilesFn
    from tests.fixtures.example_project import ExProjectDir
    from tests.fixtures.git_repo import (
        BaseRepoVersionDef,
        BuildRepoFn,
        BuildRepoOrCopyCacheFn,
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
def deps_files_4_repo_initial_commit(
    deps_files_4_example_git_project: list[Path],
) -> list[Path]:
    return [
        *deps_files_4_example_git_project,
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_for_repo_initial_commit(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_repo_initial_commit: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_repo_initial_commit)


@pytest.fixture(scope="session")
def get_commits_for_repo_w_initial_commit(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
) -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "Unreleased": {
            "changelog_sections": {
                # ORDER matters here since greater than 1 commit, changelogs sections are alphabetized
                # But value is ultimately defined by the commits, which means the commits are
                # referenced by index value
                #
                # NOTE: Since Initial commit is not a valid commit type, it is not included in the
                #       changelog sections, except for the Emoji Parser because it does not fail when
                #       no emoji is found.
                "angular": [],
                "emoji": [{"section": "Other", "i_commits": [0]}],
                "scipy": [],
            },
            "commits": [
                {
                    "angular": INITIAL_COMMIT_MESSAGE,
                    "emoji": INITIAL_COMMIT_MESSAGE,
                    "scipy": INITIAL_COMMIT_MESSAGE,
                },
            ],
        },
    }

    def _get_commits_for_repo_w_initial_commit(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition, commit_type
        )

    return _get_commits_for_repo_w_initial_commit


@pytest.fixture(scope="session")
def get_versions_repo_w_initial_commit(
    get_commits_for_repo_w_initial_commit: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_repo_w_initial_commit() -> list[VersionStr]:
        return list(get_commits_for_repo_w_initial_commit().keys())

    return _get_versions_for_repo_w_initial_commit


@pytest.fixture(scope="session")
def build_repo_w_initial_commit(
    get_commits_for_repo_w_initial_commit: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
) -> BuildRepoFn:
    def _build_repo_w_initial_commit(
        dest_dir: Path | str,
        commit_type: CommitConvention = "angular",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = False,
    ) -> tuple[Path, HvcsBase]:
        repo_dir, hvcs = build_configured_base_repo(
            dest_dir,
            commit_type=commit_type,
            hvcs_client_name=hvcs_client_name,
            hvcs_domain=hvcs_domain,
            tag_format_str=tag_format_str,
            extra_configs=extra_configs,
            mask_initial_release=mask_initial_release,
        )

        repo_def = get_commits_for_repo_w_initial_commit(commit_type)
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
                mask_initial_release=mask_initial_release,
            )

            # write expected RST changelog
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
                mask_initial_release=mask_initial_release,
            )

        return repo_dir, hvcs

    return _build_repo_w_initial_commit


# --------------------------------------------------------------------------- #
# Test-level fixtures that will cache the built directory & set up test case  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_initial_commit(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_repo_w_initial_commit: BuildRepoFn,
    build_spec_hash_for_repo_initial_commit: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_repo_w_initial_commit(cached_repo_path)

    build_repo_or_copy_cache(
        repo_name=repo_w_initial_commit.__name__,
        build_spec_hash=build_spec_hash_for_repo_initial_commit,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()
