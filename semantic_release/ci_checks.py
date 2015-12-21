import os

from semantic_release.errors import CiVerificationError


def checker(func):
    """
    A decorator that will convert AssertionErrors into
    CiVerificationError.

    :param func: A function that will raise AssertionError
    """

    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except AssertionError:
            raise CiVerificationError(
                'The verification check for the environment did not pass.'
            )

    return func_wrapper


@checker
def travis(branch='master'):
    """
    Performs necessary checks to ensure that the travis build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get('TRAVIS_BRANCH') == branch
    assert os.environ.get('TRAVIS_PULL_REQUEST') == 'false'


def check(branch):
    """
    Detects the current CI environment, if any, and performs necessary
    environment checks.

    :param branch: The branch that should be the current branch.
    """

    if os.environ.get('TRAVIS') == 'true':
        return travis(branch)
