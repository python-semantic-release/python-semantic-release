.. _envvars:

Environment Variables
*********************

.. _env-debug:

``DEBUG``
=========
Set to ``*`` to get a lot of debug information.
See :ref:`debug-usage` for more.


CI
==

See :ref:`automatic-checks`.

.. _env-circleci:

``CIRCLECI``
------------
Used to check if this is a Circle CI environment.

.. _env-frigg:

``FRIGG``
---------
Used to check if this is a Frigg environment.

.. _env-semaphore:

``SEMAPHORE``
-------------
Used to check if this is a Semaphore environment.

.. _env-travis:

``TRAVIS``
----------
Used to check if this is a Travis CI environment.

.. _env-gitlab_ci:

``GITLAB_CI``
-------------
Used to check if this is a GitLab CI environment.

.. _env-jenkins_url:

``JENKINS_URL``
---------------
Used to check if this is a Jenkins CI environment.

``CI_SERVER_HOST``
------------------
Host component of the GitLab instance URL, without protocol and port.
Example: `gitlab.example.com`

.. note::
  Automatically set in a GitLab CI environment from version 12.1.


HVCS Authentication
===================

.. _env-gh_token:

``GH_TOKEN``
------------
A personal access token from GitHub. This is used for authenticating
when pushing tags, publishing releases etc. See :ref:`automatic-github` for
usage.

To generate a token go to https://github.com/settings/tokens
and click on *Personal access token*.

.. _env-gl_token:

``GL_TOKEN``
------------
A personal access token from GitLab. This is used for authenticating
when pushing tags, publishing releases etc.

.. _env-gitea_token:

``GITEA_TOKEN``
------------
A personal access token from Gitea. This is used for authenticating
when pushing tags, publishing releases etc.

.. _env-repository:

Artifact Repository
===================

.. _env-pypi_token:

``PYPI_TOKEN``
--------------
.. deprecated:: 7.20.0
  Please use :ref:`env-repository_password` instead

Set an API token for publishing to https://pypi.org/.

.. _env-pypi_password:

``PYPI_PASSWORD``
-----------------
.. deprecated:: 7.20.0
  Please use :ref:`env-repository_password` instead

Used together with :ref:`env-pypi_username` when publishing to https://pypi.org/.

.. _env-pypi_username:

``PYPI_USERNAME``
-----------------
.. deprecated:: 7.20.0
  Please use :ref:`env-repository_username` instead

Used together with :ref:`env-pypi_password` when publishing to https://pypi.org/.

.. _env-repository_username:

``REPOSITORY_USERNAME``
-----------------------
Used together with :ref:`env-repository_password` when publishing artifact.

.. note::
  If you use token authentication with `pypi` set this to `__token__`

.. _env-repository_password:

``REPOSITORY_PASSWORD``
-----------------------
Used together with :ref:`env-repository_username` when publishing artifact.
Also used for token when using token authentication.

.. warning::
  You should use token authentication instead of username and password
  authentication for the following reasons:

  - It is `strongly recommended by PyPI <https://pypi.org/help/#apitoken>`_.
  - Tokens can be given access to only a single project, which reduces the
    possible damage if it is compromised.
  - You can change your password without having to update it in CI settings.
  - If your PyPI username is the same as your GitHub and you have it set
    as a secret in a CI service, they will likely scrub it from the build
    output. This can break things, for example repository links.

  - Find more information on `how to obtain a token <https://pypi.org/help/#apitoken>`_.

.. _env-repository_url:

``REPOSITORY_URL``
------------------
Custom repository (package index) URL to upload the package to.
Takes precedence over :ref:`config-repository_url`

See :ref:`automatic-dist-upload` for more about uploads to custom repositories.

``TWINE_CERT``
------------------
Path to alternative CA bundle to use for SSL verification to repository. `See here for more information <https://twine.readthedocs.io/en/stable/>`