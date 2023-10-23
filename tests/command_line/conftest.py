from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from requests_mock import ANY

from semantic_release.cli.commands import main
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import load_raw_config_file

from tests.util import (
    get_release_history_from_context,
    prepare_mocked_git_command_wrapper_type,
)

if TYPE_CHECKING:
    from pathlib import Path

    from git.repo import Repo
    from pytest import MonkeyPatch
    from requests_mock.mocker import Mocker

    from semantic_release.changelog.release_history import ReleaseHistory


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture
def post_mocker(requests_mock: Mocker) -> Mocker:
    """Patch all POST requests, mocking a response body for VCS release creation."""
    requests_mock.register_uri("POST", ANY, json={"id": 999})
    return requests_mock


@pytest.fixture
def mocked_git_push(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the `Repo.git.push()` method in `semantic_release.cli.main`."""
    mocked_push = MagicMock()
    cls = prepare_mocked_git_command_wrapper_type(push=mocked_push)
    monkeypatch.setattr(main.Repo, "GitCommandWrapperType", cls)
    return mocked_push


@pytest.fixture
def config_path(example_project: Path) -> Path:
    return example_project / DEFAULT_CONFIG_FILE


@pytest.fixture
def raw_config(config_path: Path) -> RawConfig:
    """
    Read the raw config file from `config_path`.

    note: a `tests.fixtures.example_project` fixture must precede this one
            otherwise, the `config_path` file will not exist, and this fixture will fail
    """
    config_text = load_raw_config_file(config_path)
    return RawConfig.model_validate(config_text)


@pytest.fixture
def cli_options(config_path: Path) -> GlobalCommandLineOptions:
    return GlobalCommandLineOptions(
        noop=False,
        verbosity=0,
        strict=False,
        config_file=str(config_path),
    )


@pytest.fixture
def runtime_context_with_tags(
    repo_with_single_branch_and_prereleases_angular_commits: Repo,
    raw_config: RawConfig,
    cli_options: GlobalCommandLineOptions,
) -> RuntimeContext:
    return RuntimeContext.from_raw_config(
        raw_config,
        repo_with_single_branch_and_prereleases_angular_commits,
        cli_options,
    )


@pytest.fixture
def release_history(runtime_context_with_tags: RuntimeContext) -> ReleaseHistory:
    return get_release_history_from_context(runtime_context_with_tags)


@pytest.fixture
def runtime_context_with_no_tags(
    repo_with_no_tags_angular_commits: Repo,
    raw_config: RawConfig,
    cli_options: GlobalCommandLineOptions,
) -> RuntimeContext:
    return RuntimeContext.from_raw_config(
        raw_config,
        repo_with_no_tags_angular_commits,
        cli_options,
    )
