from __future__ import annotations

import os
from pathlib import Path
from re import IGNORECASE, compile as regexp
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from requests_mock import ANY

from semantic_release.cli import config as cli_config_module
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.const import DEFAULT_CONFIG_FILE
from semantic_release.cli.util import load_raw_config_file

from tests.util import prepare_mocked_git_command_wrapper_type

if TYPE_CHECKING:
    from re import Pattern
    from typing import Protocol

    from git.repo import Repo
    from pytest import MonkeyPatch
    from requests_mock.mocker import Mocker

    from tests.fixtures.example_project import ExProjectDir

    class GetSanitizedChangelogContentFn(Protocol):
        def __call__(
            self,
            repo_dir: Path,
            remove_insertion_flag: bool = True,
        ) -> str: ...

    class ReadConfigFileFn(Protocol):
        """Read the raw config file from `config_path`."""

        def __call__(self, file: Path | str) -> RawConfig: ...

    class RetrieveRuntimeContextFn(Protocol):
        """Retrieve the runtime context for a repo."""

        def __call__(self, repo: Repo) -> RuntimeContext: ...


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply the e2e marker to all tests in the end-to-end test directory."""
    cli_test_directory = Path(__file__).parent
    for item in items:
        if cli_test_directory in item.path.parents:
            item.add_marker(pytest.mark.e2e)


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
    monkeypatch.setattr(cli_config_module.Repo, "GitCommandWrapperType", cls)
    return mocked_push


@pytest.fixture
def config_path(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / DEFAULT_CONFIG_FILE


@pytest.fixture
def read_config_file() -> ReadConfigFileFn:
    def _read_config_file(file: Path | str) -> RawConfig:
        config_text = load_raw_config_file(file)
        return RawConfig.model_validate(config_text)

    return _read_config_file


@pytest.fixture
def cli_options(config_path: Path) -> GlobalCommandLineOptions:
    return GlobalCommandLineOptions(
        noop=False,
        verbosity=0,
        strict=False,
        config_file=str(config_path),
    )


@pytest.fixture
def retrieve_runtime_context(
    read_config_file: ReadConfigFileFn,
    cli_options: GlobalCommandLineOptions,
) -> RetrieveRuntimeContextFn:
    def _retrieve_runtime_context(repo: Repo) -> RuntimeContext:
        cwd = os.getcwd()
        repo_dir = str(Path(repo.working_dir).resolve())

        os.chdir(repo_dir)
        try:
            raw_config = read_config_file(cli_options.config_file)
            return RuntimeContext.from_raw_config(raw_config, cli_options)
        finally:
            os.chdir(cwd)

    return _retrieve_runtime_context


@pytest.fixture(scope="session")
def long_hash_pattern() -> Pattern:
    return regexp(r"\b([0-9a-f]{40})\b", IGNORECASE)


@pytest.fixture(scope="session")
def short_hash_pattern() -> Pattern:
    return regexp(r"\b([0-9a-f]{7})\b", IGNORECASE)


@pytest.fixture(scope="session")
def get_sanitized_rst_changelog_content(
    changelog_rst_file: Path,
    default_rst_changelog_insertion_flag: str,
    long_hash_pattern: Pattern,
    short_hash_pattern: Pattern,
) -> GetSanitizedChangelogContentFn:
    rst_short_hash_link_pattern = regexp(r"(_[0-9a-f]{7})\b", IGNORECASE)

    def _get_sanitized_rst_changelog_content(
        repo_dir: Path,
        remove_insertion_flag: bool = True,
    ) -> str:
        # TODO: v10 change -- default turns to update so this is not needed
        # Because we are in init mode, the insertion flag is not present in the changelog
        # we must take it out manually because our repo generation fixture includes it automatically
        with (repo_dir / changelog_rst_file).open(newline=os.linesep) as rfd:
            # use os.linesep here because the insertion flag is os-specific
            # but convert the content to universal newlines for comparison
            changelog_content = (
                rfd.read().replace(
                    f"{default_rst_changelog_insertion_flag}{os.linesep}", ""
                )
                if remove_insertion_flag
                else rfd.read()
            ).replace("\r", "")

        changelog_content = long_hash_pattern.sub("0" * 40, changelog_content)
        changelog_content = short_hash_pattern.sub("0" * 7, changelog_content)
        return rst_short_hash_link_pattern.sub(f'_{"0" * 7}', changelog_content)

    return _get_sanitized_rst_changelog_content


@pytest.fixture(scope="session")
def get_sanitized_md_changelog_content(
    changelog_md_file: Path,
    default_md_changelog_insertion_flag: str,
    long_hash_pattern: Pattern,
    short_hash_pattern: Pattern,
) -> GetSanitizedChangelogContentFn:
    def _get_sanitized_md_changelog_content(
        repo_dir: Path,
        remove_insertion_flag: bool = True,
    ) -> str:
        # TODO: v10 change -- default turns to update so this is not needed
        # Because we are in init mode, the insertion flag is not present in the changelog
        # we must take it out manually because our repo generation fixture includes it automatically
        with (repo_dir / changelog_md_file).open(newline=os.linesep) as rfd:
            # use os.linesep here because the insertion flag is os-specific
            # but convert the content to universal newlines for comparison
            changelog_content = (
                rfd.read().replace(
                    f"{default_md_changelog_insertion_flag}{os.linesep}", ""
                )
                if remove_insertion_flag
                else rfd.read()
            ).replace("\r", "")

        changelog_content = long_hash_pattern.sub("0" * 40, changelog_content)
        return short_hash_pattern.sub("0" * 7, changelog_content)

    return _get_sanitized_md_changelog_content
