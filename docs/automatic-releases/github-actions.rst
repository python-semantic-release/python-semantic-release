Setting up python-semantic-release on GitHub Actions
====================================================

Python Semantic Release includes a GitHub Action which runs the ``publish``
command.

Inputs
------

+-------------------+-------------------------------------------------+
| Input             | Description                                     |
+===================+=================================================+
| ``github_token``  | **Required.** The GitHub token used to post     |
|                   | release notes and push new commits/tags created |
|                   | by Python Semantic Release.                     |
+-------------------+-------------------------------------------------+
| ``pypi_username`` | **Required unless upload_to_pypi is false.**    |
|                   | Username with access to push to PyPi.           |
+-------------------+-------------------------------------------------+
| ``pypi_password`` | **Required unless upload_to_pypi is false.**    |
|                   | Password to the account specified in            |
|                   | ``pypi_username``.                              |
+-------------------+-------------------------------------------------+
| ``directory``     | A sub-directory to ``cd`` into before running.  |
|                   | Defaults to the root of the repository.         |
+-------------------+-------------------------------------------------+

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
           pypi_username: <ADD YOUR USERNAME HERE>
           pypi_password: ${{ secrets.PYPI_PASSWORD }}

``PYPI_PASSWORD`` should be set as a secret on your repository's settings page.
It is safe to include your username directly in the configuration, although you
could also set it as a secret if you wish.

.. warning::
  You must set `fetch-depth` to 0 when using ``actions/checkout@v2``, since
  Python Semantic Release needs access to the full history to determine whether
  a release should be made.

.. warning::
  The ``GITHUB_TOKEN`` secret is automatically configured by GitHub, with the
  same permissions as the user who triggered the workflow run. This can
  sometimes cause a problem if your default branch is protected, since only
  administrators will be able to push to it without creating a pull request.

  You can work around this by a user with the necessary permissions creating a
  Personal Access Token, and storing that in a different secret.

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
       pypi_username: <ADD YOUR USERNAME HERE>
       pypi_password: ${{ secrets.PYPI_PASSWORD }}

   - name: Release Project 2
     uses: relekang/python-semantic-release@master
     with:
       directory: ./project2
       github_token: ${{ secrets.GITHUB_TOKEN }}
       pypi_username: <ADD YOUR USERNAME HERE>
       pypi_password: ${{ secrets.PYPI_PASSWORD }}

.. note::
  The release notes posted to GitHub will not currently distinguish which
  project they are from (see `this issue`_).

.. _this issue: https://github.com/relekang/python-semantic-release/issues/168
