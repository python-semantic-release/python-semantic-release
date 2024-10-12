from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from re import compile as regexp
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
        filters=(
            *hvcs_client.get_changelog_context_filters(),
            read_file,
            convert_md_to_rst,
        ),
    )


def read_file(filepath: str) -> str:
    try:
        with Path(filepath).open(newline=os.linesep) as rfd:
            return rfd.read()
    except FileNotFoundError as err:
        logging.warning(err)
        return ""


def convert_md_to_rst(md_content: str) -> str:
    rst_content = md_content
    replacements = {
        # Replace markdown doubleunder bold with rst bold
        "bold-inline": (regexp(r"(?<=\s)__(.+?)__(?=\s|$)"), r"**\1**"),
        # Replace markdown italics with rst italics
        "italic-inline": (regexp(r"(?<=\s)_([^_].+?[^_])_(?=\s|$)"), r"*\1*"),
        # Replace markdown bullets with rst bullets
        "bullets": (regexp(r"^(\s*)-(\s)"), r"\1*\2"),
        # Replace markdown inline raw content with rst inline raw content
        "raw-inline": (regexp(r"(?<=\s)(`[^`]+`)(?![`_])(?=\s|$)"), r"`\1`"),
    }

    for pattern, replacement in replacements.values():
        rst_content = pattern.sub(replacement, rst_content)

    return rst_content
