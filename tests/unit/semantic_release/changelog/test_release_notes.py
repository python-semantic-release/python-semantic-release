from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git import Commit, Repo
from git.objects import Object

# NOTE: use backport with newer API to support 3.7
from importlib_resources import files

import semantic_release
from semantic_release.changelog.release_history import Release, ReleaseHistory
from semantic_release.cli.changelog_writer import generate_release_notes
from semantic_release.commit_parser import ParsedCommit
from semantic_release.enums import LevelBump
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab
from semantic_release.version import Version

from tests.const import TODAY_DATE_STR

if TYPE_CHECKING:
    from git import Actor

    from semantic_release.hvcs import HvcsBase


@pytest.fixture
def artificial_release_history(commit_author: Actor):
    version = Version.parse("1.1.0-alpha.3")
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

    return ReleaseHistory(
        unreleased={},
        released={
            version: Release(
                tagger=commit_author,
                committer=commit_author,
                tagged_date=datetime.now(),
                elements={
                    "fix": [fix_commit_parsed],
                },
                version=version,
            )
        },
    )


@pytest.fixture
def release_notes_template() -> str:
    """Retrieve the semantic-release default release notes template."""
    version_notes_template = files(semantic_release.__name__).joinpath(
        Path("data", "templates", "angular", "md", ".release_notes.md.j2")
    )
    return version_notes_template.read_text(encoding="utf-8")


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_release_notes_template(
    example_git_https_url: str,
    hvcs_client: type[HvcsBase],
    artificial_release_history: ReleaseHistory,
):
    """
    Unit test goal: just make sure it renders the release notes template without error.

    Scenarios are better suited for all the variations (commit types).
    """
    version_str = "1.1.0-alpha.3"
    version = Version.parse(version_str)
    commit_obj = artificial_release_history.released[version]["elements"]["fix"][0]
    commit_url = hvcs_client(example_git_https_url).commit_hash_url(
        commit_obj.commit.hexsha
    )
    commit_description = str.join(os.linesep, commit_obj.descriptions)
    expected_content = str.join(
        os.linesep,
        [
            f"## v{version_str} ({TODAY_DATE_STR})",
            "",
            "### Fix",
            "",
            f"* {commit_description} ([`{commit_obj.commit.hexsha[:7]}`]({commit_url}))",
            "",
        ],
    )

    actual_content = generate_release_notes(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release=artificial_release_history.released[version],
        template_dir=Path(""),
        history=artificial_release_history,
        style="angular",
    )

    assert expected_content == actual_content
