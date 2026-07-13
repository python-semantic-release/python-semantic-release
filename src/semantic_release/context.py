from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path
from re import compile as regexp, escape as regex_escape
from typing import TYPE_CHECKING, Any, Sequence

import tomlkit
from git import Actor
from git.repo.base import Repo

from semantic_release.changelog.context import ChangelogMode
from semantic_release.changelog.template import (
    environment as create_template_environment,
)
from semantic_release.cli.config import (
    ChangelogOutputFormat,
    RawConfig,
    _known_commit_parsers,
    _known_hvcs,
)
from semantic_release.cli.util import load_raw_config_file
from semantic_release.const import COMMIT_MESSAGE, DEFAULT_COMMIT_AUTHOR
from semantic_release.errors import (
    DetachedHeadGitError,
    InvalidConfiguration,
    MissingGitRemote,
    NotAReleaseBranch,
    ParserLoadError,
)
from semantic_release.helpers import dynamic_import
from semantic_release.version.declarations.pattern import PatternVersionDeclaration
from semantic_release.version.declarations.toml import TomlVersionDeclaration
from semantic_release.version.translator import VersionTranslator

if TYPE_CHECKING:  # pragma: no cover
    from re import Pattern

    from jinja2 import Environment
    from typing_extensions import Self

    from semantic_release.cli.config import BranchConfig
    from semantic_release.commit_parser import CommitParser, ParseResult, ParserOptions
    from semantic_release.hvcs import HvcsBase
    from semantic_release.version.declarations.i_version_replacer import (
        IVersionReplacer,
    )

logger = logging.getLogger(__name__)


def _build_default_commit_author() -> Actor:
    match = Actor.name_email_regex.match(DEFAULT_COMMIT_AUTHOR)
    if not match:
        raise InvalidConfiguration(
            f"Invalid default git author: {DEFAULT_COMMIT_AUTHOR} "
            f"should match {Actor.name_email_regex}"
        )
    return Actor(*match.groups())


@dataclass
class SemanticReleaseContext:
    """
    Core configuration context for semantic-release operations.

    This class holds all configuration needed for semantic release operations
    such as building release history, rendering changelogs, computing versions,
    and applying version updates.

    Users can create instances either by calling ``from_config_file()`` to load
    from pyproject.toml, or by directly instantiating with explicit parameters.
    """

    repo_dir: Path
    hvcs_client: HvcsBase
    commit_parser: CommitParser[ParseResult, ParserOptions]
    version_translator: VersionTranslator

    # Optional fields with sensible defaults
    project_metadata: dict[str, Any] = field(default_factory=dict)
    major_on_zero: bool = False
    allow_zero_version: bool = True
    prerelease: bool = False

    # Changelog settings
    changelog_file: Path = Path("CHANGELOG.md")
    changelog_mode: ChangelogMode = ChangelogMode.UPDATE
    changelog_style: str = "conventional"
    changelog_output_format: ChangelogOutputFormat = ChangelogOutputFormat.MARKDOWN
    changelog_insertion_flag: str = ""
    changelog_mask_initial_release: bool = True
    changelog_excluded_commit_patterns: tuple[Pattern[str], ...] = ()

    # Template settings
    template_dir: Path = field(default_factory=lambda: Path("templates"))
    template_environment: Environment = field(
        default_factory=lambda: create_template_environment(
            template_dir=Path("templates"),
            autoescape=False,
            newline_sequence="\n",
        )
    )

    # Version declarations
    version_declarations: tuple[IVersionReplacer, ...] = ()

    # Build/publish settings
    build_command: str | None = None
    build_command_env: dict[str, str] = field(default_factory=dict)
    dist_glob_patterns: tuple[str, ...] = ()
    upload_to_vcs_release: bool = False
    assets: list[str] = field(default_factory=list)

    # Git settings
    commit_author: Actor = field(default_factory=lambda: _build_default_commit_author())
    commit_message: str = COMMIT_MESSAGE
    no_git_verify: bool = False
    ignore_token_for_push: bool = False

    @classmethod
    def from_config_file(
        cls,
        config_file: Path | str = "pyproject.toml",
        repo_dir: Path | str | None = None,
    ) -> Self:
        """
        Load configuration from a config file and create a SemanticReleaseContext.

        This convenience method reads configuration from pyproject.toml (or another
        config file) and constructs all required objects (parser, HVCS client, etc.).

        :param config_file: Path to the configuration file. Defaults to "pyproject.toml".
        :param repo_dir: Repository directory. If not specified, uses the config's
            repo_dir or current working directory.

        :raises FileNotFoundError: If the config file doesn't exist.
        :raises InvalidConfiguration: If the configuration is invalid.
        :raises ParserLoadError: If the commit parser cannot be loaded.

        :return: A configured SemanticReleaseContext instance.
        """
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        raw_config_dict = load_raw_config_file(config_path)
        raw = RawConfig.model_validate(raw_config_dict or {})

        return cls._from_raw_config(raw, repo_dir)

    @classmethod
    def _from_raw_config(
        cls,
        raw: RawConfig,
        repo_dir: Path | str | None = None,
    ) -> Self:
        resolved_repo_dir = Path(repo_dir) if repo_dir else raw.repo_dir
        project_metadata = _load_project_metadata(resolved_repo_dir)

        with Repo(str(resolved_repo_dir)) as git_repo:
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

        branch_config = _select_branch_options(raw.branches, active_branch)
        commit_parser = _build_commit_parser(
            raw.commit_parser, raw.commit_parser_options
        )
        changelog_excluded_commit_patterns = _build_excluded_commit_patterns(
            raw.commit_message, raw.changelog.exclude_commit_patterns
        )
        commit_author = _build_commit_author(raw.commit_author)
        version_declarations = _build_version_declarations(
            raw.version_toml, raw.version_variables, raw.tag_format
        )
        hvcs_client = _build_hvcs_client(raw, remote_url)
        changelog_file = _resolve_changelog_path(
            raw.changelog.default_templates.changelog_file, resolved_repo_dir
        )
        template_dir = _resolve_template_dir(
            raw.changelog.template_dir, resolved_repo_dir
        )
        template_environment = create_template_environment(
            template_dir=template_dir,
            **raw.changelog.environment.model_dump(),
        )
        version_translator = VersionTranslator(
            tag_format=raw.tag_format,
            prerelease_token=branch_config.prerelease_token,
            add_partial_tags=raw.add_partial_tags,
        )
        build_command_env = _build_command_env(raw.build_command_env)

        return cls(
            repo_dir=resolved_repo_dir,
            project_metadata=project_metadata,
            commit_parser=commit_parser,
            version_translator=version_translator,
            major_on_zero=raw.major_on_zero,
            allow_zero_version=raw.allow_zero_version,
            prerelease=branch_config.prerelease,
            hvcs_client=hvcs_client,
            changelog_file=changelog_file,
            changelog_mode=raw.changelog.mode,
            # TODO: better support for custom parsers that actually just extend defaults
            #
            # Here we just assume the desired changelog style matches the parser name
            # as we provide templates specific to each parser type. Unfortunately if the
            # user has provided a custom parser, it would be up to the user to provide
            # custom templates but we just assume the base template is conventional
            # changelog_style = (
            #     raw.commit_parser
            #     if raw.commit_parser in _known_commit_parsers
            #     else "conventional"
            # )
            changelog_style="conventional",
            changelog_output_format=raw.changelog.default_templates.output_format,
            changelog_insertion_flag=raw.changelog.insertion_flag,
            changelog_mask_initial_release=raw.changelog.default_templates.mask_initial_release,
            changelog_excluded_commit_patterns=changelog_excluded_commit_patterns,
            template_dir=template_dir,
            template_environment=template_environment,
            version_declarations=tuple(version_declarations),
            build_command=raw.build_command,
            build_command_env=build_command_env,
            dist_glob_patterns=raw.publish.dist_glob_patterns,
            upload_to_vcs_release=raw.publish.upload_to_vcs_release,
            assets=raw.assets,
            commit_author=commit_author,
            commit_message=raw.commit_message,
            no_git_verify=raw.no_git_verify,
            ignore_token_for_push=raw.remote.ignore_token_for_push,
        )


def _load_project_metadata(repo_dir: Path) -> dict[str, Any]:
    project_metadata: dict[str, Any] = {}
    curr_dir = Path.cwd().resolve()
    allowed_directories = [
        dir_path
        for dir_path in [curr_dir, *curr_dir.parents]
        if str(repo_dir) in str(dir_path)
    ]
    for allowed_dir in allowed_directories:
        if (proj_toml := allowed_dir.joinpath("pyproject.toml")).exists():
            config_toml = tomlkit.parse(proj_toml.read_text())
            project_metadata = config_toml.unwrap().get("project", project_metadata)
            break
    return project_metadata


def _select_branch_options(branches: dict, active_branch: str) -> BranchConfig:
    for group, options in branches.items():
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


def _build_commit_parser(
    parser_name: str, parser_options: dict[str, Any]
) -> CommitParser[ParseResult, ParserOptions]:
    try:
        commit_parser_cls = (
            _known_commit_parsers[parser_name]
            if parser_name in _known_commit_parsers
            else dynamic_import(parser_name)
        )
    except ValueError as err:
        raise ParserLoadError(
            str.join(
                "\n",
                [
                    f"Unrecognized commit parser value: {parser_name!r}.",
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

    # TODO: Breaking change v11
    # commit_parser_opts_class = commit_parser_cls.get_default_options().__class__
    commit_parser_opts_class = commit_parser_cls.parser_options
    try:
        return commit_parser_cls(options=commit_parser_opts_class(**parser_options))
    except TypeError as err:
        raise ParserLoadError(
            str.join("\n", [str(err), f"Failed to initialize {parser_name}"])
        ) from err


def _build_excluded_commit_patterns(
    commit_message: str, exclude_patterns: Sequence[str]
) -> tuple[Pattern[str], ...]:
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
            regex_escape(commit_message.strip()),
        )
    )
    return (
        psr_release_commit_regex,
        *(regexp(pattern) for pattern in exclude_patterns),
    )


def _build_commit_author(commit_author_config: Any) -> Actor:
    from semantic_release.cli.config import EnvConfigVar

    if isinstance(commit_author_config, EnvConfigVar):
        commit_author_str = commit_author_config.getvalue() or ""
    else:
        commit_author_str = commit_author_config or ""

    commit_author_valid = Actor.name_email_regex.match(commit_author_str)
    if not commit_author_valid:
        raise ValueError(
            f"Invalid git author: {commit_author_str} "
            f"should match {Actor.name_email_regex}"
        )
    return Actor(*commit_author_valid.groups())


def _build_version_declarations(
    version_toml: Sequence[str] | None,
    version_variables: Sequence[str] | None,
    tag_format: str,
) -> list[IVersionReplacer]:
    version_declarations: list[IVersionReplacer] = []

    try:
        version_declarations.extend(
            TomlVersionDeclaration.from_string_definition(definition)
            for definition in iter(version_toml or ())
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
        version_declarations.extend(
            PatternVersionDeclaration.from_string_definition(definition, tag_format)
            for definition in iter(version_variables or ())
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

    return version_declarations


def _build_hvcs_client(raw: RawConfig, remote_url: str) -> HvcsBase:
    # Provide warnings if the token is missing
    if not raw.remote.token:
        logger.debug("hvcs token is not set")

        if not raw.remote.ignore_token_for_push:
            logger.warning("Token value is missing!")

    hvcs_client_cls = _known_hvcs[raw.remote.type]
    return hvcs_client_cls(
        remote_url=remote_url,
        hvcs_domain=raw.remote.domain,
        hvcs_api_domain=raw.remote.api_domain,
        token=raw.remote.token,
        allow_insecure=raw.remote.insecure,
    )


def _resolve_changelog_path(changelog_file: str, repo_dir: Path) -> Path:
    # Must use absolute after resolve because windows does not resolve if the path
    # does not exist which means it returns a relative path. So we force absolute
    # to ensure path is complete for the next check of path matching
    changelog_path = Path(changelog_file).expanduser().resolve().absolute()

    # Prevent path traversal attacks
    if repo_dir not in changelog_path.parents:
        raise InvalidConfiguration(
            "Changelog file destination must be inside of the repository directory."
        )
    return changelog_path


def _resolve_template_dir(template_dir: str, repo_dir: Path) -> Path:
    # Must use absolute after resolve because windows does not resolve if the path
    # does not exist which means it returns a relative path. So we force absolute
    # to ensure path is complete for the next check of path matching
    template_path = Path(template_dir).expanduser().resolve().absolute()

    # Prevent path traversal attacks
    if repo_dir not in template_path.parents:
        raise InvalidConfiguration(
            "Template directory must be inside of the repository directory."
        )
    return template_path


def _build_command_env(env_var_defs: Sequence[str]) -> dict[str, str]:
    build_cmd_env = {}

    for i, env_var_def in enumerate(env_var_defs):
        # Creative hack to handle missing =, but also = that can then be unpacked
        # as the resulting parts array can be either 2 or 3 in length. It becomes 3
        # with our forced empty value at the end which can be dropped
        parts = [*env_var_def.split("=", 1), ""]
        # Removes any odd spacing around =, and extracts name=value
        name, env_val = (part.strip() for part in parts[:2])

        if not name:
            # Skip when invalid format (ex. starting with = and no name)
            logger.warning("Skipping invalid build_command_env[%s] definition", i)
            continue

        if not env_val and env_var_def[-1] != "=":
            # Avoid the edge case that user wants to define a value as empty
            # and don't autoresolve it
            env_val = os.getenv(name, "")

        build_cmd_env[name] = env_val

    return build_cmd_env


__all__ = ["SemanticReleaseContext"]
