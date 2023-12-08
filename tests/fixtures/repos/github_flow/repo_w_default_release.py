from __future__ import annotations

from copy import deepcopy
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from git import Head, Repo

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
        CreateReleaseFn,
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        RepoDefinition,
        SimulateChangeCommitsNReturnChangelogEntryFn,
        TomlSerializableTypes,
        VersionStr,
    )


@pytest.fixture(scope="session")
def get_commits_for_github_flow_repo_w_default_release_channel() -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "0.1.0": {
            "changelog_sections": {
                "angular": [{"section": "Unknown", "i_commits": [0]}],
                "emoji": [{"section": "Other", "i_commits": [0]}],
                "scipy": [{"section": "None", "i_commits": [0]}],
                "tag": [{"section": "Unknown", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "Initial commit",
                    "emoji": "Initial commit",
                    "scipy": "Initial commit",
                    "tag": "Initial commit",
                },
            ],
        },
        "0.1.1": {
            "changelog_sections": {
                "angular": [{"section": "Fix", "i_commits": [0]}],
                "emoji": [{"section": ":bug:", "i_commits": [0]}],
                "scipy": [{"section": "Fix", "i_commits": [0]}],
                "tag": [{"section": "Fix", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "fix(cli): add missing text",
                    "emoji": ":bug: add missing text",
                    "scipy": "MAINT: add missing text",
                    "tag": ":nut_and_bolt: add missing text",
                }
            ],
        },
        "0.2.0": {
            "changelog_sections": {
                "angular": [{"section": "Feature", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
                "tag": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat(cli): add cli interface",
                    "emoji": ":sparkles: add cli interface",
                    "scipy": "ENH: add cli interface",
                    "tag": ":sparkles: add cli interface",
                },
                {
                    "angular": "docs(cli): add cli documentation",
                    "emoji": ":books: add cli documentation",
                    "scipy": "DOC: add cli documentation",
                    "tag": ":books: add cli documentation", # TODO: ????
                }
            ],
        },
    }

    def _get_commits_for_github_flow_repo_w_default_release_channel(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        definition: RepoDefinition = {}

        for version, version_def in base_definition.items():
            definition[version] = {
                # Extract the correct changelog section header for the commit type
                "changelog_sections": deepcopy(
                    version_def["changelog_sections"][commit_type]
                ),
                "commits": [
                    # Extract the correct commit message for the commit type
                    message_variants[commit_type]
                    for message_variants in version_def["commits"]
                ],
            }

        return definition

    return _get_commits_for_github_flow_repo_w_default_release_channel


@pytest.fixture(scope="session")
def get_versions_for_github_flow_repo_w_default_release_channel(
    get_commits_for_github_flow_repo_w_default_release_channel: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_github_flow_repo_w_default_release_channel() -> list[VersionStr]:
        return list(
            get_commits_for_github_flow_repo_w_default_release_channel().keys()
        )

    return _get_versions_for_github_flow_repo_w_default_release_channel


@pytest.fixture(scope="session")
def build_github_flow_repo_w_default_release_channel(
    get_commits_for_github_flow_repo_w_default_release_channel: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    default_tag_format_str: str,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    create_release_tagged_commit: CreateReleaseFn,
) -> BuildRepoFn:
    def _build_github_flow_repo_w_default_release_channel(
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

        # Retrieve/Define project vars that will be used to create the repo below
        repo_def = get_commits_for_github_flow_repo_w_default_release_channel(commit_type)
        versions = (key for key in repo_def)
        next_version = next(versions)
        next_version_def = repo_def[next_version]

        # must be after build_configured_base_repo() so we dont set the
        # default tag format in the pyproject.toml (we want semantic-release to use its defaults)
        # however we need it to manually create the tags it knows how to parse
        tag_format = tag_format_str or default_tag_format_str

        with temporary_working_directory(repo_dir), Repo(".") as git_repo:
            # commit initial files & update commit msg with sha & url
            next_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo, next_version_def["commits"], hvcs
            )

            main_branch_head = git_repo.heads.main

            # Make initial feature release (v0.1.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointers & Save them for concurrent development simulation
            patch_release_version = next(versions)
            patch_release_version_def = repo_def[patch_release_version]

            minor_release_version = next(versions)
            minor_release_version_def = repo_def[minor_release_version]

            # check out fix branch
            fix_branch_1 = "fix/missing-text"
            fix_branch_head = git_repo.create_head(fix_branch_1, main_branch_head.commit)
            fix_branch_head.checkout()

            # Make a patch level commit
            patch_release_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo, patch_release_version_def["commits"], hvcs
            )

            # check out feature branch
            feat_branch_1 = "feat/add-some-text"
            feat_branch_head = git_repo.create_head(feat_branch_1, main_branch_head.commit)
            feat_branch_head.checkout()

            # Make 2 commits for a feature level bump
            pr_title = f"{minor_release_version_def['commits'][0]} (#2)"
            minor_release_version_def["commits"] = simulate_change_commits_n_rtn_changelog_entry(
                git_repo, minor_release_version_def["commits"], hvcs
            )

            # check out main branch
            main_branch_head.checkout()

            # Merge fix branch into main & delete branch
            git_repo.git.merge(
                fix_branch_1,
                "--no-ff",
                m=f"Merge branch '{fix_branch_1}' into 'main'"
            )
            Head.delete(git_repo, feat_branch_head, force=True)

            # Make patch release for fix (v0.1.1)
            create_release_tagged_commit(git_repo, patch_release_version, tag_format)

            # Squash commits from feat branch into index (ignore conflicts)
            git_repo.git.merge(
                feat_branch_1,
                "--squash",
                "--strategy-option=theirs",
            )

            # Commit the squashed changes with GitHub default squash message
            pr_squash_n_merge_msg = dedent(
                f"""
                {pr_title}

                * {minor_release_version_def["commits"][0]}

                * {minor_release_version_def["commits"][1]}
                """
            )
            git_repo.git.commit("--no-edit", m=pr_squash_n_merge_msg)

            # Delete feat branch
            Head.delete(git_repo, feat_branch_head, force=True)

            # Make feature release (v0.2.0)
            create_release_tagged_commit(git_repo, minor_release_version, tag_format)

        return repo_dir, hvcs

    return _build_github_flow_repo_w_default_release_channel


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_default_release_channel_angular_commits(
    build_github_flow_repo_w_default_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_default_release_channel_angular_commits.__name__
    )
    build_github_flow_repo_w_default_release_channel(
        cached_repo_path, commit_type="angular"
    )
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_default_release_channel_emoji_commits(
    build_github_flow_repo_w_default_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_default_release_channel_emoji_commits.__name__
    )
    build_github_flow_repo_w_default_release_channel(
        cached_repo_path, commit_type="emoji"
    )
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_default_release_channel_scipy_commits(
    build_github_flow_repo_w_default_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_default_release_channel_scipy_commits.__name__
    )
    build_github_flow_repo_w_default_release_channel(
        cached_repo_path, commit_type="scipy"
    )
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_default_release_channel_tag_commits(
    build_github_flow_repo_w_default_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_default_release_channel_tag_commits.__name__
    )
    build_github_flow_repo_w_default_release_channel(
        cached_repo_path, commit_type="tag"
    )
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_github_flow_w_default_release_channel_angular_commits(
    cached_repo_w_github_flow_w_default_release_channel_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_default_release_channel_angular_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_default_release_channel_angular_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_default_release_channel_emoji_commits(
    cached_repo_w_github_flow_w_default_release_channel_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_default_release_channel_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_default_release_channel_emoji_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_default_release_channel_scipy_commits(
    cached_repo_w_github_flow_w_default_release_channel_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_default_release_channel_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_default_release_channel_scipy_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_default_release_channel_tag_commits(
    cached_repo_w_github_flow_w_default_release_channel_tag_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_default_release_channel_tag_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_default_release_channel_tag_commits,
        example_project_dir,
    )
    return example_project_git_repo()
