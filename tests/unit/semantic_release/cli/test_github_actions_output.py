from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from semantic_release import Version
from semantic_release.cli.github_actions_output import VersionGitHubActionsOutput

from tests.util import actions_output_to_dict

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "version, is_prerelease",
    [
        ("1.2.3", False),
        ("1.2.3-alpha.1", True),
    ],
)
@pytest.mark.parametrize("released", (True, False))
def test_version_github_actions_output_format(
    released: bool, version: str, is_prerelease: bool
):
    expected_output = dedent(
        f"""\
        released={'true' if released else 'false'}
        version={version}
        tag=v{version}
        is_prerelease={'true' if is_prerelease else 'false'}
        """
    )
    output = VersionGitHubActionsOutput(
        released=released,
        version=Version.parse(version),
    )

    # Evaluate (expected -> actual)
    assert expected_output == output.to_output_text()


def test_version_github_actions_output_fails_if_missing_output():
    output = VersionGitHubActionsOutput(
        version=Version.parse("1.2.3"),
    )

    # Execute with expected failure
    with pytest.raises(ValueError, match="required outputs were not set"):
        output.to_output_text()


def test_version_github_actions_output_writes_to_github_output_if_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    mock_output_file = tmp_path / "action.out"
    version_str = "1.2.3"
    monkeypatch.setenv("GITHUB_OUTPUT", str(mock_output_file.resolve()))
    output = VersionGitHubActionsOutput(
        version=Version.parse(version_str),
        released=True,
    )

    output.write_if_possible()

    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )

    # Evaluate (expected -> actual)
    assert version_str == action_outputs["version"]
    assert str(True).lower() == action_outputs["released"]
    assert str(False).lower() == action_outputs["is_prerelease"]


def test_version_github_actions_output_no_error_if_not_in_gha(
    monkeypatch: pytest.MonkeyPatch,
):
    output = VersionGitHubActionsOutput(
        version=Version.parse("1.2.3"),
        released=True,
    )

    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    output.write_if_possible()
