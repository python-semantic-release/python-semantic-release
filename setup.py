import re
import sys

from setuptools import find_packages, setup


def _read_long_description():
    try:
        with open("readme.rst") as fd:
            return fd.read()
    except Exception:
        return None


with open("semantic_release/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name="python-semantic-release",
    version=version,
    url="http://github.com/relekang/python-semantic-release",
    author="Rolf Erik Lekang",
    author_email="me@rolflekang.com",
    description="Automatic Semantic Versioning for Python projects",
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
        # See https://github.com/relekang/python-semantic-release/issues/336
        # and https://github.com/relekang/python-semantic-release/pull/337
        # and https://github.com/relekang/python-semantic-release/issues/491
        "tomlkit~=0.10",
        "dotty-dict>=1.3.0,<2",
        "dataclasses==0.8; python_version < '3.7.0'",
        "packaging",
    ],
    extras_require={
        "test": [
            "coverage>=5,<6",
            "pytest>=5,<6",
            "pytest-xdist>=1,<2",
            "pytest-mock>=2,<3",
            "responses==0.13.3",
            "mock==1.3.0",
        ],
        "docs": ["Sphinx==1.3.6", "Jinja2==3.0.3"],
        "dev": ["tox", "isort", "black"],
        "mypy": ["mypy==0.982", "types-requests"],
    },
    entry_points="""
        [console_scripts]
        semantic-release=semantic_release.cli:entry
    """,
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
