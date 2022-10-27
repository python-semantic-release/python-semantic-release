import logging
import os

import click
# NOTE: use backport with newer API than stdlib
from importlib_resources import files
from rich import print as rprint

from semantic_release.changelog import recursive_render, release_history
from semantic_release.changelog.context import make_changelog_context

log = logging.getLogger(__name__)


@click.command()
# TODO: dry run?
@click.pass_context
def changelog(ctx: click.Context) -> None:
    """
    This is the magic changelog function that writes out your beautiful changelog
    """
    repo = ctx.obj.repo
    parser = ctx.obj.commit_parser
    translator = ctx.obj.version_translator
    hvcs_client = ctx.obj.hvcs_client
    env = ctx.obj.template_environment
    template_dir = ctx.obj.template_dir
    default_output_file = ctx.obj.default_changelog_output_file

    rh = release_history(repo=repo, translator=translator, commit_parser=parser)
    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client, release_history=rh
    )
    changelog_context.bind_to_environment(env)
    if not os.path.exists(template_dir):
        log.info("Path %r not found, using default changelog template", template_dir)
        default_changelog_text = (
            files("semantic_release")
            .joinpath("data/templates/CHANGELOG.md.j2")
            .read_text(encoding="utf-8")
        )
        tmpl = env.from_string(default_changelog_text).stream()
        with open(default_output_file, "w+", encoding="utf-8") as f:
            tmpl.dump(f)
    else:
        log.debug("Rendering whole directory %r recursively")
        recursive_render(template_dir, environment=env, _root_dir=repo.working_dir)

    # TODO: --post?

    rprint("[green]:sparkles: Done! :sparkles:")
