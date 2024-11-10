from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.cli.config import ChangelogOutputFormat

from tests.const import DEFAULT_BRANCH_NAME, EXAMPLE_HVCS_DOMAIN, INITIAL_COMMIT_MESSAGE
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
        CreateSquashMergeCommitFn,
        ExProjectGitRepoFn,
        ExtractRepoDefinitionFn,
        FormatGitHubSquashCommitMsgFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        RepoDefinition,
        SimulateChangeCommitsNReturnChangelogEntryFn,
        SimulateDefaultChangelogCreationFn,
        TomlSerializableTypes,
        VersionStr,
    )


FIX_BRANCH_1_NAME = "fix/patch-1"
FEAT_BRANCH_1_NAME = "feat/feature-1"


@pytest.fixture(scope="session")
def get_commits_for_github_flow_repo_w_default_release_channel(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
    format_squash_commit_msg_github: FormatGitHubSquashCommitMsgFn,
) -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "1.0.0": {
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
        "1.0.1": {
            "changelog_sections": {
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [1]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [1]},
                ],
                "scipy": [
                    {"section": "Fix", "i_commits": [1]},
                ],
            },
            "commits": [
                {
                    "angular": "fix(cli): add missing text",
                    "emoji": ":bug: add missing text",
                    "scipy": "MAINT: add missing text",
                },
                # Placeholder for the squash commit
                {"angular": "", "emoji": "", "scipy": ""},
            ],
        },
        "1.1.0": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [3]},
                    # TODO: when squash commits are parsed
                    # {"section": "Documentation", "i_commits": [2]},
                    # {"section": "Features", "i_commits": [0]},
                    # {"section": "Testing", "i_commits": [1]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [3]},
                    # {"section": ":sparkles:", "i_commits": [0]},
                    # {"section": "Other", "i_commits": [1, 2]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [3]},
                    # TODO: when squash commits are parsed
                    # {"section": "Documentation", "i_commits": [2]},
                    # {"section": "Feature", "i_commits": [0]},
                    # {"section": "None", "i_commits": [1]},
                ],
            },
            "commits": [
                {
                    "angular": "feat(cli): add cli interface",
                    "emoji": ":sparkles: add cli interface",
                    "scipy": "ENH: add cli interface",
                },
                {
                    "angular": "test(cli): add cli tests",
                    "emoji": ":checkmark: add cli tests",
                    "scipy": "TST: add cli tests",
                },
                {
                    "angular": "docs(cli): add cli documentation",
                    "emoji": ":books: add cli documentation",
                    "scipy": "DOC: add cli documentation",
                },
                # Placeholder for the squash commit
                {"angular": "", "emoji": "", "scipy": ""},
            ],
        },
    }

    # Update the commit definition for the squash commit using the GitHub format
    for i, (version_str, cmt_title_index) in enumerate(
        (
            ("1.0.1", 0),
            ("1.1.0", 0),
        ),
        start=2,
    ):
        version_def = base_definition[version_str]
        squash_commit_def: dict[CommitConvention, str] = {
            # Create the squash commit message for each commit type
            commit_type: format_squash_commit_msg_github(
                # Use the primary commit message as the PR title
                pr_title=version_def["commits"][cmt_title_index][commit_type],
                pr_number=i,
                squashed_commits=[
                    cmt[commit_type]
                    for cmt in version_def["commits"][:-1]
                    # This assumes the squash commit is the last commit in the list
                ],
            )
            for commit_type in version_def["changelog_sections"]
        }
        # Update the commit definition for the squash commit
        version_def["commits"][-1] = squash_commit_def

    # End loop

    def _get_commits_for_github_flow_repo_w_default_release_channel(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition,
            commit_type,
        )

    return _get_commits_for_github_flow_repo_w_default_release_channel


@pytest.fixture(scope="session")
def get_versions_for_github_flow_repo_w_default_release_channel(
    get_commits_for_github_flow_repo_w_default_release_channel: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_github_flow_repo_w_default_release_channel() -> (
        list[VersionStr]
    ):
        return list(get_commits_for_github_flow_repo_w_default_release_channel().keys())

    return _get_versions_for_github_flow_repo_w_default_release_channel


@pytest.fixture(scope="session")
def build_github_flow_repo_w_default_release_channel(
    get_commits_for_github_flow_repo_w_default_release_channel: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    default_tag_format_str: str,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    create_release_tagged_commit: CreateReleaseFn,
    create_squash_merge_commit: CreateSquashMergeCommitFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
) -> BuildRepoFn:
    """
    Builds a repository with the GitHub Flow branching strategy and a squash commit merging strategy
    for a single release channel on the default branch.
    """

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
            extra_configs={
                # Set the default release branch
                "tool.semantic_release.branches.main": {
                    "match": r"^(main|master)$",
                    "prerelease": False,
                },
                "tool.semantic_release.allow_zero_version": False,
                **(extra_configs or {}),
            },
        )

        # Retrieve/Define project vars that will be used to create the repo below
        repo_def = get_commits_for_github_flow_repo_w_default_release_channel(
            commit_type
        )
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
                git_repo,
                next_version_def["commits"],
            )

            main_branch_head = git_repo.heads[DEFAULT_BRANCH_NAME]

            # write expected Markdown changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make initial release (v1.0.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointers & Save them for concurrent development simulation
            patch_release_version = next(versions)
            patch_release_version_def = repo_def[patch_release_version]

            minor_release_version = next(versions)
            minor_release_version_def = repo_def[minor_release_version]

            # check out fix branch
            fix_branch_head = git_repo.create_head(
                FIX_BRANCH_1_NAME, main_branch_head.commit
            )
            fix_branch_head.checkout()

            # Make a patch level commit
            patch_release_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    # drop merge commit
                    git_repo,
                    patch_release_version_def["commits"][:1],
                ),
                # Add/Keep the merge message
                patch_release_version_def["commits"][1],
            ]

            # check out feature branch
            feat_branch_head = git_repo.create_head(
                FEAT_BRANCH_1_NAME, main_branch_head.commit
            )
            feat_branch_head.checkout()

            # Make 3 commits for a feature level bump (feat, test, docs)
            minor_release_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    minor_release_version_def["commits"][:3],
                ),
                # Add/Keep the merge message
                minor_release_version_def["commits"][3],
            ]

            # check out main branch
            main_branch_head.checkout()

            # Create Squash merge commit of fix branch into main (ignore conflicts & saving result)
            patch_release_version_def["commits"][1] = create_squash_merge_commit(
                git_repo=git_repo,
                branch_name=fix_branch_head.name,
                commit_def=patch_release_version_def["commits"][1],
            )

            # write expected Markdown changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=patch_release_version,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=patch_release_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make patch release for fix (v1.0.1)
            create_release_tagged_commit(git_repo, patch_release_version, tag_format)

            # Create Squash merge commit of feature branch into main (ignore conflicts)
            minor_release_version_def["commits"][3] = create_squash_merge_commit(
                git_repo=git_repo,
                branch_name=feat_branch_head.name,
                commit_def=minor_release_version_def["commits"][3],
            )

            # write expected Markdown changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=minor_release_version,
                dest_file=repo_dir.joinpath(changelog_md_file),
                output_format=ChangelogOutputFormat.MARKDOWN,
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=minor_release_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make minor release for feature (v1.1.1)
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
