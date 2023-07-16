import random
from itertools import chain, zip_longest

import pytest

from semantic_release.commit_parser.scipy import (
    ScipyCommitParser,
    ScipyParserOptions,
    tag_to_section,
)
from semantic_release.enums import LevelBump

from tests.const import SCIPY_FORMATTED_COMMIT_BODY_PARTS
from tests.util import xdist_sort_hack


@pytest.fixture
def default_scipy_parser_options():
    yield ScipyCommitParser.parser_options()


@pytest.fixture
def default_scipy_parser(default_scipy_parser_options):
    yield ScipyCommitParser(default_scipy_parser_options)


@pytest.fixture(params=tag_to_section.keys())
def scipy_tag(request):
    return request.param


@pytest.fixture(
    params=xdist_sort_hack(
        [
            "scipy.stats.qmc: centered-discrepancy optimization of a Latin hypercube",
            "inverse missing in idstn, idctn (#14479)",
            "Merge pull request #14447 from AnirudhDagar/rename_ndimage_modules",
            "Add tests for args kwarg in quad_vec",
            "badge with version of the doc in the navbar (#14132)",
            "Bump scipy from 1.7.0 to 1.7.1 (#28)",
            "avoid nan if angle=0 in RotvecRotation",
        ]
    )
)
def subject(request):
    return request.param


@pytest.fixture(params=xdist_sort_hack(SCIPY_FORMATTED_COMMIT_BODY_PARTS))
def body_parts(request):
    return request.param


@pytest.fixture()
def expected_response_scipy(
    default_scipy_parser_options, scipy_tag, subject, body_parts
):
    bump_level = default_scipy_parser_options.tag_to_level[scipy_tag]
    type_ = tag_to_section[scipy_tag]
    changelog_body = (subject, *body_parts)
    return (bump_level, type_, None, changelog_body)


def _make_scipy_commit(scipy_tag, subject, body_parts):
    body = "\n\n".join(body_parts)
    commit_msg = f"{scipy_tag}: {subject}\n\n{body}"
    return commit_msg


@pytest.fixture
def valid_scipy_commit(scipy_tag, subject, body_parts):
    return _make_scipy_commit(scipy_tag, subject, body_parts)


@pytest.fixture(
    params=xdist_sort_hack(
        [
            k
            for k, v in ScipyParserOptions().tag_to_level.items()
            if v is LevelBump.PATCH
        ]
    )
)
def scipy_commits_patch(request, subject):
    yield [
        _make_scipy_commit(request.param, subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]


@pytest.fixture(
    params=xdist_sort_hack(
        [
            k
            for k, v in ScipyParserOptions().tag_to_level.items()
            if v is LevelBump.MINOR
        ]
    )
)
def scipy_commits_minor(request, subject, default_scipy_parser_options):
    patch_tags = [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.PATCH
    ]
    patch_commits = [
        _make_scipy_commit(random.choice(patch_tags), subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]
    minor_commits = [
        _make_scipy_commit(request.param, subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]
    return list(
        chain.from_iterable(
            zip_longest(minor_commits, patch_commits, fillvalue="uninteresting")
        )
    )


@pytest.fixture(
    params=xdist_sort_hack(
        [
            k
            for k, v in ScipyParserOptions().tag_to_level.items()
            if v is LevelBump.MAJOR
        ]
    )
)
def scipy_commits_major(request, subject, default_scipy_parser_options):
    patch_tags = [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.PATCH
    ]
    minor_tags = [
        k
        for k, v in default_scipy_parser_options.tag_to_level.items()
        if v is LevelBump.MINOR
    ]
    patch_commits = [
        _make_scipy_commit(random.choice(patch_tags), subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]
    minor_commits = [
        _make_scipy_commit(random.choice(minor_tags), subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]
    major_commits = [
        _make_scipy_commit(request.param, subject, body_parts)
        for body_parts in SCIPY_FORMATTED_COMMIT_BODY_PARTS
    ]
    return list(
        chain.from_iterable(
            zip_longest(
                major_commits, minor_commits, patch_commits, fillvalue="uninteresting"
            )
        )
    )
