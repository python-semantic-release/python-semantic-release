import pytest

from semantic_release.errors import UnknownCommitMessageStyleError
from semantic_release.history import scipy_parser


def test_valid_scipy_commit(valid_scipy_commit, expected_response_scipy):
    (commit_tag, subject, _, body_parts) = expected_response_scipy
    result = scipy_parser(valid_scipy_commit)

    assert result[0] == commit_tag
    assert result[1] == subject
    assert len(result[3]) == len(body_parts)
    assert all(a == b for a, b in zip(result[3], body_parts))
