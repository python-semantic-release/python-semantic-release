from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

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
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        RepoActions,
        TomlSerializableTypes,
    )


@pytest.fixture(scope="session")
def deps_files_4_repo_initial_commit(
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
def build_spec_hash_4_repo_initial_commit(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_repo_initial_commit: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_repo_initial_commit)


@pytest.fixture(scope="session")
def get_repo_definition_4_repo_w_initial_commit(
    convert_commit_specs_to_commit_defs: ConvertCommitSpecsToCommitDefsFn,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    stable_now_date: GetStableDateNowFn,
) -> GetRepoDefinitionFn:
    def _get_repo_from_defintion(
        commit_type: CommitConvention,
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = False,
    ) -> Sequence[RepoActions]:
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
                                    "conventional": INITIAL_COMMIT_MESSAGE,
                                    "emoji": INITIAL_COMMIT_MESSAGE,
                                    "scipy": INITIAL_COMMIT_MESSAGE,
                                    "datetime": stable_now_date().isoformat(
                                        timespec="seconds"
                                    ),
                                    "include_in_changelog": bool(
                                        commit_type == "emoji"
                                    ),
                                },
                            ],
                            commit_type,
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
                            },
                            {
                                "path": changelog_rst_file,
                                "format": ChangelogOutputFormat.RESTRUCTURED_TEXT,
                            },
                        ],
                    },
                },
            ]
        )

        return repo_construction_steps

    return _get_repo_from_defintion


@pytest.fixture(scope="session")
def build_repo_w_initial_commit(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_repo_w_initial_commit: GetRepoDefinitionFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_repo_initial_commit: str,
) -> BuildSpecificRepoFn:
    def _build_specific_repo_type(
        repo_name: str, commit_type: CommitConvention, dest_dir: Path
    ) -> Sequence[RepoActions]:
        def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
            repo_construction_steps = get_repo_definition_4_repo_w_initial_commit(
                commit_type=commit_type,
            )
            return build_repo_from_definition(cached_repo_path, repo_construction_steps)

        build_repo_or_copy_cache(
            repo_name=repo_name,
            build_spec_hash=build_spec_hash_4_repo_initial_commit,
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
def repo_w_initial_commit(
    build_repo_w_initial_commit: BuildSpecificRepoFn,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
) -> BuiltRepoResult:
    repo_name = repo_w_initial_commit.__name__

    return {
        "definition": build_repo_w_initial_commit(
            repo_name=repo_name,
            commit_type="conventional",  # not used but required
            dest_dir=example_project_dir,
        ),
        "repo": example_project_git_repo(),
    }
