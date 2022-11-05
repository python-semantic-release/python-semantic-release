import logging
import os
from textwrap import dedent, indent
from typing import Optional

import click

# NOTE: use backport with newer API than stdlib
from importlib_resources import files

from semantic_release.changelog import recursive_render, release_history
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.util import noop_report
from semantic_release.enums import LevelBump
from semantic_release.version import next_version, tags_and_versions

log = logging.getLogger(__name__)


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
@click.pass_context
def version(
    ctx: click.Context,
    print_only: bool = False,
    force_prerelease: bool = False,
    force_level: Optional[str] = None,
    commit_changes: bool = True,
    update_changelog: bool = True,
    push_changes: bool = True,
    make_vcs_release: bool = True,
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
    prerelease = force_prerelease or runtime.prerelease
    hvcs_client = runtime.hvcs_client
    changelog_file = runtime.changelog_file
    env = runtime.template_environment
    template_dir = runtime.template_dir
    assets = runtime.assets
    commit_message = runtime.commit_message
    major_on_zero = runtime.major_on_zero
    opts = runtime.global_cli_options

    # Only push if we're committing changes
    if push_changes and not commit_changes:
        log.warning("")
    # Only make a release if we're pushing the changes

    if force_prerelease:
        log.warning("Forcing prerelease due to '--prerelease' command-line flag")

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
        if force_prerelease:
            v = v.to_prerelease()

    else:
        v = next_version(
            repo=repo,
            translator=translator,
            commit_parser=parser,
            prerelease=prerelease,
            major_on_zero=major_on_zero,
        )
    # TODO: if it's already the same/released?
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

    if commit_changes and opts.noop:
        all_paths_to_add = paths + (assets if assets else [])
        # Indents the newlines so that terminal formatting is happy - note the
        # git commit line of the output is 24 spaces indented too
        # Only this message needs such special handling because of the newlines
        # that might be in a commit message between the subject and body
        indented_commit_message = commit_message.format(version=v).replace(
            "\n\n", "\n\n" + " " * 24
        )
        noop_report(
            indent(
                dedent(
                    f"""
                    would have run:
                        git add {" ".join(all_paths_to_add)}
                        git commit -m "{indented_commit_message}"
                    """
                ),
                prefix=" " * 4,
            )
        )
    elif commit_changes:
        repo.git.add(paths)
        if assets:
            repo.git.add(assets)

        repo.git.commit(m=commit_message.format(version=v))

        repo.git.tag("-a", v.as_tag(), m=v.as_tag())

    if update_changelog:
        rh = release_history(repo=repo, translator=translator, commit_parser=parser)
        changelog_context = make_changelog_context(
            hvcs_client=hvcs_client, release_history=rh
        )
        changelog_context.bind_to_environment(env)

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
                ctx.exit(0)
            with open(str(changelog_file), "w+", encoding="utf-8") as f:
                tmpl.dump(f)

            updated_paths = [changelog_file]
        else:
            if opts.noop:
                noop_report(
                    f"would have recursively rendered the template directory "
                    f"{template_dir!r} relative to {repo.working_dir!r}"
                )
                ctx.exit(0)
            updated_paths = recursive_render(
                template_dir, environment=env, _root_dir=repo.working_dir
            )

        if commit_changes and opts.noop:
            noop_report(
                dedent(
                    f"""
                    would have run:
                        git add {" ".join(updated_paths)}
                        git commit --amend --no-edit
                    """
                )
            )
        if commit_changes:
            repo.git.add(updated_paths)
            repo.git.commit("--amend", "--no-edit")

    if push_changes:
        remote_url = runtime.hvcs_client.remote_url(
            use_token=not runtime.ignore_token_for_push
        )
        active_branch = repo.active_branch.name
        if opts.noop:
            noop_report(
                dedent(
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
    elif make_vcs_release:
        hvcs_client.create_or_update_release(
            tag=v.as_tag(),
            changelog=changelog_file.read_text(encoding="utf-8"),
            prerelease=v.is_prerelease,
        )

    return str(v)
