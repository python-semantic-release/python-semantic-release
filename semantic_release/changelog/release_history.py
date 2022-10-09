import logging
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

from git import Repo

from semantic_release.commit_parser import CommitParser, ParseError, ParseResult
from semantic_release.version.algorithm import tags_and_versions
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

log = logging.getLogger(__name__)


# NOTE the `released` dict should actually be the following structure:
# {
#     "version": {
#          "change_type": [ParseResult]
#     }
# }
# Changes introduced by each version should be stored in that version's value

# Note: generic NamedTuples aren't yet supported by mypy
# see https://github.com/python/mypy/issues/685
class ReleaseHistory(NamedTuple):
    unreleased: Dict[str, List[ParseResult]]
    released: Dict[Version, Dict[str, List[ParseResult]]]

    def __repr__(self) -> str:
        return (
            f"<{type(self).__qualname__}: {len(self.unreleased)} commits unreleased, "
            f"{len(self.released)} versions released>"
        )


def release_history(
    repo: Repo,
    translator: VersionTranslator,
    commit_parser: CommitParser,
) -> ReleaseHistory:
    all_git_tags_and_versions = tags_and_versions(repo.tags, translator)
    unreleased: Dict[str, List[ParseResult]] = defaultdict(list)
    released: Dict[Version, Dict[str, List[ParseResult]]] = {}

    # Strategy:
    # Loop through commits in history, parsing as we go.
    # Add these commits to `unreleased` as a key-value mapping
    # of type_ to ParseResult, until we encounter a tag
    # which matches a commit.
    # Then, we add the version for that tag as a key to `released`,
    # and set the value to an empty dict. Into that empty dict
    # we place the key-value mapping type_ to ParseResult as before.
    # We do this until we encounter a commit which another tag matches.

    is_commit_released = False
    the_version: Optional[Version] = None

    for commit in repo.iter_commits():
        parse_result = commit_parser.parse(commit)
        commit_type = (
            "unknown" if isinstance(parse_result, ParseError) else parse_result.type
        )

        for tag, version in all_git_tags_and_versions:
            if tag.commit == commit:
                # we have found the latest commit introduced by this tag
                is_commit_released = True
                the_version = version
                break

        if not is_commit_released:
            unreleased[commit_type].append(parse_result)
            continue

        assert the_version is not None
        released.setdefault(the_version, defaultdict(list))
        released[the_version][commit_type].append(parse_result)

    return ReleaseHistory(unreleased=unreleased, released=released)
