import pytest

from semantic_release.history.parser_scipy import COMMIT_TYPES, ChangeType


@pytest.fixture(params=COMMIT_TYPES)
def scipy_type(request):
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
        list(),
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
def expected_response_scipy(scipy_type: ChangeType, subject, body_parts):
    bump_level = scipy_type.bump_level
    topic = scipy_type.section
    changelog_body = (subject, *body_parts)
    return (bump_level, topic, None, changelog_body)


@pytest.fixture()
def valid_scipy_commit(scipy_type: ChangeType, subject, body_parts):
    body = "\n\n".join(body_parts)
    commit_msg = f"{scipy_type.tag}: {subject}\n\n{body}"
    return commit_msg
