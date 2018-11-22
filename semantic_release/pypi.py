"""PyPI
"""
from invoke import run
from twine import settings
from twine.commands import upload as twine_upload


def upload_to_pypi(
        dists: str = 'sdist bdist_wheel',
        username: str = None,
        password: str = None,
        skip_existing: bool = False
):
    """Creates the wheel and uploads to pypi with twine.

    :param dists: The dists string passed to setup.py. Default: 'bdist_wheel'
    :param username: PyPI account username string
    :param password: PyPI account password string
    :param skip_existing: Continue uploading files if one already exists. (Only valid when
        uploading to PyPI. Other implementations may not support this.)
    """
    run('python setup.py {}'.format(dists))
    twine_upload.upload(
        settings.Settings(
            username=username,
            password=password,
            skip_existing=skip_existing,
        ),
        ['dist/*'],
    )
    run('rm -rf build dist')
