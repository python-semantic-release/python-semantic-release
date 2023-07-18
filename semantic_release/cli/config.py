from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

from git import Actor
from git.repo.base import Repo
from jinja2 import Environment
from pydantic import BaseModel
from typing_extensions import Literal

from semantic_release.changelog import environment
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.masking_filter import MaskingFilter
from semantic_release.commit_parser import (
    AngularCommitParser,
    CommitParser,
    EmojiCommitParser,
    ParseResult,
    ParserOptions,
    ScipyCommitParser,
    TagCommitParser,
)
from semantic_release.const import COMMIT_MESSAGE, DEFAULT_COMMIT_AUTHOR, SEMVER_REGEX
from semantic_release.errors import InvalidConfiguration, NotAReleaseBranch
from semantic_release.helpers import dynamic_import
from semantic_release.hvcs import Gitea, Github, Gitlab, HvcsBase
from semantic_release.version import VersionTranslator
from semantic_release.version.declaration import (
    PatternVersionDeclaration,
    TomlVersionDeclaration,
    VersionDeclarationABC,
)

log = logging.getLogger(__name__)


class HvcsClient(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"


class EnvConfigVar(BaseModel):
    env: str
    default: Optional[str] = None
    default_env: Optional[str] = None

    def getvalue(self) -> Optional[str]:
        return os.getenv(self.env, os.getenv(self.default_env or "", self.default))


MaybeFromEnv = Union[EnvConfigVar, str]


class ChangelogEnvironmentConfig(BaseModel):
    block_start_string: str = "{%"
    block_end_string: str = "%}"
    variable_start_string: str = "{{"
    variable_end_string: str = "}}"
    comment_start_string: str = "{#"
    comment_end_string: str = "#}"
    line_statement_prefix: Optional[str] = None
    line_comment_prefix: Optional[str] = None
    trim_blocks: bool = False
    lstrip_blocks: bool = False
    newline_sequence: Literal["\n", "\r", "\r\n"] = "\n"
    keep_trailing_newline: bool = False
    extensions: Tuple[str, ...] = ()
    autoescape: Union[bool, str] = True


class ChangelogConfig(BaseModel):
    template_dir: str = "templates"
    changelog_file: str = "CHANGELOG.md"
    exclude_commit_patterns: Tuple[str, ...] = ()
    environment: ChangelogEnvironmentConfig = ChangelogEnvironmentConfig()


class BranchConfig(BaseModel):
    match: str = "(main|master)"
    prerelease_token = "rc"
    prerelease: bool = False


class RemoteConfig(BaseModel):
    name: str = "origin"
    token: MaybeFromEnv = EnvConfigVar(env="GH_TOKEN")
    url: Optional[MaybeFromEnv] = None
    type: HvcsClient = HvcsClient.GITHUB
    domain: Optional[str] = None
    api_domain: Optional[str] = None
    ignore_token_for_push: bool = False


class PublishConfig(BaseModel):
    dist_glob_patterns: Tuple[str, ...] = ("dist/*",)
    upload_to_vcs_release: bool = True


class RawConfig(BaseModel):
    assets: List[str] = []
    branches: Dict[str, BranchConfig] = {"main": BranchConfig()}
    build_command: Optional[str] = None
    changelog: ChangelogConfig = ChangelogConfig()
    commit_author: MaybeFromEnv = EnvConfigVar(
        env="GIT_COMMIT_AUTHOR", default=DEFAULT_COMMIT_AUTHOR
    )
    commit_message: str = COMMIT_MESSAGE
    commit_parser: str = "angular"
    # It's up to the parser_options() method to validate these
    commit_parser_options: Dict[str, Any] = {
        "allowed_tags": [
            "build",
            "chore",
            "ci",
            "docs",
            "feat",
            "fix",
            "perf",
            "style",
            "refactor",
            "test",
        ],
        "minor_tags": ["feat"],
        "patch_tags": ["fix", "perf"],
    }
    logging_use_named_masks: bool = False
    major_on_zero: bool = True
    remote: RemoteConfig = RemoteConfig()
    tag_format: str = "v{version}"
    publish: PublishConfig = PublishConfig()
    version_toml: Optional[Tuple[str, ...]] = None
    version_variables: Optional[Tuple[str, ...]] = None


@dataclass
class GlobalCommandLineOptions:
    """
    A dataclass to hold all the command line options that
    should be set in the RuntimeContext
    """

    noop: bool = False
    verbosity: int = 0
    config_file: str = DEFAULT_CONFIG_FILE
    strict: bool = False


######
# RuntimeContext
######
# This is what we want to attach to `click.Context.obj`
# There are currently no defaults here - this is on purpose,
# the defaults should be specified and handled by `RawConfig`.
# When this is constructed we should know exactly what the user
# wants
def _recursive_getattr(obj: Any, path: str) -> Any:
    """
    Used to find nested parts of RuntimeContext which
    might contain sensitive data. Returns None if an attribute
    is missing
    """
    out = obj
    for part in path.split("."):
        out = getattr(out, part, None)
    return out


_known_commit_parsers = {
    "angular": AngularCommitParser,
    "emoji": EmojiCommitParser,
    "scipy": ScipyCommitParser,
    "tag": TagCommitParser,
}

_known_hvcs = {
    HvcsClient.GITHUB: Github,
    HvcsClient.GITLAB: Gitlab,
    HvcsClient.GITEA: Gitea,
}


@dataclass
class RuntimeContext:
    _mask_attrs_: ClassVar[List[str]] = ["hvcs_client.token"]

    repo: Repo
    commit_parser: CommitParser[ParseResult, ParserOptions]
    version_translator: VersionTranslator
    major_on_zero: bool
    prerelease: bool
    assets: List[str]
    commit_author: Actor
    commit_message: str
    changelog_excluded_commit_patterns: Tuple[re.Pattern[str], ...]
    version_declarations: Tuple[VersionDeclarationABC, ...]
    hvcs_client: HvcsBase
    changelog_file: Path
    ignore_token_for_push: bool
    template_environment: Environment
    template_dir: str
    build_command: Optional[str]
    dist_glob_patterns: Tuple[str, ...]
    upload_to_vcs_release: bool
    global_cli_options: GlobalCommandLineOptions
    # This way the filter can be passed around if needed, so that another function
    # can accept the filter as an argument and call
    masker: MaskingFilter

    @staticmethod
    def resolve_from_env(param: Optional[MaybeFromEnv]) -> Optional[str]:
        if isinstance(param, EnvConfigVar):
            return param.getvalue()
        return param

    @staticmethod
    def select_branch_options(
        choices: Dict[str, BranchConfig], active_branch: str
    ) -> BranchConfig:
        for group, options in choices.items():
            if re.match(options.match, active_branch):
                log.info(
                    "Using group %r options, as %r matches %r",
                    group,
                    options.match,
                    active_branch,
                )
                return options
            log.debug(
                "Rejecting group %r as %r doesn't match %r",
                group,
                options.match,
                active_branch,
            )
        else:
            raise NotAReleaseBranch(
                f"branch {active_branch!r} isn't in any release groups; no release will be made"
            )

    def apply_log_masking(self, masker: MaskingFilter) -> MaskingFilter:
        for attr in self._mask_attrs_:
            masker.add_mask_for(str(_recursive_getattr(self, attr)), f"context.{attr}")
            masker.add_mask_for(repr(_recursive_getattr(self, attr)), f"context.{attr}")
        return masker

    @classmethod
    def from_raw_config(
        cls, raw: RawConfig, repo: Repo, global_cli_options: GlobalCommandLineOptions
    ) -> RuntimeContext:
        ##
        # credentials masking for logging
        masker = MaskingFilter(_use_named_masks=raw.logging_use_named_masks)
        # branch-specific configuration
        branch_config = cls.select_branch_options(raw.branches, repo.active_branch.name)
        # commit_parser
        commit_parser_cls = (
            _known_commit_parsers[raw.commit_parser]
            if raw.commit_parser in _known_commit_parsers
            else dynamic_import(raw.commit_parser)
        )

        commit_parser = commit_parser_cls(
            options=commit_parser_cls.parser_options(**raw.commit_parser_options)
        )

        # We always exclude PSR's own release commits from the Changelog
        # when parsing commits
        _psr_release_commit_re = re.compile(
            raw.commit_message.replace(r"{version}", r"(?P<version>.*)")
        )
        changelog_excluded_commit_patterns = (
            _psr_release_commit_re,
            *(re.compile(pattern) for pattern in raw.changelog.exclude_commit_patterns),
        )

        _commit_author_str = cls.resolve_from_env(raw.commit_author) or ""
        _commit_author_valid = Actor.name_email_regex.match(_commit_author_str)
        if not _commit_author_valid:
            raise ValueError(
                f"Invalid git author: {_commit_author_str} should match {Actor.name_email_regex}"
            )

        commit_author = Actor(*_commit_author_valid.groups())

        version_declarations: List[VersionDeclarationABC] = []
        for decl in () if raw.version_toml is None else raw.version_toml:
            try:
                path, search_text = decl.split(":", maxsplit=1)
                # VersionDeclarationABC handles path existence check
                vd = TomlVersionDeclaration(path, search_text)
            except ValueError as exc:
                log.error("Invalid TOML declaration %r", decl, exc_info=True)
                raise InvalidConfiguration(
                    f"Invalid TOML declaration {decl!r}"
                ) from exc

            version_declarations.append(vd)

        for decl in () if raw.version_variables is None else raw.version_variables:
            try:
                path, variable = decl.split(":", maxsplit=1)
                # VersionDeclarationABC handles path existence check
                search_text = rf"(?x){variable}\s*(:=|[:=])\s*(?P<quote>['\"])(?P<version>{SEMVER_REGEX.pattern})(?P=quote)"
                pd = PatternVersionDeclaration(path, search_text)
            except ValueError as exc:
                log.error("Invalid variable declaration %r", decl, exc_info=True)
                raise InvalidConfiguration(
                    f"Invalid variable declaration {decl!r}"
                ) from exc

            version_declarations.append(pd)

        # hvcs_client
        hvcs_client_cls = _known_hvcs[raw.remote.type]
        raw_remote_url = raw.remote.url
        resolved_remote_url = cls.resolve_from_env(raw_remote_url)
        remote_url = (
            resolved_remote_url
            if resolved_remote_url is not None
            else repo.remote(raw.remote.name).url
        )

        token = cls.resolve_from_env(raw.remote.token)
        if isinstance(raw.remote.token, EnvConfigVar) and not token:
            log.warning(
                "the token for the remote VCS is configured as stored in the %s environment variable, but it is empty",
                raw.remote.token.env,
            )
        elif not token:
            log.debug("hvcs token is not set")

        hvcs_client = hvcs_client_cls(
            remote_url=remote_url,
            hvcs_domain=cls.resolve_from_env(raw.remote.domain),
            hvcs_api_domain=cls.resolve_from_env(raw.remote.api_domain),
            token=token,
        )

        # changelog_file
        changelog_file = Path(raw.changelog.changelog_file).resolve()

        template_environment = environment(
            template_dir=raw.changelog.template_dir, **raw.changelog.environment.dict()
        )

        # version_translator
        version_translator = VersionTranslator(
            tag_format=raw.tag_format, prerelease_token=branch_config.prerelease_token
        )

        self = cls(
            repo=repo,
            commit_parser=commit_parser,
            version_translator=version_translator,
            major_on_zero=raw.major_on_zero,
            build_command=raw.build_command,
            version_declarations=tuple(version_declarations),
            hvcs_client=hvcs_client,
            changelog_file=changelog_file,
            assets=raw.assets,
            commit_author=commit_author,
            commit_message=raw.commit_message,
            changelog_excluded_commit_patterns=changelog_excluded_commit_patterns,
            prerelease=branch_config.prerelease,
            ignore_token_for_push=raw.remote.ignore_token_for_push,
            template_dir=raw.changelog.template_dir,
            template_environment=template_environment,
            dist_glob_patterns=raw.publish.dist_glob_patterns,
            upload_to_vcs_release=raw.publish.upload_to_vcs_release,
            global_cli_options=global_cli_options,
            masker=masker,
        )
        # credential masker
        self.apply_log_masking(self.masker)

        return self
