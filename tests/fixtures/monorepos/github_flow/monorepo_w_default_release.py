from __future__ import annotations

from datetime import timedelta
from itertools import count
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, cast

import pytest

from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.commit_parser.conventional.options_monorepo import (
    ConventionalCommitMonorepoParserOptions,
)
from semantic_release.commit_parser.conventional.parser_monorepo import (
    ConventionalCommitMonorepoParser,
)
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
    from typing import Sequence

    from semantic_release.commit_parser._base import CommitParser, ParserOptions
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
        CommitSpec,
        ConvertCommitSpecsToCommitDefsFn,
        ConvertCommitSpecToCommitDefFn,
        ExProjectGitRepoFn,
        FormatGitHubSquashCommitMsgFn,
        GetRepoDefinitionFn,
        RepoActionChangeDirectory,
        RepoActions,
        RepoActionWriteChangelogsDestFile,
        TomlSerializableTypes,
    )


@pytest.fixture(scope="session")
def deps_files_4_github_flow_monorepo_w_default_release_channel(
    deps_files_4_example_git_monorepo: list[Path],
) -> list[Path]:
    return [
        *deps_files_4_example_git_monorepo,
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_4_github_flow_monorepo_w_default_release_channel(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_github_flow_monorepo_w_default_release_channel: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(
        deps_files_4_github_flow_monorepo_w_default_release_channel
    )


@pytest.fixture(scope="session")
def get_repo_definition_4_github_flow_monorepo_w_default_release_channel(
    convert_commit_specs_to_commit_defs: ConvertCommitSpecsToCommitDefsFn,
    convert_commit_spec_to_commit_def: ConvertCommitSpecToCommitDefFn,
    format_squash_commit_msg_github: FormatGitHubSquashCommitMsgFn,
    monorepo_pkg1_changelog_md_file: Path,
    monorepo_pkg1_changelog_rst_file: Path,
    monorepo_pkg2_changelog_md_file: Path,
    monorepo_pkg2_changelog_rst_file: Path,
    monorepo_pkg1_name: str,
    monorepo_pkg2_name: str,
    monorepo_pkg1_dir: str,
    monorepo_pkg2_dir: str,
    monorepo_pkg1_docs_dir: str,
    monorepo_pkg2_docs_dir: str,
    monorepo_pkg1_version_py_file: Path,
    monorepo_pkg2_version_py_file: Path,
    monorepo_pkg1_pyproject_toml_file: Path,
    monorepo_pkg2_pyproject_toml_file: Path,
    stable_now_date: GetStableDateNowFn,
    default_tag_format_str: str,
) -> GetRepoDefinitionFn:
    """
    Builds a Monorepo with the GitHub Flow branching strategy and a squash commit merging strategy
    for a single release channel on the default branch.

    Implementation:
    - The monorepo contains two packages, each with its own internal changelog but shared template.
    - The repository implements the following git graph:

    ```
    * chore(release): pkg1@1.1.0 [skip ci] (tag: pkg1-v1.1.0, branch: main, HEAD -> main)
    * feat(pkg1): file modified outside of pkg 1, identified by scope (#5)
    |
    | * docs: pkg1 docs modified outside of pkg 1, identified by path filter (branch: pkg1/feat/pr-4)
    | * feat(pkg1): file modified outside of pkg 1, identified by scope
    |/
    * chore(release): pkg2@1.1.1 [skip ci] (tag: pkg2-v1.1.1)
    * fix(pkg2-cli): file modified outside of pkg 2, identified by scope (#4)
    |
    | * fix(pkg2-cli): file modified outside of pkg 2, identified by scope (branch: pkg2/fix/pr-3)
    |/
    * chore(release): pkg2@1.1.0 [skip ci] (tag: pkg2-v1.1.0)
    * feat: no pkg scope but file in pkg 2 directory  (#3)                   # Squash merge of pkg2/feat/pr-2
    * chore(release): pkg1@1.0.1 [skip ci] (tag: pkg1-v1.0.1)
    * fix: no pkg scope but file in pkg 1 directory  (#2)                    # Squash merge of pkg1/fix/pr-1
    |
    | * docs(cli): add cli documentation
    | * test(cli): add cli tests
    | * feat: no pkg scope but file in pkg 2 directory (branch: pkg2/feat/pr-2)
    |/
    | * fix: no pkg scope but file in pkg 1 directory (branch: pkg1/fix/pr-1)
    |/
    * chore(release): pkg2@1.0.0 [skip ci] (tag: pkg2-v1.0.0)          # Initial release of pkg 2
    * chore(release): pkg1@1.0.0 [skip ci] (tag: pkg1-v1.0.0)          # Initial release of pkg 1
    * Initial commit                                                    # Includes core functionality for both packages
    ```
    """

    def _get_repo_from_definition(
        commit_type: CommitConvention,
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = default_tag_format_str,
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

        pkg1_changelog_file_definitions: Sequence[RepoActionWriteChangelogsDestFile] = [
            {
                "path": monorepo_pkg1_changelog_md_file,
                "format": ChangelogOutputFormat.MARKDOWN,
                "mask_initial_release": True,
            },
            {
                "path": monorepo_pkg1_changelog_rst_file,
                "format": ChangelogOutputFormat.RESTRUCTURED_TEXT,
                "mask_initial_release": True,
            },
        ]

        pkg2_changelog_file_definitions: Sequence[RepoActionWriteChangelogsDestFile] = [
            {
                "path": monorepo_pkg2_changelog_md_file,
                "format": ChangelogOutputFormat.MARKDOWN,
                "mask_initial_release": True,
            },
            {
                "path": monorepo_pkg2_changelog_rst_file,
                "format": ChangelogOutputFormat.RESTRUCTURED_TEXT,
                "mask_initial_release": True,
            },
        ]

        change_to_pkg1_dir: RepoActionChangeDirectory = {
            "action": RepoActionStep.CHANGE_DIRECTORY,
            "details": {
                "directory": monorepo_pkg1_dir,
            },
        }

        change_to_pkg2_dir: RepoActionChangeDirectory = {
            "action": RepoActionStep.CHANGE_DIRECTORY,
            "details": {
                "directory": monorepo_pkg2_dir,
            },
        }

        change_to_example_project_dir: RepoActionChangeDirectory = {
            "action": RepoActionStep.CHANGE_DIRECTORY,
            "details": {
                "directory": "/",
            },
        }

        if commit_type != "conventional":
            raise ValueError(f"Unsupported commit type: {commit_type}")

        pkg1_path_filters = (".", f"../../{monorepo_pkg1_docs_dir}")
        pkg1_commit_parser = ConventionalCommitMonorepoParser(
            options=ConventionalCommitMonorepoParserOptions(
                parse_squash_commits=True,
                ignore_merge_commits=ignore_merge_commits,
                scope_prefix=f"{monorepo_pkg1_name}-?",
                path_filters=pkg1_path_filters,
            )
        )

        pkg2_path_filters = (".", f"../../{monorepo_pkg2_docs_dir}")
        pkg2_commit_parser = ConventionalCommitMonorepoParser(
            options=ConventionalCommitMonorepoParserOptions(
                parse_squash_commits=pkg1_commit_parser.options.parse_squash_commits,
                ignore_merge_commits=pkg1_commit_parser.options.ignore_merge_commits,
                scope_prefix=f"{monorepo_pkg2_name}-?",
                path_filters=pkg2_path_filters,
            )
        )

        common_configs: dict[str, TomlSerializableTypes] = {
            # Set the default release branch
            "tool.semantic_release.branches.main": {
                "match": r"^(main|master)$",
                "prerelease": False,
            },
            "tool.semantic_release.allow_zero_version": False,
            "tool.semantic_release.changelog.exclude_commit_patterns": [r"^chore"],
            "tool.semantic_release.commit_parser": f"{commit_type}-monorepo",
            "tool.semantic_release.commit_parser_options.parse_squash_commits": pkg1_commit_parser.options.parse_squash_commits,
            "tool.semantic_release.commit_parser_options.ignore_merge_commits": pkg1_commit_parser.options.ignore_merge_commits,
        }

        mr1_pkg1_fix_branch_name = f"{monorepo_pkg1_name}/fix/pr-1"
        mr2_pkg2_feat_branch_name = f"{monorepo_pkg2_name}/feat/pr-2"
        mr3_pkg2_fix_branch_name = f"{monorepo_pkg2_name}/fix/pr-3"
        mr4_pkg1_feat_branch_name = f"{monorepo_pkg1_name}/feat/pr-4"

        pkg1_new_version = Version.parse(
            "1.0.0", tag_format=f"{monorepo_pkg1_name}-{tag_format_str}"
        )
        pkg2_new_version = Version.parse(
            "1.0.0", tag_format=f"{monorepo_pkg2_name}-{tag_format_str}"
        )

        repo_construction_steps: list[RepoActions] = [
            {
                "action": RepoActionStep.CREATE_MONOREPO,
                "details": {
                    "commit_type": commit_type,
                    "hvcs_client_name": hvcs_client_name,
                    "hvcs_domain": hvcs_domain,
                    "post_actions": [
                        {
                            "action": RepoActionStep.CONFIGURE_MONOREPO,
                            "details": {
                                "package_dir": monorepo_pkg1_dir,
                                "package_name": monorepo_pkg1_name,
                                "tag_format_str": pkg1_new_version.tag_format,
                                "mask_initial_release": mask_initial_release,
                                "extra_configs": {
                                    **common_configs,
                                    "tool.semantic_release.commit_message": (
                                        pkg1_cmt_msg_format := dedent(
                                            f"""\
                                        chore(release): {monorepo_pkg1_name}@{{version}} [skip ci]

                                        Automatically generated by python-semantic-release
                                        """
                                        )
                                    ),
                                    "tool.semantic_release.commit_parser_options.scope_prefix": pkg1_commit_parser.options.scope_prefix,
                                    "tool.semantic_release.commit_parser_options.path_filters": pkg1_path_filters,
                                    **(extra_configs or {}),
                                },
                            },
                        },
                        {
                            "action": RepoActionStep.CONFIGURE_MONOREPO,
                            "details": {
                                "package_dir": monorepo_pkg2_dir,
                                "package_name": monorepo_pkg2_name,
                                "tag_format_str": pkg2_new_version.tag_format,
                                "mask_initial_release": mask_initial_release,
                                "extra_configs": {
                                    **common_configs,
                                    "tool.semantic_release.commit_message": (
                                        pkg2_cmt_msg_format := dedent(
                                            f"""\
                                            chore(release): {monorepo_pkg2_name}@{{version}} [skip ci]

                                            Automatically generated by python-semantic-release
                                            """
                                        )
                                    ),
                                    "tool.semantic_release.commit_parser_options.scope_prefix": pkg2_commit_parser.options.scope_prefix,
                                    "tool.semantic_release.commit_parser_options.path_filters": pkg2_path_filters,
                                    **(extra_configs or {}),
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
                                                cid_c1_initial := "c1_initial_commit"
                                            ),
                                            "conventional": INITIAL_COMMIT_MESSAGE,
                                            "emoji": INITIAL_COMMIT_MESSAGE,
                                            "scipy": INITIAL_COMMIT_MESSAGE,
                                            "datetime": next(commit_timestamp_gen),
                                            "include_in_changelog": bool(
                                                commit_type == "emoji"
                                            ),
                                        },
                                    ],
                                    commit_type,
                                    # this parser does not matter since the commit is common
                                    parser=cast(
                                        "CommitParser[ParseResult, ParserOptions]",
                                        pkg1_commit_parser,
                                    ),
                                    monorepo=True,
                                ),
                            },
                        },
                    ],
                },
            }
        ]

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg1_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg1_new_version.tag_format,
                        "version_py_file": monorepo_pkg1_version_py_file.relative_to(
                            monorepo_pkg1_dir
                        ),
                        "commit_message_format": pkg1_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg1_new_version,
                                    "dest_files": pkg1_changelog_file_definitions,
                                    "commit_ids": [cid_c1_initial],
                                },
                            },
                            change_to_pkg1_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg2_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg2_new_version.tag_format,
                        "version_py_file": monorepo_pkg2_version_py_file.relative_to(
                            monorepo_pkg2_dir
                        ),
                        "commit_message_format": pkg2_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg2_new_version,
                                    "dest_files": pkg2_changelog_file_definitions,
                                    "commit_ids": [cid_c1_initial],
                                },
                            },
                            change_to_pkg2_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        pkg1_fix_branch_commits: Sequence[CommitSpec] = [
            {
                "cid": "pkg1-fix-1-squashed",
                "conventional": "fix: no pkg scope but file in pkg 1 directory\n\nResolves: #123\n",
                "emoji": ":bug: no pkg scope but file in pkg 1 directory\n\nResolves: #123\n",
                "scipy": "MAINT: no pkg scope but file in pkg 1 directory\n\nResolves: #123\n",
                "datetime": next(commit_timestamp_gen),
            },
        ]

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": mr1_pkg1_fix_branch_name,
                            "start_branch": DEFAULT_BRANCH_NAME,
                        }
                    },
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "pre_actions": [change_to_pkg1_dir],
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    **commit,
                                    "include_in_changelog": False,
                                }
                                for commit in pkg1_fix_branch_commits
                            ],
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg1_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        # simulate separate work by another person at same time as the fix branch
        pkg2_feat_branch_commits: Sequence[CommitSpec] = [
            {
                "cid": "pkg2-feat-1-squashed",
                "conventional": "feat: no pkg scope but file in pkg 2 directory",
                "emoji": ":sparkles: no pkg scope but file in pkg 2 directory",
                "scipy": "ENH: no pkg scope but file in pkg 2 directory",
                "datetime": next(commit_timestamp_gen),
            },
            {
                "cid": "pkg2-feat-2-squashed",
                "conventional": "test(cli): add cli tests",
                "emoji": ":checkmark: add cli tests",
                "scipy": "TST: add cli tests",
                "datetime": next(commit_timestamp_gen),
            },
            {
                "cid": "pkg2-feat-3-squashed",
                "conventional": "docs(cli): add cli documentation",
                "emoji": ":memo: add cli documentation",
                "scipy": "DOC: add cli documentation",
                "datetime": next(commit_timestamp_gen),
            },
        ]

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": mr2_pkg2_feat_branch_name,
                            "start_branch": DEFAULT_BRANCH_NAME,
                        },
                    },
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "pre_actions": [change_to_pkg2_dir],
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    **commit,
                                    "include_in_changelog": False,
                                }
                                for commit in pkg2_feat_branch_commits
                            ],
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg2_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        pkg1_new_version = Version.parse(
            "1.0.1", tag_format=pkg1_new_version.tag_format
        )

        all_commit_types: list[CommitConvention] = ["conventional", "emoji", "scipy"]
        fix_branch_pr_number = next(pr_num_gen)
        fix_branch_squash_commit_spec: CommitSpec = {
            "cid": "mr1-pkg1-fix",
            **{  # type: ignore[typeddict-item]
                cmt_type: format_squash_commit_msg_github(
                    # Use the primary commit message as the PR title
                    pr_title=pkg1_fix_branch_commits[0][cmt_type],
                    pr_number=fix_branch_pr_number,
                    squashed_commits=[
                        cmt[commit_type] for cmt in pkg1_fix_branch_commits[1:]
                    ],
                )
                for cmt_type in all_commit_types
            },
            "datetime": next(commit_timestamp_gen),
            "include_in_changelog": True,
        }

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.GIT_SQUASH,
                    "details": {
                        "branch": mr1_pkg1_fix_branch_name,
                        "strategy_option": "theirs",
                        "commit_def": convert_commit_spec_to_commit_def(
                            fix_branch_squash_commit_spec,
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg1_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "config_file": monorepo_pkg1_pyproject_toml_file,
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg1_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg1_new_version.tag_format,
                        "version_py_file": monorepo_pkg1_version_py_file.relative_to(
                            monorepo_pkg1_dir
                        ),
                        "commit_message_format": pkg1_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg1_new_version,
                                    "dest_files": pkg1_changelog_file_definitions,
                                    "commit_ids": [
                                        f'{fix_branch_squash_commit_spec["cid"]}-{index + 1}'
                                        for index in range(len(pkg1_fix_branch_commits))
                                    ],
                                },
                            },
                            change_to_pkg1_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        feat_branch_pr_number = next(pr_num_gen)
        feat_branch_squash_commit_spec: CommitSpec = {
            "cid": "mr2-pkg2-feat",
            **{  # type: ignore[typeddict-item]
                cmt_type: format_squash_commit_msg_github(
                    # Use the primary commit message as the PR title
                    pr_title=pkg2_feat_branch_commits[0][cmt_type],
                    pr_number=feat_branch_pr_number,
                    squashed_commits=[
                        cmt[commit_type] for cmt in pkg2_feat_branch_commits[1:]
                    ],
                )
                for cmt_type in all_commit_types
            },
            "datetime": next(commit_timestamp_gen),
            "include_in_changelog": True,
        }

        pkg2_new_version = Version.parse(
            "1.1.0", tag_format=pkg2_new_version.tag_format
        )

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_SQUASH,
                    "details": {
                        "branch": mr2_pkg2_feat_branch_name,
                        "strategy_option": "theirs",
                        "commit_def": convert_commit_spec_to_commit_def(
                            feat_branch_squash_commit_spec,
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg2_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "config_file": monorepo_pkg2_pyproject_toml_file,
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg2_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg2_new_version.tag_format,
                        "version_py_file": monorepo_pkg2_version_py_file.relative_to(
                            monorepo_pkg2_dir
                        ),
                        "commit_message_format": pkg2_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg2_new_version,
                                    "dest_files": pkg2_changelog_file_definitions,
                                    "commit_ids": [
                                        f'{feat_branch_squash_commit_spec["cid"]}-{index + 1}'
                                        for index in range(
                                            len(pkg2_feat_branch_commits)
                                        )
                                    ],
                                },
                            },
                            change_to_pkg2_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        pkg2_fix_branch_commits: Sequence[CommitSpec] = [
            {
                "cid": "pkg2-fix-1-squashed",
                "conventional": "fix(pkg2-cli): file modified outside of pkg 2, identified by scope\n\nResolves: #123\n",
                "emoji": ":bug: (pkg2-cli) file modified outside of pkg 2, identified by scope\n\nResolves: #123\n",
                "scipy": "MAINT:pkg2-cli: file modified outside of pkg 2, identified by scope\n\nResolves: #123\n",
                "datetime": next(commit_timestamp_gen),
            },
        ]

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": mr3_pkg2_fix_branch_name,
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
                                    **commit,
                                    "include_in_changelog": False,
                                }
                                for commit in pkg2_fix_branch_commits
                            ],
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg2_commit_parser,
                            ),
                            monorepo=True,
                        ),
                    },
                },
            ]
        )

        pkg2_new_version = Version.parse(
            "1.1.1", tag_format=pkg2_new_version.tag_format
        )

        fix_branch_pr_number = next(pr_num_gen)
        fix_branch_squash_commit_spec = {
            "cid": "mr3-pkg2-fix",
            **{  # type: ignore[typeddict-item]
                cmt_type: format_squash_commit_msg_github(
                    # Use the primary commit message as the PR title
                    pr_title=pkg2_fix_branch_commits[0][cmt_type],
                    pr_number=fix_branch_pr_number,
                    squashed_commits=[
                        cmt[commit_type] for cmt in pkg2_fix_branch_commits[1:]
                    ],
                )
                for cmt_type in all_commit_types
            },
            "datetime": next(commit_timestamp_gen),
            "include_in_changelog": True,
        }

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.GIT_SQUASH,
                    "details": {
                        "branch": mr3_pkg2_fix_branch_name,
                        "strategy_option": "theirs",
                        "commit_def": convert_commit_spec_to_commit_def(
                            fix_branch_squash_commit_spec,
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg2_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "config_file": monorepo_pkg2_pyproject_toml_file,
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg2_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg2_new_version.tag_format,
                        "version_py_file": monorepo_pkg2_version_py_file.relative_to(
                            monorepo_pkg2_dir
                        ),
                        "commit_message_format": pkg2_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg2_new_version,
                                    "dest_files": pkg2_changelog_file_definitions,
                                    "commit_ids": [
                                        f'{fix_branch_squash_commit_spec["cid"]}-{index + 1}'
                                        for index in range(len(pkg2_fix_branch_commits))
                                    ],
                                },
                            },
                            change_to_pkg2_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        pkg1_feat_branch_commits: Sequence[CommitSpec] = [
            {
                "cid": "pkg1-feat-1-squashed",
                "conventional": "feat(pkg1): file modified outside of pkg 1, identified by scope",
                "emoji": ":sparkles: (pkg1) file modified outside of pkg 1, identified by scope",
                "scipy": "ENH:pkg1: file modified outside of pkg 1, identified by scope",
                "datetime": next(commit_timestamp_gen),
            },
            {
                "cid": "pkg1-docs-2-squashed",
                "conventional": "docs: pkg1 docs modified outside of pkg 1, identified by path filter",
                "emoji": ":book: pkg1 docs modified outside of pkg 1, identified by path filter",
                "scipy": "DOC: pkg1 docs modified outside of pkg 1, identified by path filter",
                "datetime": next(commit_timestamp_gen),
                "file_to_change": f"{monorepo_pkg1_docs_dir}/index.rst",
            },
        ]

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": mr4_pkg1_feat_branch_name,
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
                                    **commit,
                                    "include_in_changelog": False,
                                }
                                for commit in pkg1_feat_branch_commits
                            ],
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg1_commit_parser,
                            ),
                            monorepo=True,
                        ),
                    },
                },
            ]
        )

        feat_branch_pr_number = next(pr_num_gen)
        feat_branch_squash_commit_spec = {
            "cid": "mr4-pkg1-feat",
            **{  # type: ignore[typeddict-item]
                cmt_type: format_squash_commit_msg_github(
                    # Use the primary commit message as the PR title
                    pr_title=pkg1_feat_branch_commits[0][cmt_type],
                    pr_number=feat_branch_pr_number,
                    squashed_commits=[
                        cmt[commit_type] for cmt in pkg1_feat_branch_commits[1:]
                    ],
                )
                for cmt_type in all_commit_types
            },
            "datetime": next(commit_timestamp_gen),
            "include_in_changelog": True,
        }

        pkg1_new_version = Version.parse(
            "1.1.0", tag_format=pkg1_new_version.tag_format
        )

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.GIT_SQUASH,
                    "details": {
                        "branch": mr4_pkg1_feat_branch_name,
                        "strategy_option": "theirs",
                        "commit_def": convert_commit_spec_to_commit_def(
                            feat_branch_squash_commit_spec,
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                pkg1_commit_parser,
                            ),
                            monorepo=True,
                        ),
                        "config_file": monorepo_pkg1_pyproject_toml_file,
                    },
                },
                {
                    "action": RepoActionStep.RELEASE,
                    "details": {
                        "version": str(pkg1_new_version),
                        "datetime": next(commit_timestamp_gen),
                        "tag_format": pkg1_new_version.tag_format,
                        "version_py_file": monorepo_pkg1_version_py_file.relative_to(
                            monorepo_pkg1_dir
                        ),
                        "commit_message_format": pkg1_cmt_msg_format,
                        "pre_actions": [
                            {
                                "action": RepoActionStep.WRITE_CHANGELOGS,
                                "details": {
                                    "new_version": pkg1_new_version,
                                    "dest_files": pkg1_changelog_file_definitions,
                                    "commit_ids": [
                                        f'{feat_branch_squash_commit_spec["cid"]}-{index + 1}'
                                        for index in range(
                                            len(pkg1_feat_branch_commits)
                                        )
                                    ],
                                },
                            },
                            change_to_pkg1_dir,
                        ],
                        "post_actions": [change_to_example_project_dir],
                    },
                },
            ]
        )

        return repo_construction_steps

    return _get_repo_from_definition


@pytest.fixture(scope="session")
def build_monorepo_w_github_flow_w_default_release_channel(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_github_flow_monorepo_w_default_release_channel: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_github_flow_monorepo_w_default_release_channel: str,
) -> BuildSpecificRepoFn:
    def _build_specific_repo_type(
        repo_name: str, commit_type: CommitConvention, dest_dir: Path
    ) -> Sequence[RepoActions]:
        def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
            repo_construction_steps = (
                get_repo_definition_4_github_flow_monorepo_w_default_release_channel(
                    commit_type=commit_type,
                )
            )
            return build_repo_from_definition(cached_repo_path, repo_construction_steps)

        build_repo_or_copy_cache(
            repo_name=repo_name,
            build_spec_hash=build_spec_hash_4_github_flow_monorepo_w_default_release_channel,
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
def monorepo_w_github_flow_w_default_release_channel_conventional_commits(
    build_monorepo_w_github_flow_w_default_release_channel: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = (
        monorepo_w_github_flow_w_default_release_channel_conventional_commits.__name__
    )
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_monorepo_w_github_flow_w_default_release_channel(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }
