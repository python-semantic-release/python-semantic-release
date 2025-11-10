"""Note: fixtures are stored in the tests/fixtures directory for better organization"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from hashlib import md5
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, cast
from unittest import mock

import pytest
from click.testing import CliRunner
from filelock import FileLock
from git import Commit, Repo

from semantic_release.version.version import Version

from tests.const import PROJ_DIR
from tests.fixtures import *
from tests.util import copy_dir_tree, remove_dir_tree

if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper
    from typing import Any, Callable, Generator, Optional, Protocol, Sequence, TypedDict

    from click.testing import Result
    from filelock import AcquireReturnProxy
    from git import Actor

    from tests.fixtures.git_repo import RepoActions

    class RunCliFn(Protocol):
        """
        Run the CLI with the provided arguments and a clean environment.

        :param argv: The arguments to pass to the CLI.
        :type argv: list[str] | None

        :param env: The environment variables to set for the CLI.
        :type env: dict[str, str] | None

        :param invoke_kwargs: Additional arguments to pass to the invoke method.
        :type invoke_kwargs: dict[str, Any] | None

        :return: The result of the CLI invocation.
        :rtype: Result
        """

        def __call__(
            self,
            argv: list[str] | None = None,
            env: dict[str, str] | None = None,
            invoke_kwargs: dict[str, Any] | None = None,
        ) -> Result: ...

    class MakeCommitObjFn(Protocol):
        def __call__(self, message: str) -> Commit: ...

    class NetrcFileFn(Protocol):
        def __call__(self, machine: str) -> _TemporaryFileWrapper[str]: ...

    class TeardownCachedDirFn(Protocol):
        def __call__(self, directory: Path) -> Path: ...

    class FormatDateStrFn(Protocol):
        def __call__(self, date: datetime) -> str: ...

    class GetStableDateNowFn(Protocol):
        def __call__(self) -> datetime: ...

    class GetMd5ForFileFn(Protocol):
        def __call__(self, file_path: Path | str) -> str: ...

    class GetMd5ForSetOfFilesFn(Protocol):
        """
        Generates a hash for a set of files based on their contents

        This function will automatically filter out any 0-byte files or `__init__.py` files

        :param: files: A list of file paths to generate a hash for (MUST BE absolute paths)
        """

        def __call__(self, files: Sequence[Path | str]) -> str: ...

    class GetAuthorizationToBuildRepoCacheFn(Protocol):
        def __call__(self, repo_name: str) -> AcquireReturnProxy | None: ...

    class BuildRepoOrCopyCacheFn(Protocol):
        def __call__(
            self,
            repo_name: str,
            build_spec_hash: str,
            build_repo_func: Callable[[Path], Sequence[RepoActions]],
            dest_dir: Path | None = None,
        ) -> Path: ...

    class RepoData(TypedDict):
        build_date: str
        build_spec_hash: str
        build_definition: Sequence[RepoActions]

    class GetCachedRepoDataFn(Protocol):
        def __call__(self, proj_dirname: str) -> RepoData | None: ...

    class SetCachedRepoDataFn(Protocol):
        def __call__(self, proj_dirname: str, data: RepoData) -> None: ...


def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager):
    parser.addoption(
        "--comprehensive",
        help="Run full test suite including slow tests",
        default=False,
        action="store_true",
    )


def pytest_configure(config: pytest.Config):
    """
    If no test selection modifications are provided, default to running only unit tests.

    See `pytest_collection_modifyitems` for more information on test selection modifications.
    """
    user_desired_comprehensive_evaluation = config.getoption("--comprehensive")
    user_provided_filter = str(config.getoption("-k"))
    user_provided_markers = str(config.getoption("-m"))

    root_test_dir = Path(__file__).parent.relative_to(config.rootpath)
    user_provided_test_path = bool(config.args != [str(root_test_dir)])

    # If no options are provided, default to running only unit tests
    if not any(
        (
            user_desired_comprehensive_evaluation,
            user_provided_test_path,
            user_provided_filter,
            user_provided_markers,
        )
    ):
        config.option.markexpr = pytest.mark.unit.name


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    """
    Test selection modifier based on markers and command line options.

    Examples
    --------
        pytest
            only unit tests that are not marked comprehensive are executed

        pytest --comprehensive
            all tests are executed

        pytest -m unit
            only unit tests that are not marked comprehensive are executed (same as no options)

        pytest -m e2e
            only end-to-end tests that are not marked comprehensive are executed

        pytest -m e2e --comprehensive
            all end-to-end tests are executed

        pytest -m "not unit"
            only tests that are not marked unit or comprehensive are executed

        pytest -m "not unit" --comprehensive
            all tests that are not marked unit are executed

        pytest -k "test_name"
            only tests that match the substring "test_name" (but not marked comprehensive) are executed

        pytest -k "test_name" --comprehensive
            all tests that match the substring "test_name" are executed

    """
    disable_comprehensive_tests = not config.getoption("--comprehensive")
    comprehensive_test_skip_marker = pytest.mark.skip(
        reason="comprehensive tests are disabled by default"
    )
    user_provided_filter = str(config.getoption("-k"))

    if any((disable_comprehensive_tests,)):
        for item in items:
            if user_provided_filter and user_provided_filter in item.name:
                continue
            if disable_comprehensive_tests and "comprehensive" in item.keywords:
                item.add_marker(comprehensive_test_skip_marker)


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture(scope="session")
def run_cli(clean_os_environment: dict[str, str]) -> RunCliFn:
    def _run_cli(
        argv: list[str] | None = None,
        env: dict[str, str] | None = None,
        invoke_kwargs: dict[str, Any] | None = None,
    ) -> Result:
        from semantic_release.cli.commands.main import main
        from semantic_release.globals import logger

        # Prevent logs from being propagated to the root logger (pytest)
        logger.propagate = False

        cli_runner = CliRunner(mix_stderr=False)
        env_vars = {**clean_os_environment, **(env or {})}
        args = ["-vv", *(argv or [])]

        with mock.patch.dict(os.environ, env_vars, clear=True):
            # run the CLI with the provided arguments
            result = cli_runner.invoke(main, args=args, **(invoke_kwargs or {}))
            # Force the output to be printed to stdout which will be captured by pytest
            sys.stdout.write(result.stdout)
            sys.stderr.write(result.stderr)
            return result

    return _run_cli


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
def stable_today_date() -> datetime:
    curr_time = datetime.now(timezone.utc).astimezone()
    est_test_completion = curr_time + timedelta(hours=1)  # exaggeration
    starting_day_of_year = curr_time.timetuple().tm_yday
    ending_day_of_year = est_test_completion.timetuple().tm_yday

    if starting_day_of_year < ending_day_of_year:
        return est_test_completion

    return curr_time


@pytest.fixture(scope="session")
def stable_now_date(stable_today_date: datetime) -> GetStableDateNowFn:
    def _stable_now_date() -> datetime:
        curr_time = datetime.now(timezone.utc).astimezone()
        return stable_today_date.replace(
            minute=curr_time.minute,
            second=curr_time.second,
            microsecond=curr_time.microsecond,
        )

    return _stable_now_date


@pytest.fixture(scope="session")
def format_date_str() -> FormatDateStrFn:
    """Formats a date as how it would appear in the changelog (Must match local timezone)"""

    def _format_date_str(date: datetime) -> str:
        return date.strftime("%Y-%m-%d")

    return _format_date_str


@pytest.fixture(scope="session")
def today_date_str(
    stable_today_date: datetime, format_date_str: FormatDateStrFn
) -> str:
    """Today's Date formatted as how it would appear in the changelog (matches local timezone)"""
    return format_date_str(stable_today_date)


@pytest.fixture(scope="session")
def cached_files_dir(request: pytest.FixtureRequest) -> Path:
    return request.config.cache.mkdir("psr-cached-repos")


@pytest.fixture(scope="session")
def get_authorization_to_build_repo_cache(
    tmp_path_factory: pytest.TempPathFactory, worker_id: str
) -> GetAuthorizationToBuildRepoCacheFn:
    def _get_authorization_to_build_repo_cache(
        repo_name: str,
    ) -> AcquireReturnProxy | None:
        if worker_id == "master":
            # not executing with multiple workers via xdist, so just continue
            return None

        # get the temp directory shared by all workers
        root_tmp_dir = tmp_path_factory.getbasetemp().parent

        return FileLock(root_tmp_dir / f"{repo_name}.lock").acquire(
            timeout=30, blocking=True
        )

    return _get_authorization_to_build_repo_cache


@pytest.fixture(scope="session")
def get_cached_repo_data(request: pytest.FixtureRequest) -> GetCachedRepoDataFn:
    def _get_cached_repo_data(proj_dirname: str) -> RepoData | None:
        cache_key = f"psr/repos/{proj_dirname}"
        return cast("Optional[RepoData]", request.config.cache.get(cache_key, None))

    return _get_cached_repo_data


@pytest.fixture(scope="session")
def set_cached_repo_data(request: pytest.FixtureRequest) -> SetCachedRepoDataFn:
    def magic_serializer(obj: Any) -> Any:
        if isinstance(obj, Path):
            return obj.__fspath__()

        if isinstance(obj, Version):
            return obj.__dict__

        return obj

    def _set_cached_repo_data(proj_dirname: str, data: RepoData) -> None:
        cache_key = f"psr/repos/{proj_dirname}"
        request.config.cache.set(
            cache_key,
            json.loads(json.dumps(data, default=magic_serializer)),
        )

    return _set_cached_repo_data


@pytest.fixture(scope="session")
def build_repo_or_copy_cache(
    cached_files_dir: Path,
    today_date_str: str,
    stable_now_date: GetStableDateNowFn,
    get_cached_repo_data: GetCachedRepoDataFn,
    set_cached_repo_data: SetCachedRepoDataFn,
    get_authorization_to_build_repo_cache: GetAuthorizationToBuildRepoCacheFn,
) -> BuildRepoOrCopyCacheFn:
    log_file = cached_files_dir.joinpath("repo-build.log")
    log_file_lock = FileLock(log_file.with_suffix(f"{log_file.suffix}.lock"), timeout=2)

    def _build_repo_w_cache_checking(
        repo_name: str,
        build_spec_hash: str,
        build_repo_func: Callable[[Path], Sequence[RepoActions]],
        dest_dir: Path | None = None,
    ) -> Path:
        # Blocking mechanism to synchronize xdist workers
        # Runs before the cache is checked because the cache will be set once the build is complete
        filelock = get_authorization_to_build_repo_cache(repo_name)

        cached_repo_data = get_cached_repo_data(repo_name)
        cached_repo_path = cached_files_dir.joinpath(repo_name)

        # Determine if the build spec has changed since the last cached build
        unmodified_build_spec = bool(
            cached_repo_data and cached_repo_data["build_spec_hash"] == build_spec_hash
        )

        if not unmodified_build_spec or not cached_repo_path.exists():
            # Cache miss, so build the repo (make sure its clean first)
            remove_dir_tree(cached_repo_path, force=True)
            cached_repo_path.mkdir(parents=True, exist_ok=True)

            build_msg = f"Building cached project files for {repo_name}"
            with log_file_lock, log_file.open(mode="a") as afd:
                afd.write(f"{stable_now_date().isoformat()}: {build_msg}...\n")

            try:
                # Try to build repository but catch any errors so that it doesn't cascade through all tests
                # do to an unreleased lock
                build_definition = build_repo_func(cached_repo_path)
            except Exception:
                remove_dir_tree(cached_repo_path, force=True)

                if filelock:
                    filelock.lock.release()

                with log_file_lock, log_file.open(mode="a") as afd:
                    afd.write(
                        f"{stable_now_date().isoformat()}: {build_msg}...FAILED\n"
                    )

                raise

            # Marks the date when the cached repo was created
            set_cached_repo_data(
                repo_name,
                {
                    "build_date": today_date_str,
                    "build_spec_hash": build_spec_hash,
                    "build_definition": build_definition,
                },
            )

            with log_file_lock, log_file.open(mode="a") as afd:
                afd.write(f"{stable_now_date().isoformat()}: {build_msg}...DONE\n")

        if filelock:
            filelock.lock.release()

        if dest_dir:
            copy_dir_tree(cached_repo_path, dest_dir)
            return dest_dir

        return cached_repo_path

    return _build_repo_w_cache_checking


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
def make_commit_obj(
    commit_author: Actor, stable_now_date: GetStableDateNowFn
) -> MakeCommitObjFn:
    def _make_commit(message: str) -> Commit:
        commit_timestamp = round(stable_now_date().timestamp())
        return Commit(
            repo=Repo(),
            binsha=Commit.NULL_BIN_SHA,
            message=message,
            author=commit_author,
            authored_date=commit_timestamp,
            committer=commit_author,
            committed_date=commit_timestamp,
            parents=[],
        )

    return _make_commit


@pytest.fixture(scope="session")
def get_md5_for_file() -> GetMd5ForFileFn:
    in_memory_cache = {}

    def _get_md5_for_file(file_path: Path | str) -> str:
        file_path = Path(file_path)
        rel_file_path = str(file_path.relative_to(PROJ_DIR))

        if rel_file_path not in in_memory_cache:
            in_memory_cache[rel_file_path] = md5(  # noqa: S324, not using hash for security
                file_path.read_bytes()
            ).hexdigest()

        return in_memory_cache[rel_file_path]

    return _get_md5_for_file


@pytest.fixture(scope="session")
def get_md5_for_set_of_files(
    get_md5_for_file: GetMd5ForFileFn,
) -> GetMd5ForSetOfFilesFn:
    in_memory_cache = {}

    def _get_md5_for_set_of_files(files: Sequence[Path | str]) -> str:
        # cast to a filtered and unique set of Path objects
        file_dependencies = sorted(
            set(
                filter(
                    lambda file_path: file_path.name != "__init__.py"
                    and file_path.stat().st_size > 0,
                    (Path(f).absolute().resolve() for f in files),
                )
            )
        )

        # create a hashable key of all dependencies to store the combined files hash
        cache_key = tuple(
            [str(file.relative_to(PROJ_DIR)) for file in file_dependencies]
        )

        # check if we have done this before
        if cache_key not in in_memory_cache:
            # since we haven't done this before, generate the hash for each file
            file_hashes = [get_md5_for_file(file) for file in file_dependencies]

            # combine the hashes into a string and then hash the result and store it
            in_memory_cache[cache_key] = md5(  # noqa: S324, not using hash for security
                str.join("\n", file_hashes).encode()
            ).hexdigest()

        # return the stored calculated hash for the set
        return in_memory_cache[cache_key]

    return _get_md5_for_set_of_files


@pytest.fixture(scope="session")
def clean_os_environment() -> dict[str, str]:
    return dict(
        filter(
            lambda k_v: k_v[1] is not None,  # type: ignore[arg-type]
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
