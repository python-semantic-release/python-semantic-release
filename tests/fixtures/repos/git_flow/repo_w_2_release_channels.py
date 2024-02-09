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
    from tests.fixtures.example_project import UpdatePyprojectTomlFn, UseParserFn
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
def get_commits_for_git_flow_repo_with_2_release_channels() -> GetRepoDefinitionFn:
    base_definition: Mapping[VersionStr, list[dict[CommitConvention, CommitMsg]]] = {
        "0.1.0": [
            {
                "angular": "Initial commit",
                "emoji": "Initial commit",
                "scipy": "Initial commit",
                "tag": "Initial commit",
            }
        ],
        "0.1.1-rc.1": [
            {
                "angular": "fix: add some more text",
                "emoji": ":bug: add some more text",
                "scipy": "MAINT: add some more text",
                "tag": ":nut_and_bolt: add some more text",
            }
        ],
        "1.0.0-rc.1": [
            {
                "angular": "feat!: add some more text",
                "emoji": ":boom: add some more text",
                "scipy": "API: add some more text",
                "tag": ":sparkles: add some more text\n\nBREAKING CHANGE: add some more text",
            }
        ],
        "1.0.0": [
            {
                "angular": "feat: add some more text",
                "emoji": ":sparkles: add some more text",
                "scipy": "ENH: add some more text",
                "tag": ":sparkles: add some more text",
            },
        ],
        "1.1.0": [
            {
                "angular": "feat: (dev) add some more text",
                "emoji": ":sparkles: (dev) add some more text",
                "scipy": "ENH: (dev) add some more text",
                "tag": ":sparkles: (dev) add some more text",
            },
        ],
        "1.1.1": [
            {
                "angular": "fix: (dev) add some more text",
                "emoji": ":bug: (dev) add some more text",
                "scipy": "MAINT: (dev) add some more text",
                "tag": ":nut_and_bolt: (dev) add some more text",
            },
        ],
        "1.2.0-alpha.1": [
            {
                "angular": "feat: (feature) add some more text",
                "emoji": ":sparkles: (feature) add some more text",
                "scipy": "ENH: (feature) add some more text",
                "tag": ":sparkles: (feature) add some more text",
            },
        ],
        "1.2.0-alpha.2": [
            {
                "angular": "feat: (feature) add some more text",
                "emoji": ":sparkles: (feature) add some more text",
                "scipy": "ENH: (feature) add some more text",
                "tag": ":sparkles: (feature) add some more text",
            },
            {
                "angular": "fix: (feature) add some missing text",
                "emoji": ":bug: (feature) add some missing text",
                "scipy": "MAINT: (feature) add some missing text",
                "tag": ":nut_and_bolt: (feature) add some missing text",
            },
        ],
    }

    def _get_commits_for_git_flow_repo_with_2_release_channels(
        commit_type: CommitConvention = "angular",
    ) -> Mapping[VersionStr, list[CommitMsg]]:
        definition: Mapping[VersionStr, list[CommitMsg]] = {}
        for version, commits in base_definition.items():
            definition[version] = [
                message_dict[commit_type] for message_dict in commits
            ]
        return definition

    return _get_commits_for_git_flow_repo_with_2_release_channels


@pytest.fixture(scope="session")
def get_versions_for_git_flow_repo_with_2_release_channels(
    get_commits_for_git_flow_repo_with_2_release_channels: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_git_flow_repo_with_2_release_channels() -> list[VersionStr]:
        return list(get_commits_for_git_flow_repo_with_2_release_channels().keys())

    return _get_versions_for_git_flow_repo_with_2_release_channels


@pytest.fixture(scope="session")
def build_git_flow_repo_with_2_release_channels(
    get_commits_for_git_flow_repo_with_2_release_channels: GetRepoDefinitionFn,
    cached_example_git_project: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    use_angular_parser: UseParserFn,
    use_emoji_parser: UseParserFn,
    use_scipy_parser: UseParserFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    default_tag_format_str: str,
) -> BuildRepoFn:
    def _build_git_flow_repo_with_2_release_channels(
        git_repo_path: Path | str,
        commit_type: CommitConvention,
        tag_format_str: str | None = None,
    ) -> None:
        repo_definition = get_commits_for_git_flow_repo_with_2_release_channels(
            commit_type
        )
        tag_format = tag_format_str or default_tag_format_str
        versions = list(repo_definition.keys())
        next_version = versions[0]

        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find cached example git project!")

        copy_dir_tree(cached_example_git_project, git_repo_path)

        with temporary_working_directory(git_repo_path), Repo(".") as git_repo:
            update_pyproject_toml(
                "tool.semantic_release.branches.features",
                {
                    "match": "feat.*",
                    "prerelease": True,
                    "prerelease_token": "alpha",
                },
            )

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

            git_repo.git.commit(
                a=True, m=repo_definition[next_version][0]  # Initial commit
            )

            # Make initial feature release (v0.1.0)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[1]

            # Prepare for a prerelease
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a patch level release candidate (v0.1.1-rc.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[2]

            # Prepare for a major feature release
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a major feature release candidate (v1.0.0-rc.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[3]

            # Prepare for a major feature release
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a major feature release (v1.0.0)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[4]

            # Change to a dev branch
            git_repo.create_head("dev")
            git_repo.heads.dev.checkout()

            # Prepare for a minor feature release
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a minor feature release (v1.1.0)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[5]

            # Prepare for a patch level release
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a patch level release (v1.1.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[6]

            # Change to a feature branch
            git_repo.create_head("feature")
            git_repo.heads.feature.checkout()

            # Prepare for a prerelease
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make an alpha prerelease (v1.2.0-alpha.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[7]

            # Prepare for a 2nd prerelease with 2 commits
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][1])

            # Make a 2nd alpha prerelease (v1.2.0-alpha.2)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

    return _build_git_flow_repo_with_2_release_channels


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_2_release_channels_angular_commits(
    build_git_flow_repo_with_2_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_2_release_channels_angular_commits.__name__
    )
    build_git_flow_repo_with_2_release_channels(cached_repo_path, "angular")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_2_release_channels_emoji_commits(
    build_git_flow_repo_with_2_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_2_release_channels_emoji_commits.__name__
    )
    build_git_flow_repo_with_2_release_channels(cached_repo_path, "emoji")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_2_release_channels_scipy_commits(
    build_git_flow_repo_with_2_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_2_release_channels_scipy_commits.__name__
    )
    build_git_flow_repo_with_2_release_channels(cached_repo_path, "scipy")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_git_flow_n_2_release_channels_tag_commits(
    build_git_flow_repo_with_2_release_channels: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_git_flow_n_2_release_channels_tag_commits.__name__
    )
    build_git_flow_repo_with_2_release_channels(cached_repo_path, "tag")
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_with_git_flow_angular_commits(
    cached_repo_w_git_flow_n_2_release_channels_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_2_release_channels_angular_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_2_release_channels_angular_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_emoji_commits(
    cached_repo_w_git_flow_n_2_release_channels_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_2_release_channels_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_2_release_channels_emoji_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_scipy_commits(
    cached_repo_w_git_flow_n_2_release_channels_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_2_release_channels_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_2_release_channels_scipy_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_with_git_flow_tag_commits(
    cached_repo_w_git_flow_n_2_release_channels_tag_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_git_flow_n_2_release_channels_tag_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_git_flow_n_2_release_channels_tag_commits,
        example_project_dir,
    )
    return example_project_git_repo()
