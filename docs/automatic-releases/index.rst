.. _automatic:

Automatic Releases
------------------

The key point with using this package is to automate your releases and stop worrying about
version numbers. Different approaches to automatic releases and publishing with the help of
this package can be found below. Using a CI is the recommended approach.

.. _automatic-guides:

Guides
^^^^^^

.. toctree::
    travis
    github-actions
    cronjobs

.. _automatic-checks:

Environment checks
~~~~~~~~~~~~~~~~~~
On publish, a few environment checks will run. Below are descriptions of what the different checks
do and under what condition they will run.

frigg
^^^^^
*Condition:* Environment variable ``FRIGG`` is ``'true'``

Checks for frigg to ensure that the build is not a pull-request and on the correct branch.
The branch check, checks against the branch that frigg said it checked out, not the current
branch.

semaphore
^^^^^^^^^
*Condition:* Environment variable ``SEMAPHORE`` is ``'true'``

Checks for semaphore to ensure that the build is not a pull-request and on the correct branch.
The branch check, checks against the branch that semaphore said it checked out, not the current
branch. It also checks that the thread state is not failure.

travis
^^^^^^
*Condition:* Environment variable ``TRAVIS`` is ``'true'``

Checks for travis to ensure that the build is not a pull-request and on the correct branch.
The branch check, checks against the branch that travis said it checked out, not the current
branch.

CircleCI
^^^^^^^^
*Condition:* Environment variable ``CIRCLECI`` is ``'true'``

Checks for circle-ci to ensure that the build is not a pull-request and on the correct branch.
The branch check, checks against the branch that circle-ci said it checked out, not the current
branch.

GitLab CI
^^^^^^^^^
*Condition:* Environment variable ``GITLAB_CI`` is ``'true'``

Checks for gitlab-ci to ensure that the build is on the correct branch.
The branch check, checks against the branch that gitlab-ci said it checked out, not the current
branch.

Jenkins
^^^^^^^
*Condition:* Environment variable ``JENKINS_URL`` is set.

Determines the branch name from either the environment variable ``BRANCH_NAME``
or the environment variable ``GIT_BRANCH``, and checks to ensure that the build is on
the correct branch. Also, if ``CHANGE_ID`` is set, meaning it is a PR from a multi-branch
pipeline, the build will not be automatically released.

Publish with CI
~~~~~~~~~~~~~~~
Add ``semantic-release version`` and ``semantic-release publish`` as after success tasks on your
preferred Continuous Integration service. Ensure that you have configured the CI so that it can
upload to an artifact repository and push to git and it should be ready to roll.

.. seealso::
  - `GitLab pypi-repository <https://docs.gitlab.com/ee/user/packages/pypi_repository/>`_ - GitLab example configuration
  - `The .pypirc file <https://packaging.python.org/specifications/pypirc/>`_ - ``~/.pypirc`` documentation

.. _automatic-github:

Configuring push to Github
^^^^^^^^^^^^^^^^^^^^^^^^^^
In order to push to Github and post the changelog to Github the environment variable
:ref:`GH_TOKEN <index-creating-vcs-releases>` has to be set. It needs access to the
``public_repo`` scope for public repositories and ``repo`` for private repositories.


