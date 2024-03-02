from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git import Commit, Object, Repo

# NOTE: use backport with newer API
from importlib_resources import files

import semantic_release
from semantic_release.changelog.context import make_changelog_context
from semantic_release.changelog.release_history import Release, ReleaseHistory
from semantic_release.changelog.template import environment
from semantic_release.commit_parser import ParsedCommit
from semantic_release.enums import LevelBump
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab
from semantic_release.version.translator import Version

from tests.const import TODAY_DATE_STR

if TYPE_CHECKING:
    from git import Actor

    from semantic_release.hvcs import HvcsBase


@pytest.fixture
def default_changelog_template() -> str:
    """Retrieve the semantic-release default changelog template."""
    version_notes_template = files(semantic_release.__name__).joinpath(
        Path("data", "templates", "CHANGELOG.md.j2")
    )
    return version_notes_template.read_text(encoding="utf-8")


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
                tagged_date=datetime.utcnow(),
                elements={
                    "feature": [feat_commit_parsed],
                    "fix": [fix_commit_parsed],
                },
            )
        },
    )


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template(
    default_changelog_template: str,
    hvcs_client: type[HvcsBase],
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
):
    version_str = "1.0.0"
    version = Version.parse(version_str)
    rh = artificial_release_history
    rh.unreleased = {}  # Wipe out unreleased

    feat_commit_obj = artificial_release_history.released[version]["elements"][
        "feature"
    ][0]
    feat_commit_url = hvcs_client(example_git_https_url).commit_hash_url(
        feat_commit_obj.commit.hexsha
    )
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_obj = artificial_release_history.released[version]["elements"]["fix"][0]
    fix_commit_url = hvcs_client(example_git_https_url).commit_hash_url(
        fix_commit_obj.commit.hexsha
    )
    fix_description = str.join("\n", fix_commit_obj.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            f"## v{version_str} ({TODAY_DATE_STR})",
            "### Feature",
            f"* {feat_description} ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "### Fix",
            f"* {fix_description} ([`{fix_commit_obj.commit.hexsha[:7]}`]({fix_commit_url}))",
            "",
        ],
    )
    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release_history=rh,
    )
    context.bind_to_environment(env)
    actual_changelog = env.from_string(default_changelog_template).render()
    assert expected_changelog == actual_changelog


@pytest.mark.parametrize("hvcs_client", [Github, Gitlab, Gitea, Bitbucket])
def test_default_changelog_template_w_unreleased_changes(
    default_changelog_template: str,
    hvcs_client: type[HvcsBase],
    example_git_https_url: str,
    artificial_release_history: ReleaseHistory,
):
    version_str = "1.0.0"
    version = Version.parse(version_str)

    feat_commit_obj = artificial_release_history.released[version]["elements"][
        "feature"
    ][0]
    feat_commit_url = hvcs_client(example_git_https_url).commit_hash_url(
        feat_commit_obj.commit.hexsha
    )
    feat_description = str.join("\n", feat_commit_obj.descriptions)

    fix_commit_obj = artificial_release_history.released[version]["elements"]["fix"][0]
    fix_commit_url = hvcs_client(example_git_https_url).commit_hash_url(
        fix_commit_obj.commit.hexsha
    )
    fix_description = str.join("\n", fix_commit_obj.descriptions)

    expected_changelog = str.join(
        "\n",
        [
            "# CHANGELOG",
            "## Unreleased",
            "### Feature",
            f"* {feat_description} ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            f"## v{version_str} ({TODAY_DATE_STR})",
            "### Feature",
            f"* {feat_description} ([`{feat_commit_obj.commit.hexsha[:7]}`]({feat_commit_url}))",
            "### Fix",
            f"* {fix_description} ([`{fix_commit_obj.commit.hexsha[:7]}`]({fix_commit_url}))",
            "",
        ],
    )
    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    context = make_changelog_context(
        hvcs_client=hvcs_client(remote_url=example_git_https_url),
        release_history=artificial_release_history,
    )
    context.bind_to_environment(env)
    actual_changelog = env.from_string(default_changelog_template).render()
    assert expected_changelog == actual_changelog
