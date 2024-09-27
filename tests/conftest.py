"""Note: fixtures are stored in the tests/fixtures directory for better organisation"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner
from git import Commit, Repo

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


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


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
    temporary_files: list[str] = []

    def _netrc_file(machine: str) -> _TemporaryFileWrapper[str]:
        ctx_mgr = NamedTemporaryFile("w", delete=False)
        with ctx_mgr as netrc_fd:
            temporary_files.append(ctx_mgr.name)

            netrc_fd.write(f"machine {machine}{os.linesep}")
            netrc_fd.write(f"login {default_netrc_username}{os.linesep}")
            netrc_fd.write(f"password {default_netrc_password}{os.linesep}")
            netrc_fd.flush()
            return ctx_mgr

    try:
        yield _netrc_file
    finally:
        for temp_file in temporary_files:
            os.unlink(temp_file)


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


@pytest.fixture(scope="session")
def clean_os_environment() -> dict[str, str]:
    return dict(  # type: ignore
        filter(
            lambda k_v: k_v[1] is not None,
            {
                "PATH": os.getenv("PATH"),
                "HOME": os.getenv("HOME"),
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
