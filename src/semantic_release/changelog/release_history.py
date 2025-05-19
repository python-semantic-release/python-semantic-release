from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, TypedDict

from git.objects.tag import TagObject

from semantic_release.commit_parser import ParseError
from semantic_release.commit_parser.token import ParsedCommit
from semantic_release.commit_parser.util import force_str
from semantic_release.enums import LevelBump
from semantic_release.globals import logger
from semantic_release.helpers import validate_types_in_sequence
from semantic_release.version.algorithm import tags_and_versions

if TYPE_CHECKING:  # pragma: no cover
    from re import Pattern
    from typing import Iterable, Iterator

    from git.repo.base import Repo
    from git.util import Actor

    from semantic_release.commit_parser import (
        CommitParser,
        ParseResult,
        ParserOptions,
    )
    from semantic_release.version.translator import VersionTranslator
    from semantic_release.version.version import Version


class ReleaseHistory:
    @classmethod
    def from_git_history(
        cls,
        repo: Repo,
        translator: VersionTranslator,
        commit_parser: CommitParser[ParseResult, ParserOptions],
        exclude_commit_patterns: Iterable[Pattern[str]] = (),
    ) -> ReleaseHistory:
        all_git_tags_and_versions = tags_and_versions(repo.tags, translator)
        unreleased: dict[str, list[ParseResult]] = defaultdict(list)
        released: dict[Version, Release] = {}

        # Performance optimization: create a mapping of tag sha to version
        # so we can quickly look up the version for a given commit based on sha
        tag_sha_2_version_lookup = {
            tag.commit.hexsha: (tag, version)
            for tag, version in all_git_tags_and_versions
        }

        ignore_merge_commits = bool(
            hasattr(commit_parser, "options")
            and hasattr(commit_parser.options, "ignore_merge_commits")
            and getattr(commit_parser.options, "ignore_merge_commits")  # noqa: B009
        )

        # Strategy:
        # Loop through commits in history, parsing as we go.
        # Add these commits to `unreleased` as a key-value mapping
        # of type_ to ParseResult, until we encounter a tag
        # which matches a commit.
        # Then, we add the version for that tag as a key to `released`,
        # and set the value to an empty dict. Into that empty dict
        # we place the key-value mapping type_ to ParseResult as before.
        # We do this until we encounter a commit which another tag matches.

        the_version: Version | None = None

        for commit in repo.iter_commits("HEAD", topo_order=True):
            # Determine if we have found another release
            logger.debug("checking if commit %s matches any tags", commit.hexsha[:7])
            t_v = tag_sha_2_version_lookup.get(commit.hexsha, None)

            if t_v is None:
                logger.debug("no tags correspond to commit %s", commit.hexsha)
            else:
                # Unpack the tuple (overriding the current version)
                tag, the_version = t_v
                # we have found the latest commit introduced by this tag
                # so we create a new Release entry
                logger.debug("found commit %s for tag %s", commit.hexsha, tag.name)

                # tag.object is a Commit if the tag is lightweight, otherwise
                # it is a TagObject with additional metadata about the tag
                if isinstance(tag.object, TagObject):
                    tagger = tag.object.tagger
                    committer = tag.object.tagger.committer()
                    _tz = timezone(timedelta(seconds=-1 * tag.object.tagger_tz_offset))
                    tagged_date = datetime.fromtimestamp(tag.object.tagged_date, tz=_tz)
                else:
                    # For some reason, sometimes tag.object is a Commit
                    tagger = tag.object.author
                    committer = tag.object.author
                    _tz = timezone(timedelta(seconds=-1 * tag.object.author_tz_offset))
                    tagged_date = datetime.fromtimestamp(
                        tag.object.committed_date, tz=_tz
                    )

                release = Release(
                    tagger=tagger,
                    committer=committer,
                    tagged_date=tagged_date,
                    elements=defaultdict(list),
                    version=the_version,
                )

                released.setdefault(the_version, release)

            logger.info(
                "parsing commit [%s] %s",
                commit.hexsha[:8],
                str(commit.message).replace("\n", " ")[:54],
            )
            # returns a ParseResult or list of ParseResult objects,
            # it is usually one, but we split a commit if a squashed merge is detected
            parse_results = commit_parser.parse(commit)

            if not any(
                (
                    isinstance(parse_results, (ParseError, ParsedCommit)),
                    (
                        (
                            isinstance(parse_results, list)
                            or type(parse_results) == tuple
                        )
                        and validate_types_in_sequence(
                            parse_results, (ParseError, ParsedCommit)
                        )
                    ),
                )
            ):
                raise TypeError("Unexpected type returned from commit_parser.parse")

            results: list[ParseResult] = [
                *(
                    [parse_results]
                    if isinstance(parse_results, (ParseError, ParsedCommit))
                    else parse_results
                ),
            ]

            is_squash_commit = bool(len(results) > 1)

            # iterate through parsed commits to add to changelog definition
            for parsed_result in results:
                commit_message = force_str(parsed_result.commit.message)
                commit_type = (
                    "unknown"
                    if isinstance(parsed_result, ParseError)
                    else parsed_result.type
                )
                logger.debug("commit has type '%s'", commit_type)

                has_exclusion_match = any(
                    pattern.match(commit_message) for pattern in exclude_commit_patterns
                )

                commit_level_bump = (
                    LevelBump.NO_RELEASE
                    if isinstance(parsed_result, ParseError)
                    else parsed_result.bump
                )

                if ignore_merge_commits and parsed_result.is_merge_commit():
                    logger.info("Excluding merge commit[%s]", parsed_result.short_hash)
                    continue

                # Skip excluded commits except for any commit causing a version bump
                # Reasoning: if a commit causes a version bump, and no other commits
                # are included, then the changelog will be empty. Even if ther was other
                # commits included, the true reason for a version bump would be missing.
                if has_exclusion_match and commit_level_bump == LevelBump.NO_RELEASE:
                    logger.info(
                        "Excluding %s commit[%s] %s",
                        "piece of squashed" if is_squash_commit else "",
                        parsed_result.short_hash,
                        commit_message.split("\n", maxsplit=1)[0][:20],
                    )
                    continue

                if (
                    isinstance(parsed_result, ParsedCommit)
                    and not parsed_result.include_in_changelog
                ):
                    logger.info(
                        str.join(
                            " ",
                            [
                                "Excluding commit[%s] because parser determined",
                                "it should not included in the changelog",
                            ],
                        ),
                        parsed_result.short_hash,
                    )
                    continue

                if the_version is None:
                    logger.info(
                        "[Unreleased] adding commit[%s] to unreleased '%s'",
                        parsed_result.short_hash,
                        commit_type,
                    )
                    unreleased[commit_type].append(parsed_result)
                    continue

                logger.info(
                    "[%s] adding commit[%s] to release '%s'",
                    the_version,
                    parsed_result.short_hash,
                    commit_type,
                )

                released[the_version]["elements"][commit_type].append(parsed_result)

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
                    "version": version,
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
    version: Version
