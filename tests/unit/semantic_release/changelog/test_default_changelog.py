from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# NOTE: use backport with newer API
from importlib_resources import files

import semantic_release
from semantic_release.changelog.context import ChangelogMode, make_changelog_context
from semantic_release.cli.changelog_writer import render_default_changelog_file
from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.commit_parser import ParsedCommit
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab

from tests.const import TODAY_DATE_STR

if TYPE_CHECKING:
    from semantic_release.changelog.release_history import ReleaseHistory


@pytest.fixture(scope="module")
def default_changelog_template() -> str:
    """Retrieve the semantic-release default changelog template."""
    version_notes_template = files(semantic_release.__name__).joinpath(
        Path("data", "templates", "angular", "md", "CHANGELOG.md.j2")
    )
    return version_notes_template.read_text(encoding="utf-8")


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template(
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    artificial_release_history.unreleased = {}  # Wipe out unreleased
    hvcs = hvcs_client(example_git_https_url)

    latest_version = next(iter(artificial_release_history.released.keys()))
    latest_release = artificial_release_history.released[latest_version]

    first_version = list(artificial_release_history.released.keys())[-1]

    feat_commit_obj = latest_release["elements"]["feature"][0]
    fix_commit_obj = latest_release["elements"]["fix"][0]
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_url = hvcs.commit_hash_url(fix_commit_obj.commit.hexsha)
    fix_description = str.join("\n", fix_commit_obj.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            f"## v{latest_version} ({TODAY_DATE_STR})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj.scope}**: {fix_description.capitalize()}",
            f"  ([`{fix_commit_obj.commit.hexsha[:7]}`]({fix_commit_url}))",
            "",
            "",
            f"## v{first_version} ({TODAY_DATE_STR})",
            "",
            "- Initial Release",
        ],
    )

    actual_changelog = render_default_changelog_file(
        output_format=ChangelogOutputFormat.MARKDOWN,
        changelog_context=make_changelog_context(
            hvcs_client=hvcs,
            release_history=artificial_release_history,
            mode=ChangelogMode.INIT,
            prev_changelog_file=changelog_md_file,
            insertion_flag="",
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template_w_unreleased_changes(
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    hvcs = hvcs_client(example_git_https_url)

    latest_version = next(iter(artificial_release_history.released.keys()))
    latest_release = artificial_release_history.released[latest_version]

    first_version = list(artificial_release_history.released.keys())[-1]

    feat_commit_obj = latest_release["elements"]["feature"][0]
    fix_commit_obj = latest_release["elements"]["fix"][0]
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_url = hvcs.commit_hash_url(fix_commit_obj.commit.hexsha)
    fix_description = str.join("\n", fix_commit_obj.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            "## Unreleased",
            "",
            "### Feature",
            "",
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "",
            f"## v{latest_version} ({TODAY_DATE_STR})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {fix_description[0].capitalize()}{fix_description[1:]}",
            f"  ([`{fix_commit_obj.commit.hexsha[:7]}`]({fix_commit_url}))",
            "",
            "",
            f"## v{first_version} ({TODAY_DATE_STR})",
            "",
            "- Initial Release",
        ],
    )

    actual_changelog = render_default_changelog_file(
        output_format=ChangelogOutputFormat.MARKDOWN,
        changelog_context=make_changelog_context(
            hvcs_client=hvcs,
            release_history=artificial_release_history,
            mode=ChangelogMode.INIT,
            prev_changelog_file=changelog_md_file,
            insertion_flag="",
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog
