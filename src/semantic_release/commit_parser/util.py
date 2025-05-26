from __future__ import annotations

from contextlib import suppress
from copy import deepcopy
from functools import reduce
from re import MULTILINE, compile as regexp
from typing import TYPE_CHECKING

# TODO: remove in v11
from semantic_release.helpers import (
    sort_numerically,  # noqa: F401 # TODO: maintained for compatibility
)

if TYPE_CHECKING:  # pragma: no cover
    from re import Pattern
    from typing import Any, TypedDict

    from git import Commit

    class RegexReplaceDef(TypedDict):
        pattern: Pattern
        repl: str


breaking_re = regexp(r"BREAKING[ -]CHANGE:\s?(.*)")

un_word_wrap: RegexReplaceDef = {
    # Match a line ending where the next line is not indented, or a bullet
    "pattern": regexp(r"((?<!-)\n(?![\s*-]))"),
    "repl": r" ",  # Replace with a space
}

un_word_wrap_hyphen: RegexReplaceDef = {
    "pattern": regexp(r"((?<=\w)-\n(?=\w))"),
    "repl": r"-",  # Replace with single hyphen
}

trim_line_endings: RegexReplaceDef = {
    # Match line endings with optional whitespace
    "pattern": regexp(r"[\r\t\f\v ]*\r?\n"),
    "repl": "\n",  # remove the optional whitespace & remove windows newlines
}

spread_out_git_footers: RegexReplaceDef = {
    # Match a git footer line, and add an extra newline after it
    # only be flexible enough for a double space indent (otherwise its probably on purpose)
    #   - found collision with dependabot's yaml in a commit message with a git footer (its unusal but possible)
    "pattern": regexp(r"^ {0,2}([\w-]*: .+)$\n?((?!\n) *[^:\n]+:)", MULTILINE),
    "repl": r"\1\n\n\2",
}


def parse_paragraphs(text: str) -> list[str]:
    r"""
    This will take a text block and return a list containing each
    paragraph with single line breaks collapsed into spaces.

    To handle Windows line endings, carriage returns '\r' are removed before
    separating into paragraphs.

    It will attempt to detect Git footers and they will not be condensed.

    :param text: The text string to be divided.
    :return: A list of condensed paragraphs, as strings.
    """
    adjusted_text = reduce(
        lambda txt, adj: adj["pattern"].sub(adj["repl"], txt),
        [trim_line_endings, un_word_wrap_hyphen],
        text,
    )

    # Repeat replacements until no more changes are made
    prev_iteration = ""
    while prev_iteration != adjusted_text:
        prev_iteration = adjusted_text
        adjusted_text = spread_out_git_footers["pattern"].sub(
            spread_out_git_footers["repl"], adjusted_text
        )

    return list(
        filter(
            None,
            [
                un_word_wrap["pattern"].sub(un_word_wrap["repl"], paragraph).strip()
                for paragraph in adjusted_text.strip().split("\n\n")
            ],
        )
    )


def force_str(msg: str | bytes | bytearray | memoryview) -> str:
    # This shouldn't be a thing but typing is being weird around what
    # git.commit.message returns and the memoryview type won't go away
    message = msg.tobytes() if isinstance(msg, memoryview) else msg
    return (
        message.decode("utf-8")
        if isinstance(message, (bytes, bytearray))
        else str(message)
    )


def deep_copy_commit(commit: Commit) -> dict[str, Any]:
    keys = [
        "repo",
        "binsha",
        "author",
        "authored_date",
        "committer",
        "committed_date",
        "message",
        "tree",
        "parents",
        "encoding",
        "gpgsig",
        "author_tz_offset",
        "committer_tz_offset",
    ]
    kwargs = {}
    for key in keys:
        with suppress(ValueError):
            if hasattr(commit, key) and (value := getattr(commit, key)) is not None:
                if key in ["parents", "repo", "tree"]:
                    # These tend to have circular references so don't deepcopy them
                    kwargs[key] = value
                    continue

                kwargs[key] = deepcopy(value)

    return kwargs
