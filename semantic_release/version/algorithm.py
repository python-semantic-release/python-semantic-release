from __future__ import annotations

import logging
from queue import Queue
from typing import TYPE_CHECKING, Iterable

from semantic_release.commit_parser import ParsedCommit
from semantic_release.const import DEFAULT_VERSION
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidVersion, MissingMergeBaseError
from semantic_release.version.version import Version

if TYPE_CHECKING:
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

log = logging.getLogger(__name__)


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
            log.warning(
                "Couldn't parse tag %s as as Version: %s",
                tag.name,
                str(e),
                exc_info=log.isEnabledFor(logging.DEBUG),
            )
            continue

        if version:
            ts_and_vs.append((tag, version))

    log.info("found %s previous tags", len(ts_and_vs))
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

            log.debug("checking if commit %s matches any tags", node.hexsha)
            version = tag_sha_2_version_lookup.get(node.hexsha, None)

            if version is not None:
                log.info(
                    "found latest version in branch history: %r (%s)",
                    str(version),
                    node.hexsha[:7],
                )
                result = version
                break

            log.debug("commit %s doesn't match any tags", node.hexsha)

            # Add all parent commits to the queue if they haven't been visited
            for parent in node.parents:
                if parent in visited:
                    log.debug("parent commit %s already visited", node.hexsha)
                    continue

                log.debug("queuing parent commit %s", parent.hexsha)
                q.put(parent)

        return result

    # Run a Breadth First Search to find the latest version in the history
    latest_version = bfs(merge_base)
    if latest_version is not None:
        log.info("the latest version in this branch's history is %s", latest_version)
    else:
        log.info("no version tags found in this branch's history")

    return latest_version


def _increment_version(
    latest_version: Version,
    latest_full_version: Version,
    latest_full_version_in_history: Version,
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
    log.debug("_increment_version: %s", ", ".join(f"{k} = {v}" for k, v in local_vars))
    if latest_version.major == 0:
        if not allow_zero_version:
            # Set up default version to be 1.0.0 if currently 0.x.x which means a commented
            # breaking change is not required to bump to 1.0.0
            log.debug(
                "Bumping major version as 0.x.x versions are disabled because of allow_zero_version=False"
            )
            level_bump = LevelBump.MAJOR

        elif not major_on_zero:
            # if we are a 0.x.y release and have set `major_on_zero`,
            # breaking changes should increment the minor digit
            # Correspondingly, we reduce the level that we increment the
            # version by.
            log.debug(
                "reducing version increment due to 0. version and major_on_zero=False"
            )

            level_bump = min(level_bump, LevelBump.MINOR)

    if prerelease:
        log.debug("prerelease=true")
        target_final_version = latest_full_version.finalize_version()
        diff_with_last_released_version = (
            latest_version - latest_full_version_in_history
        )
        log.debug(
            "diff between the latest version %s and the latest full release version %s "
            "is: %s",
            latest_version,
            latest_full_version_in_history,
            diff_with_last_released_version,
        )
        # 6a i) if the level_bump > the level bump introduced by any prerelease tag
        # before e.g. 1.2.4-rc.3 -> 1.3.0-rc.1
        if level_bump > diff_with_last_released_version:
            log.debug(
                "this release has a greater bump than any change since the last full "
                "release, %s",
                latest_full_version_in_history,
            )
            return target_final_version.bump(level_bump).to_prerelease(
                token=prerelease_token
            )

        # 6a ii) if level_bump <= the level bump introduced by prerelease tag
        log.debug(
            "there has already been at least a %s release since the last full "
            "release %s",
            level_bump,
            latest_full_version_in_history,
        )
        log.debug("this release will increment the prerelease revision")
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
        log.debug(
            "prerelease=false and the latest version %s is a prerelease", latest_version
        )
        diff_with_last_released_version = (
            latest_version - latest_full_version_in_history
        )
        log.debug(
            "diff between the latest version %s and the latest full release version %s "
            "is: %s",
            latest_version,
            latest_full_version_in_history,
            diff_with_last_released_version,
        )
        if level_bump > diff_with_last_released_version:
            log.debug(
                "this release has a greater bump than any change since the last full "
                "release, %s",
                latest_full_version_in_history,
            )
            return latest_version.bump(level_bump).finalize_version()
        log.debug(
            "there has already been at least a %s release since the last full "
            "release %s",
            level_bump,
            latest_full_version_in_history,
        )
        return latest_version.finalize_version()

    # 6b. ii) If there's been no prerelease
    log.debug(
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
    # Step 1. All tags, sorted descending by semver ordering rules
    all_git_tags_as_versions = tags_and_versions(repo.tags, translator)
    all_full_release_tags_and_versions = list(
        filter(lambda t_v: not t_v[1].is_prerelease, all_git_tags_as_versions)
    )
    log.info(
        "Found %s full releases (excluding prereleases)",
        len(all_full_release_tags_and_versions),
    )

    # Default initial version
    latest_full_release_tag, latest_full_release_version = next(
        iter(all_full_release_tags_and_versions),
        (None, translator.from_string(DEFAULT_VERSION)),
    )

    # we can safely scan the extra commits on this
    # branch if it's never been released, but we have no other
    # guarantees that other branches exist
    # Note the merge_base might be on our current branch, it's not
    # necessarily the merge base of the current branch with `main`
    other_ref = (
        repo.active_branch
        if latest_full_release_tag is None
        else latest_full_release_tag.name
    )

    # Conditional log message to inform what was chosen as the comparison point
    # to find the merge base of the current branch with the latest full release
    log_msg = (
        str.join(
            ", ",
            [
                "No full releases have been made yet",
                f"the default version to use is {latest_full_release_version}",
            ],
        )
        if latest_full_release_tag is None
        else str.join(
            ", ",
            [
                f"The last full release was {latest_full_release_version}",
                f"tagged as {latest_full_release_tag!r}",
            ],
        )
    )

    log.info(log_msg)
    merge_bases = repo.merge_base(other_ref, repo.active_branch)

    if len(merge_bases) < 1:
        raise MissingMergeBaseError(
            f"Unable to find merge-base between {other_ref} and {repo.active_branch.name}"
        )

    if len(merge_bases) > 1:
        raise NotImplementedError(
            str.join(
                " ",
                [
                    "This branch has more than one merge-base with the",
                    "latest version, which is not yet supported",
                ],
            )
        )

    merge_base = merge_bases[0]

    if merge_base is None:
        str_tag_name = (
            "None" if latest_full_release_tag is None else latest_full_release_tag.name
        )
        raise ValueError(
            f"The merge_base found by merge_base({str_tag_name}, {repo.active_branch}) "
            "is None"
        )

    latest_full_version_in_history = _bfs_for_latest_version_in_history(
        merge_base=merge_base,
        full_release_tags_and_versions=all_full_release_tags_and_versions,
    )
    log.info(
        "The last full version in this branch's history was %s",
        latest_full_version_in_history,
    )

    commits_since_last_full_release = (
        repo.iter_commits()
        if latest_full_version_in_history is None
        else repo.iter_commits(f"{latest_full_version_in_history.as_tag()}...")
    )

    # Step 4. Parse each commit since the last release and find any tags that have
    # been added since then.
    parsed_levels: set[LevelBump] = set()
    latest_version = latest_full_version_in_history or Version(
        0,
        0,
        0,
        prerelease_token=translator.prerelease_token,
        tag_format=translator.tag_format,
    )

    # We only include pre-releases here if doing a prerelease.
    # If it's not a prerelease, we need to include commits back
    # to the last full version in consideration for what kind of
    # bump to produce. However if we're doing a prerelease, we can
    # include prereleases here to potentially consider a smaller portion
    # of history (from a prerelease since the last full release, onwards)

    # Note that a side-effect of this is, if at some point the configuration
    # for a particular branch pattern changes w.r.t. prerelease=True/False,
    # the new kind of version will be produced from the commits already
    # included in a prerelease since the last full release on the branch
    tag_sha_2_version_lookup = {
        tag.commit.hexsha: (tag, version)
        for tag, version in all_git_tags_as_versions
        if prerelease or not version.is_prerelease
    }

    # N.B. these should be sorted so long as we iterate the commits in reverse order
    for commit in commits_since_last_full_release:
        parse_result = commit_parser.parse(commit)
        if isinstance(parse_result, ParsedCommit):
            log.debug(
                "adding %s to the levels identified in commits_since_last_full_release",
                parse_result.bump,
            )
            parsed_levels.add(parse_result.bump)

        log.debug("checking if commit %s matches any tags", commit.hexsha)
        t_v = tag_sha_2_version_lookup.get(commit.hexsha, None)

        if t_v is None:
            # If we haven't found the latest prerelease on the branch,
            # keep the loop going to look for it
            log.debug("no tags correspond to commit %s", commit.hexsha)
            continue

        # Unpack the tuple
        tag, latest_version = t_v
        log.debug(
            "tag %r (%s) matches commit %s. the latest version is %s",
            tag.name,
            tag.commit.hexsha,
            commit.hexsha,
            latest_version,
        )
        break

    log.debug(
        "parsed the following distinct levels from the commits since the last release: "
        "%s",
        parsed_levels,
    )
    level_bump = max(parsed_levels, default=LevelBump.NO_RELEASE)
    log.info("The type of the next release release is: %s", level_bump)
    if level_bump is LevelBump.NO_RELEASE:  # noqa: SIM102
        if latest_version.major != 0 or allow_zero_version:
            log.info("No release will be made")
            return latest_version

    return _increment_version(
        latest_version=latest_version,
        latest_full_version=latest_full_release_version,
        latest_full_version_in_history=(
            latest_full_version_in_history
            or Version(
                0,
                0,
                0,
                prerelease_token=translator.prerelease_token,
                tag_format=translator.tag_format,
            )
        ),
        level_bump=level_bump,
        prerelease=prerelease,
        prerelease_token=translator.prerelease_token,
        major_on_zero=major_on_zero,
        allow_zero_version=allow_zero_version,
    )
