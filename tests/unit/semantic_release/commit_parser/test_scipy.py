import pytest

from semantic_release.commit_parser.scipy import ScipyCommitParser, tag_to_section

from tests.unit.semantic_release.commit_parser.helper import make_commit


@pytest.fixture
def default_options():
    yield ScipyCommitParser.parser_options()


@pytest.fixture
def default_scipy_parser(default_options):
    yield ScipyCommitParser(default_options)


@pytest.fixture(params=tag_to_section.keys())
def scipy_tag(request):
    return request.param


@pytest.fixture(
    params=[
        "scipy.stats.qmc: centered-discrepancy optimization of a Latin hypercube",
        "inverse missing in idstn, idctn (#14479)",
        "Merge pull request #14447 from AnirudhDagar/rename_ndimage_modules",
        "Add tests for args kwarg in quad_vec",
        "badge with version of the doc in the navbar (#14132)",
        "Bump scipy from 1.7.0 to 1.7.1 (#28)",
        "avoid nan if angle=0 in RotvecRotation",
    ]
)
def subject(request):
    return request.param


@pytest.fixture(
    params=[
        # a squash merge that preserved PR commit messages
        (
            "DOC: import ropy.transform to test for numpy error",
            "DOC: lower numpy version",
            "DOC: lower numpy version further",
            "MAINT: remove debugging import",
        ),
        # empty body
        (),
        # formatted body
        (
            """Bumps [sphinx](https://github.com/sphinx-doc/sphinx) from 3.5.3 to 4.1.1.
            - [Release notes](https://github.com/sphinx-doc/sphinx/releases)
            - [Changelog](https://github.com/sphinx-doc/sphinx/blob/4.x/CHANGES)
            - [Commits](https://github.com/sphinx-doc/sphinx/commits/v4.1.1)""",
            """---
            updated-dependencies:
            - dependency-name: sphinx
            dependency-type: direct:development
            update-type: version-update:semver-major""",
        ),
        (
            "Bug spotted on Fedora, see https://src.fedoraproject.org/rpms/scipy/pull-request/22",
            "The `int[::]` annotation is used to accept non-contiguous views.",
        ),
        ("[skip azp] [skip actions]",),
    ]
)
def body_parts(request):
    return request.param


@pytest.fixture()
def expected_response_scipy(default_options, scipy_tag, subject, body_parts):
    bump_level = default_options.tag_to_level[scipy_tag]
    type_ = tag_to_section[scipy_tag]
    changelog_body = (subject, *body_parts)
    return (bump_level, type_, None, changelog_body)


@pytest.fixture()
def valid_scipy_commit(scipy_tag, subject, body_parts):
    body = "\n\n".join(body_parts)
    commit_msg = f"{scipy_tag}: {subject}\n\n{body}"
    return commit_msg


def test_valid_scipy_commit(
    default_scipy_parser, valid_scipy_commit, expected_response_scipy
):
    (bump, type_, _, body_parts) = expected_response_scipy
    result = default_scipy_parser.parse(make_commit(valid_scipy_commit))

    assert result.bump is bump
    assert result.type == type_
    assert len(result.descriptions) == len(body_parts)
    assert all(a == b for a, b in zip(result.descriptions, body_parts))
