GitHub Action for Python Semantic Release
=========================================

Inputs
------

+-------------------+-------------------------------------------------+
| Input             | Description                                     |
+===================+=================================================+
| ``github_token``  | **Required.** The GitHub token used to push     |
|                   | release notes and new commits/tags created by   |
|                   | the tool. Usually                               |
|                   | ``${{ secrets.GITHUB_TOKEN }}``.                |
+-------------------+-------------------------------------------------+
| ``pypi_username`` | **Required unless upload_to_pypi is false in    |
|                   | setup.cfg.** Username with project access to    |
|                   | push to PyPi.                                   |
+-------------------+-------------------------------------------------+
| ``pypi_password`` | **Required unless upload_to_pypi is false in    |
|                   | setup.cfg.** Password to the account specified  |
|                   | in ``pypi_username``.                           |
+-------------------+-------------------------------------------------+
| ``directory``     | A sub-directory to ``cd`` into before running.  |
|                   | Defaults to the root of the repository.         |
+-------------------+-------------------------------------------------+

Further options are **required** to be configured in either
``setup.cfg`` or ``pyproject.toml`` as documented `here`_.

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
         uses: relekang/python-semantic-release@v4
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           pypi_username: <ADD YOUR USERNAME HERE>
           pypi_password: ${{ secrets.PYPI_PASSWORD }}

``PYPI_PASSWORD`` should be set as a secret on your repository's
settings page. It is safe to include your username directly in the
configuration, although you could also set it as a secret if you wish.
The ``GITHUB_TOKEN`` secret is automatically configured by Actions.

Multiple Projects
~~~~~~~~~~~~~~~~~

If you have multiple projects stored within a single repository (or your
project is not at the root of the repository), you can pass the
``directory`` input. The step can be called multiple times to release
multiple projects.

.. code:: yaml

   - name: Release Project 1
     uses: relekang/python-semantic-release@v4
     with:
       directory: ./project1
       github_token: ${{ secrets.GITHUB_TOKEN }}
       pypi_username: <ADD YOUR USERNAME HERE>
       pypi_password: ${{ secrets.PYPI_PASSWORD }}

   - name: Release Project 2
     uses: relekang/python-semantic-release@v4
     with:
       directory: ./project2
       github_token: ${{ secrets.GITHUB_TOKEN }}
       pypi_username: <ADD YOUR USERNAME HERE>
       pypi_password: ${{ secrets.PYPI_PASSWORD }}

Note that the release notes posted to GitHub will not currently
distinguish which project they are from (see `this issue`_).

.. _here: https://python-semantic-release.readthedocs.io/en/latest/configuration.html
.. _this issue: https://github.com/relekang/python-semantic-release/issues/168
