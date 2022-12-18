import logging
import shlex
import subprocess

import click
from twine.commands.upload import upload

from semantic_release.cli.util import noop_report
from semantic_release.version import tags_and_versions

log = logging.getLogger(__name__)


@click.command(short_help="Build and publish a distribution")
@click.option(
    "--upload-to-repository/--no-upload-to-repository",
    "upload_to_repository",
    default=True,
    help="Whether or not to upload any built artefacts to the configured artefact repository",
)
@click.option(
    "--upload-to-vcs-release/--no-upload-to-vcs-release",
    "upload_to_vcs_release",
    default=True,
    help="Whether or not to upload any built artefacts to the latest release",
)
@click.pass_context
def publish(
    ctx: click.Context,
    upload_to_repository: bool = True,
    upload_to_vcs_release: bool = True,
) -> None:
    """
    Build and publish a distribution to a Python package repository
    or VCS release.
    """
    runtime = ctx.obj
    repo = runtime.repo
    hvcs_client = runtime.hvcs_client
    translator = runtime.version_translator
    build_command = runtime.build_command
    dist_glob_patterns = runtime.dist_glob_patterns
    upload_to_repository &= runtime.upload_to_repository
    upload_to_vcs_release &= runtime.upload_to_vcs_release
    twine_settings = runtime.twine_settings

    if upload_to_repository and not twine_settings:
        ctx.fail(
            "Your configuration sets upload_to_repository = true, but your twine "
            "upload settings are invalid"
        )

    if runtime.global_cli_options.noop:
        noop_report(f"would have run the build_command {build_command!r}")
    else:
        try:
            log.info("Running build command %s", build_command)
            subprocess.run(shlex.split(build_command), check=True)
        except subprocess.CalledProcessError as exc:
            ctx.fail(str(exc))

    if runtime.global_cli_options.noop and upload_to_repository:
        noop_report(
            "would have uploaded files matching any of the globs "
            ", ".join(repr(g) for g in dist_glob_patterns) + " to your repository"
        )
    elif upload_to_repository:
        log.info("Uploading distributions to repository")
        upload(upload_settings=twine_settings, dists=dist_glob_patterns)

    latest_tag = tags_and_versions(repo.tags, translator)[0][0]
    if upload_to_vcs_release and runtime.global_cli_options.noop:
        noop_report(
            "would have uploaded files matching any of the globs "
            + ", ".join(repr(g) for g in dist_glob_patterns)
            + " to a remote VCS release, if supported"
        )
    elif upload_to_vcs_release:
        log.info("Uploading distributions to release")
        for pattern in dist_glob_patterns:
            hvcs_client.upload_dists(tag=latest_tag, dist_glob=pattern)
