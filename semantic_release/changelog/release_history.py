from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable, Iterator

from git.objects.tag import TagObject
from git.repo.base import Repo
from git.util import Actor

# For Python3.7 compatibility
from typing_extensions import TypedDict

from semantic_release.commit_parser import (
    CommitParser,
    ParseError,
    ParseResult,
    ParserOptions,
)
from semantic_release.version.algorithm import tags_and_versions
from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version

log = logging.getLogger(__name__)


class ReleaseHistory:
    @classmethod
    def from_git_history(
        cls,
        repo: Repo,
        translator: VersionTranslator,
        commit_parser: CommitParser[ParseResult, ParserOptions],
        exclude_commit_patterns: Iterable[re.Pattern[str]] = (),
    ) -> ReleaseHistory:
        all_git_tags_and_versions = tags_and_versions(repo.tags, translator)
        unreleased: dict[str, list[ParseResult]] = defaultdict(list)
        released: dict[Version, Release] = {}

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
        the_version: Version | None = None

        for commit in repo.iter_commits():
            # mypy will be happy if we make this an explicit string
            commit_message = str(commit.message)

            parse_result = commit_parser.parse(commit)
            commit_type = (
                "unknown" if isinstance(parse_result, ParseError) else parse_result.type
            )
            log.debug("commit has type %s", commit_type)

            for tag, version in all_git_tags_and_versions:
                if tag.commit == commit:
                    # we have found the latest commit introduced by this tag
                    # so we create a new Release entry
                    log.debug("found commit %s for tag %s", commit.hexsha, tag.name)
                    is_commit_released = True
                    the_version = version

                    # tag.object is a Commit if the tag is lightweight, otherwise
                    # it is a TagObject with additional metadata about the tag
                    if isinstance(tag.object, TagObject):
                        tagger = tag.object.tagger
                        committer = tag.object.tagger.committer()
                        _tz = timezone(timedelta(seconds=tag.object.tagger_tz_offset))
                        tagged_date = datetime.fromtimestamp(
                            tag.object.tagged_date, tz=_tz
                        )
                    else:
                        # For some reason, sometimes tag.object is a Commit
                        tagger = tag.object.author
                        committer = tag.object.author
                        _tz = timezone(timedelta(seconds=tag.object.author_tz_offset))
                        tagged_date = datetime.fromtimestamp(
                            tag.object.committed_date, tz=_tz
                        )

                    release = Release(
                        tagger=tagger,
                        committer=committer,
                        tagged_date=tagged_date,
                        elements=defaultdict(list),
                    )

                    released.setdefault(the_version, release)
                    break

            if any(pat.match(commit_message) for pat in exclude_commit_patterns):
                log.debug(
                    "Skipping excluded commit %s (%s)",
                    commit.hexsha,
                    commit_message.replace("\n", " ")[:20],
                )
                continue

            if not is_commit_released:
                log.debug("adding commit %s to unreleased commits", commit.hexsha)
                unreleased[commit_type].append(parse_result)
                continue

            if the_version is None:
                raise RuntimeError("expected a version to be found")

            log.debug(
                "adding commit %s with type %s to release section for %s",
                commit.hexsha,
                commit_type,
                the_version,
            )

            released[the_version]["elements"][commit_type].append(parse_result)

        return cls(unreleased=unreleased, released=released)

    def __init__(
        self, unreleased: dict[str, list[ParseResult]], released: dict[Version, Release]
    ) -> None:
        self.released = released
        self.unreleased = unreleased

    def __iter__(
        self,
    ) -> Iterator[dict[str, list[ParseResult]] | dict[Version, Release]]:
        """
        Enables unpacking:
        >>> rh = ReleaseHistory(...)
        >>> unreleased, released = rh
        """
        yield self.unreleased
        yield self.released

    def release(
        self, version: Version, tagger: Actor, committer: Actor, tagged_date: datetime
    ) -> ReleaseHistory:
        if version in self.released:
            raise ValueError(f"{version} has already been released!")

        # return a new instance to avoid potential accidental
        # mutation
        return ReleaseHistory(
            unreleased={},
            released={
                version: {
                    "tagger": tagger,
                    "committer": committer,
                    "tagged_date": tagged_date,
                    "elements": self.unreleased,
                },
                **self.released,
            },
        )

    def __repr__(self) -> str:
        return (
            f"<{type(self).__qualname__}: "
            f"{sum(len(commits) for commits in self.unreleased.values())} "
            f"commits unreleased, {len(self.released)} versions released>"
        )


class Release(TypedDict):
    tagger: Actor
    committer: Actor
    tagged_date: datetime
    elements: dict[str, list[ParseResult]]
