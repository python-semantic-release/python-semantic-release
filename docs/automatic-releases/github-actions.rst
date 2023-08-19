.. _github-actions:

Setting up python-semantic-release on GitHub Actions
====================================================

Python Semantic Release includes a GitHub Action which runs the ``version`` and
``publish`` commands. The repository is set to ``PyPI``. You can read the full set
of inputs available, and their descriptions in the `action definition`_.

Your project's configuration file will be used as normal.

The GitHub Action provides the following outputs:

+-------------+-----------------------------------------------------------+
| Output      | Description                                               |
+-------------+-----------------------------------------------------------+
| released    | "true" if a release was made, "false" otherwise           |
+-------------+-----------------------------------------------------------+
| version     | The newly released version if one was made, otherwise     |
|             | the current version                                       |
+-------------+-----------------------------------------------------------+
| tag         | The Git tag corresponding to the "version" output. The    |
|             | format is dictated by your configuration.                 |
+-------------+-----------------------------------------------------------+

.. _action definition: https://github.com/python-semantic-release/python-semantic-release/blob/master/action.yml

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
       concurrency: release
       permissions:
         id-token: write
         contents: write

       steps:
       - uses: actions/checkout@v3
         with:
           fetch-depth: 0

       - name: Python Semantic Release
         uses: python-semantic-release/python-semantic-release@master
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}

``concurrency`` is a
`beta feature of GitHub Actions <https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idconcurrency>`_
which disallows two or more release jobs to run in parallel. This prevents race
conditions if there are multiple pushes in a short period of time.

If you would like to use Python Semantic Release to create GitHub Releases against
your repository, you will need to allow the additional ``contents: write`` permission.
More information can be found in the `permissions for GitHub Apps documentation`_

.. _permissions for GitHub Apps documentation: https://docs.github.com/en/rest/overview/permissions-required-for-github-apps?apiVersion=2022-11-28#contents

.. warning::
  You must set ``fetch-depth`` to 0 when using ``actions/checkout@v2``, since
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
     uses: python-semantic-release/python-semantic-release@master
     with:
       directory: ./project1
       github_token: ${{ secrets.GITHUB_TOKEN }}

   - name: Release Project 2
     uses: python-semantic-release/python-semantic-release@master
     with:
       directory: ./project2
       github_token: ${{ secrets.GITHUB_TOKEN }}
