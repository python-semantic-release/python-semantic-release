"""
Scipy commit style parser

Parses commit messages of the following forms

```
<tag>: <subject>

<body>
```

Both <tag> and <body> are optional. If <tag> is missing, then the commit message
should be of the form

```
<subject>

<body>
```

again with an optional body. Releases will only be generated for tagged commits
or commits.

https://docs.scipy.org/doc/scipy/reference/dev/contributor/continuous_integration.html#continuous-integration
"""
import logging
import re
from dataclasses import dataclass
from semantic_release.history.parser_angular import MINOR_TYPES

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from .parser_helpers import ParsedCommit, parse_paragraphs, re_breaking

logger = logging.getLogger(__name__)


@dataclass
class ChangeType:
    tag: str
    description: str
    bump_level: int = 0

    def make_breaking(self):
        self.bump_level = 3


@dataclass
class Breaking(ChangeType):
    bump_level: int = 3


@dataclass
class Compatible(ChangeType):
    bump_level: int = 2


@dataclass
class Patch(ChangeType):
    bump_level: int = 1


@dataclass
class Ignore(ChangeType):
    bump_level: int = 0


COMMIT_TYPES = [
    Breaking("API", "an (incompatible) API change"),
    Compatible("DEP", "deprecate something, or remove a deprecated object"),
    Compatible("ENH", "enhancement"),
    Compatible("REV", "revert an earlier commit"),
    Patch("BUG", "bug fix"),
    Ignore("MAINT", "maintenance commit (refactoring, typos, etc.)"),
    Ignore("BENCH", "changes to the benchmark suite"),
    Ignore("BLD", "change related to building"),
    Ignore("DEV", "development tool or utility"),
    Ignore("DOC", "documentation"),
    Ignore("STY", "style fix (whitespace, PEP8)"),
    Ignore("TST", "addition or modification of tests"),
    Ignore("REL", "related to releasing"),
    
    # strictly speaking not part of the standard
    Compatible("FEAT", "new feature"),
    Ignore("TEST", "addition or modification of tests"),
]


@LoggedFunction(logger)
def parse_commit_message(message: str) -> ParsedCommit:
    """
    Parse a scipy-style commit message

    :param message: A string of a commit message.
    :return: A tuple of (level to bump, type of change, scope of change, a tuple
    with descriptions)
    :raises UnknownCommitMessageStyleError: if regular expression matching fails
    """

    blocks = message.split("\n\n")
    blocks = [x for x in blocks if not x == ""]
    header = blocks[0]

    for msg_type in COMMIT_TYPES:
        msg_type:ChangeType
        tag = msg_type.tag
        if header.startswith(tag):
            header = header[len(tag):]
            header = header[2:] if header[0] == ":" else header[0]
            blocks[0] = header
            break
    else:
        # some commits may not have an acronym if they belong to a PR that
        # wasn't squashed (for maintainability) ignore them
        msg_type = Ignore("", "Untagged commit.")

    # Look for descriptions of breaking changes
    # technically scipy doesn't document breaking changes explicitly
    breaking_blocks = [block for block in blocks if block.startswith("BREAKING CHANGE")]
    if breaking_blocks:
        msg_type.make_breaking()

    return ParsedCommit(
        msg_type.bump_level,
        msg_type.description,
        None,  # scipy style doesn't use scopes
        blocks,
        breaking_blocks
    )
