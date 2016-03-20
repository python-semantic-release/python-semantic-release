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
def travis(branch):
    """
    Performs necessary checks to ensure that the travis build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get('TRAVIS_BRANCH') == branch
    assert os.environ.get('TRAVIS_PULL_REQUEST') == 'false'


@checker
def semaphore(branch):
    """
    Performs necessary checks to ensure that the semaphore build is successful,
    on the correct branch and not a pull-request.

    :param branch:  The branch the environment should be running against.
    """
    assert os.environ.get('BRANCH_NAME') == branch
    assert os.environ.get('PULL_REQUEST_NUMBER') is None
    assert os.environ.get('SEMAPHORE_THREAD_RESULT') != 'failed'


@checker
def frigg(branch):
    """
    Performs necessary checks to ensure that the frigg build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get('FRIGG_BUILD_BRANCH') == branch
    assert not os.environ.get('FRIGG_PULL_REQUEST')


@checker
def circle(branch):
    """
    Performs necessary checks to ensure that the circle build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get('CIRCLE_BRANCH') == branch
    assert not os.environ.get('CI_PULL_REQUEST')


def check(branch='master'):
    """
    Detects the current CI environment, if any, and performs necessary
    environment checks.

    :param branch: The branch that should be the current branch.
    """

    if os.environ.get('TRAVIS') == 'true':
        return travis(branch)
    elif os.environ.get('SEMAPHORE') == 'true':
        return semaphore(branch)
    elif os.environ.get('FRIGG') == 'true':
        return frigg(branch)
    elif os.environ.get('CIRCLECI') == 'true':
        return circle(branch)
