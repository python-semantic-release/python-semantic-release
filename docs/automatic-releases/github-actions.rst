.. _gh_actions:

GitHub Actions
==============

There are two official GitHub Actions for Python Semantic Release:

1. :ref:`python-semantic-release/python-semantic-release@TAG <gh_actions-psr>`
    This is the main action that runs the :ref:`version <cmd-version>` CLI
    command. It is used to (1) determine the next version number, (2) stamp the
    version number, (3) run the build command, (4) build the changelog, (5) commit
    the changes, (6) tag the commit, (7) publish the commit & tag and lastly
    (8) create a GitHub release. For more information review the
    :ref:`version command documentation <cmd-version>` and see
    :ref:`below <gh_actions-psr>` for the Action configuration options.

2. :ref:`python-semantic-release/publish-action@TAG <gh_actions-publish>`
    This action is used to execute the :ref:`publish <cmd-publish>` CLI command.
    It is used to upload files, such as distribution artifacts and other assets,
    to a GitHub release.

.. note::
  These GitHub Actions are only simplified wrappers around the
  python-semantic-release CLI. Ultimately, they download and install the
  published package from PyPI so if you find that you are trying to do something
  more advanced or less common, you may need to install and use the CLI directly.

.. _gh_actions-psr:

Python Semantic Release Action
''''''''''''''''''''''''''''''

The official `Python Semantic Release GitHub Action`_ is a `GitHub Docker Action`_,
which means at the beginning of the job it will build a Docker image that contains
the Python Semantic Release package and its dependencies. It will then run the
job step inside the Docker Container. This is done to ensure that the environment
is consistent across all GitHub Runners regardless of platform. With this choice,
comes some limitations of non-configurable options like a pre-defined python
version, lack of installed build tools, and an inability to utilize caching.

The primary benefit of using the GitHub Action is that it is easy to set up and
use for most projects. We handle a lot of the git configuration under the hood,
so you don't have to handle it yourself. There are a plenty of customization
options available which are detailed individually below.

Most importantly your project's configuration file will be used as normal, as
your project will be mounted into the container for the action to use.

.. _Python Semantic Release GitHub Action: https://github.com/marketplace/actions/python-semantic-release
.. _GitHub Docker Action: https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-docker-container-action

.. seealso::

  `action.yml`__: the code definition of the action

  __ https://github.com/python-semantic-release/python-semantic-release/blob/master/action.yml

.. _gh_actions-psr-inputs:

Inputs
------

GitHub Action inputs are used for select configuration and provide the necessary
information to execute the action. The inputs are passed to the action using the
``with`` keyword in the workflow file. Many inputs will mirror the command line
options available in the :ref:`version <cmd-version>` command. This section
outlines each supported input and its purpose.

----

.. _gh_actions-psr-inputs-build:

``build``
""""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should execute the build command or not. This option is
equivalent to adding the command line switch ``--skip-build`` (when ``false``) to
the :ref:`version <cmd-version>` command. If set to ``true``, no command line switch
is passed and the default behavior of the :ref:`version <cmd-version>` is used.

**Required:** ``false``

.. note::
  If not set or set to ``true``, the default behavior is defined by the
  :ref:`version <cmd-version>` command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-skip_build` option for the :ref:`version <cmd-version>`
    command.

----

.. _gh_actions-psr-inputs-build_metadata:

``build_metadata``
""""""""""""""""""

**Type:** ``string``

Explicitly set the build metadata of the version. This is equivalent to running the command:

.. code:: shell

  semantic-release version --build-metadata <metadata>

**Required:** ``false``

.. seealso::

  - :ref:`cmd-version-option-build-metadata` option for the :ref:`version <cmd-version>` command

----

.. _gh_actions-psr-inputs-changelog:

``changelog``
"""""""""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should generate a changelog or not. This option is
equivalent to adding either ``--changelog`` (on ``true``) or ``--no-changelog``
(on ``false``) to the :ref:`version <cmd-version>` command.

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-changelog` options for the :ref:`version <cmd-version>`
    command

----

.. _gh_actions-psr-inputs-commit:

``commit``
""""""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should commit any changes to the local repository. Changes
include the version stamps, changelog, and any other files that are modified and added
to the index during the build command. This option is equivalent to adding either
``--commit`` (on ``true``) or ``--no-commit`` (on ``false``) to the
:ref:`version <cmd-version>` command.

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-commit` options for the :ref:`version <cmd-version>` command

----

.. _gh_actions-psr-inputs-directory:

``directory``
"""""""""""""

If the project is not at the root of the repository (like in monorepos), you
can specify a sub-directory to change into before running semantic-release.

**Required:** ``false``

**Default:** ``.``

----

.. _gh_actions-psr-inputs-force:

``force``
"""""""""

**Type:** ``Literal["prerelease", "patch", "minor", "major"]``

Force the next version to be a specific bump type. This is equivalent to running
the command:

.. code:: shell

    semantic-release version --<type>

    # Ex: force a patch level version bump
    semantic-release version --patch


**Required:** ``false``

.. seealso::

  - :ref:`cmd-version-option-force-level` options for the :ref:`version <cmd-version>` command

----

.. _gh_actions-psr-inputs-git_committer_email:

``git_committer_email``
"""""""""""""""""""""""

The email of the account used to commit. If customized, it must be associated
with the provided token.

**Required:** ``false``

----

.. _gh_actions-psr-inputs-git_committer_name:

``git_committer_name``
""""""""""""""""""""""

The name of the account used to commit. If customized, it must be associated
with the provided token.

**Required:** ``false``

----

.. _gh_actions-psr-inputs-github_token:

``github_token``
""""""""""""""""

The GitHub Token is essential for access to your GitHub repository to allow the
push of commits & tags as well as to create a release. Not only do you need to
provide the token as an input but you also need to ensure that the token has the
correct permissions.

The token should have the following `permissions`_:

* id-token: write
* contents: write

**Required:** ``true``

.. _permissions: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idpermissions

----

.. _gh_actions-psr-inputs-prerelease:

``prerelease``
""""""""""""""

Force the version to be a prerelease version when set to ``true``. This is equivalent
to running the command:

.. code:: shell

  semantic-release version --as-prerelease

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-as-prerelease` option for the :ref:`version <cmd-version>`
    command

----

.. _gh_actions-psr-inputs-prerelease_token:

``prerelease_token``
""""""""""""""""""""

Override any prerelease token in the configuration file with this value, if it is
a pre-release. This will override the matching release branch configuration's
``prerelease_token`` value. If you always want it to be a prerelease then you must
also set the :ref:`gh_actions-psr-inputs-prerelease` input to ``true``.

This option is equivalent to running the command:

.. code:: shell

  semantic-release version --prerelease-token <token>

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-prerelease-token` option for the :ref:`version <cmd-version>`
    command

----

.. _gh_actions-psr-inputs-push:

``push``
""""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should push any commits or tags from the local repository
to the remote repository. This option is equivalent to adding either ``--push`` (on
``true``) or ``--no-push`` (on ``false``) to the :ref:`version <cmd-version>` command.

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-push` options for the :ref:`version <cmd-version>` command

----

.. _gh_actions-psr-inputs-root_options:

``root_options``
""""""""""""""""

Additional options for the main ``semantic-release`` command, which will come
before the :ref:`version <cmd-version>` subcommand.

  **Example**

  .. code:: yaml

    - uses: python-semantic-release/python-semantic-release@v9.11.0
      with:
        root_options: "-vv --noop"

  This configuration would cause the command to be
  ``semantic-release -vv --noop version``, which would run the version command
  verbosely but in no-operation mode.

**Required:** ``false``

**Default:** ``-v``

.. seealso::

  - :ref:`Options <cmd-main-options>` for the :ref:`semantic-release <cmd-main>` command

----

.. _gh_actions-psr-inputs-ssh_public_signing_key:

``ssh_public_signing_key``
""""""""""""""""""""""""""

The public key associated with the private key used in signing a commit and tag.

**Required:** ``false``

----

.. _gh_actions-psr-inputs-ssh_private_signing_key:

``ssh_private_signing_key``
"""""""""""""""""""""""""""

The private key used to sign a commit and tag.

**Required:** ``false``

----

.. _gh_actions-psr-inputs-tag:

``tag``
"""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should create a version tag in the local repository. This
option is equivalent to adding either ``--tag`` (on ``true``) or ``--no-tag`` (on
``false``) to the :ref:`version <cmd-version>` command.

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-tag` options for the :ref:`version <cmd-version>` command

----

.. _gh_actions-psr-inputs-vcs_release:

``vcs_release``
"""""""""""""""

**Type:** ``Literal["true", "false"]``

Override whether the action should create a release on the VCS. This option is
equivalent to adding either ``--vcs-release`` (on ``true``) or ``--no-vcs-release``
(on ``false``) to the :ref:`version <cmd-version>` command.

**Required:** ``false``

.. note::
  If not set, the default behavior is defined by the :ref:`version <cmd-version>`
  command and any user :ref:`configurations <config-root>`.

.. seealso::

  - :ref:`cmd-version-option-vcs-release` options for the :ref:`version <cmd-version>`
    command

----

.. _gh_actions-psr-outputs:

Outputs
-------

The Python Semantic Release Action also provides outputs that can be used in subsequent
steps of the workflow. These outputs are used to provide information about the release
and any actions that were taken.

----

.. _gh_actions-psr-outputs-is_prerelease:

``is_prerelease``
""""""""""""""""

**Type:** ``Literal["true", "false"]``

A boolean value indicating whether the released version is a prerelease.

----

.. _gh_actions-psr-outputs-released:

``released``
""""""""""""

**Type:** ``Literal["true", "false"]``

A boolean value indicating whether a release was made.

----

.. _gh_actions-psr-outputs-version:

``version``
"""""""""""

**Type:** ``string``

The newly released SemVer version string if one was made,
otherwise the current version.

Example: ``1.2.3``

----

.. _gh_actions-psr-outputs-tag:

``tag``
"""""""

**Type:** ``string``

The Git tag corresponding to the ``version`` output but in
the tag format dictated by your configuration.

Example: ``v1.2.3``

----

.. _gh_actions-publish:

Python Semantic Release Publish Action
''''''''''''''''''''''''''''''''''''''

The official `Python Semantic Release Publish Action`_ is a `GitHub Docker Action`_, which
means at the beginning of the job it will build a Docker image that contains the Python
Semantic Release package and its dependencies. It will then run the job step inside the
Docker Container. This is done to ensure that the environment is consistent across all
GitHub Runners regardless of platform. With this choice, comes some limitations of
non-configurable options like a pre-defined python version, lack of additional 3rd party
tools, and an inability to utilize caching.

The primary benefit of using the GitHub Action is that it is easy to set up and use for
most projects. We handle some additional configuration under the hood, so you don't have
to handle it yourself. We do however provide a few customization options which are detailed
individually below.

Most importantly your project's configuration file will be used as normal, as your project
will be mounted into the container for the action to use.

If you have issues with the action, please open an issue on the
`python-semantic-release/publish-action`_ repository.

.. _Python Semantic Release Publish Action: https://github.com/marketplace/actions/python-semantic-release-publish

.. seealso::

  - `action.yml`__: the code definition for the publish action

  __ https://github.com/python-semantic-release/publish-action/blob/main/action.yml

.. _gh_actions-publish-inputs:

Inputs
------

GitHub Action inputs are used for select configuration and provide the necessary
information to execute the action. The inputs are passed to the action using the
``with`` keyword in the workflow file. Many inputs will mirror the command line
options available in the :ref:`publish <cmd-publish>` command and others will be
specific to adjustment of the action environment. This section outlines each
supported input and its purpose.

----

.. _gh_actions-publish-inputs-directory:

``directory``
"""""""""""""

If the project is not at the root of the repository (like in monorepos), you
can specify a sub-directory to change into before running semantic-release.

**Required:** ``false``

**Default:** ``.``

----

.. _gh_actions-publish-inputs-github_token:

``github_token``
""""""""""""""""

The GitHub Token is essential for access to your GitHub repository to allow the
publish of assets to a release. Not only do you need to provide the token as an
input but you also need to ensure that the token has the correct permissions.

The token should have the following `permissions`_:

* ``contents: write``: Required for modifying a GitHub Release

**Required:** ``true``

.. _permissions: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idpermissions

----

.. _gh_actions-publish-inputs-root_options:

``root_options``
""""""""""""""""

Additional options for the main ``semantic-release`` command, which will come
before the :ref:`publish <cmd-publish>` subcommand.

  **Example**

  .. code:: yaml

    - uses: python-semantic-release/publish-action@v9.8.9
      with:
        root_options: "-vv --noop"

  This configuration would cause the command to be
  ``semantic-release -vv --noop publish``, which would run the publish command
  verbosely but in no-operation mode.

**Required:** ``false``

**Default:** ``-v``

.. seealso::

  - :ref:`Options <cmd-main-options>` for the :ref:`semantic-release <cmd-main>`
    command

----

.. _gh_actions-publish-inputs-tag:

``tag``
"""""""

**Type:** ``string``

The tag corresponding to the GitHub Release that the artifacts should be published
to. This option is equivalent to running the command:

.. code:: shell

  semantic-release publish --tag <tag>

Python Semantic Release will automatically determine the latest release if no
``--tag`` option is provided.

**Required:** ``false``

.. seealso::

  - :ref:`cmd-publish-option-tag` option for the :ref:`publish <cmd-publish>` command

----

.. _gh_actions-publish-outputs:

Outputs
-------

There are no outputs provided by the Python Semantic Release Publish Action at this time.

.. note::
  If you would like outputs to be provided by this action, please open an issue
  on the `python-semantic-release/publish-action`_ repository.

.. _python-semantic-release/publish-action: https://github.com/python-semantic-release/publish-action/issues

----

.. _gh_actions-examples:

Examples
''''''''

Common Workflow Example
-----------------------

The following is a common workflow example that uses both the Python Semantic Release Action
and the Python Semantic Release Publish Action. This workflow will run on every push to the
``main`` branch and will create a new release upon a successful version determination. If a
version is released, the workflow will then publish the package to PyPI and upload the package
to the GitHub Release Assets as well.

.. code:: yaml

    name: Continuous Delivery

    on:
      push:
        branches:
          - main

    jobs:
      release:
        runs-on: ubuntu-latest
        concurrency: release

        permissions:
          id-token: write
          contents: write

        steps:
          # Note: we need to checkout the repository at the workflow sha in case during the workflow
          # the branch was updated. To keep PSR working with the configured release branches,
          # we force a checkout of the desired release branch but at the workflow sha HEAD.
          - name: Setup | Checkout Repository at workflow sha
            uses: actions/checkout@v4
            with:
              fetch-depth: 0
              ref: ${{ github.sha }}

          - name: Setup | Force correct release branch on workflow sha
            run: |
              git checkout -B ${{ github.ref_name }} ${{ github.sha }}

          - name: Action | Semantic Version Release
            id: release
            # Adjust tag with desired version if applicable.
            uses: python-semantic-release/python-semantic-release@v9.11.0
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }}
              git_committer_name: "github-actions"
              git_committer_email: "actions@users.noreply.github.com"

          - name: Publish | Upload package to PyPI
            uses: pypa/gh-action-pypi-publish@v1
            if: steps.release.outputs.released == 'true'

          - name: Publish | Upload to GitHub Release Assets
            uses: python-semantic-release/publish-action@v9.8.9
            if: steps.release.outputs.released == 'true'
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }}
              tag: ${{ steps.release.outputs.tag }}

.. important::
  The `concurrency`_ directive is used on the job to prevent race conditions of more than
  one release job in the case if there are multiple pushes to ``main`` in a short period
  of time.

.. warning::
  You must set ``fetch-depth`` to 0 when using ``actions/checkout@v4``, since
  Python Semantic Release needs access to the full history to build a changelog
  and at least the latest tags to determine the next version.

.. warning::
  The ``GITHUB_TOKEN`` secret is automatically configured by GitHub, with the
  same permissions role as the user who triggered the workflow run. This causes
  a problem if your default branch is protected to specific users.

  You can work around this by storing an administrator's Personal Access Token
  as a separate secret and using that instead of ``GITHUB_TOKEN``. In this
  case, you will also need to pass the new token to ``actions/checkout`` (as
  the ``token`` input) in order to gain push access.

.. _concurrency: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idconcurrency

Version Overrides Example
-------------------------

In the case where you want to provide multiple command line options to the
:ref:`version <cmd-version>` command, you provide them through the ``with``
directive in the workflow file. In this example, we want to force a patch
version bump, not produce a changelog, and provide specialized build
metadata. As a regular CLI command, this would look like:

.. code:: shell

  semantic-release version --patch --no-changelog --build-metadata abc123

The equivalent GitHub Action configuration would be:

.. code:: yaml

  # snippet

  - name: Action | Semantic Version Release
    # Adjust tag with desired version if applicable.
    uses: python-semantic-release/python-semantic-release@v9.11.0
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      force: patch
      changelog: false
      build_metadata: abc123

.. _gh_actions-monorepo:

Actions with Monorepos
''''''''''''''''''''''

While ``python-semantic-release`` does **NOT** have full monorepo support, if you
have multiple projects stored within a single repository (or your project is
not at the root of the repository), you can pass the
:ref:`directory <gh_actions-psr-inputs-directory>` input to the action to change
directory before semantic-release execution.

For multiple packages, you would need to run the action multiple times, to release
each project. The following example demonstrates how to release two projects in
a monorepo.

The ``directory`` input directive is also available for the Python Semantic Release
Publish Action.

.. code:: yaml

   - name: Release Project 1
     uses: python-semantic-release/python-semantic-release@v9.11.0
     with:
       directory: ./project1
       github_token: ${{ secrets.GITHUB_TOKEN }}

   - name: Release Project 2
     uses: python-semantic-release/python-semantic-release@v9.11.0
     with:
       directory: ./project2
       github_token: ${{ secrets.GITHUB_TOKEN }}
