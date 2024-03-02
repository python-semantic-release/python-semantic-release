from datetime import datetime

A_FULL_VERSION_STRING = "1.11.567"
A_PRERELEASE_VERSION_STRING = "2.3.4-dev.23"
A_FULL_VERSION_STRING_WITH_BUILD_METADATA = "4.2.3+build.12345"

EXAMPLE_REPO_OWNER = "example_owner"
EXAMPLE_REPO_NAME = "example_repo"
EXAMPLE_HVCS_DOMAIN = "example.com"

SUCCESS_EXIT_CODE = 0

TODAY_DATE_STR = datetime.now().strftime("%Y-%m-%d")
"""Date formatted as how it would appear in the changelog (Must match local timezone)"""

COMMIT_MESSAGE = "{version}\n\nAutomatically generated by python-semantic-release\n"

# Different in-scope commits that produce a certain release type
ANGULAR_COMMITS_PATCH = [
    "fix: something annoying\n",
    "fixup the bugfix\n",
    "oops it broke again\n",
    "fix\n",
    "fix\n",
    "fix\n",
    "fix\n",
    "fix: release the bugfix-fix\n",
]
ANGULAR_COMMITS_MINOR = [
    "feat: something special\n",
    "fix: needed a tweak\n",
    "tweaked again\n",
    "tweaked again\n",
    "tweaked again\n",
    "fix\n",
    "fix\n",
    "feat: last minute rush order\n",
]
# Take previous commits and insert a breaking change
ANGULAR_COMMITS_MAJOR = ANGULAR_COMMITS_MINOR.copy()
ANGULAR_COMMITS_MAJOR.insert(
    4, "fix!: big change\n\nBREAKING CHANGE: reworked something for previous feature\n"
)

EMOJI_COMMITS_PATCH = [
    ":bug: something annoying\n",
    "fixup the bugfix\n",
    "oops it broke again\n",
    "fix\n",
    "fix\n",
    "fix\n",
    "fix\n",
    "fix\n",
    ":bug: release the bugfix-fix\n",
]
EMOJI_COMMITS_MINOR = [
    ":sparkles: something special\n",
    ":sparkles::pencil: docs for something special\n",
    ":bug: needed a tweak\n",
    "tweaked again\n",
    "tweaked again\n",
    "tweaked again\n",
    "fix\n",
    "fix\n",
    # Emoji in description should not be used to evaluate change type
    ":sparkles: last minute rush order\n\n:boom: Good thing we're 10x developers",
]
EMOJI_COMMITS_MAJOR = EMOJI_COMMITS_MINOR.copy()
EMOJI_COMMITS_MAJOR.insert(4, ":boom: Move to the blockchain")

SCIPY_FORMATTED_COMMIT_BODY_PARTS = [
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

# Note - the scipy commit testing in v7 is very comprehensive -
# fixtures for commits that should evaluate to the various scopes
# are in tests/fixtures/scipy


TAG_COMMITS_PATCH = [
    ":nut_and_bolt: something annoying\n",
    "fixup the bugfix\n",
    "oops it broke again\n",
    "fix\n",
    "fix\n",
    "fix\n",
    "fix\n",
    ":persevere: fix\n",
    ":nut_and_bolt: release the bugfix-fix\n",
]
TAG_COMMITS_MINOR = [
    ":sparkles: something special\n",
    ":nut_and_bolt: needed a tweak\n",
    "tweaked again\n",
    "tweaked again\n",
    "tweaked again\n",
    "fix\n",
    "fix\n",
    ":sparkles: last minute rush order\n",
]
TAG_COMMITS_MAJOR = TAG_COMMITS_MINOR.copy()
TAG_COMMITS_MAJOR.insert(
    4,
    ":nut_and_bolt: big change\n\nBREAKING CHANGE: reworked something for previous "
    "feature\n",
)

EXAMPLE_PROJECT_NAME = "example"
EXAMPLE_PROJECT_VERSION = "0.0.0"

# Uses the internal defaults of semantic-release unless otherwise needed for testing
# modify the pyproject toml as necessary for the test using update_pyproject_toml()
# and derivative fixtures
EXAMPLE_PYPROJECT_TOML_CONTENT = rf"""
[tool.poetry]
name = "{EXAMPLE_PROJECT_NAME}"
version = "{EXAMPLE_PROJECT_VERSION}"
description = "Just an example"
license = "MIT"
authors = ["semantic-release <not-a.real@email.com>"]
readme = "README.md"
classifiers = [
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only"
]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.semantic_release]
version_variables = [
    "src/{EXAMPLE_PROJECT_NAME}/_version.py:__version__",
]
version_toml = ["pyproject.toml:tool.poetry.version"]
"""

EXAMPLE_SETUP_CFG_CONTENT = rf"""
[metadata]
name = example
version = {EXAMPLE_PROJECT_VERSION}
description = Just an example really
long_description = file: README.md
long_description_content_type = text/markdown
author = semantic-release
author_email = not-a.real@email.com
url = https://github.com/python-semantic-release/python-semantic-release
python_requires = >=3.7


[options]
zip_safe = True
include_package_data = True
packages = find:
install_requires =
    PyYAML==6.0
    pydantic==1.9.0

[options.extras_require]
dev =
    tox
    twine==3.1.1

test =
    pytest
    pytest-cov
    pytest-mock
    pytest-aiohttp

lint =
    flake8
    black>=22.6.0
    isort>=5.10.1

[options.packages.find]
exclude =
    test*

[bdist_wheel]
universal = 1

[coverage:run]
omit = */tests/*

[tools:pytest]
python_files = tests/test_*.py tests/**/test_*.py

[isort]
skip = .tox,venv
default_section = THIRDPARTY
known_first_party = {EXAMPLE_PROJECT_NAME},tests
multi_line_output=3
include_trailing_comma=True
force_grid_wrap=0
use_parentheses=True
line_length=88

[flake8]
max-line-length = 88
"""

EXAMPLE_SETUP_PY_CONTENT = rf"""
import re
import sys

from setuptools import find_packages, setup


def _read_long_description():
    try:
        with open("readme.rst") as fd:
            return fd.read()
    except Exception:
        return None


with open("{EXAMPLE_PROJECT_NAME}/_version.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name="{EXAMPLE_PROJECT_NAME}",
    version="{EXAMPLE_PROJECT_VERSION}",
    url="http://github.com/python-semantic-release/python-semantic-release",
    author="semantic-release",
    author_email="not-a.real@email.com",
    description="Just an example",
    long_description=_read_long_description(),
    packages=find_packages(exclude=("tests",)),
    license="MIT",
    install_requires=[
        "click>=7,<9",
        "click_log>=0.3,<1",
        "gitpython>=3.0.8,<4",
        "invoke>=1.4.1,<2",
        "semver>=2.10,<3",
        "twine>=3,<4",
        "requests>=2.25,<3",
        "wheel",
        "python-gitlab>=2,<4",
        # tomlkit used to be pinned to 0.7.0
        # See https://github.com/python-semantic-release/python-semantic-release/issues/336
        # and https://github.com/python-semantic-release/python-semantic-release/pull/337
        # and https://github.com/python-semantic-release/python-semantic-release/issues/491
        "tomlkit~=0.10",
        "dotty-dict>=1.3.0,<2",
        "dataclasses==0.8; python_version < '3.7.0'",
        "packaging",
    ],
    extras_require={{
        "test": [
            "coverage>=5,<6",
            "pytest>=5,<6",
            "pytest-xdist>=1,<2",
            "pytest-mock>=2,<3",
            "pytest-lazy-fixture~=0.6.3",
            "responses==0.13.3",
            "mock==1.3.0",
        ],
        "docs": ["Sphinx==1.3.6", "Jinja2==3.0.3"],
        "dev": ["tox", "isort", "black"],
        "mypy": ["mypy", "types-requests"],
    }},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
"""

EXAMPLE_CHANGELOG_MD_CONTENT = r"""
# CHANGELOG.md

## This is an example changelog

## v1.0.0
* Various bugfixes, security enhancements
* Extra cookies to enhance your experience
* ~Removed~ simplified cookie opt-out handling logic
"""

EXAMPLE_RELEASE_NOTES_TEMPLATE = r"""## What's Changed
{% for type_, commits in release["elements"] | dictsort %}
### {{ type_ | capitalize }}
{%- if type_ != "unknown" %}
{% for commit in commits %}
* {{ commit.commit.summary.rstrip() }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{%- endfor %}{% endif %}{% endfor %}
"""  # noqa: E501

RELEASE_NOTES = "# Release Notes"
