"""Note: fixtures are stored in the tests/fixtures directory for better organisation"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.fixtures import *
from tests.util import remove_dir_tree

if TYPE_CHECKING:
    from typing import Generator, Protocol

    class TeardownCachedDirFn(Protocol):
        def __call__(self, directory: Path) -> Path: ...


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
