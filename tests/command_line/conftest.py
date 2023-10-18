from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator
from unittest import mock
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

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

    from _pytest.monkeypatch import MonkeyPatch
    from git.repo import Repo

    from semantic_release.changelog.release_history import ReleaseHistory


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture
def mocked_session_post() -> Generator[MagicMock, Any, None]:
    """Mock the `post()` method in `requests.Session`."""
    with mock.patch("requests.sessions.Session.post") as mocked_session:
        yield mocked_session


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
    config_text = load_raw_config_file(config_path)
    return RawConfig.model_validate(config_text)


@pytest.fixture
def cli_options(config_path: Path) -> GlobalCommandLineOptions:
    return GlobalCommandLineOptions(
        noop=False,
        verbosity=0,
        strict=False,
        config_file=config_path,
    )


@pytest.fixture
def runtime_context_with_tags(
    # note (1/2): the following fixture must precede the `raw_config` fixture...
    repo_with_single_branch_and_prereleases_angular_commits: Repo,
    # note (2/2): ... so that the config file gets updated before it is read:
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
