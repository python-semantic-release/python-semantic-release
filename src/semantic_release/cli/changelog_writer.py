from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

# NOTE: use backport with newer API than stdlib
from importlib_resources import files

import semantic_release
from semantic_release.changelog.context import (
    ReleaseNotesContext,
    autofit_text_width,
    create_pypi_url,
    make_changelog_context,
)
from semantic_release.changelog.template import environment, recursive_render
from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.cli.const import (
    DEFAULT_CHANGELOG_NAME_STEM,
    DEFAULT_RELEASE_NOTES_TPL_FILE,
    JINJA2_EXTENSION,
)
from semantic_release.cli.util import noop_report
from semantic_release.errors import InternalError
from semantic_release.globals import logger
from semantic_release.helpers import sort_numerically

if TYPE_CHECKING:  # pragma: no cover
    from jinja2 import Environment

    from semantic_release.changelog.context import ChangelogContext
    from semantic_release.changelog.release_history import Release, ReleaseHistory
    from semantic_release.cli.config import RuntimeContext
    from semantic_release.hvcs._base import HvcsBase


def get_default_tpl_dir(style: str, sub_dir: str | None = None) -> Path:
    module_base_path = Path(str(files(semantic_release.__name__)))
    default_templates_path = module_base_path.joinpath(
        f"data/templates/{style}",
        "" if sub_dir is None else sub_dir.strip("/"),
    )

    if default_templates_path.is_dir():
        return default_templates_path

    raise InternalError(
        str.join(
            " ",
            [
                "Default template directory not found at",
                f"{default_templates_path}. Installation corrupted!",
            ],
        )
    )


def render_default_changelog_file(
    output_format: ChangelogOutputFormat,
    changelog_context: ChangelogContext,
    changelog_style: str,
) -> str:
    tpl_dir = get_default_tpl_dir(style=changelog_style, sub_dir=output_format.value)
    changelog_tpl_file = Path(DEFAULT_CHANGELOG_NAME_STEM).with_suffix(
        str.join(".", ["", output_format.value, JINJA2_EXTENSION.lstrip(".")])
    )

    # Create a new environment as we don't want user's configuration as it might
    # not match our default template structure
    template_env = changelog_context.bind_to_environment(
        environment(
            autoescape=False,
            newline_sequence="\n",
            template_dir=tpl_dir,
        )
    )

    # Using the proper enviroment with the changelog context, render the template
    template = template_env.get_template(str(changelog_tpl_file))
    changelog_content = template.render().rstrip()

    # Normalize line endings to ensure universal newlines because that is what is expected
    # of the content when we write it to a file. When using pathlib.Path.write_text(), it
    # will automatically normalize the file to the OS. At this point after render, we may
    # have mixed line endings because of the read_file() call of the previous changelog
    # (which may be /r/n or /n)
    return str.join(
        "\n", [line.replace("\r", "") for line in changelog_content.split("\n")]
    )


def render_release_notes(
    release_notes_template_file: str,
    template_env: Environment,
) -> str:
    # NOTE: release_notes_template_file must be a relative path to the template directory
    # because jinja2's filtering and template loading filter is janky
    template = template_env.get_template(release_notes_template_file)
    release_notes = template.render().rstrip() + os.linesep

    # Normalize line endings to match the current platform
    return str.join(
        os.linesep, [line.replace("\r", "") for line in release_notes.split("\n")]
    )


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
    output_format: ChangelogOutputFormat,
    changelog_context: ChangelogContext,
    changelog_style: str,
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
        return str(changelog_file)

    changelog_text = render_default_changelog_file(
        output_format=output_format,
        changelog_context=changelog_context,
        changelog_style=changelog_style,
    )
    # write_text() will automatically normalize newlines to the OS, so we just use an universal newline here
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
        mode=runtime_ctx.changelog_mode,
        insertion_flag=runtime_ctx.changelog_insertion_flag,
        prev_changelog_file=runtime_ctx.changelog_file,
        mask_initial_release=runtime_ctx.changelog_mask_initial_release,
    )

    user_templates = []

    # Update known templates list if Directory exists and directory has actual files to render
    if template_dir.is_dir():
        user_templates.extend(
            [
                f
                for f in template_dir.rglob("*")
                if f.is_file() and f.suffix == JINJA2_EXTENSION
            ]
        )

        with suppress(ValueError):
            # do not include a release notes override when considering number of changelog templates
            user_templates.remove(template_dir / DEFAULT_RELEASE_NOTES_TPL_FILE)

    # Render user templates if found
    if len(user_templates) > 0:
        return apply_user_changelog_template_directory(
            template_dir=template_dir,
            environment=changelog_context.bind_to_environment(
                runtime_ctx.template_environment
            ),
            destination_dir=project_dir,
            noop=noop,
        )

    logger.info(
        "No contents found in %r, using default changelog template", template_dir
    )
    return [
        write_default_changelog(
            changelog_file=runtime_ctx.changelog_file,
            destination_dir=project_dir,
            output_format=runtime_ctx.changelog_output_format,
            changelog_context=changelog_context,
            changelog_style=runtime_ctx.changelog_style,
            noop=noop,
        )
    ]


def generate_release_notes(
    hvcs_client: HvcsBase,
    release: Release,
    template_dir: Path,
    history: ReleaseHistory,
    style: str,
    mask_initial_release: bool,
    license_name: str = "",
) -> str:
    users_tpl_file = template_dir / DEFAULT_RELEASE_NOTES_TPL_FILE

    # Determine if the user has a custom release notes template or we should use
    # the default template directory with our default release notes template
    tpl_dir = (
        template_dir
        if users_tpl_file.is_file()
        else get_default_tpl_dir(
            style=style, sub_dir=ChangelogOutputFormat.MARKDOWN.value
        )
    )

    release_notes_tpl_file = (
        users_tpl_file.name
        if users_tpl_file.is_file()
        else DEFAULT_RELEASE_NOTES_TPL_FILE
    )

    release_notes_env = ReleaseNotesContext(
        repo_name=hvcs_client.repo_name,
        repo_owner=hvcs_client.owner,
        hvcs_type=hvcs_client.__class__.__name__.lower(),
        version=release["version"],
        release=release,
        mask_initial_release=mask_initial_release,
        license_name=license_name,
        filters=(
            *hvcs_client.get_changelog_context_filters(),
            create_pypi_url,
            autofit_text_width,
            sort_numerically,
        ),
    ).bind_to_environment(
        # Use a new, non-configurable environment for release notes -
        # not user-configurable at the moment
        environment(autoescape=False, template_dir=tpl_dir)
    )

    # TODO: Remove in v11
    release_notes_env.globals["context"] = release_notes_env.globals["ctx"] = {
        "history": history,
        "mask_initial_release": mask_initial_release,
    }

    return render_release_notes(
        release_notes_template_file=release_notes_tpl_file,
        template_env=release_notes_env,
    )
