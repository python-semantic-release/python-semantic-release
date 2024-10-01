from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal

if TYPE_CHECKING:
    from jinja2 import Environment

    from semantic_release.changelog.release_history import Release, ReleaseHistory
    from semantic_release.hvcs._base import HvcsBase
    from semantic_release.version.version import Version


@dataclass
class ReleaseNotesContext:
    repo_name: str
    repo_owner: str
    hvcs_type: str
    version: Version
    release: Release
    filters: tuple[Callable[..., Any], ...] = ()

    def bind_to_environment(self, env: Environment) -> Environment:
        env_globals = dict(
            filter(lambda k_v: k_v[0] != "filters", self.__dict__.items())
        )

        for g, v in env_globals.items():
            env.globals[g] = v

        for f in self.filters:
            env.filters[f.__name__] = f

        return env


class ChangelogMode(Enum):
    INIT = "init"
    UPDATE = "update"


@dataclass
class ChangelogContext:
    repo_name: str
    repo_owner: str
    hvcs_type: str
    history: ReleaseHistory
    changelog_mode: Literal["update", "init"]
    prev_changelog_file: str
    changelog_insertion_flag: str
    filters: tuple[Callable[..., Any], ...] = ()

    def bind_to_environment(self, env: Environment) -> Environment:
        env.globals["context"] = self
        env.globals["ctx"] = self
        for f in self.filters:
            env.filters[f.__name__] = f
        return env


def make_changelog_context(
    hvcs_client: HvcsBase,
    release_history: ReleaseHistory,
    mode: ChangelogMode,
    prev_changelog_file: Path,
    insertion_flag: str,
) -> ChangelogContext:
    return ChangelogContext(
        repo_name=hvcs_client.repo_name,
        repo_owner=hvcs_client.owner,
        history=release_history,
        changelog_mode=mode.value,
        changelog_insertion_flag=insertion_flag,
        prev_changelog_file=str(prev_changelog_file),
        hvcs_type=hvcs_client.__class__.__name__.lower(),
        filters=(*hvcs_client.get_changelog_context_filters(), read_file),
    )


def read_file(filepath: str) -> str:
    try:
        return Path(filepath).read_text()
    except FileNotFoundError as err:
        logging.warning(err)
        return ""
