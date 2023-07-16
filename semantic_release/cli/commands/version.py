from __future__ import annotations

import logging
import os
import subprocess
from contextlib import nullcontext
from datetime import datetime
from typing import TYPE_CHECKING, ContextManager

import click
import shellingham  # type: ignore[import]

from semantic_release.changelog import ReleaseHistory, environment, recursive_render
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.common import (
    render_default_changelog_file,
    render_release_notes,
)
from semantic_release.cli.github_actions_output import VersionGitHubActionsOutput
from semantic_release.cli.util import indented, noop_report, rprint
from semantic_release.const import DEFAULT_SHELL, DEFAULT_VERSION
from semantic_release.enums import LevelBump
from semantic_release.version import (
    Version,
    VersionTranslator,
    next_version,
    tags_and_versions,
)

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from git import Repo

    from semantic_release.version.declaration import VersionDeclarationABC


def is_forced_prerelease(
    force_prerelease: bool, force_level: str | None, prerelease: bool
) -> bool:
    """
    Determine if this release is forced to have prerelease on/off.
    If ``force_prerelease`` is set then yes.
    Otherwise if we are forcing a specific level bump without force_prerelease,
    it's False.
    Otherwise (``force_level is None``) use the value of ``prerelease``
    """
    log.debug(", ".join(f"{k} = {v}" for k, v in locals().items()))
    return force_prerelease or ((force_level is None) and prerelease)


def version_from_forced_level(
    repo: Repo, level_bump: LevelBump, translator: VersionTranslator
) -> Version:
    ts_and_vs = tags_and_versions(repo.tags, translator)

    # If we have no tags, return the default version
    if not ts_and_vs:
        return Version.parse(DEFAULT_VERSION).bump(level_bump)

    _, latest_version = ts_and_vs[0]
    return latest_version.bump(level_bump)


def apply_version_to_source_files(
    repo: Repo,
    version_declarations: list[VersionDeclarationABC],
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


def shell(cmd: str, *, check: bool = True) -> subprocess.CompletedProcess:
    shell: str | None
    try:
        shell, _ = shellingham.detect_shell()
    except shellingham.ShellDetectionFailure:
        log.warning("failed to detect shell, using default shell: %s", DEFAULT_SHELL)
        log.debug("stack trace", exc_info=True)
        shell = DEFAULT_SHELL

    if not shell:
        raise TypeError("'shell' is None")

    return subprocess.run([shell, "-c", cmd], check=check)


@click.command(
    short_help="Detect and apply a new version",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--print", "print_only", is_flag=True, help="Print the next version and exit"
)
@click.option(
    "--prerelease",
    "force_prerelease",
    is_flag=True,
    help="Force the next version to be a prerelease",
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
    help="force the next version to be a major release",
)
@click.option(
    "--minor",
    "force_level",
    flag_value="minor",
    help="force the next version to be a minor release",
)
@click.option(
    "--patch",
    "force_level",
    flag_value="patch",
    help="force the next version to be a patch release",
)
@click.option(
    "--commit/--no-commit",
    "commit_changes",
    default=True,
    help="Whether or not to commit changes locally",
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
@click.pass_context
def version(
    ctx: click.Context,
    print_only: bool = False,
    force_prerelease: bool = False,
    prerelease_token: str | None = None,
    force_level: str | None = None,
    commit_changes: bool = True,
    update_changelog: bool = True,
    push_changes: bool = True,
    make_vcs_release: bool = True,
    build_metadata: str | None = None,
    skip_build: bool = False,
) -> str:
    """
    Detect the semantically correct next version that should be applied to your
    project.

    \b
    By default:
      * Write this new version to the project metadata locations
        specified in the configuration file
      * Create a new commit with these locations and any other assets configured
        to be included in a release
      * Tag this commit according the configured format, with a tag that uniquely
        identifies the version being released.
      * Push the new tag and commit to the remote for the repository
      * Create a release (if supported) in the remote VCS for this tag
    """
    runtime = ctx.obj
    repo = runtime.repo
    parser = runtime.commit_parser
    translator = runtime.version_translator
    prerelease = is_forced_prerelease(
        force_prerelease=force_prerelease,
        force_level=force_level,
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
    build_command = runtime.build_command
    opts = runtime.global_cli_options
    gha_output = VersionGitHubActionsOutput()

    if prerelease_token:
        log.info("Forcing use of %s as the prerelease token", prerelease_token)
        translator.prerelease_token = prerelease_token

    # Only push if we're committing changes
    if push_changes and not commit_changes:
        log.info("changes will not be pushed because --no-commit disables pushing")
        push_changes &= commit_changes
    # Only make a release if we're pushing the changes
    if make_vcs_release and not push_changes:
        log.info("No vcs release will be created because pushing changes is disabled")
        make_vcs_release &= push_changes

    if force_prerelease:
        log.warning("Forcing prerelease due to '--prerelease' command-line flag")
    elif force_level:
        log.warning(
            "Forcing prerelease=False due to '--%s' command-line flag and no '--prerelease' flag",
            force_level,
        )

    if force_level:
        level_bump = LevelBump.from_string(force_level)
        log.warning(
            "Forcing a %s level bump due to '--force' command-line option", force_level
        )

        new_version = version_from_forced_level(
            repo=repo, level_bump=level_bump, translator=translator
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
        )

    if build_metadata:
        new_version.build_metadata = build_metadata

    gha_output.released = False
    gha_output.version = new_version
    ctx.call_on_close(gha_output.write_if_possible)

    # Print the new version so that command-line output capture will work
    click.echo(str(new_version))

    # If the new version has already been released, we fail and abort if strict;
    # otherwise we exit with 0.
    if new_version in {v for _, v in tags_and_versions(repo.tags, translator)}:
        if opts.strict:
            ctx.fail(
                f"No release will be made, {str(new_version)} has already been released!"
            )
        else:
            rprint(
                f"[bold orange1]No release will be made, {str(new_version)} has already been released!"
            )
            ctx.exit(0)

    if print_only:
        ctx.exit(0)

    rprint(
        f"[bold green]The next version is: [white]{str(new_version)}[/white]! :rocket:"
    )

    files_with_new_version_written = apply_version_to_source_files(
        repo=repo,
        version_declarations=runtime.version_declarations,
        version=new_version,
        noop=opts.noop,
    )
    all_paths_to_add = files_with_new_version_written + (assets or [])

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
                f"[bold green]:hammer_and_wrench: Running build command: {build_command}"
            )
            shell(build_command, check=True)
        except subprocess.CalledProcessError as exc:
            ctx.fail(str(exc))

    # Commit changes
    if commit_changes and opts.noop:
        # Indents the newlines so that terminal formatting is happy - note the
        # git commit line of the output is 24 spaces indented too
        # Only this message needs such special handling because of the newlines
        # that might be in a commit message between the subject and body
        indented_commit_message = commit_message.format(version=new_version).replace(
            "\n\n", "\n\n" + " " * 24
        )
        noop_report(
            indented(
                f"""
                would have run:
                    git add {" ".join(all_paths_to_add)}
                    git commit -m "{indented_commit_message}"
                """
            )
        )

    elif commit_changes:
        repo.git.add(all_paths_to_add)

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

    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client, release_history=rh
    )
    changelog_context.bind_to_environment(env)

    updated_paths: list[str] = []
    if update_changelog:
        if not os.path.exists(template_dir):
            log.info(
                "Path %r not found, using default changelog template", template_dir
            )
            if opts.noop:
                noop_report(
                    f"would have written your changelog to {changelog_file.relative_to(repo.working_dir)}"
                )
            else:
                changelog_text = render_default_changelog_file(env)
                with open(str(changelog_file), "w+", encoding="utf-8") as f:
                    f.write(changelog_text)

            updated_paths = [str(changelog_file.relative_to(repo.working_dir))]
        else:
            if opts.noop:
                noop_report(
                    f"would have recursively rendered the template directory "
                    f"{template_dir!r} relative to {repo.working_dir!r}. "
                    "Paths which would be modified by this operation cannot be "
                    "determined in no-op mode."
                )
            else:
                updated_paths = recursive_render(
                    template_dir, environment=env, _root_dir=repo.working_dir
                )

        if commit_changes and opts.noop:
            noop_report(
                indented(
                    f"""
                    would have run:
                        git add {" ".join(updated_paths)}
                    """
                )
            )
        elif commit_changes:
            # Anything changed here should be staged.
            repo.git.add(updated_paths)

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
        command += "git commit -m '{commit_message.format(version=v)}'"

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
            )

    # Run the tagging after potentially creating a new HEAD commit.
    # This way if no source code is modified, i.e. all metadata updates
    # are disabled, and the changelog generation is disabled or it's not
    # modified, then the HEAD commit will be tagged as a release commit
    # despite not being made by PSR
    if commit_changes and opts.noop:
        noop_report(
            indented(
                f"""
                would have run:
                    git tag -a {new_version.as_tag()} -m "{new_version.as_tag()}"
                """
            )
        )
    elif commit_changes:
        with custom_git_environment():
            repo.git.tag("-a", new_version.as_tag(), m=new_version.as_tag())

    if push_changes:
        remote_url = runtime.hvcs_client.remote_url(
            use_token=not runtime.ignore_token_for_push
        )
        active_branch = repo.active_branch.name
        if opts.noop:
            noop_report(
                indented(
                    f"""
                    would have run:
                        git push {runtime.masker.mask(remote_url)} {active_branch}
                        git push --tags {runtime.masker.mask(remote_url)} {active_branch}
                    """
                )
            )
        else:
            repo.git.push(remote_url, active_branch)
            repo.git.push("--tags", remote_url, active_branch)

    gha_output.released = True

    if make_vcs_release and opts.noop:
        noop_report(
            f"would have created a release for the tag {new_version.as_tag()!r}"
        )
        noop_report(f"would have uploaded the following assets: {runtime.assets}")
    elif make_vcs_release:
        release = rh.released[new_version]
        # Use a new, non-configurable environment for release notes - not user-configurable at the moment
        release_note_environment = environment(template_dir=runtime.template_dir)
        changelog_context.bind_to_environment(release_note_environment)
        release_notes = render_release_notes(
            template_environment=release_note_environment,
            version=new_version,
            release=release,
        )
        try:
            release_id = hvcs_client.create_or_update_release(
                tag=new_version.as_tag(),
                release_notes=release_notes,
                prerelease=new_version.is_prerelease,
            )
        except Exception as e:
            log.error("%s", str(e), exc_info=True)
            ctx.fail(str(e))
        if not release_id:
            log.warning("release_id not identified, cannot upload assets")
        else:
            for asset in assets:
                log.info("Uploading asset %s", asset)
                try:
                    hvcs_client.upload_asset(release_id, asset)
                except Exception as e:
                    log.error("%s", str(e), exc_info=True)
                    ctx.fail(str(e))

    return str(new_version)
