from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import pytest
from git import Repo

from tests.const import COMMIT_MESSAGE
from tests.util import add_text_to_file, copy_dir_tree, temporary_working_directory

if TYPE_CHECKING:
    from pathlib import Path


    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import UpdatePyprojectTomlFn, UseParserFn
    from tests.fixtures.git_repo import (
        BaseRepoVersionDef,
        BuildRepoFn,
        CommitConvention,
        ExProjectGitRepoFn,
        GetRepoDefinitionFn,
        GetVersionStringsFn,
        RepoDefinition,
        VersionStr,
    )


@pytest.fixture(scope="session")
def get_commits_for_github_flow_repo_w_feature_release_channel() -> GetRepoDefinitionFn:
    base_definition: dict[str, BaseRepoVersionDef] = {
        "0.1.0": {
            "changelog_sections": {
                "angular": [{"section": "Unknown", "i_commits": [0]}],
                "emoji": [{"section": "Other", "i_commits": [0]}],
                "scipy": [{"section": "None", "i_commits": [0]}],
                "tag": [{"section": "Unknown", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "Initial commit",
                    "emoji": "Initial commit",
                    "scipy": "Initial commit",
                    "tag": "Initial commit",
                }
            ],
        },
        "0.1.1-rc.1": {
            "changelog_sections": {
                "angular": [{"section": "Fix", "i_commits": [0]}],
                "emoji": [{"section": ":bug:", "i_commits": [0]}],
                "scipy": [{"section": "Fix", "i_commits": [0]}],
                "tag": [{"section": "Fix", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "fix: add some more text",
                    "emoji": ":bug: add some more text",
                    "scipy": "MAINT: add some more text",
                    "tag": ":nut_and_bolt: add some more text",
                }
            ],
        },
        "0.2.0-rc.1": {
            "changelog_sections": {
                "angular": [{"section": "Feature", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
                "tag": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat: add some more text",
                    "emoji": ":sparkles: add some more text",
                    "scipy": "ENH: add some more text",
                    "tag": ":sparkles: add some more text",
                },
            ],
        },
        "0.2.0": {
            "changelog_sections": {
                "angular": [{"section": "Feature", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
                "tag": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat: add some more text",
                    "emoji": ":sparkles: add some more text",
                    "scipy": "ENH: add some more text",
                    "tag": ":sparkles: add some more text",
                },
            ],
        },
        "0.3.0-beta.1": {
            "changelog_sections": {
                "angular": [{"section": "Feature", "i_commits": [0]}],
                "emoji": [{"section": ":sparkles:", "i_commits": [0]}],
                "scipy": [{"section": "Feature", "i_commits": [0]}],
                "tag": [{"section": "Feature", "i_commits": [0]}],
            },
            "commits": [
                {
                    "angular": "feat: (feature) add some more text",
                    "emoji": ":sparkles: (feature) add some more text",
                    "scipy": "ENH: (feature) add some more text",
                    "tag": ":sparkles: (feature) add some more text",
                },
            ],
        },
    }

    def _get_commits_for_github_flow_repo_w_feature_release_channel(
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
                    message_variants[commit_type]
                    for message_variants in version_def["commits"]
                ],
            }

        return definition

    return _get_commits_for_github_flow_repo_w_feature_release_channel


@pytest.fixture(scope="session")
def get_versions_for_github_flow_repo_w_feature_release_channel(
    get_commits_for_github_flow_repo_w_feature_release_channel: GetRepoDefinitionFn,
) -> GetVersionStringsFn:
    def _get_versions_for_github_flow_repo_w_feature_release_channel() -> (
        list[VersionStr]
    ):
        return list(get_commits_for_github_flow_repo_w_feature_release_channel().keys())

    return _get_versions_for_github_flow_repo_w_feature_release_channel


@pytest.fixture(scope="session")
def build_github_flow_repo_w_feature_release_channel(
    get_commits_for_github_flow_repo_w_feature_release_channel: GetRepoDefinitionFn,
    cached_example_git_project: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    use_angular_parser: UseParserFn,
    use_emoji_parser: UseParserFn,
    use_scipy_parser: UseParserFn,
    use_tag_parser: UseParserFn,
    file_in_repo: str,
    default_tag_format_str: str,
) -> BuildRepoFn:
    def _build_github_flow_repo_w_feature_release_channel(
        git_repo_path: Path | str,
        commit_type: CommitConvention,
        tag_format_str: str | None = None,
    ) -> None:
        repo_definition = get_commits_for_github_flow_repo_w_feature_release_channel(
            commit_type
        )
        tag_format = tag_format_str or default_tag_format_str
        versions = list(repo_definition.keys())
        next_version = versions[0]

        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find cached files directory!")

        copy_dir_tree(cached_example_git_project, git_repo_path)

        with temporary_working_directory(git_repo_path), Repo(".") as git_repo:
            update_pyproject_toml(
                "tool.semantic_release.branches.beta-testing",
                {"match": "beta.*", "prerelease": True, "prerelease_token": "beta"},
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
                a=True,
                m=repo_definition[next_version][0],  # Initial commit
            )

            # Make initial feature release (v0.1.0)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[1]

            # Make a patch level commit
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a patch level release candidate (v0.1.1-rc.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[2]

            # Make a minor level commit
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a minor level release candidate (v0.2.0-rc.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[3]

            # Make a minor level commit
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a minor level release (v0.2.0)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

            # Increment version pointer
            next_version = versions[4]

            # Checkout beta_testing branch
            git_repo.create_head("beta_testing")
            git_repo.heads.beta_testing.checkout()

            # Make a feature level commit
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=repo_definition[next_version][0])

            # Make a feature level beta release (v0.3.0-beta.1)
            add_text_to_file(git_repo, file_in_repo)
            git_repo.git.commit(m=COMMIT_MESSAGE.format(version=next_version))
            tag_str = tag_format.format(version=next_version)
            git_repo.git.tag(tag_str, m=tag_str)

    return _build_github_flow_repo_w_feature_release_channel


# --------------------------------------------------------------------------- #
# Session-level fixtures to use to set up cached repositories on first use    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_feature_release_channel_angular_commits(
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_feature_release_channel_angular_commits.__name__
    )
    build_github_flow_repo_w_feature_release_channel(cached_repo_path, "angular")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_feature_release_channel_emoji_commits(
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__
    )
    build_github_flow_repo_w_feature_release_channel(cached_repo_path, "emoji")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_feature_release_channel_scipy_commits(
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__
    )
    build_github_flow_repo_w_feature_release_channel(cached_repo_path, "scipy")
    return teardown_cached_dir(cached_repo_path)


@pytest.fixture(scope="session")
def cached_repo_w_github_flow_w_feature_release_channel_tag_commits(
    build_github_flow_repo_w_feature_release_channel: BuildRepoFn,
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    cached_repo_path = cached_files_dir.joinpath(
        cached_repo_w_github_flow_w_feature_release_channel_tag_commits.__name__
    )
    build_github_flow_repo_w_feature_release_channel(cached_repo_path, "tag")
    return teardown_cached_dir(cached_repo_path)


# --------------------------------------------------------------------------- #
# Test-level fixtures to use to set up temporary test directory               #
# --------------------------------------------------------------------------- #


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_angular_commits(
    cached_repo_w_github_flow_w_feature_release_channel_angular_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_feature_release_channel_angular_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_feature_release_channel_angular_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_emoji_commits(
    cached_repo_w_github_flow_w_feature_release_channel_emoji_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_feature_release_channel_emoji_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_feature_release_channel_emoji_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_scipy_commits(
    cached_repo_w_github_flow_w_feature_release_channel_scipy_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_feature_release_channel_scipy_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_feature_release_channel_scipy_commits,
        example_project_dir,
    )
    return example_project_git_repo()


@pytest.fixture
def repo_w_github_flow_w_feature_release_channel_tag_commits(
    cached_repo_w_github_flow_w_feature_release_channel_tag_commits: Path,
    example_project_git_repo: ExProjectGitRepoFn,
    example_project_dir: Path,
    change_to_ex_proj_dir: None,
) -> Repo:
    if not cached_repo_w_github_flow_w_feature_release_channel_tag_commits.exists():
        raise RuntimeError("Unable to find cached repository!")
    copy_dir_tree(
        cached_repo_w_github_flow_w_feature_release_channel_tag_commits,
        example_project_dir,
    )
    return example_project_git_repo()
