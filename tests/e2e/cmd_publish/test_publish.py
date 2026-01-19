from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast
from unittest import mock

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs import Github

from tests.const import MAIN_PROG_NAME, PUBLISH_SUBCMD
from tests.fixtures.repos import repo_w_trunk_only_conventional_commits
from tests.util import assert_exit_code, assert_successful_exit_code

if TYPE_CHECKING:
    from typing import Sequence

    from requests_mock import Mocker

    from tests.conftest import RunCliFn
    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        GetCfgValueFromDefFn,
        GetHvcsClientFromRepoDefFn,
        GetVersionsFromRepoBuildDefFn,
    )


@pytest.mark.parametrize("cmd_args", [(), ("--tag", "latest")])
@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_publish_latest_uses_latest_tag(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    cmd_args: Sequence[str],
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    latest_version = get_versions_from_repo_build_def(repo_result["definition"])[-1]
    latest_tag = f"v{latest_version}"

    with mock.patch.object(
        Github,
        Github.upload_dists.__name__,
    ) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, *cmd_args]

        # Act
        result = run_cli(cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        mocked_upload_dists.assert_called_once_with(tag=latest_tag, dist_glob="dist/*")


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_trunk_only_conventional_commits.__name__)]
)
def test_publish_to_tag_uses_tag(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    # Testing a non-latest tag to distinguish from test_publish_latest_uses_latest_tag()
    previous_version = get_versions_from_repo_build_def(repo_result["definition"])[-2]
    previous_tag = f"v{previous_version}"

    with mock.patch.object(Github, Github.upload_dists.__name__) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", previous_tag]

        # Act
        result = run_cli(cli_cmd[1:])

        # Evaluate
        assert_successful_exit_code(result, cli_cmd)
        mocked_upload_dists.assert_called_once_with(
            tag=previous_tag, dist_glob="dist/*"
        )


@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_publish_fails_on_nonexistant_tag(run_cli: RunCliFn):
    non_existant_tag = "nonexistant-tag"

    with mock.patch.object(Github, Github.upload_dists.__name__) as mocked_upload_dists:
        cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", non_existant_tag]

        # Act
        result = run_cli(cli_cmd[1:])

        # Evaluate
        assert_exit_code(1, result, cli_cmd)
        assert (
            f"Tag '{non_existant_tag}' not found in local repository!" in result.stderr
        )
        mocked_upload_dists.assert_not_called()


@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture_name)
        for repo_fixture_name in [
            repo_w_trunk_only_conventional_commits.__name__,
        ]
    ],
)
def test_publish_fails_on_github_upload_dists(
    repo_result: BuiltRepoResult,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    run_cli: RunCliFn,
    requests_mock: Mocker,
):
    """
    Given a repo with conventional commits and at least one tag
    When publishing to a valid tag but upload dists authentication fails
    Then the command fails with exit code 1

    Reference: python-semantic-release/publish-action#77
    """
    repo_def = repo_result["definition"]
    tag_format_str = cast("str", get_cfg_value_from_def(repo_def, "tag_format_str"))
    all_versions = get_versions_from_repo_build_def(repo_def)
    latest_release_version = all_versions[-1]
    release_tag = tag_format_str.format(version=latest_release_version)
    hvcs_client = get_hvcs_client_from_repo_def(repo_def)
    if not isinstance(hvcs_client, Github):
        pytest.fail("Test setup error: HvcsClient is not a Github instance")

    release_id = 12
    files = [
        Path(f"dist/package-{latest_release_version}.whl"),
        Path(f"dist/package-{latest_release_version}.tar.gz"),
    ]
    tag_endpoint = hvcs_client.create_api_url(
        endpoint=f"/repos/{hvcs_client.owner}/{hvcs_client.repo_name}/releases/tags/{release_tag}",
    )
    release_endpoint = hvcs_client.create_api_url(
        endpoint=f"/repos/{hvcs_client.owner}/{hvcs_client.repo_name}/releases/{release_id}"
    )
    upload_url = release_endpoint + "/assets"
    expected_num_upload_attempts = len(files)

    # Setup: Create distribution files before upload
    for file in files:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch()

    # Setup: Mock upload url retrieval
    requests_mock.register_uri("GET", tag_endpoint, json={"id": release_id})
    requests_mock.register_uri(
        "GET", release_endpoint, json={"upload_url": f"{upload_url}{{?name,label}}"}
    )

    # Setup: Mock upload failure
    uploader_mock = requests_mock.register_uri("POST", upload_url, status_code=403)

    # Act
    cli_cmd = [MAIN_PROG_NAME, PUBLISH_SUBCMD, "--tag", "latest"]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert isinstance(result.exception, SystemExit)
    assert expected_num_upload_attempts == uploader_mock.call_count
    for file in files:
        assert f"Failed to upload asset '{file}'" in result.stderr
