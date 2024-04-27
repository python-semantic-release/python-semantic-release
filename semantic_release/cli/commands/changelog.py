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
    from semantic_release.cli.commands.cli_context import CliContextObj
    from semantic_release.version import Version

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
    help="Post the generated release notes to the remote VCS's release for this tag",
)
@click.pass_obj
def changelog(cli_ctx: CliContextObj, release_tag: str | None = None) -> None:
    """Generate and optionally publish a changelog for your project"""
    ctx = click.get_current_context()
    runtime = cli_ctx.runtime_ctx
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
                "would have written your changelog to "
                + str(changelog_file.relative_to(repo.working_dir))
            )
        else:
            changelog_text = render_default_changelog_file(env)
            changelog_file.write_text(f"{changelog_text}\n", encoding="utf-8")

    else:
        if runtime.global_cli_options.noop:
            noop_report(
                f"would have recursively rendered the template directory "
                f"{template_dir!r} relative to {repo.working_dir!r}"
            )
        else:
            recursive_render(template_dir, environment=env, _root_dir=repo.working_dir)

    if release_tag and isinstance(hvcs_client, RemoteHvcsBase):
        if runtime.global_cli_options.noop:
            noop_report(
                f"would have posted changelog to the release for tag {release_tag}"
            )

        # note: the following check ensures 'version is not None', but mypy can't follow
        version: Version = translator.from_tag(release_tag)  # type: ignore[assignment]
        if not version:
            ctx.fail(
                f"Tag {release_tag!r} doesn't match tag format "
                f"{translator.tag_format!r}"
            )

        try:
            release = rh.released[version]
        except KeyError:
            ctx.fail(f"tag {release_tag} not in release history")

        template = get_release_notes_template(template_dir)
        release_notes = render_release_notes(
            release_notes_template=template,
            template_environment=env,
            version=version,
            release=release,
        )

        if runtime.global_cli_options.noop:
            noop_report(
                "would have posted the following release notes:\n" + release_notes
            )
        else:
            try:
                hvcs_client.create_or_update_release(
                    release_tag, f"{release_notes}\n", prerelease=version.is_prerelease
                )
            except Exception as e:
                log.exception(e)
                ctx.fail(str(e))
