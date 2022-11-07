from __future__ import annotations

import re

breaking_re = re.compile(r"BREAKING[ -]CHANGE:\s?(.*)")


def parse_paragraphs(text: str) -> list[str]:
    """
    This will take a text block and return a list containing each
    paragraph with single line breaks collapsed into spaces.
    :param text: The text string to be divided.
    :return: A list of condensed paragraphs, as strings.
    """
    return [
        paragraph.replace("\n", " ")
        for paragraph in text.split("\n\n")
        if len(paragraph) > 0
    ]
