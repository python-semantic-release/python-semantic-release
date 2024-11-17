from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.cli.config import ChangelogOutputFormat

import tests.conftest
import tests.const
import tests.util
from tests.const import DEFAULT_BRANCH_NAME, EXAMPLE_HVCS_DOMAIN, INITIAL_COMMIT_MESSAGE
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
        CreateMergeCommitFn,
        CreateReleaseFn,
        ExProjectGitRepoFn,
        ExtractRepoDefinitionFn,
        FormatGitHubMergeCommitMsgFn,
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
FEAT_BRANCH_2_NAME = "feat/feature-2"


@pytest.fixture(scope="session")
def deps_files_4_github_flow_repo_w_feature_release_channel(
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
def build_spec_hash_for_github_flow_repo_w_feature_release_channel(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_github_flow_repo_w_feature_release_channel: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(
        deps_files_4_github_flow_repo_w_feature_release_channel
    )


@pytest.fixture(scope="session")
def get_commits_for_github_flow_repo_w_feature_release_channel(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
    format_merge_commit_msg_github: FormatGitHubMergeCommitMsgFn,
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
        "1.0.1-alpha.1": {
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
                }
            ],
        },
        "1.0.1-alpha.2": {
            "changelog_sections": {
                "angular": [{"section": "Bug Fixes", "i_commits": [0]}],
                "emoji": [{"section": ":bug:", "i_commits": [0]}],
                "scipy": [{"section": "Fix", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "fix: adjust text to resolve",
                    "emoji": ":bug: adjust text to resolve",
                    "scipy": "MAINT: adjust text to resolve",
                },
            ],
        },
        "1.0.1": {
            "changelog_sections": {
                "angular": [],
                "emoji": [
                    {"section": "Other", "i_commits": [0]},
                ],
                "scipy": [],
            },
            "commits": [
                {
                    "angular": format_merge_commit_msg_github(
                        pr_number=25,
                        branch_name=FIX_BRANCH_1_NAME,
                    ),
                    "emoji": format_merge_commit_msg_github(
                        pr_number=25,
                        branch_name=FIX_BRANCH_1_NAME,
                    ),
                    "scipy": format_merge_commit_msg_github(
                        pr_number=25,
                        branch_name=FIX_BRANCH_1_NAME,
                    ),
                },
            ],
        },
        "1.1.0-alpha.1": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [0]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [0]},
                ],
            },
            "commits": [
                {
                    "angular": "feat: add some more text",
                    "emoji": ":sparkles: add some more text",
                    "scipy": "ENH: add some more text",
                },
            ],
        },
        "1.1.0": {
            "changelog_sections": {
                "angular": [],
                "emoji": [{"section": "Other", "i_commits": [0]}],
                "scipy": [],
            },
            "commits": [
                {
                    "angular": format_merge_commit_msg_github(
                        pr_number=26,
                        branch_name=FEAT_BRANCH_1_NAME,
                    ),
                    "emoji": format_merge_commit_msg_github(
                        pr_number=26,
                        branch_name=FEAT_BRANCH_1_NAME,
                    ),
                    "scipy": format_merge_commit_msg_github(
                        pr_number=26,
                        branch_name=FEAT_BRANCH_1_NAME,
                    ),
                },
            ],
        },
    }

    def _get_commits_for_github_flow_repo_w_feature_release_channel(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition, commit_type
        )

    return _get_commits_for_github_flow_repo_w_feature_release_channel


@pytest.fixture(scope="session")
def get_versions_for_github_flow_repo_w_feature_release_channel(
    get_commits_for_github_flow_repo_w_feature_release_channel: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_github_flow_repo_w_feature_release_channel() -> (
        list[VersionStr]
    ):
        return list(get_commits_for_github_flow_repo_w_feature_release_channel().keys())

    return _get_versions_for_github_flow_repo_w_feature_release_channel


@pytest.fixture(scope="session")
def build_github_flow_repo_w_feature_release_channel(
    get_commits_for_github_flow_repo_w_feature_release_channel: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    default_tag_format_str: str,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
    create_release_tagged_commit: CreateReleaseFn,
    create_merge_commit: CreateMergeCommitFn,
) -> BuildRepoFn:
    """
    Builds a repository with the GitHub Flow branching strategy using merge commits
    for alpha feature releases and official releases on the default branch.
    """

    def _build_github_flow_repo_w_feature_release_channel(
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
            mask_initial_release=mask_initial_release,
            extra_configs={
                # Set the default release branch
                "tool.semantic_release.branches.main": {
                    "match": r"^(main|master)$",
                    "prerelease": False,
                },
                # branch "feat/" & "fix/" has prerelease suffix of "alpha"
                "tool.semantic_release.branches.alpha-release": {
                    "match": r"^(feat|fix)/.+",
                    "prerelease": True,
                    "prerelease_token": "alpha",
                },
                "tool.semantic_release.allow_zero_version": False,
                **(extra_configs or {}),
            },
        )

        # Retrieve/Define project vars that will be used to create the repo below
        repo_def = get_commits_for_github_flow_repo_w_feature_release_channel(
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

            # Make initial release (v1.0.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # check out fix branch
            fix_branch_head = git_repo.create_head(
                FIX_BRANCH_1_NAME, main_branch_head.commit
            )
            fix_branch_head.checkout()

            # Make a patch level commit
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

            # Make a patch level release candidate (v1.0.1-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Make an additional fix from alpha.1
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

            # Make an additional prerelease (v1.0.1-alpha.2)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Merge fix branch into main (saving updated commit sha)
            main_branch_head.checkout()
            next_version_def["commits"][0] = create_merge_commit(
                git_repo=git_repo,
                branch_name=fix_branch_head.name,
                commit_def=next_version_def["commits"][0],
                fast_forward=False,
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

            # Make a patch level release (v1.0.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # checkout feat branch
            feat_branch_head = git_repo.create_head(
                FEAT_BRANCH_1_NAME, main_branch_head.commit
            )
            feat_branch_head.checkout()

            # Make a minor level commit
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

            # Make a patch level release candidate (v1.1.0-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Merge feat branch into main
            main_branch_head.checkout()
            next_version_def["commits"][0] = create_merge_commit(
                git_repo=git_repo,
                branch_name=feat_branch_head.name,
                commit_def=next_version_def["commits"][0],
                fast_forward=False,
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

            # Make a minor level release (v1.1.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

        return repo_dir, hvcs

    return _build_github_flow_repo_w_feature_release_channel


# --------------------------------------------------------------------------- #
# Test-level fixtures that will cache the built directory & set up test case  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_angular_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    build_spec_hash_for_github_flow_repo_w_feature_release_channel: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_github_flow_repo_w_feature_release_channel(cached_repo_path, "angular")

    build_repo_or_copy_cache(
        repo_name=repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
        build_spec_hash=build_spec_hash_for_github_flow_repo_w_feature_release_channel,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_emoji_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    build_spec_hash_for_github_flow_repo_w_feature_release_channel: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_github_flow_repo_w_feature_release_channel(cached_repo_path, "emoji")

    build_repo_or_copy_cache(
        repo_name=repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
        build_spec_hash=build_spec_hash_for_github_flow_repo_w_feature_release_channel,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_scipy_commits(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    build_spec_hash_for_github_flow_repo_w_feature_release_channel: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_github_flow_repo_w_feature_release_channel(cached_repo_path, "scipy")

    build_repo_or_copy_cache(
        repo_name=repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
        build_spec_hash=build_spec_hash_for_github_flow_repo_w_feature_release_channel,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()
