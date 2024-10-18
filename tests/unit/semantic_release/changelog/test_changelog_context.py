from __future__ import annotations

import os
from datetime import datetime
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from git import Commit, Object, Repo

from semantic_release.changelog.context import ChangelogMode, make_changelog_context
from semantic_release.changelog.release_history import Release, ReleaseHistory
from semantic_release.changelog.template import environment
from semantic_release.commit_parser import ParsedCommit
from semantic_release.enums import LevelBump
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab
from semantic_release.version.translator import Version

from tests.const import EXAMPLE_CHANGELOG_MD_CONTENT

if TYPE_CHECKING:
    from pathlib import Path

    from git import Actor

    from tests.fixtures.git_repo import BuildRepoFn


@pytest.fixture
def changelog_tpl_github_context() -> str:
    """Returns an changelog template which uses all the GitHub configured filters"""
    return dedent(
        r"""
        # Changelog

        > Repository: {{ "[%s](%s)" | format(context.hvcs_type | capitalize, "/" | create_repo_url) }}

        ## v2.0.0

        {{ "[Change Summary](%s)" | format("v1.0.0" | compare_url("v2.0.0")) }}

        ### Bug Fixes

        - Fixed a minor bug {{ "([#%s](%s))" | format(22, 22 | pull_request_url) }}
        - **cli:** fix a problem {{ "([%s](%s))" | format("000000", "000000" | commit_hash_url) }}

        ### Resolved Issues

        - {{ "[#%s](%s)" | format(19, 19 | issue_url) }}
        """
    ).lstrip()


@pytest.fixture
def changelog_tpl_gitea_context() -> str:
    """Returns an changelog template which uses all the Gitea configured filters"""
    return dedent(
        r"""
        # Changelog

        > Repository: {{ "[%s](%s)" | format(context.hvcs_type | capitalize, "/" | create_repo_url) }}

        ## v2.0.0

        ### Bug Fixes

        - Fixed a minor bug {{ "([#%s](%s))" | format(22, 22 | pull_request_url) }}
        - **cli:** fix a problem {{ "([%s](%s))" | format("000000", "000000" | commit_hash_url) }}

        ### Resolved Issues

        - {{ "[#%s](%s)" | format(19, 19 | issue_url) }}
        """
    ).lstrip()


@pytest.fixture
def changelog_tpl_gitlab_context() -> str:
    """Returns an changelog template which uses all the GitLab configured filters"""
    return dedent(
        r"""
        # Changelog

        > Repository: {{ "[%s](%s)" | format(context.hvcs_type | capitalize, "/" | create_repo_url) }}

        ## v2.0.0

        {{ "[Change Summary](%s)" | format("v1.0.0" | compare_url("v2.0.0")) }}

        ### Bug Fixes

        - Fixed a minor bug {{ "([#%s](%s))" | format(22, 22 | merge_request_url) }}
        - Fixed a performance bug {{ "([#%s](%s))" | format(25, 25 | pull_request_url) }}
        - **cli:** fix a problem {{ "([%s](%s))" | format("000000", "000000" | commit_hash_url) }}

        ### Resolved Issues

        - {{ "[#%s](%s)" | format(19, 19 | issue_url) }}
        """
    ).lstrip()


@pytest.fixture
def changelog_tpl_bitbucket_context() -> str:
    """Returns an changelog template which uses all the BitBucket configured filters"""
    return dedent(
        r"""
        # Changelog

        > Repository: {{ "[%s](%s)" | format(context.hvcs_type | capitalize, "/" | create_repo_url) }}

        ## v2.0.0

        {{ "[Change Summary](%s)" | format("v1.0.0" | compare_url("v2.0.0")) }}

        ### Bug Fixes

        - Fixed a minor bug {{ "([#%s](%s))" | format(22, 22 | pull_request_url) }}
        - **cli:** fix a problem {{ "([%s](%s))" | format("000000", "000000" | commit_hash_url) }}
        """
    ).lstrip()


@pytest.fixture
def artificial_release_history(commit_author: Actor):
    version = Version.parse("1.0.0")

    commit_subject = "fix(cli): fix a problem"

    fix_commit = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=commit_subject,
    )

    fix_commit_parsed = ParsedCommit(
        bump=LevelBump.PATCH,
        type="fix",
        scope="cli",
        descriptions=[commit_subject],
        breaking_descriptions=[],
        commit=fix_commit,
    )

    commit_subject = "feat(cli): add a new feature"

    feat_commit = Commit(
        Repo("."),
        Object.NULL_HEX_SHA[:20].encode("utf-8"),
        message=commit_subject,
    )

    feat_commit_parsed = ParsedCommit(
        bump=LevelBump.MINOR,
        type="feat",
        scope="cli",
        descriptions=[commit_subject],
        breaking_descriptions=[],
        commit=feat_commit,
    )

    return ReleaseHistory(
        unreleased={
            "feature": [feat_commit_parsed],
        },
        released={
            version: Release(
                tagger=commit_author,
                committer=commit_author,
                tagged_date=datetime.now(),
                elements={
                    "feature": [feat_commit_parsed],
                    "fix": [fix_commit_parsed],
                },
                version=version,
            )
        },
    )


def test_changelog_context_bitbucket(
    changelog_tpl_bitbucket_context: str,
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    hvcs = Bitbucket(example_git_https_url)

    expected_changelog = str.join(
        "\n",
        [
            "# Changelog",
            "",
            f'> Repository: [{hvcs.__class__.__name__.capitalize()}]({hvcs.create_repo_url("")})',
            "",
            "## v2.0.0",
            "",
            f'[Change Summary]({hvcs.compare_url("v1.0.0", "v2.0.0")})',
            "",
            "### Bug Fixes",
            "",
            f"- Fixed a minor bug ([#22]({hvcs.pull_request_url(22)}))",
            f'- **cli:** fix a problem ([000000]({hvcs.commit_hash_url("000000")}))',
            "",
        ],
    )

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs,
        release_history=artificial_release_history,
        mode=ChangelogMode.INIT,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl_bitbucket_context).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_github(
    changelog_tpl_github_context: str,
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    hvcs = Github(example_git_https_url)

    expected_changelog = str.join(
        "\n",
        [
            "# Changelog",
            "",
            f'> Repository: [{hvcs.__class__.__name__.capitalize()}]({hvcs.create_repo_url("")})',
            "",
            "## v2.0.0",
            "",
            f'[Change Summary]({hvcs.compare_url("v1.0.0", "v2.0.0")})',
            "",
            "### Bug Fixes",
            "",
            f"- Fixed a minor bug ([#22]({hvcs.pull_request_url(22)}))",
            f'- **cli:** fix a problem ([000000]({hvcs.commit_hash_url("000000")}))',
            "",
            "### Resolved Issues",
            "",
            f"- [#19]({hvcs.issue_url(19)})",
            "",
        ],
    )

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs,
        release_history=artificial_release_history,
        mode=ChangelogMode.INIT,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl_github_context).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_gitea(
    changelog_tpl_gitea_context: str,
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    hvcs = Gitea(example_git_https_url)

    expected_changelog = str.join(
        "\n",
        [
            "# Changelog",
            "",
            f'> Repository: [{hvcs.__class__.__name__.capitalize()}]({hvcs.create_repo_url("")})',
            "",
            "## v2.0.0",
            "",
            "### Bug Fixes",
            "",
            f"- Fixed a minor bug ([#22]({hvcs.pull_request_url(22)}))",
            f'- **cli:** fix a problem ([000000]({hvcs.commit_hash_url("000000")}))',
            "",
            "### Resolved Issues",
            "",
            f"- [#19]({hvcs.issue_url(19)})",
            "",
        ],
    )

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs,
        release_history=artificial_release_history,
        mode=ChangelogMode.INIT,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl_gitea_context).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_gitlab(
    changelog_tpl_gitlab_context: str,
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    hvcs = Gitlab(example_git_https_url)

    expected_changelog = str.join(
        "\n",
        [
            "# Changelog",
            "",
            f'> Repository: [{hvcs.__class__.__name__.capitalize()}]({hvcs.create_repo_url("")})',
            "",
            "## v2.0.0",
            "",
            f'[Change Summary]({hvcs.compare_url("v1.0.0", "v2.0.0")})',
            "",
            "### Bug Fixes",
            "",
            f"- Fixed a minor bug ([#22]({hvcs.merge_request_url(22)}))",
            f"- Fixed a performance bug ([#25]({hvcs.pull_request_url(25)}))",
            f'- **cli:** fix a problem ([000000]({hvcs.commit_hash_url("000000")}))',
            "",
            "### Resolved Issues",
            "",
            f"- [#19]({hvcs.issue_url(19)})",
            "",
        ],
    )

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs,
        release_history=artificial_release_history,
        mode=ChangelogMode.INIT,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl_gitlab_context).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_read_file(
    example_git_https_url: str,
    build_configured_base_repo: BuildRepoFn,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
    change_to_ex_proj_dir: Path,
    example_project_dir: Path,
):
    build_configured_base_repo(example_project_dir)

    # normalize expected to os specific newlines
    expected_changelog = str.join(
        os.linesep,
        [
            *[
                line.replace("\r", "")
                for line in EXAMPLE_CHANGELOG_MD_CONTENT.strip().split("\n")
            ],
            "",
        ],
    )

    changelog_tpl = """{{ "%s" | read_file | trim }}%ls""".replace(
        "%s", str(changelog_md_file)
    ).replace("%ls", os.linesep)

    env = environment(
        newline_sequence="\n" if os.linesep == "\n" else "\r\n",
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,
    )
    context = make_changelog_context(
        hvcs_client=Gitlab(example_git_https_url),
        release_history=artificial_release_history,
        mode=ChangelogMode.UPDATE,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl).render()

    # Evaluate
    assert expected_changelog.encode() == actual_changelog.encode()


@pytest.mark.parametrize("file_path", ["", "nonexistent.md"])
def test_changelog_context_read_file_fails_gracefully(
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
    file_path: str,
):
    changelog_tpl = """{{ "%s" | read_file }}""".replace("%s", file_path)
    expected_changelog = ""

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=Gitlab(example_git_https_url),
        release_history=artificial_release_history,
        mode=ChangelogMode.UPDATE,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_autofit_text_width(
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    changelog_tpl = """{{ "This is a long line that should be autofitted" | autofit_text_width(20) }}"""
    expected_changelog = "This is a long line\nthat should be\nautofitted"

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=Gitlab(example_git_https_url),
        release_history=artificial_release_history,
        mode=ChangelogMode.UPDATE,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl).render()

    # Evaluate
    assert expected_changelog == actual_changelog


def test_changelog_context_autofit_text_width_w_indent(
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
    changelog_md_file: Path,
):
    changelog_tpl = """{{ "This is a long line that should be autofitted" | autofit_text_width(20, indent_size=2) }}"""
    expected_changelog = "This is a long line\n  that should be\n  autofitted"

    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=Gitlab(example_git_https_url),
        release_history=artificial_release_history,
        mode=ChangelogMode.UPDATE,
        prev_changelog_file=changelog_md_file,
        insertion_flag="",
    )
    context.bind_to_environment(env)

    # Create changelog from template with environment
    actual_changelog = env.from_string(changelog_tpl).render()

    # Evaluate
    assert expected_changelog == actual_changelog
