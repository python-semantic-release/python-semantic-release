from typing import List

from git import Repo

from semantic_release.version import Version, VersionTranslator


# TODO: actually this considers tags from all branches. While there's guaranteed to
# be a unique tag in this case, a pre-release from a branch whose merge-base is
# behind the latest release on the main branch will get a misleading version -
# say main has released 0.8.0 but the merge-base of the current branch with main
# is just after 0.3.0. Then picking the current branch up again for a prerelease will
# lead to it getting 0.8.0-dev.1 (when it should likely get 0.3.0-dev.1) - will need
# to revisit this for multibranching, it may be significantly more complex than the below.
def version_history(repo: Repo, translator: VersionTranslator) -> List[Version]:
    """
    Given the repository instance and a translator, return a list of Version instances
    from the Git tags, sorted in descending order according to semantic version
    specification on precedence.
    """
    return sorted((translator.from_tag(tag.name) for tag in repo.tags), reverse=True)

# commit_parser = ...
# release_scope = max(commit.scope for commit in CommitStream(repo.commits, parser=commit_parser)[version_history[0] :])
