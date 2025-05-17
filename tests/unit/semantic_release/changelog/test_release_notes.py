from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

import pytest

# NOTE: use backport with newer API to support 3.7
from importlib_resources import files

import semantic_release
from semantic_release.cli.changelog_writer import generate_release_notes
from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab

if TYPE_CHECKING:
    from semantic_release.changelog.release_history import ReleaseHistory

    from tests.fixtures.example_project import ExProjectDir


@pytest.fixture(scope="module")
def release_notes_template() -> str:
    """Retrieve the semantic-release default release notes template."""
    version_notes_template = files(semantic_release.__name__).joinpath(
        Path("data", "templates", "conventional", "md", ".release_notes.md.j2")
    )
    return version_notes_template.read_text(encoding="utf-8")


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("license_name", ["", "MIT"])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    license_name: str,
    artificial_release_history: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(artificial_release_history.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = artificial_release_history.released[version]

    feat_commit_obj = release["elements"]["feature"][0]
    fix_commit_obj_1 = release["elements"]["fix"][0]
    fix_commit_obj_2 = release["elements"]["fix"][1]
    fix_commit_obj_3 = release["elements"]["fix"][2]
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

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            *(
                [""]
                if not license_name
                else [
                    "",
                    f"_This release is published under the {license_name} License._",
                    "",
                ]
            ),
            "### Feature",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{feat_commit_obj.scope}**: " if feat_commit_obj.scope else ""
                ),
                commit_desc=feat_description.capitalize(),
                short_hash=feat_commit_obj.commit.hexsha[:7],
                url=feat_commit_url,
            ),
            "",
            "### Fix",
            "",
            # Commit 2 is first because it has no scope
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{fix_commit_obj_2.scope}**: " if fix_commit_obj_2.scope else ""
                ),
                commit_desc=fix_commit_2_description.capitalize(),
                short_hash=fix_commit_obj_2.commit.hexsha[:7],
                url=fix_commit_2_url,
            ),
            "",
            # Commit 3 is second because it starts with an A even though it has the same scope as 1
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{fix_commit_obj_3.scope}**: " if fix_commit_obj_3.scope else ""
                ),
                commit_desc=fix_commit_3_description.capitalize(),
                short_hash=fix_commit_obj_3.commit.hexsha[:7],
                url=fix_commit_3_url,
            ),
            "",
            # Commit 1 is last
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{fix_commit_obj_1.scope}**: " if fix_commit_obj_1.scope else ""
                ),
                commit_desc=fix_commit_1_description.capitalize(),
                short_hash=fix_commit_obj_1.commit.hexsha[:7],
                url=fix_commit_1_url,
            ),
            "",
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=artificial_release_history,
        style="conventional",
        mask_initial_release=mask_initial_release,
        license_name=license_name,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_w_a_brk_description(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    release_history_w_brk_change: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(release_history_w_brk_change.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = release_history_w_brk_change.released[version]

    brk_fix_commit_obj = next(iter(release["elements"].values()))[0]
    assert isinstance(brk_fix_commit_obj, ParsedCommit)

    brk_fix_commit_url = hvcs.commit_hash_url(brk_fix_commit_obj.commit.hexsha)
    brk_fix_description = str.join("\n", brk_fix_commit_obj.descriptions)
    brk_fix_brking_description = str.join(
        "\n", brk_fix_commit_obj.breaking_descriptions
    )

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            "",
            "### Bug Fixes",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                commit_desc=brk_fix_description.capitalize(),
                short_hash=brk_fix_commit_obj.commit.hexsha[:7],
                url=brk_fix_commit_url,
            ),
            "",
            "### Breaking Changes",
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
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=release_history_w_brk_change,
        style="conventional",
        mask_initial_release=mask_initial_release,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_w_multiple_brk_changes(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    release_history_w_multiple_brk_changes: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(release_history_w_multiple_brk_changes.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = release_history_w_multiple_brk_changes.released[version]

    brk_fix_commit_obj = release["elements"]["Bug Fixes"][0]
    brk_feat_commit_obj = release["elements"]["Features"][0]
    assert isinstance(brk_fix_commit_obj, ParsedCommit)
    assert isinstance(brk_feat_commit_obj, ParsedCommit)

    brk_fix_commit_url = hvcs.commit_hash_url(brk_fix_commit_obj.commit.hexsha)
    brk_fix_description = str.join("\n", brk_fix_commit_obj.descriptions)
    brk_fix_brking_description = str.join(
        "\n", brk_fix_commit_obj.breaking_descriptions
    )

    brk_feat_commit_url = hvcs.commit_hash_url(brk_feat_commit_obj.commit.hexsha)
    brk_feat_description = str.join("\n", brk_feat_commit_obj.descriptions)
    brk_feat_brking_description = str.join(
        "\n", brk_feat_commit_obj.breaking_descriptions
    )

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            "",
            "### Bug Fixes",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                commit_desc=brk_fix_description.capitalize(),
                short_hash=brk_fix_commit_obj.commit.hexsha[:7],
                url=brk_fix_commit_url,
            ),
            "",
            "### Features",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{brk_feat_commit_obj.scope}**: "
                    if brk_feat_commit_obj.scope
                    else ""
                ),
                commit_desc=brk_feat_description.capitalize(),
                short_hash=brk_feat_commit_obj.commit.hexsha[:7],
                url=brk_feat_commit_url,
            ),
            "",
            "### Breaking Changes",
            "",
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
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=release_history_w_multiple_brk_changes,
        style="conventional",
        mask_initial_release=mask_initial_release,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("license_name", ["", "MIT"])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_first_release_masked(
    example_git_https_url: str,
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    license_name: str,
    single_release_history: ReleaseHistory,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    hvcs = hvcs_client(example_git_https_url)
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            *(
                [""]
                if not license_name
                else [
                    "",
                    f"_This release is published under the {license_name} License._",
                    "",
                ]
            ),
            "- Initial Release",
            "",
        ],
    )

    actual_content = generate_release_notes(
        hvcs_client=hvcs,
        release=release,
        template_dir=Path(""),
        history=single_release_history,
        style="conventional",
        mask_initial_release=True,
        license_name=license_name,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("license_name", ["", "MIT"])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_first_release_unmasked(
    example_git_https_url: str,
    hvcs_client: type[Bitbucket | Gitea | Github | Gitlab],
    license_name: str,
    single_release_history: ReleaseHistory,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    hvcs = hvcs_client(example_git_https_url)
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    feat_commit_obj = release["elements"]["feature"][0]
    assert isinstance(feat_commit_obj, ParsedCommit)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            *(
                [""]
                if not license_name
                else [
                    "",
                    f"_This release is published under the {license_name} License._",
                    "",
                ]
            ),
            "### Feature",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{feat_commit_obj.scope}**: " if feat_commit_obj.scope else ""
                ),
                commit_desc=feat_description.capitalize(),
                short_hash=feat_commit_obj.commit.hexsha[:7],
                url=feat_commit_url,
            ),
            "",
        ],
    )

    actual_content = generate_release_notes(
        hvcs_client=hvcs,
        release=release,
        template_dir=Path(""),
        history=single_release_history,
        style="conventional",
        mask_initial_release=False,
        license_name=license_name,
    )

    assert expected_content == actual_content


def test_release_notes_context_sort_numerically_filter(
    example_git_https_url: str,
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        dedent(
            """\
            {{ [
                    ".. _#5: link",
                    ".. _PR#3: link",
                    ".. _PR#10: link",
                    ".. _#100: link"
                ] | sort_numerically | join("\\n")
            }}
            """
        )
    )

    expected_content = str.join(
        os.linesep,
        dedent(
            """\
            .. _#5: link
            .. _#100: link
            .. _PR#3: link
            .. _PR#10: link
            """
        ).split("\n"),
    )

    actual_content = generate_release_notes(
        hvcs_client=Github(remote_url=example_git_https_url),
        release=release,
        template_dir=example_project_dir,
        history=single_release_history,
        style="conventional",
        mask_initial_release=False,
    )

    assert expected_content == actual_content


def test_release_notes_context_sort_numerically_filter_reversed(
    example_git_https_url: str,
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        dedent(
            """\
            {{ [
                    ".. _#5: link",
                    ".. _PR#3: link",
                    ".. _PR#10: link",
                    ".. _#100: link"
                ] | sort_numerically(reverse=True) | join("\\n")
            }}
            """
        )
    )

    expected_content = str.join(
        os.linesep,
        dedent(
            """\
            .. _#100: link
            .. _#5: link
            .. _PR#10: link
            .. _PR#3: link
            """
        ).split("\n"),
    )

    actual_content = generate_release_notes(
        hvcs_client=Github(remote_url=example_git_https_url),
        release=release,
        template_dir=example_project_dir,
        history=single_release_history,
        style="conventional",
        mask_initial_release=False,
    )

    assert expected_content == actual_content


def test_release_notes_context_pypi_url_filter(
    example_git_https_url: str,
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        """{{ "example-package" | create_pypi_url }}"""
    )

    expected_content = f"https://pypi.org/project/example-package{os.linesep}"

    actual_content = generate_release_notes(
        hvcs_client=Github(remote_url=example_git_https_url),
        release=release,
        template_dir=example_project_dir,
        history=single_release_history,
        style="conventional",
        mask_initial_release=False,
    )

    assert expected_content == actual_content


def test_release_notes_context_pypi_url_filter_tagged(
    example_git_https_url: str,
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        """{{ "example-package" | create_pypi_url(release.version | string) }}"""
    )

    expected_content = f"https://pypi.org/project/example-package/{version}{os.linesep}"

    actual_content = generate_release_notes(
        hvcs_client=Github(remote_url=example_git_https_url),
        release=release,
        template_dir=example_project_dir,
        history=single_release_history,
        style="conventional",
        mask_initial_release=False,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("hvcs_client_class", [Github, Gitlab, Gitea])
def test_release_notes_context_release_url_filter(
    example_git_https_url: str,
    hvcs_client_class: type[Github | Gitlab | Gitea],
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        dedent(
            """\
            {{
                "[%s](%s)" | format(
                    release.version.as_tag(),
                    release.version.as_tag() | create_release_url,
                )
            }}
            """
        )
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        hvcs_client = hvcs_client_class(remote_url=example_git_https_url)

        expected_content = dedent(
            f"""\
            [{version.as_tag()}]({hvcs_client.create_release_url(version.as_tag())})
            """
        )

        actual_content = generate_release_notes(
            hvcs_client=hvcs_client,
            release=release,
            template_dir=example_project_dir,
            history=single_release_history,
            style="conventional",
            mask_initial_release=False,
        )

    assert expected_content == actual_content


@pytest.mark.parametrize("hvcs_client_class", [Github, Gitlab, Gitea, Bitbucket])
def test_release_notes_context_format_w_official_name_filter(
    example_git_https_url: str,
    hvcs_client_class: type[Github | Gitlab | Gitea],
    single_release_history: ReleaseHistory,
    example_project_dir: ExProjectDir,
    change_to_ex_proj_dir: None,
):
    version = list(single_release_history.released.keys())[-1]
    release = single_release_history.released[version]

    example_project_dir.joinpath(".release_notes.md.j2").write_text(
        dedent(
            """\
            {{ "%s" | format_w_official_vcs_name }}
            {{ "{}" | format_w_official_vcs_name }}
            {{ "{vcs_name}" | format_w_official_vcs_name }}
            """
        )
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        hvcs_client = hvcs_client_class(remote_url=example_git_https_url)
        expected_content = dedent(
            f"""\
            {hvcs_client.OFFICIAL_NAME}
            {hvcs_client.OFFICIAL_NAME}
            {hvcs_client.OFFICIAL_NAME}
            """
        )

        actual_content = generate_release_notes(
            hvcs_client=hvcs_client,
            release=release,
            template_dir=example_project_dir,
            history=single_release_history,
            style="conventional",
            mask_initial_release=False,
        )

    assert expected_content == actual_content


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_w_a_notice(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    release_history_w_a_notice: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(release_history_w_a_notice.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = release_history_w_a_notice.released[version]

    notice_commit_obj = next(iter(release["elements"].values()))[0]
    assert isinstance(notice_commit_obj, ParsedCommit)

    notice_commit_url = hvcs.commit_hash_url(notice_commit_obj.commit.hexsha)
    notice_commit_description = str.join("\n", notice_commit_obj.descriptions)
    notice_description = str.join("\n", notice_commit_obj.release_notices)

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            "",
            "### Refactoring",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{notice_commit_obj.scope}**: "
                    if notice_commit_obj.scope
                    else ""
                ),
                commit_desc=notice_commit_description.capitalize().rstrip(),
                short_hash=notice_commit_obj.commit.hexsha[:7],
                url=notice_commit_url,
            ),
            "",
            "### Additional Release Information",
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{notice_commit_obj.scope}**: "
                    if notice_commit_obj.scope
                    else ""
                ),
                change_desc=notice_description.capitalize().rstrip(),
            ),
            "",
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=release_history_w_a_notice,
        style="conventional",
        mask_initial_release=mask_initial_release,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_w_a_notice_n_brk_change(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    release_history_w_notice_n_brk_change: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(release_history_w_notice_n_brk_change.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = release_history_w_notice_n_brk_change.released[version]

    brk_fix_commit_obj = release["elements"]["Bug Fixes"][0]
    notice_commit_obj = release["elements"]["Refactoring"][0]
    assert isinstance(brk_fix_commit_obj, ParsedCommit)
    assert isinstance(notice_commit_obj, ParsedCommit)

    brk_fix_commit_url = hvcs.commit_hash_url(brk_fix_commit_obj.commit.hexsha)
    brk_fix_description = str.join("\n", brk_fix_commit_obj.descriptions)
    brk_fix_brking_description = str.join(
        "\n", brk_fix_commit_obj.breaking_descriptions
    )

    notice_commit_url = hvcs.commit_hash_url(notice_commit_obj.commit.hexsha)
    notice_commit_description = str.join("\n", notice_commit_obj.descriptions)
    notice_description = str.join("\n", notice_commit_obj.release_notices)

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            "",
            "### Bug Fixes",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                commit_desc=brk_fix_description.capitalize().rstrip(),
                short_hash=brk_fix_commit_obj.commit.hexsha[:7],
                url=brk_fix_commit_url,
            ),
            "",
            "### Refactoring",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{notice_commit_obj.scope}**: "
                    if notice_commit_obj.scope
                    else ""
                ),
                commit_desc=notice_commit_description.capitalize().rstrip(),
                short_hash=notice_commit_obj.commit.hexsha[:7],
                url=notice_commit_url,
            ),
            "",
            "### Breaking Changes",
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{brk_fix_commit_obj.scope}**: "
                    if brk_fix_commit_obj.scope
                    else ""
                ),
                change_desc=brk_fix_brking_description.capitalize().rstrip(),
            ),
            "",
            "### Additional Release Information",
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{notice_commit_obj.scope}**: "
                    if notice_commit_obj.scope
                    else ""
                ),
                change_desc=notice_description.capitalize().rstrip(),
            ),
            "",
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=release_history_w_notice_n_brk_change,
        style="conventional",
        mask_initial_release=mask_initial_release,
    )

    assert expected_content == actual_content


@pytest.mark.parametrize("mask_initial_release", [True, False])
@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template_w_multiple_notices(
    example_git_https_url: str,
    hvcs_client: type[Github | Gitlab | Gitea | Bitbucket],
    release_history_w_multiple_notices: ReleaseHistory,
    mask_initial_release: bool,
    today_date_str: str,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    released_versions = iter(release_history_w_multiple_notices.released.keys())
    version = next(released_versions)
    prev_version = next(released_versions)
    hvcs = hvcs_client(example_git_https_url)
    release = release_history_w_multiple_notices.released[version]

    feat_commit_obj = release["elements"]["Features"][0]
    refactor_commit_obj = release["elements"]["Refactoring"][0]
    assert isinstance(refactor_commit_obj, ParsedCommit)
    assert isinstance(feat_commit_obj, ParsedCommit)

    refactor_commit_url = hvcs.commit_hash_url(refactor_commit_obj.commit.hexsha)
    refactor_commit_desc = str.join("\n", refactor_commit_obj.descriptions)
    refactor_commit_notice_desc = str.join("\n", refactor_commit_obj.release_notices)

    feat_commit_url = hvcs.commit_hash_url(feat_commit_obj.commit.hexsha)
    feat_description = str.join("\n", feat_commit_obj.descriptions)
    feat_commit_notice_desc = str.join("\n", feat_commit_obj.release_notices)

    expected_content = str.join(
        os.linesep,
        [
            f"## v{version} ({today_date_str})",
            "",
            "### Features",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{feat_commit_obj.scope}**: " if feat_commit_obj.scope else ""
                ),
                commit_desc=feat_description.capitalize().rstrip(),
                short_hash=feat_commit_obj.commit.hexsha[:7],
                url=feat_commit_url,
            ),
            "",
            "### Refactoring",
            "",
            "- {commit_scope}{commit_desc} ([`{short_hash}`]({url}))".format(
                commit_scope=(
                    f"**{refactor_commit_obj.scope}**: "
                    if refactor_commit_obj.scope
                    else ""
                ),
                commit_desc=refactor_commit_desc.capitalize().rstrip(),
                short_hash=refactor_commit_obj.commit.hexsha[:7],
                url=refactor_commit_url,
            ),
            "",
            "### Additional Release Information",
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{refactor_commit_obj.scope}**: "
                    if refactor_commit_obj.scope
                    else ""
                ),
                change_desc=refactor_commit_notice_desc.capitalize().rstrip(),
            ),
            "",
            "- {commit_scope}{change_desc}".format(
                commit_scope=(
                    f"**{feat_commit_obj.scope}**: " if feat_commit_obj.scope else ""
                ),
                change_desc=feat_commit_notice_desc.capitalize().rstrip(),
            ),
            "",
        ],
    )

    if not isinstance(hvcs, Gitea):
        expected_content += str.join(
            os.linesep,
            [
                "",
                "---",
                "",
                "**Detailed Changes**: [{prev_version}...{new_version}]({version_compare_url})".format(
                    prev_version=prev_version.as_tag(),
                    new_version=version.as_tag(),
                    version_compare_url=hvcs.compare_url(
                        prev_version.as_tag(), version.as_tag()
                    ),
                ),
                "",
            ],
        )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=release,
        template_dir=Path(""),
        history=release_history_w_multiple_notices,
        style="conventional",
        mask_initial_release=mask_initial_release,
    )

    assert expected_content == actual_content
