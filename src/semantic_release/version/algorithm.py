from __future__ import annotations

import logging
from contextlib import suppress
from functools import reduce
from queue import LifoQueue
from typing import TYPE_CHECKING, Iterable

from semantic_release.commit_parser import ParsedCommit
from semantic_release.commit_parser.token import ParseError
from semantic_release.const import DEFAULT_VERSION
from semantic_release.enums import LevelBump, SemanticReleaseLogLevels
from semantic_release.errors import InternalError, InvalidVersion
from semantic_release.globals import logger
from semantic_release.helpers import validate_types_in_sequence

if TYPE_CHECKING:  # pragma: no cover
    from typing import Sequence

    from git.objects.commit import Commit
    from git.refs.tag import Tag
    from git.repo.base import Repo

    from semantic_release.commit_parser import (
        CommitParser,
        ParseResult,
        ParserOptions,
    )
    from semantic_release.version.translator import VersionTranslator
    from semantic_release.version.version import Version


def tags_and_versions(
    tags: Iterable[Tag], translator: VersionTranslator
) -> list[tuple[Tag, Version]]:
    """
    Return a list of 2-tuples, where each element is a tuple (tag, version)
    from the tags in the Git repo and their corresponding `Version` according
    to `Version.from_tag`. The returned list is sorted according to semver
    ordering rules.

    Tags which are not matched by `translator` are ignored.
    """
    ts_and_vs: list[tuple[Tag, Version]] = []
    for tag in tags:
        try:
            version = translator.from_tag(tag.name)
        except (NotImplementedError, InvalidVersion) as e:
            logger.warning(
                "Couldn't parse tag %s as as Version: %s",
                tag.name,
                str(e),
                exc_info=logger.isEnabledFor(logging.DEBUG),
            )
            continue

        if version:
            ts_and_vs.append((tag, version))

    logger.info("found %s previous tags", len(ts_and_vs))
    return sorted(ts_and_vs, reverse=True, key=lambda v: v[1])


def _traverse_graph_for_commits(
    head_commit: Commit,
    latest_release_tag_str: str = "",
) -> Sequence[Commit]:
    # Depth-first search
    def dfs(start_commit: Commit, stop_nodes: set[Commit]) -> Sequence[Commit]:
        # Create a stack for DFS
        stack: LifoQueue[Commit] = LifoQueue()

        # Create a set to store visited graph nodes (commit objects in this case)
        visited: set[Commit] = set()

        # Initialize the result
        commits: list[Commit] = []

        # Add the source node in the queue to start the search
        stack.put(start_commit)

        # Traverse the git history capturing each commit found before it reaches a stop node
        while not stack.empty():
            if (node := stack.get()) in visited or node in stop_nodes:
                continue

            visited.add(node)
            commits.append(node)

            # Add all parent commits to the stack from left to right so that the rightmost is popped first
            # as the left side is generally the merged into branch
            for parent in node.parents:
                stack.put(parent)

        return commits

    # Run a Depth First Search to find all the commits since the last release
    return dfs(
        start_commit=head_commit,
        stop_nodes=set(
            head_commit.repo.iter_commits(latest_release_tag_str)
            if latest_release_tag_str
            else []
        ),
    )


def _increment_version(
    latest_version: Version,
    latest_full_version: Version,
    level_bump: LevelBump,
    prerelease: bool,
    prerelease_token: str,
    major_on_zero: bool,
    allow_zero_version: bool,
) -> Version:
    """
    Using the given versions, along with a given `level_bump`, increment to
    the next version according to whether or not this is a prerelease.

    `latest_version` is the most recent version released from this branch's history.
    `latest_full_version`, the most recent full release (i.e. not a prerelease)
    in this branch's history.

    `latest_version` and `latest_full_version` can be the same, but aren't necessarily.
    """
    local_vars = list(locals().items())
    logger.log(
        SemanticReleaseLogLevels.SILLY,
        "_increment_version: %s",
        str.join(", ", [f"{k} = {v}" for k, v in local_vars]),
    )

    # Handle variations where the latest version is 0.x.x
    if latest_version.major == 0:
        if not allow_zero_version:
            # Set up default version to be 1.0.0 if currently 0.x.x which means a commented
            # breaking change is not required to bump to 1.0.0
            logger.debug(
                "Bumping major version as 0.x.x versions are disabled because of allow_zero_version=False"
            )
            level_bump = LevelBump.MAJOR

        elif not major_on_zero:
            # if we are a 0.x.y release and have set `major_on_zero`,
            # breaking changes should increment the minor digit
            # Correspondingly, we reduce the level that we increment the
            # version by.
            logger.debug(
                "reducing version increment due to 0. version and major_on_zero=False"
            )

            level_bump = min(level_bump, LevelBump.MINOR)

    logger.debug(
        "prerelease=%s and the latest version %s %s prerelease",
        prerelease,
        latest_version,
        "is a" if latest_version.is_prerelease else "is not a",
    )

    if level_bump == LevelBump.NO_RELEASE:
        raise ValueError("level_bump must be at least PRERELEASE_REVISION")

    if level_bump == LevelBump.PRERELEASE_REVISION and not latest_version.is_prerelease:
        raise ValueError(
            "Cannot increment a non-prerelease version with a prerelease level bump"
        )

    # assume we always want to increment the version that is the latest in the branch's history
    base_version = latest_version

    # if the current version is a prerelease & we want a new prerelease, then
    # figure out if we need to bump the prerelease revision or start a new prerelease
    if latest_version.is_prerelease:
        # find the change since the last full release because if the current version is a prerelease
        # then we need to predict properly the next full version
        diff_with_last_released_version = latest_version - latest_full_version
        logger.debug(
            "the diff b/w the latest version '%s' and the latest full release version '%s' is: %s",
            latest_version,
            latest_full_version,
            diff_with_last_released_version,
        )

        # Since the difference is less than or equal to the level bump and we want a new prerelease,
        # we can abort early and just increment the revision
        if level_bump <= diff_with_last_released_version:
            # 6a ii) if level_bump <= the level bump introduced by the previous tag (latest_version)
            if prerelease:
                logger.debug(
                    "there has already been at least a %s release since the last full release %s",
                    level_bump,
                    latest_full_version,
                )
                logger.debug("Incrementing the prerelease revision...")
                new_revision = base_version.to_prerelease(
                    token=prerelease_token,
                    revision=(
                        1
                        if latest_version.prerelease_token != prerelease_token
                        else (latest_version.prerelease_revision or 0) + 1
                    ),
                )
                logger.debug("Incremented %s to %s", base_version, new_revision)
                return new_revision

            # When we don't want a prerelease, but the previous version is a prerelease that
            # had a greater bump than we currently are applying, choose the larger bump instead
            # as it consumes this bump
            logger.debug("Finalizing the prerelease version...")
            return base_version.finalize_version()

        # Fallthrough to handle all larger level bumps
        logger.debug(
            "this release has a greater bump than any change since the last full release, %s",
            latest_full_version,
        )

        # Fallthrough, if we don't want a prerelease, or if we do but the level bump is greater
        #
        # because the current version is a prerelease, we must start from the last full version
        # Case 1: we identified that the level bump is greater than the change since
        #         the last full release, this will also reset the prerelease revision
        # Case 2: we don't want a prerelease, so consider only the last full version in history
        base_version = latest_full_version

    # From the base version, we can now increment the version according to the level bump
    # regardless of the prerelease status as bump() handles the reset and pass through
    logger.debug("Bumping %s with a %s bump", base_version, level_bump)
    target_next_version = base_version.bump(level_bump)

    # Converting to/from a prerelease if necessary
    target_next_version = (
        target_next_version.to_prerelease(token=prerelease_token)
        if prerelease
        else target_next_version.finalize_version()
    )

    logger.debug("Incremented %s to %s", base_version, target_next_version)
    return target_next_version


def next_version(
    repo: Repo,
    translator: VersionTranslator,
    commit_parser: CommitParser[ParseResult, ParserOptions],
    allow_zero_version: bool,
    major_on_zero: bool,
    prerelease: bool = False,
) -> Version:
    """
    Evaluate the history within `repo`, and based on the tags and commits in the repo
    history, identify the next semantic version that should be applied to a release
    """
    # Default initial version
    # Since the translator is configured by the user, we can't guarantee that it will
    # be able to parse the default version. So we first cast it to a tag using the default
    # value and the users configured tag format, then parse it back to a version object
    default_initial_version = translator.from_tag(
        translator.str_to_tag(DEFAULT_VERSION)
    )
    if default_initial_version is None:
        # This should never happen, but if it does, it's a bug
        raise InternalError(
            "Translator was unable to parse the embedded default version"
        )

    # Step 1. All tags, sorted descending by semver ordering rules
    all_git_tags_as_versions = tags_and_versions(repo.tags, translator)

    # Retrieve all commit hashes (regardless of merges) in the current branch's history from repo origin
    commit_hash_set = {
        commit.hexsha
        for commit in _traverse_graph_for_commits(head_commit=repo.active_branch.commit)
    }

    # Filter all releases that are not found in the current branch's history
    historic_versions: list[Version] = []
    for tag, version in all_git_tags_as_versions:
        # TODO: move this to tags_and_versions() function?
        # Ignore the error that is raised when tag points to a Blob or Tree object rather
        # than a commit object (tags that point to tags that then point to commits are resolved automatically)
        with suppress(ValueError):
            if tag.commit.hexsha in commit_hash_set:
                historic_versions.append(version)

    # Step 2. Get the latest final release version in the history of the current branch
    #  or fallback to the default 0.0.0 starting version value if none are found
    latest_full_release_version = next(
        filter(
            lambda version: not version.is_prerelease,
            historic_versions,
        ),
        default_initial_version,
    )

    logger.info(
        f"The last full version in this branch's history was {latest_full_release_version}"
        if latest_full_release_version != default_initial_version
        else "No full releases found in this branch's history"
    )

    # Step 3. Determine the latest release version in the history of the current branch
    # If we the desired result is a prerelease, we must determine if there was any previous
    # prerelease in the history of the current branch beyond the latest_full_release_version.
    # Important to note that, we only consider prereleases that are of the same prerelease token
    # as the basis of incrementing the prerelease revision.
    # If we are not looking for a prerelease, this is the same as the last full release.
    latest_version = (
        latest_full_release_version
        if not prerelease
        else next(
            filter(
                lambda version: all(
                    [
                        version.is_prerelease,
                        version.prerelease_token == translator.prerelease_token,
                        version >= latest_full_release_version,
                    ]
                ),
                historic_versions,
            ),
            latest_full_release_version,  # default
        )
    )

    logger.info("The latest release in this branch's history was %s", latest_version)

    # Step 4. Walk the git tree to find all commits that have been made since the last release
    commits_since_last_release = _traverse_graph_for_commits(
        head_commit=repo.active_branch.commit,
        latest_release_tag_str=(
            # NOTE: the default_initial_version should not actually exist on the repository (ie v0.0.0)
            # so we provide an empty tag string when there are no tags on the repository yet
            latest_version.as_tag() if latest_version != default_initial_version else ""
        ),
    )

    logger.info(
        f"Found {len(commits_since_last_release)} commits since the last release!"
        if len(commits_since_last_release) > 0
        else "No commits found since the last release!"
    )

    # Step 5. apply the parser to each commit in the history (could return multiple results per commit)
    parsed_results = list(map(commit_parser.parse, commits_since_last_release))

    # Step 5A. Accumulate all parsed results into a single list accounting for possible multiple results per commit
    consolidated_results: list[ParseResult] = reduce(
        lambda accumulated_results, p_results: [
            *accumulated_results,
            *(
                # Cast to list if not already a list
                p_results
                if isinstance(p_results, list) or type(p_results) == tuple
                else [p_results]
            ),
        ],
        parsed_results,
        [],
    )

    # Step 5B. Validation type check for the parser results (important because of possible custom parsers)
    if not validate_types_in_sequence(consolidated_results, (ParseError, ParsedCommit)):
        raise TypeError("Unexpected type returned from commit_parser.parse")

    # Step 5C. Parse the commits to determine the bump level that should be applied
    parsed_levels: set[LevelBump] = {
        parsed_result.bump  # type: ignore[union-attr] # too complex for type checkers
        for parsed_result in filter(
            # Filter out any non-ParsedCommit results (i.e. ParseErrors)
            lambda parsed_result: isinstance(parsed_result, ParsedCommit),
            consolidated_results,
        )
    }

    logger.debug(
        "parsed the following distinct levels from the commits since the last release: %s",
        parsed_levels,
    )

    level_bump = max(parsed_levels, default=LevelBump.NO_RELEASE)
    logger.info("The type of the next release release is: %s", level_bump)

    if all(
        [
            level_bump is LevelBump.NO_RELEASE,
            latest_version.major != 0 or allow_zero_version,
        ]
    ):
        logger.info("No release will be made")
        return latest_version

    return _increment_version(
        latest_version=latest_version,
        latest_full_version=latest_full_release_version,
        level_bump=level_bump,
        prerelease=prerelease,
        prerelease_token=translator.prerelease_token,
        major_on_zero=major_on_zero,
        allow_zero_version=allow_zero_version,
    )
