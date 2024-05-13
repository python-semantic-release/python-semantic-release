from __future__ import annotations

from logging import getLogger
from os import listdir
from pathlib import Path
from typing import TYPE_CHECKING

# NOTE: use backport with newer API than stdlib
from importlib_resources import files

from semantic_release.changelog.context import (
    ReleaseNotesContext,
    make_changelog_context,
)
from semantic_release.changelog.template import environment, recursive_render
from semantic_release.cli.util import noop_report

if TYPE_CHECKING:
    from jinja2 import Environment

    from semantic_release.changelog.release_history import Release, ReleaseHistory
    from semantic_release.cli.config import RuntimeContext
    from semantic_release.hvcs._base import HvcsBase


log = getLogger(__name__)


def get_release_notes_template(template_dir: Path) -> str:
    """Read the project's template for release notes, falling back to the default."""
    fname = template_dir / ".release_notes.md.j2"
    try:
        return fname.read_text(encoding="utf-8")
    except FileNotFoundError:
        return (
            files("semantic_release")
            .joinpath("data/templates/release_notes.md.j2")
            .read_text(encoding="utf-8")
        )


def render_default_changelog_file(template_env: Environment) -> str:
    changelog_text = (
        files("semantic_release")
        .joinpath("data/templates/CHANGELOG.md.j2")
        .read_text(encoding="utf-8")
    )
    template = template_env.from_string(changelog_text)
    return template.render().rstrip()


def render_release_notes(
    release_notes_template: str,
    template_env: Environment,
) -> str:
    template = template_env.from_string(release_notes_template)
    return template.render().rstrip()


def apply_user_changelog_template_directory(
    template_dir: Path,
    environment: Environment,
    destination_dir: Path,
    noop: bool = False,
) -> list[str]:
    if noop:
        noop_report(
            str.join(
                " ",
                [
                    "would have recursively rendered the template directory",
                    f"{template_dir!r} relative to {destination_dir!r}.",
                    "Paths which would be modified by this operation cannot be",
                    "determined in no-op mode.",
                ],
            )
        )
        return []

    return recursive_render(
        template_dir, environment=environment, _root_dir=destination_dir
    )


def write_default_changelog(
    changelog_file: Path,
    destination_dir: Path,
    environment: Environment,
    noop: bool = False,
) -> str:
    if noop:
        noop_report(
            str.join(
                " ",
                [
                    "would have written your changelog to",
                    str(changelog_file.relative_to(destination_dir)),
                ],
            )
        )
    else:
        changelog_text = render_default_changelog_file(environment)
        changelog_file.write_text(f"{changelog_text}\n", encoding="utf-8")

    return str(changelog_file)


def write_changelog_files(
    runtime_ctx: RuntimeContext,
    release_history: ReleaseHistory,
    hvcs_client: HvcsBase,
    noop: bool = False,
) -> list[str]:
    project_dir = Path(runtime_ctx.repo_dir)
    template_dir = runtime_ctx.template_dir

    changelog_context = make_changelog_context(
        hvcs_client=hvcs_client,
        release_history=release_history,
    )

    changelog_context.bind_to_environment(runtime_ctx.template_environment)

    use_user_template_dir = bool(
        # Directory exists and directory is not empty
        template_dir.exists() and template_dir.is_dir() and listdir(template_dir)
    )

    if use_user_template_dir:
        return apply_user_changelog_template_directory(
            template_dir=template_dir,
            environment=runtime_ctx.template_environment,
            destination_dir=project_dir,
            noop=noop,
        )

    log.info("No contents found in %r, using default changelog template", template_dir)
    return [
        write_default_changelog(
            changelog_file=runtime_ctx.changelog_file,
            destination_dir=project_dir,
            environment=runtime_ctx.template_environment,
            noop=noop,
        )
    ]


def generate_release_notes(
    hvcs_client: HvcsBase,
    release: Release,
    template_dir: Path,
) -> str:
    release_notes_env = ReleaseNotesContext(
        repo_name=hvcs_client.repo_name,
        repo_owner=hvcs_client.owner,
        hvcs_type=hvcs_client.__class__.__name__.lower(),
        version=release["version"],
        release=release,
        filters=(*hvcs_client.get_changelog_context_filters(),),
    ).bind_to_environment(
        # Use a new, non-configurable environment for release notes -
        # not user-configurable at the moment
        environment(template_dir=template_dir)
    )

    return render_release_notes(
        release_notes_template=get_release_notes_template(template_dir),
        template_env=release_notes_env,
    )
