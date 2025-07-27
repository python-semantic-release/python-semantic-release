from __future__ import annotations

import os
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from semantic_release.cli.github_actions_output import VersionGitHubActionsOutput
from semantic_release.hvcs.github import Github
from semantic_release.version.version import Version

from tests.const import EXAMPLE_HVCS_DOMAIN, EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.util import actions_output_to_dict

if TYPE_CHECKING:
    from pathlib import Path


BASE_VCS_URL = f"https://{EXAMPLE_HVCS_DOMAIN}/{EXAMPLE_REPO_OWNER}/{EXAMPLE_REPO_NAME}"


@pytest.mark.parametrize(
    "prev_version, version, released, is_prerelease",
    [
        ("1.2.2", "1.2.3", True, False),
        ("1.2.2", "1.2.3-alpha.1", True, True),
        ("1.2.2", "1.2.2", False, False),
        ("1.2.2-alpha.1", "1.2.2-alpha.1", False, True),
        (None, "1.2.3", True, False),
    ],
)
def test_version_github_actions_output_format(
    released: bool, version: str, is_prerelease: bool, prev_version: str
):
    commit_sha = "0" * 40  # 40 zeroes to simulate a SHA-1 hash
    release_notes = dedent(
        """\
        ## Changes
        - Added new feature
        - Fixed bug
        """
    )
    expected_output = (
        dedent(
            f"""\
            released={'true' if released else 'false'}
            version={version}
            tag=v{version}
            is_prerelease={'true' if is_prerelease else 'false'}
            link={BASE_VCS_URL}/releases/tag/v{version}
            previous_version={prev_version or ""}
            commit_sha={commit_sha}
            """
        )
        + f"release_notes<<EOF{os.linesep}{release_notes}EOF{os.linesep}"
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        actual_output_text = VersionGitHubActionsOutput(
            gh_client=Github(f"{BASE_VCS_URL}.git", hvcs_domain=EXAMPLE_HVCS_DOMAIN),
            released=released,
            version=Version.parse(version),
            commit_sha=commit_sha,
            release_notes=release_notes,
            prev_version=Version.parse(prev_version) if prev_version else None,
        ).to_output_text()

    # Evaluate (expected -> actual)
    assert expected_output == actual_output_text


def test_version_github_actions_output_fails_if_missing_released_param():
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        version=Version.parse("1.2.3"),
    )

    # Execute with expected failure
    with pytest.raises(ValueError, match="required outputs were not set"):
        output.to_output_text()


def test_version_github_actions_output_fails_if_missing_commit_sha_param():
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        released=True,
        version=Version.parse("1.2.3"),
    )

    # Execute with expected failure
    with pytest.raises(ValueError, match="required outputs were not set"):
        output.to_output_text()


def test_version_github_actions_output_fails_if_missing_release_notes_param():
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        released=True,
        version=Version.parse("1.2.3"),
    )

    # Execute with expected failure
    with pytest.raises(ValueError, match="required outputs were not set"):
        output.to_output_text()


def test_version_github_actions_output_writes_to_github_output_if_available(
    tmp_path: Path,
):
    mock_output_file = tmp_path / "action.out"
    prev_version_str = "1.2.2"
    version_str = "1.2.3"
    commit_sha = "0" * 40  # 40 zeroes to simulate a SHA-1 hash
    release_notes = dedent(
        """\
        ## Changes
        - Added new feature
        - Fixed bug
        """
    )

    patched_environ = {"GITHUB_OUTPUT": str(mock_output_file.resolve())}

    with mock.patch.dict(os.environ, patched_environ, clear=True):
        VersionGitHubActionsOutput(
            gh_client=Github(f"{BASE_VCS_URL}.git", hvcs_domain=EXAMPLE_HVCS_DOMAIN),
            version=Version.parse(version_str),
            released=True,
            commit_sha=commit_sha,
            release_notes=release_notes,
            prev_version=Version.parse(prev_version_str),
        ).write_if_possible()

    with open(mock_output_file, encoding="utf-8", newline=os.linesep) as rfd:
        action_outputs = actions_output_to_dict(rfd.read())

    # Evaluate (expected -> actual)
    assert version_str == action_outputs["version"]
    assert str(True).lower() == action_outputs["released"]
    assert str(False).lower() == action_outputs["is_prerelease"]
    assert f"{BASE_VCS_URL}/releases/tag/v{version_str}" == action_outputs["link"]
    assert f"v{version_str}" == action_outputs["tag"]
    assert commit_sha == action_outputs["commit_sha"]
    assert prev_version_str == action_outputs["previous_version"]
    assert release_notes == action_outputs["release_notes"]


def test_version_github_actions_output_no_error_if_not_in_gha(
    monkeypatch: pytest.MonkeyPatch,
):
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        version=Version.parse("1.2.3"),
        released=True,
        commit_sha="0" * 40,  # 40 zeroes to simulate a SHA-1 hash
    )

    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    output.write_if_possible()
