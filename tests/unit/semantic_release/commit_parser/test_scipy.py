from tests.unit.semantic_release.commit_parser.helper import make_commit


def test_valid_scipy_commit(
    default_scipy_parser, valid_scipy_commit, expected_response_scipy
):
    (bump, type_, _, body_parts) = expected_response_scipy
    result = default_scipy_parser.parse(make_commit(valid_scipy_commit))

    assert result.bump is bump
    assert result.type == type_
    assert len(result.descriptions) == len(body_parts)
    assert all(a == b for a, b in zip(result.descriptions, body_parts))
