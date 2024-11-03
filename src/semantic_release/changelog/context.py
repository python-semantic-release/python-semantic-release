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
            autofit_text_width,
        ),
    )


def read_file(filepath: str) -> str:
    try:
        if not filepath:
            raise FileNotFoundError("No file path provided")  # noqa: TRY301

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
        "raw-inline": (regexp(r"(?<=\s)(`[^`]+`)(?![`_])"), r"`\1`"),
    }

    for pattern, replacement in replacements.values():
        rst_content = pattern.sub(replacement, rst_content)

    return rst_content


def autofit_text_width(text: str, maxwidth: int = 100, indent_size: int = 0) -> str:
    """Format the description text to fit within a specified width"""
    input_text = text.strip()

    if len(input_text) <= maxwidth:
        # If the text is already within the maxwidth, return immediately
        return input_text

    indent = " " * indent_size
    formatted_description = []

    # Re-format text to fit within the maxwidth
    for paragraph in input_text.split("\n\n"):
        formatted_paragraph = []

        # Split the paragraph into words with no empty strings
        words = list(
            filter(
                None, paragraph.replace("\r", "").replace("\n", " ").strip().split(" ")
            )
        )

        # Initialize the line for each paragraph
        line = words[0]
        next_line = ""

        for word in words[1:]:
            # Check if the current line + the next word (and a space) will fit within the maxwidth
            # If it does, then update the current line
            next_line = f"{line} {word}"
            if len(next_line) <= maxwidth:
                line = next_line
                continue

            # Add the current line to the paragraph and start a new line
            formatted_paragraph.append(line)
            line = f"{indent}{word}"

        # Store the last line in the paragraph since it hasn't reached the maxwidth yet
        formatted_paragraph.append(line)

        #
        formatted_description.append(str.join("\n", formatted_paragraph))

    # Print the formatted description
    return str.join("\n\n", formatted_description).strip()
