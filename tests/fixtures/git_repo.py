from __future__ import annotations

import sys
from copy import deepcopy
from functools import reduce
from pathlib import Path
from textwrap import dedent
from time import sleep
from typing import TYPE_CHECKING

import pytest
from git import Actor, Repo

from semantic_release.cli.config import ChangelogOutputFormat

from tests.const import (
    COMMIT_MESSAGE,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    NULL_HEX_SHA,
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

    from semantic_release.commit_parser.angular import AngularCommitParser
    from semantic_release.commit_parser.emoji import EmojiCommitParser
    from semantic_release.commit_parser.scipy import ScipyCommitParser
    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        GetWheelFileFn,
        UpdatePyprojectTomlFn,
        UseCustomParserFn,
        UseHvcsFn,
        UseParserFn,
    )

    CommitConvention = Literal["angular", "emoji", "scipy"]
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
        commits: list[CommitDef]

    class BaseAccumulatorVersionReduction(TypedDict):
        limit_value: str
        limit_found: bool
        repo_def: dict[VersionStr, RepoVersionDef]

    class ChangelogTypeHeadingDef(TypedDict):
        section: ChangelogTypeHeading
        i_commits: list[int]
        """List of indexes values to match to the commits list in the RepoVersionDef"""

    class CommitDef(TypedDict):
        msg: CommitMsg
        type: str
        desc: str
        sha: str

    class BaseRepoVersionDef(TypedDict):
        """A Common Repo definition for a get_commits_repo_*() fixture with all commit convention types"""

        changelog_sections: dict[CommitConvention, list[ChangelogTypeHeadingDef]]
        commits: list[dict[CommitConvention, str]]

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
        def __call__(self, git_repo: Repo, commit: CommitDef) -> CommitDef: ...

    class SimulateChangeCommitsNReturnChangelogEntryFn(Protocol):
        def __call__(
            self, git_repo: Repo, commit_msgs: list[CommitDef]
        ) -> list[CommitDef]: ...

    class CreateReleaseFn(Protocol):
        def __call__(
            self, git_repo: Repo, version: str, tag_format: str = ...
        ) -> None: ...

    class ExProjectGitRepoFn(Protocol):
        def __call__(self) -> Repo: ...

    class ExtractRepoDefinitionFn(Protocol):
        def __call__(
            self,
            base_repo_def: dict[str, BaseRepoVersionDef],
            commit_type: CommitConvention,
        ) -> RepoDefinition: ...

    class GetCommitDefFn(Protocol):
        def __call__(self, msg: str) -> CommitDef: ...

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
            hvcs: HvcsBase,
            dest_file: Path | None = None,
            max_version: str | None = None,
            output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN,
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
def extract_commit_convention_from_base_repo_def(
    get_commit_def_of_angular_commit: GetCommitDefFn,
    get_commit_def_of_emoji_commit: GetCommitDefFn,
    get_commit_def_of_scipy_commit: GetCommitDefFn,
) -> ExtractRepoDefinitionFn:
    message_parsers: dict[CommitConvention, GetCommitDefFn] = {
        "angular": get_commit_def_of_angular_commit,
        "emoji": get_commit_def_of_emoji_commit,
        "scipy": get_commit_def_of_scipy_commit,
    }

    def _extract_commit_convention_from_base_repo_def(
        base_repo_def: dict[str, BaseRepoVersionDef],
        commit_type: CommitConvention,
    ) -> RepoDefinition:
        definition: RepoDefinition = {}
        parse_msg_fn = message_parsers[commit_type]

        for version, version_def in base_repo_def.items():
            definition[version] = {
                # Extract the correct changelog section header for the commit type
                "changelog_sections": deepcopy(
                    version_def["changelog_sections"][commit_type]
                ),
                "commits": [
                    # Extract the correct commit message for the commit type
                    parse_msg_fn(message_variants[commit_type])
                    for message_variants in version_def["commits"]
                ],
            }

        return definition

    return _extract_commit_convention_from_base_repo_def


@pytest.fixture(scope="session")
def get_commit_def_of_angular_commit(
    default_angular_parser: AngularCommitParser,
) -> GetCommitDefFn:
    def _get_commit_def_of_angular_commit(msg: str) -> CommitDef:
        parsed_result = default_angular_parser.parse_message(msg)
        return {
            "msg": msg,
            "type": "unknown" if parsed_result is None else parsed_result.type,
            "desc": (
                msg
                if parsed_result is None
                else str.join("\n\n", parsed_result.descriptions)
            ),
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_angular_commit


@pytest.fixture(scope="session")
def get_commit_def_of_emoji_commit(
    default_emoji_parser: EmojiCommitParser,
) -> GetCommitDefFn:
    def _get_commit_def_of_emoji_commit(msg: str) -> CommitDef:
        parsed_result = default_emoji_parser.parse_message(msg)
        return {
            "msg": msg,
            "type": "unknown" if parsed_result is None else parsed_result.type,
            "desc": (
                msg
                if parsed_result is None
                else str.join("\n\n", parsed_result.descriptions)
            ),
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_emoji_commit


@pytest.fixture(scope="session")
def get_commit_def_of_scipy_commit(
    default_scipy_parser: ScipyCommitParser,
) -> GetCommitDefFn:
    def _get_commit_def_of_scipy_commit(msg: str) -> CommitDef:
        parsed_result = default_scipy_parser.parse_message(msg)
        return {
            "msg": msg,
            "type": "unknown" if parsed_result is None else parsed_result.type,
            "desc": (
                msg
                if parsed_result is None
                else str.join("\n\n", parsed_result.descriptions)
            ),
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_scipy_commit


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

        sleep(1)  # ensure commit timestamps are unique

        # tag commit with version number
        tag_str = tag_format.format(version=version)
        git_repo.git.tag(tag_str, m=tag_str)

        sleep(1)  # ensure commit timestamps are unique

    return _mimic_semantic_release_commit


@pytest.fixture(scope="session")
def commit_n_rtn_changelog_entry() -> CommitNReturnChangelogEntryFn:
    def _commit_n_rtn_changelog_entry(git_repo: Repo, commit: CommitDef) -> CommitDef:
        # make commit with --all files
        git_repo.git.commit(a=True, m=commit["msg"])

        # Capture the resulting commit message and sha
        return {
            "msg": str(git_repo.head.commit.message).strip(),
            "type": commit["type"],
            "desc": commit["desc"],
            "sha": git_repo.head.commit.hexsha,
        }

    return _commit_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def simulate_change_commits_n_rtn_changelog_entry(
    commit_n_rtn_changelog_entry: CommitNReturnChangelogEntryFn,
    file_in_repo: str,
) -> SimulateChangeCommitsNReturnChangelogEntryFn:
    def _simulate_change_commits_n_rtn_changelog_entry(
        git_repo: Repo, commit_msgs: list[CommitDef]
    ) -> list[CommitDef]:
        changelog_entries = []
        for commit_msg in commit_msgs:
            add_text_to_file(git_repo, file_in_repo)
            changelog_entries.append(commit_n_rtn_changelog_entry(git_repo, commit_msg))
            sleep(1)  # ensure commit timestamps are unique
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
            config.set_value("tag", "gpgsign", False)

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
    use_custom_parser: UseCustomParserFn,
    example_git_https_url: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    get_wheel_file: GetWheelFileFn,
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

            # Set the build_command to create a wheel file (using the build_command_env version variable)
            build_result_file = (
                get_wheel_file("$NEW_VERSION")
                if sys.platform != "win32"
                else get_wheel_file("$Env:NEW_VERSION")
            )
            update_pyproject_toml(
                # NOTE: must work in both bash and Powershell
                "tool.semantic_release.build_command",
                dedent(
                    f"""\
                    mkdir -p "{build_result_file.parent}"
                    touch "{build_result_file}"
                    """
                    if sys.platform != "win32"
                    else f"""\
                    mkdir {build_result_file.parent} > $null
                    New-Item -ItemType file -Path "{build_result_file}" -Force | Select-Object OriginalPath
                    """
                ),
            )

            # Apply configurations to pyproject.toml
            if extra_configs is not None:
                for key, value in extra_configs.items():
                    update_pyproject_toml(key, value)

        return Path(dest_dir), hvcs

    return _build_configured_base_repo


@pytest.fixture(scope="session")
def simulate_default_changelog_creation(  # noqa: C901
    default_md_changelog_insertion_flag: str,
    default_rst_changelog_insertion_flag: str,
) -> SimulateDefaultChangelogCreationFn:
    def reduce_repo_def(
        acc: BaseAccumulatorVersionReduction, ver_2_def: tuple[str, RepoVersionDef]
    ) -> BaseAccumulatorVersionReduction:
        if acc["limit_found"]:
            return acc

        if ver_2_def[0] == acc["limit_value"]:
            acc["limit_found"] = True

        acc["repo_def"][ver_2_def[0]] = ver_2_def[1]
        return acc

    def build_version_entry_markdown(
        version: VersionStr,
        version_def: RepoVersionDef,
        hvcs: HvcsBase,
    ) -> str:
        version_entry = [
            f"## {version}\n"
            if version == "Unreleased"
            else f"## v{version} ({TODAY_DATE_STR})\n"
        ]

        for section_def in version_def["changelog_sections"]:
            # Create Markdown section heading
            version_entry.append(f"### {section_def['section']}\n")

            for i in section_def["i_commits"]:
                descriptions = version_def["commits"][i]["desc"].split("\n\n")
                # NOTE: we assume url is always too long for the line so put it on the next line
                # to meet the autofit 100 character limit
                commit_cl_desc = "- {commit_desc}\n  ([`{short_sha}`]({commit_url}))\n".format(
                    commit_desc=descriptions[0].capitalize(),
                    short_sha=version_def["commits"][i]["sha"][:7],
                    commit_url=hvcs.commit_hash_url(
                        version_def["commits"][i]["sha"]
                    ),
                )

                if len(descriptions) > 1:
                    commit_cl_desc += str.join("\n", ["", *descriptions[1:], ""])

                # Add commits to section
                version_entry.append(commit_cl_desc)

        return str.join("\n", version_entry)

    def build_version_entry_restructured_text(
        version: VersionStr,
        version_def: RepoVersionDef,
        hvcs: HvcsBase,
    ) -> str:
        version_entry = [
            (
                ".. _changelog-unreleased:"
                if version == "Unreleased"
                else f".. _changelog-v{version}:"
            ),
            "",
            (
                f"{version}"
                if version == "Unreleased"
                else f"v{version} ({TODAY_DATE_STR})"
            ),
        ]
        version_entry.append("=" * len(version_entry[-1]))
        version_entry.append("")  # Add newline

        urls = []
        for section_def in version_def["changelog_sections"]:
            # Create RestructuredText section heading
            version_entry.append(f"{section_def['section']}")
            version_entry.append("-" * (len(version_entry[-1])) + "\n")

            for i in section_def["i_commits"]:
                descriptions = version_def["commits"][i]["desc"].split("\n\n")
                commit_cl_desc = "* {commit_desc} (`{short_sha}`_)\n".format(
                    commit_desc=descriptions[0].capitalize(),
                    short_sha=version_def["commits"][i]["sha"][:7],
                )

                if len(descriptions) > 1:
                    commit_cl_desc += str.join("\n", ["", *descriptions[1:], ""])

                # Add commits to section
                version_entry.append(commit_cl_desc)

            urls.extend(
                [
                    ".. _{short_sha}: {commit_url}".format(
                        short_sha=version_def["commits"][i]["sha"][:7],
                        commit_url=hvcs.commit_hash_url(
                            version_def["commits"][i]["sha"]
                        ),
                    )
                    for i in section_def["i_commits"]
                ]
            )

        # Add commit URLs to the end of the version entry
        version_entry.extend(sorted(urls))

        return str.join("\n", version_entry) + "\n"

    def build_version_entry(
        version: VersionStr,
        version_def: RepoVersionDef,
        output_format: ChangelogOutputFormat,
        hvcs: HvcsBase,
    ) -> str:
        output_functions = {
            ChangelogOutputFormat.MARKDOWN: build_version_entry_markdown,
            ChangelogOutputFormat.RESTRUCTURED_TEXT: build_version_entry_restructured_text,
        }
        return output_functions[output_format](version, version_def, hvcs)

    def _mimic_semantic_release_default_changelog(
        repo_definition: RepoDefinition,
        hvcs: HvcsBase,
        dest_file: Path | None = None,
        max_version: str | None = None,
        output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN,
    ) -> str:
        if output_format == ChangelogOutputFormat.MARKDOWN:
            header = dedent(
                f"""\
                # CHANGELOG

                {default_md_changelog_insertion_flag}
                """
            ).rstrip()
        elif output_format == ChangelogOutputFormat.RESTRUCTURED_TEXT:
            universal_newline_insertion_flag = (
                default_rst_changelog_insertion_flag.replace("\r", "")
            )
            header = str.join(
                "\n\n",
                [
                    dedent(
                        """\
                        .. _changelog:

                        =========
                        CHANGELOG
                        =========
                        """
                    ).rstrip(),
                    universal_newline_insertion_flag,
                ],
            )
        else:
            raise ValueError(f"Unknown output format: {output_format}")

        version_entries = []

        repo_def = (
            repo_definition
            if max_version is None
            else reduce(
                reduce_repo_def,
                repo_definition.items(),
                {
                    "limit_value": max_version,
                    "limit_found": False,
                    "repo_def": {},
                },
            )["repo_def"]
        )

        for version, version_def in repo_def.items():
            # prepend entries to force reverse ordering
            version_entries.insert(
                0, build_version_entry(version, version_def, output_format, hvcs)
            )

        changelog_content = (
            str.join(
                "\n" * 2, [header, str.join("\n" * 2, list(version_entries))]
            ).rstrip()
            + "\n"
        )

        if dest_file is not None:
            # Converts uninversal newlines to the OS-specific upon write
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
