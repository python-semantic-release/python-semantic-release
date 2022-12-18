from __future__ import annotations

import logging
import os

import click
from git import Repo

log = logging.getLogger(__name__)


def travis(branch: str) -> None:
    """
    Performs necessary checks to ensure that the travis build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert (
        os.environ.get("TRAVIS_BRANCH") == branch
    ), f"TRAVIS_BRANCH environment variable is not {branch!r}"
    assert (
        os.environ.get("TRAVIS_PULL_REQUEST") == "false"
    ), "TRAVIS_PULL_REQUEST environment variable is not 'false'"


def semaphore(branch: str) -> None:
    """
    Performs necessary checks to ensure that the semaphore build is successful,
    on the correct branch and not a pull-request.

    :param branch:  The branch the environment should be running against.
    """
    assert (
        os.environ.get("BRANCH_NAME") == branch
    ), f"BRANCH_NAME environment_variable is not {branch!r}"
    assert (
        os.environ.get("PULL_REQUEST_NUMBER") is None
    ), "PULL_REQUEST_NUMBER environment variable is not empty"
    assert (
        os.environ.get("SEMAPHORE_THREAD_RESULT") != "failed"
    ), "SEMAPHORE_THREAD_RESULT environment variable is 'failed'"


def frigg(branch: str) -> None:
    """
    Performs necessary checks to ensure that the frigg build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert (
        os.environ.get("FRIGG_BUILD_BRANCH") == branch
    ), f"FRIGG_BUILD_BRANCH environment variable is not {branch!r}"
    assert not os.environ.get("FRIGG_PULL_REQUEST"), "FRIGG_PULL_REQUEST is not empty"


def circleci(branch: str) -> None:
    """
    Performs necessary checks to ensure that the circle build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert (
        os.environ.get("CIRCLE_BRANCH") == branch
    ), f"CIRCLE_BRANCH environment variable is not {branch!r}"
    assert not os.environ.get(
        "CI_PULL_REQUEST"
    ), "CI_PULL_REQUEST environment variable is not empty"


def gitlabci(branch: str) -> None:
    """
    Performs necessary checks to ensure that the gitlab build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert (
        os.environ.get("CI_COMMIT_REF_NAME") == branch
    ), f"CI_COMMIT_REF_NAME environment variable is not {branch!r}"
    # TODO - don't think there's a merge request indicator variable


def bitbucket(branch: str) -> None:
    """
    Performs necessary checks to ensure that the bitbucket build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """
    assert (
        os.environ.get("BITBUCKET_BRANCH") == branch
    ), f"BITBUCKET_BRANCH environment variable is not {branch!r}"
    assert not os.environ.get(
        "BITBUCKET_PR_ID"
    ), "BITBUCKET_PR_ID environment variable is not empty"


def jenkins(branch: str) -> None:
    """
    Performs necessary checks to ensure that the jenkins build is one
    that should create releases.

    :param branch: The branch the environment should be running against.
    """

    branch_name = os.environ.get("BRANCH_NAME") or os.environ.get("GIT_BRANCH")
    assert os.environ.get("JENKINS_URL") is not None
    assert (
        branch_name == branch
    ), f"BRANCH_NAME='{os.getenv('BRANCH_NAME', '')}', GIT_BRANCH='{os.getenv('GIT_BRANCH')}', expected {branch!r}"
    assert not os.environ.get(
        "CHANGE_ID"
    ), "CHANGE_ID environment variable is not empty"  # pull request id


CI_SERVICE_VERIFICATIONS = {
    "travis": travis,
    "semaphore": semaphore,
    "frigg": frigg,
    "circleci": circleci,
    "gitlabci": gitlabci,
    "jenkins": jenkins,
    "bitbucket": bitbucket,
}


@click.command(
    short_help="Verify CI environment preconditions",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
    deprecated=True,
)
@click.argument(
    "service",
    # cast to a list to make mypy happy
    type=click.Choice(list(CI_SERVICE_VERIFICATIONS), case_sensitive=False),
    required=True,
    # help="The CI environment to verify",
)
@click.pass_context
def verify_ci(ctx: click.Context, service: str) -> None:
    """
    Performs a set of validations of preconditions for the specified CI service
    """
    validation_func = CI_SERVICE_VERIFICATIONS[service]
    log.debug("validating environment for CI service %r", service)
    repo = Repo(search_parent_directories=True)
    branch = repo.active_branch.name
    try:
        validation_func(branch)
    except Exception as exc:
        ctx.fail(str(exc))
