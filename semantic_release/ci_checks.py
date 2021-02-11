"""CI Checks
"""
import os
from typing import Callable

from semantic_release.errors import CiVerificationError


def checker(func: Callable) -> Callable:
    """
    A decorator that will convert AssertionErrors into
    CiVerificationError.

    :param func: A function that will raise AssertionError
    :return: The given function wrapped to raise a CiVerificationError on AssertionError
    """

    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except AssertionError:
            raise CiVerificationError(
                "The verification check for the environment did not pass."
            )

    return func_wrapper


@checker
def travis(branch: str):
    """
    Performs necessary checks to ensure that the travis build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get("TRAVIS_BRANCH") == branch
    assert os.environ.get("TRAVIS_PULL_REQUEST") == "false"


@checker
def semaphore(branch: str):
    """
    Performs necessary checks to ensure that the semaphore build is successful,
    on the correct branch and not a pull-request.

    :param branch:  The branch the environment should be running against.
    """
    assert os.environ.get("BRANCH_NAME") == branch
    assert os.environ.get("PULL_REQUEST_NUMBER") is None
    assert os.environ.get("SEMAPHORE_THREAD_RESULT") != "failed"


@checker
def frigg(branch: str):
    """
    Performs necessary checks to ensure that the frigg build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get("FRIGG_BUILD_BRANCH") == branch
    assert not os.environ.get("FRIGG_PULL_REQUEST")


@checker
def circle(branch: str):
    """
    Performs necessary checks to ensure that the circle build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get("CIRCLE_BRANCH") == branch
    assert not os.environ.get("CI_PULL_REQUEST")


@checker
def gitlab(branch: str):
    """
    Performs necessary checks to ensure that the gitlab build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get("CI_COMMIT_REF_NAME") == branch
    # TODO - don't think there's a merge request indicator variable


@checker
def bitbucket(branch: str):
    """
    Performs necessary checks to ensure that the bitbucket build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert os.environ.get("BITBUCKET_BRANCH") == branch
    assert not os.environ.get("BITBUCKET_PR_ID")


@checker
def jenkins(branch: str):
    """
    Performs necessary checks to ensure that the jenkins build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """

    branch_name = os.environ.get("BRANCH_NAME") or os.environ.get("GIT_BRANCH")
    assert os.environ.get("JENKINS_URL") is not None
    assert branch_name == branch
    assert not os.environ.get("CHANGE_ID")  # pull request id


def check(branch: str = "master"):
    """
    Detects the current CI environment, if any, and performs necessary
    environment checks.

    :param branch: The branch that should be the current branch.
    """
    if os.environ.get("TRAVIS") == "true":
        travis(branch)
    elif os.environ.get("SEMAPHORE") == "true":
        semaphore(branch)
    elif os.environ.get("FRIGG") == "true":
        frigg(branch)
    elif os.environ.get("CIRCLECI") == "true":
        circle(branch)
    elif os.environ.get("GITLAB_CI") == "true":
        gitlab(branch)
    elif os.environ.get("JENKINS_URL") is not None:
        jenkins(branch)
    elif "BITBUCKET_BUILD_NUMBER" in os.environ:
        bitbucket(branch)
