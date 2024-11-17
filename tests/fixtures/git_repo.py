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

import tests.conftest
import tests.const
import tests.util
from tests.const import (
    COMMIT_MESSAGE,
    DEFAULT_BRANCH_NAME,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    NULL_HEX_SHA,
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

    from tests.conftest import (
        BuildRepoOrCopyCacheFn,
        GetMd5ForSetOfFilesFn,
        GetStableDateNowFn,
    )
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
        scope: str
        mr: str
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
            mask_initial_release: bool = False,
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
            mask_initial_release: bool = False,
        ) -> str: ...

    class FormatGitSquashCommitMsgFn(Protocol):
        def __call__(
            self,
            squashed_commits: list[CommitDef],
        ) -> str: ...

    class FormatGitHubSquashCommitMsgFn(Protocol):
        def __call__(
            self,
            pr_title: str,
            pr_number: int,
            squashed_commits: list[CommitDef | str],
        ) -> str: ...

    class FormatBitBucketSquashCommitMsgFn(Protocol):
        def __call__(
            self,
            branch_name: str,
            pr_title: str,
            pr_number: int,
            squashed_commits: list[CommitDef],
        ) -> str: ...

    class FormatGitMergeCommitMsgFn(Protocol):
        def __call__(self, branch_name: str, tgt_branch_name: str) -> str: ...

    class FormatGitHubMergeCommitMsgFn(Protocol):
        def __call__(self, pr_number: int, branch_name: str) -> str: ...

    class CreateMergeCommitFn(Protocol):
        def __call__(
            self,
            git_repo: Repo,
            branch_name: str,
            commit_def: CommitDef,
            fast_forward: bool = True,
        ) -> CommitDef: ...

    class CreateSquashMergeCommitFn(Protocol):
        def __call__(
            self,
            git_repo: Repo,
            branch_name: str,
            commit_def: CommitDef,
            strategy_option: str = "theirs",
        ) -> CommitDef: ...


@pytest.fixture(scope="session")
def deps_files_4_example_git_project(
    deps_files_4_example_project: list[Path],
) -> list[Path]:
    return [
        *deps_files_4_example_project,
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_4_example_git_project(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_example_git_project: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_example_git_project)


@pytest.fixture(scope="session")
def cached_example_git_project(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_example_git_project: str,
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

    def _build_repo(cached_repo_path: Path):
        if not cached_example_project.exists():
            raise RuntimeError("Unable to find cached project files")

        # make a copy of the example project as a base
        copy_dir_tree(cached_example_project, cached_repo_path)

        # initialize git repo (open and close)
        # NOTE: We don't want to hold the repo object open for the entire test session,
        # the implementation on Windows holds some file descriptors open until close is called.
        with Repo.init(cached_repo_path) as repo:
            # Without this the global config may set it to "master", we want consistency
            repo.git.branch("-M", DEFAULT_BRANCH_NAME)
            with repo.config_writer("repository") as config:
                config.set_value("user", "name", commit_author.name)
                config.set_value("user", "email", commit_author.email)
                config.set_value("commit", "gpgsign", False)
                config.set_value("tag", "gpgsign", False)

            repo.create_remote(name="origin", url=example_git_https_url)

            # make sure all base files are in index to enable initial commit
            repo.index.add(("*", ".gitignore"))

    # End of _build_repo()

    return build_repo_or_copy_cache(
        repo_name=cached_example_git_project.__name__.split("_", maxsplit=1)[1],
        build_spec_hash=build_spec_hash_4_example_git_project,
        build_repo_func=_build_repo,
    )


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
        if not (parsed_result := default_angular_parser.parse_message(msg)):
            return {
                "msg": msg,
                "type": "unknown",
                "desc": msg,
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
            }

        descriptions = list(parsed_result.descriptions)
        if parsed_result.linked_merge_request:
            descriptions[0] = str.join("(", descriptions[0].split("(")[:-1]).strip()

        return {
            "msg": msg,
            "type": parsed_result.type,
            "desc": str.join("\n\n", descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_angular_commit


@pytest.fixture(scope="session")
def get_commit_def_of_emoji_commit(
    default_emoji_parser: EmojiCommitParser,
) -> GetCommitDefFn:
    def _get_commit_def_of_emoji_commit(msg: str) -> CommitDef:
        if not (parsed_result := default_emoji_parser.parse_message(msg)):
            return {
                "msg": msg,
                "type": "unknown",
                "desc": msg,
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
            }

        descriptions = list(parsed_result.descriptions)
        if parsed_result.linked_merge_request:
            descriptions[0] = str.join("(", descriptions[0].split("(")[:-1]).strip()

        return {
            "msg": msg,
            "type": parsed_result.type,
            "desc": str.join("\n\n", descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_emoji_commit


@pytest.fixture(scope="session")
def get_commit_def_of_scipy_commit(
    default_scipy_parser: ScipyCommitParser,
) -> GetCommitDefFn:
    def _get_commit_def_of_scipy_commit(msg: str) -> CommitDef:
        if not (parsed_result := default_scipy_parser.parse_message(msg)):
            return {
                "msg": msg,
                "type": "unknown",
                "desc": msg,
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
            }

        descriptions = list(parsed_result.descriptions)
        if parsed_result.linked_merge_request:
            descriptions[0] = str.join("(", descriptions[0].split("(")[:-1]).strip()

        return {
            "msg": msg,
            "type": parsed_result.type,
            "desc": str.join("\n\n", descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
        }

    return _get_commit_def_of_scipy_commit


@pytest.fixture(scope="session")
def format_merge_commit_msg_git() -> FormatGitMergeCommitMsgFn:
    def _format_merge_commit_msg_git(branch_name: str, tgt_branch_name: str) -> str:
        return f"Merge branch '{branch_name}' into '{tgt_branch_name}'"

    return _format_merge_commit_msg_git


@pytest.fixture(scope="session")
def format_merge_commit_msg_github() -> FormatGitHubMergeCommitMsgFn:
    def _format_merge_commit_msg_git(pr_number: int, branch_name: str) -> str:
        return f"Merge pull request #{pr_number} from '{branch_name}'"

    return _format_merge_commit_msg_git


@pytest.fixture(scope="session")
def format_squash_commit_msg_git(commit_author: Actor) -> FormatGitSquashCommitMsgFn:
    def _format_squash_commit_msg_git(
        squashed_commits: list[CommitDef],
    ) -> str:
        return (
            str.join(
                "\n\n",
                [
                    "Squashed commit of the following:",
                    *[
                        str.join(
                            "\n",
                            [
                                f"commit {commit['sha']}",
                                f"Author: {commit_author.name} <{commit_author.email}>",
                                # TODO: get date from CommitDef object
                                "Date:   Day Mon DD HH:MM:SS YYYY +HHMM",
                                "",
                                *[f"    {line}" for line in commit["msg"].split("\n")],
                            ],
                        )
                        for commit in squashed_commits
                    ],
                ],
            )
            + "\n"
        )

    return _format_squash_commit_msg_git


@pytest.fixture(scope="session")
def format_squash_commit_msg_github() -> FormatGitHubSquashCommitMsgFn:
    def _format_squash_commit_msg_github(
        pr_title: str,
        pr_number: int,
        squashed_commits: list[CommitDef | str],
    ) -> str:
        sq_cmts: list[str] = (  # type: ignore
            squashed_commits
            if not isinstance(squashed_commits[0], dict)
            else [commit["msg"] for commit in squashed_commits]  # type: ignore
        )
        return (
            str.join(
                "\n\n",
                [
                    f"{pr_title} (#{pr_number})",
                    *[f"* {commit_str}" for commit_str in sq_cmts],
                ],
            )
            + "\n"
        )

    return _format_squash_commit_msg_github


@pytest.fixture(scope="session")
def format_squash_commit_msg_bitbucket() -> FormatBitBucketSquashCommitMsgFn:
    def _format_squash_commit_msg_bitbucket(
        branch_name: str,
        pr_title: str,
        pr_number: int,
        squashed_commits: list[CommitDef],
    ) -> str:
        # See #1085, for detail on BitBucket squash commit message format
        return (
            str.join(
                "\n\n",
                [
                    f"Merged in {branch_name}  (pull request #{pr_number})",
                    f"{pr_title}",
                    *[f"* {commit_str}" for commit_str in squashed_commits],
                ],
            )
            + "\n"
        )

    return _format_squash_commit_msg_bitbucket


@pytest.fixture(scope="session")
def create_merge_commit(stable_now_date: GetStableDateNowFn) -> CreateMergeCommitFn:
    def _create_merge_commit(
        git_repo: Repo,
        branch_name: str,
        commit_def: CommitDef,
        fast_forward: bool = True,
    ) -> CommitDef:
        with git_repo.git.custom_environment(
            GIT_AUTHOR_DATE=stable_now_date().isoformat(timespec="seconds"),
            GIT_COMMITTER_DATE=stable_now_date().isoformat(timespec="seconds"),
        ):
            git_repo.git.merge(
                branch_name,
                ff=fast_forward,
                no_ff=bool(not fast_forward),
                m=commit_def["msg"],
            )

        sleep(1)  # ensure commit timestamps are unique

        # return the commit definition with the sha & message updated
        return {
            **commit_def,
            "msg": str(git_repo.head.commit.message).strip(),
            "sha": git_repo.head.commit.hexsha,
        }

    return _create_merge_commit


@pytest.fixture(scope="session")
def create_squash_merge_commit(
    stable_now_date: GetStableDateNowFn,
) -> CreateSquashMergeCommitFn:
    def _create_squash_merge_commit(
        git_repo: Repo,
        branch_name: str,
        commit_def: CommitDef,
        strategy_option: str = "theirs",
    ) -> CommitDef:
        # merge --squash never commits on action, first it stages the changes
        git_repo.git.merge(
            branch_name,
            squash=True,
            strategy_option=strategy_option,
        )

        # commit the squashed changes
        git_repo.git.commit(
            m=commit_def["msg"],
            date=stable_now_date().isoformat(timespec="seconds"),
        )

        sleep(1)  # ensure commit timestamps are unique

        # return the commit definition with the sha & message updated
        return {
            **commit_def,
            "msg": str(git_repo.head.commit.message).strip(),
            "sha": git_repo.head.commit.hexsha,
        }

    return _create_squash_merge_commit


@pytest.fixture(scope="session")
def create_release_tagged_commit(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_tag_format_str: str,
    stable_now_date: GetStableDateNowFn,
) -> CreateReleaseFn:
    def _mimic_semantic_release_commit(
        git_repo: Repo,
        version: str,
        tag_format: str = default_tag_format_str,
    ) -> None:
        # stamp version into pyproject.toml
        update_pyproject_toml("tool.poetry.version", version)

        curr_datetime = stable_now_date()

        # commit --all files with version number commit message
        git_repo.git.commit(
            a=True,
            m=COMMIT_MESSAGE.format(version=version),
            date=curr_datetime.isoformat(timespec="seconds"),
        )

        # ensure commit timestamps are unique (adding one second even though a nanosecond has gone by)
        curr_datetime = curr_datetime.replace(second=(curr_datetime.second + 1) % 60)

        with git_repo.git.custom_environment(
            GIT_COMMITTER_DATE=curr_datetime.isoformat(timespec="seconds"),
        ):
            # tag commit with version number
            tag_str = tag_format.format(version=version)
            git_repo.git.tag(tag_str, m=tag_str)

        sleep(1)  # ensure commit timestamps are unique

    return _mimic_semantic_release_commit


@pytest.fixture(scope="session")
def commit_n_rtn_changelog_entry(
    stable_now_date: GetStableDateNowFn,
) -> CommitNReturnChangelogEntryFn:
    def _commit_n_rtn_changelog_entry(git_repo: Repo, commit: CommitDef) -> CommitDef:
        # make commit with --all files

        git_repo.git.commit(
            a=True,
            m=commit["msg"],
            date=stable_now_date().isoformat(timespec="seconds"),
        )

        # Capture the resulting commit message and sha
        return {
            **commit,
            "msg": str(git_repo.head.commit.message).strip(),
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
        mask_initial_release: bool = False,
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

            # Set whether or not the initial release should be masked
            update_pyproject_toml(
                "tool.semantic_release.changelog.default_templates.mask_initial_release",
                mask_initial_release,
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
    today_date_str: str,
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
            else f"## v{version} ({today_date_str})\n"
        ]

        for section_def in version_def["changelog_sections"]:
            # Create Markdown section heading
            version_entry.append(f"### {section_def['section']}\n")

            for i in section_def["i_commits"]:
                descriptions = version_def["commits"][i]["desc"].split("\n\n")

                # NOTE: We have to be wary of the line length as the default changelog
                # has a 100 character limit or otherwise our tests will fail because the
                # URLs and whitespace don't line up

                subject_line = "- {commit_scope}{commit_desc}".format(
                    commit_desc=descriptions[0].capitalize(),
                    commit_scope=(
                        f"**{version_def['commits'][i]['scope']}**: "
                        if version_def["commits"][i]["scope"]
                        else ""
                    ),
                )

                mr_link = (
                    ""
                    if not version_def["commits"][i]["mr"]
                    else "([{mr}]({mr_url}),".format(
                        mr=version_def["commits"][i]["mr"],
                        mr_url=hvcs.pull_request_url(version_def["commits"][i]["mr"]),
                    )
                )

                sha_link = "[`{short_sha}`]({commit_url}))".format(
                    short_sha=version_def["commits"][i]["sha"][:7],
                    commit_url=hvcs.commit_hash_url(version_def["commits"][i]["sha"]),
                )
                # Add opening parenthesis if no MR link
                sha_link = sha_link if mr_link else f"({sha_link}"

                # NOTE: we are assuming that the subject line is always less than 100 characters
                commit_cl_desc = f"{subject_line} {mr_link}".rstrip()
                if len(commit_cl_desc) > 100:
                    commit_cl_desc = f"{subject_line}\n  {mr_link}".rstrip()

                if len(f"{commit_cl_desc} {sha_link}") > 100:
                    commit_cl_desc = f"{commit_cl_desc}\n  {sha_link}\n"
                else:
                    commit_cl_desc = f"{commit_cl_desc} {sha_link}\n"

                if len(descriptions) > 1:
                    commit_cl_desc += (
                        "\n" + str.join("\n\n", [*descriptions[1:]]) + "\n"
                    )

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
                else f"v{version} ({today_date_str})"
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

                # NOTE: We have to be wary of the line length as the default changelog
                # has a 100 character limit or otherwise our tests will fail because the
                # URLs and whitespace don't line up

                subject_line = "* {commit_scope}{commit_desc}".format(
                    commit_desc=descriptions[0].capitalize(),
                    commit_scope=(
                        f"**{version_def['commits'][i]['scope']}**: "
                        if version_def["commits"][i]["scope"]
                        else ""
                    ),
                )

                mr_link = (
                    ""
                    if not version_def["commits"][i]["mr"]
                    else "(`{mr}`_,".format(
                        mr=version_def["commits"][i]["mr"],
                    )
                )

                sha_link = "`{short_sha}`_)".format(
                    short_sha=version_def["commits"][i]["sha"][:7],
                )
                # Add opening parenthesis if no MR link
                sha_link = sha_link if mr_link else f"({sha_link}"

                # NOTE: we are assuming that the subject line is always less than 100 characters
                commit_cl_desc = f"{subject_line} {mr_link}".rstrip()
                if len(commit_cl_desc) > 100:
                    commit_cl_desc = f"{subject_line}\n  {mr_link}".rstrip()

                if len(f"{commit_cl_desc} {sha_link}") > 100:
                    commit_cl_desc = f"{commit_cl_desc}\n  {sha_link}\n"
                else:
                    commit_cl_desc = f"{commit_cl_desc} {sha_link}\n"

                if len(descriptions) > 1:
                    commit_cl_desc += (
                        "\n" + str.join("\n\n", [*descriptions[1:]]) + "\n"
                    )

                # Add commits to section
                version_entry.append(commit_cl_desc)

            urls.extend(
                [
                    ".. _{mr}: {mr_url}".format(
                        mr=version_def["commits"][i]["mr"],
                        mr_url=hvcs.pull_request_url(version_def["commits"][i]["mr"]),
                    )
                    for i in section_def["i_commits"]
                    if version_def["commits"][i]["mr"]
                ]
            )
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

        if version_entry[-1] == "":
            version_entry.pop()

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

    def build_initial_version_entry(
        version: VersionStr,
        version_def: RepoVersionDef,
        output_format: ChangelogOutputFormat,
        hvcs: HvcsBase,
    ) -> str:
        if output_format == ChangelogOutputFormat.MARKDOWN:
            return str.join(
                "\n",
                [
                    f"## v{version} ({today_date_str})",
                    "",
                    "- Initial Release",
                    "",
                ],
            )
        if output_format == ChangelogOutputFormat.RESTRUCTURED_TEXT:
            title = f"v{version} ({today_date_str})"
            return str.join(
                "\n",
                [
                    f".. _changelog-v{version}:",
                    "",
                    title,
                    "=" * len(title),
                    "",
                    "* Initial Release",
                    "",
                ],
            )
        raise ValueError(f"Unknown output format: {output_format}")

    def _mimic_semantic_release_default_changelog(
        repo_definition: RepoDefinition,
        hvcs: HvcsBase,
        dest_file: Path | None = None,
        max_version: str | None = None,
        output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN,
        # TODO: Breaking v10, when default is toggled to true, also change this to True
        mask_initial_release: bool = False,
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

        for i, (version, version_def) in enumerate(repo_def.items()):
            # prepend entries to force reverse ordering
            entry = (
                build_initial_version_entry(version, version_def, output_format, hvcs)
                if i == 0 and mask_initial_release and version != "Unreleased"
                else build_version_entry(version, version_def, output_format, hvcs)
            )
            version_entries.insert(0, entry)

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
