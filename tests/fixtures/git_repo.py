from __future__ import annotations

import os
import sys
from contextlib import suppress
from copy import deepcopy
from datetime import datetime, timedelta
from functools import reduce
from itertools import count
from pathlib import Path
from shutil import rmtree
from textwrap import dedent
from time import sleep
from typing import TYPE_CHECKING, TypeVar, cast
from unittest import mock

import pytest
from git import Actor, Repo

from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.hvcs.bitbucket import Bitbucket
from semantic_release.hvcs.gitea import Gitea
from semantic_release.hvcs.github import Github
from semantic_release.hvcs.gitlab import Gitlab
from semantic_release.version.version import Version

import tests.conftest
import tests.const
import tests.util
from tests.const import (
    COMMIT_MESSAGE,
    DEFAULT_BRANCH_NAME,
    DEFAULT_MERGE_STRATEGY_OPTION,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    NULL_HEX_SHA,
    RepoActionStep,
)
from tests.util import (
    add_text_to_file,
    copy_dir_tree,
    temporary_working_directory,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Dict,
        Generator,
        Generic,
        List,
        Literal,
        Protocol,
        Sequence,
        Set,
        Tuple,
        TypedDict,
        TypeVar,
        Union,
    )

    from semantic_release.commit_parser._base import CommitParser, ParserOptions
    from semantic_release.commit_parser.conventional import (
        ConventionalCommitParser,
    )
    from semantic_release.commit_parser.conventional.parser_monorepo import (
        ConventionalCommitMonorepoParser,
    )
    from semantic_release.commit_parser.emoji import EmojiCommitParser
    from semantic_release.commit_parser.scipy import ScipyCommitParser
    from semantic_release.commit_parser.token import ParsedMessageResult, ParseResult

    from tests.fixtures.example_project import (
        GetHvcsFn,
        GetParserFromConfigFileFn,
        UpdateVersionPyFileFn,
    )
    from tests.fixtures.monorepos.git_monorepo import BuildMonorepoFn

    try:
        # Python 3.8 and 3.9 compatibility
        from typing_extensions import TypeAlias
    except ImportError:
        from typing import TypeAlias  # type: ignore[attr-defined, no-redef]

    from typing_extensions import NotRequired

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

    CommitConvention = Literal["conventional", "emoji", "scipy"]
    VersionStr = str
    CommitMsg = str
    DatetimeISOStr = str
    ChangelogTypeHeading = str
    TomlSerializableTypes = Union[
        Dict[Any, Any], Set[Any], List[Any], Tuple[Any, ...], int, float, bool, str
    ]

    class RepoVersionDef(TypedDict):
        """
        A reduced common repo definition, that is specific to a type of commit conventions

        Used for builder functions that only need to know about a single commit convention type
        """

        commits: list[CommitDef]

    class BaseAccumulatorVersionReduction(TypedDict):
        version_limit: Version
        repo_def: RepoDefinition

    class ChangelogTypeHeadingDef(TypedDict):
        section: ChangelogTypeHeading
        i_commits: list[int]
        """List of indexes values to match to the commits list in the RepoVersionDef"""

    class CommitDef(TypedDict):
        cid: str
        msg: CommitMsg
        type: str
        category: str
        desc: str
        brking_desc: str
        scope: str
        mr: str
        sha: str
        datetime: NotRequired[DatetimeISOStr]
        include_in_changelog: bool
        file_to_change: NotRequired[Path | str]

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
            mask_initial_release: bool = True,  # Default as of v10
            package_name: str = ...,
            monorepo: bool = False,
        ) -> tuple[Path, HvcsBase]: ...

    class CommitNReturnChangelogEntryFn(Protocol):
        def __call__(self, git_repo: Repo, commit_def: CommitDef) -> CommitDef: ...

    class SimulateChangeCommitsNReturnChangelogEntryFn(Protocol):
        def __call__(
            self, git_repo: Repo, commit_msgs: Sequence[CommitDef]
        ) -> Sequence[CommitDef]: ...

    class CreateReleaseFn(Protocol):
        def __call__(
            self,
            git_repo: Repo,
            version: str,
            tag_format: str = ...,
            timestamp: DatetimeISOStr | None = None,
            version_py_file: Path | str = ...,
            commit_message_format: str = ...,
        ) -> None: ...

    class ExProjectGitRepoFn(Protocol):
        def __call__(self) -> Repo: ...

    class ExtractRepoDefinitionFn(Protocol):
        def __call__(
            self,
            base_repo_def: dict[str, BaseRepoVersionDef],
            commit_type: CommitConvention,
        ) -> RepoDefinition: ...

    T_contra = TypeVar("T_contra", contravariant=True)

    class GetCommitDefFn(Protocol[T_contra]):
        def __call__(self, msg: str, parser: T_contra) -> CommitDef: ...

    class GetVersionStringsFn(Protocol):
        def __call__(self) -> list[VersionStr]: ...

    class GetCommitsFromRepoBuildDefFn(Protocol):
        def __call__(
            self,
            build_definition: Sequence[RepoActions],
            filter_4_changelog: bool = False,
            ignore_merge_commits: bool = False,
        ) -> RepoDefinition: ...

    RepoDefinition: TypeAlias = dict[VersionStr, RepoVersionDef]  # type: ignore[misc] # mypy is thoroughly confused
    """
    A Type alias to define a repositories versions, commits, and changelog sections
    for a specific commit convention
    """

    class SimulateDefaultChangelogCreationFn(Protocol):
        def __call__(
            self,
            repo_definition: RepoDefinition,
            hvcs: Github | Gitlab | Gitea | Bitbucket,
            dest_file: Path | None = None,
            max_version: Version | Literal["Unreleased"] | None = None,
            output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN,
            mask_initial_release: bool = True,  # Default as of v10
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

    class FormatGitLabMergeCommitMsgFn(Protocol):
        def __call__(
            self,
            mr_title: str,
            mr_number: int,
            source_branch: str,
            target_branch: str,
            closed_issues: list[str],
        ) -> str: ...

    class CreateMergeCommitFn(Protocol):
        def __call__(
            self,
            git_repo: Repo,
            branch_name: str,
            commit_def: CommitDef,
            fast_forward: bool = True,
            strategy_option: str = DEFAULT_MERGE_STRATEGY_OPTION,
        ) -> CommitDef: ...

    class CreateSquashMergeCommitFn(Protocol):
        def __call__(
            self,
            git_repo: Repo,
            branch_name: str,
            commit_def: CommitDef,
            strategy_option: str = DEFAULT_MERGE_STRATEGY_OPTION,
        ) -> CommitDef: ...

    class CommitSpec(TypedDict):
        cid: str
        conventional: str
        emoji: str
        scipy: str
        datetime: NotRequired[DatetimeISOStr]
        include_in_changelog: NotRequired[bool]
        file_to_change: NotRequired[Path | str]

    class DetailsBase(TypedDict):
        pre_actions: NotRequired[Sequence[RepoActions]]
        post_actions: NotRequired[Sequence[RepoActions]]

    class RepoActionConfigure(TypedDict):
        action: Literal[RepoActionStep.CONFIGURE]
        details: RepoActionConfigureDetails

    class RepoActionConfigureDetails(DetailsBase):
        commit_type: CommitConvention
        hvcs_client_name: str
        hvcs_domain: str
        tag_format_str: str | None
        mask_initial_release: bool
        extra_configs: dict[str, TomlSerializableTypes]

    class RepoActionConfigureMonorepo(TypedDict):
        action: Literal[RepoActionStep.CONFIGURE_MONOREPO]
        details: RepoActionConfigureMonorepoDetails

    class RepoActionConfigureMonorepoDetails(DetailsBase):
        package_dir: Path | str
        package_name: str
        tag_format_str: str | None
        mask_initial_release: bool
        extra_configs: dict[str, TomlSerializableTypes]

    class RepoActionCreateMonorepo(TypedDict):
        action: Literal[RepoActionStep.CREATE_MONOREPO]
        details: RepoActionCreateMonorepoDetails

    class RepoActionCreateMonorepoDetails(DetailsBase):
        commit_type: CommitConvention
        hvcs_client_name: str
        hvcs_domain: str
        origin_url: NotRequired[str]

    class RepoActionChangeDirectory(TypedDict):
        action: Literal[RepoActionStep.CHANGE_DIRECTORY]
        details: RepoActionChangeDirectoryDetails

    class RepoActionChangeDirectoryDetails(DetailsBase):
        directory: Path | str

    class RepoActionMakeCommits(TypedDict):
        action: Literal[RepoActionStep.MAKE_COMMITS]
        details: RepoActionMakeCommitsDetails

    class RepoActionMakeCommitsDetails(DetailsBase):
        commits: Sequence[CommitDef]

    class RepoActionRelease(TypedDict):
        action: Literal[RepoActionStep.RELEASE]
        details: RepoActionReleaseDetails

    class RepoActionReleaseDetails(DetailsBase):
        commit_message_format: NotRequired[str]
        datetime: DatetimeISOStr
        tag_format: NotRequired[str]
        version: str
        version_py_file: NotRequired[Path | str]

    class RepoActionGitCheckout(TypedDict):
        action: Literal[RepoActionStep.GIT_CHECKOUT]
        details: RepoActionGitCheckoutDetails

    class RepoActionGitCheckoutDetails(DetailsBase):
        create_branch: NotRequired[RepoActionGitCheckoutCreateBranch]
        branch: NotRequired[str]

    class RepoActionGitCheckoutCreateBranch(TypedDict):
        name: str
        start_branch: str

    class RepoActionGitSquash(TypedDict):
        action: Literal[RepoActionStep.GIT_SQUASH]
        details: RepoActionGitSquashDetails

    class RepoActionGitSquashDetails(DetailsBase):
        branch: str
        strategy_option: str
        commit_def: CommitDef
        config_file: NotRequired[Path | str]

    class RepoActionGitMergeDetails(DetailsBase):
        branch_name: str
        commit_def: CommitDef
        fast_forward: Literal[False]
        strategy_option: NotRequired[str]

    class RepoActionGitFFMergeDetails(DetailsBase):
        branch_name: str
        fast_forward: Literal[True]

    MergeDetails = TypeVar(
        "MergeDetails",
        bound=Union[RepoActionGitMergeDetails, RepoActionGitFFMergeDetails],
    )

    class RepoActionGitMerge(Generic[MergeDetails], TypedDict):
        action: Literal[RepoActionStep.GIT_MERGE]
        details: MergeDetails

    class RepoActionWriteChangelogs(TypedDict):
        action: Literal[RepoActionStep.WRITE_CHANGELOGS]
        details: RepoActionWriteChangelogsDetails

    class RepoActionWriteChangelogsDetails(DetailsBase):
        new_version: Version | Literal["Unreleased"]
        max_version: NotRequired[Version | Literal["Unreleased"]]
        dest_files: Sequence[RepoActionWriteChangelogsDestFile]
        commit_ids: Sequence[str]

    class RepoActionWriteChangelogsDestFile(TypedDict):
        path: Path | str
        format: ChangelogOutputFormat
        mask_initial_release: bool

    class ConvertCommitSpecToCommitDefFn(Protocol):
        def __call__(
            self,
            commit_spec: CommitSpec,
            commit_type: CommitConvention,
            parser: CommitParser[ParseResult, ParserOptions],
            monorepo: bool = ...,
        ) -> CommitDef: ...

    class GetRepoDefinitionFn(Protocol):
        def __call__(
            self,
            commit_type: CommitConvention,
            hvcs_client_name: str = "github",
            hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
            tag_format_str: str | None = None,
            extra_configs: dict[str, TomlSerializableTypes] | None = None,
            mask_initial_release: bool = ...,
            ignore_merge_commits: bool = True,  # Default as of v10
        ) -> Sequence[RepoActions]: ...

    class BuildRepoFromDefinitionFn(Protocol):
        def __call__(
            self,
            dest_dir: Path | str,
            repo_construction_steps: Sequence[RepoActions],
        ) -> Sequence[RepoActions]: ...

    class BuiltRepoResult(TypedDict):
        definition: Sequence[RepoActions]
        repo: Repo

    class GetVersionsFromRepoBuildDefFn(Protocol):
        def __call__(self, repo_def: Sequence[RepoActions]) -> Sequence[Version]: ...

    class ConvertCommitSpecsToCommitDefsFn(Protocol):
        def __call__(
            self,
            commits: Sequence[CommitSpec],
            commit_type: CommitConvention,
            parser: CommitParser[ParseResult, ParserOptions],
            monorepo: bool = ...,
        ) -> Sequence[CommitDef]: ...

    class BuildSpecificRepoFn(Protocol):
        def __call__(
            self, repo_name: str, commit_type: CommitConvention, dest_dir: Path
        ) -> Sequence[RepoActions]: ...

    RepoActions: TypeAlias = Union[
        RepoActionChangeDirectory,
        RepoActionConfigure,
        RepoActionConfigureMonorepo,
        RepoActionCreateMonorepo,
        RepoActionGitCheckout,
        RepoActionGitMerge[RepoActionGitMergeDetails],
        RepoActionGitMerge[RepoActionGitFFMergeDetails],
        RepoActionGitSquash,
        RepoActionMakeCommits,
        RepoActionRelease,
        RepoActionWriteChangelogs,
    ]

    class GetGitRepo4DirFn(Protocol):
        def __call__(self, directory: Path | str) -> Repo: ...

    class SplitRepoActionsByReleaseTagsFn(Protocol):
        def __call__(
            self,
            repo_definition: Sequence[RepoActions],
        ) -> dict[Version | Literal["Unreleased"] | None, list[RepoActions]]: ...

    class GetCfgValueFromDefFn(Protocol):
        def __call__(
            self, build_definition: Sequence[RepoActions], key: str
        ) -> Any: ...

    class SquashedCommitSupportedParser(Protocol):
        def unsquash_commit_message(self, message: str) -> list[str]: ...

        def parse_message(self, message: str) -> ParsedMessageResult | None: ...

    class SeparateSquashedCommitDefFn(Protocol):
        def __call__(
            self, squashed_commit_def: CommitDef, parser: SquashedCommitSupportedParser
        ) -> list[CommitDef]: ...

    class GenerateDefaultReleaseNotesFromDefFn(Protocol):
        def __call__(
            self,
            version_actions: Sequence[RepoActions],
            hvcs: Github | Gitlab | Gitea | Bitbucket,
            previous_version: Version | None = None,
            license_name: str = "",
            dest_file: Path | None = None,
            mask_initial_release: bool = True,  # Default as of v10
        ) -> str: ...

    class GetHvcsClientFromRepoDefFn(Protocol):
        def __call__(
            self,
            repo_def: Sequence[RepoActions],
        ) -> Github | Gitlab | Gitea | Bitbucket: ...


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

    def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
        if not cached_example_project.exists():
            raise RuntimeError("Unable to find cached project files")

        # make a copy of the example project as a base
        copy_dir_tree(cached_example_project, cached_repo_path)

        # initialize git repo (open and close)
        # NOTE: We don't want to hold the repo object open for the entire test session,
        # the implementation on Windows holds some file descriptors open until close is called.
        with Repo.init(cached_repo_path) as repo:
            rmtree(str(Path(repo.git_dir, "hooks")))

            # set up remote origin (including a refs directory)
            git_origin_dir = Path(repo.common_dir, "refs", "remotes", "origin")
            repo.create_remote(name=git_origin_dir.name, url=example_git_https_url)
            git_origin_dir.mkdir(parents=True, exist_ok=True)

            # Without this the global config may set it to "master", we want consistency
            repo.git.branch("-M", DEFAULT_BRANCH_NAME)

            with repo.config_writer("repository") as config:
                config.set_value("user", "name", commit_author.name)
                config.set_value("user", "email", commit_author.email)
                config.set_value("commit", "gpgsign", False)
                config.set_value("tag", "gpgsign", False)

                # set up a remote tracking branch for the default branch
                config.set_value(f'branch "{DEFAULT_BRANCH_NAME}"', "remote", "origin")
                config.set_value(
                    f'branch "{DEFAULT_BRANCH_NAME}"',
                    "merge",
                    f"refs/heads/{DEFAULT_BRANCH_NAME}",
                )

            # make sure all base files are in index to enable initial commit
            repo.index.add(("*", ".gitignore"))

        # This is a special build, we don't expose the Repo Actions to the caller
        return []

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
    return "file.txt"


@pytest.fixture(scope="session")
def example_git_ssh_url():
    return f"git@{EXAMPLE_HVCS_DOMAIN}:{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def example_git_https_url():
    return f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}.git"


@pytest.fixture(scope="session")
def get_commit_def_of_conventional_commit() -> GetCommitDefFn[ConventionalCommitParser]:
    def _get_commit_def(msg: str, parser: ConventionalCommitParser) -> CommitDef:
        if not (parsed_result := parser.parse_message(msg)):
            return {
                "cid": "",
                "msg": msg,
                "type": "unknown",
                "category": "Unknown",
                "desc": msg,
                "brking_desc": "",
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
                "include_in_changelog": False,
            }

        return {
            "cid": "",
            "msg": msg,
            "type": parsed_result.type,
            "category": parsed_result.category,
            "desc": str.join("\n\n", parsed_result.descriptions),
            "brking_desc": str.join("\n\n", parsed_result.breaking_descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
            "include_in_changelog": True,
        }

    return _get_commit_def


@pytest.fixture(scope="session")
def get_commit_def_of_conventional_commit_monorepo() -> (
    GetCommitDefFn[ConventionalCommitMonorepoParser]
):
    def _get_commit_def(
        msg: str, parser: ConventionalCommitMonorepoParser
    ) -> CommitDef:
        if not (parsed_result := parser.parse_message(msg)):
            return {
                "cid": "",
                "msg": msg,
                "type": "unknown",
                "category": "Unknown",
                "desc": msg,
                "brking_desc": "",
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
                "include_in_changelog": False,
            }

        return {
            "cid": "",
            "msg": msg,
            "type": parsed_result.type,
            "category": parsed_result.category,
            "desc": str.join("\n\n", parsed_result.descriptions),
            "brking_desc": str.join("\n\n", parsed_result.breaking_descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
            "include_in_changelog": True,
        }

    return _get_commit_def


@pytest.fixture(scope="session")
def get_commit_def_of_emoji_commit() -> GetCommitDefFn[EmojiCommitParser]:
    def _get_commit_def_of_emoji_commit(
        msg: str, parser: EmojiCommitParser
    ) -> CommitDef:
        if not (parsed_result := parser.parse_message(msg)):
            return {
                "cid": "",
                "msg": msg,
                "type": "unknown",
                "category": "Other",
                "desc": msg,
                "brking_desc": "",
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
                "include_in_changelog": False,
            }

        return {
            "cid": "",
            "msg": msg,
            "type": parsed_result.type,
            "category": parsed_result.category,
            "desc": str.join("\n\n", parsed_result.descriptions),
            "brking_desc": str.join("\n\n", parsed_result.breaking_descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
            "include_in_changelog": True,
        }

    return _get_commit_def_of_emoji_commit


@pytest.fixture(scope="session")
def get_commit_def_of_scipy_commit() -> GetCommitDefFn[ScipyCommitParser]:
    def _get_commit_def_of_scipy_commit(
        msg: str, parser: ScipyCommitParser
    ) -> CommitDef:
        if not (parsed_result := parser.parse_message(msg)):
            return {
                "cid": "",
                "msg": msg,
                "type": "unknown",
                "category": "Unknown",
                "desc": msg,
                "brking_desc": "",
                "scope": "",
                "mr": "",
                "sha": NULL_HEX_SHA,
                "include_in_changelog": False,
            }

        return {
            "cid": "",
            "msg": msg,
            "type": parsed_result.type,
            "category": parsed_result.category,
            "desc": str.join("\n\n", parsed_result.descriptions),
            "brking_desc": str.join("\n\n", parsed_result.breaking_descriptions),
            "scope": parsed_result.scope,
            "mr": parsed_result.linked_merge_request,
            "sha": NULL_HEX_SHA,
            "include_in_changelog": True,
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
def format_merge_commit_msg_gitlab() -> FormatGitLabMergeCommitMsgFn:
    def _format_merge_commit_msg(
        mr_title: str,
        mr_number: int,
        source_branch: str,
        target_branch: str,
        closed_issues: list[str],
    ) -> str:
        """REF: https://docs.gitlab.com/17.8/ee/user/project/merge_requests/commit_templates.html"""
        reference = f"{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}!{mr_number}"
        issue_statement = (
            ""
            if not closed_issues
            else str.join(
                " ",
                [
                    "Closes",
                    str.join(
                        " and ", [str.join(", ", closed_issues[:-1]), closed_issues[-1]]
                    )
                    if len(closed_issues) > 1
                    else closed_issues[0],
                ],
            )
        )
        return str.join(
            "\n\n",
            filter(
                None,
                [
                    f"Merge branch '{source_branch}' into '{target_branch}'",
                    f"{mr_title}",
                    f"{issue_statement}",
                    f"See merge request {reference}",
                ],
            ),
        )

    return _format_merge_commit_msg


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
        sq_commits: list[str] = (
            cast("list[str]", squashed_commits)
            if len(squashed_commits) > 1 and not isinstance(squashed_commits[0], dict)
            else list(
                filter(
                    None,
                    [
                        commit.get("msg", "") if isinstance(commit, dict) else commit
                        for commit in squashed_commits
                    ],
                )
            )
        )
        pr_title_parts = pr_title.strip().split("\n\n", maxsplit=1)
        return (
            str.join(
                "\n\n",
                [
                    f"{pr_title_parts[0]} (#{pr_number})",
                    *pr_title_parts[1:],
                    *[f"* {commit_str}" for commit_str in sq_commits],
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
        strategy_option: str = DEFAULT_MERGE_STRATEGY_OPTION,
    ) -> CommitDef:
        curr_dt = stable_now_date()
        commit_dt = (
            datetime.fromisoformat(commit_def["datetime"])
            if "datetime" in commit_def
            else curr_dt
        )
        timestamp = commit_dt.isoformat(timespec="seconds")

        if curr_dt == commit_dt:
            sleep(1)  # ensure commit timestamps are unique

        with git_repo.git.custom_environment(
            GIT_AUTHOR_DATE=timestamp,
            GIT_COMMITTER_DATE=timestamp,
        ):
            git_repo.git.merge(
                branch_name,
                ff=fast_forward,
                no_ff=bool(not fast_forward),
                m=commit_def["msg"],
                strategy_option=strategy_option,
            )

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
        strategy_option: str = DEFAULT_MERGE_STRATEGY_OPTION,
    ) -> CommitDef:
        curr_dt = stable_now_date()
        commit_dt = (
            datetime.fromisoformat(commit_def["datetime"])
            if "datetime" in commit_def
            else curr_dt
        )

        if curr_dt == commit_dt:
            sleep(1)  # ensure commit timestamps are unique

        # merge --squash never commits on action, first it stages the changes
        git_repo.git.merge(
            branch_name,
            squash=True,
            strategy_option=strategy_option,
        )

        # commit the squashed changes
        git_repo.git.commit(
            m=commit_def["msg"],
            date=commit_dt.isoformat(timespec="seconds"),
        )

        # After a merge we need to ensure the remote tracking branch is updated
        with suppress(TypeError):
            # Fake an automated push to remote by updating the remote tracking branch
            # Detached HEAD commits won't have an active branch and throw a TypeError
            git_repo.git.update_ref(
                f"refs/remotes/origin/{git_repo.active_branch.name}",
                git_repo.head.commit.hexsha,
            )

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
    update_version_py_file: UpdateVersionPyFileFn,
    default_tag_format_str: str,
    stable_now_date: GetStableDateNowFn,
) -> CreateReleaseFn:
    def _mimic_semantic_release_commit(
        git_repo: Repo,
        version: Version | str,
        tag_format: str = default_tag_format_str,
        timestamp: DatetimeISOStr | None = None,
        version_py_file: Path | str = "",
        commit_message_format: str = COMMIT_MESSAGE,
    ) -> None:
        curr_dt = stable_now_date()
        commit_dt = (
            datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else curr_dt
        )

        if curr_dt == commit_dt:
            sleep(1)  # ensure commit timestamps are unique

        # stamp version into version file
        if version_py_file:
            update_version_py_file(version=version, version_file=version_py_file)
        else:
            update_version_py_file(version=version)

        # stamp version into pyproject.toml
        update_pyproject_toml("tool.poetry.version", str(version))

        # commit --all files with version number commit message
        git_repo.git.commit(
            a=True,
            m=commit_message_format.format(version=str(version)),
            date=commit_dt.isoformat(timespec="seconds"),
        )

        with suppress(TypeError):
            # Fake an automated push to remote by updating the remote tracking branch
            # Detached HEAD commits won't have an active branch and throw a TypeError
            git_repo.git.update_ref(
                f"refs/remotes/origin/{git_repo.active_branch.name}",
                git_repo.head.commit.hexsha,
            )

        # ensure commit timestamps are unique (adding one second even though a nanosecond has gone by)
        commit_dt += timedelta(seconds=1)

        with git_repo.git.custom_environment(
            GIT_COMMITTER_DATE=commit_dt.isoformat(timespec="seconds"),
        ):
            # tag commit with version number
            tag_str = tag_format.format(version=str(version))
            git_repo.git.tag(tag_str, m=tag_str)

    return _mimic_semantic_release_commit


@pytest.fixture(scope="session")
def commit_n_rtn_changelog_entry(
    stable_now_date: GetStableDateNowFn,
) -> CommitNReturnChangelogEntryFn:
    def _commit_n_rtn_changelog_entry(
        git_repo: Repo, commit_def: CommitDef
    ) -> CommitDef:
        # make commit with --all files
        curr_dt = stable_now_date()
        commit_dt = (
            datetime.fromisoformat(commit_def["datetime"])
            if "datetime" in commit_def
            else curr_dt
        )

        if curr_dt == commit_dt:
            sleep(1)  # ensure commit timestamps are unique

        git_repo.git.commit(
            a=True,
            m=commit_def["msg"],
            date=commit_dt.isoformat(timespec="seconds"),
        )

        with suppress(TypeError):
            # Fake an automated push to remote by updating the remote tracking branch
            # Detached HEAD commits won't have an active branch and throw a TypeError
            git_repo.git.update_ref(
                f"refs/remotes/origin/{git_repo.active_branch.name}",
                git_repo.head.commit.hexsha,
            )

        # Capture the resulting commit message and sha
        return {
            **commit_def,
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
        git_repo: Repo, commit_msgs: Sequence[CommitDef]
    ) -> Sequence[CommitDef]:
        changelog_entries: list[CommitDef] = []
        for commit_msg in commit_msgs:
            if not git_repo.is_dirty(index=True, working_tree=False):
                add_text_to_file(
                    git_repo, str(commit_msg.get("file_to_change", file_in_repo))
                )

            changelog_entries.append(commit_n_rtn_changelog_entry(git_repo, commit_msg))

        return changelog_entries

    return _simulate_change_commits_n_rtn_changelog_entry


@pytest.fixture(scope="session")
def get_hvcs_client_from_repo_def(
    example_git_https_url: str,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
) -> GetHvcsClientFromRepoDefFn:
    hvcs_client_classes = {
        Bitbucket.__name__.lower(): Bitbucket,
        Github.__name__.lower(): Github,
        Gitea.__name__.lower(): Gitea,
        Gitlab.__name__.lower(): Gitlab,
    }

    def _get_hvcs_client_from_repo_def(
        repo_def: Sequence[RepoActions],
    ) -> Github | Gitlab | Gitea | Bitbucket:
        hvcs_type = get_cfg_value_from_def(repo_def, "hvcs_client_name")
        hvcs_client_class = hvcs_client_classes[hvcs_type]

        # Prevent the HVCS client from using the environment variables
        with mock.patch.dict(os.environ, {}, clear=True):
            hvcs_client = cast(
                "HvcsBase",
                hvcs_client_class(
                    example_git_https_url,
                    hvcs_domain=get_cfg_value_from_def(repo_def, "hvcs_domain"),
                ),
            )
            # Force the HVCS client to attempt to resolve the repo name (as we generally cache it)
            assert hvcs_client.repo_name
            assert hvcs_client.owner
            return cast("Github | Gitlab | Gitea | Bitbucket", hvcs_client)

    return _get_hvcs_client_from_repo_def


@pytest.fixture(scope="session")
def build_configured_base_repo(  # noqa: C901
    cached_example_git_project: Path,
    configure_base_repo: BuildRepoFn,
) -> BuildRepoFn:
    """
    This fixture is intended to simplify repo scenario building by initially
    creating the repo but also configuring semantic_release in the pyproject.toml
    for when the test executes semantic_release. It returns a function so that
    derivative fixtures can call this fixture with individual parameters.
    """

    def _build_configured_base_repo(  # noqa: C901
        dest_dir: Path | str,
        commit_type: CommitConvention = "conventional",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = True,  # Default as of v10
        package_name: str = EXAMPLE_PROJECT_NAME,
        monorepo: bool = False,
    ) -> tuple[Path, HvcsBase]:
        if not cached_example_git_project.exists():
            raise RuntimeError("Unable to find cached git project files!")

        # Copy the cached git project the dest directory
        copy_dir_tree(cached_example_git_project, dest_dir)

        return configure_base_repo(
            dest_dir=dest_dir,
            commit_type=commit_type,
            hvcs_client_name=hvcs_client_name,
            hvcs_domain=hvcs_domain,
            tag_format_str=tag_format_str,
            extra_configs=extra_configs,
            mask_initial_release=mask_initial_release,
            package_name=package_name,
            monorepo=monorepo,
        )

    return _build_configured_base_repo


@pytest.fixture(scope="session")
def configure_base_repo(  # noqa: C901
    use_github_hvcs: UseHvcsFn,
    use_gitlab_hvcs: UseHvcsFn,
    use_gitea_hvcs: UseHvcsFn,
    use_bitbucket_hvcs: UseHvcsFn,
    use_conventional_parser: UseParserFn,
    use_emoji_parser: UseParserFn,
    use_scipy_parser: UseParserFn,
    use_custom_parser: UseCustomParserFn,
    example_git_https_url: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    get_wheel_file: GetWheelFileFn,
    pyproject_toml_file: Path,
    get_hvcs: GetHvcsFn,
) -> BuildRepoFn:
    """
    This fixture is intended to simplify repo scenario building by initially
    creating the repo but also configuring semantic_release in the pyproject.toml
    for when the test executes semantic_release. It returns a function so that
    derivative fixtures can call this fixture with individual parameters.
    """

    def _configure_base_repo(  # noqa: C901
        dest_dir: Path | str,
        commit_type: str = "conventional",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = True,  # Default as of v10
        package_name: str = EXAMPLE_PROJECT_NAME,
        monorepo: bool = False,
    ) -> tuple[Path, HvcsBase]:
        # Make sure we are in the dest directory
        with temporary_working_directory(dest_dir):
            # Set parser configuration
            if commit_type == "conventional":
                use_conventional_parser(
                    toml_file=pyproject_toml_file, monorepo=monorepo
                )
            elif commit_type == "emoji":
                use_emoji_parser(toml_file=pyproject_toml_file, monorepo=monorepo)
            elif commit_type == "scipy":
                use_scipy_parser(toml_file=pyproject_toml_file, monorepo=monorepo)
            else:
                use_custom_parser(commit_type, toml_file=pyproject_toml_file)

            # Set HVCS configuration
            if hvcs_client_name == "github":
                use_github_hvcs(hvcs_domain, toml_file=pyproject_toml_file)
            elif hvcs_client_name == "gitlab":
                use_gitlab_hvcs(hvcs_domain, toml_file=pyproject_toml_file)
            elif hvcs_client_name == "gitea":
                use_gitea_hvcs(hvcs_domain, toml_file=pyproject_toml_file)
            elif hvcs_client_name == "bitbucket":
                use_bitbucket_hvcs(hvcs_domain, toml_file=pyproject_toml_file)
            else:
                raise ValueError(f"Unknown HVCS client name: {hvcs_client_name}")

            # Create HVCS Client instance
            hvcs = get_hvcs(
                hvcs_client_name=hvcs_client_name,
                origin_url=example_git_https_url,
                hvcs_domain=hvcs_domain,
            )

            # Set tag format in configuration
            if tag_format_str is not None:
                update_pyproject_toml(
                    "tool.semantic_release.tag_format",
                    tag_format_str,
                    toml_file=pyproject_toml_file,
                )

            # Set the build_command to create a wheel file (using the build_command_env version variable)
            build_result_file = (
                get_wheel_file("$NEW_VERSION", pkg_name=package_name)
                if sys.platform != "win32"
                else get_wheel_file("$Env:NEW_VERSION", pkg_name=package_name)
            )
            update_pyproject_toml(
                # NOTE: must work in both bash and Powershell
                "tool.semantic_release.build_command",
                # NOTE: we are trying to ensure a few non-file-path characters are removed, but this is not
                #       the equivalent of a cononcial version translator, so it may not work in all cases
                dedent(
                    f"""\
                    mkdir -p "{build_result_file.parent}"
                    WHEEL_FILE="$(printf '%s' "{build_result_file}" | sed 's/+/./g')"
                    touch "$WHEEL_FILE"
                    """
                    if sys.platform != "win32"
                    else f"""\
                    mkdir {build_result_file.parent} > $null
                    $WHEEL_FILE = "{build_result_file}".Replace('+', '.')
                    New-Item -ItemType file -Path "$WHEEL_FILE" -Force | Select-Object OriginalPath
                    """
                ),
                toml_file=pyproject_toml_file,
            )

            # Set whether or not the initial release should be masked
            update_pyproject_toml(
                "tool.semantic_release.changelog.default_templates.mask_initial_release",
                mask_initial_release,
                toml_file=pyproject_toml_file,
            )

            # Apply configurations to pyproject.toml
            if extra_configs is not None:
                for key, value in extra_configs.items():
                    update_pyproject_toml(key, value, toml_file=pyproject_toml_file)

        return Path(dest_dir), hvcs

    return _configure_base_repo


@pytest.fixture(scope="session")
def separate_squashed_commit_def() -> SeparateSquashedCommitDefFn:
    def _separate_squashed_commit_def(
        squashed_commit_def: CommitDef,
        parser: SquashedCommitSupportedParser,
    ) -> list[CommitDef]:
        if not hasattr(parser, "unsquash_commit_message"):
            return [squashed_commit_def]

        unsquashed_messages = parser.unsquash_commit_message(
            message=squashed_commit_def["msg"]
        )

        commit_num_gen = (i for i in count(start=1, step=1))

        return [
            {
                "cid": f"{squashed_commit_def['cid']}-{next(commit_num_gen)}",
                "msg": squashed_message,
                "type": parsed_result.type,
                "category": parsed_result.category,
                "desc": str.join("\n\n", parsed_result.descriptions),
                "brking_desc": str.join("\n\n", parsed_result.breaking_descriptions),
                "scope": parsed_result.scope,
                "mr": parsed_result.linked_merge_request or squashed_commit_def["mr"],
                "sha": squashed_commit_def["sha"],
                "include_in_changelog": True,
                "datetime": squashed_commit_def.get("datetime", ""),
            }
            for parsed_result, squashed_message in iter(
                (parser.parse_message(squashed_msg), squashed_msg)
                for squashed_msg in unsquashed_messages
            )
            if parsed_result is not None
        ]

    return _separate_squashed_commit_def


@pytest.fixture(scope="session")
def convert_commit_spec_to_commit_def(
    get_commit_def_of_conventional_commit: GetCommitDefFn[ConventionalCommitParser],
    get_commit_def_of_conventional_commit_monorepo: GetCommitDefFn[
        ConventionalCommitMonorepoParser
    ],
    get_commit_def_of_emoji_commit: GetCommitDefFn[EmojiCommitParser],
    get_commit_def_of_scipy_commit: GetCommitDefFn[ScipyCommitParser],
    stable_now_date: datetime,
) -> ConvertCommitSpecToCommitDefFn:
    message_parsers = {
        "conventional": get_commit_def_of_conventional_commit,
        "conventional-monorepo": get_commit_def_of_conventional_commit_monorepo,
        "emoji": get_commit_def_of_emoji_commit,
        "scipy": get_commit_def_of_scipy_commit,
    }

    def _convert(
        commit_spec: CommitSpec,
        commit_type: CommitConvention,
        parser: CommitParser[ParseResult, ParserOptions],
        monorepo: bool = False,
    ) -> CommitDef:
        parse_msg_fn = cast(
            "GetCommitDefFn[Any]",
            message_parsers[f"{commit_type}{'-monorepo' if monorepo else ''}"],
        )

        # Extract the correct commit message for the commit type
        commit_def: CommitDef = {
            **parse_msg_fn(commit_spec[commit_type], parser=parser),
            "cid": commit_spec["cid"],
            "datetime": (
                commit_spec["datetime"]
                if "datetime" in commit_spec
                else stable_now_date.isoformat(timespec="seconds")
            ),
            "include_in_changelog": commit_spec.get("include_in_changelog", True),
        }

        if "file_to_change" in commit_spec:
            commit_def.update(
                {
                    "file_to_change": commit_spec["file_to_change"],
                }
            )

        return commit_def

    return _convert


@pytest.fixture(scope="session")
def convert_commit_specs_to_commit_defs(
    convert_commit_spec_to_commit_def: ConvertCommitSpecToCommitDefFn,
) -> ConvertCommitSpecsToCommitDefsFn:
    def _convert(
        commits: Sequence[CommitSpec],
        commit_type: CommitConvention,
        parser: CommitParser[ParseResult, ParserOptions],
        monorepo: bool = False,
    ) -> Sequence[CommitDef]:
        return [
            convert_commit_spec_to_commit_def(
                commit, commit_type, parser=parser, monorepo=monorepo
            )
            for commit in commits
        ]

    return _convert


@pytest.fixture(scope="session")
def build_repo_from_definition(  # noqa: C901, its required and its just test code
    build_configured_base_repo: BuildRepoFn,
    build_base_monorepo: BuildMonorepoFn,
    configure_monorepo_package: BuildRepoFn,
    default_tag_format_str: str,
    create_release_tagged_commit: CreateReleaseFn,
    create_squash_merge_commit: CreateSquashMergeCommitFn,
    create_merge_commit: CreateMergeCommitFn,
    simulate_change_commits_n_rtn_changelog_entry: SimulateChangeCommitsNReturnChangelogEntryFn,
    simulate_default_changelog_creation: SimulateDefaultChangelogCreationFn,
    separate_squashed_commit_def: SeparateSquashedCommitDefFn,
    get_hvcs: GetHvcsFn,
    example_git_https_url: str,
    get_parser_from_config_file: GetParserFromConfigFileFn,
    pyproject_toml_file: Path,
) -> BuildRepoFromDefinitionFn:
    def expand_repo_construction_steps(
        acc: Sequence[RepoActions], step: RepoActions
    ) -> Sequence[RepoActions]:
        empty_tuple = cast("tuple[RepoActions, ...]", ())
        unpacked_pre_actions = reduce(
            expand_repo_construction_steps,  # type: ignore[arg-type]
            step["details"].pop("pre_actions", empty_tuple),
            empty_tuple,
        )

        unpacked_post_actions = reduce(
            expand_repo_construction_steps,  # type: ignore[arg-type]
            step["details"].pop("post_actions", empty_tuple),
            empty_tuple,
        )

        return (*acc, *unpacked_pre_actions, step, *unpacked_post_actions)

    def _build_repo_from_definition(  # noqa: C901, its required and its just test code
        dest_dir: Path | str, repo_construction_steps: Sequence[RepoActions]
    ) -> Sequence[RepoActions]:
        completed_repo_steps: list[RepoActions] = []

        expanded_repo_construction_steps: tuple[RepoActions, ...] = tuple(
            reduce(
                expand_repo_construction_steps,  # type: ignore[arg-type]
                repo_construction_steps,
                (),
            )
        )

        repo_dir = Path(dest_dir).resolve().absolute()
        commit_type: CommitConvention = "conventional"
        hvcs: Github | Gitlab | Gitea | Bitbucket
        commit_cache: dict[str, CommitDef] = {}
        current_repo_def: dict[Version | Literal["Unreleased"], RepoVersionDef] = {}

        with temporary_working_directory(repo_dir):
            for step in expanded_repo_construction_steps:
                step_result = deepcopy(step)
                action = step["action"]

                if action == RepoActionStep.CONFIGURE:
                    cfg_def = cast("RepoActionConfigureDetails", step_result["details"])

                    # Make sure the resulting build definition is complete with the default
                    cfg_def["tag_format_str"] = (
                        cfg_def["tag_format_str"] or default_tag_format_str
                    )

                    _, hvcs = build_configured_base_repo(  # type: ignore[assignment] # TODO: fix the type error
                        dest_dir,
                        **{
                            key: cfg_def[key]  # type: ignore[literal-required]
                            for key in [
                                "commit_type",
                                "hvcs_client_name",
                                "hvcs_domain",
                                "tag_format_str",
                                "mask_initial_release",
                                "extra_configs",
                            ]
                        },
                    )

                elif action == RepoActionStep.CREATE_MONOREPO:
                    cfg_mr_def = cast(
                        "RepoActionCreateMonorepoDetails", step_result["details"]
                    )
                    build_base_monorepo(dest_dir=repo_dir)
                    hvcs = get_hvcs(
                        hvcs_client_name=cfg_mr_def["hvcs_client_name"],
                        origin_url=cfg_mr_def.get("origin_url")
                        or example_git_https_url,
                        hvcs_domain=cfg_mr_def["hvcs_domain"],
                    )
                    commit_type = cfg_mr_def["commit_type"]

                elif action == RepoActionStep.CONFIGURE_MONOREPO:
                    cfg_mr_pkg_def = cast(
                        "RepoActionConfigureMonorepoDetails", step_result["details"]
                    )
                    configure_monorepo_package(
                        dest_dir=cfg_mr_pkg_def["package_dir"],
                        commit_type=commit_type,
                        hvcs_client_name=hvcs.__class__.__name__.lower(),
                        hvcs_domain=str(hvcs.hvcs_domain),
                        tag_format_str=cfg_mr_pkg_def["tag_format_str"],
                        extra_configs=cfg_mr_pkg_def["extra_configs"],
                        mask_initial_release=cfg_mr_pkg_def["mask_initial_release"],
                        package_name=cfg_mr_pkg_def["package_name"],
                        monorepo=True,
                    )

                elif action == RepoActionStep.CHANGE_DIRECTORY:
                    change_dir_def = cast(
                        "RepoActionChangeDirectoryDetails", step_result["details"]
                    )
                    if not (
                        new_cwd := Path(change_dir_def["directory"])
                        .resolve()
                        .absolute()
                    ).exists():
                        msg = f"Directory {change_dir_def['directory']} does not exist."
                        raise NotADirectoryError(msg)

                    # Helpful Transform to find the project root repo without needing to pass it around (ie '/' => repo_dir)
                    new_cwd = (
                        repo_dir if str(new_cwd) == str(repo_dir.root) else new_cwd
                    )

                    if not new_cwd.is_dir():
                        msg = f"Path {change_dir_def['directory']} is not a directory."
                        raise NotADirectoryError(msg)

                    # TODO: 3.9+, use is_relative_to
                    # if not new_cwd.is_relative_to(repo_dir):
                    if repo_dir != new_cwd and repo_dir not in new_cwd.parents:
                        msg = f"Cannot change directory to '{new_cwd}' as it is outside the repo directory '{repo_dir}'."
                        raise ValueError(msg)

                    os.chdir(str(new_cwd))

                elif action == RepoActionStep.MAKE_COMMITS:
                    mk_cmts_def = cast(
                        "RepoActionMakeCommitsDetails", step_result["details"]
                    )

                    # update the commit definitions with the repo hashes
                    with Repo(repo_dir) as git_repo:
                        mk_cmts_def["commits"] = (
                            simulate_change_commits_n_rtn_changelog_entry(
                                git_repo,
                                mk_cmts_def["commits"],
                            )
                        )

                    for commit in mk_cmts_def["commits"]:
                        if commit["cid"] in commit_cache:
                            raise ValueError(
                                f"Duplicate commit id '{commit['cid']}' detected!"
                            )

                        commit_cache.update({commit["cid"]: commit})

                elif action == RepoActionStep.WRITE_CHANGELOGS:
                    w_chlgs_def = cast(
                        "RepoActionWriteChangelogsDetails", step["details"]
                    )

                    # Mark the repo definition with the latest stored commits for the upcoming release
                    new_version = w_chlgs_def["new_version"]
                    current_repo_def.update(
                        {
                            new_version: {
                                "commits": [
                                    *filter(
                                        None,
                                        (
                                            cmt
                                            for commit_id in w_chlgs_def["commit_ids"]
                                            if (cmt := commit_cache[commit_id])[
                                                "include_in_changelog"
                                            ]
                                        ),
                                    )
                                ]
                            }
                        }
                    )

                    # in order to support monorepo changelogs we must filter and map the stored repo definition
                    # to match only the sub-package's versions which are identified by matching tag formats
                    filtered_repo_def_4_changelog: RepoDefinition = {
                        str(version): repo_def
                        for version, repo_def in current_repo_def.items()
                        if (
                            isinstance(version, Version)
                            and isinstance(new_version, Version)
                            and version.tag_format == new_version.tag_format
                        )
                        or version == new_version
                    }

                    # Write each changelog with the current repo definition
                    with Repo(repo_dir) as git_repo:
                        for changelog_file_def in w_chlgs_def["dest_files"]:
                            changelog_file = repo_dir.joinpath(
                                changelog_file_def["path"]
                            )
                            simulate_default_changelog_creation(
                                filtered_repo_def_4_changelog,
                                hvcs=hvcs,
                                dest_file=changelog_file,
                                output_format=changelog_file_def["format"],
                                mask_initial_release=changelog_file_def[
                                    "mask_initial_release"
                                ],
                                max_version=w_chlgs_def.get("max_version"),
                            )

                            git_repo.git.add(str(changelog_file), force=True)

                elif action == RepoActionStep.RELEASE:
                    release_def = cast("RepoActionReleaseDetails", step["details"])

                    with Repo(repo_dir) as git_repo:
                        create_release_tagged_commit(
                            git_repo,
                            version=release_def["version"],
                            tag_format=release_def.get(
                                "tag_format", default_tag_format_str
                            ),
                            timestamp=release_def["datetime"],
                            version_py_file=release_def.get("version_py_file", ""),
                            commit_message_format=release_def.get(
                                "commit_message_format", COMMIT_MESSAGE
                            ),
                        )

                elif action == RepoActionStep.GIT_CHECKOUT:
                    ckout_def = cast("RepoActionGitCheckoutDetails", step["details"])

                    with Repo(repo_dir) as git_repo:
                        if "create_branch" in ckout_def:
                            create_branch_def = ckout_def["create_branch"]
                            start_head = git_repo.heads[
                                create_branch_def["start_branch"]
                            ]
                            new_branch_head = git_repo.create_head(
                                create_branch_def["name"],
                                commit=start_head.commit,
                            )
                            # set up a remote tracking branch for the new branch
                            with git_repo.config_writer("repository") as config:
                                config.set_value(
                                    f'branch "{create_branch_def["name"]}"',
                                    "remote",
                                    "origin",
                                )
                                config.set_value(
                                    f'branch "{create_branch_def["name"]}"',
                                    "merge",
                                    f'refs/heads/{create_branch_def["name"]}',
                                )
                            new_branch_head.checkout()

                        elif "branch" in ckout_def:
                            git_repo.heads[ckout_def["branch"]].checkout()

                elif action == RepoActionStep.GIT_SQUASH:
                    squash_def = cast(
                        "RepoActionGitSquashDetails", step_result["details"]
                    )

                    # Update the commit definition with the repo hash
                    with Repo(repo_dir) as git_repo:
                        squash_def["commit_def"] = create_squash_merge_commit(
                            git_repo=git_repo,
                            branch_name=squash_def["branch"],
                            commit_def=squash_def["commit_def"],
                            strategy_option=squash_def["strategy_option"],
                        )
                        if (
                            first_cid := f"{squash_def['commit_def']['cid']}-1"
                        ) in commit_cache:
                            raise ValueError(
                                f"Duplicate commit id '{first_cid}' detected!"
                            )

                        commit_cache.update(
                            {
                                squashed_commit_def["cid"]: squashed_commit_def
                                for squashed_commit_def in separate_squashed_commit_def(
                                    squashed_commit_def=squash_def["commit_def"],
                                    parser=cast(
                                        "SquashedCommitSupportedParser",
                                        get_parser_from_config_file(
                                            file=squash_def.get(
                                                "config_file", pyproject_toml_file
                                            ),
                                        ),
                                    ),
                                )
                            }
                        )

                elif action == RepoActionStep.GIT_MERGE:
                    this_step = cast(
                        "RepoActionGitMerge[RepoActionGitFFMergeDetails | RepoActionGitMergeDetails]",
                        step_result,
                    )

                    with Repo(repo_dir) as git_repo:
                        if this_step["details"]["fast_forward"]:
                            git_repo.git.merge(
                                this_step["details"]["branch_name"], ff=True
                            )

                        else:
                            merge_def = this_step["details"]

                            # Update the commit definition with the repo hash
                            merge_def["commit_def"] = create_merge_commit(
                                git_repo=git_repo,
                                branch_name=merge_def["branch_name"],
                                commit_def=merge_def["commit_def"],
                                fast_forward=merge_def["fast_forward"],
                                strategy_option=merge_def.get(
                                    "strategy_option", DEFAULT_MERGE_STRATEGY_OPTION
                                ),
                            )

                            if merge_def["commit_def"]["cid"] in commit_cache:
                                raise ValueError(
                                    f"Duplicate commit id '{merge_def['commit_def']['cid']}' detected!"
                                )

                            commit_cache.update(
                                {
                                    merge_def["commit_def"]["cid"]: merge_def[
                                        "commit_def"
                                    ]
                                }
                            )

                        # After a merge we need to ensure the remote tracking branch is updated
                        with suppress(TypeError):
                            # Fake an automated push to remote by updating the remote tracking branch
                            # Detached HEAD commits won't have an active branch and throw a TypeError
                            git_repo.git.update_ref(
                                f"refs/remotes/origin/{git_repo.active_branch.name}",
                                git_repo.head.commit.hexsha,
                            )

                else:
                    raise ValueError(f"Unknown action: {action}")

                completed_repo_steps.append(step_result)

        return completed_repo_steps

    return _build_repo_from_definition


@pytest.fixture(scope="session")
def get_cfg_value_from_def() -> GetCfgValueFromDefFn:
    def _get_cfg_value_from_def(
        build_definition: Sequence[RepoActions], key: str
    ) -> Any:
        configure_steps = [
            step
            for step in build_definition
            if step["action"] == RepoActionStep.CONFIGURE
        ]
        for step in configure_steps[::-1]:
            if key in step["details"]:
                return step["details"][key]  # type: ignore[literal-required]

        raise ValueError(f"Unable to find configuration key: {key}")

    return _get_cfg_value_from_def


@pytest.fixture(scope="session")
def get_versions_from_repo_build_def(
    default_tag_format_str: str,
) -> GetVersionsFromRepoBuildDefFn:
    def _get_versions(repo_def: Sequence[RepoActions]) -> Sequence[Version]:
        return [
            Version.parse(
                step["details"]["version"],
                tag_format=step["details"].get("tag_format", default_tag_format_str),
            )
            for step in repo_def
            if step["action"] == RepoActionStep.RELEASE
        ]

    return _get_versions


@pytest.fixture(scope="session")
def get_commits_from_repo_build_def() -> GetCommitsFromRepoBuildDefFn:
    def _get_commits(
        build_definition: Sequence[RepoActions],
        filter_4_changelog: bool = False,
        ignore_merge_commits: bool = False,
    ) -> RepoDefinition:
        # Extract the commits from the build definition
        repo_def: RepoDefinition = {}
        commits: list[CommitDef] = []
        for build_step in build_definition:
            if build_step["action"] == RepoActionStep.MAKE_COMMITS:
                commits_made = deepcopy(build_step["details"]["commits"])
                if filter_4_changelog:
                    commits_made = list(
                        filter(
                            lambda commit: commit["include_in_changelog"], commits_made
                        )
                    )
                commits.extend(commits_made)

            elif any(
                (
                    build_step["action"] == RepoActionStep.GIT_SQUASH,
                    build_step["action"] == RepoActionStep.GIT_MERGE,
                )
            ):
                if "commit_def" in build_step["details"]:
                    commit_def = build_step["details"]["commit_def"]  # type: ignore[typeddict-item]

                    if any(
                        (
                            ignore_merge_commits
                            and build_step["action"] == RepoActionStep.GIT_MERGE,
                            filter_4_changelog
                            and not commit_def["include_in_changelog"],
                        )
                    ):
                        continue

                    commits.append(commit_def)

            elif build_step["action"] == RepoActionStep.RELEASE:
                version = build_step["details"]["version"]
                repo_def[version] = {"commits": [*commits]}
                commits.clear()

        # Any remaining commits are considered unreleased
        if len(commits) > 0:
            repo_def["Unreleased"] = {"commits": [*commits]}

        return repo_def

    return _get_commits


@pytest.fixture(scope="session")
def split_repo_actions_by_release_tags(
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
) -> SplitRepoActionsByReleaseTagsFn:
    def _split_repo_actions_by_release_tags(
        repo_definition: Sequence[RepoActions],
    ) -> dict[Version | Literal["Unreleased"] | None, list[RepoActions]]:
        releasetags_2_steps: dict[
            Version | Literal["Unreleased"] | None, list[RepoActions]
        ] = {
            None: [],
        }

        # Create generator for next release tags
        next_release_tag_gen = (
            version for version in get_versions_from_repo_build_def(repo_definition)
        )

        # initialize the first release tag
        curr_release_tag: Version | Literal["Unreleased"] = next(next_release_tag_gen)
        releasetags_2_steps[curr_release_tag] = []

        # Loop through all actions and split them by release tags
        for step in repo_definition:
            if any(
                step["action"] == action
                for action in [
                    RepoActionStep.CONFIGURE,
                    RepoActionStep.CREATE_MONOREPO,
                    RepoActionStep.CONFIGURE_MONOREPO,
                ]
            ):
                releasetags_2_steps[None].append(step)
                continue

            if step["action"] == RepoActionStep.WRITE_CHANGELOGS:
                continue

            releasetags_2_steps[curr_release_tag].append(step)

            if step["action"] == RepoActionStep.RELEASE:
                try:
                    curr_release_tag = next(next_release_tag_gen)
                    releasetags_2_steps[curr_release_tag] = []
                except StopIteration:
                    curr_release_tag = "Unreleased"
                    releasetags_2_steps[curr_release_tag] = []

        insignificant_actions = [
            RepoActionStep.GIT_CHECKOUT,
            RepoActionStep.CHANGE_DIRECTORY,
        ]

        # Remove Unreleased if there are no significant steps in an Unreleased section
        if "Unreleased" in releasetags_2_steps and not [
            step
            for step in releasetags_2_steps["Unreleased"]
            if step["action"] not in insignificant_actions
        ]:
            del releasetags_2_steps["Unreleased"]

        # Return all actions split up by release tags
        return releasetags_2_steps

    return _split_repo_actions_by_release_tags


@pytest.fixture(scope="session")
def simulate_default_changelog_creation(  # noqa: C901
    default_md_changelog_insertion_flag: str,
    default_rst_changelog_insertion_flag: str,
    today_date_str: str,
) -> SimulateDefaultChangelogCreationFn:
    def reduce_repo_def(
        acc: BaseAccumulatorVersionReduction, ver_2_def: tuple[str, RepoVersionDef]
    ) -> BaseAccumulatorVersionReduction:
        version_str, version_def = ver_2_def

        if Version.parse(version_str) <= acc["version_limit"]:
            acc["repo_def"][version_str] = version_def

        return acc

    def build_version_entry_markdown(
        version: VersionStr,
        version_def: RepoVersionDef,
        hvcs: Github | Gitlab | Gitea | Bitbucket,
    ) -> str:
        version_entry = [
            f"## {version}\n"
            if version == "Unreleased"
            else f"## v{version} ({today_date_str})\n"
        ]

        changelog_sections = sorted(
            {commit["category"] for commit in version_def["commits"]}
        )

        brking_descriptions = []

        for section in changelog_sections:
            # Create Markdown section heading
            section_title = section.title() if not section.startswith(":") else section
            version_entry.append(f"### {section_title}\n")

            commits: list[CommitDef] = list(
                filter(
                    lambda commit, section=section: (  # type: ignore[arg-type]
                        commit["category"] == section
                    ),
                    version_def["commits"],
                )
            )

            section_bullets = []

            # format each commit
            for commit_def in commits:
                descriptions = commit_def["desc"].split("\n\n")
                if commit_def["brking_desc"]:
                    brking_descriptions.append(
                        "- {commit_scope}{brk_desc}".format(
                            commit_scope=(
                                f"**{commit_def['scope']}**: "
                                if commit_def["scope"]
                                else ""
                            ),
                            brk_desc=commit_def["brking_desc"].capitalize(),
                        )
                    )

                # NOTE: We have to be wary of the line length as the default changelog
                # has a 100 character limit or otherwise our tests will fail because the
                # URLs and whitespace don't line up

                subject_line = "- {commit_scope}{commit_desc}".format(
                    commit_desc=descriptions[0].capitalize(),
                    commit_scope=(
                        f"**{commit_def['scope']}**: " if commit_def["scope"] else ""
                    ),
                )

                mr_link = (
                    ""
                    if not commit_def["mr"]
                    else "([{mr}]({mr_url}),".format(
                        mr=commit_def["mr"],
                        mr_url=hvcs.pull_request_url(commit_def["mr"]),
                    )
                )

                sha_link = "[`{short_sha}`]({commit_url}))".format(
                    short_sha=commit_def["sha"][:7],
                    commit_url=hvcs.commit_hash_url(commit_def["sha"]),
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

                # COMMENTED out for v10 as the defualt changelog now only writes the subject line
                # if len(descriptions) > 1:
                #     commit_cl_desc += (
                #         "\n" + str.join("\n\n", [*descriptions[1:]]) + "\n"
                #     )

                # Add commits to section
                if commit_cl_desc not in section_bullets:
                    section_bullets.append(commit_cl_desc)

            version_entry.extend(sorted(section_bullets))

        # Add breaking changes to the end of the version entry
        if brking_descriptions:
            version_entry.append("### Breaking Changes\n")
            version_entry.extend([*sorted(brking_descriptions), ""])

        return str.join("\n", version_entry)

    def build_version_entry_restructured_text(
        version: VersionStr,
        version_def: RepoVersionDef,
        hvcs: Github | Gitlab | Gitea | Bitbucket,
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

        changelog_sections = sorted(
            {commit["category"] for commit in version_def["commits"]}
        )

        brking_descriptions = []
        urls = []

        for section in changelog_sections:
            # Create RestructuredText section heading
            section_title = section.title() if not section.startswith(":") else section
            version_entry.append(f"{section_title}")
            version_entry.append("-" * (len(version_entry[-1])) + "\n")

            # Filter commits by section
            commits: list[CommitDef] = list(
                filter(
                    lambda commit, section=section: (  # type: ignore[arg-type]
                        commit["category"] == section
                    ),
                    version_def["commits"],
                )
            )

            section_bullets = []

            for commit_def in commits:
                descriptions = commit_def["desc"].split("\n\n")
                if commit_def["brking_desc"]:
                    brking_descriptions.append(
                        "* {commit_scope}{brk_desc}".format(
                            commit_scope=(
                                f"**{commit_def['scope']}**: "
                                if commit_def["scope"]
                                else ""
                            ),
                            brk_desc=commit_def["brking_desc"].capitalize(),
                        )
                    )

                # NOTE: We have to be wary of the line length as the default changelog
                # has a 100 character limit or otherwise our tests will fail because the
                # URLs and whitespace don't line up

                subject_line = "* {commit_scope}{commit_desc}".format(
                    commit_desc=descriptions[0].capitalize(),
                    commit_scope=(
                        f"**{commit_def['scope']}**: " if commit_def["scope"] else ""
                    ),
                )

                mr_link = (
                    ""
                    if not commit_def["mr"]
                    else "(`{mr}`_,".format(
                        mr=commit_def["mr"],
                    )
                )

                sha_link = "`{short_sha}`_)".format(
                    short_sha=commit_def["sha"][:7],
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

                # COMMENTED out for v10 as the defualt changelog now only writes the subject line
                # if len(descriptions) > 1:
                #     commit_cl_desc += (
                #         "\n" + str.join("\n\n", [*descriptions[1:]]) + "\n"
                #     )

                # Add commits to section
                if commit_cl_desc not in section_bullets:
                    section_bullets.append(commit_cl_desc)

            version_entry.extend(sorted(section_bullets))

            urls.extend(
                [
                    *[
                        ".. _{mr}: {mr_url}".format(
                            mr=commit_def["mr"],
                            mr_url=hvcs.pull_request_url(commit_def["mr"]),
                        )
                        for commit_def in commits
                        if commit_def["mr"]
                    ],
                    *[
                        ".. _{short_sha}: {commit_url}".format(
                            short_sha=commit_def["sha"][:7],
                            commit_url=hvcs.commit_hash_url(commit_def["sha"]),
                        )
                        for commit_def in commits
                    ],
                ]
            )

        # Add breaking changes to the end of the version entry
        if brking_descriptions:
            version_entry.append("Breaking Changes")
            version_entry.append("-" * len(version_entry[-1]) + "\n")
            version_entry.extend([*sorted(brking_descriptions), ""])

        # Add commit URLs to the end of the version entry
        version_entry.extend(sorted(set(urls)))

        if version_entry[-1] == "":
            version_entry.pop()

        return str.join("\n", version_entry) + "\n"

    def build_version_entry(
        version: VersionStr,
        version_def: RepoVersionDef,
        output_format: ChangelogOutputFormat,
        hvcs: Github | Gitlab | Gitea | Bitbucket,
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
        hvcs: Github | Gitlab | Gitea | Bitbucket,
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
        hvcs: Github | Gitlab | Gitea | Bitbucket,
        dest_file: Path | None = None,
        max_version: Version | Literal["Unreleased"] | None = None,
        output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN,
        mask_initial_release: bool = True,  # Default as of v10
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

        version_entries: list[str] = []

        repo_def: RepoDefinition = (
            repo_definition  # type: ignore[assignment]
            if max_version is None
            else reduce(
                reduce_repo_def,  # type: ignore[arg-type]
                repo_definition.items(),
                {
                    "version_limit": max_version,
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


@pytest.fixture(scope="session")
def generate_default_release_notes_from_def(  # noqa: C901
    today_date_str: str,
    get_commits_from_repo_build_def: GetCommitsFromRepoBuildDefFn,
) -> GenerateDefaultReleaseNotesFromDefFn:
    def build_version_entry_markdown(
        version: VersionStr,
        version_def: RepoVersionDef,
        hvcs: Github | Gitlab | Gitea | Bitbucket,
        license_name: str,
    ) -> str:
        version_entry = [
            f"## v{version} ({today_date_str})",
            *(
                [""]
                if not license_name
                else [
                    "",
                    f"_This release is published under the {license_name} License._",
                    "",
                ]
            ),
        ]

        changelog_sections = sorted(
            {commit["category"] for commit in version_def["commits"]}
        )

        brking_descriptions = []

        for section in changelog_sections:
            # Create Markdown section heading
            section_title = section.title() if not section.startswith(":") else section
            version_entry.append(f"### {section_title}\n")

            commits: list[CommitDef] = list(
                filter(
                    lambda commit, section=section: (  # type: ignore[arg-type]
                        commit["category"] == section
                    ),
                    version_def["commits"],
                )
            )

            section_bullets = []

            # format each commit
            for commit_def in commits:
                descriptions = commit_def["desc"].split("\n\n")
                if commit_def["brking_desc"]:
                    brking_descriptions.append(
                        "- {commit_scope}{brk_desc}".format(
                            commit_scope=(
                                f"**{commit_def['scope']}**: "
                                if commit_def["scope"]
                                else ""
                            ),
                            brk_desc=commit_def["brking_desc"].capitalize(),
                        )
                    )

                # NOTE: During release notes, we make the line length very large as the VCS
                # will handle the line wrapping for us so here we don't have to worry about it
                max_line_length = 1000

                subject_line = "- {commit_scope}{commit_desc}".format(
                    commit_desc=descriptions[0].capitalize(),
                    commit_scope=(
                        f"**{commit_def['scope']}**: " if commit_def["scope"] else ""
                    ),
                )

                mr_link = (
                    ""
                    if not commit_def["mr"]
                    else "([{mr}]({mr_url}),".format(
                        mr=commit_def["mr"],
                        mr_url=hvcs.pull_request_url(commit_def["mr"]),
                    )
                )

                sha_link = "[`{short_sha}`]({commit_url}))".format(
                    short_sha=commit_def["sha"][:7],
                    commit_url=hvcs.commit_hash_url(commit_def["sha"]),
                )
                # Add opening parenthesis if no MR link
                sha_link = sha_link if mr_link else f"({sha_link}"

                commit_cl_desc = f"{subject_line} {mr_link}".rstrip()
                if len(commit_cl_desc) > max_line_length:
                    commit_cl_desc = f"{subject_line}\n  {mr_link}".rstrip()

                if len(f"{commit_cl_desc} {sha_link}") > max_line_length:
                    commit_cl_desc = f"{commit_cl_desc}\n  {sha_link}\n"
                else:
                    commit_cl_desc = f"{commit_cl_desc} {sha_link}\n"

                # NOTE: remove this when we no longer are writing the whole commit msg (squash commits enabled)
                # if len(descriptions) > 1:
                #     commit_cl_desc += (
                #         "\n" + str.join("\n\n", [*descriptions[1:]]) + "\n"
                #     )

                # Add commits to section
                section_bullets.append(commit_cl_desc)

            version_entry.extend(sorted(section_bullets))

        # Add breaking changes to the end of the version entry
        if brking_descriptions:
            version_entry.append("### Breaking Changes\n")
            version_entry.extend([*sorted(brking_descriptions), ""])

        return str.join("\n", version_entry)

    def build_initial_version_entry_markdown(
        version: VersionStr,
        license_name: str = "",
    ) -> str:
        return str.join(
            "\n",
            [
                f"## v{version} ({today_date_str})",
                *(
                    [""]
                    if not license_name
                    else [
                        "",
                        f"_This release is published under the {license_name} License._",
                        "",
                    ]
                ),
                "- Initial Release",
                "",
            ],
        )

    def _generate_default_release_notes(
        version_actions: Sequence[RepoActions],
        hvcs: Github | Gitlab | Gitea | Bitbucket,
        previous_version: Version | None = None,
        license_name: str = "",
        dest_file: Path | None = None,
        mask_initial_release: bool = True,  # Default as of v10
    ) -> str:
        limited_repo_def: RepoDefinition = get_commits_from_repo_build_def(
            build_definition=version_actions,
            filter_4_changelog=True,
        )
        version: Version = Version.parse(next(iter(limited_repo_def.keys())))
        version_def: RepoVersionDef = limited_repo_def[str(version)]

        release_notes_content = (
            str.join(
                "\n" * 2,
                [
                    (
                        build_initial_version_entry_markdown(str(version), license_name)
                        if mask_initial_release and not previous_version
                        else build_version_entry_markdown(
                            str(version), version_def, hvcs, license_name
                        )
                    ).rstrip(),
                    *(
                        [
                            "---",
                            "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                                prev_version=previous_version.as_tag(),
                                new_version=version.as_tag(),
                                version_compare_url=hvcs.compare_url(
                                    previous_version.as_tag(), version.as_tag()
                                ),
                            ),
                        ]
                        if previous_version and not isinstance(hvcs, Gitea)
                        else []
                    ),
                ],
            ).rstrip()
            + "\n"
        )

        if dest_file is not None:
            # Converts universal newlines to the OS-specific upon write
            dest_file.write_text(release_notes_content)

        # match the line endings of the current OS
        return (
            str.join(os.linesep, release_notes_content.splitlines(keepends=False))
            + os.linesep
        )

    return _generate_default_release_notes


@pytest.fixture
def git_repo_for_directory() -> Generator[GetGitRepo4DirFn, None, None]:
    repos: list[Repo] = []

    # Must be a callable function to ensure files exist before repo is opened
    def _git_repo_4_dir(directory: Path | str) -> Repo:
        if not Path(directory).exists():
            raise RuntimeError("Unable to find git project!")

        repo = Repo(directory)
        repos.append(repo)
        return repo

    try:
        yield _git_repo_4_dir
    finally:
        for repo in repos:
            repo.close()


@pytest.fixture
def example_project_git_repo(
    example_project_dir: ExProjectDir,
    git_repo_for_directory: GetGitRepo4DirFn,
) -> ExProjectGitRepoFn:
    def _example_project_git_repo() -> Repo:
        return git_repo_for_directory(example_project_dir)

    return _example_project_git_repo
