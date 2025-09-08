from __future__ import annotations

from datetime import timedelta
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.version.version import Version

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
    from typing import Any, Sequence

    from semantic_release.commit_parser._base import CommitParser, ParserOptions
    from semantic_release.commit_parser.conventional.parser import (
        ConventionalCommitParser,
    )
    from semantic_release.commit_parser.emoji import EmojiCommitParser
    from semantic_release.commit_parser.scipy import ScipyCommitParser
    from semantic_release.commit_parser.token import ParseResult

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
        RepoActionGitMerge,
        RepoActionGitMergeDetails,
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
    default_conventional_parser: ConventionalCommitParser,
    default_emoji_parser: EmojiCommitParser,
    default_scipy_parser: ScipyCommitParser,
    default_tag_format_str: str,
) -> GetRepoDefinitionFn:
    """
    Builds a repository with the GitHub Flow branching strategy using merge commits
    for alpha feature releases and official releases on the default branch.
    """
    parser_classes: dict[CommitConvention, CommitParser[Any, Any]] = {
        "conventional": default_conventional_parser,
        "emoji": default_emoji_parser,
        "scipy": default_scipy_parser,
    }

    def _get_repo_from_definition(
        commit_type: CommitConvention,
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = True,
        ignore_merge_commits: bool = True,
    ) -> Sequence[RepoActions]:
        stable_now_datetime = stable_now_date()
        commit_timestamp_gen = (
            (stable_now_datetime + timedelta(seconds=i)).isoformat(timespec="seconds")
            for i in count(step=1)
        )
        pr_num_gen = (i for i in count(start=2, step=1))
        commit_parser = cast(
            "CommitParser[ParseResult, ParserOptions]",
            parser_classes[commit_type],
        )

        changelog_file_definitions: Sequence[RepoActionWriteChangelogsDestFile] = [
            {
                "path": changelog_md_file,
                "format": ChangelogOutputFormat.MARKDOWN,
                "mask_initial_release": mask_initial_release,
            },
            {
                "path": changelog_rst_file,
                "format": ChangelogOutputFormat.RESTRUCTURED_TEXT,
                "mask_initial_release": mask_initial_release,
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
                    "tag_format_str": tag_format_str or default_tag_format_str,
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
                        "tool.semantic_release.commit_parser_options.ignore_merge_commits": ignore_merge_commits,
                        "tool.semantic_release.allow_zero_version": False,
                        **(extra_configs or {}),
                    },
                },
            }
        )

        # Make initial release
        new_version = Version.parse(
            "1.0.0", tag_format=(tag_format_str or default_tag_format_str)
        )

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_db_initial := "db_c1_initial_commit"),
                                    "conventional": INITIAL_COMMIT_MESSAGE,
                                    "emoji": INITIAL_COMMIT_MESSAGE,
                                    "scipy": INITIAL_COMMIT_MESSAGE,
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": bool(
                                        commit_type == "emoji"
                                    ),
                                },
                                {
                                    "cid": (cid_db_c2_feat := "db_c2_feat"),
                                    "conventional": "feat: add new feature",
                                    "emoji": ":sparkles: add new feature",
                                    "scipy": "ENH: add new feature",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                            parser=commit_parser,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_db_initial, cid_db_c2_feat],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a fix and release it as an alpha release
        new_version = Version.parse("1.0.1-alpha.1", tag_format=new_version.tag_format)
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
                                    "cid": (cid_fib1_c1_fix := "fix_branch_c1_fix"),
                                    "conventional": "fix: correct some text\n\nResolves: #123",
                                    "emoji": ":bug: correct some text\n\nResolves: #123",
                                    "scipy": "MAINT: correct some text\n\nResolves: #123",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                            parser=commit_parser,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_fib1_c1_fix],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Update the fix and release another alpha release
        new_version = Version.parse("1.0.1-alpha.2", tag_format=new_version.tag_format)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_fib1_c2_fix := "fix_branch_1_c2_fix"),
                                    "conventional": "fix: adjust text to resolve",
                                    "emoji": ":bug: adjust text to resolve",
                                    "scipy": "MAINT: adjust text to resolve",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                            parser=commit_parser,
                        ),
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_fib1_c2_fix],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Merge the fix branch into the default branch and formally release it
        new_version = Version.parse("1.0.1", tag_format=new_version.tag_format)

        merge_def_type_placeholder: RepoActionGitMerge[RepoActionGitMergeDetails] = {
            "action": RepoActionStep.GIT_MERGE,
            "details": {
                "branch_name": FIX_BRANCH_1_NAME,
                "fast_forward": False,
                "commit_def": convert_commit_spec_to_commit_def(
                    {
                        "cid": (cid_fib1_merge := "fix_branch_1_merge"),
                        "conventional": (
                            merge_msg := format_merge_commit_msg_github(
                                pr_number=next(pr_num_gen),
                                branch_name=FIX_BRANCH_1_NAME,
                            )
                        ),
                        "emoji": merge_msg,
                        "scipy": merge_msg,
                        "datetime": next(commit_timestamp_gen),
                        "include_in_changelog": not ignore_merge_commits,
                    },
                    commit_type,
                    parser=commit_parser,
                ),
            },
        }

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                merge_def_type_placeholder,
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_fib1_merge],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a feature branch and release it as an alpha release
        new_version = Version.parse("1.1.0-alpha.1", tag_format=new_version.tag_format)

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
                                    "cid": (
                                        cid_feb1_c1_feat := "feat_branch_1_c1_feat"
                                    ),
                                    "conventional": "feat(cli): add cli interface",
                                    "emoji": ":sparkles: add cli interface",
                                    "scipy": "ENH: add cli interface",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                            parser=commit_parser,
                        )
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_feb1_c1_feat],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Merge the feature branch and officially release it
        new_version = Version.parse("1.1.0", tag_format=new_version.tag_format)

        merge_def_type_placeholder = {
            "action": RepoActionStep.GIT_MERGE,
            "details": {
                "branch_name": FEAT_BRANCH_1_NAME,
                "fast_forward": False,
                "commit_def": convert_commit_spec_to_commit_def(
                    {
                        "cid": (cid_feb1_merge := "feat_branch_1_merge"),
                        "conventional": (
                            merge_msg := format_merge_commit_msg_github(
                                pr_number=next(pr_num_gen),
                                branch_name=FEAT_BRANCH_1_NAME,
                            )
                        ),
                        "emoji": merge_msg,
                        "scipy": merge_msg,
                        "datetime": next(commit_timestamp_gen),
                        "include_in_changelog": not ignore_merge_commits,
                    },
                    commit_type,
                    parser=commit_parser,
                ),
            },
        }

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                merge_def_type_placeholder,
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(new_version),
                        "tag_format": new_version.tag_format,
                        "datetime": next(commit_timestamp_gen),
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_feb1_merge],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        return repo_construction_steps

    return _get_repo_from_definition


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
