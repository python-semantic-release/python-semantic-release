from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from semantic_release.cli.commands.main import main

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git.repo import Repo
    from requests_mock import Mocker

    from tests.e2e.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import UseHvcsFn, UseReleaseNotesTemplateFn


@pytest.mark.parametrize(
    "tokens",
    [
        ("gitlab-token", "gitlab-private-token"),
        ("gitlab-token", "gitlab-token"),
        ("", "gitlab-token"),
        ("gitlab-token", None),
        ("gitlab-token", ""),
        (None, "gitlab-private-token"),
        (None, None),
    ],
)
def test_gitlab_release_tokens(
    cli_runner: CliRunner,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    mocked_git_push: MagicMock,
    requests_mock: Mocker,
    use_gitlab_hvcs: UseHvcsFn,
    tokens: tuple[str, str],
    repo_w_no_tags_angular_commits: Repo,
) -> None:
    """Verify that gitlab tokens are used correctly."""
    # Setup
    private_token, job_token = tokens
    use_gitlab_hvcs()
    requests_mock.register_uri(
        "POST",
        "https://example.com/api/v4/projects/999/releases",
        json={"id": 999},
        headers={"Content-Type": "application/json"},
    )
    requests_mock.register_uri(
        "GET",
        "https://example.com/api/v4/projects/example_owner%2Fexample_repo",
        json={"id": 999},
        headers={"Content-Type": "application/json"},
    )

    env_dict = {}
    if private_token is not None:
        env_dict["GITLAB_TOKEN"] = private_token
    if job_token is not None:
        env_dict["CI_JOB_TOKEN"] = job_token
    with mock.patch.dict(os.environ, env_dict):
        # Act
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--vcs-release"]
        result = cli_runner.invoke(main, cli_cmd[1:])

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert requests_mock.call_count == 2
    assert requests_mock.last_request is not None
    assert requests_mock.request_history[0].method == "GET"
    assert requests_mock.request_history[1].method == "POST"

    job_token_header = "JOB-TOKEN"
    private_token_header = "PRIVATE-TOKEN"
    for request in requests_mock.request_history:
        if private_token and private_token != job_token:
            assert request._request.headers[private_token_header] == private_token
            assert job_token_header not in request._request.headers
        elif job_token:
            assert request._request.headers[job_token_header] == job_token
            assert private_token_header not in request._request.headers
        else:
            assert private_token_header not in request._request.headers
            assert job_token_header not in request._request.headers
