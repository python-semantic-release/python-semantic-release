import logging

import click

from semantic_release.cli.util import noop_report
from semantic_release.version import tags_and_versions

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
@click.pass_context
def publish(ctx: click.Context, tag: str = "latest") -> None:
    """
    Build and publish a distribution to a VCS release.
    """
    runtime = ctx.obj
    repo = runtime.repo
    hvcs_client = runtime.hvcs_client
    translator = runtime.version_translator
    dist_glob_patterns = runtime.dist_glob_patterns

    if tag == "latest":
        tag = str(tags_and_versions(repo.tags, translator)[0][0])
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
