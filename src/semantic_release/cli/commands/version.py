from __future__ import annotations

import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import click
import shellingham  # type: ignore[import]
from click_option_group import MutuallyExclusiveOptionGroup, optgroup
from git import GitCommandError, Repo
from requests import HTTPError

from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.cli.changelog_writer import (
    generate_release_notes,
    write_changelog_files,
)
from semantic_release.cli.github_actions_output import (
    PersistenceMode,
    VersionGitHubActionsOutput,
)
from semantic_release.cli.util import noop_report, rprint
from semantic_release.const import DEFAULT_SHELL, DEFAULT_VERSION
from semantic_release.enums import LevelBump
from semantic_release.errors import (
    BuildDistributionsError,
    DetachedHeadGitError,
    GitCommitEmptyIndexError,
    GitFetchError,
    InternalError,
    LocalGitError,
    UnexpectedResponse,
    UnknownUpstreamBranchError,
    UpstreamBranchChangedError,
)
from semantic_release.gitproject import GitProject
from semantic_release.globals import logger
from semantic_release.hvcs.github import Github
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.version.algorithm import (
    next_version,
    tags_and_versions,
)
from semantic_release.version.translator import VersionTranslator

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path
    from typing import Mapping, Sequence

    from git.refs.tag import Tag

    from semantic_release.cli.cli_context import CliContextObj
    from semantic_release.version.declaration import IVersionReplacer
    from semantic_release.version.version import Version


def is_forced_prerelease(
    as_prerelease: bool, forced_level_bump: LevelBump | None, prerelease: bool
) -> bool:
    """
    Determine if this release is forced to have prerelease on/off.
    If ``force_prerelease`` is set then yes.
    Otherwise if we are forcing a specific level bump without force_prerelease,
    it's False.
    Otherwise (``force_level is None``) use the value of ``prerelease``
    """
    local_vars = list(locals().items())
    logger.debug(
        "%s: %s",
        is_forced_prerelease.__name__,
        str.join(", ", iter(f"{k} = {v}" for k, v in local_vars)),
    )
    return (
        as_prerelease
        or forced_level_bump is LevelBump.PRERELEASE_REVISION
        or ((forced_level_bump is None) and prerelease)
    )


def last_released(
    repo_dir: Path, tag_format: str, add_partial_tags: bool = False
) -> tuple[Tag, Version] | None:
    with Repo(str(repo_dir)) as git_repo:
        ts_and_vs = tags_and_versions(
            git_repo.tags,
            VersionTranslator(tag_format=tag_format, add_partial_tags=add_partial_tags),
        )

    return ts_and_vs[0] if ts_and_vs else None


def version_from_forced_level(
    repo_dir: Path, forced_level_bump: LevelBump, translator: VersionTranslator
) -> Version:
    with Repo(str(repo_dir)) as git_repo:
        ts_and_vs = tags_and_versions(git_repo.tags, translator)

    # If we have no tags, return the default version
    if not ts_and_vs:
        # Since the translator is configured by the user, we can't guarantee that it will
        # be able to parse the default version. So we first cast it to a tag using the default
        # value and the users configured tag format, then parse it back to a version object
        default_initial_version = translator.from_tag(
            translator.str_to_tag(DEFAULT_VERSION)
        )
        if default_initial_version is None:
            # This should never happen, but if it does, it's a bug
            raise InternalError(
                "Translator was unable to parse the embedded default version"
            )
        return default_initial_version.bump(forced_level_bump)

    _, latest_version = ts_and_vs[0]
    if forced_level_bump is not LevelBump.PRERELEASE_REVISION:
        return latest_version.bump(forced_level_bump)

    # We need to find the latest version with the prerelease token
    # we're looking for, and return that version + an increment to
    # the prerelease revision.

    # NOTE this can probably be cleaned up.
    # ts_and_vs are in order, so check if we're looking at prereleases
    # for the same (major, minor, patch) as the latest version.
    # If we are, we can increment the revision and we're done. If
    # we don't find a prerelease targeting this version with the same
    # token as the one we're looking to prerelease, we can use revision 1.
    for _, version in ts_and_vs:
        if not (
            version.major == latest_version.major
            and version.minor == latest_version.minor
            and version.patch == latest_version.patch
        ):
            break
        if (
            version.is_prerelease
            and version.prerelease_token == translator.prerelease_token
        ):
            return version.bump(LevelBump.PRERELEASE_REVISION)
    return latest_version.to_prerelease(token=translator.prerelease_token, revision=1)


def apply_version_to_source_files(
    repo_dir: Path,
    version_declarations: Sequence[IVersionReplacer],
    version: Version,
    noop: bool = False,
) -> list[str]:
    if len(version_declarations) < 1:
        return []

    if not noop:
        logger.debug("Updating version %s in repository files...", version)

    paths = [
        decl.update_file_w_version(new_version=version, noop=noop)
        for decl in version_declarations
    ]

    repo_filepaths = [
        str(updated_file.relative_to(repo_dir))
        for updated_file in paths
        if updated_file is not None
    ]

    if noop:
        noop_report(
            str.join(
                "",
                [
                    "would have updated versions in the following paths:",
                    *[f"\n    {filepath}" for filepath in repo_filepaths],
                ],
            )
        )

    return repo_filepaths


def shell(
    cmd: str, *, env: Mapping[str, str] | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    shell: str | None
    try:
        shell, _ = shellingham.detect_shell()
    except shellingham.ShellDetectionFailure:
        logger.warning("failed to detect shell, using default shell: %s", DEFAULT_SHELL)
        logger.debug("stack trace", exc_info=True)
        shell = DEFAULT_SHELL

    if not shell:
        raise TypeError("'shell' is None")

    shell_cmd_param = defaultdict(
        lambda: "-c",
        {
            "cmd": "/c",
            "powershell": "-Command",
            "pwsh": "-Command",
        },
    )

    return subprocess.run(  # noqa: S603
        [shell, shell_cmd_param[shell], cmd],
        env=(env or {}),
        check=check,
    )


def is_windows() -> bool:
    return sys.platform == "win32"


def get_windows_env() -> Mapping[str, str | None]:
    return {
        environment_variable: os.getenv(environment_variable, None)
        for environment_variable in (
            "ALLUSERSAPPDATA",
            "ALLUSERSPROFILE",
            "APPDATA",
            "COMMONPROGRAMFILES",
            "COMMONPROGRAMFILES(X86)",
            "DEFAULTUSERPROFILE",
            "HOMEPATH",
            "PATHEXT",
            "PROFILESFOLDER",
            "PROGRAMFILES",
            "PROGRAMFILES(X86)",
            "SYSTEM",
            "SYSTEM16",
            "SYSTEM32",
            "SYSTEMDRIVE",
            "SYSTEMPROFILE",
            "SYSTEMROOT",
            "TEMP",
            "TMP",
            "USERNAME",  # must include for python getpass.getuser() on windows
            "USERPROFILE",
            "USERSID",
            "WINDIR",
        )
    }


def build_distributions(
    build_command: str | None,
    build_command_env: Mapping[str, str] | None = None,
    noop: bool = False,
) -> None:
    """
    Run the build command to build the distributions.

    :param build_command: The build command to run.
    :param build_command_env: The environment variables to use when running the
        build command.
    :param noop: Whether or not to run the build command.

    :raises: BuildDistributionsError: if the build command fails
    """
    if not build_command:
        rprint("[green]No build command specified, skipping")
        return

    if noop:
        noop_report(f"would have run the build_command {build_command}")
        return

    logger.info("Running build command %s", build_command)
    rprint(f"[bold green]:hammer_and_wrench: Running build command: {build_command}")

    build_env_vars: dict[str, str] = dict(
        filter(
            lambda k_v: k_v[1] is not None,  # type: ignore[arg-type]
            {
                # Common values
                "PATH": os.getenv("PATH", ""),
                "HOME": os.getenv("HOME", None),
                "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV", None),
                # Windows environment variables
                **(get_windows_env() if is_windows() else {}),
                # affects build decisions
                "CI": os.getenv("CI", None),
                # Identifies which CI environment
                "GITHUB_ACTIONS": os.getenv("GITHUB_ACTIONS", None),
                "GITLAB_CI": os.getenv("GITLAB_CI", None),
                "GITEA_ACTIONS": os.getenv("GITEA_ACTIONS", None),
                "BITBUCKET_CI": (
                    str(True).lower()
                    if os.getenv("BITBUCKET_REPO_FULL_NAME", None)
                    else None
                ),
                "PSR_DOCKER_GITHUB_ACTION": os.getenv("PSR_DOCKER_GITHUB_ACTION", None),
                **(build_command_env or {}),
            }.items(),
        )
    )

    try:
        shell(build_command, env=build_env_vars, check=True)
        rprint("[bold green]Build completed successfully!")
    except subprocess.CalledProcessError as exc:
        logger.exception(exc)
        logger.error("Build command failed with exit code %s", exc.returncode)  # noqa: TRY400
        raise BuildDistributionsError from exc


@click.command(
    short_help="Detect and apply a new version",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@optgroup.group("Print flags", cls=MutuallyExclusiveOptionGroup)
@optgroup.option(
    "--print", "print_only", is_flag=True, help="Print the next version and exit"
)
@optgroup.option(
    "--print-tag",
    "print_only_tag",
    is_flag=True,
    help="Print the next version tag and exit",
)
@optgroup.option(
    "--print-last-released",
    is_flag=True,
    help="Print the last released version and exit",
)
@optgroup.option(
    "--print-last-released-tag",
    is_flag=True,
    help="Print the last released version tag and exit",
)
@click.option(
    "--as-prerelease",
    "as_prerelease",
    is_flag=True,
    help="Ensure the next version to be released is a prerelease version",
)
@click.option(
    "--prerelease-token",
    "prerelease_token",
    default=None,
    help="Force the next version to use this prerelease token, if it is a prerelease",
)
@click.option(
    "--major",
    "force_level",
    flag_value="major",
    help="Force the next version to be a major release",
)
@click.option(
    "--minor",
    "force_level",
    flag_value="minor",
    help="Force the next version to be a minor release",
)
@click.option(
    "--patch",
    "force_level",
    flag_value="patch",
    help="Force the next version to be a patch release",
)
@click.option(
    "--prerelease",
    "force_level",
    flag_value="prerelease_revision",
    help="Force the next version to be a prerelease",
)
@click.option(
    "--commit/--no-commit",
    "commit_changes",
    default=True,
    help="Whether or not to commit changes locally",
)
@click.option(
    "--tag/--no-tag",
    "create_tag",
    default=True,
    help="Whether or not to create a tag for the new version",
)
@click.option(
    "--changelog/--no-changelog",
    "update_changelog",
    default=True,
    help="Whether or not to update the changelog",
)
@click.option(
    "--push/--no-push",
    "push_changes",
    default=True,
    help="Whether or not to push the new commit and tag to the remote",
)
@click.option(
    "--vcs-release/--no-vcs-release",
    "make_vcs_release",
    default=True,
    help="Whether or not to create a release in the remote VCS, if supported",
)
@click.option(
    "--build-metadata",
    "build_metadata",
    default=os.getenv("PSR_BUILD_METADATA"),
    help="Build metadata to append to the new version",
)
@click.option(
    "--skip-build",
    "skip_build",
    default=False,
    is_flag=True,
    help="Skip building the current project",
)
@click.pass_obj
def version(  # noqa: C901
    cli_ctx: CliContextObj,
    print_only: bool,
    print_only_tag: bool,
    print_last_released: bool,
    print_last_released_tag: bool,
    as_prerelease: bool,
    prerelease_token: str | None,
    commit_changes: bool,
    create_tag: bool,
    update_changelog: bool,
    push_changes: bool,
    make_vcs_release: bool,
    build_metadata: str | None,
    skip_build: bool,
    force_level: str | None = None,
) -> None:
    """
    Detect the semantically correct next version that should be applied to your
    project.

    By default:

    * Write this new version to the project metadata locations specified
    in the configuration file

    * Create a new commit with these locations and any other assets configured
    to be included in a release

    * Tag this commit according the configured format, with a tag that uniquely
    identifies the version being released.

    * Push the new tag and commit to the remote for the repository

    * Create a release (if supported) in the remote VCS for this tag
    """
    ctx = click.get_current_context()

    # Enable any cli overrides of configuration before asking for the runtime context
    config = cli_ctx.raw_config

    # We can short circuit updating the release if we are only printing the last released version
    if print_last_released or print_last_released_tag:
        # TODO: get tag format a better way
        if not (
            last_release := last_released(
                config.repo_dir,
                tag_format=config.tag_format,
                add_partial_tags=config.add_partial_tags,
            )
        ):
            logger.warning("No release tags found.")
            return

        click.echo(last_release[0] if print_last_released_tag else last_release[1])
        return

    # TODO: figure out --print of next version with & without branch validation
    # do you always need a prerelease token if its not --as-prerelease?
    runtime = cli_ctx.runtime_ctx
    translator = runtime.version_translator

    parser = runtime.commit_parser
    hvcs_client = runtime.hvcs_client
    assets = runtime.assets
    commit_author = runtime.commit_author
    commit_message = runtime.commit_message
    major_on_zero = runtime.major_on_zero
    no_verify = runtime.no_git_verify
    opts = runtime.global_cli_options
    add_partial_tags = config.add_partial_tags
    gha_output = VersionGitHubActionsOutput(
        gh_client=hvcs_client if isinstance(hvcs_client, Github) else None,
        mode=(
            PersistenceMode.TEMPORARY
            if opts.noop or (not commit_changes and not create_tag)
            else PersistenceMode.PERMANENT
        ),
        released=False,
    )

    forced_level_bump = None if not force_level else LevelBump.from_string(force_level)
    prerelease = is_forced_prerelease(
        as_prerelease=as_prerelease,
        forced_level_bump=forced_level_bump,
        prerelease=runtime.prerelease,
    )

    if prerelease_token:
        logger.info("Forcing use of %s as the prerelease token", prerelease_token)
        translator.prerelease_token = prerelease_token

    # Check if the repository is shallow and unshallow it if necessary
    # This ensures we have the full history for commit analysis
    project = GitProject(
        directory=runtime.repo_dir,
        commit_author=runtime.commit_author,
        credential_masker=runtime.masker,
    )
    if project.is_shallow_clone():
        logger.info("Repository is a shallow clone, converting to full clone...")
        project.git_unshallow(noop=opts.noop)

    # Only push if we're committing changes
    if push_changes and not commit_changes and not create_tag:
        logger.info("changes will not be pushed because --no-commit disables pushing")
        push_changes &= commit_changes

    # Only push if we're creating a tag
    if push_changes and not create_tag and not commit_changes:
        logger.info("new tag will not be pushed because --no-tag disables pushing")
        push_changes &= create_tag

    # Only make a release if we're pushing the changes
    if make_vcs_release and not push_changes:
        logger.info(
            "No vcs release will be created because pushing changes is disabled"
        )
        make_vcs_release &= push_changes

    if not forced_level_bump:
        with Repo(str(runtime.repo_dir)) as git_repo:
            new_version = next_version(
                repo=git_repo,
                translator=translator,
                commit_parser=parser,
                prerelease=prerelease,
                major_on_zero=major_on_zero,
                allow_zero_version=runtime.allow_zero_version,
            )
    else:
        logger.warning(
            "Forcing a '%s' release due to '--%s' command-line flag",
            force_level,
            (
                force_level
                if forced_level_bump is not LevelBump.PRERELEASE_REVISION
                else "prerelease"
            ),
        )

        new_version = version_from_forced_level(
            repo_dir=runtime.repo_dir,
            forced_level_bump=forced_level_bump,
            translator=translator,
        )

        # We only turn the forced version into a prerelease if the user has specified
        # that that is what they want on the command-line; otherwise we assume they are
        # forcing a full release
        new_version = (
            new_version.to_prerelease(token=translator.prerelease_token)
            if prerelease
            else new_version.finalize_version()
        )

    if build_metadata:
        new_version.build_metadata = build_metadata

    # Update GitHub Actions output value with new version & set delayed write
    gha_output.version = new_version
    if isinstance(hvcs_client, Github):
        ctx.call_on_close(gha_output.write_if_possible)

    # Make string variant of version or appropriate tag as necessary
    version_to_print = str(new_version) if not print_only_tag else new_version.as_tag()

    # Print the new version so that command-line output capture will work
    click.echo(version_to_print)

    with Repo(str(runtime.repo_dir)) as git_repo:
        # TODO: performance improvement - cache the result of tags_and_versions (previously done in next_version())
        previously_released_versions = {
            v for _, v in tags_and_versions(git_repo.tags, translator)
        }

    # If the new version has already been released, we fail and abort if strict;
    # otherwise we exit with 0.
    if new_version in previously_released_versions:
        err_msg = str.join(
            " ",
            [
                "[bold orange1]No release will be made,",
                f"{new_version!s} has already been released!",
            ],
        )

        if opts.strict:
            click.echo(err_msg, err=True)
            ctx.exit(2)

        rprint(err_msg)
        return

    if print_only or print_only_tag:
        return

    # TODO: need a better way as this is inconsistent if releasing older version patches
    if last_release := last_released(config.repo_dir, tag_format=config.tag_format):
        # If we have a last release, we can set the previous version for the
        # GitHub Actions output
        gha_output.prev_version = last_release[1]

    with Repo(str(runtime.repo_dir)) as git_repo:
        release_history = ReleaseHistory.from_git_history(
            repo=git_repo,
            translator=translator,
            commit_parser=parser,
            exclude_commit_patterns=runtime.changelog_excluded_commit_patterns,
        )

    rprint(f"[bold green]The next version is: [white]{new_version!s}[/white]! :rocket:")

    commit_date = datetime.now(timezone.utc).astimezone()  # Locale-aware timestamp
    try:
        # Create release object for the new version
        # This will be used to generate the changelog prior to the commit and/or tag
        release_history = release_history.release(
            new_version,
            tagger=commit_author,
            committer=commit_author,
            tagged_date=commit_date,
        )
    except ValueError as ve:
        click.echo(str(ve), err=True)
        ctx.exit(1)

    all_paths_to_add: list[str] = []

    if update_changelog:
        # Write changelog files & add them to the list of files to commit
        all_paths_to_add.extend(
            write_changelog_files(
                runtime_ctx=runtime,
                release_history=release_history,
                hvcs_client=hvcs_client,
                noop=opts.noop,
            )
        )

    # Apply the new version to the source files
    files_with_new_version_written = apply_version_to_source_files(
        repo_dir=runtime.repo_dir,
        version_declarations=runtime.version_declarations,
        version=new_version,
        noop=opts.noop,
    )
    all_paths_to_add.extend(files_with_new_version_written)
    all_paths_to_add.extend(assets or [])

    # Build distributions before committing any changes - this way if the
    # build fails, modifications to the source code won't be committed
    if skip_build:
        rprint("[bold orange1]Skipping build due to --skip-build flag")
    else:
        try:
            build_distributions(
                build_command=runtime.build_command,
                build_command_env={
                    # User defined overrides of environment (from config)
                    **runtime.build_command_env,
                    # PSR injected environment variables
                    "NEW_VERSION": str(new_version),
                    "PACKAGE_NAME": runtime.project_metadata.get("name", ""),
                },
                noop=opts.noop,
            )
        except BuildDistributionsError as exc:
            click.echo(str(exc), err=True)
            click.echo("Build failed, aborting release", err=True)
            ctx.exit(1)

    license_cfg = runtime.project_metadata.get(
        "license-expression",
        runtime.project_metadata.get(
            "license",
            "",
        ),
    )

    license_cfg = "" if not isinstance(license_cfg, (str, dict)) else license_cfg
    license_cfg = (
        license_cfg.get("text", "") if isinstance(license_cfg, dict) else license_cfg
    )

    gha_output.release_notes = release_notes = generate_release_notes(
        hvcs_client,
        release=release_history.released[new_version],
        template_dir=runtime.template_dir,
        history=release_history,
        style=runtime.changelog_style,
        mask_initial_release=runtime.changelog_mask_initial_release,
        license_name="" if not isinstance(license_cfg, str) else license_cfg,
    )

    # Preparing for committing changes; we always stage files even if we're not committing them in order to support a two-stage commit
    project.git_add(paths=all_paths_to_add, noop=opts.noop)
    if commit_changes:
        # NOTE: If we haven't modified any source code then we skip trying to make a commit
        # and any tag that we apply will be to the HEAD commit (made outside of
        # running PSR
        try:
            project.git_commit(
                message=commit_message.format(version=new_version),
                date=int(commit_date.timestamp()),
                no_verify=no_verify,
                noop=opts.noop,
            )
        except GitCommitEmptyIndexError:
            logger.info("No local changes to add to any commit, skipping")
            commit_changes = False

    # Tag the version after potentially creating a new HEAD commit.
    # This way if no source code is modified, i.e. all metadata updates
    # are disabled, and the changelog generation is disabled or it's not
    # modified, then the HEAD commit will be tagged as a release commit
    # despite not being made by PSR
    if create_tag:
        project.git_tag(
            tag_name=new_version.as_tag(),
            message=new_version.as_tag(),
            isotimestamp=commit_date.isoformat(),
            noop=opts.noop,
        )

        with Repo(str(runtime.repo_dir)) as git_repo:
            gha_output.commit_sha = git_repo.head.commit.hexsha

    if push_changes:
        remote_url = runtime.hvcs_client.remote_url(
            use_token=not runtime.ignore_token_for_push
        )

        if commit_changes:
            # Verify that the upstream branch has not changed before pushing
            # This prevents conflicts if another commit was pushed while we were preparing the release
            # We check HEAD~1 because we just made a release commit
            try:
                project.verify_upstream_unchanged(
                    local_ref="HEAD~1",
                    upstream_ref=config.remote.name,
                    remote_url=remote_url,
                    noop=opts.noop,
                )
            except UpstreamBranchChangedError as exc:
                click.echo(str(exc), err=True)
                click.echo(
                    "Upstream branch has changed. Please pull the latest changes and try again.",
                    err=True,
                )
                ctx.exit(1)
            except (
                DetachedHeadGitError,
                GitCommandError,
                UnknownUpstreamBranchError,
                GitFetchError,
                LocalGitError,
            ) as exc:
                click.echo(str(exc), err=True)
                click.echo("Unable to verify upstream due to error!", err=True)
                ctx.exit(1)

            # TODO: integrate into push branch
            with Repo(str(runtime.repo_dir)) as git_repo:
                active_branch = git_repo.active_branch.name

            project.git_push_branch(
                remote_url=remote_url,
                branch=active_branch,
                noop=opts.noop,
            )

        if create_tag:
            # push specific tag refspec (that we made) to remote
            project.git_push_tag(
                remote_url=remote_url,
                tag=new_version.as_tag(),
                noop=opts.noop,
            )
            # Create or update partial tags for releases
            if add_partial_tags and not prerelease:
                partial_tags = [new_version.as_major_tag(), new_version.as_minor_tag()]
                # If build metadata is set, also retag the version without the metadata
                if build_metadata:
                    partial_tags.append(new_version.as_patch_tag())

                for partial_tag in partial_tags:
                    project.git_tag(
                        tag_name=partial_tag,
                        message=f"{partial_tag} => {new_version.as_tag()}",
                        isotimestamp=commit_date.isoformat(),
                        noop=opts.noop,
                        force=True,
                    )
                    project.git_push_tag(
                        remote_url=remote_url,
                        tag=partial_tag,
                        noop=opts.noop,
                        force=True,
                    )

    # Update GitHub Actions output value now that release has occurred
    gha_output.released = True

    if not make_vcs_release:
        return

    if not isinstance(hvcs_client, RemoteHvcsBase):
        logger.info("Remote does not support releases. Skipping release creation...")
        return

    exception: Exception | None = None
    help_message = ""
    try:
        hvcs_client.create_release(
            tag=new_version.as_tag(),
            release_notes=release_notes,
            prerelease=new_version.is_prerelease,
            assets=assets,
            noop=opts.noop,
        )
    except HTTPError as err:
        exception = err
    except UnexpectedResponse as err:
        exception = err
        help_message = str.join(
            " ",
            [
                "Before re-running, make sure to clean up any artifacts",
                "on the hvcs that may have already been created.",
            ],
        )
        help_message = str.join(
            "\n",
            [
                "Unexpected response from remote VCS!",
                help_message,
            ],
        )
    except Exception as err:  # noqa: BLE001
        # TODO: Remove this catch-all exception handler in the future
        exception = err
    finally:
        if exception is not None:
            logger.exception(exception)
            click.echo(str(exception), err=True)
            if help_message:
                click.echo(help_message, err=True)
            click.echo(
                f"Failed to create release on {hvcs_client.__class__.__name__}!",
                err=True,
            )
            ctx.exit(1)
