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


Authentication
==============

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

.. _env-pypi_token:

``PYPI_TOKEN``
--------------
Set an API token for publishing to https://pypi.org/. Information on how to
obtain a token is given `here <https://pypi.org/help/#apitoken>`_.

See :ref:`automatic-pypi` for more about PyPI uploads.

.. note::
  If :ref:`env-pypi_password`, :ref:`env-pypi_username`, and :ref:`env-pypi_token` are not specified credentials from ``$HOME/.pypirc`` will be used.

.. _env-pypi_password:

``PYPI_PASSWORD``
-----------------
Used together with :ref:`env-pypi_username` when publishing to https://pypi.org/.

.. warning::
  You should use :ref:`env-pypi_token` instead of username and password
  authentication for the following reasons:

  - It is `strongly recommended by PyPI <https://pypi.org/help/#apitoken>`_.
  - Tokens can be given access to only a single project, which reduces the
    possible damage if it is compromised.
  - You can change your password without having to update it in CI settings.
  - If your PyPI username is the same as your GitHub and you have it set
    as a secret in a CI service, they will likely scrub it from the build
    output. This can break things, for example repository links.

.. _env-pypi_username:

``PYPI_USERNAME``
-----------------
Used together with :ref:`env-pypi_password` when publishing to https://pypi.org/.
