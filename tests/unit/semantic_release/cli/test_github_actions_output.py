import pytest

from semantic_release import Version
from semantic_release.cli.github_actions_output import VersionGitHubActionsOutput

from tests.util import actions_output_to_dict


@pytest.mark.parametrize("released", (True, False))
def test_version_github_actions_output_format(released):
    version = Version.parse("1.2.3")
    output = VersionGitHubActionsOutput()

    output.version = version
    output.released = released

    text = output.to_output_text()
    assert (
        text
        == f"released={str(released).lower()}\nversion={str(version)}\ntag={version.as_tag()}"
    )


def test_version_github_actions_output_fails_if_missing_output():
    version = Version.parse("1.2.3")
    output = VersionGitHubActionsOutput()

    output.version = version

    with pytest.raises(ValueError, match="required outputs were not set"):
        output.to_output_text()


def test_version_github_actions_output_writes_to_github_output_if_available(
    monkeypatch, tmp_path
):
    mock_output_file = tmp_path / "action.out"
    version = Version.parse("1.2.3")
    output = VersionGitHubActionsOutput()

    output.version = version
    output.released = True

    monkeypatch.setenv("GITHUB_OUTPUT", str(mock_output_file.resolve()))
    output.write_if_possible()

    action_outputs = actions_output_to_dict(
        mock_output_file.read_text(encoding="utf-8")
    )

    assert action_outputs["version"] == str(version)
    assert action_outputs["released"] == "true"


def test_version_github_actions_output_no_error_if_not_in_gha(monkeypatch):
    version = Version.parse("1.2.3")
    output = VersionGitHubActionsOutput()

    output.version = version
    output.released = True

    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    output.write_if_possible()
