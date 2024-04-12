from __future__ import annotations

import logging
import os
import subprocess
from contextlib import nullcontext
from datetime import datetime
from typing import TYPE_CHECKING

import click
import shellingham  # type: ignore[import]
from click_option_group import MutuallyExclusiveOptionGroup, optgroup
from git.exc import GitCommandError
from requests import HTTPError

from semantic_release.changelog import ReleaseHistory, environment, recursive_render
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.common import (
    get_release_notes_template,
    render_default_changelog_file,
    render_release_notes,
)
from semantic_release.cli.github_actions_output import VersionGitHubActionsOutput
from semantic_release.cli.util import indented, noop_report, rprint
from semantic_release.const import DEFAULT_SHELL, DEFAULT_VERSION
from semantic_release.enums import LevelBump
from semantic_release.errors import UnexpectedResponse
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.version import Version, next_version, tags_and_versions

log = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from typing import ContextManager, Iterable, Mapping

    from git import Repo
    from git.refs.tag import Tag

    from semantic_release.cli.commands.cli_context import CliContextObj
    from semantic_release.version import VersionTranslator
    from semantic_release.version.declaration import VersionDeclarationABC


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
    log.debug(
        "%s: %s",
        is_forced_prerelease.__name__,
        ", ".join(f"{k} = {v}" for k, v in local_vars),
    )
    return (
        as_prerelease
        or forced_level_bump is LevelBump.PRERELEASE_REVISION
        or ((forced_level_bump is None) and prerelease)
    )


def last_released(
    repo: Repo, translator: VersionTranslator
) -> tuple[Tag, Version] | None:
    ts_and_vs = tags_and_versions(repo.tags, translator)
    return ts_and_vs[0] if ts_and_vs else None


def version_from_forced_level(
    repo: Repo, forced_level_bump: LevelBump, translator: VersionTranslator
) -> Version:
    ts_and_vs = tags_and_versions(repo.tags, translator)

    # If we have no tags, return the default version
    if not ts_and_vs:
        return Version.parse(DEFAULT_VERSION).bump(forced_level_bump)

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
    repo: Repo,
    version_declarations: Iterable[VersionDeclarationABC],
    version: Version,
    noop: bool = False,
) -> list[str]:
    working_dir = os.getcwd() if repo.working_dir is None else repo.working_dir

    paths = [
        str(declaration.path.resolve().relative_to(working_dir))
        for declaration in version_declarations
    ]
    if noop:
        noop_report(
            "would have updated versions in the following paths:"
            + "".join(f"\n    {path}" for path in paths)
        )
    else:
        log.debug("writing version %s to source paths %s", version, paths)
        for declaration in version_declarations:
            new_content = declaration.replace(new_version=version)
            declaration.path.write_text(new_content)

    return paths


def shell(
    cmd: str, *, env: Mapping[str, str] | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    shell: str | None
    try:
        shell, _ = shellingham.detect_shell()
    except shellingham.ShellDetectionFailure:
        log.warning("failed to detect shell, using default shell: %s", DEFAULT_SHELL)
        log.debug("stack trace", exc_info=True)
        shell = DEFAULT_SHELL

    if not shell:
        raise TypeError("'shell' is None")

    return subprocess.run(
        [shell, "-c" if shell != "cmd" else "/c", cmd],  # noqa: S603
        env=(env or {}),
        check=check,
    )


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
    print_only: bool = False,
    print_only_tag: bool = False,
    print_last_released: bool = False,
    print_last_released_tag: bool = False,
    as_prerelease: bool = False,
    prerelease_token: str | None = None,
    force_level: str | None = None,
    commit_changes: bool = True,
    create_tag: bool = True,
    update_changelog: bool = True,
    push_changes: bool = True,
    make_vcs_release: bool = True,
    build_metadata: str | None = None,
    skip_build: bool = False,
) -> str:
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
    runtime = cli_ctx.runtime_ctx
    repo = runtime.repo
    translator = runtime.version_translator

    # We can short circuit updating the release if we are only printing the last released version
    if print_last_released or print_last_released_tag:
        if last_release := last_released(repo, translator):
            if print_last_released:
                click.echo(last_release[1])
            if print_last_released_tag:
                click.echo(last_release[0])
        else:
            log.warning("No release tags found.")
        ctx.exit(0)

    parser = runtime.commit_parser
    forced_level_bump = None if not force_level else LevelBump.from_string(force_level)
    prerelease = is_forced_prerelease(
        as_prerelease=as_prerelease,
        forced_level_bump=forced_level_bump,
        prerelease=runtime.prerelease,
    )
    hvcs_client = runtime.hvcs_client
    changelog_file = runtime.changelog_file
    changelog_excluded_commit_patterns = runtime.changelog_excluded_commit_patterns
    env = runtime.template_environment
    template_dir = runtime.template_dir
    assets = runtime.assets
    commit_author = runtime.commit_author
    commit_message = runtime.commit_message
    major_on_zero = runtime.major_on_zero
    no_verify = runtime.no_git_verify
    build_command = runtime.build_command
    opts = runtime.global_cli_options
    gha_output = VersionGitHubActionsOutput()

    if prerelease_token:
        log.info("Forcing use of %s as the prerelease token", prerelease_token)
        translator.prerelease_token = prerelease_token

    # Only push if we're committing changes
    if push_changes and not commit_changes and not create_tag:
        log.info("changes will not be pushed because --no-commit disables pushing")
        push_changes &= commit_changes
    # Only push if we're creating a tag
    if push_changes and not create_tag and not commit_changes:
        log.info("new tag will not be pushed because --no-tag disables pushing")
        push_changes &= create_tag
    # Only make a release if we're pushing the changes
    if make_vcs_release and not push_changes:
        log.info("No vcs release will be created because pushing changes is disabled")
        make_vcs_release &= push_changes

    if forced_level_bump:
        log.warning(
            "Forcing a '%s' release due to '--%s' command-line flag",
            force_level,
            (
                force_level
                if forced_level_bump is not LevelBump.PRERELEASE_REVISION
                else "prerelease"
            ),
        )

        new_version = version_from_forced_level(
            repo=repo, forced_level_bump=forced_level_bump, translator=translator
        )

        # We only turn the forced version into a prerelease if the user has specified
        # that that is what they want on the command-line; otherwise we assume they are
        # forcing a full release
        new_version = (
            new_version.to_prerelease(token=translator.prerelease_token)
            if prerelease
            else new_version.finalize_version()
        )

    else:
        new_version = next_version(
            repo=repo,
            translator=translator,
            commit_parser=parser,
            prerelease=prerelease,
            major_on_zero=major_on_zero,
            allow_zero_version=runtime.allow_zero_version,
        )

    if build_metadata:
        new_version.build_metadata = build_metadata

    if as_prerelease:
        before_conversion, new_version = (
            new_version,
            new_version.to_prerelease(token=translator.prerelease_token),
        )
        log.info(
            "Converting %s to %s due to '--as-prerelease' command-line option",
            before_conversion,
            new_version,
        )

    gha_output.released = False
    gha_output.version = new_version
    ctx.call_on_close(gha_output.write_if_possible)

    # Print the new version so that command-line output capture will work
    if print_only_tag:
        click.echo(translator.str_to_tag(str(new_version)))
    else:
        click.echo(str(new_version))

    # If the new version has already been released, we fail and abort if strict;
    # otherwise we exit with 0.
    if new_version in {v for _, v in tags_and_versions(repo.tags, translator)}:
        if opts.strict:
            ctx.fail(
                f"No release will be made, {new_version!s} has already been "
                "released!"
            )
        else:
            rprint(
                f"[bold orange1]No release will be made, {new_version!s} has "
                "already been released!"
            )
            ctx.exit(0)

    if print_only or print_only_tag:
        ctx.exit(0)

    rprint(f"[bold green]The next version is: [white]{new_version!s}[/white]! :rocket:")

    rh = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=parser,
        exclude_commit_patterns=changelog_excluded_commit_patterns,
    )

    commit_date = datetime.now()
    try:
        rh = rh.release(
            new_version,
            tagger=commit_author,
            committer=commit_author,
            tagged_date=commit_date,
        )
    except ValueError as ve:
        ctx.fail(str(ve))

    all_paths_to_add: list[str] = []

    if update_changelog:
        changelog_context = make_changelog_context(
            hvcs_client=hvcs_client, release_history=rh
        )
        changelog_context.bind_to_environment(env)

        if template_dir.is_dir():
            if opts.noop:
                noop_report(
                    f"would have recursively rendered the template directory "
                    f"{template_dir!r} relative to {repo.working_dir!r}. "
                    "Paths which would be modified by this operation cannot be "
                    "determined in no-op mode."
                )
            else:
                all_paths_to_add.extend(
                    recursive_render(
                        template_dir, environment=env, _root_dir=repo.working_dir
                    )
                )

        else:
            log.info(
                "Path %r not found, using default changelog template", template_dir
            )
            if opts.noop:
                noop_report(
                    "would have written your changelog to "
                    + str(changelog_file.relative_to(repo.working_dir))
                )
            else:
                changelog_text = render_default_changelog_file(env)
                changelog_file.write_text(f"{changelog_text}\n", encoding="utf-8")

            all_paths_to_add.append(str(changelog_file.relative_to(repo.working_dir)))

    # Apply the new version to the source files
    files_with_new_version_written = apply_version_to_source_files(
        repo=repo,
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
    elif not build_command:
        rprint("[green]No build command specified, skipping")
    elif runtime.global_cli_options.noop:
        noop_report(f"would have run the build_command {build_command}")
    else:
        try:
            log.info("Running build command %s", build_command)
            rprint(
                "[bold green]:hammer_and_wrench: Running build command: "
                + build_command
            )
            shell(
                build_command,
                check=True,
                env=dict(
                    filter(
                        lambda k_v: k_v[1] is not None,  # type: ignore
                        {
                            # Common values
                            "PATH": os.getenv("PATH", ""),
                            "HOME": os.getenv("HOME", None),
                            "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV", None),
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
                            "PSR_DOCKER_GITHUB_ACTION": os.getenv(
                                "PSR_DOCKER_GITHUB_ACTION", None
                            ),
                            # User defined overrides of environment (from config)
                            **runtime.build_command_env,
                            # PSR injected environment variables
                            "NEW_VERSION": str(new_version),
                        }.items(),
                    )
                ),
            )
        except subprocess.CalledProcessError as exc:
            ctx.fail(str(exc))

    # Commit changes
    if commit_changes and opts.noop:
        noop_report(
            indented(
                f"""
                would have run:
                    git add {" ".join(all_paths_to_add)}
                """
            )
        )

    elif commit_changes:
        # TODO: in future this loop should be 1 line:
        # repo.index.add(all_paths_to_add, force=False)  # noqa: ERA001
        # but since 'force' is deliberally ineffective (as in docstring) in gitpython 3.1.18
        # we have to do manually add each filepath, and catch the exception if it is an ignored file
        for updated_path in all_paths_to_add:
            try:
                repo.git.add(updated_path)
            except GitCommandError:  # noqa: PERF203
                log.warning("Failed to add path (%s) to index", updated_path)

    def custom_git_environment() -> ContextManager[None]:
        """
        git.custom_environment is a context manager but
        is not reentrant, so once we have "used" it
        we need to throw it away and re-create it in
        order to use it again
        """
        return (
            nullcontext()
            if not commit_author
            else repo.git.custom_environment(
                GIT_AUTHOR_NAME=commit_author.name,
                GIT_AUTHOR_EMAIL=commit_author.email,
                GIT_COMMITTER_NAME=commit_author.name,
                GIT_COMMITTER_EMAIL=commit_author.email,
            )
        )

    # If we haven't modified any source code then we skip trying to make a commit
    # and any tag that we apply will be to the HEAD commit (made outside of
    # running PSR
    if not repo.index.diff("HEAD"):
        log.info("No local changes to add to any commit, skipping")

    elif commit_changes and opts.noop:
        command = (
            f"""\
            GIT_AUTHOR_NAME={commit_author.name} \\
                GIT_AUTHOR_EMAIL={commit_author.email} \\
                GIT_COMMITTER_NAME={commit_author.name} \\
                GIT_COMMITTER_EMAIL={commit_author.email} \\
                """
            if commit_author
            else ""
        )

        # Indents the newlines so that terminal formatting is happy - note the
        # git commit line of the output is 24 spaces indented too
        # Only this message needs such special handling because of the newlines
        # that might be in a commit message between the subject and body
        indented_commit_message = commit_message.format(version=new_version).replace(
            "\n\n", "\n\n" + " " * 24
        )

        command += f"git commit -m '{indented_commit_message}'"
        command += "--no-verify" if no_verify else ""

        noop_report(
            indented(
                f"""
                would have run:
                    {command}
                """
            )
        )

    elif commit_changes:
        with custom_git_environment():
            repo.git.commit(
                m=commit_message.format(version=new_version),
                date=int(commit_date.timestamp()),
                no_verify=no_verify,
            )

    # Run the tagging after potentially creating a new HEAD commit.
    # This way if no source code is modified, i.e. all metadata updates
    # are disabled, and the changelog generation is disabled or it's not
    # modified, then the HEAD commit will be tagged as a release commit
    # despite not being made by PSR
    if commit_changes or create_tag:
        if opts.noop:
            noop_report(
                indented(
                    f"""
                    would have run:
                        git tag -a {new_version.as_tag()} -m "{new_version.as_tag()}"
                    """
                )
            )
        else:
            with custom_git_environment():
                repo.git.tag("-a", new_version.as_tag(), m=new_version.as_tag())

    if push_changes:
        remote_url = runtime.hvcs_client.remote_url(
            use_token=not runtime.ignore_token_for_push
        )
        active_branch = repo.active_branch.name
        if commit_changes and opts.noop:
            noop_report(
                indented(
                    f"""
                    would have run:
                        git push {runtime.masker.mask(remote_url)} {active_branch}
                    """  # noqa: E501
                )
            )
        elif commit_changes:
            repo.git.push(remote_url, active_branch)

        if create_tag and opts.noop:
            noop_report(
                indented(
                    f"""
                    would have run:
                        git push {runtime.masker.mask(remote_url)} tag {new_version.as_tag()}
                    """  # noqa: E501
                )
            )
        elif create_tag:
            # push specific tag refspec (that we made) to remote
            # ---------------
            # Resolves issue #803 where a tag that already existed was pushed and caused
            # a failure. Its not clear why there was an incorrect tag (likely user error change)
            # but we will avoid possibly pushing an separate tag that we didn't create.
            repo.git.push(remote_url, "tag", new_version.as_tag())

    gha_output.released = True

    if make_vcs_release and isinstance(hvcs_client, RemoteHvcsBase):
        if opts.noop:
            noop_report(
                f"would have created a release for the tag {new_version.as_tag()!r}"
            )

        release = rh.released[new_version]
        # Use a new, non-configurable environment for release notes -
        # not user-configurable at the moment
        release_note_environment = environment(template_dir=runtime.template_dir)
        changelog_context = make_changelog_context(
            hvcs_client=hvcs_client, release_history=rh
        )
        changelog_context.bind_to_environment(release_note_environment)

        template = get_release_notes_template(template_dir)
        release_notes = render_release_notes(
            release_notes_template=template,
            template_environment=release_note_environment,
            version=new_version,
            release=release,
        )
        if opts.noop:
            noop_report(
                "would have created the following release notes: \n" + release_notes
            )
            noop_report(f"would have uploaded the following assets: {runtime.assets}")
        else:
            try:
                hvcs_client.create_release(
                    tag=new_version.as_tag(),
                    release_notes=release_notes,
                    prerelease=new_version.is_prerelease,
                    assets=assets,
                )
            except HTTPError as err:
                log.exception(err)
                ctx.fail(str.join("\n", [str(err), "Failed to create release!"]))
            except UnexpectedResponse as err:
                log.exception(err)
                ctx.fail(
                    str.join(
                        "\n",
                        [
                            str(err),
                            "Unexpected response from remote VCS!",
                            "Before re-running, make sure to clean up any artifacts on the hvcs that may have already been created.",
                        ],
                    )
                )
            except Exception as e:
                log.exception(e)
                ctx.fail(str(e))

    return str(new_version)
