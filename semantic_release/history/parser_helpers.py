"""Commit parser helpers
"""
import collections
import re
from typing import List

re_breaking = re.compile("BREAKING[ -]CHANGE: ?(.*)")


ParsedCommit = collections.namedtuple(
    "ParsedCommit", ["bump", "type", "scope", "descriptions", "breaking_descriptions"]
)


def parse_paragraphs(text: str) -> List[str]:
    """
    This will take a text block and return a tuple containing each
    paragraph with single line breaks collapsed into spaces.

    :param text: The text string to be divided.
    :return: A tuple of paragraphs.
    """
    return [
        paragraph.replace("\n", " ")
        for paragraph in text.split("\n\n")
        if len(paragraph) > 0
    ]
