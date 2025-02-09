from __future__ import annotations

from datetime import timedelta
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from semantic_release.cli.config import ChangelogOutputFormat

import tests.conftest
import tests.const
import tests.util
from tests.const import (
    DEFAULT_BRANCH_NAME,
    EXAMPLE_HVCS_DOMAIN,
    INITIAL_COMMIT_MESSAGE,
    RepoActionStep,
)

if TYPE_CHECKING:
    from typing import Sequence

    from tests.conftest import (
        GetCachedRepoDataFn,
        GetMd5ForSetOfFilesFn,
        GetStableDateNowFn,
    )
    from tests.fixtures.example_project import ExProjectDir
    from tests.fixtures.git_repo import (
        BuildRepoFromDefinitionFn,
        BuildRepoOrCopyCacheFn,
        BuildSpecificRepoFn,
        BuiltRepoResult,
        CommitConvention,
        ConvertCommitSpecsToCommitDefsFn,
        ConvertCommitSpecToCommitDefFn,
        ExProjectGitRepoFn,
        FormatGitHubMergeCommitMsgFn,
        GetRepoDefinitionFn,
        RepoActions,
        RepoActionWriteChangelogsDestFile,
        TomlSerializableTypes,
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
def build_spec_hash_4_github_flow_repo_w_feature_release_channel(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_github_flow_repo_w_feature_release_channel: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(
        deps_files_4_github_flow_repo_w_feature_release_channel
    )


@pytest.fixture(scope="session")
def get_repo_definition_4_github_flow_repo_w_feature_release_channel(
    convert_commit_specs_to_commit_defs: ConvertCommitSpecsToCommitDefsFn,
    convert_commit_spec_to_commit_def: ConvertCommitSpecToCommitDefFn,
    format_merge_commit_msg_github: FormatGitHubMergeCommitMsgFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    stable_now_date: GetStableDateNowFn,
) -> GetRepoDefinitionFn:
    """
    Builds a repository with the GitHub Flow branching strategy using merge commits
    for alpha feature releases and official releases on the default branch.
    """

    def _get_repo_from_defintion(
        commit_type: CommitConvention,
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = False,
    ) -> Sequence[RepoActions]:
        stable_now_datetime = stable_now_date()
        commit_timestamp_gen = (
            (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
            for i in count(step=1)
        )
        pr_num_gen = (i for i in count(start=2, step=1))

        changelog_file_definitons: Sequence[RepoActionWriteChangelogsDestFile] = [
            {
                "path": changelog_md_file,
                "format": ChangelogOutputFormat.MARKDOWN,
            },
            {
                "path": changelog_rst_file,
                "format": ChangelogOutputFormat.RESTRUCTURED_TEXT,
            },
        ]

        repo_construction_steps: list[RepoActions] = []

        repo_construction_steps.append(
            {
                "action": RepoActionStep.CONFIGURE,
                "details": {
                    "commit_type": commit_type,
                    "hvcs_client_name": hvcs_client_name,
                    "hvcs_domain": hvcs_domain,
                    "tag_format_str": tag_format_str,
                    "mask_initial_release": mask_initial_release,
                    "extra_configs": {
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
                },
            }
        )

        # Make initial release
        new_version = "1.0.0"

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "conventional": INITIAL_COMMIT_MESSAGE,
                                    "emoji": INITIAL_COMMIT_MESSAGE,
                                    "scipy": INITIAL_COMMIT_MESSAGE,
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": bool(
                                        commit_type == "emoji"
                                    ),
                                },
                                {
                                    "conventional": "feat: add new feature",
                                    "emoji": ":sparkles: add new feature",
                                    "scipy": "ENH: add new feature",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a fix and release it as an alpha release
        new_version = "1.0.1-alpha.1"
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": FIX_BRANCH_1_NAME,
                            "start_branch": DEFAULT_BRANCH_NAME,
                        }
                    },
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "conventional": "fix: correct some text",
                                    "emoji": ":bug: correct some text",
                                    "scipy": "MAINT: correct some text",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Update the fix and release another alpha release
        new_version = "1.0.1-alpha.2"
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "conventional": "fix: adjust text to resolve",
                                    "emoji": ":bug: adjust text to resolve",
                                    "scipy": "MAINT: adjust text to resolve",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Merge the fix branch into the default branch and formally release it
        new_version = "1.0.1"
        fix_branch_pr_number = next(pr_num_gen)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.GIT_MERGE,
                    "details": {
                        "branch_name": FIX_BRANCH_1_NAME,
                        "fast_forward": False,
                        "commit_def": convert_commit_spec_to_commit_def(
                            {
                                "conventional": format_merge_commit_msg_github(
                                    pr_number=fix_branch_pr_number,
                                    branch_name=FIX_BRANCH_1_NAME,
                                ),
                                "emoji": format_merge_commit_msg_github(
                                    pr_number=fix_branch_pr_number,
                                    branch_name=FIX_BRANCH_1_NAME,
                                ),
                                "scipy": format_merge_commit_msg_github(
                                    pr_number=fix_branch_pr_number,
                                    branch_name=FIX_BRANCH_1_NAME,
                                ),
                                "datetime": next(commit_timestamp_gen),
                                "include_in_changelog": bool(commit_type == "emoji"),
                            },
                            commit_type,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a feature branch and release it as an alpha release
        new_version = "1.1.0-alpha.1"

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": FEAT_BRANCH_1_NAME,
                            "start_branch": DEFAULT_BRANCH_NAME,
                        },
                    },
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "conventional": "feat(cli): add cli interface",
                                    "emoji": ":sparkles: add cli interface",
                                    "scipy": "ENH: add cli interface",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                        )
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Merge the feature branch and officially release it
        new_version = "1.1.0"
        feat_branch_pr_number = next(pr_num_gen)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.GIT_MERGE,
                    "details": {
                        "branch_name": FEAT_BRANCH_1_NAME,
                        "fast_forward": False,
                        "commit_def": convert_commit_spec_to_commit_def(
                            {
                                "conventional": format_merge_commit_msg_github(
                                    pr_number=feat_branch_pr_number,
                                    branch_name=FEAT_BRANCH_1_NAME,
                                ),
                                "emoji": format_merge_commit_msg_github(
                                    pr_number=feat_branch_pr_number,
                                    branch_name=FEAT_BRANCH_1_NAME,
                                ),
                                "scipy": format_merge_commit_msg_github(
                                    pr_number=feat_branch_pr_number,
                                    branch_name=FEAT_BRANCH_1_NAME,
                                ),
                                "datetime": next(commit_timestamp_gen),
                                "include_in_changelog": bool(commit_type == "emoji"),
                            },
                            commit_type,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": new_version,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitons,
                                },
                            },
                        ],
                    },
                },
            ]
        )

        return repo_construction_steps

    return _get_repo_from_defintion


@pytest.fixture(scope="session")
def build_repo_w_github_flow_w_feature_release_channel(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_github_flow_repo_w_feature_release_channel: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_github_flow_repo_w_feature_release_channel: str,
) -> BuildSpecificRepoFn:
    def _build_specific_repo_type(
        repo_name: str, commit_type: CommitConvention, dest_dir: Path
    ) -> Sequence[RepoActions]:
        def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
            repo_construction_steps = (
                get_repo_definition_4_github_flow_repo_w_feature_release_channel(
                    commit_type=commit_type,
                )
            )
            return build_repo_from_definition(cached_repo_path, repo_construction_steps)

        build_repo_or_copy_cache(
            repo_name=repo_name,
            build_spec_hash=build_spec_hash_4_github_flow_repo_w_feature_release_channel,
            build_repo_func=_build_repo,
            dest_dir=dest_dir,
        )

        if not (cached_repo_data := get_cached_repo_data(proj_dirname=repo_name)):
            raise ValueError("Failed to retrieve repo data from cache")

        return cached_repo_data["build_definition"]

    return _build_specific_repo_type


# --------------------------------------------------------------------------- #
# Test-level fixtures that will cache the built directory & set up test case  #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_conventional_commits(
    build_repo_w_github_flow_w_feature_release_channel: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = (
        repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__
    )
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_repo_w_github_flow_w_feature_release_channel(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_emoji_commits(
    build_repo_w_github_flow_w_feature_release_channel: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_repo_w_github_flow_w_feature_release_channel(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_scipy_commits(
    build_repo_w_github_flow_w_feature_release_channel: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_repo_w_github_flow_w_feature_release_channel(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }
