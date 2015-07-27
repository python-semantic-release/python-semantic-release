import re
from setuptools import find_packages, setup


def _read_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst', format='markdown')
    except Exception:
        return None

version = ''
with open('semantic_release/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

setup(
    name='python-semantic-release',
    version=version,
    url='http://github.com/relekang/python-semantic-release',
    author='Rolf Erik Lekang',
    author_email='me@rolflekang.com',
    description='Automatic semantic versioning for python projects',
    long_description=_read_long_description(),
    packages=find_packages(exclude='tests'),
    license='MIT',
    install_requires=[
        'click==4.1',
    ],
    entry_points='''
        [console_scripts]
        semantic-release=semantic_release.cli:handle
    ''',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ]
)
