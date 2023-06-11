from __future__ import annotations

import filecmp
import os
import shutil
from unittest import mock

import pytest
import requests_mock
from pytest_lazyfixture import lazy_fixture
from requests import Session

from semantic_release.cli import changelog, main
from semantic_release.hvcs import Github

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER
from tests.util import flatten_dircmp


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
@pytest.mark.parametrize("args", [(), ("--post-to-release-tag", "v1.99.9191")])
def test_changelog_noop_is_noop(
    repo, args, tmp_path_factory, example_project, cli_runner
):
    tempdir = tmp_path_factory.mktemp("test_noop")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)

    # Set up a requests HTTP session so we can catch the HTTP calls and ensure they're made

    session = Session()
    session.hooks = {"response": [lambda r, *_, **__: r.raise_for_status()]}

    mock_adapter = requests_mock.Adapter()
    mock_adapter.register_uri(
        method=requests_mock.ANY, url=requests_mock.ANY, json={"id": 10001}
    )
    session.mount("http://", mock_adapter)
    session.mount("https://", mock_adapter)

    with mock.patch(
        "semantic_release.hvcs.github.build_requests_session",
        # new=mocked_build_requests_session,
        return_value=session,
    ), requests_mock.Mocker(session=session) as mocker:
        result = cli_runner.invoke(main, ["--noop", changelog.name, *args])

    assert result.exit_code == 0

    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)

    differing_files = flatten_dircmp(dcmp)
    assert not differing_files

    if args:
        # mocked.assert_called_once()
        assert not mocker.called
        assert not mock_adapter.called


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture("repo_with_no_tags_angular_commits"),
        lazy_fixture("repo_with_single_branch_angular_commits"),
        lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
        lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),
        lazy_fixture("repo_with_git_flow_angular_commits"),
        lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),
    ],
)
def test_changelog_content_regenerated(
    repo, tmp_path_factory, example_project, example_changelog_md, cli_runner
):
    tempdir = tmp_path_factory.mktemp("test_changelog")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)

    # Remove the changelog and then check that we can regenerate it
    os.remove(str(example_changelog_md.resolve()))

    result = cli_runner.invoke(main, [changelog.name])
    assert result.exit_code == 0

    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)

    differing_files = flatten_dircmp(dcmp)
    assert not differing_files


# Just need to test that it works for "a" project, not all
@pytest.mark.usefixtures("repo_with_single_branch_and_prereleases_angular_commits")
@pytest.mark.parametrize(
    "args", [("--post-to-release-tag", "v1.99.91910000000000000000000000000")]
)
def test_changelog_release_tag_not_in_history(
    args, tmp_path_factory, example_project, cli_runner
):
    tempdir = tmp_path_factory.mktemp("test_changelog")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)

    result = cli_runner.invoke(main, [changelog.name, *args])
    assert result.exit_code == 2
    assert "not in release history" in result.stderr.lower()


@pytest.mark.usefixtures("repo_with_single_branch_and_prereleases_angular_commits")
@pytest.mark.parametrize("args", [("--post-to-release-tag", "v0.1.0")])
def test_changelog_post_to_release(
    args, monkeypatch, tmp_path_factory, example_project, cli_runner
):
    tempdir = tmp_path_factory.mktemp("test_changelog")
    shutil.rmtree(str(tempdir.resolve()))
    shutil.copytree(src=str(example_project.resolve()), dst=tempdir)

    # Set up a requests HTTP session so we can catch the HTTP calls and ensure they're made

    session = Session()
    session.hooks = {"response": [lambda r, *_, **__: r.raise_for_status()]}

    mock_adapter = requests_mock.Adapter()
    mock_adapter.register_uri(
        method=requests_mock.ANY, url=requests_mock.ANY, json={"id": 10001}
    )
    session.mount("http://", mock_adapter)
    session.mount("https://", mock_adapter)

    # Patch out env vars that affect changelog URLs but only get set in e.g.
    # Github actions
    with mock.patch(
        "semantic_release.hvcs.github.build_requests_session",
        return_value=session,
    ) as mocker, monkeypatch.context() as m:
        m.delenv("GITHUB_REPOSITORY", raising=False)
        m.delenv("CI_PROJECT_NAMESPACE", raising=False)
        result = cli_runner.invoke(main, [changelog.name, *args])

    assert result.exit_code == 0

    assert mocker.called
    assert mock_adapter.called
    assert mock_adapter.last_request.url == (
        "https://{api_url}/repos/{owner}/{repo_name}/releases".format(
            api_url=Github.DEFAULT_API_DOMAIN,
            owner=EXAMPLE_REPO_OWNER,
            repo_name=EXAMPLE_REPO_NAME,
        )
    )
