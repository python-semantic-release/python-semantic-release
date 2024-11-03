from __future__ import annotations

import importlib.util
import os
import secrets
import shutil
import stat
import string
from contextlib import contextmanager, suppress
from pathlib import Path
from textwrap import indent
from typing import TYPE_CHECKING, Tuple

from git import Repo
from pydantic.dataclasses import dataclass

from semantic_release.changelog.context import ChangelogMode, make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.cli import config as cli_config_module
from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import ParsedCommit, ParseResult
from semantic_release.enums import LevelBump

from tests.const import SUCCESS_EXIT_CODE

if TYPE_CHECKING:
    import filecmp
    from typing import Any, Callable, Generator, Iterable, TypeVar

    try:
        from typing import TypeAlias
    except ImportError:
        # for python 3.8 and 3.9
        from typing_extensions import TypeAlias

    from unittest.mock import MagicMock

    from click.testing import Result as ClickInvokeResult
    from git import Commit

    from semantic_release.cli.config import RuntimeContext
    from semantic_release.commit_parser.token import ParseError

    _R = TypeVar("_R")

    GitCommandWrapperType: TypeAlias = cli_config_module.Repo.GitCommandWrapperType


def get_func_qual_name(func: Callable) -> str:
    return f"{func.__module__}.{func.__qualname__}"


def assert_exit_code(
    exit_code: int, result: ClickInvokeResult, cli_cmd: list[str]
) -> bool:
    if result.exit_code != exit_code:
        raise AssertionError(
            str.join(
                os.linesep,
                [
                    f"{result.exit_code} != {exit_code} (actual != expected)",
                    "",
                    # Explain what command failed
                    "Unexpected exit code from command:",
                    # f"  '{str.join(' ', cli_cmd)}'",
                    indent(f"'{str.join(' ', cli_cmd)}'", " " * 2),
                    "",
                    # Add indentation to each line for stdout & stderr
                    "stdout:",
                    indent(result.stdout, " " * 2),
                    "stderr:",
                    indent(result.stderr, " " * 2),
                ],
            )
        )
    return True


def assert_successful_exit_code(result: ClickInvokeResult, cli_cmd: list[str]) -> bool:
    return assert_exit_code(SUCCESS_EXIT_CODE, result, cli_cmd)


def get_full_qualname(callable_obj: Callable) -> str:
    parts = filter(
        None,
        [
            callable_obj.__module__,
            (
                None
                if callable_obj.__class__.__name__ == "function"
                else callable_obj.__class__.__name__
            ),
            callable_obj.__name__,
        ],
    )
    return str.join(".", parts)


def copy_dir_tree(src_dir: Path | str, dst_dir: Path | str) -> None:
    """Compatibility wrapper for shutil.copytree"""
    # python3.8+
    shutil.copytree(
        src=str(src_dir),
        dst=str(dst_dir),
        dirs_exist_ok=True,
    )


def remove_dir_tree(directory: Path | str = ".", force: bool = False) -> None:
    """
    Compatibility wrapper for shutil.rmtree

    Helpful for deleting directories with .git/* files, which usually have some
    read-only permissions
    """

    def on_read_only_error(_func, path, _exc_info):
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)

    # Prevent error if already deleted or never existed, that is our desired state
    with suppress(FileNotFoundError):
        shutil.rmtree(str(directory), onerror=on_read_only_error if force else None)


def dynamic_python_import(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module


@contextmanager
def temporary_working_directory(directory: Path | str) -> Generator[None, None, None]:
    cwd = os.getcwd()
    os.chdir(str(directory))
    try:
        yield
    finally:
        os.chdir(cwd)


def shortuid(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits

    return "".join(secrets.choice(alphabet) for _ in range(length))


def add_text_to_file(repo: Repo, filename: str, text: str | None = None):
    with open(f"{repo.working_tree_dir}/{filename}", "a+") as f:
        f.write(text or f"default text {shortuid(12)}")
        f.write(os.linesep)

    repo.index.add(filename)


def flatten_dircmp(dcmp: filecmp.dircmp) -> list[str]:
    return (
        dcmp.diff_files
        + dcmp.left_only
        + dcmp.right_only
        + [
            os.sep.join((directory, file))
            for directory, cmp in dcmp.subdirs.items()
            for file in flatten_dircmp(cmp)
        ]
    )


def xdist_sort_hack(it: Iterable[_R]) -> Iterable[_R]:
    """
    hack for pytest-xdist

    https://pytest-xdist.readthedocs.io/en/latest/known-limitations.html#workarounds

    taking an iterable of params for a pytest.mark.parametrize decorator, this
    ensures a deterministic sort so that xdist can always work

    Being able to use `pytest -nauto` is a huge speedup on testing
    """
    return dict(enumerate(it)).values()


def actions_output_to_dict(output: str) -> dict[str, str]:
    return {line.split("=")[0]: line.split("=")[1] for line in output.splitlines()}


def get_release_history_from_context(runtime_context: RuntimeContext) -> ReleaseHistory:
    with Repo(str(runtime_context.repo_dir)) as git_repo:
        release_history = ReleaseHistory.from_git_history(
            git_repo,
            runtime_context.version_translator,
            runtime_context.commit_parser,
            runtime_context.changelog_excluded_commit_patterns,
        )
    changelog_context = make_changelog_context(
        hvcs_client=runtime_context.hvcs_client,
        release_history=release_history,
        mode=ChangelogMode.INIT,
        prev_changelog_file=Path("CHANGELOG.md"),
        insertion_flag="",
    )
    changelog_context.bind_to_environment(runtime_context.template_environment)
    return release_history


def prepare_mocked_git_command_wrapper_type(
    **mocked_methods: MagicMock,
) -> type[GitCommandWrapperType]:
    """
    Mock the specified methods of `Repo.GitCommandWrapperType` (`git.Git` by default).

    Initialized `MagicMock` objects are passed as keyword arguments, where the argument
    name is the name of the method to mock.

    For example, the following invocation mocks the `Repo.git.push()` command / method.

    Arrange:
    >>> from unittest.mock import MagicMock
    >>> from git import Repo

    >>> mocked_push = MagicMock()
    >>> cls = prepare_mocked_git_command_wrapper_type(push=mocked_push)
    >>> Repo.GitCommandWrapperType = cls
    >>> repo = Repo(".")

    Act:
    >>> repo.git.push("origin", "master")
    <MagicMock name='mock()' id='...'>

    Assert:
    >>> mocked_push.assert_called_once()
    """

    class MockGitCommandWrapperType(cli_config_module.Repo.GitCommandWrapperType):
        def __getattr__(self, name: str) -> Any:
            try:
                return object.__getattribute__(self, f"mocked_{name}")
            except AttributeError:
                return super().__getattr__(name)

    for name, method in mocked_methods.items():
        setattr(MockGitCommandWrapperType, f"mocked_{name}", method)
    return MockGitCommandWrapperType


class CustomParserWithNoOpts(CommitParser[ParseResult, ParserOptions]):
    def parse(self, commit: Commit) -> ParsedCommit | ParseError:
        return ParsedCommit(
            bump=LevelBump.NO_RELEASE,
            type="",
            scope="",
            descriptions=[],
            breaking_descriptions=[],
            commit=commit,
        )


@dataclass
class CustomParserOpts(ParserOptions):
    allowed_tags: Tuple[str, ...] = ("new", "custom")  # noqa: UP006


class CustomParserWithOpts(CommitParser[ParseResult, CustomParserOpts]):
    parser_options = CustomParserOpts

    def parse(self, commit: Commit) -> ParsedCommit | ParseError:
        return ParsedCommit(
            bump=LevelBump.NO_RELEASE,
            type="custom",
            scope="",
            descriptions=[],
            breaking_descriptions=[],
            commit=commit,
        )


class IncompleteCustomParser(CommitParser):
    pass
