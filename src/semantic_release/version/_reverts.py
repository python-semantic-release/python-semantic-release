from __future__ import annotations

from collections import Counter, defaultdict
from re import MULTILINE, compile as regexp
from typing import TYPE_CHECKING

from semantic_release.commit_parser.util import force_str

if TYPE_CHECKING:  # pragma: no cover
    from typing import Sequence

    from git.objects.commit import Commit


_REVERT_SUBJECT = regexp(
    r'^(?:(?:Revert|Reapply) ".+"|revert(?:\([^\n()]+\))?!?:[^\n]+)\r?$'
)
_REVERT_TARGET = regexp(
    r"^This reverts commit ([0-9a-f]{40}|[0-9a-f]{64})\.?\r?$", MULTILINE
)


def _find_ambiguous_reverts(targets: dict[str, str]) -> set[str]:
    # Multiple reverts of one target may have different parser bump levels.
    # Keep their entire connected history, since choosing a pair would otherwise
    # make the result depend on traversal order.
    reverts_by_target: dict[str, list[str]] = defaultdict(list)
    for commit_id, target_id in targets.items():
        reverts_by_target[target_id].append(commit_id)
    ambiguous: set[str] = set()
    pending = [
        target_id
        for target_id, reverts in reverts_by_target.items()
        if len(reverts) > 1
    ]
    while pending:
        commit_id = pending.pop()
        if commit_id in ambiguous:
            continue
        ambiguous.add(commit_id)
        pending.extend(reverts_by_target.get(commit_id, []))
        if commit_id in targets:
            pending.append(targets[commit_id])
    return ambiguous


def filter_reverted_commits(commits: Sequence[Commit]) -> list[Commit]:
    """
    Remove unreleased commit/revert pairs before computing their version impact.

    References must name a complete commit ID in the supplied release window.
    Process outer reverts before their targets so reverting a revert restores the
    original change, regardless of the history traversal order.
    """
    commit_ids = {commit.hexsha for commit in commits}
    targets: dict[str, str] = {}
    for commit in commits:
        message = force_str(commit.message)
        subject = message.partition("\n")[0]
        if not _REVERT_SUBJECT.fullmatch(subject):
            continue

        references = _REVERT_TARGET.findall(message)
        if (
            len(references) == 1
            and references[0] in commit_ids
            and references[0] != commit.hexsha
        ):
            targets[commit.hexsha] = references[0]

    ambiguous = _find_ambiguous_reverts(targets)
    targets = {
        commit_id: target_id
        for commit_id, target_id in targets.items()
        if commit_id not in ambiguous
    }

    # An original may be encountered before a later revert along another merge
    # parent. Follow the reference graph rather than relying on DFS or timestamps.
    referenced_by = Counter(targets.values())
    pending = [commit_id for commit_id in targets if not referenced_by[commit_id]]
    canceled: set[str] = set()
    while pending:
        commit_id = pending.pop()
        target_id = targets[commit_id]
        if commit_id not in canceled and target_id not in canceled:
            canceled.update((commit_id, target_id))

        referenced_by[target_id] -= 1
        if not referenced_by[target_id] and target_id in targets:
            pending.append(target_id)

    return [commit for commit in commits if commit.hexsha not in canceled]
