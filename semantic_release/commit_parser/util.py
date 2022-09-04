import re
from typing import List, NamedTuple

from git import Commit

from semantic_release.enums import LevelBump


breaking_re = re.compile(r"BREAKING[ -]CHANGE:\s?(.*)")


def parse_paragraphs(text: str) -> List[str]:
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


class ParsedCommit(NamedTuple):
    bump: LevelBump
    type: str
    scope: str
    descriptions: List[str]
    breaking_descriptions: List[str]
    commit: Commit
