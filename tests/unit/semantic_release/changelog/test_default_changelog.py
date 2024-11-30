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
    today_date_str: str,
):
    artificial_release_history.unreleased = {}  # Wipe out unreleased
    hvcs = hvcs_client(example_git_https_url)

    latest_version = next(iter(artificial_release_history.released.keys()))
    latest_release = artificial_release_history.released[latest_version]

    first_version = list(artificial_release_history.released.keys())[-1]

    feat_commit_obj = latest_release["elements"]["feature"][0]
    fix_commit_obj_1 = latest_release["elements"]["fix"][0]
    fix_commit_obj_2 = latest_release["elements"]["fix"][1]
    fix_commit_obj_3 = latest_release["elements"]["fix"][2]
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj_1, ParsedCommit)
    assert isinstance(fix_commit_obj_2, ParsedCommit)
    assert isinstance(fix_commit_obj_3, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_1_url = hvcs.commit_hash_url(fix_commit_obj_1.commit.hexsha)
    fix_commit_1_description = str.join("\n", fix_commit_obj_1.descriptions)

    fix_commit_2_url = hvcs.commit_hash_url(fix_commit_obj_2.commit.hexsha)
    fix_commit_2_description = str.join("\n", fix_commit_obj_2.descriptions)

    fix_commit_3_url = hvcs.commit_hash_url(fix_commit_obj_3.commit.hexsha)
    fix_commit_3_description = str.join("\n", fix_commit_obj_3.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            f"## v{latest_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            # Due to the 100 character limit, hash url will be on the second line
            f"- {fix_commit_2_description.capitalize()}",
            f"  ([`{fix_commit_obj_2.commit.hexsha[:7]}`]({fix_commit_2_url}))",
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_3.scope}**: {fix_commit_3_description.capitalize()}",
            f"  ([`{fix_commit_obj_3.commit.hexsha[:7]}`]({fix_commit_3_url}))",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_1.scope}**: {fix_commit_1_description.capitalize()}",
            f"  ([`{fix_commit_obj_1.commit.hexsha[:7]}`]({fix_commit_1_url}))",
            "",
            "",
            f"## v{first_version} ({today_date_str})",
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
            mask_initial_release=True,
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template_w_a_brk_change(
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    example_git_https_url: str,
    release_history_w_brk_change: ReleaseHistory,
    changelog_md_file: Path,
    today_date_str: str,
):
    hvcs = hvcs_client(example_git_https_url)

    releases = iter(release_history_w_brk_change.released.keys())
    latest_version = next(releases)
    latest_release = release_history_w_brk_change.released[latest_version]

    previous_version = next(releases)
    previous_release = release_history_w_brk_change.released[previous_version]

    first_version = list(release_history_w_brk_change.released.keys())[-1]

    brk_fix_commit_obj = latest_release["elements"]["Bug Fixes"][0]
    feat_commit_obj = previous_release["elements"]["feature"][0]
    fix_commit_obj_1 = previous_release["elements"]["fix"][0]
    fix_commit_obj_2 = previous_release["elements"]["fix"][1]
    fix_commit_obj_3 = previous_release["elements"]["fix"][2]
    assert isinstance(brk_fix_commit_obj, ParsedCommit)
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj_1, ParsedCommit)
    assert isinstance(fix_commit_obj_2, ParsedCommit)
    assert isinstance(fix_commit_obj_3, ParsedCommit)

    brk_fix_commit_url = hvcs.commit_hash_url(brk_fix_commit_obj.commit.hexsha)
    brk_fix_description = str.join("\n", brk_fix_commit_obj.descriptions)
    brk_fix_brking_description = str.join(
        "\n", brk_fix_commit_obj.breaking_descriptions
    )

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_1_url = hvcs.commit_hash_url(fix_commit_obj_1.commit.hexsha)
    fix_commit_1_description = str.join("\n", fix_commit_obj_1.descriptions)

    fix_commit_2_url = hvcs.commit_hash_url(fix_commit_obj_2.commit.hexsha)
    fix_commit_2_description = str.join("\n", fix_commit_obj_2.descriptions)

    fix_commit_3_url = hvcs.commit_hash_url(fix_commit_obj_3.commit.hexsha)
    fix_commit_3_description = str.join("\n", fix_commit_obj_3.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            f"## v{latest_version} ({today_date_str})",
            "",
            "### Bug Fixes",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{brk_fix_commit_obj.scope}**: {brk_fix_description.capitalize()}",
            f"  ([`{brk_fix_commit_obj.commit.hexsha[:7]}`]({brk_fix_commit_url}))",
            "",
            "### BREAKING CHANGES",
            "",
            # Currently does not consider the 100 character limit because the current
            # descriptions are short enough to fit in one line
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                change_desc=brk_fix_brking_description.capitalize(),
            ),
            "",
            "",
            f"## v{previous_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            # Due to the 100 character limit, hash url will be on the second line
            f"- {fix_commit_2_description.capitalize()}",
            f"  ([`{fix_commit_obj_2.commit.hexsha[:7]}`]({fix_commit_2_url}))",
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_3.scope}**: {fix_commit_3_description.capitalize()}",
            f"  ([`{fix_commit_obj_3.commit.hexsha[:7]}`]({fix_commit_3_url}))",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_1.scope}**: {fix_commit_1_description.capitalize()}",
            f"  ([`{fix_commit_obj_1.commit.hexsha[:7]}`]({fix_commit_1_url}))",
            "",
            "",
            f"## v{first_version} ({today_date_str})",
            "",
            "- Initial Release",
        ],
    )

    actual_changelog = render_default_changelog_file(
        output_format=ChangelogOutputFormat.MARKDOWN,
        changelog_context=make_changelog_context(
            hvcs_client=hvcs,
            release_history=release_history_w_brk_change,
            mode=ChangelogMode.INIT,
            prev_changelog_file=changelog_md_file,
            insertion_flag="",
            mask_initial_release=True,
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template_w_multiple_brk_changes(
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    example_git_https_url: str,
    release_history_w_multiple_brk_changes: ReleaseHistory,
    changelog_md_file: Path,
    today_date_str: str,
):
    hvcs = hvcs_client(example_git_https_url)

    releases = iter(release_history_w_multiple_brk_changes.released.keys())
    latest_version = next(releases)
    latest_release = release_history_w_multiple_brk_changes.released[latest_version]

    previous_version = next(releases)
    previous_release = release_history_w_multiple_brk_changes.released[previous_version]

    first_version = list(release_history_w_multiple_brk_changes.released.keys())[-1]

    brk_feat_commit_obj = latest_release["elements"]["Features"][0]
    brk_fix_commit_obj = latest_release["elements"]["Bug Fixes"][0]
    feat_commit_obj = previous_release["elements"]["feature"][0]
    fix_commit_obj_1 = previous_release["elements"]["fix"][0]
    fix_commit_obj_2 = previous_release["elements"]["fix"][1]
    fix_commit_obj_3 = previous_release["elements"]["fix"][2]
    assert isinstance(brk_feat_commit_obj, ParsedCommit)
    assert isinstance(brk_fix_commit_obj, ParsedCommit)
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj_1, ParsedCommit)
    assert isinstance(fix_commit_obj_2, ParsedCommit)
    assert isinstance(fix_commit_obj_3, ParsedCommit)

    brk_feat_commit_url = hvcs.commit_hash_url(brk_feat_commit_obj.commit.hexsha)
    brk_feat_description = str.join("\n", brk_feat_commit_obj.descriptions)
    brk_feat_brking_description = str.join(
        "\n", brk_feat_commit_obj.breaking_descriptions
    )

    brk_fix_commit_url = hvcs.commit_hash_url(brk_fix_commit_obj.commit.hexsha)
    brk_fix_description = str.join("\n", brk_fix_commit_obj.descriptions)
    brk_fix_brking_description = str.join(
        "\n", brk_fix_commit_obj.breaking_descriptions
    )

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_1_url = hvcs.commit_hash_url(fix_commit_obj_1.commit.hexsha)
    fix_commit_1_description = str.join("\n", fix_commit_obj_1.descriptions)

    fix_commit_2_url = hvcs.commit_hash_url(fix_commit_obj_2.commit.hexsha)
    fix_commit_2_description = str.join("\n", fix_commit_obj_2.descriptions)

    fix_commit_3_url = hvcs.commit_hash_url(fix_commit_obj_3.commit.hexsha)
    fix_commit_3_description = str.join("\n", fix_commit_obj_3.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            f"## v{latest_version} ({today_date_str})",
            "",
            "### Bug Fixes",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{brk_fix_commit_obj.scope}**: {brk_fix_description.capitalize()}",
            f"  ([`{brk_fix_commit_obj.commit.hexsha[:7]}`]({brk_fix_commit_url}))",
            "",
            "### Features",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- {brk_feat_description.capitalize()}",
            f"  ([`{brk_feat_commit_obj.commit.hexsha[:7]}`]({brk_feat_commit_url}))",
            "",
            "### BREAKING CHANGES",
            "",
            # Currently does not consider the 100 character limit because the current
            # descriptions are short enough to fit in one line
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{brk_feat_commit_obj.scope}**: "
                    if brk_feat_commit_obj.scope
                    else ""
                ),
                change_desc=brk_feat_brking_description.capitalize(),
            ),
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                change_desc=brk_fix_brking_description.capitalize(),
            ),
            "",
            "",
            f"## v{previous_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            # Due to the 100 character limit, hash url will be on the second line
            f"- {fix_commit_2_description.capitalize()}",
            f"  ([`{fix_commit_obj_2.commit.hexsha[:7]}`]({fix_commit_2_url}))",
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_3.scope}**: {fix_commit_3_description.capitalize()}",
            f"  ([`{fix_commit_obj_3.commit.hexsha[:7]}`]({fix_commit_3_url}))",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_1.scope}**: {fix_commit_1_description.capitalize()}",
            f"  ([`{fix_commit_obj_1.commit.hexsha[:7]}`]({fix_commit_1_url}))",
            "",
            "",
            f"## v{first_version} ({today_date_str})",
            "",
            "- Initial Release",
        ],
    )

    actual_changelog = render_default_changelog_file(
        output_format=ChangelogOutputFormat.MARKDOWN,
        changelog_context=make_changelog_context(
            hvcs_client=hvcs,
            release_history=release_history_w_multiple_brk_changes,
            mode=ChangelogMode.INIT,
            prev_changelog_file=changelog_md_file,
            insertion_flag="",
            mask_initial_release=True,
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template_no_initial_release_mask(
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
    today_date_str: str,
):
    artificial_release_history.unreleased = {}  # Wipe out unreleased
    hvcs = hvcs_client(example_git_https_url)

    latest_version = next(iter(artificial_release_history.released.keys()))
    latest_release = artificial_release_history.released[latest_version]

    first_version = list(artificial_release_history.released.keys())[-1]

    feat_commit_obj = latest_release["elements"]["feature"][0]
    fix_commit_obj_1 = latest_release["elements"]["fix"][0]
    fix_commit_obj_2 = latest_release["elements"]["fix"][1]
    fix_commit_obj_3 = latest_release["elements"]["fix"][2]
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj_1, ParsedCommit)
    assert isinstance(fix_commit_obj_2, ParsedCommit)
    assert isinstance(fix_commit_obj_3, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_1_url = hvcs.commit_hash_url(fix_commit_obj_1.commit.hexsha)
    fix_commit_1_description = str.join("\n", fix_commit_obj_1.descriptions)

    fix_commit_2_url = hvcs.commit_hash_url(fix_commit_obj_2.commit.hexsha)
    fix_commit_2_description = str.join("\n", fix_commit_obj_2.descriptions)

    fix_commit_3_url = hvcs.commit_hash_url(fix_commit_obj_3.commit.hexsha)
    fix_commit_3_description = str.join("\n", fix_commit_obj_3.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "",
            "",
            f"## v{latest_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            # Due to the 100 character limit, hash url will be on the second line
            f"- {fix_commit_2_description.capitalize()}",
            f"  ([`{fix_commit_obj_2.commit.hexsha[:7]}`]({fix_commit_2_url}))",
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_3.scope}**: {fix_commit_3_description.capitalize()}",
            f"  ([`{fix_commit_obj_3.commit.hexsha[:7]}`]({fix_commit_3_url}))",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_1.scope}**: {fix_commit_1_description.capitalize()}",
            f"  ([`{fix_commit_obj_1.commit.hexsha[:7]}`]({fix_commit_1_url}))",
            "",
            "",
            f"## v{first_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
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
            mask_initial_release=False,
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
    today_date_str: str,
):
    hvcs = hvcs_client(example_git_https_url)

    latest_version = next(iter(artificial_release_history.released.keys()))
    latest_release = artificial_release_history.released[latest_version]

    first_version = list(artificial_release_history.released.keys())[-1]

    feat_commit_obj = latest_release["elements"]["feature"][0]
    fix_commit_obj_1 = latest_release["elements"]["fix"][0]
    fix_commit_obj_2 = latest_release["elements"]["fix"][1]
    fix_commit_obj_3 = latest_release["elements"]["fix"][2]
    assert isinstance(feat_commit_obj, ParsedCommit)
    assert isinstance(fix_commit_obj_1, ParsedCommit)
    assert isinstance(fix_commit_obj_2, ParsedCommit)
    assert isinstance(fix_commit_obj_3, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_1_url = hvcs.commit_hash_url(fix_commit_obj_1.commit.hexsha)
    fix_commit_1_description = str.join("\n", fix_commit_obj_1.descriptions)

    fix_commit_2_url = hvcs.commit_hash_url(fix_commit_obj_2.commit.hexsha)
    fix_commit_2_description = str.join("\n", fix_commit_obj_2.descriptions)

    fix_commit_3_url = hvcs.commit_hash_url(fix_commit_obj_3.commit.hexsha)
    fix_commit_3_description = str.join("\n", fix_commit_obj_3.descriptions)

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
            f"## v{latest_version} ({today_date_str})",
            "",
            "### Feature",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{feat_commit_obj.scope}**: {feat_description.capitalize()}",
            f"  ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            # Due to the 100 character limit, hash url will be on the second line
            f"- {fix_commit_2_description.capitalize()}",
            f"  ([`{fix_commit_obj_2.commit.hexsha[:7]}`]({fix_commit_2_url}))",
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_3.scope}**: {fix_commit_3_description.capitalize()}",
            f"  ([`{fix_commit_obj_3.commit.hexsha[:7]}`]({fix_commit_3_url}))",
            "",
            # Due to the 100 character limit, hash url will be on the second line
            f"- **{fix_commit_obj_1.scope}**: {fix_commit_1_description.capitalize()}",
            f"  ([`{fix_commit_obj_1.commit.hexsha[:7]}`]({fix_commit_1_url}))",
            "",
            "",
            f"## v{first_version} ({today_date_str})",
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
            mask_initial_release=True,
        ),
        changelog_style="angular",
    )

    assert expected_changelog == actual_changelog
