import re
from setuptools import find_packages, setup
import sys


def _read_long_description():
    try:
        with open('readme.rst') as fd:
            return fd.read()
    except Exception:
        return None


with open('semantic_release/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

with open('requirements/base.txt', 'r') as fd:
    requirements = fd.read().strip().split('\n')

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

setup(
    name='python-semantic-release',
    version=version,
    url='http://github.com/relekang/python-semantic-release',
    author='Rolf Erik Lekang',
    author_email='me@rolflekang.com',
    description='Automatic semantic versioning for python projects',
    long_description=_read_long_description(),
    packages=find_packages(exclude=('tests',)),
    license='MIT',
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        semantic-release=semantic_release.cli:entry
    ''',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ]
)
