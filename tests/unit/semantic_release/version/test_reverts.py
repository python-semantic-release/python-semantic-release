from __future__ import annotations

from itertools import permutations

import pytest
from git import Commit, Repo

from semantic_release.version._reverts import filter_reverted_commits

from tests.fixtures.repos import repo_w_initial_commit


def make_commit(repo: Repo, number: int, message: str | bytes) -> Commit:
    return Commit(repo, binsha=number.to_bytes(20, "big"), message=message)


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
@pytest.mark.parametrize(
    "subject",
    [
        'Revert "feat: introduce a feature"',
        'Reapply "feat: introduce a feature"',
        "revert: undo a feature",
        "revert(api): undo a feature",
        "revert(api)!: undo a feature",
    ],
)
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_revert_pair_with_complete_commit_reference(subject: str, newline: str):
    """
    Given a Git or conventional revert with a complete commit reference,
    When selecting commits that affect the next version,
    Then the original and revert are excluded and unrelated commits keep their order.
    """
    repo = Repo()
    original = make_commit(repo, 1, "feat: introduce a feature")
    unrelated = make_commit(repo, 2, "fix: independent bug")
    revert = make_commit(
        repo,
        3,
        f"{subject}{newline}{newline}This reverts commit {original.hexsha}.{newline}",
    )
    assert filter_reverted_commits([revert, unrelated, original]) == [unrelated]


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
@pytest.mark.parametrize("revert_count", [1, 2, 3, 4])
def test_revert_chain_is_independent_of_traversal_order(revert_count: int):
    """
    Given a chain of reverts which can appear out of order in a merged graph,
    When selecting commits that affect the next version,
    Then an even number of reverts restores the original version impact.
    """
    repo = Repo()
    original = make_commit(repo, 1, "feat!: introduce a breaking change")
    commits = [original]
    for number in range(2, revert_count + 2):
        commits.append(
            make_commit(
                repo,
                number,
                f"revert: undo previous change\n\nThis reverts commit {commits[-1].hexsha}.",
            )
        )

    for order in permutations(commits):
        assert filter_reverted_commits(order) == (
            [original] if revert_count % 2 == 0 else []
        )


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
@pytest.mark.parametrize(
    "message",
    [
        "docs: describe reverts\n\nThis reverts commit {target}.",
        "fix: describe reverts\n\nThis reverts commit {target}.",
        "revert: mention a commit\n\nExample: This reverts commit {target}.",
        'Revert "a change"\n\n> This reverts commit {target}.',
        "revert: ambiguous references\n\nThis reverts commit {target}.\n"
        "This reverts commit {other}.",
        "revert: incomplete reference\n\nThis reverts commit 1234abcd.",
        "revert: no reference",
    ],
)
def test_unrelated_mentions_do_not_cancel_commits(message: str):
    """
    Given commit messages that do not unambiguously identify a reverted commit,
    When selecting commits that affect the next version,
    Then their version impact is retained.
    """
    repo = Repo()
    original = make_commit(repo, 1, "feat!: introduce a breaking change")
    other = make_commit(repo, 2, "fix: an independent bug")
    mention = make_commit(
        repo, 3, message.format(target=original.hexsha, other=other.hexsha)
    )
    commits = [mention, other, original]
    assert filter_reverted_commits(commits) == commits


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
def test_revert_of_commit_outside_release_window_is_retained():
    """
    Given a revert targeting a commit outside the current release window,
    When selecting commits that affect the next version,
    Then the revert is passed to the configured parser without modification.
    """
    repo = Repo()
    released = make_commit(repo, 1, "feat: released feature")
    revert = make_commit(
        repo,
        2,
        f"revert: remove feature\n\nThis reverts commit {released.hexsha}.",
    )
    assert filter_reverted_commits([revert]) == [revert]


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
def test_multiple_independent_revert_pairs_with_bytes_messages():
    """
    Given independent feature/revert pairs and byte-valued messages,
    When selecting commits that affect the next version,
    Then all canceled pairs are removed and the unrelated fix remains.
    """
    repo = Repo()
    first = make_commit(repo, 1, "feat: first")
    second = make_commit(repo, 2, "feat: second")
    fix = make_commit(repo, 3, "fix: independent")
    reverts = [
        make_commit(
            repo,
            number,
            f"revert: undo feature\n\nThis reverts commit {target.hexsha}.".encode(),
        )
        for number, target in [(4, first), (5, second)]
    ]
    assert filter_reverted_commits([*reverts, second, fix, first]) == [fix]


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
def test_malformed_reference_cycles_are_retained():
    """
    Given impossible cyclic or self-referencing revert messages,
    When selecting commits that affect the next version,
    Then no commits are silently removed and traversal terminates.
    """
    repo = Repo()
    first = make_commit(repo, 1, "")
    second = make_commit(repo, 2, "")
    third = make_commit(repo, 3, "")
    first.message = f"revert: cyclic one\n\nThis reverts commit {second.hexsha}."
    second.message = f"revert: cyclic two\n\nThis reverts commit {first.hexsha}."
    third.message = f"revert: self reference\n\nThis reverts commit {third.hexsha}."
    commits = [first, second, third]
    assert filter_reverted_commits(commits) == commits


@pytest.mark.usefixtures(repo_w_initial_commit.__name__)
def test_ambiguous_reverts_preserve_component_and_filter_independent_pair():
    """
    Given two different reverts of one target and a revert of one of those reverts,
    When selecting commits in different traversal orders,
    Then the ambiguous history is retained while an independent pair is canceled.
    """
    repo = Repo()
    original = make_commit(repo, 1, "feat: first feature")
    first = make_commit(
        repo, 2, f"revert!: remove API\n\nThis reverts commit {original.hexsha}."
    )
    second = make_commit(
        repo, 3, f"revert: remove feature\n\nThis reverts commit {original.hexsha}."
    )
    reapply = make_commit(
        repo, 4, f'Reapply "remove API"\n\nThis reverts commit {first.hexsha}.'
    )
    independent = make_commit(repo, 5, "feat: independent feature")
    independent_revert = make_commit(
        repo, 6, f"revert: independent\n\nThis reverts commit {independent.hexsha}."
    )
    preserved = {original.hexsha, first.hexsha, second.hexsha, reapply.hexsha}
    for order in permutations(
        [original, first, second, reapply, independent, independent_revert]
    ):
        assert filter_reverted_commits(order) == [
            commit for commit in order if commit.hexsha in preserved
        ]
