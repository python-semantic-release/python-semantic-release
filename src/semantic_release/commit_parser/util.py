from __future__ import annotations

from functools import reduce
from re import compile as regexp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from re import Pattern
    from typing import TypedDict

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


def parse_paragraphs(text: str) -> list[str]:
    r"""
    This will take a text block and return a list containing each
    paragraph with single line breaks collapsed into spaces.

    To handle Windows line endings, carriage returns '\r' are removed before
    separating into paragraphs.

    :param text: The text string to be divided.
    :return: A list of condensed paragraphs, as strings.
    """
    adjusted_text = reduce(
        lambda txt, adj: adj["pattern"].sub(adj["repl"], txt),
        [trim_line_endings, un_word_wrap_hyphen],
        text,
    )

    return list(
        filter(
            None,
            [
                un_word_wrap["pattern"].sub(un_word_wrap["repl"], paragraph).strip()
                for paragraph in adjusted_text.split("\n\n")
            ],
        )
    )
