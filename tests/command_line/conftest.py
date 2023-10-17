from pathlib import Path
from typing import Any, Generator
from unittest import mock
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from git.repo import Repo

from semantic_release.changelog.context import make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import load_raw_config_file


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


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
