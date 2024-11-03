from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import pytest
from git import Repo

from semantic_release.cli.config import ChangelogOutputFormat

from tests.const import EXAMPLE_HVCS_DOMAIN, NULL_HEX_SHA
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
        SimulateDefaultChangelogCreationFn,
        TomlSerializableTypes,
        VersionStr,
    )


@pytest.fixture(scope="session")
def get_commits_for_git_flow_repo_w_3_release_channels() -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "0.1.0": {
            "changelog_sections": {
                "angular": [{"section": "Unknown", "i_commits": [0]}],
                "emoji": [{"section": "Other", "i_commits": [0]}],
                "scipy": [{"section": "Unknown", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": {"msg": "Initial commit", "sha": NULL_HEX_SHA},
                    "emoji": {"msg": "Initial commit", "sha": NULL_HEX_SHA},
                    "scipy": {"msg": "Initial commit", "sha": NULL_HEX_SHA},
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
                    "angular": {"msg": "fix: correct some text", "sha": NULL_HEX_SHA},
                    "emoji": {"msg": ":bug: correct some text", "sha": NULL_HEX_SHA},
                    "scipy": {"msg": "MAINT: correct some text", "sha": NULL_HEX_SHA},
                }
            ],
        },
        "1.0.0-rc.1": {
            "changelog_sections": {
                "angular": [
                    {"section": "Breaking", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [1]},
                ],
                "emoji": [
                    {"section": ":boom:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [1]},
                ],
                "scipy": [
                    {"section": "Breaking", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [1]},
                ],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "feat!: add revolutionary feature",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":boom: add revolutionary feature",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "API: add revolutionary feature",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'feat/feature-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'feat/feature-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'feat/feature-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        "1.0.0": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [2, 1]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [2, 1]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [2, 1]},
                ],
            },
            "commits": [
                {
                    "angular": {"msg": "feat: add some more text", "sha": NULL_HEX_SHA},
                    "emoji": {
                        "msg": ":sparkles: add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {"msg": "ENH: add some more text", "sha": NULL_HEX_SHA},
                },
                {
                    "angular": {
                        "msg": "Merge branch 'feat/feature-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'feat/feature-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'feat/feature-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        "1.1.0-alpha.1": {
            "changelog_sections": {
                "angular": [{"section": "Features", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "feat(dev): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":sparkles: (dev) add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "ENH(dev): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        "1.1.0-alpha.2": {
            "changelog_sections": {
                "angular": [{"section": "Features", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "feat(dev): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":sparkles: (dev) add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "ENH(dev): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        "1.1.0-rc.1": {
            "changelog_sections": {
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [1]},
                    {"section": "Unknown", "i_commits": [2, 0]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [1]},
                    {"section": "Other", "i_commits": [2, 0]},
                ],
                "scipy": [
                    {"section": "Fix", "i_commits": [1]},
                    {"section": "Unknown", "i_commits": [2, 0]},
                ],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "Merge branch 'feat/feature-3' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'feat/feature-3' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'feat/feature-3' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "fix(dev): correct some text",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":bug: correct dev-scoped text",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "MAINT(dev): correct some text",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'fix/patch-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'fix/patch-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'fix/patch-1' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        "1.1.0-rc.2": {
            "changelog_sections": {
                "angular": [
                    {"section": "Features", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [1]},
                ],
                "emoji": [
                    {"section": ":sparkles:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [1]},
                ],
                "scipy": [
                    {"section": "Feature", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [1]},
                ],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "feat(scope): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":sparkles: add scoped change",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "ENH(scope): add some more text",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'feat/feature-4' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'feat/feature-4' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'feat/feature-4' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
        # TODO: shouldn't be any commit, just a merge into main and release rc.2 as it was successful
        # this is not implemented because currently not supported
        "1.1.0": {
            "changelog_sections": {
                "angular": [
                    {"section": "Bug Fixes", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [2, 1]},
                ],
                "emoji": [
                    {"section": ":bug:", "i_commits": [0]},
                    {"section": "Other", "i_commits": [2, 1]},
                ],
                "scipy": [
                    {"section": "Fix", "i_commits": [0]},
                    {"section": "Unknown", "i_commits": [2, 1]},
                ],
            },
            "commits": [
                {
                    "angular": {
                        "msg": "fix(scope): correct some text",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": ":bug: correct feature-scoped text",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "MAINT(scope): correct some text",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'fix/patch-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'fix/patch-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'fix/patch-2' into 'dev'",
                        "sha": NULL_HEX_SHA,
                    },
                },
                {
                    "angular": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                    "emoji": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                    "scipy": {
                        "msg": "Merge branch 'dev' into 'main'",
                        "sha": NULL_HEX_SHA,
                    },
                },
            ],
        },
    }

    def _get_commits_for_git_flow_repo_w_3_release_channels(
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
                    deepcopy(message_variants[commit_type])
                    for message_variants in version_def["commits"]
                ],
            }

        return definition

    return _get_commits_for_git_flow_repo_w_3_release_channels


@pytest.fixture(scope="session")
def get_versions_for_git_flow_repo_w_3_release_channels(
    get_commits_for_git_flow_repo_w_3_release_channels: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_git_flow_repo_w_3_release_channels() -> list[VersionStr]:
        return list(get_commits_for_git_flow_repo_w_3_release_channels().keys())

    return _get_versions_for_git_flow_repo_w_3_release_channels


@pytest.fixture(scope="session")
def build_git_flow_repo_w_3_release_channels(
    get_commits_for_git_flow_repo_w_3_release_channels: GetRepoDefinitionFn,
    build_configured_base_repo: BuildRepoFn,
    default_tag_format_str: str,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
    create_release_tagged_commit: CreateReleaseFn,
) -> BuildRepoFn:
    def _build_git_flow_repo_w_3_release_channels(
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
                # branch "dev" has prerelease suffix of "rc"
                "tool.semantic_release.branches.dev": {
                    "match": r"^dev$",
                    "prerelease": True,
                    "prerelease_token": "rc",
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
        repo_def = get_commits_for_git_flow_repo_w_3_release_channels(commit_type)
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

            # Grab reference to the main branch
            main_branch_head = git_repo.heads["main"]

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

            # Make initial feature release (v0.1.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Change to a dev branch
            dev_branch_head = git_repo.create_head(
                "dev", commit=main_branch_head.commit
            )
            dev_branch_head.checkout()

            # Change to a feature branch
            feat_branch_head = git_repo.create_head(
                "feat/feature-1", commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Prepare for a prerelease (by adding a change, direct commit to dev branch)
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
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make a patch level alpha release (v0.1.1-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Prepare for a major feature release
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-1],
                ),
                *next_version_def["commits"][-1:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                feat_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-1]["msg"],
            )
            next_version_def["commits"][-1]["sha"] = git_repo.head.commit.hexsha

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

            # Make a major feature release candidate (v1.0.0-rc.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Switch to a feature branch
            feat_branch_head = git_repo.create_head(
                "feat/feature-2", commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Add non-breaking feature commit
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-2],
                ),
                *next_version_def["commits"][-2:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                feat_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-2]["msg"],
            )
            next_version_def["commits"][-2]["sha"] = git_repo.head.commit.hexsha

            # checkout main branch (in prep for merge & release)
            main_branch_head.checkout()

            # Merge dev branch into main branch
            git_repo.git.merge(
                dev_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-1]["msg"],
            )
            next_version_def["commits"][-1]["sha"] = git_repo.head.commit.hexsha

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
                "feat/feature-3", commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Prepare for a minor bump release candidate
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
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make a minor bump release candidate (v1.1.0-alpha.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

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
            )

            # write expected RST changelog to this version
            simulate_default_changelog_creation(
                repo_def,
                hvcs=hvcs,
                max_version=next_version,
                dest_file=repo_dir.joinpath(changelog_rst_file),
                output_format=ChangelogOutputFormat.RESTRUCTURED_TEXT,
            )

            # Make a 2nd release candidate (v1.1.0-alpha.2)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                feat_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][0]["msg"],
            )
            next_version_def["commits"][0]["sha"] = git_repo.head.commit.hexsha

            # Switch to a feature branch
            fix_branch_head = git_repo.create_head(
                "fix/patch-1", commit=dev_branch_head.commit
            )
            fix_branch_head.checkout()

            # Make a patch commit
            next_version_def["commits"] = [
                next_version_def["commits"][0],
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][1:-1],
                ),
                next_version_def["commits"][-1],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                fix_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-1]["msg"],
            )
            next_version_def["commits"][-1]["sha"] = git_repo.head.commit.hexsha

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

            # Make an alpha prerelease (v1.1.0-rc.1)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Switch to a feature branch
            feat_branch_head = git_repo.create_head(
                "feat/feature-4", commit=dev_branch_head.commit
            )
            feat_branch_head.checkout()

            # Make a another feature commit
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-1],
                ),
                next_version_def["commits"][-1],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                feat_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-1]["msg"],
            )
            next_version_def["commits"][-1]["sha"] = git_repo.head.commit.hexsha

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

            # Make a 2nd alpha prerelease (v1.1.0-rc.2)
            create_release_tagged_commit(git_repo, next_version, tag_format)

            # Increment version pointer
            next_version = next(versions)
            next_version_def = repo_def[next_version]

            # Switch to a fix branch
            fix_branch_head = git_repo.create_head(
                "fix/patch-2", commit=dev_branch_head.commit
            )
            fix_branch_head.checkout()

            # Make a patch level commit
            next_version_def["commits"] = [
                *simulate_change_commits_n_rtn_changelog_entry(
                    git_repo,
                    next_version_def["commits"][:-2],
                ),
                *next_version_def["commits"][-2:],
            ]

            # checkout dev branch (in prep for merge)
            dev_branch_head.checkout()

            # Merge feature branch into dev branch
            git_repo.git.merge(
                fix_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-2]["msg"],
            )
            next_version_def["commits"][-2]["sha"] = git_repo.head.commit.hexsha

            # checkout main branch (in prep for merge & release)
            main_branch_head.checkout()

            # Merge dev branch into main branch
            git_repo.git.merge(
                dev_branch_head.name,
                no_ff=True,
                m=next_version_def["commits"][-1]["msg"],
            )
            next_version_def["commits"][-1]["sha"] = git_repo.head.commit.hexsha

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

            # Make a 3rd alpha prerelease (v1.1.0)
            create_release_tagged_commit(git_repo, next_version, tag_format)

        return repo_dir, hvcs

    return _build_git_flow_repo_w_3_release_channels


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_3_release_channels_angular_commits_tag_format(
    build_git_flow_repo_w_3_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_3_release_channels_angular_commits_tag_format.__name__
    )
    build_git_flow_repo_w_3_release_channels(
        cached_repo_path, "angular", tag_format_str="vpy{version}"
    )
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_3_release_channels_angular_commits(
    build_git_flow_repo_w_3_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_3_release_channels_angular_commits.__name__
    )
    build_git_flow_repo_w_3_release_channels(cached_repo_path, "angular")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_3_release_channels_emoji_commits(
    build_git_flow_repo_w_3_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_3_release_channels_emoji_commits.__name__
    )
    build_git_flow_repo_w_3_release_channels(cached_repo_path, "emoji")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_3_release_channels_scipy_commits(
    build_git_flow_repo_w_3_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_3_release_channels_scipy_commits.__name__
    )
    build_git_flow_repo_w_3_release_channels(cached_repo_path, "scipy")
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_with_git_flow_and_release_channels_angular_commits_using_tag_format(
    cached_repo_w_git_flow_n_3_release_channels_angular_commits_tag_format: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_3_release_channels_angular_commits_tag_format.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_3_release_channels_angular_commits_tag_format,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_and_release_channels_angular_commits(
    cached_repo_w_git_flow_n_3_release_channels_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_3_release_channels_angular_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_3_release_channels_angular_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_and_release_channels_emoji_commits(
    cached_repo_w_git_flow_n_3_release_channels_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_3_release_channels_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_3_release_channels_emoji_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_and_release_channels_scipy_commits(
    cached_repo_w_git_flow_n_3_release_channels_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_3_release_channels_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_3_release_channels_scipy_commits,
        example_project_dir,
    )
    return example_project_git_repo()
