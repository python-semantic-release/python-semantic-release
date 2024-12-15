from __future__ import annotations

import logging
from contextlib import suppress
from queue import LifoQueue, Queue
from typing import TYPE_CHECKING, Iterable

from semantic_release.commit_parser import ParsedCommit
from semantic_release.const import DEFAULT_VERSION
from semantic_release.enums import LevelBump, SemanticReleaseLogLevels
from semantic_release.errors import InternalError, InvalidVersion

if TYPE_CHECKING:  # pragma: no cover
    from typing import Sequence

    from git.objects.blob import Blob
    from git.objects.commit import Commit
    from git.objects.tag import TagObject
    from git.objects.tree import Tree
    from git.refs.tag import Tag
    from git.repo.base import Repo

    from semantic_release.commit_parser import (
        CommitParser,
        ParseResult,
        ParserOptions,
    )
    from semantic_release.version.translator import VersionTranslator
    from semantic_release.version.version import Version


logger = logging.getLogger(__name__)


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


def _bfs_for_latest_version_in_history(
    merge_base: Commit | TagObject | Blob | Tree,
    full_release_tags_and_versions: list[tuple[Tag, Version]],
) -> Version | None:
    """
    Run a breadth-first search through the given `merge_base`'s parents,
    looking for the most recent version corresponding to a commit in the
    `merge_base`'s parents' history. If no commits in the history correspond
    to a released version, return None
    """
    tag_sha_2_version_lookup = {
        tag.commit.hexsha: version for tag, version in full_release_tags_and_versions
    }

    # Step 3. Latest full release version within the history of the current branch
    # Breadth-first search the merge-base and its parent commits for one which matches
    # the tag of the latest full release tag in history
    def bfs(start_commit: Commit | TagObject | Blob | Tree) -> Version | None:
        # Derived from Geeks for Geeks
        # https://www.geeksforgeeks.org/python-program-for-breadth-first-search-or-bfs-for-a-graph/?ref=lbp

        # Create a queue for BFS
        q: Queue[Commit | TagObject | Blob | Tree] = Queue()

        # Create a set to store visited graph nodes (commit objects in this case)
        visited: set[Commit | TagObject | Blob | Tree] = set()

        # Add the source node in the queue & mark as visited to start the search
        q.put(start_commit)
        visited.add(start_commit)

        # Initialize the result to None
        result = None

        # Traverse the git history until it finds a version tag if one exists
        while not q.empty():
            node = q.get()
            visited.add(node)

            logger.debug("checking if commit %s matches any tags", node.hexsha)
            version = tag_sha_2_version_lookup.get(node.hexsha, None)

            if version is not None:
                logger.info(
                    "found latest version in branch history: %r (%s)",
                    str(version),
                    node.hexsha[:7],
                )
                result = version
                break

            logger.debug("commit %s doesn't match any tags", node.hexsha)

            # Add all parent commits to the queue if they haven't been visited
            for parent in node.parents:
                if parent in visited:
                    logger.debug("parent commit %s already visited", node.hexsha)
                    continue

                logger.debug("queuing parent commit %s", parent.hexsha)
                q.put(parent)

        return result

    # Run a Breadth First Search to find the latest version in the history
    latest_version = bfs(merge_base)
    if latest_version is not None:
        logger.info("the latest version in this branch's history is %s", latest_version)
    else:
        logger.info("no version tags found in this branch's history")

    return latest_version


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
                logger.debug("queuing parent commit %s", parent.hexsha[:7])
                stack.put(parent)

        return commits

    # Step 3. Latest full release version within the history of the current branch
    # Breadth-first search the merge-base and its parent commits for one which matches
    # the tag of the latest full release tag in history
    def bfs(start_commit: Commit, stop_nodes: set[Commit]) -> Sequence[Commit]:
        # Derived from Geeks for Geeks
        # https://www.geeksforgeeks.org/python-program-for-breadth-first-search-or-bfs-for-a-graph/?ref=lbp

        # Create a queue for BFS
        q: Queue[Commit] = Queue()

        # Create a set to store visited graph nodes (commit objects in this case)
        visited: set[Commit] = set()

        # Initialize the result
        commits: list[Commit] = []

        if start_commit in stop_nodes:
            logger.debug("start commit %s is a stop node", start_commit.hexsha[:7])
            return commits

        # Add the source node in the queue to start the search
        q.put(start_commit)

        # Traverse the git history capturing each commit found before it reaches a stop node
        while not q.empty():
            if (node := q.get()) in visited:
                continue

            visited.add(node)
            commits.append(node)

            # Add all parent commits to the queue if they haven't been visited (read parents in reverse order)
            # as the left side is generally the merged into branch
            for parent in node.parents[::-1]:
                if parent in visited:
                    logger.debug("parent commit %s already visited", node.hexsha[:7])
                    continue

                if parent in stop_nodes:
                    logger.debug("parent commit %s is a stop node", node.hexsha[:7])
                    continue

                logger.debug("queuing parent commit %s", parent.hexsha[:7])
                q.put(parent)

        return commits

    # Run a Depth First Search to find all the commits since the last release
    commits_since_last_release = dfs(
        start_commit=head_commit,
        stop_nodes=set(
            head_commit.repo.iter_commits(latest_release_tag_str)
            if latest_release_tag_str
            else []
        ),
    )

    log_msg = (
        f"Found {len(commits_since_last_release)} commits since the last release!"
        if len(commits_since_last_release) > 0
        else "No commits found since the last release!"
    )
    logger.info(log_msg)

    return commits_since_last_release


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

    `latest_version`, `latest_full_version` and `latest_full_version_in_history`
    can be the same, but aren't necessarily.

    `latest_version` is the most recent version released from this branch's history.
    `latest_full_version` is the most recent full release (i.e. not a prerelease)
    anywhere in the repository's history, including commits which aren't present on
    this branch.
    `latest_full_version_in_history`, correspondingly, is the latest full release which
    is in this branch's history.
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

    # Determine the difference between the latest version and the latest full release
    diff_with_last_released_version = latest_version - latest_full_version
    logger.debug(
        "diff between the latest version %s and the latest full release version %s is: %s",
        latest_version,
        latest_full_version,
        diff_with_last_released_version,
    )

    # Handle prerelease version bumps
    if prerelease:
        # 6a i) if the level_bump > the level bump introduced by any prerelease tag
        # before e.g. 1.2.4-rc.3 -> 1.3.0-rc.1
        if level_bump > diff_with_last_released_version:
            logger.debug(
                "this release has a greater bump than any change since the last full release, %s",
                latest_full_version,
            )
            return (
                latest_full_version.finalize_version()
                .bump(level_bump)
                .to_prerelease(token=prerelease_token)
            )

        # 6a ii) if level_bump <= the level bump introduced by prerelease tag
        logger.debug(
            "there has already been at least a %s release since the last full release %s",
            level_bump,
            latest_full_version,
        )
        logger.debug("this release will increment the prerelease revision")
        return latest_version.to_prerelease(
            token=prerelease_token,
            revision=(
                1
                if latest_version.prerelease_token != prerelease_token
                else (latest_version.prerelease_revision or 0) + 1
            ),
        )

    # 6b. if not prerelease
    # NOTE: These can actually be condensed down to the single line
    # 6b. i) if there's been a prerelease
    if latest_version.is_prerelease:
        logger.debug(
            "prerelease=false and the latest version %s is a prerelease", latest_version
        )
        if level_bump > diff_with_last_released_version:
            logger.debug(
                "this release has a greater bump than any change since the last full release, %s",
                latest_full_version,
            )
            return latest_version.bump(level_bump).finalize_version()

        logger.debug(
            "there has already been at least a %s release since the last full release %s",
            level_bump,
            latest_full_version,
        )
        return latest_version.finalize_version()

    # 6b. ii) If there's been no prerelease
    logger.debug(
        "prerelease=false and %s is not a prerelease; bumping with a %s release",
        latest_version,
        level_bump,
    )
    return latest_version.bump(level_bump)


def next_version(
    repo: Repo,
    translator: VersionTranslator,
    commit_parser: CommitParser[ParseResult, ParserOptions],
    prerelease: bool = False,
    major_on_zero: bool = True,
    allow_zero_version: bool = True,
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

    # Step 5. Parse the commits to determine the bump level that should be applied
    parsed_levels: set[LevelBump] = {
        parsed_result.bump  # type: ignore[union-attr] # too complex for type checkers
        for parsed_result in filter(
            lambda parsed_result: isinstance(parsed_result, ParsedCommit),
            map(commit_parser.parse, commits_since_last_release),
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
