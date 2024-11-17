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
        FormatGitMergeCommitMsgFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        RepoDefinition,
        SimulateChangeCommitsNReturnChangelogEntryFn,
        SimulateDefaultChangelogCreationFn,
        TomlSerializableTypes,
        VersionStr,
    )


DEV_BRANCH_NAME = "dev"
FEAT_BRANCH_1_NAME = "feat/feature-1"
FEAT_BRANCH_2_NAME = "feat/feature-2"
FEAT_BRANCH_3_NAME = "feat/feature-3"
FIX_BRANCH_1_NAME = "fix/patch-1"


@pytest.fixture(scope="session")
def deps_files_4_git_flow_repo_w_2_release_channels(
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
def build_spec_hash_for_git_flow_repo_w_2_release_channels(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_git_flow_repo_w_2_release_channels: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_git_flow_repo_w_2_release_channels)


@pytest.fixture(scope="session")
def get_commits_for_git_flow_repo_w_2_release_channels(
    extract_commit_convention_from_base_repo_def: ExtractRepoDefinitionFn,
    format_merge_commit_msg_git: FormatGitMergeCommitMsgFn,
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
        "0.1.1-alpha.1": {
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
        "1.0.0-alpha.1": {
            "changelog_sections": {
                "angular": [{"section": "Features", "i_commits": [0]}],
                "emoji": [{"section": ":boom:", "i_commits": [0]}],
                "scipy": [{"section": "Breaking", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat!: add revolutionary feature\n\nBREAKING CHANGE: this is a breaking change",
                    "emoji": ":boom: add revolutionary feature\n\nThis change is a breaking change",
                    "scipy": "API: add revolutionary feature\n\nBREAKING CHANGE: this is a breaking change",
                }
            ],
        },
        "1.0.0": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [2, 1]},
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
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                },
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                },
            ],
        },
        "1.1.0": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [2, 1]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [0]},
                ],
            },
            "commits": [
                {
                    "angular": "feat(dev): add some more text",
                    "emoji": ":sparkles: (dev) add some more text",
                    "scipy": "ENH(dev): add some more text",
                },
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_2_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_2_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=FEAT_BRANCH_2_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                },
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                },
            ],
        },
        "1.1.1": {
            "changelog_sections": {
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [2, 1]},
                ],
                "scipy": [
                    {"section": "Fix", "i_commits": [0]},
                ],
            },
            "commits": [
                {
                    "angular": "fix(dev): correct some text",
                    "emoji": ":bug: correct dev-scoped text",
                    "scipy": "MAINT(dev): correct some text",
                },
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=FIX_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=FIX_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=FIX_BRANCH_1_NAME,
                        tgt_branch_name=DEV_BRANCH_NAME,
                    ),
                },
                {
                    "angular": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "emoji": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                    "scipy": format_merge_commit_msg_git(
                        branch_name=DEV_BRANCH_NAME,
                        tgt_branch_name=DEFAULT_BRANCH_NAME,
                    ),
                },
            ],
        },
        "1.2.0-alpha.1": {
            "changelog_sections": {
                "angular": [{"section": "Features", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat(scope): add some more text",
                    "emoji": ":sparkles: add scoped change",
                    "scipy": "ENH(scope): add some more text",
                }
            ],
        },
        "1.2.0-alpha.2": {
            "changelog_sections": {
                # ORDER matters here since greater than 1 commit, changelogs sections are alphabetized
                # But value is ultimately defined by the commits, which means the commits are
                # referenced by index value
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [1]},
                    {"section": "Features", "i_commits": [0]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [1]},
                    {"section": ":sparkles:", "i_commits": [0]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [0]},
                    {"section": "Fix", "i_commits": [1]},
                ],
            },
            "commits": [
                {
                    "angular": "feat(scope): add some more text",
                    "emoji": ":sparkles: add scoped change",
                    "scipy": "ENH(scope): add some more text",
                },
                {
                    "angular": "fix(scope): correct some text",
                    "emoji": ":bug: correct feature-scoped text",
                    "scipy": "MAINT(scope): correct some text",
                },
            ],
        },
    }

    def _get_commits_for_git_flow_repo_w_2_release_channels(
        commit_type: CommitConvention = "angular",
    ) -> RepoDefinition:
        return extract_commit_convention_from_base_repo_def(
            base_definition, commit_type
        )

    return _get_commits_for_git_flow_repo_w_2_release_channels


@pytest.fixture(scope="session")
def get_versions_for_git_flow_repo_w_2_release_channels(
    get_commits_for_git_flow_repo_w_2_release_channels: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_git_flow_repo_w_2_release_channels() -> list[VersionStr]:
        return list(get_commits_for_git_flow_repo_w_2_release_channels().keys())

    return _get_versions_for_git_flow_repo_w_2_release_channels


@pytest.fixture(scope="session")
def build_git_flow_repo_w_2_release_channels(
    get_commits_for_git_flow_repo_w_2_release_channels: GetRepoDefinitionFn,
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
    This fixture returns a function that when called will build a git repo that
    uses the git flow branching strategy with 2 release channels
        1. alpha feature releases
        2. release candidate releases
    """

    def _build_git_flow_repo_w_2_release_channels(
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
                # branch "feature" has prerelease suffix of "alpha"
                "tool.semantic_release.branches.features": {
                    "match": r"feat/.+",
                    "prerelease": True,
                    "prerelease_token": "alpha",
                },
                **(extra_configs or {}),
            },
        )

        # Retrieve/Define project vars that will be used to create the repo below
        repo_def = get_commits_for_git_flow_repo_w_2_release_channels(commit_type)
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

            # Grab reference to main branch
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

            # Publish initial feature release (v0.1.0) [updates tool.poetry.version]
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Change to a dev branch
            dev_branch_head = git_repo.create_head(
                DEV_BRANCH_NAME, commit=main_branch_head.commit
            )
            dev_branch_head.checkout()

            # Change to a feature branch
            feat_branch_head = git_repo.create_head(
                FEAT_BRANCH_1_NAME, commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Prepare for a prerelease (by adding a change, direct commit to dev branch)
            # modify && commit modification -> update commit msg with sha & url
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

            # Make a patch level alpha release (v0.1.1-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Prepare for a major feature release
            # modify && commit modification -> update commit msg with sha & url
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

            # Make a major feature alpha release (v1.0.0-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Prepare for a major feature release
            # modify && commit modification -> update commit msg with sha & url
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-2],
                ),
                *next_version_def["commits"][-2:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch (saving result definition)
            next_version_def["commits"][-2] = create_merge_commit(
                git_repo=git_repo,
                branch_name=feat_branch_head.name,
                commit_def=next_version_def["commits"][-2],
                fast_forward=False,
            )

            # checkout main branch (in prep for merge & release)
            main_branch_head.checkout()

            # Merge dev branch into main branch (saving result definition)
            next_version_def["commits"][-1] = create_merge_commit(
                git_repo=git_repo,
                branch_name=dev_branch_head.name,
                commit_def=next_version_def["commits"][-1],
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

            # Make a major feature release (v1.0.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Update & Change to the dev branch
            dev_branch_head.checkout()
            git_repo.git.merge(main_branch_head.name, ff=True)

            # Switch to a feature branch
            feat_branch_head = git_repo.create_head(
                FEAT_BRANCH_2_NAME, commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Prepare for a minor feature release
            # modify && commit modification -> update commit msg with sha & url
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-2],
                ),
                *next_version_def["commits"][-2:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch (saving result definition)
            next_version_def["commits"][-2] = create_merge_commit(
                git_repo=git_repo,
                branch_name=feat_branch_head.name,
                commit_def=next_version_def["commits"][-2],
                fast_forward=False,
            )

            # checkout main branch (in prep for merge & release)
            main_branch_head.checkout()

            # Merge dev branch into main branch (saving result definition)
            next_version_def["commits"][-1] = create_merge_commit(
                git_repo=git_repo,
                branch_name=dev_branch_head.name,
                commit_def=next_version_def["commits"][-1],
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

            # Make a minor feature release (v1.1.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Update & Change to the dev branch
            dev_branch_head.checkout()
            git_repo.git.merge(main_branch_head.name, ff=True)

            # Switch to a fix branch
            fix_branch_head = git_repo.create_head(
                FIX_BRANCH_1_NAME, commit=dev_branch_head.commit
            )
            fix_branch_head.checkout()

            # Prepare for a patch level release
            # modify && commit modification -> update commit msg with sha & url
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-2],
                ),
                *next_version_def["commits"][-2:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch (saving result definition)
            next_version_def["commits"][-2] = create_merge_commit(
                git_repo=git_repo,
                branch_name=fix_branch_head.name,
                commit_def=next_version_def["commits"][-2],
                fast_forward=False,
            )

            # checkout main branch (in prep for merge & release)
            main_branch_head.checkout()

            # Merge dev branch into main branch (saving result definition)
            next_version_def["commits"][-1] = create_merge_commit(
                git_repo=git_repo,
                branch_name=dev_branch_head.name,
                commit_def=next_version_def["commits"][-1],
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

            # Make a patch level release (v1.1.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Update & Change to the dev branch
            dev_branch_head.checkout()
            git_repo.git.merge(main_branch_head.name, ff=True)

            # Switch to a feature branch
            feat_branch_head = git_repo.create_head(
                FEAT_BRANCH_3_NAME, commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Prepare for an alpha prerelease
            # modify && commit modification -> update commit msg with sha & url
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

            # Make an alpha prerelease (v1.2.0-alpha.1) on the feature branch
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Prepare for a 2nd prerelease with 2 commits
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

            # Make a 2nd alpha prerelease (v1.2.0-alpha.2) on the feature branch
            create_release_tagged_commit(git_repo, next_version, tag_format)

            return repo_dir, hvcs

    return _build_git_flow_repo_w_2_release_channels


# --------------------------------------------------------------------------- #
# Test-level fixtures that will cache the built directory & set up test case  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_git_flow_angular_commits(
    build_git_flow_repo_w_2_release_channels: BuildRepoFn,
    build_spec_hash_for_git_flow_repo_w_2_release_channels: str,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_git_flow_repo_w_2_release_channels(cached_repo_path, "angular")

    build_repo_or_copy_cache(
        repo_name=repo_w_git_flow_angular_commits.__name__,
        build_spec_hash=build_spec_hash_for_git_flow_repo_w_2_release_channels,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_git_flow_emoji_commits(
    build_git_flow_repo_w_2_release_channels: BuildRepoFn,
    build_spec_hash_for_git_flow_repo_w_2_release_channels: str,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_git_flow_repo_w_2_release_channels(cached_repo_path, "emoji")

    build_repo_or_copy_cache(
        repo_name=repo_w_git_flow_emoji_commits.__name__,
        build_spec_hash=build_spec_hash_for_git_flow_repo_w_2_release_channels,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()


@pytest.fixture
def repo_w_git_flow_scipy_commits(
    build_git_flow_repo_w_2_release_channels: BuildRepoFn,
    build_spec_hash_for_git_flow_repo_w_2_release_channels: str,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    def _build_repo(cached_repo_path: Path):
        build_git_flow_repo_w_2_release_channels(cached_repo_path, "scipy")

    build_repo_or_copy_cache(
        repo_name=repo_w_git_flow_scipy_commits.__name__,
        build_spec_hash=build_spec_hash_for_git_flow_repo_w_2_release_channels,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    return example_project_git_repo()
