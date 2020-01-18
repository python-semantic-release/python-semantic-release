"""PyPI
"""
from invoke import run

from semantic_release import ImproperConfigurationError


def upload_to_pypi(
        dists: str = 'sdist bdist_wheel',
        path: str = 'dist',
        username: str = None,
        password: str = None,
        skip_existing: bool = False,
        remove_dist: bool = True
):
    """Creates the wheel and uploads to pypi with twine.

    :param dists: The dists string passed to setup.py. Default: 'bdist_wheel'
    :param username: PyPI account username string
    :param password: PyPI account password string
    :param skip_existing: Continue uploading files if one already exists. (Only valid when
         uploading to PyPI. Other implementations may not support this.)
    """
    if username is None or password is None or username == "" or password == "":
        raise ImproperConfigurationError('Missing credentials for uploading')
    if remove_dist:
        run(f'rm -rf {path}')
    run('python setup.py {}'.format(dists))
    run(
        "twine upload -u '{}' -p '{}' {} \"{}/*\"".format(
            username,
            password,
            '--skip-existing' if skip_existing else '',
            path
        )
    )
    if remove_dist:
        run(f'rm -rf {path}')
