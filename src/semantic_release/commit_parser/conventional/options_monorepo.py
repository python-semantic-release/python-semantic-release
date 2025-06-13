from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
from typing_extensions import Annotated

from .options import ConventionalCommitParserOptions

if TYPE_CHECKING:  # pragma: no cover
    pass


@dataclass
class ConventionalMonorepoParserOptions(ConventionalCommitParserOptions):
    """Options dataclass for ConventionalCommitMonorepoParser."""

    path_filters: Annotated[tuple[Path, ...], Field(validate_default=True)] = (
        Path("."),
    )
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
    the `path_filters` option to filter commits by directory and scope.
    """

    @field_validator("path_filters", mode="before")
    @classmethod
    def convert_strs_to_paths(cls, value: Any) -> tuple[Path]:
        values = value if isinstance(value, Iterable) else [value]
        results = []

        for val in values:
            if isinstance(val, (str, Path)):
                results.append(Path(val))
                continue

            raise TypeError(f"Invalid type: {type(val)}, expected str or Path.")

        return tuple(results)

    @field_validator("path_filters", mode="after")
    @classmethod
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
