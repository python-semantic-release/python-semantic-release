from __future__ import annotations

import filecmp
import os
import shutil
from typing import TYPE_CHECKING, Any, Generator
from unittest import mock

import pytest
import requests_mock
from pytest_lazyfixture import lazy_fixture
from requests import Session

from semantic_release.changelog.context import make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.cli import changelog, main
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import load_raw_config_file
from semantic_release.hvcs import Github

from tests.const import (
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
)
from tests.util import flatten_dircmp

if TYPE_CHECKING:
    from pathlib import Path
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git.repo import Repo


@pytest.fixture
def mocked_session_post() -> Generator[MagicMock, Any, None]:
    """Mock the `post()` method in `requests.Session`."""
    with mock.patch("requests.sessions.Session.post") as mocked_session:
        yield mocked_session


@pytest.fixture
def runtime_context(
    example_project_with_release_notes_template: Path,
    repo_with_single_branch_and_prereleases_angular_commits: Repo,
) -> RuntimeContext:
    config_path = example_project_with_release_notes_template / DEFAULT_CONFIG_FILE
    cli_options = GlobalCommandLineOptions(
        noop=False, verbosity=0, strict=False, config_file=config_path
    )
    config_text = load_raw_config_file(config_path)
    raw_config = RawConfig.model_validate(config_text)
    return RuntimeContext.from_raw_config(
        raw_config, repo_with_single_branch_and_prereleases_angular_commits, cli_options
    )


@pytest.fixture
def release_history(runtime_context: RuntimeContext) -> ReleaseHistory:
    rh = ReleaseHistory.from_git_history(
        runtime_context.repo,
        runtime_context.version_translator,
        runtime_context.commit_parser,
        runtime_context.changelog_excluded_commit_patterns,
    )
    changelog_context = make_changelog_context(runtime_context.hvcs_client, rh)
    changelog_context.bind_to_environment(runtime_context.template_environment)
    return rh


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

    # Set up a requests HTTP session so we can catch the HTTP calls and ensure
    # they're made

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
        return_value=session,
    ), requests_mock.Mocker(session=session) as mocker:
        result = cli_runner.invoke(main, ["--noop", changelog.name, *args])

    assert result.exit_code == 0

    dcmp = filecmp.dircmp(str(example_project.resolve()), tempdir)

    differing_files = flatten_dircmp(dcmp)
    assert not differing_files

    if args:
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

    # Set up a requests HTTP session so we can catch the HTTP calls and ensure they're
    # made

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


def test_custom_release_notes_template(
    release_history: ReleaseHistory,
    runtime_context: RuntimeContext,
    mocked_session_post: MagicMock,
    cli_runner: CliRunner,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    # Arrange
    tag = runtime_context.repo.tags[-1].name
    version = runtime_context.version_translator.from_tag(tag)
    release = release_history.released[version]

    # Act
    resp = cli_runner.invoke(main, [changelog.name, "--post-to-release-tag", tag])
    expected_release_notes = runtime_context.template_environment.from_string(
        EXAMPLE_RELEASE_NOTES_TEMPLATE
    ).render(version=version, release=release)

    # Assert
    assert resp.exit_code == 0, (
        "Unexpected failure in command "
        f"'semantic-release {changelog.name} --post-to-release-tag {tag}': "
        + resp.stderr
    )
    mocked_session_post.assert_called_once()
    assert (
        mocked_session_post.call_args.kwargs["json"]["body"] == expected_release_notes
    )
