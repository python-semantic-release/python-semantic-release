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
            id=
            upload_url=
            assets=[]
            assets_dist={{}}
            """
        ).replace("\n", os.linesep)
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


def test_version_github_actions_output_with_release_id():
    """Test that release_id property works correctly"""
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        release_id=12345,
    )

    assert output.release_id == 12345


def test_version_github_actions_output_release_id_validation():
    """Test that release_id setter validates type"""
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
    )

    with pytest.raises(TypeError, match="should be an integer"):
        output.release_id = "not an int"


def test_version_github_actions_output_with_upload_url():
    """Test that upload_url property works correctly"""
    test_url = "https://uploads.github.com/repos/owner/repo/releases/123/assets"
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        upload_url=test_url,
    )

    assert output.upload_url == test_url


def test_version_github_actions_output_upload_url_validation():
    """Test that upload_url setter validates type"""
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
    )

    with pytest.raises(TypeError, match="should be a string"):
        output.upload_url = 123


def test_version_github_actions_output_with_assets():
    """Test that assets property works correctly"""
    test_assets = [
        {
            "name": "package-1.0.0.tar.gz",
            "size": 1024,
            "content_type": "application/gzip",
            "browser_download_url": f"{BASE_VCS_URL}/releases/download/v1.0.0/package-1.0.0.tar.gz",
        },
        {
            "name": "package-1.0.0-py3-none-any.whl",
            "size": 2048,
            "content_type": "application/octet-stream",
            "browser_download_url": f"{BASE_VCS_URL}/releases/download/v1.0.0/package-1.0.0-py3-none-any.whl",
        },
    ]
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        assets=test_assets,
    )

    assert output.assets == test_assets
    assert len(output.assets) == 2


def test_version_github_actions_output_assets_validation():
    """Test that assets setter validates type"""
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
    )

    with pytest.raises(TypeError, match="should be a list"):
        output.assets = {"not": "a list"}


def test_version_github_actions_output_assets_dist():
    """Test that assets_dist property correctly categorizes distribution assets"""
    test_assets = [
        {
            "name": "package-1.0.0.tar.gz",
            "size": 1024,
            "browser_download_url": f"{BASE_VCS_URL}/releases/download/v1.0.0/package-1.0.0.tar.gz",
        },
        {
            "name": "package-1.0.0-py3-none-any.whl",
            "size": 2048,
            "browser_download_url": f"{BASE_VCS_URL}/releases/download/v1.0.0/package-1.0.0-py3-none-any.whl",
        },
        {
            "name": "checksums.txt",
            "size": 128,
            "browser_download_url": f"{BASE_VCS_URL}/releases/download/v1.0.0/checksums.txt",
        },
    ]
    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git"),
        assets=test_assets,
    )

    assets_dist = output.assets_dist

    # Verify wheel is categorized correctly
    assert "wheel" in assets_dist
    assert assets_dist["wheel"]["name"] == "package-1.0.0-py3-none-any.whl"

    # Verify sdist is categorized correctly
    assert "sdist" in assets_dist
    assert assets_dist["sdist"]["name"] == "package-1.0.0.tar.gz"

    # Verify other files use extension as key
    assert "txt" in assets_dist
    assert assets_dist["txt"]["name"] == "checksums.txt"


def test_version_github_actions_output_format_with_new_fields():
    """Test that output format includes all new fields"""
    commit_sha = "0" * 40
    version_str = "1.2.3"
    release_notes = "Test release"
    release_id = 12345
    upload_url = "https://uploads.github.com/repos/owner/repo/releases/123/assets"
    test_assets = [
        {
            "name": "package-1.0.0.tar.gz",
            "size": 1024,
        }
    ]

    output = VersionGitHubActionsOutput(
        gh_client=Github(f"{BASE_VCS_URL}.git", hvcs_domain=EXAMPLE_HVCS_DOMAIN),
        released=True,
        version=Version.parse(version_str),
        commit_sha=commit_sha,
        release_notes=release_notes,
        release_id=release_id,
        upload_url=upload_url,
        assets=test_assets,
    )

    output_text = output.to_output_text()

    # Verify new fields are present in output
    assert f"id={release_id}" in output_text
    assert f"upload_url={upload_url}" in output_text
    assert "assets=[" in output_text
    assert "assets_dist={" in output_text


def test_version_github_actions_output_writes_new_fields_to_file(tmp_path: Path):
    """Test that new fields are written to GitHub Actions output file"""
    mock_output_file = tmp_path / "action.out"
    version_str = "1.2.3"
    commit_sha = "0" * 40
    release_notes = "Test release"
    release_id = 12345
    upload_url = "https://uploads.github.com/repos/owner/repo/releases/123/assets"
    test_assets = [
        {
            "name": "package-1.0.0-py3-none-any.whl",
            "size": 2048,
        }
    ]

    patched_environ = {"GITHUB_OUTPUT": str(mock_output_file.resolve())}

    with mock.patch.dict(os.environ, patched_environ, clear=True):
        VersionGitHubActionsOutput(
            gh_client=Github(f"{BASE_VCS_URL}.git", hvcs_domain=EXAMPLE_HVCS_DOMAIN),
            version=Version.parse(version_str),
            released=True,
            commit_sha=commit_sha,
            release_notes=release_notes,
            release_id=release_id,
            upload_url=upload_url,
            assets=test_assets,
        ).write_if_possible()

    with open(mock_output_file, encoding="utf-8", newline=os.linesep) as rfd:
        action_outputs = actions_output_to_dict(rfd.read())

    # Verify new fields are present in the output file
    assert str(release_id) == action_outputs["id"]
    assert upload_url == action_outputs["upload_url"]
    assert action_outputs["assets"]  # Should be a JSON string
    assert action_outputs["assets_dist"]  # Should be a JSON string

    # Verify JSON can be parsed
    import json

    assets_list = json.loads(action_outputs["assets"])
    assert len(assets_list) == 1
    assert assets_list[0]["name"] == "package-1.0.0-py3-none-any.whl"

    assets_dist_dict = json.loads(action_outputs["assets_dist"])
    assert "wheel" in assets_dist_dict
