from __future__ import annotations

import importlib.util
import os
import secrets
import shutil
import stat
import string
from contextlib import contextmanager, suppress
from pathlib import Path
from re import compile as regexp
from textwrap import indent
from typing import TYPE_CHECKING, Tuple

from git import Git, Repo
from pydantic.dataclasses import dataclass

from semantic_release.changelog.context import ChangelogMode, make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.conventional import ConventionalCommitParser
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.enums import LevelBump

from tests.const import SUCCESS_EXIT_CODE

if TYPE_CHECKING:
    import filecmp
    from typing import Any, Callable, Generator, Iterable, TypeVar

    try:
        # Python 3.8 and 3.9 compatibility
        from typing_extensions import TypeAlias
    except ImportError:
        from typing import TypeAlias  # type: ignore[attr-defined, no-redef]

    from unittest.mock import MagicMock

    from click.testing import Result as ClickInvokeResult
    from git import Commit

    from semantic_release.cli.config import RuntimeContext

    _R = TypeVar("_R")

    GitCommandWrapperType: TypeAlias = Git


def get_func_qual_name(func: Callable) -> str:
    return str.join(".", filter(None, [func.__module__, func.__qualname__]))


def assert_exit_code(
    exit_code: int, result: ClickInvokeResult, cli_cmd: list[str]
) -> bool:
    if result.exit_code == exit_code:
        return True

    raise AssertionError(
        str.join(
            os.linesep,
            [
                f"{result.exit_code} != {exit_code} (actual != expected)",
                "",
                # Explain what command failed
                "Unexpected exit code from command:",
                indent(f"'{str.join(' ', cli_cmd)}'", " " * 2),
            ],
        )
    )


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
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
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
    """Makes a deterministic file change for testing"""
    tgt_file = Path(filename).resolve().absolute()

    # TODO: switch to Path.is_relative_to() when 3.8 support is deprecated
    # if not tgt_file.is_relative_to(Path(repo.working_dir).resolve().absolute()):
    if Path(repo.working_dir).resolve().absolute() not in tgt_file.parents:
        raise ValueError(
            f"File {tgt_file} is not relative to the repository working directory {repo.working_dir}"
        )

    tgt_file.parent.mkdir(parents=True, exist_ok=True)
    file_contents = tgt_file.read_text() if tgt_file.exists() else ""
    line_number = len(file_contents.splitlines())

    file_contents += f"{line_number}  {text or 'default text'}{os.linesep}"
    tgt_file.write_text(file_contents, encoding="utf-8")

    repo.index.add(tgt_file)


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
    single_line_var_pattern = regexp(r"^(?P<name>\w+)=(?P<value>.*?)\r?$")
    multiline_var_pattern = regexp(r"^(?P<name>\w+?)<<EOF\r?$")
    multiline_var_pattern_end = regexp(r"^EOF\r?$")

    found_multiline_var = False
    current_var_name = ""
    current_var_value = ""
    result: dict[str, str] = {}
    for line in output.splitlines(keepends=True):
        if found_multiline_var:
            if match := multiline_var_pattern_end.match(line):
                # End of a multiline variable
                found_multiline_var = False
                result[current_var_name] = current_var_value
                continue

            current_var_value += line
            continue

        if match := single_line_var_pattern.match(line):
            # Single line variable
            result[match.group("name")] = match.group("value")
            continue

        if match := multiline_var_pattern.match(line):
            # Start of a multiline variable
            found_multiline_var = True
            current_var_name = match.group("name")
            current_var_value = ""
            continue

    return result


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
        mask_initial_release=runtime_context.changelog_mask_initial_release,
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

    class MockGitCommandWrapperType(Git):
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


class CustomConventionalParserWithIgnorePatterns(ConventionalCommitParser):
    def parse(self, commit: Commit) -> ParsedCommit | ParseError:
        if not (parse_msg_result := super().parse_message(str(commit.message))):
            return ParseError(commit, "Unable to parse commit")

        return ParsedCommit.from_parsed_message_result(
            commit,
            ParsedMessageResult(
                **{
                    **parse_msg_result._asdict(),
                    "include_in_changelog": bool(
                        not str(commit.message).startswith("chore")
                    ),
                }
            ),
        )
