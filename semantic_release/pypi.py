from invoke import run
from twine.commands import upload as twine_upload


def upload_to_pypi(dists='bdist_wheel'):
    """
    Creates the wheel and uploads to pypi with twine.

    :param dists: The dists string passed to setup.py. Default: 'bdist_wheel'
    """
    run('python setup.py {}'.format(dists))
    twine_upload.upload(dists=['dist/*'], repository='pypi', sign=False, identity=None,
                        username=None, password=None, comment=None, sign_with='gpg')
    run('rm -rf build dist')
