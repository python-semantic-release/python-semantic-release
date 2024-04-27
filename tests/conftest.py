"""Note: fixtures are stored in the tests/fixtures directory for better organisation"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import pytest
from git import Commit

from tests.fixtures import *
from tests.util import remove_dir_tree

if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper
    from typing import Generator, Protocol

    class MakeCommitObjFn(Protocol):
        def __call__(self, message: str) -> Commit: ...

    class NetrcFileFn(Protocol):
        def __call__(self, machine: str) -> _TemporaryFileWrapper[str]: ...

    class TeardownCachedDirFn(Protocol):
        def __call__(self, directory: Path) -> Path: ...


@pytest.fixture(scope="session")
def default_netrc_username() -> str:
    return "username"


@pytest.fixture(scope="session")
def default_netrc_password() -> str:
    return "password"


@pytest.fixture(scope="session")
def netrc_file(
    default_netrc_username: str,
    default_netrc_password: str,
) -> Generator[NetrcFileFn, None, None]:
    entered_context_managers: list[_TemporaryFileWrapper[str]] = []

    def _netrc_file(machine: str) -> _TemporaryFileWrapper[str]:
        ctx_mgr = NamedTemporaryFile("w")
        netrc_fd = ctx_mgr.__enter__()
        entered_context_managers.append(ctx_mgr)

        netrc_fd.write(f"machine {machine}" + "\n")
        netrc_fd.write(f"login {default_netrc_username}" + "\n")
        netrc_fd.write(f"password {default_netrc_password}" + "\n")
        netrc_fd.flush()
        return ctx_mgr

    exception = None
    try:
        yield _netrc_file
    except Exception as err:
        exception = err
    finally:
        for context_manager in entered_context_managers:
            context_manager.__exit__(
                None if not exception else type(exception),
                exception,
                None if not exception else exception.__traceback__,
            )


@pytest.fixture(scope="session")
def cached_files_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("cached_files_dir")


@pytest.fixture(scope="session")
def teardown_cached_dir() -> Generator[TeardownCachedDirFn, None, None]:
    directories: list[Path] = []

    def _teardown_cached_dir(directory: Path | str) -> Path:
        directories.append(Path(directory))
        return directories[-1]

    try:
        yield _teardown_cached_dir
    finally:
        # clean up any registered cached directories
        for directory in directories:
            if directory.exists():
                remove_dir_tree(directory, force=True)


@pytest.fixture(scope="session")
def make_commit_obj() -> MakeCommitObjFn:
    def _make_commit(message: str) -> Commit:
        return Commit(repo=Repo(), binsha=Commit.NULL_BIN_SHA, message=message)

    return _make_commit
