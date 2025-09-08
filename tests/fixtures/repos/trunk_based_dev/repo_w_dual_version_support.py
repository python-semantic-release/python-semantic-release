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
    from tests.fixtures.example_project import (
        ExProjectDir,
    )
    from tests.fixtures.git_repo import (
        BuildRepoFromDefinitionFn,
        BuildRepoOrCopyCacheFn,
        BuildSpecificRepoFn,
        BuiltRepoResult,
        CommitConvention,
        ConvertCommitSpecsToCommitDefsFn,
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        RepoActions,
        RepoActionWriteChangelogsDestFile,
        TomlSerializableTypes,
    )


MAINTENANCE_BRANCH_NAME = "v1.x"


@pytest.fixture(scope="session")
def deps_files_4_repo_w_dual_version_support(
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
def build_spec_hash_4_repo_w_dual_version_support(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_repo_w_dual_version_support: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_repo_w_dual_version_support)


@pytest.fixture(scope="session")
def get_repo_definition_4_trunk_only_repo_w_dual_version_support(
    convert_commit_specs_to_commit_defs: ConvertCommitSpecsToCommitDefsFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    stable_now_date: GetStableDateNowFn,
    default_conventional_parser: ConventionalCommitParser,
    default_emoji_parser: EmojiCommitParser,
    default_scipy_parser: ScipyCommitParser,
    default_tag_format_str: str,
) -> GetRepoDefinitionFn:
    """
    Builds a repository with trunk-only committing (no-branching) strategy with
    only official releases with latest and previous version support.
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
                        "tool.semantic_release.branches.latest": {
                            "match": r"^(main|master)$",
                            "prerelease": False,
                        },
                        "tool.semantic_release.branches.maintenance": {
                            "match": r"^v1\.x$",
                            "prerelease": False,
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
            "1.0.0", tag_format=tag_format_str or default_tag_format_str
        )

        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_c1_initial := "c1_initial_commit"),
                                    "conventional": INITIAL_COMMIT_MESSAGE,
                                    "emoji": INITIAL_COMMIT_MESSAGE,
                                    "scipy": INITIAL_COMMIT_MESSAGE,
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": bool(
                                        commit_type == "emoji"
                                    ),
                                },
                                {
                                    "cid": (cid_c2_feat := "c2-feat"),
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
                                    "commit_ids": [cid_c1_initial, cid_c2_feat],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a fix and officially release it
        new_version = Version.parse("1.0.1", tag_format=new_version.tag_format)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_c3_fix := "c3-fix"),
                                    "conventional": "fix: correct some text",
                                    "emoji": ":bug: correct some text",
                                    "scipy": "MAINT: correct some text",
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
                                    "commit_ids": [cid_c3_fix],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Make a breaking change and officially release it
        new_version = Version.parse("2.0.0", tag_format=new_version.tag_format)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {
                        "create_branch": {
                            "name": MAINTENANCE_BRANCH_NAME,
                            "start_branch": DEFAULT_BRANCH_NAME,
                        }
                    },
                },
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_c4_break_feat := "c4-break-feat"),
                                    "conventional": str.join(
                                        "\n\n",
                                        [
                                            "feat: add revolutionary feature",
                                            "BREAKING CHANGE: this is a breaking change",
                                        ],
                                    ),
                                    "emoji": str.join(
                                        "\n\n",
                                        [
                                            ":boom: add revolutionary feature",
                                            "This change is a breaking change",
                                        ],
                                    ),
                                    "scipy": str.join(
                                        "\n\n",
                                        [
                                            "API: add revolutionary feature",
                                            "This is a breaking change",
                                        ],
                                    ),
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
                                    "commit_ids": [cid_c4_break_feat],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Fix a critical bug in the previous version and officially release it
        new_version = Version.parse("1.0.2", tag_format=new_version.tag_format)
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": MAINTENANCE_BRANCH_NAME},
                },
                {
                    "action": RepoActionStep.MAKE_COMMITS,
                    "details": {
                        "commits": convert_commit_specs_to_commit_defs(
                            [
                                {
                                    "cid": (cid_c5_v1_fix := "c5-fix"),
                                    "conventional": "fix: correct critical bug\n\nResolves: #123\n",
                                    "emoji": ":bug: correct critical bug\n\nResolves: #123\n",
                                    "scipy": "MAINT: correct critical bug\n\nResolves: #123\n",
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
                                    "max_version": new_version,
                                    "dest_files": changelog_file_definitions,
                                    "commit_ids": [cid_c5_v1_fix],
                                },
                            },
                        ],
                    },
                },
            ]
        )

        # Return to the latest release variant
        repo_construction_steps.extend(
            [
                {
                    "action": RepoActionStep.GIT_CHECKOUT,
                    "details": {"branch": DEFAULT_BRANCH_NAME},
                },
                # TODO: return and make another release on the latest version
                # currently test variant of the changelog generator can't support this
            ]
        )

        return repo_construction_steps

    return _get_repo_from_definition


@pytest.fixture(scope="session")
def build_trunk_only_repo_w_dual_version_support(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_dual_version_support: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_w_dual_version_support: str,
) -> BuildSpecificRepoFn:
    def _build_specific_repo_type(
        repo_name: str, commit_type: CommitConvention, dest_dir: Path
    ) -> Sequence[RepoActions]:
        def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
            repo_construction_steps = (
                get_repo_definition_4_trunk_only_repo_w_dual_version_support(
                    commit_type=commit_type,
                )
            )
            return build_repo_from_definition(cached_repo_path, repo_construction_steps)

        build_repo_or_copy_cache(
            repo_name=repo_name,
            build_spec_hash=build_spec_hash_4_repo_w_dual_version_support,
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
def repo_w_trunk_only_dual_version_spt_conventional_commits(
    build_trunk_only_repo_w_dual_version_support: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_trunk_only_dual_version_spt_conventional_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_dual_version_support(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_trunk_only_dual_version_spt_emoji_commits(
    build_trunk_only_repo_w_dual_version_support: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_trunk_only_dual_version_spt_emoji_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_dual_version_support(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_trunk_only_dual_version_spt_scipy_commits(
    build_trunk_only_repo_w_dual_version_support: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_trunk_only_dual_version_spt_scipy_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_dual_version_support(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }
