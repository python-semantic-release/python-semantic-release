from unittest import mock

import pytest

from semantic_release.cli import main, publish
from semantic_release.hvcs import Github
from semantic_release.version import tags_and_versions


@pytest.mark.parametrize("cmd_args", [(), ("--tag", "latest")])
def test_publish_latest_uses_latest_tag(
    repo_with_single_branch_angular_commits,
    cli_runner,
    cmd_args,
):
    with mock.patch.object(Github, "upload_dists") as mocked_upload_dists, mock.patch(
        "semantic_release.cli.commands.publish.tags_and_versions",
        return_value=([("v1.0.0", "1.0.0")]),
    ) as mock_tags_and_versions:
        result = cli_runner.invoke(main, [publish.name, *cmd_args])
        assert result.exit_code == 0

    mock_tags_and_versions.assert_called_once()
    mocked_upload_dists.assert_called_once_with(tag="v1.0.0", dist_glob="dist/*")


def test_publish_to_tag_uses_tag(repo_with_single_branch_angular_commits, cli_runner):
    tag = "v99.999.9999+build.1234"
    with mock.patch.object(Github, "upload_dists") as mocked_upload_dists, mock.patch(
        "semantic_release.cli.commands.publish.tags_and_versions",
        return_value=([("v1.0.0", "1.0.0")]),
    ) as mock_tags_and_versions:
        result = cli_runner.invoke(main, [publish.name, "--tag", tag])
        assert result.exit_code == 0

    mock_tags_and_versions.assert_not_called()
    assert mocked_upload_dists.called_once_with(tag=tag, dist_glob="dist/*")
