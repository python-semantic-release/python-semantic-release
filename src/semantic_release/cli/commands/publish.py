from __future__ import annotations

from typing import TYPE_CHECKING

import click
from git import Repo

from semantic_release.cli.util import noop_report
from semantic_release.errors import AssetUploadError
from semantic_release.globals import logger
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.version.algorithm import tags_and_versions

if TYPE_CHECKING:  # pragma: no cover
    from semantic_release.cli.cli_context import CliContextObj


def publish_distributions(
    tag: str,
    hvcs_client: RemoteHvcsBase,
    dist_glob_patterns: tuple[str, ...],
    noop: bool = False,
) -> None:
    if noop:
        noop_report(
            str.join(
                " ",
                [
                    "would have uploaded files matching any of the globs",
                    str.join(", ", [repr(g) for g in dist_glob_patterns]),
                    "to a remote VCS release, if supported",
                ],
            )
        )
        return

    logger.info("Uploading distributions to release")
    for pattern in dist_glob_patterns:
        hvcs_client.upload_dists(tag=tag, dist_glob=pattern)  # type: ignore[attr-defined]


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
def publish(cli_ctx: CliContextObj, tag: str) -> None:
    """Build and publish a distribution to a VCS release."""
    ctx = click.get_current_context()
    runtime = cli_ctx.runtime_ctx
    hvcs_client = runtime.hvcs_client
    translator = runtime.version_translator
    dist_glob_patterns = runtime.dist_glob_patterns

    with Repo(str(runtime.repo_dir)) as git_repo:
        repo_tags = git_repo.tags

    if tag == "latest":
        try:
            tag = str(tags_and_versions(repo_tags, translator)[0][0])
        except IndexError:
            click.echo(
                str.join(
                    " ",
                    [
                        "No tags found with format",
                        repr(translator.tag_format),
                        "couldn't identify latest version",
                    ],
                ),
                err=True,
            )
            ctx.exit(1)

    if tag not in {tag.name for tag in repo_tags}:
        click.echo(f"Tag '{tag}' not found in local repository!", err=True)
        ctx.exit(1)

    if not isinstance(hvcs_client, RemoteHvcsBase):
        click.echo(
            "Remote does not support artifact upload. Exiting with no action taken...",
            err=True,
        )
        return

    try:
        publish_distributions(
            tag=tag,
            hvcs_client=hvcs_client,
            dist_glob_patterns=dist_glob_patterns,
            noop=runtime.global_cli_options.noop,
        )
    except AssetUploadError as err:
        click.echo(err, err=True)
        ctx.exit(1)
