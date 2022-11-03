import logging
import os
from typing import Optional

import click

from semantic_release.cli.config import RuntimeContext
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
# A "--commit/--no-commit" option? Or is this better with the "--dry-run" flag?
# how about push/no-push?
@click.pass_context
def version(
    ctx: click.Context,
    print_only: bool = False,
    force_prerelease: bool = False,
    force_level: Optional[str] = None,
) -> None:
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
    """
    runtime: RuntimeContext = ctx.obj
    repo = runtime.repo
    parser = runtime.commit_parser
    translator = runtime.version_translator
    prerelease = force_prerelease or runtime.prerelease
    assets = runtime.assets
    commit_message = runtime.commit_message
    major_on_zero = runtime.major_on_zero

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
    print(str(v))
    if print_only or runtime.global_cli_options.noop:
        ctx.exit(0)

    for declaration in runtime.version_declarations:
        new_content = declaration.replace(new_version=v)
        declaration.path.write_text(new_content)

    working_dir = os.getcwd() if repo.working_dir is None else repo.working_dir

    paths = [
        declaration.path.resolve().relative_to(working_dir)
        for declaration in runtime.version_declarations
    ]
    log.debug("versions declared in: %s", ", ".join(str(path) for path in paths))
    repo.git.add(paths)
    if assets:
        repo.git.add(assets)

    repo.git.commit(m=commit_message.format(version=v))

    repo.git.tag("-a", v.as_tag(), m=v.as_tag())

    remote_url = runtime.hvcs_client.remote_url(
        use_token=not runtime.ignore_token_for_push
    )
    # Wrap in GitCommandError handling - remove token
    repo.git.push(remote_url, repo.active_branch.name)
    repo.git.push("--tags", remote_url, repo.active_branch.name)
