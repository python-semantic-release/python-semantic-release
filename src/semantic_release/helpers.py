from __future__ import annotations

import importlib.util
import os
import re
import string
import sys
from functools import lru_cache, reduce, wraps
from pathlib import Path, PurePosixPath
from re import IGNORECASE, compile as regexp
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Sequence, TypeVar
from urllib.parse import urlsplit

from semantic_release.globals import logger

if TYPE_CHECKING:  # pragma: no cover
    from logging import Logger
    from re import Pattern
    from typing import Iterable


number_pattern = regexp(r"(?P<prefix>\S*?)(?P<number>\d[\d,]*)\b")
hex_number_pattern = regexp(
    r"(?P<prefix>\S*?)(?:0x)?(?P<number>[0-9a-f]+)\b", IGNORECASE
)


def get_number_from_str(
    string: str, default: int = -1, interpret_hex: bool = False
) -> int:
    if interpret_hex and (match := hex_number_pattern.search(string)):
        return abs(int(match.group("number"), 16))

    if match := number_pattern.search(string):
        return int(match.group("number"))

    return default


def sort_numerically(
    iterable: Iterable[str], reverse: bool = False, allow_hex: bool = False
) -> list[str]:
    # Alphabetically sort prefixes first, then sort by number
    alphabetized_list = sorted(iterable)

    # Extract prefixes in order to group items by prefix
    unmatched_items = []
    prefixes: dict[str, list[str]] = {}
    for item in alphabetized_list:
        if not (
            pattern_match := (
                (hex_number_pattern.search(item) if allow_hex else None)
                or number_pattern.search(item)
            )
        ):
            unmatched_items.append(item)
            continue

        prefix = prefix if (prefix := pattern_match.group("prefix")) else ""

        if prefix not in prefixes:
            prefixes[prefix] = []

        prefixes[prefix].append(item)

    # Sort prefixes and items by number mixing in unmatched items as alphabetized with other prefixes
    return reduce(
        lambda acc, next_item: acc + next_item,
        [
            (
                sorted(
                    prefixes[prefix],
                    key=lambda x: get_number_from_str(
                        x, default=-1, interpret_hex=allow_hex
                    ),
                    reverse=reverse,
                )
                if prefix in prefixes
                else [prefix]
            )
            for prefix in sorted([*prefixes.keys(), *unmatched_items])
        ],
        [],
    )


def text_reducer(text: str, filter_pair: tuple[Pattern[str], str]) -> str:
    """Reduce function to apply mulitple filters to a string"""
    if not text:  # abort if the paragraph is empty
        return text

    filter_pattern, replacement = filter_pair
    return filter_pattern.sub(replacement, text)


def validate_types_in_sequence(
    sequence: Sequence, types: type | tuple[type, ...]
) -> bool:
    """Validate that all elements in a sequence are of a specific type"""
    return all(isinstance(item, types) for item in sequence)


def format_arg(value: Any) -> str:
    """Helper to format an argument an argument for logging"""
    if type(value) == str:
        return f"'{value.strip()}'"
    return str(value)


def check_tag_format(tag_format: str) -> None:
    if "version" not in (f[1] for f in string.Formatter().parse(tag_format)):
        raise ValueError(
            f"Invalid tag_format {tag_format!r}, must use 'version' as a format key"
        )


_R = TypeVar("_R")
_FuncType = Callable[..., _R]


def logged_function(logger: Logger) -> Callable[[_FuncType[_R]], _FuncType[_R]]:
    """
    Decorator which adds debug logging of a function's input arguments and return
    value.

    The input arguments are logged before the function is called, and the
    return value is logged once it has completed.

    :param logger: Logger to send output to.
    """

    def _logged_function(func: _FuncType[_R]) -> _FuncType[_R]:
        @wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> _R:
            logger.debug(
                "%s(%s, %s)",
                func.__name__,
                ", ".join([format_arg(x) for x in args]),
                ", ".join([f"{k}={format_arg(v)}" for k, v in kwargs.items()]),
            )

            # Call function
            result = func(*args, **kwargs)

            # Log result
            logger.debug("%s -> %s", func.__qualname__, str(result))
            return result

        return _wrapper

    return _logged_function


@logged_function(logger)
def dynamic_import(import_path: str) -> Any:
    """
    Dynamically import an object from a conventionally formatted "module:attribute"
    string
    """
    if ":" not in import_path:
        raise ValueError(
            f"Invalid import path {import_path!r}, must use 'module:Class' format"
        )

    # Split the import path into module and attribute
    module_name, attr = import_path.split(":", maxsplit=1)

    # Check if the module is a file path, if it can be resolved and exists on disk then import as a file
    module_filepath = Path(module_name).resolve()
    if module_filepath.exists():
        module_path = (
            module_filepath.stem
            if Path(module_name).is_absolute()
            else str(Path(module_name).with_suffix("")).replace(os.sep, ".").lstrip(".")
        )

        if module_path not in sys.modules:
            logger.debug("Loading '%s' from file '%s'", module_path, module_filepath)
            spec = importlib.util.spec_from_file_location(
                module_path, str(module_filepath)
            )
            if spec is None:
                raise ImportError(f"Could not import {module_filepath}")

            module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            sys.modules.update({spec.name: module})
            spec.loader.exec_module(module)  # type: ignore[union-attr]

        return getattr(sys.modules[module_path], attr)

    # Otherwise, import as a module
    try:
        logger.debug("Importing module '%s'", module_name)
        module = importlib.import_module(module_name)
        logger.debug("Loading '%s' from module '%s'", attr, module_name)
        return getattr(module, attr)
    except TypeError as err:
        raise ImportError(
            str.join(
                "\n",
                [
                    str(err.args[0]),
                    "Verify the import format matches 'module:attribute' or 'path/to/module:attribute'",
                ],
            )
        ) from err


class ParsedGitUrl(NamedTuple):
    """Container for the elements parsed from a git URL"""

    scheme: str
    netloc: str
    namespace: str
    repo_name: str


@lru_cache(maxsize=512)
def parse_git_url(url: str) -> ParsedGitUrl:
    """
    Attempt to parse a string as a git url http[s]://, git://, file://, or ssh format, into a
    ParsedGitUrl.

    supported examples:
        http://git.mycompany.com/username/myproject.git
        https://github.com/username/myproject.git
        https://gitlab.com/group/subgroup/myproject.git
        https://git.mycompany.com:4443/username/myproject.git
        git://host.xz/path/to/repo.git/
        git://host.xz:9418/path/to/repo.git/
        git@github.com:username/myproject.git                  <-- assumes ssh://
        ssh://git@github.com:3759/myproject.git                <-- non-standard, but assume user 3759
        ssh://git@github.com:username/myproject.git
        ssh://git@bitbucket.org:7999/username/myproject.git
        git+ssh://git@github.com:username/myproject.git
        /Users/username/dev/remote/myproject.git               <-- Posix File paths
        file:///Users/username/dev/remote/myproject.git
        C:/Users/username/dev/remote/myproject.git             <-- Windows File paths
        file:///C:/Users/username/dev/remote/myproject.git

    REFERENCE: https://stackoverflow.com/questions/31801271/what-are-the-supported-git-url-formats

    Raises ValueError if the url can't be parsed.
    """
    logger.debug("Parsing git url %r", url)

    # Normalizers are a list of tuples of (pattern, replacement)
    normalizers = [
        # normalize implicit ssh urls to explicit ssh://
        (r"^([\w._-]+@)", r"ssh://\1"),
        # normalize git+ssh:// urls to ssh://
        (r"^git\+ssh://", "ssh://"),
        # normalize an scp like syntax to URL compatible syntax
        # excluding port definitions (:#####) & including numeric usernames
        (r"(ssh://(?:[\w._-]+@)?[\w.-]+):(?!\d{1,5}/\w+/)(.*)$", r"\1/\2"),
        # normalize implicit file (windows || posix) urls to explicit file:// urls
        (r"^([C-Z]:/)|^/(\w)", r"file:///\1\2"),
    ]

    for pattern, replacement in normalizers:
        url = re.compile(pattern).sub(replacement, url)

    # run the url through urlsplit to separate out the parts
    urllib_split = urlsplit(url)

    # Fail if url scheme not found
    if not urllib_split.scheme:
        raise ValueError(f"Cannot parse {url!r}")

    # We have been able to parse the url with urlsplit,
    # so it's a (file|git|ssh|https?)://... structure
    # but we aren't validating the protocol scheme as its not our business

    # use PosixPath to normalize the path & then separate out the namespace & repo_name
    namespace, _, name = (
        str(PurePosixPath(urllib_split.path)).lstrip("/").rpartition("/")
    )

    # strip out the .git at the end of the repo_name if present
    name = name[:-4] if name.endswith(".git") else name

    # check that we have all the required parts of the url
    required_parts = [
        urllib_split.scheme,
        # Allow empty net location for file:// urls
        True if urllib_split.scheme == "file" else urllib_split.netloc,
        namespace,
        name,
    ]

    if not all(required_parts):
        raise ValueError(f"Bad url: {url!r}")

    return ParsedGitUrl(
        scheme=urllib_split.scheme,
        netloc=urllib_split.netloc,
        namespace=namespace,
        repo_name=name,
    )
