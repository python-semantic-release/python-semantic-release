from __future__ import annotations

from datetime import timedelta
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from semantic_release.cli.config import ChangelogOutputFormat

import tests.conftest
import tests.const
import tests.util
from tests.const import (
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
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        RepoActions,
        TomlSerializableTypes,
    )


@pytest.fixture(scope="session")
def deps_files_4_repo_w_no_tags(
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
def build_spec_hash_4_repo_w_no_tags(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_repo_w_no_tags: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_repo_w_no_tags)


@pytest.fixture(scope="session")
def get_repo_definition_4_trunk_only_repo_w_no_tags(
    convert_commit_specs_to_commit_defs: ConvertCommitSpecsToCommitDefsFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    stable_now_date: GetStableDateNowFn,
    default_conventional_parser: ConventionalCommitParser,
    default_emoji_parser: EmojiCommitParser,
    default_scipy_parser: ScipyCommitParser,
) -> GetRepoDefinitionFn:
    """
    Builds a repository with trunk-only committing (no-branching) strategy without
    any releases.
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

        repo_construction_steps: list[RepoActions] = []
        repo_construction_steps.extend(
            [
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
                            "tool.semantic_release.commit_parser_options.ignore_merge_commits": ignore_merge_commits,
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
                                    "cid": (cid_c2_feat1 := "c2-feat1"),
                                    "conventional": "feat: add new feature",
                                    "emoji": ":sparkles: add new feature",
                                    "scipy": "ENH: add new feature",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                                {
                                    "cid": (cid_c3_fix1 := "c3-fix1"),
                                    "conventional": "fix: correct some text",
                                    "emoji": ":bug: correct some text",
                                    "scipy": "MAINT: correct some text",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                                {
                                    "cid": (cid_c4_fix2 := "c4-fix2"),
                                    "conventional": "fix: correct more text\n\nCloses: #123",
                                    "emoji": ":bug: correct more text\n\nCloses: #123",
                                    "scipy": "MAINT: correct more text\n\nCloses: #123",
                                    "datetime": next(commit_timestamp_gen),
                                    "include_in_changelog": True,
                                },
                            ],
                            commit_type,
                            parser=cast(
                                "CommitParser[ParseResult, ParserOptions]",
                                parser_classes[commit_type],
                            ),
                        ),
                    },
                },
                {
                    "action": RepoActionStep.WRITE_CHANGELOGS,
                    "details": {
                        "new_version": "Unreleased",
                        "dest_files": [
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
                        ],
                        "commit_ids": [
                            cid_c1_initial,
                            cid_c2_feat1,
                            cid_c3_fix1,
                            cid_c4_fix2,
                        ],
                    },
                },
            ]
        )

        return repo_construction_steps

    return _get_repo_from_definition


@pytest.fixture(scope="session")
def build_trunk_only_repo_w_no_tags(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_w_no_tags: str,
) -> BuildSpecificRepoFn:
    def _build_specific_repo_type(
        repo_name: str, commit_type: CommitConvention, dest_dir: Path
    ) -> Sequence[RepoActions]:
        def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
            repo_construction_steps = get_repo_definition_4_trunk_only_repo_w_no_tags(
                commit_type=commit_type,
            )
            return build_repo_from_definition(cached_repo_path, repo_construction_steps)

        build_repo_or_copy_cache(
            repo_name=repo_name,
            build_spec_hash=build_spec_hash_4_repo_w_no_tags,
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
def repo_w_no_tags_conventional_commits_using_tag_format(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_w_no_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    """
    Replicates repo with no tags, but with a tag format X{version}

    Follows tag format defined in python-semantic-release#1137
    """
    repo_name = repo_w_no_tags_conventional_commits_using_tag_format.__name__
    commit_type: CommitConvention = (
        repo_name.split("_commits", maxsplit=1)[0].split("_")[-1]  # type: ignore[assignment]
    )

    def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
        repo_construction_steps = get_repo_definition_4_trunk_only_repo_w_no_tags(
            commit_type=commit_type,
            tag_format_str="X{version}",
        )
        return build_repo_from_definition(cached_repo_path, repo_construction_steps)

    build_repo_or_copy_cache(
        repo_name=repo_name,
        build_spec_hash=build_spec_hash_4_repo_w_no_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    if not (cached_repo_data := get_cached_repo_data(proj_dirname=repo_name)):
        raise ValueError("Failed to retrieve repo data from cache")

    return {
        "definition": cached_repo_data["build_definition"],
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_no_tags_conventional_commits_w_zero_version(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_w_no_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    """Replicates repo with no tags, but with allow_zero_version=True"""
    repo_name = repo_w_no_tags_conventional_commits_w_zero_version.__name__
    commit_type: CommitConvention = (
        repo_name.split("_commits", maxsplit=1)[0].split("_")[-1]  # type: ignore[assignment]
    )

    def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
        repo_construction_steps = get_repo_definition_4_trunk_only_repo_w_no_tags(
            commit_type=commit_type,
            extra_configs={
                "tool.semantic_release.allow_zero_version": True,
            },
        )
        return build_repo_from_definition(cached_repo_path, repo_construction_steps)

    build_repo_or_copy_cache(
        repo_name=repo_name,
        build_spec_hash=build_spec_hash_4_repo_w_no_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    if not (cached_repo_data := get_cached_repo_data(proj_dirname=repo_name)):
        raise ValueError("Failed to retrieve repo data from cache")

    return {
        "definition": cached_repo_data["build_definition"],
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_no_tags_conventional_commits_unmasked_initial_release(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_no_tags: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_w_no_tags: str,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    """Replicates repo with no tags, but with mask_initial_release=False"""
    repo_name = repo_w_no_tags_conventional_commits_unmasked_initial_release.__name__
    commit_type: CommitConvention = (
        repo_name.split("_commits", maxsplit=1)[0].split("_")[-1]  # type: ignore[assignment]
    )

    def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
        repo_construction_steps = get_repo_definition_4_trunk_only_repo_w_no_tags(
            commit_type=commit_type,
            extra_configs={
                "tool.semantic_release.changelog.default_templates.mask_initial_release": False,
            },
        )
        return build_repo_from_definition(cached_repo_path, repo_construction_steps)

    build_repo_or_copy_cache(
        repo_name=repo_name,
        build_spec_hash=build_spec_hash_4_repo_w_no_tags,
        build_repo_func=_build_repo,
        dest_dir=example_project_dir,
    )

    if not (cached_repo_data := get_cached_repo_data(proj_dirname=repo_name)):
        raise ValueError("Failed to retrieve repo data from cache")

    return {
        "definition": cached_repo_data["build_definition"],
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_no_tags_conventional_commits(
    build_trunk_only_repo_w_no_tags: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_no_tags_conventional_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_no_tags(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_no_tags_emoji_commits(
    build_trunk_only_repo_w_no_tags: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_no_tags_emoji_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_no_tags(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }


@pytest.fixture
def repo_w_no_tags_scipy_commits(
    build_trunk_only_repo_w_no_tags: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_no_tags_scipy_commits.__name__
    commit_type: CommitConvention = repo_name.split("_")[-2]  # type: ignore[assignment]

    return {
        "definition": build_trunk_only_repo_w_no_tags(
            repo_name=repo_name,
            commit_type=commit_type,
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }
