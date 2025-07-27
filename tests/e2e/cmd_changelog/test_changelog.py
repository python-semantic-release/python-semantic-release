from __future__ import annotations

import os
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest import mock

import pytest
import requests_mock
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture
from requests import Session

import semantic_release.hvcs.github
from semantic_release.changelog.context import ChangelogMode
from semantic_release.cli.config import ChangelogOutputFormat
from semantic_release.hvcs.github import Github

from tests.const import (
    CHANGELOG_SUBCMD,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_REPO_NAME,
    EXAMPLE_REPO_OWNER,
    MAIN_PROG_NAME,
)
from tests.fixtures.example_project import (
    change_to_ex_proj_dir,
    changelog_md_file,
    changelog_rst_file,
    default_md_changelog_insertion_flag,
    default_rst_changelog_insertion_flag,
    example_changelog_md,
    example_changelog_rst,
)
from tests.fixtures.repos import (
    repo_w_git_flow_conventional_commits,
    repo_w_git_flow_emoji_commits,
    repo_w_git_flow_scipy_commits,
    repo_w_git_flow_w_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_alpha_prereleases_n_scipy_commits,
    repo_w_git_flow_w_beta_alpha_rev_prereleases_n_conventional_commits,
    repo_w_git_flow_w_beta_alpha_rev_prereleases_n_emoji_commits,
    repo_w_git_flow_w_beta_alpha_rev_prereleases_n_scipy_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits,
    repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits,
    repo_w_github_flow_w_default_release_channel_conventional_commits,
    repo_w_github_flow_w_default_release_channel_emoji_commits,
    repo_w_github_flow_w_default_release_channel_scipy_commits,
    repo_w_github_flow_w_feature_release_channel_conventional_commits,
    repo_w_github_flow_w_feature_release_channel_emoji_commits,
    repo_w_github_flow_w_feature_release_channel_scipy_commits,
    repo_w_no_tags_conventional_commits,
    repo_w_no_tags_emoji_commits,
    repo_w_no_tags_scipy_commits,
    repo_w_trunk_only_conventional_commits,
    repo_w_trunk_only_emoji_commits,
    repo_w_trunk_only_n_prereleases_conventional_commits,
    repo_w_trunk_only_n_prereleases_emoji_commits,
    repo_w_trunk_only_n_prereleases_scipy_commits,
    repo_w_trunk_only_scipy_commits,
)
from tests.util import (
    add_text_to_file,
    assert_exit_code,
    assert_successful_exit_code,
    get_func_qual_name,
    get_release_history_from_context,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import TypedDict

    from requests_mock import Mocker

    from semantic_release.commit_parser.conventional.parser import (
        ConventionalCommitParser,
    )
    from semantic_release.commit_parser.emoji import EmojiCommitParser
    from semantic_release.commit_parser.scipy import ScipyCommitParser

    from tests.conftest import RunCliFn
    from tests.e2e.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        UpdatePyprojectTomlFn,
        UseReleaseNotesTemplateFn,
    )
    from tests.fixtures.git_repo import (
        BuildRepoFromDefinitionFn,
        BuiltRepoResult,
        CommitConvention,
        CommitDef,
        CommitNReturnChangelogEntryFn,
        GetCommitDefFn,
        GetRepoDefinitionFn,
        GetVersionsFromRepoBuildDefFn,
    )

    class Commit2Section(TypedDict):
        conventional: Commit2SectionCommit
        emoji: Commit2SectionCommit
        scipy: Commit2SectionCommit

    class Commit2SectionCommit(TypedDict):
        commit: CommitDef
        section: str


@pytest.mark.parametrize("arg0", [None, "--post-to-release-tag"])
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in (
            # Only need to test when it has tags or no tags
            # DO NOT need to consider all repo types as it doesn't change no-op behavior
            repo_w_no_tags_conventional_commits.__name__,
            repo_w_trunk_only_conventional_commits.__name__,
        )
    ],
)
def test_changelog_noop_is_noop(
    repo_result: BuiltRepoResult,
    arg0: str | None,
    run_cli: RunCliFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    repo = repo_result["repo"]
    repo_def = repo_result["definition"]
    released_versions = get_versions_from_repo_build_def(repo_def)

    version_str = released_versions[-1] if len(released_versions) > 0 else None

    repo.git.reset("--hard")

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
        get_func_qual_name(semantic_release.hvcs.github.build_requests_session),
        return_value=session,
    ), requests_mock.Mocker(session=session) as mocker:
        args = [arg0, f"v{version_str}"] if version_str and arg0 else []
        cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD, *args]
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert not repo.git.status(short=True)
    if args:
        assert not mocker.called
        assert not mock_adapter.called


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        *[
            lazy_fixture(repo_fixture)
            for repo_fixture in [
                # All commit types and one without a release
                repo_w_no_tags_conventional_commits.__name__,
                repo_w_trunk_only_conventional_commits.__name__,
                repo_w_trunk_only_emoji_commits.__name__,
                repo_w_trunk_only_scipy_commits.__name__,
            ]
        ],
        *[
            pytest.param(lazy_fixture(repo_fixture), marks=pytest.mark.comprehensive)
            for repo_fixture in [
                # repo_w_no_tags_conventional_commits.__name__,
                repo_w_no_tags_emoji_commits.__name__,
                repo_w_no_tags_scipy_commits.__name__,
                # repo_w_trunk_only_conventional_commits.__name__,
                # repo_w_trunk_only_emoji_commits.__name__,
                # repo_w_trunk_only_scipy_commits.__name__,
                repo_w_trunk_only_n_prereleases_conventional_commits.__name__,
                repo_w_trunk_only_n_prereleases_emoji_commits.__name__,
                repo_w_trunk_only_n_prereleases_scipy_commits.__name__,
                repo_w_github_flow_w_default_release_channel_conventional_commits.__name__,
                repo_w_github_flow_w_default_release_channel_emoji_commits.__name__,
                repo_w_github_flow_w_default_release_channel_scipy_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_conventional_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_emoji_commits.__name__,
                repo_w_github_flow_w_feature_release_channel_scipy_commits.__name__,
                repo_w_git_flow_conventional_commits.__name__,
                repo_w_git_flow_emoji_commits.__name__,
                repo_w_git_flow_scipy_commits.__name__,
                repo_w_git_flow_w_beta_alpha_rev_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_beta_alpha_rev_prereleases_n_emoji_commits.__name__,
                repo_w_git_flow_w_beta_alpha_rev_prereleases_n_scipy_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_emoji_commits.__name__,
                repo_w_git_flow_w_alpha_prereleases_n_scipy_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_emoji_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_scipy_commits.__name__,
                repo_w_git_flow_w_rc_n_alpha_prereleases_n_conventional_commits_using_tag_format.__name__,
            ]
        ],
    ],
)
def test_changelog_content_regenerated(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
    insertion_flag: str,
):
    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.INIT.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Because we are in init mode, the insertion flag is not present in the changelog
    # we must take it out manually because our repo generation fixture includes it automatically
    with changelog_file.open(newline=os.linesep) as rfd:
        # use os.linesep here because the insertion flag is os-specific
        # but convert the content to universal newlines for comparison
        expected_changelog_content = (
            rfd.read().replace(f"{insertion_flag}{os.linesep}", "").replace("\r", "")
        )

    # Remove the changelog and then check that we can regenerate it
    os.remove(str(changelog_file.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_changelog_content_regenerated_masked_initial_release(
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    get_repo_definition_4_trunk_only_repo_w_tags: GetRepoDefinitionFn,
    example_project_dir: ExProjectDir,
    run_cli: RunCliFn,
    changelog_file: Path,
    insertion_flag: str,
):
    build_definition = get_repo_definition_4_trunk_only_repo_w_tags(
        commit_type="conventional",
        mask_initial_release=True,
        extra_configs={
            "tool.semantic_release.changelog.default_templates.changelog_file": str(
                changelog_file.name
            ),
            "tool.semantic_release.changelog.mode": ChangelogMode.INIT.value,
        },
    )
    build_repo_from_definition(example_project_dir, build_definition)

    # Because we are in init mode, the insertion flag is not present in the changelog
    # we must take it out manually because our repo generation fixture includes it automatically
    with changelog_file.open(newline=os.linesep) as rfd:
        # use os.linesep here because the insertion flag is os-specific
        # but convert the content to universal newlines for comparison
        expected_changelog_content = (
            rfd.read().replace(f"{insertion_flag}{os.linesep}", "").replace("\r", "")
        )

    # Remove the changelog and then check that we can regenerate it
    os.remove(str(changelog_file.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file",
    [
        lazy_fixture(example_changelog_md.__name__),
        lazy_fixture(example_changelog_rst.__name__),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_unchanged(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
):
    """
    Given that the changelog file already exists for the current release,
    When the changelog command is run in "update" mode,
    Then the changelog file is not modified.
    """
    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Capture the expected changelog content
    expected_changelog_content = changelog_file.read_text()

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file",
    [
        lazy_fixture(example_changelog_md.__name__),
        lazy_fixture(example_changelog_rst.__name__),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_w_no_tags_conventional_commits.__name__,
            repo_w_no_tags_emoji_commits.__name__,
            repo_w_no_tags_scipy_commits.__name__,
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_prev_changelog(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
):
    """
    Given that the changelog file does not exist,
    When the changelog command is run in "update" mode,
    Then the changelog file is initialized with the default content.
    """
    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Capture the expected changelog content
    expected_changelog_content = changelog_file.read_text()

    # Remove any previous changelog to update
    os.remove(str(changelog_file.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that the changelog file was re-created
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_flag(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
    insertion_flag: str,
):
    """
    Given a changelog template without the insertion flag,
    When the changelog command is run in "update" mode,
    Then the changelog is not modified.
    """
    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Remove the insertion flag from the changelog
    changelog_file.write_text(
        changelog_file.read_text().replace(
            f"{insertion_flag}\n",
            "",
            1,
        )
    )

    # Capture the expected changelog content
    expected_changelog_content = changelog_file.read_text()

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_format, changelog_file",
    [
        (
            ChangelogOutputFormat.MARKDOWN,
            lazy_fixture(changelog_md_file.__name__),
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT,
            lazy_fixture(changelog_rst_file.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # MUST HAVE at least 2 tags!
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_header(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_format: ChangelogOutputFormat,
    changelog_file: Path,
    default_md_changelog_insertion_flag: str,
    default_rst_changelog_insertion_flag: str,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    """
    Given a changelog template with the insertion flag at the beginning of the file,
    When the changelog command is run in "update" mode,
    Then the changelog is rebuilt with the latest release prepended to the existing content.
    """
    repo = repo_result["repo"]

    # Mappings of correct fixtures to use based on the changelog format
    insertion_flags = {
        ChangelogOutputFormat.MARKDOWN: (
            "# CHANGELOG{ls}{ls}{flag}".format(
                ls=os.linesep,
                flag=default_md_changelog_insertion_flag,
            )
        ),
        ChangelogOutputFormat.RESTRUCTURED_TEXT: (
            ".. _changelog:{ls}{ls}{h1_border}{ls}CHANGELOG{ls}{h1_border}{ls}{ls}{flag}".format(
                ls=os.linesep,
                h1_border="=" * 9,
                flag=default_rst_changelog_insertion_flag,
            )
        ),
    }

    # Select the correct insertion flag based on the format
    insertion_flag = insertion_flags[changelog_format]

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.insertion_flag",
        insertion_flag,
    )

    # Capture the expected changelog content of current release
    with changelog_file.open(newline=os.linesep) as rfd:
        expected_changelog_content = rfd.read()

    # Reset changelog file to last release
    previous_tag = f'v{get_versions_from_repo_build_def(repo_result["definition"])[-2]}'
    repo.git.checkout(previous_tag, "--", str(changelog_file.name))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_format, changelog_file, insertion_flag",
    [
        (
            ChangelogOutputFormat.MARKDOWN,
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT,
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # MUST HAVE at least 2 tags!
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_footer(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_format: ChangelogOutputFormat,
    changelog_file: Path,
    insertion_flag: str,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
):
    """
    Given a changelog template with the insertion flag at the end of the file,
    When the changelog command is run in "update" mode,
    Then the changelog is rebuilt with only the latest release.
    """
    repo_result["repo"]

    # Mappings of correct fixtures to use based on the changelog format
    prev_version_tag = (
        f"v{get_versions_from_repo_build_def(repo_result['definition'])[-2]}"
    )
    split_flags = {
        ChangelogOutputFormat.MARKDOWN: f"\n\n## {prev_version_tag}",
        ChangelogOutputFormat.RESTRUCTURED_TEXT: f"\n\n.. _changelog-{prev_version_tag}:",
    }

    # Select the correct variable based on the format
    split_flag = split_flags[changelog_format]

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Capture the expected changelog content of current release (w/ universal newlines)
    # NOTE: universal newlines is fine because we use our split flag above is also universal
    expected_changelog_content = changelog_file.read_text().split(split_flag)[0]

    # Determine the contents to save while truncating the rest
    with changelog_file.open(newline=os.linesep) as rfd:
        # read file contents grabbing only the text before the insertion flag
        truncated_contents = str.join(
            "",
            [
                rfd.read().split(insertion_flag)[0],
                insertion_flag,
                os.linesep,
            ],
        )

    # Remove any text after the insertion flag
    # force output to not perform any newline translations
    with changelog_file.open(mode="w", newline="") as wfd:
        # overwrite the file with truncated contents
        wfd.write(truncated_contents)
        wfd.flush()

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    actual_content = changelog_file.read_text()

    # Check that the changelog content only includes the latest release as there
    # is no previous release information as the insertion flag is at the end of the file
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_file, insertion_flag",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        lazy_fixture(repo_fixture)
        for repo_fixture in [
            # Must not have a single release/tag
            repo_w_no_tags_conventional_commits.__name__,
            repo_w_no_tags_emoji_commits.__name__,
            repo_w_no_tags_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_no_releases(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    changelog_file: Path,
    insertion_flag: str,
):
    """
    Given the repository has no releases and the user has provided a initialized changelog,
    When the changelog command is run in "update" mode,
    Then the changelog is populated with unreleased changes.
    """
    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    # Custom text to maintain (must be different from the default)
    custom_text = "---{ls}{ls}Custom footer text{ls}".format(ls=os.linesep)

    # Capture and modify the current changelog content to become the expected output
    # We much use os.linesep here since the insertion flag is os-specific
    with changelog_file.open(newline=os.linesep) as rfd:
        initial_changelog_parts = rfd.read().split(insertion_flag)

    # content is os-specific because of the insertion flag & how we read the original file
    expected_changelog_content = str.join(
        insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                os.linesep,
                [
                    initial_changelog_parts[1],
                    "",
                    custom_text,
                ],
            ),
        ],
    )

    # Grab the Unreleased changelog & create the initalized user changelog
    # force output to not perform any newline translations
    with changelog_file.open(mode="w", newline="") as wfd:
        wfd.write(
            str.join(
                insertion_flag,
                [initial_changelog_parts[0], f"{os.linesep * 2}{custom_text}"],
            )
        )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog footer is maintained and updated with Unreleased info
    assert expected_changelog_content == actual_content


@pytest.mark.parametrize(
    "changelog_format, changelog_file, insertion_flag",
    [
        (
            ChangelogOutputFormat.MARKDOWN,
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
        ),
        (
            ChangelogOutputFormat.RESTRUCTURED_TEXT,
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result, commit_type",
    [
        (lazy_fixture(repo_fixture), repo_fixture.split("_")[-2])
        for repo_fixture in [
            repo_w_trunk_only_conventional_commits.__name__,
            repo_w_trunk_only_emoji_commits.__name__,
            repo_w_trunk_only_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_update_mode_unreleased_n_released(
    repo_result: BuiltRepoResult,
    commit_type: CommitConvention,
    changelog_format: ChangelogOutputFormat,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_git_ssh_url: str,
    file_in_repo: str,
    commit_n_rtn_changelog_entry: CommitNReturnChangelogEntryFn,
    changelog_file: Path,
    insertion_flag: str,
    get_commit_def_of_conventional_commit: GetCommitDefFn[ConventionalCommitParser],
    get_commit_def_of_emoji_commit: GetCommitDefFn[EmojiCommitParser],
    get_commit_def_of_scipy_commit: GetCommitDefFn[ScipyCommitParser],
    default_conventional_parser: ConventionalCommitParser,
    default_emoji_parser: EmojiCommitParser,
    default_scipy_parser: ScipyCommitParser,
):
    """
    Given there are unreleased changes and a previous release in the changelog,
    When the changelog command is run in "update" mode,
    Then the changelog is only updated with the unreleased changes.
    """
    repo = repo_result["repo"]

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.changelog_file",
        str(changelog_file.name),
    )

    commit_n_section: Commit2Section = {
        "conventional": {
            "commit": get_commit_def_of_conventional_commit(
                "perf: improve the performance of the application",
                parser=default_conventional_parser,
            ),
            "section": "Performance Improvements",
        },
        "emoji": {
            "commit": get_commit_def_of_emoji_commit(
                ":zap: improve the performance of the application",
                parser=default_emoji_parser,
            ),
            "section": ":zap:",
        },
        "scipy": {
            "commit": get_commit_def_of_scipy_commit(
                "MAINT: fix an issue",
                parser=default_scipy_parser,
            ),
            "section": "Fix",
        },
    }

    # Custom text to maintain (must be different from the default)
    custom_text = "---\n\nCustom footer text\n"

    # Update the changelog with the custom footer text
    changelog_file.write_text(
        str.join(
            "\n\n",
            [
                changelog_file.read_text(),
                custom_text,
            ],
        )
    )

    # Capture the current changelog content so we can estimate the expected output
    # We much use os.linesep here since the insertion flag is os-specific
    with changelog_file.open(newline=os.linesep) as rfd:
        initial_changelog_parts = rfd.read().split(insertion_flag)

    # Make a change to the repo to create unreleased changes
    add_text_to_file(repo, file_in_repo)
    unreleased_commit_entry = commit_n_rtn_changelog_entry(
        repo,
        commit_n_section[commit_type]["commit"],
    )

    with mock.patch.dict(os.environ, {}, clear=True):
        hvcs = Github(example_git_ssh_url, hvcs_domain=EXAMPLE_HVCS_DOMAIN)
        assert hvcs.repo_name  # force caching of repo values (ignoring the env)

    unreleased_change_variants = {
        ChangelogOutputFormat.MARKDOWN: dedent(
            f"""
            ## Unreleased

            ### {commit_n_section[commit_type]["section"]}

            - {unreleased_commit_entry['desc'].capitalize()}
              ([`{unreleased_commit_entry['sha'][:7]}`]({hvcs.commit_hash_url(unreleased_commit_entry['sha'])}))
            """
        ),
        ChangelogOutputFormat.RESTRUCTURED_TEXT: dedent(
            f"""
            .. _changelog-unreleased:

            Unreleased
            ==========

            {commit_n_section[commit_type]["section"]}
            {"-" * len(commit_n_section[commit_type]["section"])}

            * {unreleased_commit_entry['desc'].capitalize()} (`{unreleased_commit_entry['sha'][:7]}`_)

            .. _{unreleased_commit_entry['sha'][:7]}: {hvcs.commit_hash_url(unreleased_commit_entry['sha'])}
            """
        ),
    }

    # Normalize line endings to the OS-specific line ending
    unreleased_changes = str.join(
        os.linesep,
        [
            line.replace("\r", "")
            for line in unreleased_change_variants[changelog_format].split("\n")
        ],
    )

    # Generate the expected changelog content (os aware because of insertion flag & initial parts)
    expected_changelog_content = str.join(
        insertion_flag,
        [
            initial_changelog_parts[0],
            str.join(
                "",
                [
                    os.linesep,
                    # Unreleased changes
                    unreleased_changes,
                    # Previous release notes
                    initial_changelog_parts[1],
                ],
            ),
        ],
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Ensure changelog exists
    assert changelog_file.exists()

    # Capture the new changelog content (os aware because of expected content)
    with changelog_file.open(newline=os.linesep) as rfd:
        actual_content = rfd.read()

    # Check that the changelog content is the same as before
    assert expected_changelog_content == actual_content


# Just need to test that it works for "a" project, not all
@pytest.mark.usefixtures(repo_w_trunk_only_n_prereleases_conventional_commits.__name__)
@pytest.mark.parametrize(
    "args", [("--post-to-release-tag", "v1.99.91910000000000000000000000000")]
)
def test_changelog_release_tag_not_in_history(
    args: list[str],
    run_cli: RunCliFn,
):
    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, *args]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(2, result, cli_cmd)
    assert "not in release history" in result.stderr.lower()


@pytest.mark.usefixtures(repo_w_trunk_only_n_prereleases_conventional_commits.__name__)
@pytest.mark.parametrize(
    "args",
    [
        ("--post-to-release-tag", "v0.1.0"),  #      first release
        ("--post-to-release-tag", "v0.1.1-rc.1"),  # second release
        ("--post-to-release-tag", "v0.2.0"),  #      latest release
    ],
)
def test_changelog_post_to_release(args: list[str], run_cli: RunCliFn):
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
        # Patching the specific module's reference to the build_requests_session function
        f"{semantic_release.hvcs.github.__name__}.{semantic_release.hvcs.github.build_requests_session.__name__}",
        return_value=session,
    ) as build_requests_session_mock:
        # Act
        cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, *args]
        result = run_cli(
            cli_cmd[1:],
            env={
                "CI": "true",
                "VIRTUAL_ENV": os.getenv("VIRTUAL_ENV", "./.venv"),
            },
        )

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert build_requests_session_mock.called
    assert mock_adapter.called
    assert mock_adapter.last_request is not None
    assert expected_request_url == mock_adapter.last_request.url


@pytest.mark.parametrize(
    "repo_result",
    [lazy_fixture(repo_w_trunk_only_n_prereleases_conventional_commits.__name__)],
)
def test_custom_release_notes_template(
    repo_result: BuiltRepoResult,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    post_mocker: Mocker,
    run_cli: RunCliFn,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    expected_call_count = 1
    version = get_versions_from_repo_build_def(repo_result["definition"])[-1]

    # Setup
    use_release_notes_template()
    runtime_context = retrieve_runtime_context(repo_result["repo"])
    release_history = get_release_history_from_context(runtime_context)
    release = release_history.released[version]
    tag = runtime_context.version_translator.str_to_tag(str(version))

    expected_release_notes = (
        runtime_context.template_environment.from_string(EXAMPLE_RELEASE_NOTES_TEMPLATE)
        .render(release=release)
        .rstrip()
        + os.linesep
    )

    # ensure normalized line endings after render
    expected_release_notes = str.join(
        os.linesep,
        str.split(expected_release_notes.replace("\r", ""), "\n"),
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD, "--post-to-release-tag", tag]
    result = run_cli(cli_cmd[1:])

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert expected_call_count == post_mocker.call_count
    assert post_mocker.last_request is not None

    actual_notes = post_mocker.last_request.json()["body"]
    assert expected_release_notes == actual_notes


@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_changelog_default_on_empty_template_dir(
    example_changelog_md: Path,
    changelog_template_dir: Path,
    example_project_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    run_cli: RunCliFn,
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
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that our default changelog was created because the user's template dir was empty
    assert example_changelog_md.exists()


@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_changelog_default_on_incorrect_config_template_file(
    example_changelog_md: Path,
    changelog_template_dir: Path,
    example_project_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    run_cli: RunCliFn,
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
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Check that our default changelog was created because the user's template dir was empty
    assert example_changelog_md.exists()


@pytest.mark.parametrize("bad_changelog_file_str", ("/etc/passwd", "../../.ssh/id_rsa"))
@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_changelog_prevent_malicious_path_traversal_file(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    bad_changelog_file_str: str,
    run_cli: RunCliFn,
):
    # Setup: A malicious path traversal filepath outside of the repository
    update_pyproject_toml(
        "tool.semantic_release.changelog.changelog_file",
        bad_changelog_file_str,
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert (
        "Changelog file destination must be inside of the repository directory."
        in result.stderr
    )


@pytest.mark.parametrize("template_dir_path", ("~/.ssh", "../../.ssh"))
@pytest.mark.usefixtures(repo_w_trunk_only_conventional_commits.__name__)
def test_changelog_prevent_external_path_traversal_dir(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    template_dir_path: str,
    run_cli: RunCliFn,
):
    # Setup: A malicious path traversal filepath outside of the repository
    update_pyproject_toml(
        "tool.semantic_release.changelog.template_dir",
        template_dir_path,
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, "--noop", CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    assert (
        "Template directory must be inside of the repository directory."
        in result.stderr
    )
