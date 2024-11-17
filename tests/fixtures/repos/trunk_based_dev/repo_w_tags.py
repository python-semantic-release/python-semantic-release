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
    from tests.fixtures.example_project import (
        ExProjectDir,
    )
    from tests.fixtures.git_repo import (
        BaseRepoVersionDef,
        BuildRepoFn,
        BuildRepoOrCopyCacheFn,
        CommitConvention,
        CreateReleaseFn,
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
def deps_files_4_repo_w_tags(
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
def build_spec_hash_for_repo_w_tags(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_repo_w_tags: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_repo_w_tags)


@pytest.fixture(scope="session")
def get_commits_for_trunk_only_repo_w_tags(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
) -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "0.1.0": {
            "changelog_sections": {
                "angular": [{"section": "Features", "i_commits": [1]}],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [1]},
                    {"section": "Other", "i_commits": [0]},
                ],
                "scipy": [{"section": "Feature", "i_commits": [1]}],
            },
            "commits": [
                {
                    "angular": INITIAL_COMMIT_MESSAGE,
                    "emoji": INITIAL_COMMIT_MESSAGE,
                    "scipy": INITIAL_COMMIT_MESSAGE,
                },
                {
                    "angular": "feat: add new feature",
                    "emoji": ":sparkles: add new feature",
                    "scipy": "ENH: add new feature",
                },
            ],
        },
        "0.1.1": {
            "changelog_sections": {
                "angular": [{"section": "Bug Fixes", "i_commits": [0]}],
                "emoji": [{"section": ":bug:", "i_commits": [0]}],
                "scipy": [{"section": "Fix", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "fix: correct some text",
                    "emoji": ":bug: correct some text",
                    "scipy": "MAINT: correct some text",
                },
            ],
        },
    }

    def _get_commits_for_trunk_only_repo_w_tags(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition, commit_type
        )

    return _get_commits_for_trunk_only_repo_w_tags


@pytest.fixture(scope="session")
def get_versions_for_trunk_only_repo_w_tags(
    get_commits_for_trunk_only_repo_w_tags: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_trunk_only_repo_w_tags() -> list[VersionStr]:
        return list(get_commits_for_trunk_only_repo_w_tags().keys())

    return _get_versions_for_trunk_only_repo_w_tags


@pytest.fixture(scope="session")
def build_trunk_only_repo_w_tags(
    get_commits_for_trunk_only_repo_w_tags: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    default_tag_format_str: str,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
    create_release_tagged_commit: CreateReleaseFn,
) -> BuildRepoFn:
    def _build_trunk_only_repo_w_tags(
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

        repo_def = get_commits_for_trunk_only_repo_w_tags(commit_type)
        versions = (key for key in repo_def)
        next_version = next(versions)
        next_version_def = repo_def[next_version]

        # must be after build_configured_base_repo() so we dont set the
        # default tag format in the pyproject.toml (we want semantic-release to use its defaults)
        # however we need it to manually create the tags it knows how to parse
        tag_format = tag_format_str or default_tag_format_str

        # Run Git operations to simulate repo commit & release history
        with temporary_working_directory(repo_dir), Repo(".") as git_repo:
            # commit initial files & update commit msg with sha & url
            next_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo,
                next_version_def["commits"],
            )

            # write expected Markdown changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
                mask_initial_release=mask_initial_release,
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
                mask_initial_release=mask_initial_release,
            )

            # Publish initial feature release (v0.1.0) [updates tool.poetry.version]
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Add a patch level change
            next_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo, next_version_def["commits"]
            )

            # write expected Markdown changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
                mask_initial_release=mask_initial_release,
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
                mask_initial_release=mask_initial_release,
            )

            # Make a patch level release (v0.1.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

        return repo_dir, hvcs

    return _build_trunk_only_repo_w_tags


# --------------------------------------------------------------------------- #
# Test-level fixtures that will cache the built directory & set up test case  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_trunk_only_angular_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_trunk_only_repo_w_tags: BuildRepoFn,
    build_spec_hash_for_repo_w_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_trunk_only_repo_w_tags(cached_repo_path, "angular")

    build_repo_or_copy_cache(
        repo_name=repo_w_trunk_only_angular_commits.__name__,
        build_spec_hash=build_spec_hash_for_repo_w_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_trunk_only_emoji_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_trunk_only_repo_w_tags: BuildRepoFn,
    build_spec_hash_for_repo_w_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_trunk_only_repo_w_tags(cached_repo_path, "emoji")

    build_repo_or_copy_cache(
        repo_name=repo_w_trunk_only_emoji_commits.__name__,
        build_spec_hash=build_spec_hash_for_repo_w_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_trunk_only_scipy_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_trunk_only_repo_w_tags: BuildRepoFn,
    build_spec_hash_for_repo_w_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_trunk_only_repo_w_tags(cached_repo_path, "scipy")

    build_repo_or_copy_cache(
        repo_name=repo_w_trunk_only_scipy_commits.__name__,
        build_spec_hash=build_spec_hash_for_repo_w_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()
