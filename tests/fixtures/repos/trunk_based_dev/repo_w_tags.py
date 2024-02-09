from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from git import Repo

from tests.const import COMMIT_MESSAGE
from tests.util import add_text_to_file, copy_dir_tree, temporary_working_directory

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Mapping

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import UseParserFn
    from tests.fixtures.git_repo import (
        BuildRepoFn,
        CommitConvention,
        CommitMsg,
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        VersionStr,
    )


@pytest.fixture(scope="session")
def get_commits_for_trunk_only_repo_w_tags() -> GetRepoDefinitionFn:
    base_definition: Mapping[VersionStr, list[dict[CommitConvention, CommitMsg]]] = {
        "0.1.0": [{
            "angular": "Initial commit",
            "emoji": "Initial commit",
            "scipy": "Initial commit",
            "tag": "Initial commit",
        }],
        "0.1.1": [{
            "angular": "fix: add some more text",
            "emoji": ":bug: add some more text",
            "scipy": "MAINT: add some more text",
            "tag": ":nut_and_bolt: add some more text",
        }],
    }
    def _get_commits_for_trunk_only_repo_w_tags(
        commit_type: CommitConvention = "angular"
    ) -> Mapping[VersionStr, list[CommitMsg]]:
        definition: Mapping[VersionStr, list[CommitMsg]] = {}
        for version, commits in base_definition.items():
            definition[version] = [
                message_dict[commit_type] for message_dict in commits
            ]
        return definition

    return _get_commits_for_trunk_only_repo_w_tags


@pytest.fixture(scope="session")
def get_versions_for_trunk_only_repo_w_tags(
    get_commits_for_trunk_only_repo_w_tags: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_trunk_only_repo_w_tags() -> list[VersionStr]:
        return list(
            get_commits_for_trunk_only_repo_w_tags().keys()
        )

    return _get_versions_for_trunk_only_repo_w_tags


@pytest.fixture(scope="session")
def build_trunk_only_repo_w_tags(
    get_commits_for_trunk_only_repo_w_tags: GetRepoDefinitionFn,
    cached_example_git_project: Path,
    use_angular_parser: UseParserFn,
    use_emoji_parser: UseParserFn,
    use_scipy_parser: UseParserFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    default_tag_format_str: str,
) -> BuildRepoFn:
    def _build_trunk_only_repo_w_tags(
        git_repo_path: Path | str,
        commit_type: CommitConvention,
        tag_format_str: str | None = None,
    ) -> None:
        repo_definition = get_commits_for_trunk_only_repo_w_tags(commit_type)
        tag_format = tag_format_str or default_tag_format_str
        versions = list(repo_definition.keys())
        next_version = versions[0]

        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find example git project!")

        copy_dir_tree(cached_example_git_project, git_repo_path)

        with temporary_working_directory(git_repo_path), Repo(".") as git_repo:
            if commit_type == "angular":
                use_angular_parser()
            elif commit_type == "emoji":
                use_emoji_parser()
            elif commit_type == "scipy":
                use_scipy_parser()
            elif commit_type == "tag":
                use_tag_parser()
            else:
                raise ValueError(f"Unknown commit type: {commit_type}")

            git_repo.git.commit(a=True, m=repo_definition[next_version][0])  # Initial commit

            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            next_version = versions[1]

            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0]) # patch level message

            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

    return _build_trunk_only_repo_w_tags


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_with_single_branch_angular_commits(
    build_trunk_only_repo_w_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_single_branch_angular_commits.__name__
    )
    build_trunk_only_repo_w_tags(cached_repo_path, "angular")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_with_single_branch_emoji_commits(
    build_trunk_only_repo_w_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_single_branch_emoji_commits.__name__
    )
    build_trunk_only_repo_w_tags(cached_repo_path, "emoji")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_with_single_branch_scipy_commits(
    build_trunk_only_repo_w_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_single_branch_scipy_commits.__name__
    )
    build_trunk_only_repo_w_tags(cached_repo_path, "scipy")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_with_single_branch_tag_commits(
    build_trunk_only_repo_w_tags: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_with_single_branch_tag_commits.__name__
    )
    build_trunk_only_repo_w_tags(cached_repo_path, "tag")
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_with_single_branch_angular_commits(
    cached_repo_with_single_branch_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_single_branch_angular_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(cached_repo_with_single_branch_angular_commits, example_project_dir)
    return example_project_git_repo()


@pytest.fixture
def repo_with_single_branch_emoji_commits(
    cached_repo_with_single_branch_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_single_branch_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(cached_repo_with_single_branch_emoji_commits, example_project_dir)
    return example_project_git_repo()


@pytest.fixture
def repo_with_single_branch_scipy_commits(
    cached_repo_with_single_branch_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_single_branch_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(cached_repo_with_single_branch_scipy_commits, example_project_dir)
    return example_project_git_repo()


@pytest.fixture
def repo_with_single_branch_tag_commits(
    cached_repo_with_single_branch_tag_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_with_single_branch_tag_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(cached_repo_with_single_branch_tag_commits, example_project_dir)
    return example_project_git_repo()
