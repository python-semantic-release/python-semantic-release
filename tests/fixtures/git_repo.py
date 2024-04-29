from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git import Actor, Repo

from tests.const import (
    COMMIT_MESSAGE,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    TODAY_DATE_STR,
)
from tests.util import (
    add_text_to_file,
    copy_dir_tree,
    shortuid,
    temporary_working_directory,
)

if TYPE_CHECKING:
    from typing import Generator, Literal, Protocol, TypedDict, Union

    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        UpdatePyprojectTomlFn,
        UseCustomParserFn,
        UseHvcsFn,
        UseParserFn,
    )

    CommitConvention = Literal["angular", "emoji", "scipy", "tag"] | str
    VersionStr = str
    CommitMsg = str
    ChangelogTypeHeading = str
    TomlSerializableTypes = Union[dict, set, list, tuple, int, float, bool, str]

    class RepoVersionDef(TypedDict):
        """
        A reduced common repo definition, that is specific to a type of commit conventions

        Used for builder functions that only need to know about a single commit convention type
        """

        changelog_sections: list[ChangelogTypeHeadingDef]
        commits: list[CommitMsg]

    class ChangelogTypeHeadingDef(TypedDict):
        section: ChangelogTypeHeading
        i_commits: list[int]
        """List of indexes values to match to the commits list in the RepoVersionDef"""

    class BaseRepoVersionDef(TypedDict):
        """A Common Repo definition for a get_commits_repo_*() fixture with all commit convention types"""

        changelog_sections: dict[CommitConvention, list[ChangelogTypeHeadingDef]]
        commits: list[dict[CommitConvention, CommitMsg]]

    class BuildRepoFn(Protocol):
        def __call__(
            self,
            dest_dir: Path | str,
            commit_type: CommitConvention = ...,
            hvcs_client_name: str = ...,
            hvcs_domain: str = ...,
            tag_format_str: str | None = None,
            extra_configs: dict[str, TomlSerializableTypes] | None = None,
        ) -> tuple[Path, HvcsBase]: ...

    class CommitNReturnChangelogEntryFn(Protocol):
        def __call__(self, git_repo: Repo, commit_msg: str, hvcs: HvcsBase) -> str: ...

    class SimulateChangeCommitsNReturnChangelogEntryFn(Protocol):
        def __call__(
            self, git_repo: Repo, commit_msgs: list[CommitMsg], hvcs: HvcsBase
        ) -> list[CommitMsg]: ...

    class CreateReleaseFn(Protocol):
        def __call__(
            self, git_repo: Repo, version: str, tag_format: str = ...
        ) -> None: ...

    class ExProjectGitRepoFn(Protocol):
        def __call__(self) -> Repo: ...

    class GetVersionStringsFn(Protocol):
        def __call__(self) -> list[VersionStr]: ...

    RepoDefinition = dict[VersionStr, RepoVersionDef]
    """
    A Type alias to define a repositories versions, commits, and changelog sections
    for a specific commit convention
    """

    class GetRepoDefinitionFn(Protocol):
        def __call__(
            self, commit_type: CommitConvention = "angular"
        ) -> RepoDefinition: ...

    class SimulateDefaultChangelogCreationFn(Protocol):
        def __call__(
            self,
            repo_definition: RepoDefinition,
            dest_file: Path | None = None,
        ) -> str: ...


@pytest.fixture(scope="session")
def commit_author():
    return Actor(name="semantic release testing", email="not_a_real@email.com")


@pytest.fixture(scope="session")
def default_tag_format_str() -> str:
    return "v{version}"


@pytest.fixture(scope="session")
def file_in_repo():
    return f"file-{shortuid()}.txt"


@pytest.fixture(scope="session")
def example_git_ssh_url():
    return f"git@{EXAMPLE_HVCS_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def example_git_https_url():
    return f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def create_release_tagged_commit(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
) -> CreateReleaseFn:
    def _mimic_semantic_release_commit(
        git_repo: Repo,
        version: str,
        tag_format: str = default_tag_format_str,
    ) -> None:
        # stamp version into pyproject.toml
        update_pyproject_toml("tool.poetry.version", version)

        # commit --all files with version number commit message
        git_repo.git.commit(a=True, m=COMMIT_MESSAGE.format(version=version))

        # tag commit with version number
        tag_str = tag_format.format(version=version)
        git_repo.git.tag(tag_str, m=tag_str)

    return _mimic_semantic_release_commit


@pytest.fixture(scope="session")
def commit_n_rtn_changelog_entry() -> CommitNReturnChangelogEntryFn:
    def _commit_n_rtn_changelog_entry(
        git_repo: Repo, commit_msg: str, hvcs: HvcsBase
    ) -> str:
        # make commit with --all files
        git_repo.git.commit(a=True, m=commit_msg)

        # log commit in changelog format after commit action
        commit_sha = git_repo.head.commit.hexsha
        return str.join(
            " ",
            [
                str(git_repo.head.commit.message).strip(),
                f"([`{commit_sha[:7]}`]({hvcs.commit_hash_url(commit_sha)}))",
            ],
        )

    return _commit_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def simulate_change_commits_n_rtn_changelog_entry(
    commit_n_rtn_changelog_entry: CommitNReturnChangelogEntryFn,
    file_in_repo: str,
) -> SimulateChangeCommitsNReturnChangelogEntryFn:
    def _simulate_change_commits_n_rtn_changelog_entry(
        git_repo: Repo, commit_msgs: list[str], hvcs: HvcsBase
    ) -> list[str]:
        changelog_entries = []
        for commit_msg in commit_msgs:
            add_text_to_file(git_repo, file_in_repo)
            changelog_entries.append(
                commit_n_rtn_changelog_entry(git_repo, commit_msg, hvcs)
            )
        return changelog_entries

    return _simulate_change_commits_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def cached_example_git_project(
    cached_files_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
    cached_example_project: Path,
    example_git_https_url: str,
    commit_author: Actor,
) -> Path:
    """
    Initializes an example project with git repo. DO NOT USE DIRECTLY.

    Use a `repo_*` fixture instead. This creates a default
    base repository, all settings can be changed later through from the
    example_project_git_repo fixture's return object and manual adjustment.
    """
    if not cached_example_project.exists():
        raise RuntimeError("Unable to find cached project files")

    cached_git_proj_path = (cached_files_dir / "example_git_project").resolve()

    # make a copy of the example project as a base
    copy_dir_tree(cached_example_project, cached_git_proj_path)

    # initialize git repo (open and close)
    # NOTE: We don't want to hold the repo object open for the entire test session,
    # the implementation on Windows holds some file descriptors open until close is called.
    with Repo.init(cached_git_proj_path) as repo:
        # Without this the global config may set it to "master", we want consistency
        repo.git.branch("-M", "main")
        with repo.config_writer("repository") as config:
            config.set_value("user", "name", commit_author.name)
            config.set_value("user", "email", commit_author.email)
            config.set_value("commit", "gpgsign", False)

        repo.create_remote(name="origin", url=example_git_https_url)

        # make sure all base files are in index to enable initial commit
        repo.index.add(("*", ".gitignore"))

        # TODO: initial commit!

    # trigger automatic cleanup of cache directory during teardown
    return teardown_cached_dir(cached_git_proj_path)


@pytest.fixture(scope="session")
def build_configured_base_repo(  # noqa: C901
    cached_example_git_project: Path,
    use_github_hvcs: UseHvcsFn,
    use_gitlab_hvcs: UseHvcsFn,
    use_gitea_hvcs: UseHvcsFn,
    use_bitbucket_hvcs: UseHvcsFn,
    use_angular_parser: UseParserFn,
    use_emoji_parser: UseParserFn,
    use_scipy_parser: UseParserFn,
    use_tag_parser: UseParserFn,
    use_custom_parser: UseCustomParserFn,
    example_git_https_url: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> BuildRepoFn:
    """
    This fixture is intended to simplify repo scenario building by initially
    creating the repo but also configuring semantic_release in the pyproject.toml
    for when the test executes semantic_release. It returns a function so that
    derivative fixtures can call this fixture with individual parameters.
    """

    def _build_configured_base_repo(  # noqa: C901
        dest_dir: Path | str,
        commit_type: str = "angular",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
    ) -> tuple[Path, HvcsBase]:
        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find cached git project files!")

        # Copy the cached git project the dest directory
        copy_dir_tree(cached_example_git_project, dest_dir)

        # Make sure we are in the dest directory
        with temporary_working_directory(dest_dir):
            # Set parser configuration
            if commit_type == "angular":
                use_angular_parser()
            elif commit_type == "emoji":
                use_emoji_parser()
            elif commit_type == "scipy":
                use_scipy_parser()
            elif commit_type == "tag":
                use_tag_parser()
            else:
                use_custom_parser(commit_type)

            # Set HVCS configuration
            if hvcs_client_name == "github":
                hvcs_class = use_github_hvcs(hvcs_domain)
            elif hvcs_client_name == "gitlab":
                hvcs_class = use_gitlab_hvcs(hvcs_domain)
            elif hvcs_client_name == "gitea":
                hvcs_class = use_gitea_hvcs(hvcs_domain)
            elif hvcs_client_name == "bitbucket":
                hvcs_class = use_bitbucket_hvcs(hvcs_domain)
            else:
                raise ValueError(f"Unknown HVCS client name: {hvcs_client_name}")

            # Create HVCS Client instance
            hvcs = hvcs_class(example_git_https_url, hvcs_domain=hvcs_domain)

            # Set tag format in configuration
            if tag_format_str is not None:
                update_pyproject_toml(
                    "tool.semantic_release.tag_format", tag_format_str
                )

            # Apply configurations to pyproject.toml
            if extra_configs is not None:
                for key, value in extra_configs.items():
                    update_pyproject_toml(key, value)

        return Path(dest_dir), hvcs

    return _build_configured_base_repo


@pytest.fixture(scope="session")
def simulate_default_changelog_creation() -> SimulateDefaultChangelogCreationFn:
    def build_version_entry(version: VersionStr, version_def: RepoVersionDef) -> str:
        version_entry = []
        if version == "Unreleased":
            version_entry.append(f"## {version}\n")
        else:
            version_entry.append(
                # TODO: artificial newline in front due to template when no Unreleased changes exist
                f"\n## v{version} ({TODAY_DATE_STR})\n"
            )

        for section_def in version_def["changelog_sections"]:
            version_entry.append(f"### {section_def['section']}\n")
            for i in section_def["i_commits"]:
                version_entry.append(f"* {version_def['commits'][i]}\n")

        return str.join("\n", version_entry)

    def _mimic_semantic_release_default_changelog(
        repo_definition: RepoDefinition,
        dest_file: Path | None = None,
    ) -> str:
        header = "# CHANGELOG"
        version_entries = []

        for version, version_def in repo_definition.items():
            # prepend entries to force reverse ordering
            version_entries.insert(0, build_version_entry(version, version_def))

        changelog_content = (
            str.join("\n" * 3, [header, str.join("\n", list(version_entries))]).rstrip()
            + "\n"
        )

        if dest_file is not None:
            dest_file.write_text(changelog_content)

        return changelog_content

    return _mimic_semantic_release_default_changelog


@pytest.fixture
def example_project_git_repo(
    example_project_dir: ExProjectDir,
) -> Generator[ExProjectGitRepoFn, None, None]:
    repos: list[Repo] = []

    # Must be a callable function to ensure files exist before repo is opened
    def _example_project_git_repo() -> Repo:
        if not example_project_dir.exists():
            raise RuntimeError("Unable to find example git project!")

        repo = Repo(example_project_dir)
        repos.append(repo)
        return repo

    try:
        yield _example_project_git_repo
    finally:
        for repo in repos:
            repo.close()
