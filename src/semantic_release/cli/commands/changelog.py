from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import click
from git import Repo

from semantic_release.changelog import ReleaseHistory
from semantic_release.cli.changelog_writer import (
    generate_release_notes,
    write_changelog_files,
)
from semantic_release.cli.util import noop_report
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase

if TYPE_CHECKING:
    from semantic_release.cli.cli_context import CliContextObj


log = logging.getLogger(__name__)


def post_release_notes(
    release_tag: str,
    release_notes: str,
    prerelease: bool,
    hvcs_client: RemoteHvcsBase,
    noop: bool = False,
) -> None:
    if noop:
        noop_report(
            str.join(
                "\n",
                [
                    f"would have posted the following release notes for tag {release_tag}:",
                    # Escape square brackets to ensure all content is displayed in the console
                    # (i.e. prevent interpretation of ansi escape sequences that is valid markdown)
                    release_notes.replace("[", "\\["),
                ],
            )
        )
        return

    hvcs_client.create_or_update_release(
        release_tag,
        release_notes,
        prerelease=prerelease,
    )


@click.command(
    short_help="Generate a changelog",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--post-to-release-tag",
    "release_tag",
    default=None,
    help="Post the generated release notes to the remote VCS's release for this tag",
)
@click.pass_obj
def changelog(cli_ctx: CliContextObj, release_tag: str | None) -> None:
    """Generate and optionally publish a changelog for your project"""
    ctx = click.get_current_context()
    runtime = cli_ctx.runtime_ctx
    translator = runtime.version_translator
    hvcs_client = runtime.hvcs_client

    with Repo(str(runtime.repo_dir)) as git_repo:
        release_history = ReleaseHistory.from_git_history(
            repo=git_repo,
            translator=translator,
            commit_parser=runtime.commit_parser,
            exclude_commit_patterns=runtime.changelog_excluded_commit_patterns,
        )

    write_changelog_files(
        runtime_ctx=runtime,
        release_history=release_history,
        hvcs_client=hvcs_client,
        noop=runtime.global_cli_options.noop,
    )

    if not release_tag:
        return

    if not isinstance(hvcs_client, RemoteHvcsBase):
        click.echo(
            "Remote does not support releases. Skipping release notes update...",
            err=True,
        )
        return

    if not (version := translator.from_tag(release_tag)):
        click.echo(
            str.join(
                " ",
                [
                    f"Tag {release_tag!r} does not match the tag format",
                    repr(translator.tag_format),
                ],
            ),
            err=True,
        )
        ctx.exit(1)

    try:
        release = release_history.released[version]
    except KeyError:
        click.echo(f"tag {release_tag} not in release history", err=True)
        ctx.exit(2)

    release_notes = generate_release_notes(
        hvcs_client,
        release,
        runtime.template_dir,
        release_history,
        style=runtime.changelog_style,
    )

    try:
        post_release_notes(
            release_tag=release_tag,
            release_notes=release_notes,
            prerelease=version.is_prerelease,
            hvcs_client=hvcs_client,
            noop=runtime.global_cli_options.noop,
        )
    except Exception as e:
        log.exception(e)
        click.echo("Failed to post release notes to remote", err=True)
        ctx.exit(1)
