.. _envvars:

Environment Variables
---------------------
These are the environment
.. _env-circleci:

CIRCLECI
^^^^^^^^
Used to check if Circle CI environment. See :ref:`automatic-checks`


.. _env-debug:

DEBUG
^^^^^
Set to ``*`` to get a lot of debug information.
See :ref:`debug-usage` for more.

.. _env-frigg:

FRIGG
^^^^^
Used to check if frigg environment. See :ref:`automatic-checks`


.. _env-gh_token:

GH_TOKEN
^^^^^^^^
A personal access token from github. This is used for authenticating
when pushing tags, publishing releases etc. See :ref:`automatic-github` for
usage.

To generate a token go to https://github.com/settings/tokens
and click on *Personal access token*.


.. _env-gitlab_ci:

GITLAB_CI
^^^^^^^^^
Used to check if Gitlab CI environment. See :ref:`automatic-checks`
Automatically defined in a gitlab ci environment.

GL_TOKEN
^^^^^^^^
A personal access token from gitlab. This is used for authenticating
when pushing tags, publishing releases etc...

CI_SERVER_HOST
^^^^^^^^^^^^^^
Host component of the GitLab instance URL, without protocol and port.
Example: gitlab.example.com
Automatically set in a gitlab ci environment (from version 12.1).


.. _env-pypi_password:

PYPI_PASSWORD
^^^^^^^^^^^^^
Used together with :ref:`env-pypi_username` when publishing to http://pypi.org.
See .. _automatic-pypi: for more.


.. _env-pypi_username:

PYPI_USERNAME
^^^^^^^^^^^^^
Used together with :ref:`env-pypi_password` when publishing to http://pypi.org.
See .. _automatic-pypi: for more.


.. _env-semaphore:

SEMAPHORE
^^^^^^^^^
Used to check if semaphore environment. See :ref:`automatic-checks`


.. _env-travis:

TRAVIS
^^^^^^
Used to check if travis environment. See :ref:`automatic-checks`
