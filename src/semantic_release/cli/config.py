from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass, is_dataclass
from enum import Enum
from functools import reduce
from pathlib import Path
from re import (
    Pattern,
    compile as regexp,
    error as RegExpError,  # noqa: N812
    escape as regex_escape,
)
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple, Type, Union

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
import tomlkit
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
from typing_extensions import Annotated, Self
from urllib3.util.url import parse_url

import semantic_release.hvcs as hvcs
from semantic_release.changelog.context import ChangelogMode
from semantic_release.changelog.template import environment
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.masking_filter import MaskingFilter
from semantic_release.commit_parser import (
    AngularCommitParser,
    CommitParser,
    ConventionalCommitMonorepoParser,
    ConventionalCommitParser,
    EmojiCommitParser,
    ParseResult,
    ParserOptions,
    ScipyCommitParser,
    TagCommitParser,
)
from semantic_release.const import COMMIT_MESSAGE, DEFAULT_COMMIT_AUTHOR
from semantic_release.errors import (
    DetachedHeadGitError,
    InvalidConfiguration,
    MissingGitRemote,
    NotAReleaseBranch,
    ParserLoadError,
)
from semantic_release.globals import logger
from semantic_release.helpers import dynamic_import
from semantic_release.version.declarations.file import FileVersionDeclaration
from semantic_release.version.declarations.i_version_replacer import IVersionReplacer
from semantic_release.version.declarations.pattern import PatternVersionDeclaration
from semantic_release.version.declarations.toml import TomlVersionDeclaration
from semantic_release.version.translator import VersionTranslator

NonEmptyString = Annotated[str, Field(..., min_length=1)]


class HvcsClient(str, Enum):
    BITBUCKET = "bitbucket"
    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"


_known_commit_parsers: dict[str, type[CommitParser[Any, Any]]] = {
    "angular": AngularCommitParser,
    "conventional": ConventionalCommitParser,
    "conventional-monorepo": ConventionalCommitMonorepoParser,
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


class ChangelogOutputFormat(str, Enum):
    """Supported changelog output formats when using the default templates."""

    MARKDOWN = "md"
    RESTRUCTURED_TEXT = "rst"
    NONE = ""


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
    autoescape: Union[bool, str] = False


class DefaultChangelogTemplatesConfig(BaseModel):
    changelog_file: str = "CHANGELOG.md"
    output_format: ChangelogOutputFormat = ChangelogOutputFormat.NONE
    mask_initial_release: bool = True

    @model_validator(mode="after")
    def interpret_output_format(self) -> Self:
        # Set the output format value when no user input is given
        if self.output_format == ChangelogOutputFormat.NONE:
            try:
                # Note: If the user gave no extension, force '.' so enumeration fails,
                # and defaults to markdown
                # Otherwise normal files with extensions will just look for the extension support
                self.output_format = ChangelogOutputFormat(
                    Path(self.changelog_file).suffix.lstrip(".") or "."
                )
            except ValueError:
                self.output_format = ChangelogOutputFormat.MARKDOWN

        return self


class ChangelogConfig(BaseModel):
    # TODO: BREAKING CHANGE v11, move to DefaultChangelogTemplatesConfig
    changelog_file: str = ""
    """Deprecated! Moved to 'default_templates.changelog_file'"""

    default_templates: DefaultChangelogTemplatesConfig = (
        DefaultChangelogTemplatesConfig(output_format=ChangelogOutputFormat.NONE)
    )
    environment: ChangelogEnvironmentConfig = ChangelogEnvironmentConfig()
    exclude_commit_patterns: Tuple[str, ...] = ()
    mode: ChangelogMode = ChangelogMode.UPDATE
    insertion_flag: str = ""
    template_dir: str = "templates"

    @field_validator("exclude_commit_patterns", mode="after")
    @classmethod
    def validate_match(cls, patterns: Tuple[str, ...]) -> Tuple[str, ...]:
        curr_index = 0
        try:
            for i, pattern in enumerate(patterns):
                curr_index = i
                regexp(pattern)
        except RegExpError as err:
            raise ValueError(
                f"exclude_commit_patterns[{curr_index}]: Invalid regular expression"
            ) from err
        return patterns

    @field_validator("changelog_file", mode="after")
    @classmethod
    def changelog_file_deprecation_warning(cls, val: str) -> str:
        logger.warning(
            str.join(
                " ",
                [
                    "The 'changelog.changelog_file' configuration option is moving to 'changelog.default_templates.changelog_file'.",
                    "Please update your configuration as the compatibility will break in v10.",
                ],
            )
        )
        return val

    @model_validator(mode="after")
    def move_changelog_file(self) -> Self:
        # TODO: Remove this method in v11
        if not self.changelog_file:
            return self

        if self.changelog_file == self.default_templates.changelog_file:
            return self

        # Re-evaluate now that we are passing the changelog_file option down to default_templates
        # and only reset the output_format if it was not already set by the user
        self.default_templates = DefaultChangelogTemplatesConfig.model_validate(
            {
                **self.default_templates.model_dump(),
                "changelog_file": self.changelog_file,
                "output_format": (
                    self.default_templates.output_format
                    if self.default_templates.output_format
                    != ChangelogOutputFormat.MARKDOWN
                    else ChangelogOutputFormat.NONE
                ),
            }
        )

        return self

    @model_validator(mode="after")
    def load_default_insertion_flag_on_missing(self) -> Self:
        # Set the insertion flag value when no user input is given
        if not self.insertion_flag:
            defaults = {
                ChangelogOutputFormat.MARKDOWN: "<!-- version list -->",
                ChangelogOutputFormat.RESTRUCTURED_TEXT: f"..{os.linesep}    version list",
            }
            try:
                self.insertion_flag = defaults[self.default_templates.output_format]
            except KeyError as err:
                raise ValueError(
                    "changelog.default_templates.output_format cannot be None"
                ) from err

        return self


class BranchConfig(BaseModel):
    match: str = "(main|master)"
    prerelease_token: str = "rc"  # noqa: S105
    prerelease: bool = False

    @field_validator("match", mode="after")
    @classmethod
    def validate_match(cls, match: str) -> str:
        # Allow the special case of a plain wildcard although it's not a valid regex
        if match == "*":
            return ".*"

        try:
            regexp(match)
        except RegExpError as err:
            raise ValueError(f"Invalid regex {match!r}") from err
        return match


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
        if self.token:
            return self
        if self.type not in _known_hvcs:
            return self
        if env_token := self._get_default_token():
            self.token = env_token
        return self

    def _get_default_token(self) -> str | None:
        hvcs_client_class = _known_hvcs[self.type]

        default_token_name = (
            getattr(hvcs_client_class, "DEFAULT_ENV_TOKEN_NAME")  # noqa: B009
            if hasattr(hvcs_client_class, "DEFAULT_ENV_TOKEN_NAME")
            else ""
        )

        return (
            EnvConfigVar(env=default_token_name).getvalue()
            if default_token_name
            else None
        )

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
            logger.warning(
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
    commit_parser: NonEmptyString = "conventional"
    # It's up to the parser_options() method to validate these
    commit_parser_options: Dict[str, Any] = {}
    logging_use_named_masks: bool = False
    major_on_zero: bool = True
    allow_zero_version: bool = False
    repo_dir: Annotated[Path, Field(validate_default=True)] = Path(".")
    remote: RemoteConfig = RemoteConfig()
    no_git_verify: bool = False
    tag_format: str = "v{version}"
    add_partial_tags: bool = False
    publish: PublishConfig = PublishConfig()
    version_toml: Optional[Tuple[str, ...]] = None
    version_variables: Optional[Tuple[str, ...]] = None

    @field_validator("repo_dir", mode="before")
    @classmethod
    def convert_str_to_path(cls, value: Any) -> Path:
        if not isinstance(value, (str, Path)):
            raise TypeError(f"Invalid type: {type(value)}, expected str or Path.")
        return Path(value)

    @field_validator("repo_dir", mode="after")
    @classmethod
    def verify_git_repo_dir(cls, dir_path: Path) -> Path:
        try:
            # Check for repository & walk up parent directories
            with Repo(str(dir_path), search_parent_directories=True) as git_repo:
                found_path = (
                    Path(git_repo.working_tree_dir or git_repo.working_dir)
                    .expanduser()
                    .absolute()
                )

        except InvalidGitRepositoryError as err:
            raise InvalidGitRepositoryError("No valid git repository found!") from err

        if dir_path.absolute() != found_path:
            logging.warning(
                "Found .git/ in higher parent directory rather than provided in configuration."
            )

        return found_path.resolve()

    @field_validator("commit_parser", mode="after")
    @classmethod
    def tag_commit_parser_deprecation_warning(cls, val: str) -> str:
        if val == "tag":
            logger.warning(
                str.join(
                    " ",
                    [
                        "The legacy 'tag' parser is deprecated and will be removed in v11.",
                        "Recommend swapping to our emoji parser (higher-compatibility)",
                        "or switch to another supported parser.",
                    ],
                )
            )
        return val

    @field_validator("commit_parser", mode="after")
    @classmethod
    def angular_commit_parser_deprecation_warning(cls, val: str) -> str:
        if val == "angular":
            logger.warning(
                str.join(
                    " ",
                    [
                        "The 'angular' parser is deprecated and will be removed in v11.",
                        "The Angular parser is being renamed to the conventional commit parser,",
                        "which is selected by switching the 'commit_parser' value to 'conventional'.",
                    ],
                )
            )
        return val

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
                # TODO: BREAKING CHANGE v11
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
                    # TODO: BREAKING CHANGE v11
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

    project_metadata: dict[str, Any]
    repo_dir: Path
    commit_parser: CommitParser[ParseResult, ParserOptions]
    version_translator: VersionTranslator
    major_on_zero: bool
    allow_zero_version: bool
    prerelease: bool
    no_git_verify: bool
    assets: List[str]
    commit_author: Actor
    commit_message: str
    changelog_excluded_commit_patterns: Tuple[Pattern[str], ...]
    version_declarations: Tuple[IVersionReplacer, ...]
    hvcs_client: hvcs.HvcsBase
    changelog_insertion_flag: str
    changelog_mask_initial_release: bool
    changelog_mode: ChangelogMode
    changelog_file: Path
    changelog_style: str
    changelog_output_format: ChangelogOutputFormat
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
            if regexp(options.match).match(active_branch):
                logger.info(
                    "Using group %r options, as %r matches %r",
                    group,
                    options.match,
                    active_branch,
                )
                return options
            logger.debug(
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
    def from_raw_config(  # noqa: C901
        cls, raw: RawConfig, global_cli_options: GlobalCommandLineOptions
    ) -> RuntimeContext:
        ##
        # credentials masking for logging
        masker = MaskingFilter(_use_named_masks=raw.logging_use_named_masks)

        # TODO: move to config if we change how the generated config is constructed
        # Retrieve project metadata from pyproject.toml
        project_metadata: dict[str, str] = {}
        curr_dir = Path.cwd().resolve()
        allowed_directories = [
            dir_path
            for dir_path in [curr_dir, *curr_dir.parents]
            if str(raw.repo_dir) in str(dir_path)
        ]
        for allowed_dir in allowed_directories:
            if (proj_toml := allowed_dir.joinpath("pyproject.toml")).exists():
                config_toml = tomlkit.parse(proj_toml.read_text())
                project_metadata = config_toml.unwrap().get("project", project_metadata)
                break

        # Retrieve details from repository
        with Repo(str(raw.repo_dir)) as git_repo:
            try:
                # Get the remote url by calling out to `git remote get-url`. This returns
                # the expanded url, taking into account any insteadOf directives
                # in the git configuration.
                remote_url = raw.remote.url or git_repo.git.remote(
                    "get-url", raw.remote.name
                )
                active_branch = git_repo.active_branch.name
            except ValueError as err:
                raise MissingGitRemote(
                    f"Unable to locate remote named '{raw.remote.name}'."
                ) from err
            except TypeError as err:
                raise DetachedHeadGitError(
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
        except ValueError as err:
            raise ParserLoadError(
                str.join(
                    "\n",
                    [
                        f"Unrecognized commit parser value: {raw.commit_parser!r}.",
                        str(err),
                        "Unable to load the given parser! Check your configuration!",
                    ],
                )
            ) from err
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
        # TODO: Breaking change v11
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
        psr_release_commit_regex = regexp(
            reduce(
                lambda regex_str, pattern: str(regex_str).replace(*pattern),
                (
                    # replace the version holder with a regex pattern to match various versions
                    (regex_escape("{version}"), r"(?P<version>\d+\.\d+\.\d+\S*)"),
                    # TODO: add any other placeholders here
                ),
                # We use re.escape to ensure that the commit message is treated as a literal
                regex_escape(raw.commit_message.strip()),
            )
        )
        changelog_excluded_commit_patterns = (
            psr_release_commit_regex,
            *(regexp(pattern) for pattern in raw.changelog.exclude_commit_patterns),
        )

        _commit_author_str = cls.resolve_from_env(raw.commit_author) or ""
        _commit_author_valid = Actor.name_email_regex.match(_commit_author_str)
        if not _commit_author_valid:
            raise ValueError(
                f"Invalid git author: {_commit_author_str} "
                f"should match {Actor.name_email_regex}"
            )

        commit_author = Actor(*_commit_author_valid.groups())

        version_declarations: list[IVersionReplacer] = []

        try:
            version_declarations.extend(
                TomlVersionDeclaration.from_string_definition(definition)
                for definition in iter(raw.version_toml or ())
            )
        except ValueError as err:
            raise InvalidConfiguration(
                str.join(
                    "\n",
                    [
                        "Invalid 'version_toml' configuration",
                        str(err),
                    ],
                )
            ) from err

        try:
            for definition in iter(raw.version_variables or ()):
                # Check if this is a file replacement definition (pattern is "*")
                parts = definition.split(":", maxsplit=2)
                if len(parts) >= 2 and parts[1] == "*":
                    # Use FileVersionDeclaration for entire file replacement
                    version_declarations.append(
                        FileVersionDeclaration.from_string_definition(definition)
                    )
                    continue

                # Use PatternVersionDeclaration for pattern-based replacement
                version_declarations.append(
                    PatternVersionDeclaration.from_string_definition(
                        definition, raw.tag_format
                    )
                )
        except ValueError as err:
            raise InvalidConfiguration(
                str.join(
                    "\n",
                    [
                        "Invalid 'version_variables' configuration",
                        str(err),
                    ],
                )
            ) from err

        # Provide warnings if the token is missing
        if not raw.remote.token:
            logger.debug("hvcs token is not set")

            if not raw.remote.ignore_token_for_push:
                logger.warning("Token value is missing!")

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
        # Must use absolute after resolve because windows does not resolve if the path does not exist
        # which means it returns a relative path. So we force absolute to ensure path is complete
        # for the next check of path matching
        changelog_file = (
            Path(raw.changelog.default_templates.changelog_file)
            .expanduser()
            .resolve()
            .absolute()
        )

        # Prevent path traversal attacks
        if raw.repo_dir not in changelog_file.parents:
            raise InvalidConfiguration(
                "Changelog file destination must be inside of the repository directory."
            )

        # Must use absolute after resolve because windows does not resolve if the path does not exist
        # which means it returns a relative path. So we force absolute to ensure path is complete
        # for the next check of path matching
        template_dir = (
            Path(raw.changelog.template_dir).expanduser().resolve().absolute()
        )

        # Prevent path traversal attacks
        if raw.repo_dir not in template_dir.parents:
            raise InvalidConfiguration(
                "Template directory must be inside of the repository directory."
            )

        template_environment = environment(
            template_dir=template_dir,
            **raw.changelog.environment.model_dump(),
        )

        # version_translator
        version_translator = VersionTranslator(
            tag_format=raw.tag_format,
            prerelease_token=branch_config.prerelease_token,
            add_partial_tags=raw.add_partial_tags,
        )

        build_cmd_env = {}

        for i, env_var_def in enumerate(raw.build_command_env):
            # creative hack to handle, missing =, but also = that then can be unpacked
            # as the resulting parts array can be either 2 or 3 in length. it becomes 3
            # with our forced empty value at the end which can be dropped
            parts = [*env_var_def.split("=", 1), ""]
            # removes any odd spacing around =, and extracts name=value
            name, env_val = (part.strip() for part in parts[:2])

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

        # TODO: better support for custom parsers that actually just extend defaults
        #
        # Here we just assume the desired changelog style matches the parser name
        # as we provide templates specific to each parser type. Unfortunately if the user has
        # provided a custom parser, it would be up to the user to provide custom templates
        # but we just assume the base template is conventional
        # changelog_style = (
        #     raw.commit_parser
        #     if raw.commit_parser in _known_commit_parsers
        #     else "conventional"
        # )

        self = cls(
            project_metadata=project_metadata,
            repo_dir=raw.repo_dir,
            commit_parser=commit_parser,
            version_translator=version_translator,
            major_on_zero=raw.major_on_zero,
            allow_zero_version=raw.allow_zero_version,
            build_command=raw.build_command,
            build_command_env=build_cmd_env,
            version_declarations=tuple(version_declarations),
            hvcs_client=hvcs_client,
            changelog_file=changelog_file,
            changelog_mode=raw.changelog.mode,
            changelog_mask_initial_release=raw.changelog.default_templates.mask_initial_release,
            changelog_insertion_flag=raw.changelog.insertion_flag,
            assets=raw.assets,
            commit_author=commit_author,
            commit_message=raw.commit_message,
            changelog_excluded_commit_patterns=changelog_excluded_commit_patterns,
            # TODO: change when we have other styles per parser
            # changelog_style=changelog_style,
            changelog_style="conventional",
            changelog_output_format=raw.changelog.default_templates.output_format,
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
