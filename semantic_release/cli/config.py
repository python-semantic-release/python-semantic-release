from __future__ import annotations

import logging
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple, Type, Union

from git import Actor, InvalidGitRepositoryError
from git.repo.base import Repo
from jinja2 import Environment
from pydantic import (
    BaseModel,
    Field,
    RootModel,
    ValidationError,
    field_validator,
    model_validator,
)

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
from typing_extensions import Annotated, Self
from urllib3.util.url import parse_url

from semantic_release import hvcs
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
from semantic_release.errors import (
    InvalidConfiguration,
    NotAReleaseBranch,
    ParserLoadError,
)
from semantic_release.helpers import dynamic_import
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.version import VersionTranslator
from semantic_release.version.declaration import (
    PatternVersionDeclaration,
    TomlVersionDeclaration,
    VersionDeclarationABC,
)

log = logging.getLogger(__name__)
NonEmptyString = Annotated[str, Field(..., min_length=1)]


class HvcsClient(str, Enum):
    BITBUCKET = "bitbucket"
    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"


_known_commit_parsers: Dict[str, type[CommitParser]] = {
    "angular": AngularCommitParser,
    "emoji": EmojiCommitParser,
    "scipy": ScipyCommitParser,
    "tag": TagCommitParser,
}


_known_hvcs: Dict[HvcsClient, Type[hvcs.HvcsBase]] = {
    HvcsClient.BITBUCKET: hvcs.Bitbucket,
    HvcsClient.GITHUB: hvcs.Github,
    HvcsClient.GITLAB: hvcs.Gitlab,
    HvcsClient.GITEA: hvcs.Gitea,
}


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
    prerelease_token: str = "rc"  # noqa: S105
    prerelease: bool = False


class RemoteConfig(BaseModel):
    name: str = "origin"
    token: Optional[str] = None
    url: Optional[str] = None
    type: HvcsClient = HvcsClient.GITHUB
    domain: Optional[str] = None
    api_domain: Optional[str] = None
    ignore_token_for_push: bool = False
    insecure: bool = False

    @field_validator("url", "domain", "api_domain", "token", mode="before")
    @classmethod
    def resolve_env_vars(cls, val: Any) -> str | None:
        ret_val = (
            val
            if not isinstance(val, dict)
            else (EnvConfigVar.model_validate(val).getvalue())
        )
        return ret_val or None

    @model_validator(mode="after")
    def set_default_token(self) -> Self:
        # Set the default token name for the given VCS when no user input is given
        if not self.token and self.type in _known_hvcs:
            if env_token := self._get_default_token():
                self.token = env_token
        return self

    def _get_default_token(self) -> str | None:
        hvcs_client_class = _known_hvcs[self.type]
        default_hvcs_instance = hvcs_client_class("git@example.com:owner/project.git")
        if not isinstance(default_hvcs_instance, RemoteHvcsBase):
            return None

        default_token_name = default_hvcs_instance.DEFAULT_ENV_TOKEN_NAME
        if not default_token_name:
            return None

        return EnvConfigVar(env=default_token_name).getvalue()

    @model_validator(mode="after")
    def check_url_scheme(self) -> Self:
        if self.url and isinstance(self.url, str):
            self.check_insecure_flag(self.url, "url")

        if self.domain and isinstance(self.domain, str):
            self.check_insecure_flag(self.domain, "domain")

        if self.api_domain and isinstance(self.api_domain, str):
            self.check_insecure_flag(self.api_domain, "api_domain")

        return self

    def check_insecure_flag(self, url_str: str, field_name: str) -> None:
        if not url_str:
            return

        scheme = parse_url(url_str).scheme
        if scheme == "http" and not self.insecure:
            raise ValueError(
                str.join(
                    "\n",
                    [
                        "Insecure 'HTTP' URL detected and disabled by default.",
                        "Set the 'insecure' flag to 'True' to enable insecure connections.",
                    ],
                )
            )

        if scheme == "https" and self.insecure:
            log.warning(
                str.join(
                    "\n",
                    [
                        f"'{field_name}' starts with 'https://' but the 'insecure' flag is set.",
                        "This flag is only necessary for 'http://' URLs.",
                    ],
                )
            )


class PublishConfig(BaseModel):
    dist_glob_patterns: Tuple[str, ...] = ("dist/*",)
    upload_to_vcs_release: bool = True


class RawConfig(BaseModel):
    assets: List[str] = []
    branches: Dict[str, BranchConfig] = {"main": BranchConfig()}
    build_command: Optional[str] = None
    build_command_env: List[str] = []
    changelog: ChangelogConfig = ChangelogConfig()
    commit_author: MaybeFromEnv = EnvConfigVar(
        env="GIT_COMMIT_AUTHOR", default=DEFAULT_COMMIT_AUTHOR
    )
    commit_message: str = COMMIT_MESSAGE
    commit_parser: NonEmptyString = "angular"
    # It's up to the parser_options() method to validate these
    commit_parser_options: Dict[str, Any] = {}
    logging_use_named_masks: bool = False
    major_on_zero: bool = True
    allow_zero_version: bool = True
    remote: RemoteConfig = RemoteConfig()
    no_git_verify: bool = False
    tag_format: str = "v{version}"
    publish: PublishConfig = PublishConfig()
    version_toml: Optional[Tuple[str, ...]] = None
    version_variables: Optional[Tuple[str, ...]] = None

    @field_validator("build_command_env", mode="after")
    @classmethod
    def remove_whitespace(cls, val: list[str]) -> list[str]:
        return [entry.strip() for entry in val]

    @model_validator(mode="after")
    def set_default_opts(self) -> Self:
        # Set the default parser options for the given commit parser when no user input is given
        if not self.commit_parser_options and self.commit_parser:
            parser_opts_type = None
            # If the commit parser is a known one, pull the default options object from it
            if self.commit_parser in _known_commit_parsers:
                # TODO: BREAKING CHANGE v10
                # parser_opts_type = (
                #     _known_commit_parsers[self.commit_parser]
                #     .get_default_options()
                #     .__class__
                # )
                parser_opts_type = _known_commit_parsers[
                    self.commit_parser
                ].parser_options
            else:
                try:
                    # if its a custom parser, try to import it and pull the default options object type
                    custom_class = dynamic_import(self.commit_parser)
                    # TODO: BREAKING CHANGE v10
                    # parser_opts_type = custom_class.get_default_options().__class__
                    if hasattr(custom_class, "parser_options"):
                        parser_opts_type = custom_class.parser_options

                except ModuleNotFoundError as err:
                    raise ParserLoadError(
                        str.join(
                            "\n",
                            [
                                str(err),
                                "Unable to import your custom parser! Check your configuration!",
                            ],
                        )
                    ) from err

                except AttributeError as err:
                    raise ParserLoadError(
                        str.join(
                            "\n",
                            [
                                str(err),
                                "Unable to find your custom parser class inside the given module.",
                                "Check your configuration!",
                            ],
                        )
                    ) from err

            # from either the custom opts class or the known parser opts class, create an instance
            if callable(parser_opts_type):
                opts_obj: Any = parser_opts_type()
                # if the opts object is a dataclass, wrap it in a RootModel so it can be transformed to a Mapping
                opts_obj = (
                    opts_obj if not is_dataclass(opts_obj) else RootModel(opts_obj)
                )
                # Must be a mapping, so if it's a BaseModel, dump the model to a dict
                self.commit_parser_options = (
                    opts_obj.model_dump()
                    if isinstance(opts_obj, (BaseModel, RootModel))
                    else opts_obj
                )
                if not isinstance(self.commit_parser_options, Mapping):
                    raise ValidationError(
                        f"Invalid parser options: {opts_obj}. Must be a mapping."
                    )

        return self


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


@dataclass
class RuntimeContext:
    _mask_attrs_: ClassVar[List[str]] = ["hvcs_client.token"]

    repo: Repo
    commit_parser: CommitParser[ParseResult, ParserOptions]
    version_translator: VersionTranslator
    major_on_zero: bool
    allow_zero_version: bool
    prerelease: bool
    no_git_verify: bool
    assets: List[str]
    commit_author: Actor
    commit_message: str
    changelog_excluded_commit_patterns: Tuple[re.Pattern[str], ...]
    version_declarations: Tuple[VersionDeclarationABC, ...]
    hvcs_client: hvcs.HvcsBase
    changelog_file: Path
    ignore_token_for_push: bool
    template_environment: Environment
    template_dir: Path
    build_command: Optional[str]
    build_command_env: dict[str, str]
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

        raise NotAReleaseBranch(
            f"branch {active_branch!r} isn't in any release groups; "
            "no release will be made"
        )

    def apply_log_masking(self, masker: MaskingFilter) -> MaskingFilter:
        for attr in self._mask_attrs_:
            masker.add_mask_for(str(_recursive_getattr(self, attr)), f"context.{attr}")
            masker.add_mask_for(repr(_recursive_getattr(self, attr)), f"context.{attr}")
        return masker

    @classmethod
    def from_raw_config(
        cls, raw: RawConfig, global_cli_options: GlobalCommandLineOptions
    ) -> RuntimeContext:
        ##
        # credentials masking for logging
        masker = MaskingFilter(_use_named_masks=raw.logging_use_named_masks)

        try:
            repo = Repo(".", search_parent_directories=True)
            active_branch = repo.active_branch.name
        except InvalidGitRepositoryError as err:
            raise InvalidGitRepositoryError("No valid git repository found!") from err
        except TypeError as err:
            raise NotAReleaseBranch(
                "Detached HEAD state cannot match any release groups; "
                "no release will be made"
            ) from err

        # branch-specific configuration
        branch_config = cls.select_branch_options(raw.branches, active_branch)

        # commit_parser
        try:
            commit_parser_cls = (
                _known_commit_parsers[raw.commit_parser]
                if raw.commit_parser in _known_commit_parsers
                else dynamic_import(raw.commit_parser)
            )
        except ModuleNotFoundError as err:
            raise ParserLoadError(
                str.join(
                    "\n",
                    [
                        str(err),
                        "Unable to import your custom parser! Check your configuration!",
                    ],
                )
            ) from err
        except AttributeError as err:
            raise ParserLoadError(
                str.join(
                    "\n",
                    [
                        str(err),
                        "Unable to find the parser class inside the given module",
                    ],
                )
            ) from err

        commit_parser_opts_class = commit_parser_cls.parser_options
        # TODO: Breaking change v10
        # commit_parser_opts_class = commit_parser_cls.get_default_options().__class__
        try:
            commit_parser = commit_parser_cls(
                options=commit_parser_opts_class(**raw.commit_parser_options)
            )
        except TypeError as err:
            raise ParserLoadError(
                str.join("\n", [str(err), f"Failed to initialize {raw.commit_parser}"])
            ) from err

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
                f"Invalid git author: {_commit_author_str} "
                f"should match {Actor.name_email_regex}"
            )

        commit_author = Actor(*_commit_author_valid.groups())

        version_declarations: list[VersionDeclarationABC] = []
        for decl in () if raw.version_toml is None else raw.version_toml:
            try:
                path, search_text = decl.split(":", maxsplit=1)
                # VersionDeclarationABC handles path existence check
                vd = TomlVersionDeclaration(path, search_text)
            except ValueError as exc:
                log.exception("Invalid TOML declaration %r", decl)
                raise InvalidConfiguration(
                    f"Invalid TOML declaration {decl!r}"
                ) from exc

            version_declarations.append(vd)

        for decl in () if raw.version_variables is None else raw.version_variables:
            try:
                path, variable = decl.split(":", maxsplit=1)
                # VersionDeclarationABC handles path existence check
                search_text = rf"(?x){variable}\s*(:=|[:=])\s*(?P<quote>['\"])(?P<version>{SEMVER_REGEX.pattern})(?P=quote)"  # noqa: E501
                pd = PatternVersionDeclaration(path, search_text)
            except ValueError as exc:
                log.exception("Invalid variable declaration %r", decl)
                raise InvalidConfiguration(
                    f"Invalid variable declaration {decl!r}"
                ) from exc

            version_declarations.append(pd)

        # Provide warnings if the token is missing
        if not raw.remote.token:
            log.debug("hvcs token is not set")

            if not raw.remote.ignore_token_for_push:
                log.warning("Token value is missing!")

        # retrieve remote url
        remote_url = raw.remote.url or repo.remote(raw.remote.name).url

        # hvcs_client
        hvcs_client_cls = _known_hvcs[raw.remote.type]
        hvcs_client = hvcs_client_cls(
            remote_url=remote_url,
            hvcs_domain=raw.remote.domain,
            hvcs_api_domain=raw.remote.api_domain,
            token=raw.remote.token,
            allow_insecure=raw.remote.insecure,
        )

        # changelog_file
        changelog_file = Path(raw.changelog.changelog_file).resolve()

        template_dir = Path(repo.working_tree_dir or ".") / raw.changelog.template_dir

        template_environment = environment(
            template_dir=raw.changelog.template_dir,
            **raw.changelog.environment.model_dump(),
        )

        # version_translator
        version_translator = VersionTranslator(
            tag_format=raw.tag_format, prerelease_token=branch_config.prerelease_token
        )

        build_cmd_env = {}

        for i, env_var_def in enumerate(raw.build_command_env):
            # creative hack to handle, missing =, but also = that then can be unpacked
            # as the resulting parts array can be either 2 or 3 in length. it becomes 3
            # with our forced empty value at the end which can be dropped
            parts = [*env_var_def.split("=", 1), ""]
            # removes any odd spacing around =, and extracts name=value
            name, env_val = [part.strip() for part in parts[:2]]

            if not name:
                # Skip when invalid format (ex. starting with = and no name)
                logging.warning(
                    "Skipping invalid build_command_env[%s] definition",
                    i,
                )
                continue

            if not env_val and env_var_def[-1] != "=":
                # avoid the edge case that user wants to define a value as empty
                # and don't autoresolve it
                env_val = os.getenv(name, "")

            build_cmd_env[name] = env_val

        self = cls(
            repo=repo,
            commit_parser=commit_parser,
            version_translator=version_translator,
            major_on_zero=raw.major_on_zero,
            allow_zero_version=raw.allow_zero_version,
            build_command=raw.build_command,
            build_command_env=build_cmd_env,
            version_declarations=tuple(version_declarations),
            hvcs_client=hvcs_client,
            changelog_file=changelog_file,
            assets=raw.assets,
            commit_author=commit_author,
            commit_message=raw.commit_message,
            changelog_excluded_commit_patterns=changelog_excluded_commit_patterns,
            prerelease=branch_config.prerelease,
            ignore_token_for_push=raw.remote.ignore_token_for_push,
            template_dir=template_dir,
            template_environment=template_environment,
            dist_glob_patterns=raw.publish.dist_glob_patterns,
            upload_to_vcs_release=raw.publish.upload_to_vcs_release,
            global_cli_options=global_cli_options,
            masker=masker,
            no_git_verify=raw.no_git_verify,
        )
        # credential masker
        self.apply_log_masking(self.masker)

        return self
