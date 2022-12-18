# NOTE: use backport with newer API than stdlib
from importlib_resources import files
from jinja2 import Environment

from semantic_release.changelog.release_history import Release
from semantic_release.version import Version


def render_default_changelog_file(template_environment: Environment) -> str:
    changelog_text = (
        files("semantic_release")
        .joinpath("data/templates/CHANGELOG.md.j2")
        .read_text(encoding="utf-8")
    )
    tmpl = template_environment.from_string(changelog_text)
    return tmpl.render()


def render_release_notes(
    template_environment: Environment, version: Version, release: Release
) -> str:
    release_template = (
        files("semantic_release")
        .joinpath("data/templates/release_notes.md.j2")
        .read_text(encoding="utf-8")
    )
    return template_environment.from_string(release_template).render(
        version=version, release=release
    )
