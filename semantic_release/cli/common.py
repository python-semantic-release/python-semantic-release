from __future__ import annotations

from typing import TYPE_CHECKING

# NOTE: use backport with newer API than stdlib
from importlib_resources import files

if TYPE_CHECKING:
    from pathlib import Path

    from jinja2 import Environment

    from semantic_release.changelog.release_history import Release
    from semantic_release.version import Version


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


def render_default_changelog_file(template_environment: Environment) -> str:
    changelog_text = (
        files("semantic_release")
        .joinpath("data/templates/CHANGELOG.md.j2")
        .read_text(encoding="utf-8")
    )
    tmpl = template_environment.from_string(changelog_text)
    return tmpl.render().rstrip()


def render_release_notes(
    release_notes_template: str,
    template_environment: Environment,
    version: Version,
    release: Release,
) -> str:
    return (
        template_environment.from_string(release_notes_template)
        .render(version=version, release=release)
        .rstrip()
    )
