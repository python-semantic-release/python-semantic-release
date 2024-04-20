from __future__ import annotations

import filecmp
import os
import shutil
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import requests_mock
from pytest_lazyfixture import lazy_fixture
from requests import Session

from semantic_release.cli import changelog, main

from tests.const import (
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    SUCCESS_EXIT_CODE,
)
from tests.fixtures.repos import (
    repo_w_github_flow_w_feature_release_channel_angular_commits,
    repo_w_github_flow_w_feature_release_channel_emoji_commits,
    repo_w_github_flow_w_feature_release_channel_scipy_commits,
    repo_w_github_flow_w_feature_release_channel_tag_commits,
    repo_with_git_flow_and_release_channels_angular_commits,
    repo_with_git_flow_and_release_channels_angular_commits_using_tag_format,
    repo_with_git_flow_and_release_channels_emoji_commits,
    repo_with_git_flow_and_release_channels_scipy_commits,
    repo_with_git_flow_and_release_channels_tag_commits,
    repo_with_git_flow_angular_commits,
    repo_with_git_flow_emoji_commits,
    repo_with_git_flow_scipy_commits,
    repo_with_git_flow_tag_commits,
    repo_with_no_tags_angular_commits,
    repo_with_no_tags_emoji_commits,
    repo_with_no_tags_scipy_commits,
    repo_with_no_tags_tag_commits,
    repo_with_single_branch_and_prereleases_angular_commits,
    repo_with_single_branch_and_prereleases_emoji_commits,
    repo_with_single_branch_and_prereleases_scipy_commits,
    repo_with_single_branch_and_prereleases_tag_commits,
    repo_with_single_branch_angular_commits,
    repo_with_single_branch_emoji_commits,
    repo_with_single_branch_scipy_commits,
    repo_with_single_branch_tag_commits,
)
from tests.util import flatten_dircmp, get_release_history_from_context, remove_dir_tree

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.command_line.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import ExProjectDir, UseReleaseNotesTemplateFn


changelog_subcmd = changelog.name or changelog.__name__  # type: ignore


@pytest.mark.parametrize(
    "repo,tag",
    [
        (lazy_fixture(repo_with_no_tags_angular_commits.__name__), None),
        (lazy_fixture(repo_with_single_branch_angular_commits.__name__), "v0.1.1"),
        (
            lazy_fixture(
                repo_with_single_branch_and_prereleases_angular_commits.__name__
            ),
            "v0.2.0",
        ),
        (
            lazy_fixture(
                repo_w_github_flow_w_feature_release_channel_angular_commits.__name__
            ),
            "v0.2.0",
        ),
        (lazy_fixture(repo_with_git_flow_angular_commits.__name__), "v1.0.0"),
        (
            lazy_fixture(
                repo_with_git_flow_and_release_channels_angular_commits.__name__
            ),
            "v1.1.0-alpha.3",
        ),
    ],
)
@pytest.mark.parametrize("arg0", [None, "--post-to-release-tag"])
def test_changelog_noop_is_noop(
    repo: Repo,
    tag: str | None,
    arg0: str | None,
    tmp_path_factory: pytest.TempPathFactory,
    example_project_dir: ExProjectDir,
    cli_runner: CliRunner,
):
    args = [arg0, tag] if tag and arg0 else []
    tempdir = tmp_path_factory.mktemp("test_noop")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)

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
        result = cli_runner.invoke(main, ["--noop", changelog_subcmd, *args])

    assert SUCCESS_EXIT_CODE == result.exit_code  # noqa: SIM300

    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)

    differing_files = flatten_dircmp(dcmp)
    assert not differing_files

    if args:
        assert not mocker.called
        assert not mock_adapter.called


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_with_no_tags_angular_commits.__name__,
            repo_with_no_tags_emoji_commits.__name__,
            repo_with_no_tags_scipy_commits.__name__,
            repo_with_no_tags_tag_commits.__name__,
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
            repo_with_single_branch_and_prereleases_angular_commits.__name__,
            repo_with_single_branch_and_prereleases_emoji_commits.__name__,
            repo_with_single_branch_and_prereleases_scipy_commits.__name__,
            repo_with_single_branch_and_prereleases_tag_commits.__name__,
            repo_w_github_flow_w_feature_release_channel_angular_commits.__name__,
            repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
            repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
            repo_w_github_flow_w_feature_release_channel_tag_commits.__name__,
            repo_with_git_flow_angular_commits.__name__,
            repo_with_git_flow_emoji_commits.__name__,
            repo_with_git_flow_scipy_commits.__name__,
            repo_with_git_flow_tag_commits.__name__,
            repo_with_git_flow_and_release_channels_angular_commits.__name__,
            repo_with_git_flow_and_release_channels_emoji_commits.__name__,
            repo_with_git_flow_and_release_channels_scipy_commits.__name__,
            repo_with_git_flow_and_release_channels_tag_commits.__name__,
            repo_with_git_flow_and_release_channels_angular_commits_using_tag_format.__name__,
        ]
    ],
)
def test_changelog_content_regenerated(
    repo: Repo,
    example_changelog_md: Path,
    cli_runner: CliRunner,
):
    expected_changelog_content = example_changelog_md.read_text()

    # Remove the changelog and then check that we can regenerate it
    os.remove(str(example_changelog_md.resolve()))

    result = cli_runner.invoke(main, [changelog_subcmd])
    assert SUCCESS_EXIT_CODE == result.exit_code  # noqa: SIM300

    # Check that the changelog file was re-created
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


# Just need to test that it works for "a" project, not all
@pytest.mark.usefixtures(
    repo_with_single_branch_and_prereleases_angular_commits.__name__
)
@pytest.mark.parametrize(
    "args", [("--post-to-release-tag", "v1.99.91910000000000000000000000000")]
)
def test_changelog_release_tag_not_in_history(
    args: list[str],
    tmp_path_factory: pytest.TempPathFactory,
    example_project_dir: ExProjectDir,
    cli_runner: CliRunner,
):
    expected_err_code = 2
    tempdir = tmp_path_factory.mktemp("test_changelog")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)

    result = cli_runner.invoke(main, [changelog_subcmd, *args])

    assert expected_err_code == result.exit_code
    assert "not in release history" in result.stderr.lower()


@pytest.mark.usefixtures(
    repo_with_single_branch_and_prereleases_angular_commits.__name__
)
@pytest.mark.parametrize("args", [("--post-to-release-tag", "v0.1.0")])
def test_changelog_post_to_release(
    args: list[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
    example_project_dir: ExProjectDir,
    cli_runner: CliRunner,
):
    tempdir = tmp_path_factory.mktemp("test_changelog")
    remove_dir_tree(tempdir.resolve(), force=True)
    shutil.copytree(src=str(example_project_dir.resolve()), dst=tempdir)

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

    expected_request_url = "{api_url}/repos/{owner}/{repo_name}/releases".format(
        api_url=f"https://{EXAMPLE_HVCS_DOMAIN}/api/v3",  # GitHub API URL
        owner=EXAMPLE_REPO_OWNER,
        repo_name=EXAMPLE_REPO_NAME,
    )

    # Patch out env vars that affect changelog URLs but only get set in e.g.
    # Github actions
    with mock.patch(
        "semantic_release.hvcs.github.build_requests_session",
        return_value=session,
    ) as mocker, mock.patch.dict("os.environ", {}, clear=True):
        result = cli_runner.invoke(main, [changelog_subcmd, *args])

    assert SUCCESS_EXIT_CODE == result.exit_code  # noqa: SIM300

    assert mocker.called
    assert mock_adapter.called
    assert mock_adapter.last_request is not None
    assert expected_request_url == mock_adapter.last_request.url


def test_custom_release_notes_template(
    repo_with_single_branch_and_prereleases_angular_commits: Repo,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    post_mocker: Mocker,
    cli_runner: CliRunner,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    # Setup
    use_release_notes_template()
    runtime_context_with_tags = retrieve_runtime_context(
        repo_with_single_branch_and_prereleases_angular_commits
    )
    expected_call_count = 1

    # Arrange
    release_history = get_release_history_from_context(runtime_context_with_tags)
    tag = runtime_context_with_tags.repo.tags[-1].name

    version = runtime_context_with_tags.version_translator.from_tag(tag)
    if version is None:
        raise ValueError(f"Tag {tag} not in release history")

    release = release_history.released[version]

    # Act
    resp = cli_runner.invoke(main, [changelog_subcmd, "--post-to-release-tag", tag])
    expected_release_notes = (
        runtime_context_with_tags.template_environment.from_string(
            EXAMPLE_RELEASE_NOTES_TEMPLATE
        ).render(version=version, release=release)
        + "\n"
    )

    # Assert
    assert SUCCESS_EXIT_CODE == resp.exit_code, (  # noqa: SIM300
        "Unexpected failure in command "
        f"'semantic-release {changelog_subcmd} --post-to-release-tag {tag}': "
        + resp.stderr
    )
    assert expected_call_count == post_mocker.call_count
    assert post_mocker.last_request is not None
    assert expected_release_notes == post_mocker.last_request.json()["body"]
