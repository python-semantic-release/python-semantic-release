from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import click

from semantic_release.cli.util import noop_report
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.version import tags_and_versions

if TYPE_CHECKING:
    from semantic_release.cli.commands.cli_context import CliContextObj


log = logging.getLogger(__name__)


@click.command(
    short_help="Publish distributions to VCS Releases",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--tag",
    "tag",
    help="The tag associated with the release to publish to",
    default="latest",
)
@click.pass_obj
def publish(cli_ctx: CliContextObj, tag: str = "latest") -> None:
    """Build and publish a distribution to a VCS release."""
    ctx = click.get_current_context()
    runtime = cli_ctx.runtime_ctx
    repo = runtime.repo
    hvcs_client = runtime.hvcs_client
    translator = runtime.version_translator
    dist_glob_patterns = runtime.dist_glob_patterns

    if tag == "latest":
        try:
            tag = str(tags_and_versions(repo.tags, translator)[0][0])
        except IndexError:
            ctx.fail(
                f"No tags found with format {translator.tag_format!r}, couldn't "
                "identify latest version"
            )

    if not isinstance(hvcs_client, RemoteHvcsBase):
        log.info(
            "Remote does not support artifact upload. Exiting with no action taken..."
        )
        ctx.exit(0)

    if runtime.global_cli_options.noop:
        noop_report(
            "would have uploaded files matching any of the globs "
            + ", ".join(repr(g) for g in dist_glob_patterns)
            + " to a remote VCS release, if supported"
        )
        ctx.exit(0)

    log.info("Uploading distributions to release")
    for pattern in dist_glob_patterns:
        hvcs_client.upload_dists(tag=tag, dist_glob=pattern)
