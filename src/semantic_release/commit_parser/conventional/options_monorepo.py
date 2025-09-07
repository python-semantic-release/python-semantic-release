from __future__ import annotations

from pathlib import Path
from re import compile as regexp, error as RegExpError  # noqa: N812
from typing import TYPE_CHECKING, Any, Iterable, Tuple

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
from typing_extensions import Annotated

from semantic_release.commit_parser.conventional.options import (
    ConventionalCommitParserOptions,
)

if TYPE_CHECKING:  # pragma: no cover
    pass


@dataclass
class ConventionalCommitMonorepoParserOptions(ConventionalCommitParserOptions):
    # TODO: add example into the docstring
    """Options dataclass for ConventionalCommitMonorepoParser."""

    path_filters: Annotated[Tuple[str, ...], Field(validate_default=True)] = (".",)
    """
    A set of relative paths to filter commits by. Only commits with file changes that
    match these file paths or its subdirectories will be considered valid commits.

    Syntax is similar to .gitignore with file path globs and inverse file match globs
    via `!` prefix. Paths should be relative to the current working directory.
    """

    scope_prefix: str = ""
    """
    A prefix that will be striped from the scope when parsing commit messages.

    If set, it will cause unscoped commits to be ignored. Use this in tandem with
    the `path_filters` option to filter commits by directory and scope. This will
    be fed into a regular expression so you must escape any special characters that
    are meaningful in regular expressions (e.g. `.`, `*`, `?`, `+`, etc.) if you want
    to match them literally.
    """

    @classmethod
    @field_validator("path_filters", mode="before")
    def convert_strs_to_paths(cls, value: Any) -> tuple[Path, ...]:
        values = value if isinstance(value, Iterable) else [value]
        results: list[Path] = []

        for val in values:
            if isinstance(val, (str, Path)):
                results.append(Path(val))
                continue

            raise TypeError(f"Invalid type: {type(val)}, expected str or Path.")

        return tuple(results)

    @classmethod
    @field_validator("path_filters", mode="after")
    def resolve_path(cls, dir_paths: tuple[Path, ...]) -> tuple[Path, ...]:
        return tuple(
            (
                Path(f"!{Path(str_path[1:]).expanduser().absolute().resolve()}")
                # maintains the negation prefix if it exists
                if (str_path := str(path)).startswith("!")
                # otherwise, resolve the path normally
                else path.expanduser().absolute().resolve()
            )
            for path in dir_paths
        )

    @classmethod
    @field_validator("scope_prefix", mode="after")
    def validate_scope_prefix(cls, scope_prefix: str) -> str:
        if not scope_prefix:
            return ""

        # Allow the special case of a plain wildcard although it's not a valid regex
        if scope_prefix == "*":
            return ".*"

        try:
            regexp(scope_prefix)
        except RegExpError as err:
            raise ValueError(f"Invalid regex {scope_prefix!r}") from err

        return scope_prefix
