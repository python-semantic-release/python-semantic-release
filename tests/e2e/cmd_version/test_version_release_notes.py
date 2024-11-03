from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main
from semantic_release.version.version import Version

from tests.const import EXAMPLE_RELEASE_NOTES_TEMPLATE, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.repos import repo_with_no_tags_angular_commits
from tests.util import assert_successful_exit_code, get_release_history_from_context

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from git import Repo
    from requests_mock import Mocker

    from tests.e2e.conftest import RetrieveRuntimeContextFn
    from tests.fixtures.example_project import UseReleaseNotesTemplateFn


@pytest.mark.parametrize(
    "repo, next_release_version",
    [
        (lazy_fixture(repo_with_no_tags_angular_commits.__name__), "0.1.0"),
    ],
)
def test_custom_release_notes_template(
    repo: Repo,
    next_release_version: str,
    cli_runner: CliRunner,
    use_release_notes_template: UseReleaseNotesTemplateFn,
    retrieve_runtime_context: RetrieveRuntimeContextFn,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
) -> None:
    """Verify the template `.release_notes.md.j2` from `template_dir` is used."""
    release_version = Version.parse(next_release_version)

    # Setup
    use_release_notes_template()
    runtime_context = retrieve_runtime_context(repo)

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--vcs-release"]
    result = cli_runner.invoke(main, cli_cmd[1:])

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
    assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
    assert post_mocker.call_count == 1
    assert post_mocker.last_request is not None

    actual_notes = post_mocker.last_request.json()["body"]
    assert expected_release_notes == actual_notes
