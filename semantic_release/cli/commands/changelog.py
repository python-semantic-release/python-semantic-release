from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import click

from semantic_release.changelog import ReleaseHistory, recursive_render
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.common import (
    get_release_notes_template,
    render_default_changelog_file,
    render_release_notes,
)
from semantic_release.cli.util import noop_report
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase

if TYPE_CHECKING:
    from pathlib import Path

    from jinja2 import Environment

    from semantic_release.cli.commands.cli_context import CliContextObj


log = logging.getLogger(__name__)


def apply_default_changelog(
    changelog_file: Path,
    destination_dir: Path,
    environment: Environment,
    noop: bool = False,
) -> None:
    if noop:
        noop_report(
            str.join(" ", [
                "would have written your changelog to",
                str(changelog_file.relative_to(destination_dir)),
            ])
        )
        return

    changelog_text = render_default_changelog_file(environment)
    changelog_file.write_text(f"{changelog_text}\n", encoding="utf-8")


def apply_user_changelog_template_directory(
    template_dir: Path,
    environment: Environment,
    target_dir: Path,
    noop: bool = False,
) -> None:
    if noop:
        noop_report(
            str.join(" ", [
                "would have recursively rendered the template directory",
                repr(template_dir),
                "relative to",
                repr(target_dir),
            ])
        )
        return

    recursive_render(template_dir, environment=environment, _root_dir=target_dir)


def post_release_notes(
    release_tag: str,
    release_notes: str,
    prerelease: bool,
    hvcs_client: RemoteHvcsBase,
    noop: bool = False,
) -> None:
    if noop:
        noop_report(
            str.join("\n", [
                f"would have posted the following release notes for tag {release_tag}:",
                release_notes,
            ])
        )
        return

    hvcs_client.create_or_update_release(
        release_tag, f"{release_notes}\n", prerelease=prerelease
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
    repo = runtime.repo
    translator = runtime.version_translator
    hvcs_client = runtime.hvcs_client
    env = runtime.template_environment
    template_dir = runtime.template_dir
    changelog_file = runtime.changelog_file
    changelog_excluded_commit_patterns = runtime.changelog_excluded_commit_patterns

    release_history = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=runtime.commit_parser,
        exclude_commit_patterns=changelog_excluded_commit_patterns,
    )

    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client, release_history=release_history,
    )

    changelog_context.bind_to_environment(env)


    if template_dir.exists():
        apply_user_changelog_template_directory(
            template_dir=template_dir,
            environment=env,
            target_dir=Path(repo.working_dir),
            noop=runtime.global_cli_options.noop,
        )
    else:
        log.info("No contents found in %r, using default changelog template", template_dir)
        apply_default_changelog(
            changelog_file=changelog_file,
            destination_dir=Path(repo.working_dir),
            environment=env,
            noop=runtime.global_cli_options.noop,
        )

    if not release_tag:
        return

    if not isinstance(hvcs_client, RemoteHvcsBase):
        log.info(
            "Remote does not support releases. Skipping release notes update..."
        )
        return

    if not (version := translator.from_tag(release_tag)):
        ctx.fail(
            str.join(" ", [
                f"Tag {release_tag!r} does not match the tag format",
                repr(translator.tag_format),
            ])
        )

    try:
        release = release_history.released[version]
    except KeyError:
        ctx.fail(f"tag {release_tag} not in release history")

    template = get_release_notes_template(template_dir)
    release_notes = render_release_notes(
        release_notes_template=template,
        template_environment=env,
        version=version,
        release=release,
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
        ctx.fail(str(e))
