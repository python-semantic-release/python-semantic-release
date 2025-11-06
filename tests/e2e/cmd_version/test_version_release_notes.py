from __future__ import annotations

import os
from datetime import timezone
from typing import TYPE_CHECKING

import pytest
from freezegun import freeze_time
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.version.version import Version

from tests.const import (
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    MAIN_PROG_NAME,
    VERSION_SUBCMD,
    RepoActionStep,
)
from tests.fixtures.repos import repo_w_no_tags_conventional_commits
from tests.fixtures.repos.trunk_based_dev.repo_w_no_tags import (
    repo_w_no_tags_emoji_commits,
    repo_w_no_tags_scipy_commits,
)
from tests.util import assert_successful_exit_code, get_release_history_from_context

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from tests.conftest import GetStableDateNowFn, RunCliFn
    from tests.e2e.conftest import (
        RetrieveRuntimeContextFn,
    )
    from tests.fixtures.example_project import (
        UpdatePyprojectTomlFn,
        UseReleaseNotesTemplateFn,
    )
    from tests.fixtures.git_repo import (
        BuiltRepoResult,
        GenerateDefaultReleaseNotesFromDefFn,
        GetHvcsClientFromRepoDefFn,
    )


@pytest.mark.parametrize(
    "repo_result, next_release_version",
    [
        (lazy_fixture(repo_w_no_tags_conventional_commits.__name__), "1.0.0"),
    ],
)
def test_custom_release_notes_template(
    repo_result: BuiltRepoResult,
    next_release_version: str,
    run_cli: RunCliFn,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    release_version = Version.parse(next_release_version)

    # Setup
    use_release_notes_template()
    runtime_context = retrieve_runtime_context(repo_result["repo"])

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--vcs-release"]
    result = run_cli(cli_cmd[1:])

    # Must run this after the action because the release history object should be pulled from the
    # repository after a tag is created
    release_history = get_release_history_from_context(runtime_context)
    release = release_history.released[release_version]

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

    # Assert
    assert_successful_exit_code(result, cli_cmd)
    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None

    actual_notes = post_mocker.last_request.json()["body"]
    assert expected_release_notes == actual_notes


@pytest.mark.parametrize(
    "repo_result, license_name, license_setting, mask_initial_release",
    [
        pytest.param(
            lazy_fixture(repo_fixture_name),
            license_name,
            license_setting,
            mask_initial_release,
            marks=pytest.mark.comprehensive,
        )
        for mask_initial_release in [True, False]
        for license_name in ["", "MIT", "GPL-3.0"]
        for license_setting in [
            "project.license-expression",
            "project.license",  # deprecated
            "project.license.text",  # deprecated
        ]
        for repo_fixture_name in [
            repo_w_no_tags_conventional_commits.__name__,
            repo_w_no_tags_emoji_commits.__name__,
            repo_w_no_tags_scipy_commits.__name__,
        ]
    ],
)
def test_default_release_notes_license_statement(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    license_name: str,
    license_setting: str,
    mask_initial_release: bool,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    stable_now_date: GetStableDateNowFn,
    get_hvcs_client_from_repo_def: GetHvcsClientFromRepoDefFn,
    generate_default_release_notes_from_def: GenerateDefaultReleaseNotesFromDefFn,
):
    new_version = "1.0.0"

    # Setup
    now_datetime = stable_now_date()
    repo_def = list(repo_result["definition"])
    repo_def.append(
        {
            "action": RepoActionStep.RELEASE,
            "details": {
                "version": new_version,
                "datetime": now_datetime.isoformat(timespec="seconds"),
            },
        }
    )
    # Setup: Overwrite the default setting (defined in test.const)
    update_pyproject_toml("project.license-expression", None)

    # Setup: set the license for the test
    update_pyproject_toml(license_setting, license_name)

    # Setup: set mask_initial_release value in configuration
    update_pyproject_toml(
        "tool.semantic_release.changelog.default_templates.mask_initial_release",
        mask_initial_release,
    )

    expected_release_notes = generate_default_release_notes_from_def(
        version_actions=repo_def,
        hvcs=get_hvcs_client_from_repo_def(repo_def),
        previous_version=None,
        license_name=license_name,
        mask_initial_release=mask_initial_release,
    )

    # Act
    with freeze_time(now_datetime.astimezone(timezone.utc)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--no-changelog", "--vcs-release"]
        result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert mocked_git_fetch.call_count == 1  # fetch called to check for remote changes
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None
    request_body = post_mocker.last_request.json()

    assert "body" in request_body
    actual_notes = request_body["body"]

    assert expected_release_notes == actual_notes
