Setting up python-semantic-release on Travis CI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This guide expects you to have activated the repository on Travis CI.
If this is not the case, please refer to `Travis documentation`_ on how to do that.

1. Add python-semantic-release settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :doc:`../configuration` for details on how to configure python-semantic-release.
Make sure that at least you have set :ref:`config-version_variable` before continuing.

2. Add environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You will need to set up three environment variables in Travis. An easy way to do that
is to go to the settings page for your package and add them there. Make sure that the
secret toggle is set correct for the ones that are secret.

You will need to set :ref:`env-pypi_token` to a PyPI API token. Furthermore,
you need to set :ref:`env-gh_token` with a personal access token for Github. It will
need either ``repo`` or ``public_repo`` scope depending on whether the
repository is private or public.

More information on how to set environment variables can be found on
`Travis documentation on environment variables`_.

3. Add travis configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following should be added to your ``.travis.yml`` file.

.. code-block:: yaml

    after_success:
    - git config --global user.name "semantic-release (via TravisCI)"
    - git config --global user.email "semantic-release@travis"
    - pip install python-semantic-release
    - semantic-release publish


The first line tells Travis that we want to run the listed tasks after a success build.
The two first lines in after_success will configure git so that python-semantic-release
will be able to commit on Travis. The third installs the latest version of pyhon-semantic-release.
The last will run the publish command, which will publish a new version if the changes
indicates that one is due.


4. Push some changes
^^^^^^^^^^^^^^^^^^^^
You are now ready to release automatically on Travis CI on every change to your master branch.

Happy coding

.. _Travis documentation: https://docs.travis-ci.com/
.. _Travis documentation on environment variables: https://docs.travis-ci.com/user/environment-variables/#Defining-Variables-in-Repository-Settings
