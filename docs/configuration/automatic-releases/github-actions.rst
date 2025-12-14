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

Included in this documentation are some recommended examples below if you want to get
started quickly. These examples are not exhaustive and you will need to adjust them
for your specific project needs especially if you are using a monorepo.

- :ref:`GitHub Actions Example Workflows <gh_actions-examples>`

- :ref:`GitHub Actions with Monorepos <gh_actions-monorepo>`

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
"""""""""

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

.. _gh_actions-psr-inputs-config_file:

``config_file``
"""""""""""""""

Path to a custom semantic-release configuration file. By default, an empty
string will look for to the ``pyproject.toml`` file in the current directory.
This is the same as passing the ``-c`` or ``--config`` parameter to semantic-release.

**Required:** ``false``

**Default:** ``""``

.. seealso::

  - :ref:`cmd-main-option-config` for the :ref:`semantic-release <cmd-main>` command

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

.. _gh_actions-psr-inputs-noop:

``no_operation_mode``
"""""""""""""""""""""

If set to true, the github action will pass the ``--noop`` parameter to
semantic-release. This will cause semantic-release to run in "no operation"
mode.

This is useful for testing the action without making any permanent changes to the repository.

**Required:** ``false``

**Default:** ``false``

.. seealso::

  - :ref:`cmd-main-option-noop` option for the :ref:`semantic-release <cmd-main>` command

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

.. important::
  This option has been removed in v10.0.0 and newer because of a command injection
  vulnerability. Please update as to v10.0.0 as soon as possible. See
  :ref:`Upgrading to v10 <upgrade_v10-root_options>` for more information.

Additional options for the main ``semantic-release`` command, which will come
before the :ref:`version <cmd-version>` subcommand.

  **Example**

  .. code:: yaml

    - uses: python-semantic-release/python-semantic-release@v9
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

.. _gh_actions-psr-inputs-strict:

``strict``
""""""""""

If set to true, the github action will pass the `--strict` parameter to
``semantic-release``.

.. seealso::

  - :ref:`cmd-main-option-strict` option for the :ref:`semantic-release <cmd-main>` command

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

.. _gh_actions-psr-inputs-verbosity:

``verbosity``
"""""""""""""

Set the verbosity level of the output as the number of ``-v``'s to pass to
``semantic-release``. 0 is no extra output, 1 is info level output, 2 is debug output, and
3 is a silly amount of debug output.

**Required:** ``false``

**Default:** ``"1"``

.. seealso::

  - :ref:`cmd-main-option-verbosity` for the :ref:`semantic-release <cmd-main>` command

----

.. _gh_actions-psr-outputs:

Outputs
-------

The Python Semantic Release Action also provides outputs that can be used in subsequent
steps of the workflow. These outputs are used to provide information about the release
and any actions that were taken.

----

.. _gh_actions-psr-outputs-commit_sha:

``commit_sha``
""""""""""""""

**Type:** ``string``

The commit SHA of the release if a release was made, otherwise an empty string.

Example upon release: ``d4c3b2a1e0f9c8b7a6e5d4c3b2a1e0f9c8b7a6e5``
Example when no release was made: ``""``

----

.. _gh_actions-psr-outputs-is_prerelease:

``is_prerelease``
"""""""""""""""""

**Type:** ``Literal["true", "false"]``

A boolean value indicating whether the released version is a prerelease.

----

.. _gh_actions-psr-outputs-link:

``link``
""""""""

**Type:** ``string``

The URL link to the release if a release was made, otherwise an empty string.

Example upon release: ``https://github.com/user/repo/releases/tag/v1.2.3``
Example when no release was made: ``""``

----

.. _gh_actions-psr-outputs-previous_version:

``previous_version``
""""""""""""""""""""

**Type:** ``string``

The previous version before the release, if a release was or will be made. If no release is detected,
this will be the current version or an empty string if no previous version exists.

----

.. _gh_actions-psr-outputs-released:

``released``
""""""""""""

**Type:** ``Literal["true", "false"]``

A boolean value indicating whether a release was made.

----

.. _gh_actions-psr-outputs-release_notes:

``release_notes``
"""""""""""""""""""

**Type:** ``string``

The release notes generated by the release, if any. If no release was made,
this will be an empty string.

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

.. _gh_actions-publish-inputs-config_file:

``config_file``
"""""""""""""""

Path to a custom semantic-release configuration file. By default, an empty
string will look for to the ``pyproject.toml`` file in the current directory.
This is the same as passing the ``-c`` or ``--config`` parameter to semantic-release.

**Required:** ``false``

**Default:** ``""``

.. seealso::

  - :ref:`cmd-main-option-config` for the :ref:`semantic-release <cmd-main>` command

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

.. _gh_actions-publish-inputs-noop:

``no_operation_mode``
"""""""""""""""""""""

If set to true, the github action will pass the ``--noop`` parameter to
semantic-release. This will cause semantic-release to run in "no operation"
mode.

This is useful for testing the action without actually publishing anything.

**Required:** ``false``

**Default:** ``false``

.. seealso::

  - :ref:`cmd-main-option-noop` option for the :ref:`semantic-release <cmd-main>` command

----

.. _gh_actions-publish-inputs-root_options:

``root_options``
""""""""""""""""

.. important::
  This option has been removed in v10.0.0 and newer because of a command injection
  vulnerability. Please update as to v10.0.0 as soon as possible. See
  :ref:`Upgrading to v10 <upgrade_v10-root_options>` for more information.

Additional options for the main ``semantic-release`` command, which will come
before the :ref:`publish <cmd-publish>` subcommand.

  **Example**

  .. code:: yaml

    - uses: python-semantic-release/publish-action@v9
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

.. _gh_actions-publish-inputs-verbosity:

``verbosity``
"""""""""""""

Set the verbosity level of the output as the number of ``-v``'s to pass to
``semantic-release``. 0 is no extra output, 1 is info level output, 2 is debug output, and
3 is a silly amount of debug output.

**Required:** ``false``

**Default:** ``"1"``

.. seealso::

  - :ref:`cmd-main-option-verbosity` for the :ref:`semantic-release <cmd-main>` command

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

The following is a simple common workflow example that uses both the Python Semantic Release Action
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

    # default: least privileged permissions across all jobs
    permissions:
      contents: read

    jobs:
      release:
        runs-on: ubuntu-latest
        concurrency:
          group: ${{ github.workflow }}-release-${{ github.ref_name }}
          cancel-in-progress: false

        permissions:
          contents: write

        steps:
          # Note: We checkout the repository at the branch that triggered the workflow.
          # Python Semantic Release will automatically convert shallow clones to full clones
          # if needed to ensure proper history evaluation. However, we forcefully reset the
          # branch to the workflow sha because it is possible that the branch was updated
          # while the workflow was running, which prevents accidentally releasing un-evaluated
          # changes.
          - name: Setup | Checkout Repository on Release Branch
            uses: actions/checkout@v4
            with:
              ref: ${{ github.ref_name }}

          - name: Setup | Force release branch to be at workflow sha
            run: |
              git reset --hard ${{ github.sha }}

          - name: Action | Semantic Version Release
            id: release
            # Adjust tag with desired version if applicable.
            uses: python-semantic-release/python-semantic-release@v10.5.3
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }}
              git_committer_name: "github-actions"
              git_committer_email: "actions@users.noreply.github.com"

          - name: Publish | Upload to GitHub Release Assets
            uses: python-semantic-release/publish-action@v10.5.3
            if: steps.release.outputs.released == 'true'
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }}
              tag: ${{ steps.release.outputs.tag }}

          - name: Upload | Distribution Artifacts
            uses: actions/upload-artifact@v4
            with:
              name: distribution-artifacts
              path: dist
              if-no-files-found: error

        outputs:
          released: ${{ steps.release.outputs.released || 'false' }}

      deploy:
        # 1. Separate out the deploy step from the publish step to run each step at
        #    the least amount of token privilege
        # 2. Also, deployments can fail, and its better to have a separate job if you need to retry
        #    and it won't require reversing the release.
        runs-on: ubuntu-latest
        needs: release
        if: ${{ needs.release.outputs.released == 'true' }}

        permissions:
          contents: read
          id-token: write

        steps:
          - name: Setup | Download Build Artifacts
            uses: actions/download-artifact@v4
            id: artifact-download
            with:
              name: distribution-artifacts
              path: dist

          # ------------------------------------------------------------------- #
          # Python Semantic Release is not responsible for publishing your      #
          # python artifacts to PyPI. Use the official PyPA publish action      #
          # instead. The following steps are an example but is not guaranteed   #
          # to work as the action is not maintained by the                      #
          # python-semantic-release team.                                       #
          # ------------------------------------------------------------------- #

          # see https://docs.pypi.org/trusted-publishers/
          - name: Publish package distributions to PyPI
            uses: pypa/gh-action-pypi-publish@@SHA1_HASH  # vX.X.X
            with:
              packages-dir: dist
              print-hash: true
              verbose: true

.. important::
  The `concurrency`_ directive is used on the job to prevent race conditions of more than
  one release job in the case if there are multiple pushes to ``main`` in a short period
  of time.

.. warning::
  The ``GITHUB_TOKEN`` secret is automatically configured by GitHub, with the
  same permissions role as the user who triggered the workflow run. This causes
  a problem if your default branch is protected to specific users.

  You can work around this by storing an administrator's Personal Access Token
  as a separate secret and using that instead of ``GITHUB_TOKEN``. In this
  case, you will also need to pass the new token to ``actions/checkout`` (as
  the ``token`` input) in order to gain push access.

.. note::
  As of v10.5.0, Python Semantic Release automatically detects and converts
  shallow clones to full clones when needed. While you can still use ``fetch-depth: 0``
  with ``actions/checkout@v4`` to fetch the full history upfront, it is no longer
  required. If you use the default shallow clone, Python Semantic Release will
  automatically fetch the full history before evaluating commits. If you are using
  an older version of PSR, you will need to unshallow the repository prior to use.

.. note::
  As of v10.5.0, the verify upstream step is no longer required as it has been
  integrated into PSR directly. If you are using an older version of PSR, you will need
  to review the older documentation for that step. See Issue `#1201`_ for more details.

.. _#1201: https://github.com/python-semantic-release/python-semantic-release/issues/1201
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
    uses: python-semantic-release/python-semantic-release@v10.5.3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      force: patch
      changelog: false
      build_metadata: abc123

.. seealso::

  - `Publish Action Manual Release Workflow`_: To maintain the Publish Action at the same
    version as Python Semantic Release, we use a Manual release workflow which forces the
    matching bump type as the root project. Check out this workflow to see how you can
    manually provide input that triggers the desired version bump.

.. _Publish Action Manual Release Workflow: https://github.com/python-semantic-release/publish-action/blob/main/.github/workflows/release.yml

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

Remember that for each release of each submodule you will then need to handle publishing
each package separately as well. This is dependent on the result of your build commands.
In the example below, we assume a simple ``build`` module command to build a ``sdist``
and wheel artifacts into the submodule's ``dist`` directory.

The ``directory`` input directive is also available for the Python Semantic Release
Publish Action.

.. code:: yaml

  jobs:

    release:

      env:
        SUBMODULE_1_DIR: project1
        SUBMODULE_2_DIR: project2

      steps:

        # ------------------------------------------------------------------- #
        # Note the use of different IDs to distinguish which submodule was    #
        # identified to be released. The subsequent actions then reference    #
        # their specific release ID to determine if a release occurred.       #
        # ------------------------------------------------------------------- #

        - name: Release submodule 1
          id: release-submod-1
          uses: python-semantic-release/python-semantic-release@v10.5.3
          with:
            directory: ${{ env.SUBMODULE_1_DIR }}
            github_token: ${{ secrets.GITHUB_TOKEN }}

        - name: Release submodule 2
          id: release-submod-2
          uses: python-semantic-release/python-semantic-release@v10.5.3
          with:
            directory: ${{ env.SUBMODULE_2_DIR }}
            github_token: ${{ secrets.GITHUB_TOKEN }}

        # ------------------------------------------------------------------- #
        # For each submodule, you will have to publish the package separately #
        # and only attempt to publish if the release for that submodule was   #
        # deemed a release (and the release was successful).                  #
        # ------------------------------------------------------------------- #

        - name: Publish | Upload package 1 to GitHub Release Assets
          uses: python-semantic-release/publish-action@v10.5.3
          if: steps.release-submod-1.outputs.released == 'true'
          with:
            directory: ${{ env.SUBMODULE_1_DIR }}
            github_token: ${{ secrets.GITHUB_TOKEN }}
            tag: ${{ steps.release-submod-1.outputs.tag }}

        - name: Publish | Upload package 2 to GitHub Release Assets
          uses: python-semantic-release/publish-action@v10.5.3
          if: steps.release-submod-2.outputs.released == 'true'
          with:
            directory: ${{ env.SUBMODULE_2_DIR }}
            github_token: ${{ secrets.GITHUB_TOKEN }}
            tag: ${{ steps.release-submod-2.outputs.tag }}

        # ------------------------------------------------------------------- #
        # Python Semantic Release is not responsible for publishing your      #
        # python artifacts to PyPI. Use the official PyPA publish action      #
        # instead. The following steps are an example but is not guaranteed   #
        # to work as the action is not maintained by the                      #
        # python-semantic-release team.                                       #
        # ------------------------------------------------------------------- #

        - name: Publish | Upload package 1 to PyPI
          uses: pypa/gh-action-pypi-publish@SHA1_HASH  # vX.X.X
          if: steps.release-submod-1.outputs.released == 'true'
          with:
            packages-dir: ${{ format('{}/dist', env.SUBMODULE_1_DIR) }}

        - name: Publish | Upload package 2 to PyPI
          uses: pypa/gh-action-pypi-publish@SHA1_HASH  # vX.X.X
          if: steps.release-submod-2.outputs.released == 'true'
          with:
            packages-dir: ${{ format('{}/dist', env.SUBMODULE_2_DIR) }}
