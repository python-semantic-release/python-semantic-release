from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from git.repo.base import Repo

from semantic_release.changelog.release_history import ReleaseHistory

if TYPE_CHECKING:  # pragma: no cover
    from semantic_release.context import SemanticReleaseContext
    from semantic_release.enums import LevelBump
    from semantic_release.version import Version


def build_release_history(
    ctx: SemanticReleaseContext,
    repo: Repo | None = None,
) -> ReleaseHistory:
    """
    Build release history by parsing git commits in the repository.

    This function reads the git history, parses commits using the configured
    commit parser, and organizes them into a ReleaseHistory structure.

    :param ctx: The SemanticReleaseContext with configuration.
    :param repo: Optional GitPython Repo instance. If not provided, opens the
        repo from ctx.repo_dir.

    :return: ReleaseHistory containing parsed commits organized by version.
    """
    if repo is None:
        with Repo(str(ctx.repo_dir)) as git_repo:
            return ReleaseHistory.from_git_history(
                repo=git_repo,
                translator=ctx.version_translator,
                commit_parser=ctx.commit_parser,
                exclude_commit_patterns=ctx.changelog_excluded_commit_patterns,
            )
    else:
        return ReleaseHistory.from_git_history(
            repo=repo,
            translator=ctx.version_translator,
            commit_parser=ctx.commit_parser,
            exclude_commit_patterns=ctx.changelog_excluded_commit_patterns,
        )


def render_changelog(
    ctx: SemanticReleaseContext,
    release_history: ReleaseHistory,
    prev_changelog_file: Path | None = None,
) -> str:
    """
    Render a changelog from release history.

    This function renders the full changelog using the configured template
    and output format.

    :param ctx: The SemanticReleaseContext with configuration.
    :param release_history: The ReleaseHistory to render.
    :param prev_changelog_file: Optional path to existing changelog file for
        update mode.

    :return: The rendered changelog as a string.
    """
    from semantic_release.changelog.context import make_changelog_context
    from semantic_release.cli.changelog_writer import render_default_changelog_file
    from semantic_release.cli.const import DEFAULT_CHANGELOG_NAME_STEM, JINJA2_EXTENSION

    if prev_changelog_file is None:
        prev_changelog_file = ctx.changelog_file

    changelog_context = make_changelog_context(
        hvcs_client=ctx.hvcs_client,
        release_history=release_history,
        mode=ctx.changelog_mode,
        prev_changelog_file=prev_changelog_file,
        insertion_flag=ctx.changelog_insertion_flag,
        mask_initial_release=ctx.changelog_mask_initial_release,
    )
    user_tpl_file = ctx.template_dir.joinpath(
        Path(DEFAULT_CHANGELOG_NAME_STEM).with_suffix(
            str.join(
                ".",
                ["", ctx.changelog_output_format.value, JINJA2_EXTENSION.lstrip(".")],
            )
        )
    )

    if user_tpl_file.exists():
        template_env = changelog_context.bind_to_environment(ctx.template_environment)
        template = template_env.get_template(user_tpl_file.name)
        changelog_content = template.render().rstrip()
    else:
        changelog_content = render_default_changelog_file(
            output_format=ctx.changelog_output_format,
            changelog_context=changelog_context,
            changelog_style=ctx.changelog_style,
        )

    return str.join(
        "\n", [line.replace("\r", "") for line in changelog_content.split("\n")]
    )


def render_release_notes(
    ctx: SemanticReleaseContext,
    release_history: ReleaseHistory,
    version: Version,
    license_name: str = "",
) -> str:
    """
    Render release notes for a specific version.

    :param ctx: The SemanticReleaseContext with configuration.
    :param release_history: The ReleaseHistory containing the release.
    :param version: The Version to render release notes for.
    :param license_name: Optional license name to include in the notes.

    :raises ValueError: If the version is not found in release_history.

    :return: The rendered release notes as a string.
    """
    from semantic_release.cli.changelog_writer import generate_release_notes

    if version not in release_history.released:
        raise ValueError(f"Version {version} not found in release history")

    release = release_history.released[version]

    return generate_release_notes(
        hvcs_client=ctx.hvcs_client,
        release=release,
        template_dir=ctx.template_dir,
        history=release_history,
        style=ctx.changelog_style,
        mask_initial_release=ctx.changelog_mask_initial_release,
        license_name=license_name,
    )


def compute_next_version(
    ctx: SemanticReleaseContext,
    repo: Repo | None = None,
    force_level: LevelBump | None = None,
) -> Version:
    """
    Compute the next version based on commits since the last release.

    :param ctx: The SemanticReleaseContext with configuration.
    :param repo: Optional GitPython Repo instance. If not provided, opens the
        repo from ctx.repo_dir.
    :param force_level: Optional level to force (overrides commit-based calculation).

    :return: The next Version.
    """
    from semantic_release.version.algorithm import next_version as algo_next_version

    if force_level is not None:
        # Use forced level bump
        from semantic_release.cli.commands.version import version_from_forced_level

        return version_from_forced_level(
            repo_dir=ctx.repo_dir,
            forced_level_bump=force_level,
            translator=ctx.version_translator,
        )

    if repo is None:
        with Repo(str(ctx.repo_dir)) as git_repo:
            return algo_next_version(
                repo=git_repo,
                translator=ctx.version_translator,
                commit_parser=ctx.commit_parser,
                prerelease=ctx.prerelease,
                major_on_zero=ctx.major_on_zero,
                allow_zero_version=ctx.allow_zero_version,
            )
    else:
        return algo_next_version(
            repo=repo,
            translator=ctx.version_translator,
            commit_parser=ctx.commit_parser,
            prerelease=ctx.prerelease,
            major_on_zero=ctx.major_on_zero,
            allow_zero_version=ctx.allow_zero_version,
        )


__all__ = [
    "build_release_history",
    "render_changelog",
    "render_release_notes",
    "compute_next_version",
]
