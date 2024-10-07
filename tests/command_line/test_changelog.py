from __future__ import annotations

import filecmp
import os
import shutil
import sys
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import requests_mock
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture
from requests import Session

import semantic_release.hvcs.github
from semantic_release.changelog.context import ChangelogMode
from semantic_release.cli.commands.main import main
from semantic_release.hvcs.github import Github

from tests.const import (
    CHANGELOG_SUBCMD,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    MAIN_PROG_NAME,
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
from tests.util import (
    add_text_to_file,
    assert_exit_code,
    assert_successful_exit_code,
    flatten_dircmp,
    get_release_history_from_context,
    remove_dir_tree,
)

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.command_line.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        UpdatePyprojectTomlFn,
        UseReleaseNotesTemplateFn,
    )
    from tests.fixtures.git_repo import CommitNReturnChangelogEntryFn


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
        cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD, *args]
        result = cli_runner.invoke(main, cli_cmd[1:])

    # Capture differences after command
    dcmp = filecmp.dircmp(str(example_project_dir.resolve()), tempdir)
    differing_files = flatten_dircmp(dcmp)

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
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
    default_md_changelog_insertion_flag: str,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.INIT.value
    )

    # Because we are in init mode, the insertion flag is not present in the changelog
    # we must take it out manually because our repo generation fixture includes it automatically
    expected_changelog_content = example_changelog_md.read_text().replace(
        f"{default_md_changelog_insertion_flag}\n", ""
    )

    # Remove the changelog and then check that we can regenerate it
    os.remove(str(example_changelog_md.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_unchanged(
    repo: Repo,
    example_changelog_md: Path,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
):
    """
    Given that the changelog file already exists for the current release,
    When the changelog command is run in "update" mode,
    Then the changelog file is not modified.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    # Capture the expected changelog content
    expected_changelog_content = example_changelog_md.read_text()

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


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
        ]
    ],
)
def test_changelog_update_mode_no_prev_changelog(
    repo: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_changelog_md: Path,
):
    """
    Given that the changelog file does not exist,
    When the changelog command is run in "update" mode,
    Then the changelog file is initialized with the default content.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    # Capture the expected changelog content
    expected_changelog_content = example_changelog_md.read_text()

    # Remove any previous changelog to update
    os.remove(str(example_changelog_md.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_flag(
    repo: Repo,
    example_changelog_md: Path,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_md_changelog_insertion_flag: str,
):
    """
    Given a changelog template without the insertion flag,
    When the changelog command is run in "update" mode,
    Then the changelog is not modified.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    # Remove the insertion flag from the changelog
    example_changelog_md.write_text(
        example_changelog_md.read_text().replace(
            f"{default_md_changelog_insertion_flag}\n",
            "",
            1,
        )
    )

    # Capture the expected changelog content
    expected_changelog_content = example_changelog_md.read_text()

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # MUST HAVE at least 2 tags!
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_header(
    repo: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_md_file: Path,
):
    """
    Given a changelog template with the insertion flag at the beginning of the file,
    When the changelog command is run in "update" mode,
    Then the changelog is rebuilt with the latest release prepended to the existing content.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")
    update_pyproject_toml(
        "tool.semantic_release.changelog.insertion_flag",
        f"# CHANGELOG{os.linesep}{os.linesep}<!-- version list -->",
    )

    # Capture the expected changelog content of current release
    with changelog_md_file.open(newline=os.linesep) as rfd:
        expected_changelog_content = rfd.read()

    # Reset changelog file to last release
    repo.git.checkout(repo.tags[-2].name, "--", str(changelog_md_file))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_md_file.exists()

    with changelog_md_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # MUST HAVE at least 2 tags!
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_footer(
    repo: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_changelog_md: Path,
    default_md_changelog_insertion_flag: str,
):
    """
    Given a changelog template with the insertion flag at the end of the file,
    When the changelog command is run in "update" mode,
    Then the changelog is rebuilt with only the latest release.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    # Capture the expected changelog content of current release
    expected_changelog_content = example_changelog_md.read_text().split(
        f"\n\n## {repo.tags[-2].name}"
    )[0]

    # Remove any text after the insertion flag
    example_changelog_md.write_text(
        str.join(
            "\n",
            [
                example_changelog_md.read_text().split(
                    default_md_changelog_insertion_flag
                )[0],
                f"{default_md_changelog_insertion_flag}\n",
            ],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog content only includes the latest release as there
    # is no previous release information as the insertion flag is at the end of the file
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # Must not have a single release/tag
            repo_with_no_tags_angular_commits.__name__,
            repo_with_no_tags_emoji_commits.__name__,
            repo_with_no_tags_scipy_commits.__name__,
            repo_with_no_tags_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_releases(
    repo: Repo,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    default_md_changelog_insertion_flag: str,
    example_changelog_md: Path,
):
    """
    Given the repository has no releases and the user has provided a initialized changelog,
    When the changelog command is run in "update" mode,
    Then the changelog is populated with unreleased changes.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    # Custom text to maintain (must be different from the default)
    custom_text = "---\n\nCustom footer text\n"

    # Capture and modify the current changelog content to become the expected output
    initial_changelog_parts = example_changelog_md.read_text().split(
        default_md_changelog_insertion_flag
    )
    expected_changelog_content = str.join(
        default_md_changelog_insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                "\n\n",
                [
                    initial_changelog_parts[1],
                    custom_text,
                ],
            ),
        ],
    )

    # Grab the Unreleased changelog & create the initalized user changelog
    example_changelog_md.write_text(
        str.join(
            default_md_changelog_insertion_flag,
            [initial_changelog_parts[0], f"\n\n{custom_text}"],
        )
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert example_changelog_md.exists()

    actual_content = example_changelog_md.read_text()

    # Check that the changelog footer is maintained and updated with Unreleased info
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "repo, commit_type",
    [
        (lazy_fixture(repo_fixture), repo_fixture.split("_")[-2])
        for repo_fixture in [
            repo_with_single_branch_angular_commits.__name__,
            repo_with_single_branch_emoji_commits.__name__,
            repo_with_single_branch_scipy_commits.__name__,
            repo_with_single_branch_tag_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_unreleased_n_released(
    repo: Repo,
    commit_type: str,
    cli_runner: CliRunner,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_changelog_md: Path,
    example_git_ssh_url: str,
    file_in_repo: str,
    commit_n_rtn_changelog_entry: CommitNReturnChangelogEntryFn,
    default_md_changelog_insertion_flag: str,
):
    """
    Given there are unreleased changes and a previous release in the changelog,
    When the changelog command is run in "update" mode,
    Then the changelog is only updated with the unreleased changes.
    """
    update_pyproject_toml("tool.semantic_release.changelog.mode", "update")

    commit_n_section = {
        "angular": {
            "commit": "perf: improve the performance of the application",
            "section": "Performance Improvements",
        },
        "emoji": {
            "commit": ":zap: improve the performance of the application",
            "section": ":zap:",
        },
        "scipy": {
            "commit": "MAINT: maintain the codebase",
            "section": "Fix",
        },
        "tag": {
            "commit": ":nut_and_bolt: improve the performance of the algorithm",
            "section": "Fix",
        },
    }

    # Custom text to maintain (must be different from the default)
    custom_text = "---\n\nCustom footer text\n"

    # Update the changelog with the custom footer text
    example_changelog_md.write_text(
        str.join(
            "\n\n",
            [
                example_changelog_md.read_text(),
                custom_text,
            ],
        )
    )

    initial_changelog_parts = example_changelog_md.read_text().split(
        default_md_changelog_insertion_flag
    )

    # Make a change to the repo to create unreleased changes
    add_text_to_file(repo, file_in_repo)
    unreleased_commit_entry = commit_n_rtn_changelog_entry(
        repo,
        commit_n_section[commit_type]["commit"],
        Github(remote_url=example_git_ssh_url, hvcs_domain=EXAMPLE_HVCS_DOMAIN),
    )

    # Generate the expected changelog content
    expected_changelog_content = str.join(
        default_md_changelog_insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                "",
                [
                    "\n",
                    # Unreleased changes
                    dedent(
                        f"""
                        ## Unreleased

                        ### {commit_n_section[commit_type]["section"]}

                        * {unreleased_commit_entry}
                        """
                    ),
                    # Previous release notes
                    initial_changelog_parts[1],
                ],
            ),
        ],
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
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
    cli_runner: CliRunner,
):
    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, *args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert "not in release history" in result.stderr.lower()


@pytest.mark.usefixtures(
    repo_with_single_branch_and_prereleases_angular_commits.__name__
)
@pytest.mark.parametrize("args", [("--post-to-release-tag", "v0.1.0")])
def test_changelog_post_to_release(args: list[str], cli_runner: CliRunner):
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

    clean_os_environment = dict(
        filter(
            lambda k_v: k_v[1] is not None,
            {
                "CI": "true",
                "PATH": os.getenv("PATH"),
                "HOME": os.getenv("HOME"),
                "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV", "./.venv"),
                **(
                    {}
                    if sys.platform != "win32"
                    else {
                        # Windows Required variables
                        "ALLUSERSAPPDATA": os.getenv("ALLUSERSAPPDATA"),
                        "ALLUSERSPROFILE": os.getenv("ALLUSERSPROFILE"),
                        "APPDATA": os.getenv("APPDATA"),
                        "COMMONPROGRAMFILES": os.getenv("COMMONPROGRAMFILES"),
                        "COMMONPROGRAMFILES(X86)": os.getenv("COMMONPROGRAMFILES(X86)"),
                        "DEFAULTUSERPROFILE": os.getenv("DEFAULTUSERPROFILE"),
                        "HOMEPATH": os.getenv("HOMEPATH"),
                        "PATHEXT": os.getenv("PATHEXT"),
                        "PROFILESFOLDER": os.getenv("PROFILESFOLDER"),
                        "PROGRAMFILES": os.getenv("PROGRAMFILES"),
                        "PROGRAMFILES(X86)": os.getenv("PROGRAMFILES(X86)"),
                        "SYSTEM": os.getenv("SYSTEM"),
                        "SYSTEM16": os.getenv("SYSTEM16"),
                        "SYSTEM32": os.getenv("SYSTEM32"),
                        "SYSTEMDRIVE": os.getenv("SYSTEMDRIVE"),
                        "SYSTEMROOT": os.getenv("SYSTEMROOT"),
                        "TEMP": os.getenv("TEMP"),
                        "TMP": os.getenv("TMP"),
                        "USERPROFILE": os.getenv("USERPROFILE"),
                        "USERSID": os.getenv("USERSID"),
                        "USERNAME": os.getenv("USERNAME"),
                        "WINDIR": os.getenv("WINDIR"),
                    }
                ),
            }.items(),
        )
    )

    # Patch out env vars that affect changelog URLs but only get set in e.g.
    # Github actions
    with mock.patch(
        # Patching the specific module's reference to the build_requests_session function
        f"{semantic_release.hvcs.github.__name__}.{semantic_release.hvcs.github.build_requests_session.__name__}",
        return_value=session,
    ) as build_requests_session_mock, mock.patch.dict(
        os.environ, clean_os_environment, clear=True
    ):
        # Act
        cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, *args]
        result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert build_requests_session_mock.called
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
    tag = repo_with_single_branch_and_prereleases_angular_commits.tags[-1].name

    version = runtime_context_with_tags.version_translator.from_tag(tag)
    if version is None:
        raise ValueError(f"Tag {tag} not in release history")

    release = release_history.released[version]

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, "--post-to-release-tag", tag]
    result = cli_runner.invoke(main, cli_cmd[1:])

    expected_release_notes = str.join(
        # ensure normalized line endings after render
        os.linesep,
        [
            line.replace("\r", "")
            for line in str.split(
                runtime_context_with_tags.template_environment.from_string(
                    EXAMPLE_RELEASE_NOTES_TEMPLATE
                )
                .render(version=version, release=release)
                .rstrip()
                + os.linesep,
                "\n",
            )
        ],
    )

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert expected_call_count == post_mocker.call_count
    assert post_mocker.last_request is not None

    actual_notes = post_mocker.last_request.json()["body"]
    assert expected_release_notes == actual_notes


@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_changelog_default_on_empty_template_dir(
    example_changelog_md: Path,
    changelog_template_dir: Path,
    example_project_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    cli_runner: CliRunner,
):
    # Setup: Make sure default changelog doesn't already exist
    example_changelog_md.unlink(missing_ok=True)

    # Setup: Create an empty template directory
    example_project_template_dir.mkdir(parents=True, exist_ok=True)

    # Setup: Set the templates directory in the configuration
    update_pyproject_toml(
        "tool.semantic_release.changelog.template_dir",
        str(changelog_template_dir),
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that our default changelog was created because the user's template dir was empty
    assert example_changelog_md.exists()


@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_changelog_default_on_incorrect_config_template_file(
    example_changelog_md: Path,
    changelog_template_dir: Path,
    example_project_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    cli_runner: CliRunner,
):
    # Setup: Make sure default changelog doesn't already exist
    example_changelog_md.unlink(missing_ok=True)

    # Setup: Create a file of the same name as the template directory
    example_project_template_dir.parent.mkdir(parents=True, exist_ok=True)
    example_project_template_dir.touch()

    # Setup: Set the templates directory as the file in the configuration
    update_pyproject_toml(
        "tool.semantic_release.changelog.template_dir",
        str(changelog_template_dir),
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that our default changelog was created because the user's template dir was empty
    assert example_changelog_md.exists()


@pytest.mark.parametrize("bad_changelog_file_str", ("/etc/passwd", "../../.ssh/id_rsa"))
@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_changelog_prevent_malicious_path_traversal_file(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    bad_changelog_file_str: str,
    cli_runner: CliRunner,
):
    # Setup: A malicious path traversal filepath outside of the repository
    update_pyproject_toml(
        "tool.semantic_release.changelog.changelog_file",
        bad_changelog_file_str,
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert (
        "Changelog file destination must be inside of the repository directory."
        in result.stderr
    )


@pytest.mark.parametrize("template_dir_path", ("~/.ssh", "../../.ssh"))
@pytest.mark.usefixtures(repo_with_single_branch_angular_commits.__name__)
def test_changelog_prevent_external_path_traversal_dir(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    template_dir_path: str,
    cli_runner: CliRunner,
):
    # Setup: A malicious path traversal filepath outside of the repository
    update_pyproject_toml(
        "tool.semantic_release.changelog.template_dir",
        template_dir_path,
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert (
        "Template directory must be inside of the repository directory."
        in result.stderr
    )
