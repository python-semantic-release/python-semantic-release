from __future__ import annotations

import logging
import os

import click

from semantic_release.changelog import ReleaseHistory, recursive_render
from semantic_release.changelog.context import make_changelog_context
from semantic_release.cli.common import (
    render_default_changelog_file,
    render_release_notes,
)
from semantic_release.cli.util import noop_report

log = logging.getLogger(__name__)


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
    help="Post the generated changelog to the remote VCS's release for this tag",
)
@click.pass_context
def changelog(ctx: click.Context, release_tag: str | None = None) -> None:
    """
    Generate and optionally publish a changelog for your project
    """
    runtime = ctx.obj
    repo = runtime.repo
    parser = runtime.commit_parser
    translator = runtime.version_translator
    hvcs_client = runtime.hvcs_client
    env = runtime.template_environment
    template_dir = runtime.template_dir
    changelog_file = runtime.changelog_file
    changelog_excluded_commit_patterns = runtime.changelog_excluded_commit_patterns

    rh = ReleaseHistory.from_git_history(
        repo=repo,
        translator=translator,
        commit_parser=parser,
        exclude_commit_patterns=changelog_excluded_commit_patterns,
    )
    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client, release_history=rh
    )
    changelog_context.bind_to_environment(env)

    if not os.path.exists(template_dir):
        log.info("Path %r not found, using default changelog template", template_dir)
        if runtime.global_cli_options.noop:
            noop_report(
                f"would have written your changelog to {changelog_file.relative_to(repo.working_dir)}"
            )
            ctx.exit(0)

        changelog_text = render_default_changelog_file(env)
        with open(str(changelog_file), "w+", encoding="utf-8") as f:
            f.write(changelog_text)
    else:
        if runtime.global_cli_options.noop:
            noop_report(
                f"would have recursively rendered the template directory "
                f"{template_dir!r} relative to {repo.working_dir!r}"
            )
            ctx.exit(0)
        recursive_render(template_dir, environment=env, _root_dir=repo.working_dir)

    if release_tag and runtime.global_cli_options.noop:
        noop_report(f"would have posted changelog to the release for tag {release_tag}")
    elif release_tag:
        version = translator.from_tag(release_tag)
        if not version:
            ctx.fail(
                f"Tag {release_tag!r} doesn't match tag format {translator.tag_format!r}"
            )

        try:
            release = rh.released[version]
        except KeyError:
            ctx.fail(f"tag {release_tag} not in release history")

        release_notes = render_release_notes(
            template_environment=env, version=version, release=release
        )
        try:
            hvcs_client.create_or_update_release(
                release_tag, release_notes, prerelease=version.is_prerelease
            )
        except Exception as e:
            log.error("%s", str(e), exc_info=True)
            ctx.fail(str(e))
