import logging
import shlex
import subprocess

import click
from rich import print as rprint
from twine.commands.upload import upload

from semantic_release.version import tags_and_versions

log = logging.getLogger(__name__)


@click.command()
@click.pass_context
def publish(ctx: click.Context) -> None:
    """
    This is the magic changelog function that writes out your beautiful changelog
    """
    repo = ctx.obj.repo
    hvcs_client = ctx.obj.hvcs_client
    translator = ctx.obj.version_translator
    build_command = ctx.obj.build_command
    dist_glob_patterns = ctx.obj.dist_glob_patterns
    upload_to_repository = ctx.obj.upload_to_repository
    upload_to_release = ctx.obj.upload_to_release
    twine_settings = ctx.obj.twine_settings

    try:
        subprocess.run(shlex.split(build_command), check=True)
    except subprocess.CalledProcessError as exc:
        ctx.fail(str(exc))

    if upload_to_repository:
        upload(upload_settings=twine_settings, dists=dist_glob_patterns)

    latest_tag = tags_and_versions(repo.tags, translator)[0][0]
    if upload_to_release:
        for pattern in dist_glob_patterns:
            hvcs_client.upload_dists(tag=latest_tag, dist_glob=pattern)

    rprint("[green]:sparkles: Done! :sparkles:")
