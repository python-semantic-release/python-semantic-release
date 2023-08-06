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

.. _automatic-github:

Configuring push to Github
^^^^^^^^^^^^^^^^^^^^^^^^^^
In order to push to Github and post the changelog to Github the environment variable
:ref:`GH_TOKEN <index-creating-vcs-releases>` has to be set. It needs access to the
``public_repo`` scope for public repositories and ``repo`` for private repositories.
