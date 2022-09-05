import logging
from typing import List, Callable, TypeVar, Generic, Iterator, Any, Optional

from git import Repo, Commit, BadName

from semantic_release.commit_parser.token import ParseResult, ParsedCommit, ParseError
from semantic_release.errors import UnknownCommitMessageStyleError
from semantic_release.version import Version, VersionTranslator

log = logging.getLogger(__name__)


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
# bump = max(
#     res.bump for res in CommitStream(
#         repo.commits, parser=commit_parser, include_parse_errors = False
#     )[translator.to_tag(version_history[0]) :]
# )


_R = TypeVar("_R", bound=ParseResult)


def _ident(x: _R) -> _R:
    """
    Default for use in CommitStream to just iterate over a repo's commits
    """
    return x


class CommitStream(Generic[_R]):
    """
    Iterable class to parse individual commits with a commit parser
    """

    def __init__(
        self,
        repo: Repo,
        commit_parser: Callable[[Commit], _R] = _ident,
        include_parse_errors: bool = True,
    ) -> None:
        self.repo = repo
        self.commit_parser = commit_parser
        self.include_parse_errors = include_parse_errors

    def _make_iterator(self, it: Iterator[_R]) -> Iterator[_R]:
        for commit in it:
            res = self.commit_parser(commit)
            if not self.include_parse_errors and isinstance(res, ParseError):
                continue
            yield res

    def __iter__(self) -> Iterator[_R]:
        return self._make_iterator(self.repo.iter_commits())

    def filter_parse_errors(self) -> Iterator[ParseResult]:
        if not self.include_parse_errors:
            return self
        return self.__class__(self.repo, self.commit_parser, include_parse_errors=False)

    def __getitem__(self, item: Any) -> Iterator[_R]:
        if not isinstance(item, slice):
            raise TypeError(f"Expected slice, got {item!r}")

        def _is_valid_ref(ref: Optional[str]) -> bool:
            try:
                self.repo.commit(ref)
                return True
            except BadName:
                return False

        from_rev = "" if not (item.start and _is_valid_ref(item.start)) else item.start
        to_rev = "" if not (item.stop and _is_valid_ref(item.stop)) else item.stop

        if not (from_rev or to_rev):
            # We consider the whole history
            return iter(self)

        rev = f"{from_rev}...{to_rev}"
        return self._make_iterator(self.repo.iter_commits(rev))
