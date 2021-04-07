Setting up python-semantic-release on GitHub Actions
====================================================

Python Semantic Release includes a GitHub Action which runs the ``publish``
command.

Inputs
------

+--------------------+----------------------------------------------------------------------------------------+
| Input              | Description                                                                            |
+====================+========================================================================================+
| ``github_token``   | See :ref:`env-gh_token`. this is usually set to ``${{ secrets.GITHUB_TOKEN }}``.       |
+--------------------+----------------------------------------------------------------------------------------+
| ``pypi_token``     | See :ref:`env-pypi_token`.                                                             |
+--------------------+----------------------------------------------------------------------------------------+
| ``pypi_username``  | See :ref:`env-pypi_username`.                                                          |
+--------------------+----------------------------------------------------------------------------------------+
| ``pypi_password``  | See :ref:`env-pypi_password`.                                                          |
+--------------------+----------------------------------------------------------------------------------------+
| ``directory``      | A sub-directory to ``cd`` into before running. Defaults to the root of the repository. |
+--------------------+----------------------------------------------------------------------------------------+

Other options are taken from your regular configuration file.

Example Workflow
----------------

.. code:: yaml

   name: Semantic Release

   on:
     push:
       branches:
         - master

   jobs:
     release:
       runs-on: ubuntu-latest

       steps:
       - uses: actions/checkout@v2
         with:
           fetch-depth: 0

       - name: Python Semantic Release
         uses: relekang/python-semantic-release@master
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           pypi_token: ${{ secrets.PYPI_TOKEN }}

:ref:`env-pypi_token` should be set as a secret on your repository's settings page.
It is also possible to use username and password authentication in a similar
fashion.

.. warning::
  You must set `fetch-depth` to 0 when using ``actions/checkout@v2``, since
  Python Semantic Release needs access to the full history to determine whether
  a release should be made.

.. warning::
  The ``GITHUB_TOKEN`` secret is automatically configured by GitHub, with the
  same permissions as the user who triggered the workflow run. This causes
  a problem if your default branch is protected.

  You can work around this by storing an administrator's Personal Access Token
  as a separate secret and using that instead of ``GITHUB_TOKEN``. In this
  case, you will also need to pass the new token to ``actions/checkout`` (as
  the ``token`` input) in order to gain push access.

Multiple Projects
-----------------

If you have multiple projects stored within a single repository (or your
project is not at the root of the repository), you can pass the
``directory`` input. The step can be called multiple times to release
multiple projects.

.. code:: yaml

   - name: Release Project 1
     uses: relekang/python-semantic-release@master
     with:
       directory: ./project1
       github_token: ${{ secrets.GITHUB_TOKEN }}
       pypi_token: ${{ secrets.PYPI_TOKEN }}

   - name: Release Project 2
     uses: relekang/python-semantic-release@master
     with:
       directory: ./project2
       github_token: ${{ secrets.GITHUB_TOKEN }}
       pypi_token: ${{ secrets.PYPI_TOKEN }}

.. note::
  The release notes posted to GitHub will not currently distinguish which
  project they are from (see `this issue`_).

.. _this issue: https://github.com/relekang/python-semantic-release/issues/168
