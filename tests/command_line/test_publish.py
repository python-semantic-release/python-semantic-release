from unittest import mock

import pytest

from semantic_release.cli import main, publish
from semantic_release.hvcs import Github


@pytest.mark.usefixtures("repo_with_single_branch_angular_commits")
@pytest.mark.parametrize("cmd_args", [(), ("--tag", "latest")])
def test_publish_latest_uses_latest_tag(
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


@pytest.mark.usefixtures("repo_with_single_branch_angular_commits")
def test_publish_to_tag_uses_tag(cli_runner):
    tag = "v99.999.9999+build.1234"
    with mock.patch.object(Github, "upload_dists") as mocked_upload_dists, mock.patch(
        "semantic_release.cli.commands.publish.tags_and_versions",
        return_value=([("v1.0.0", "1.0.0")]),
    ) as mock_tags_and_versions:
        result = cli_runner.invoke(main, [publish.name, "--tag", tag])
        assert result.exit_code == 0

    mock_tags_and_versions.assert_not_called()
    mocked_upload_dists.assert_called_once_with(tag=tag, dist_glob="dist/*")
