from __future__ import annotations

import re

breaking_re = re.compile(r"BREAKING[ -]CHANGE:\s?(.*)")


def parse_paragraphs(text: str) -> list[str]:
    r"""
    This will take a text block and return a list containing each
    paragraph with single line breaks collapsed into spaces.

    To handle Windows line endings, carriage returns '\r' are removed before
    separating into paragraphs.

    :param text: The text string to be divided.
    :return: A list of condensed paragraphs, as strings.
    """
    return list(
        filter(
            None,
            [
                paragraph.replace("\n", " ").strip()
                for paragraph in text.replace("\r", "").split("\n\n")
            ],
        )
    )
