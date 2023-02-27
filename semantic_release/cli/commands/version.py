from __future__ import annotations

import logging
import os
from datetime import datetime

import click

# NOTE: use backport with newer API than stdlib
from importlib_resources import files

from semantic_release.changelog import ReleaseHistory, environment, recursive_render
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.util import indented, noop_report
from semantic_release.enums import LevelBump
from semantic_release.version import next_version, tags_and_versions

log = logging.getLogger(__name__)


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


@click.command(short_help="Detect and apply a new version")
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
    help="Build metadata to append to the latest version",
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
    opts = runtime.global_cli_options

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
        ts_and_vs = tags_and_versions(repo.tags, translator)
        _, latest_version = ts_and_vs[0]
        v = latest_version.bump(level_bump)

        # We only turn the forced version into a prerelease if the user has specified
        # that that is what they want on the command-line; otherwise we assume they are
        # forcing a full release
        if prerelease:
            v = v.to_prerelease()
        else:
            v = v.finalize_version()

    else:
        v = next_version(
            repo=repo,
            translator=translator,
            commit_parser=parser,
            prerelease=prerelease,
            major_on_zero=major_on_zero,
        )

    if build_metadata:
        v.build_metadata = build_metadata

    # Perhaps this behaviour should change if no release should be made?
    # Or perhaps a graceful exit if the tag already exists
    click.echo(str(v))
    if print_only:
        ctx.exit(0)

    working_dir = os.getcwd() if repo.working_dir is None else repo.working_dir

    paths = [
        str(declaration.path.resolve().relative_to(working_dir))
        for declaration in runtime.version_declarations
    ]
    log.debug("versions declared in: %s", ", ".join(paths))
    if opts.noop:
        noop_report(
            "would have updated versions in the following paths:"
            + "".join(f"\n    {path}" for path in paths)
        )
    else:
        for declaration in runtime.version_declarations:
            new_content = declaration.replace(new_version=v)
            declaration.path.write_text(new_content)

    all_paths_to_add = paths + (assets if assets else [])
    # _head_is_new_release_commit = False

    if commit_changes and opts.noop:
        # Indents the newlines so that terminal formatting is happy - note the
        # git commit line of the output is 24 spaces indented too
        # Only this message needs such special handling because of the newlines
        # that might be in a commit message between the subject and body
        indented_commit_message = commit_message.format(version=v).replace(
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
    rh = rh.release(
        v, tagger=commit_author, committer=commit_author, tagged_date=commit_date
    )

    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client, release_history=rh
    )
    changelog_context.bind_to_environment(env)

    if update_changelog:
        updated_paths: list[str] = []

        if not os.path.exists(template_dir):
            log.info(
                "Path %r not found, using default changelog template", template_dir
            )
            changelog_text = (
                files("semantic_release")
                .joinpath("data/templates/CHANGELOG.md.j2")
                .read_text(encoding="utf-8")
            )
            tmpl = env.from_string(changelog_text).stream()
            if opts.noop:
                noop_report(
                    f"would have written your changelog to {changelog_file.relative_to(repo.working_dir)}"
                )
            else:
                with open(str(changelog_file), "w+", encoding="utf-8") as f:
                    tmpl.dump(f)

            updated_paths.append(str(changelog_file.relative_to(repo.working_dir)))
        else:
            if opts.noop:
                noop_report(
                    f"would have recursively rendered the template directory "
                    f"{template_dir!r} relative to {repo.working_dir!r}. "
                    "Paths which would be modified by this operation cannot be "
                    "determined in no-op mode."
                )
            else:
                updated_paths += recursive_render(
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

    # If there are any modifications to the source code of the repository, we make
    # a release commit to commit the CHANGELOG and other files changed by rendering
    # to the repo, which will be the new HEAD commit

    # If we haven't modified any source code then we skip trying to make a commit
    # and any tag that we apply will be to the HEAD commit (made outside of
    # running PSR
    if not repo.index.diff("HEAD"):
        log.info("No local changes to add to any commit, skipping")

    elif commit_changes and opts.noop:
        command = "git commit -m '{commit_message.format(version=v)}'"
        command += (
            f" --author '{commit_author.name} <{commit_author.email}>'"
            if commit_author
            else ""
        )

        noop_report(
            indented(
                f"""
                would have run:
                    {command}
                """
            )
        )

    elif commit_changes:
        repo.git.commit(
            m=commit_message.format(version=v),
            author=f"{commit_author.name} <{commit_author.email}>",
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
                    git tag -a {v.as_tag()} -m "{v.as_tag()}"
                """
            )
        )
    elif commit_changes:
        repo.git.tag("-a", v.as_tag(), m=v.as_tag())

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
            # Wrap in GitCommandError handling - remove token
            repo.git.push(remote_url, active_branch)
            repo.git.push("--tags", remote_url, active_branch)

    if make_vcs_release and opts.noop:
        noop_report(f"would have created a release for the tag {v.as_tag()!r}")
        noop_report(f"would have uploaded the following assets: {runtime.assets}")
    elif make_vcs_release:
        release = rh.released[v]
        release_template = (
            files("semantic_release")
            .joinpath("data/templates/release_notes.md.j2")
            .read_text(encoding="utf-8")
        )
        # Use a new, non-configurable environment for release notes - not user-configurable at the moment
        release_note_environment = environment(template_dir=runtime.template_dir)
        changelog_context.bind_to_environment(release_note_environment)
        release_notes = release_note_environment.from_string(release_template).render(
            version=v, release=release
        )
        try:
            release_id = hvcs_client.create_or_update_release(
                tag=v.as_tag(),
                release_notes=release_notes,
                prerelease=v.is_prerelease,
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

    return str(v)
