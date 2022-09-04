from typing import List

from git import Repo

from semantic_release.version import Version, VersionTranslator


def version_history(repo: Repo, translator: VersionTranslator) -> List[Version]:
    """
    Given the repository instance and a translator, return a list of Version instances
    from the Git tags, sorted in descending order according to semantic version
    specification on precedence.
    """
    return sorted((translator.from_tag(tag.name) for tag in repo.tags), reverse=True)

# commit_parser = ...
# release_scope = max(commit.scope for commit in CommitStream(repo.commits, parser=commit_parser)[version_history[0] :])
