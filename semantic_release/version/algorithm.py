import logging
from queue import Queue
from typing import Optional, Set, List

from git import Repo, Commit

from semantic_release.commit_parser import CommitParser, ParsedCommit
from semantic_release.enums import LevelBump
from semantic_release.version.version import Version
from semantic_release.version.translator import VersionTranslator

log = logging.getLogger(__name__)


def next_version(
    repo: Repo,
    translator: VersionTranslator,
    commit_parser: CommitParser,
    prerelease: bool = False,
) -> Version:
    # Step 1. All tags, sorted descending by semver ordering rules
    all_git_tags_as_versions = sorted(
        [(t, translator.from_tag(t.name)) for t in repo.tags],
        reverse=True,
        key=lambda v: v[1],
    )
    all_full_release_tags_and_versions = [
        (t, v) for t, v in all_git_tags_as_versions if not v.is_prerelease
    ]

    # Default initial version of 0.0.0
    latest_full_release_tag, latest_full_release_version = next(
        iter(all_full_release_tags_and_versions),
        (None, translator.from_string("0.0.0")),
    )
    # TODO: if never released
    merge_bases = repo.merge_base(
        latest_full_release_tag.name, repo.active_branch.commit.hexsha
    )
    if len(merge_bases) > 1:
        raise NotImplementedError(
            "This branch has more than one merge-base with the "
            "latest release, which is not yet supported"
        )
    merge_base = merge_bases[0]

    # Step 3. Latest full release version within the history of the current branch
    # Breadth-first search the merge-base and its parent commits for one which matches
    # the tag of the latest full release tag in history
    def bfs(visited: Set[Commit], q: Queue) -> Optional[Version]:
        if q.empty():
            return

        node = q.get()
        if node in visited:
            return

        for tag, version in all_full_release_tags_and_versions:
            if tag.commit == node:
                return version

        visited.add(node)
        for parent in q.parents:
            q.add(parent)

        return bfs(visited, q)

    q = Queue()
    q.put(merge_base)
    last_full_version_in_history: Optional[str] = bfs(set(), q)
    last_full_tag_in_history = "" if last_full_version_in_history is None else last_full_version_in_history.as_tag()

    commits_since_last_full_release = repo.iter_commits(
        f"{last_full_tag_in_history or ''}..."
    )

    # Step 4. Parse each commit since the last release and find any tags that have
    # been added since then.
    parsed_levels: List[ParsedCommit] = []
    latest_version = last_full_version_in_history

    # N.B. these should be sorted so long as we iterate the commits in reverse order
    for commit in commits_since_last_full_release:
        parse_result = commit_parser.parse(commit)
        if isinstance(parse_result, ParsedCommit):
            parsed_levels.append(parse_result.bump)

        for tag, version in (
            (tag, version)
            for tag, version in all_git_tags_as_versions
            if version.is_prerelease
        ):
            if tag.commit == commit:
                latest_version = version
                break
        else:
            # If we haven't found the latest prerelease on the branch,
            # keep the outer loop going to look for it
            continue
        # If we found it in the inner loop, break the outer loop too
        break

    level_bump = max(parsed_levels, default=LevelBump.NO_RELEASE)
    if level_bump is LevelBump.NO_RELEASE:
        log.info("No release will be made")
        return latest_version

    # Step 6. Decide the version bump
    # 6a. if prerelease
    if prerelease:
        target_final_version = latest_full_release_version.finalize_version()
        diff_with_last_released_version = latest_version - last_full_version_in_history
        # 6a i) if the level_bump > the level bump introduced by any prerelease tag before
        # e.g. 1.2.4-rc.3 -> 1.3.0-rc.1
        if level_bump > diff_with_last_released_version:
            next_version = target_final_version.bump(level_bump).to_prerelease(
                token=translator.prerelease_token
            )
        # 6a ii) if level_bump <= the level bump introduced by prerelease tag
        else:
            next_version = latest_version.to_prerelease(
                token=translator.prerelease_token,
                revision=(
                    1
                    if latest_version.prerelease_token != translator.prerelease_token
                    else latest_version.prerelease_revision + 1
                ),
            )

    # 6b. if not prerelease
    else:
        # NOTE: These can actually be condensed down to the single line
        # 6b. i) if there's been a prerelease
        if latest_version.is_prerelease:
            diff_with_last_released_version = latest_version - last_full_version_in_history
            if level_bump > diff_with_last_released_version:
                next_version = latest_version.bump(level_bump).finalize_version()
            else:
                next_version = latest_version.finalize_version()

        # 6b. ii) If there's been no prerelease
        else:
            next_version = latest_version.bump(level_bump)

    return next_version
