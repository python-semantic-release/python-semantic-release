from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from filelock import FileLock, Timeout

import tests.conftest as root_conftest

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class _DummyCache:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value


class _DummyConfig:
    def __init__(self) -> None:
        self.cache = _DummyCache()


class _DummyRequest:
    def __init__(self) -> None:
        self.config = _DummyConfig()


class _DummyTmpPathFactory:
    def __init__(self, basetemp: Path) -> None:
        self._basetemp = basetemp

    def getbasetemp(self) -> Path:
        return self._basetemp


def _can_acquire_lock_immediately(lock_file: Path) -> bool:
    lock = FileLock(lock_file)

    try:
        proxy = lock.acquire(timeout=0, blocking=False)
    except Timeout:
        return False

    proxy.lock.release()
    return True


def test_build_repo_or_copy_cache_holds_lock_until_copy_complete(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Given a cache hit, when the cache is copied, then no worker can reacquire the repo lock mid-copy."""
    cached_files_dir = tmp_path / "cached-repos"
    cached_files_dir.mkdir()

    repo_name = "repo-w-lock-check"
    build_spec_hash = "stable-build-hash"
    cached_repo_path = cached_files_dir / repo_name
    cached_repo_path.mkdir()
    (cached_repo_path / "README.txt").write_text(
        "cached repo content", encoding="utf-8"
    )

    lock_file = tmp_path / f"{repo_name}.lock"
    lock_was_available_during_copy = False

    def get_cached_repo_data(_repo_name: str) -> dict[str, Any] | None:
        return {
            "build_date": "2026-03-08",
            "build_spec_hash": build_spec_hash,
            "build_definition": [],
        }

    def set_cached_repo_data(_repo_name: str, _repo_data: dict[str, Any]) -> None:
        return None

    def get_authorization_to_build_repo_cache(_repo_name: str):
        return FileLock(lock_file).acquire(timeout=1, blocking=True)

    def build_repo_func(_dest_dir: Path) -> list[Any]:
        raise AssertionError("build_repo_func should not run when cache is valid")

    # Keep access to the original function while monkeypatching.
    original_copy_dir_tree = root_conftest.copy_dir_tree

    def wrapped_copy_dir_tree(src_dir: Path | str, dst_dir: Path | str) -> None:
        nonlocal lock_was_available_during_copy
        lock_was_available_during_copy = _can_acquire_lock_immediately(lock_file)
        original_copy_dir_tree(src_dir, dst_dir)

    monkeypatch.setattr(root_conftest, "copy_dir_tree", wrapped_copy_dir_tree)

    build_repo_or_copy_cache = root_conftest.build_repo_or_copy_cache.__wrapped__(
        cached_files_dir=cached_files_dir,
        today_date_str="2026-03-08",
        stable_now_date=lambda: datetime(2026, 3, 8, tzinfo=timezone.utc),
        get_cached_repo_data=get_cached_repo_data,
        set_cached_repo_data=set_cached_repo_data,
        get_authorization_to_build_repo_cache=get_authorization_to_build_repo_cache,
    )

    dest_dir = tmp_path / "copied-repo"
    result_dir = build_repo_or_copy_cache(
        repo_name,
        build_spec_hash,
        build_repo_func,
        dest_dir=dest_dir,
    )

    assert result_dir == dest_dir
    assert (dest_dir / "README.txt").read_text(
        encoding="utf-8"
    ) == "cached repo content"
    assert not lock_was_available_during_copy
    assert _can_acquire_lock_immediately(lock_file)


def test_cached_repo_metadata_is_shared_via_filesystem(tmp_path: Path) -> None:
    """Given isolated cache objects, when repo metadata is set, then another worker can read it."""
    cached_files_dir = tmp_path / "cached-repos"
    cached_files_dir.mkdir()

    writer_request = _DummyRequest()
    reader_request = _DummyRequest()

    set_cached_repo_data = root_conftest.set_cached_repo_data.__wrapped__(
        request=writer_request,
        cached_files_dir=cached_files_dir,
    )
    get_cached_repo_data = root_conftest.get_cached_repo_data.__wrapped__(
        request=reader_request,
        cached_files_dir=cached_files_dir,
    )

    expected_data = {
        "build_date": "2026-03-08",
        "build_spec_hash": "abc123",
        "build_definition": [],
    }
    set_cached_repo_data("repo-data-check", expected_data)

    assert get_cached_repo_data("repo-data-check") == expected_data


def test_get_authorization_to_build_repo_cache_uses_xdist_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Given xdist worker env, when requesting a lock, then the per-repo lock is acquired."""
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")
    shared_base = tmp_path / "pytest-1" / "popen-gw0"
    shared_base.mkdir(parents=True)

    get_authorization = root_conftest.get_authorization_to_build_repo_cache.__wrapped__(
        tmp_path_factory=_DummyTmpPathFactory(shared_base),
    )

    repo_name = "repo-lock-check"
    lock_proxy = get_authorization(repo_name)
    assert lock_proxy is not None

    lock_file = shared_base.parent / f"{repo_name}.lock"
    assert not _can_acquire_lock_immediately(lock_file)

    lock_proxy.lock.release()
    assert _can_acquire_lock_immediately(lock_file)


def test_get_authorization_to_build_repo_cache_returns_none_without_xdist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Given no xdist worker env, when requesting a lock, then no lock is created."""
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    shared_base = tmp_path / "pytest-1" / "popen-gw0"
    shared_base.mkdir(parents=True)

    get_authorization = root_conftest.get_authorization_to_build_repo_cache.__wrapped__(
        tmp_path_factory=_DummyTmpPathFactory(shared_base),
    )

    assert get_authorization("repo-lock-check") is None
