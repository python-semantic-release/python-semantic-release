.. _upgrade_v8:

Upgrading to v8
===============

Python Semantic Release v8.0.0 introduced a number of breaking changes.
The internals have been changed significantly to better support highly-requested
features and to streamline the maintenance of the project.

As a result, certain things have been removed, reimplemented differently, or now
exhibit different behavior to earlier versions of Python Semantic Release. This
page is a guide to help projects to ``pip install python-semantic-release>=8.0.0`` with
fewer surprises.

.. _upgrade_v8-github-action:

Python Semantic Release GitHub Action
-------------------------------------

.. _upgrade_v8-removed-artefact-upload:

GitHub Action no longer publishes artifacts to PyPI or GitHub Releases
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Python Semantic Release no longer uploads distributions to PyPI - see
:ref:`upgrade_v8-commands-repurposed-version-and-publish`. If you are
using Python Semantic Release to publish release notes and artifacts to
GitHub releases, there is a new GitHub Action `upload-to-gh-release`_
which will perform this action for you.

This means the following workflows perform the same actions, and if you
are using the former, you will need to modify your workflow to include the
steps in the latter.

This workflow is written to use Python Semantic Release v7.33.5:

.. code:: yaml

   ---
   name: Semantic Release

   on:
     push:
       branches:
         - main

   jobs:
     release:
       runs-on: ubuntu-latest
       concurrency: release

       steps:
       - uses: actions/checkout@v3
         with:
           fetch-depth: 0

       # This action uses Python Semantic Release v7
       - name: Python Semantic Release
         uses: python-semantic-release/python-semantic-release@v7.33.5
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           repository_username: __token__
           repository_password: ${{ secrets.PYPI_TOKEN }}

The following workflow achieves the same result using Python Semantic Release v8,
the `upload-to-gh-release`_ GitHub Action, and the `pypa/gh-action-pypi-publish`_
GitHub Action:

.. code:: yaml

   ---
   name: Semantic Release

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

       steps:
       - uses: actions/checkout@v3
         with:
           fetch-depth: 0

       # This action uses Python Semantic Release v8
       - name: Python Semantic Release
         id: release
         uses: python-semantic-release/python-semantic-release@v8.7.0
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}

       - name: Publish package distributions to PyPI
         uses: pypa/gh-action-pypi-publish@v1
         # NOTE: DO NOT wrap the conditional in ${{ }} as it will always evaluate to true.
         # See https://github.com/actions/runner/issues/1173
         if: steps.release.outputs.released == 'true'

       - name: Publish package distributions to GitHub Releases
         uses: python-semantic-release/upload-to-gh-release@v8.7.0
         if: steps.release.outputs.released == 'true'
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}


.. _upload-to-gh-release: https://github.com/python-semantic-release/upload-to-gh-release
.. _pypa/gh-action-pypi-publish: https://github.com/pypa/gh-action-pypi-publish

.. _upgrade_v8-github-action-removed-pypi-token:

Removal of ``pypi_token``, ``repository_username`` and ``repository_password`` inputs
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Since the library no longer supports publishing to PyPI, the ``pypi_token``,
``repository_username`` and ``repository_password`` inputs of the GitHub action have
all been removed. See the above section for how to publish to PyPI using the official
GitHub Action from the Python Packaging Authority (PyPA).

.. _upgrade_v8-options-inputs:

Rename ``additional_options`` to ``root_options``
"""""""""""""""""""""""""""""""""""""""""""""""""

Because the purposes of the :ref:`cmd-version` and :ref:`cmd-publish` commands
have changed, the GitHub action now performs both commands in sequence. For this
reason, and because the usage of the CLI has changed, ``additional_options`` has
been renamed to ``root_options`` to reflect the fact that the options are for the
main :ref:`cmd-main` command group.

.. _upgrade_v8-commands:

Commands
--------

.. _upgrade_v8-commands-repurposed-version-and-publish:

Repurposing of ``version`` and ``publish`` commands
"""""""""""""""""""""""""""""""""""""""""""""""""""
Python Semantic Release's primary purpose is to enable automation of correct semantic
versioning for software projects. Over the years, this automation has been extended to
include other actions such as building/publishing the project and its artifacts to
artefact repositories, creating releases in remote version control systems, and writing
changelogs.

In Python Semantic Release <8.0.0, the ``publish`` command was a one-stop-shop for
performing every piece of automation provided. This has been changed - the ``version``
command now handles determining the next version, applying the changes to the project
metadata according to the configuration, writing a changelog, and committing/pushing
changes to the remote Git repository. It also handles creating a release in the remote
VCS. It does *not* publish software artifacts to remote repositories such as PyPI;
the rationale behind this decision is simply that under the hood, Python Semantic Release
used `twine`_ to upload artifacts to package indexes such as PyPI, and it's recommended
to use twine directly via the command-line. From the twine
`documentation <https://twine.readthedocs.io/en/stable/contributing.html#architectural-overview>`_:

   Twine is a command-line tool for interacting with PyPI securely over HTTPS.

As a result Python Semantic Release no longer depends on twine internals.

The ``publish`` command now handles publishing software artifacts to releases in the
remote version control system.

.. _twine: https://twine.readthedocs.io/en/stable
.. _twine upload: https://twine.readthedocs.io/en/stable/#twine-upload

To achieve a similar flow of logic such as

    1. Determine the next version
    2. Write this version to the configured metadata locations
    3. Write the changelog
    4. Push the changes to the metadata and changelog to the remote repository
    5. Create a release in the remote version control system
    6. Build a wheel
    7. Publish the wheel to PyPI
    8. Publish the distribution artifacts to the release in the remote VCS

You should run::

    semantic-release version
    twine upload dist/*  # or whichever path your distributions are placed in
    semantic-release publish

With steps 1-6 being handled by the :ref:`cmd-version` command, step 7 being left
to the developer to handle, and lastly step 8 to be handled by the
:ref:`cmd-publish` command.

.. _upgrade_v8-removed-define-option:

Removal of ``-D/--define`` command-line option
""""""""""""""""""""""""""""""""""""""""""""""

It is no longer possible to override arbitrary configuration values using the ``-D``/
``--define`` option. You should provide the appropriate values via a configuration
file using :ref:`cmd-main-option-config` or via the available command-line options.

This simplifies the command-line option parsing significantly and is less error-prone,
which has resulted in previous issues (e.g. `#600`_) with overrides on the command-line.
Some of the configuration values expected by Python Semantic Release use complex data
types such as lists or nested structures, which would be tedious and error-prone to
specify using just command-line options.

.. _#600: https://github.com/python-semantic-release/python-semantic-release/issues/600

.. _upgrade_v8-commands-no-verify-ci:

Removal of CI verifications
"""""""""""""""""""""""""""

Prior to v8, Python Semantic Release would perform some prerequisite verification
of environment variables before performing any version changes using the ``publish``
command. It's not feasible for Python Semantic Release to verify any possible CI
environment fully, and these checks were only triggered if certain environment
variables were set - they wouldn't fail locally.

These checks previously raised :py:class:``semantic_release.CiVerificationError``, and
were the only place in which this custom exception was used. Therefore, this exception
has **also** been removed from Python Semantic Release in v8.

If you were relying on this functionality, it's recommended that you add the following
shell commands *before* invoking ``semantic-release`` to verify your environment:

.. note::
   In the following, $RELEASE_BRANCH refers to the git branch against which you run your
   releases using Python Semantic Release. You will need to ensure it is set properly
   (e.g. via ``export RELEASE_BRANCH=main`` and/or replace the variable with the branch
   name you want to verify the CI environment for.

.. _upgrade_v8-commands-no-verify-ci-travis:

Travis
~~~~~~

**Condition**: environment variable ``TRAVIS=true``

**Replacement**:

.. code-block:: bash

    if ! [[
          $TRAVIS_BRANCH == $RELEASE_BRANCH  && \
          $TRAVIS_PULL_REQUEST == 'false'
        ]]; then
      exit 1
    fi


.. _upgrade_v8-commands-no-verify-ci-semaphore:

Semaphore
~~~~~~~~~

**Condition**: environment variable ``SEMAPHORE=true``

**Replacement**:

.. code-block:: bash

    if ! [[
            $BRANCH_NAME == $RELEASE_BRANCH && \
            $SEMAPHORE_THREAD_RESULT != 'failed' && \
            -n $PULL_REQUEST_NUMBER
        ]]; then
      exit 1
    fi


.. _upgrade_v8-commands-no-verify-ci-frigg:

Frigg
~~~~~

**Condition**: environment variable ``FRIGG=true``

**Replacement**:

.. code-block:: bash

    if ! [[
          $FRIGG_BUILD_BRANCH == $RELEASE_BRANCH && \
          -n $FRIGG_PULL_REQUEST
        ]]; then
      exit 1
    fi

.. _upgrade_v8-commands-no-verify-ci-circle-ci:

Circle CI
~~~~~~~~~

**Condition**: environment variable ``CIRCLECI=true``

**Replacement**:

..  code-block:: bash

    if ! [[
          $CIRCLE_BRANCH == $RELEASE_BRANCH && \
          -n $CI_PULL_REQUEST
        ]]; then
      exit 1
    fi

.. _upgrade_v8-commands-no-verify-ci-gitlab-ci:

GitLab CI
~~~~~~~~~

**Condition**: environment variable ``GITLAB_CI=true``

**Replacement**:

.. code-block:: bash

    if ! [[ $CI_COMMIT_REF_NAME == $RELEASE_BRANCH ]]; then
      exit 1
    fi

.. _upgrade_v8-commands-no-verify-ci-bitbucket:

**Condition**: environment variable ``BITBUCKET_BUILD_NUMBER`` is set

**Replacement**:

.. code-block:: bash

    if ! [[
          $BITBUCKET_BRANCH == $RELEASE_BRANCH && \
          -n $BITBUCKET_PR_ID
        ]]; then
      exit 1
    fi

.. _upgrade_v8-commands-no-verify-ci-jenkins:

Jenkins
~~~~~~~

**Condition**: environment variable ``JENKINS_URL`` is set

**Replacement**:

.. code-block:: bash

    if [[ -z $BRANCH_NAME ]]; then
      BRANCH_NAME=$BRANCH_NAME
    elif [[ -z $GIT_BRANCH ]]; then
      BRANCH_NAME=$GIT_BRANCH
    fi

    if ! [[
          $BRANCH_NAME == $RELEASE_BRANCH && \
          -n $CHANGE_ID
        ]]; then
      exit 1
    fi

.. _upgrade_v8-removed-build-status-checking:

Removal of Build Status Checking
""""""""""""""""""""""""""""""""

Prior to v8, Python Semantic Release contained a configuration option,
``check_build_status``, which would attempt to prevent a release being made
if it was possible to identify that a corresponding build pipeline was failing.
For similar reasons to those motivating the removal of
:ref:`CI Checks <upgrade_v8-commands-no-verify-ci>`, this feature has also been removed.

If you are leveraging this feature in Python Semantic Release v7, the following
bash commands will replace the functionality, and you can add these to your pipeline.
You will need to install ``jq`` and ``curl`` to run these commands; they can be easily
installed through your system's package manager, for example on Ubuntu:

.. code-block:: bash

   sudo apt update && sudo apt upgrade
   sudo apt install -y curl jq

On Windows, you can refer to the `installation guide for jq`_, and if ``curl`` is not already
installed, you can download it from `the curl website`_

.. _installation guide for jq: https://jqlang.github.io/jq/download/
.. _the curl website: https://curl.se/

.. _upgrade_v8-removed-build-status-checking-github:

GitHub
~~~~~~

.. code-block:: bash

   export RESP="$(
     curl \
        -H "Authorization: token $GITHUB_TOKEN" \
        -fSsL https://$GITHUB_API_DOMAIN/repos/$REPO_OWNER/$REPO_NAME/commits/$(git rev-parse HEAD)/status || exit 1
   )"

   if [ $(jq -r '.state' <<< "$RESP") != "success" ]; then
      echo "Build status is not success" >&2
      exit 1
   fi

Note that ``$GITHUB_API_DOMAIN`` is typically ``api.github.com`` unless you are using
GitHub Enterprise with a custom domain name.

.. _upgrade_v8-removed-build-status-checking-gitea:

Gitea
~~~~~

.. code-block:: bash

   export RESP="$(
     curl \
        -H "Authorization: token $GITEA_TOKEN" \
        -fSsL https://$GITEA_DOMAIN/repos/$REPO_OWNER/$REPO_NAME/statuses/$(git rev-parse HEAD) || exit 1
   )"

   if [ $(jq -r '.state' <<< "$RESP") != "success" ]; then
      echo "Build status is not success" >&2
      exit 1
   fi

.. _upgrade_v8-removed-build-status-checking-gitlab:

Gitlab
~~~~~~

.. code-block:: bash

   export RESP="$(
     curl \
        -H "Authorization: token $GITLAB_TOKEN" \
        -fSsL https://$GITLAB_DOMAIN/api/v4/projects/$PROJECT_ID/repository/commits/$(git rev-parse HEAD)/statuses
   )"

   for line in $(jq -r '.[] | [.name, .status, .allow_failure] | join("|")' <<<"$RESP"); do
     IFS="|" read -r job_name job_status allow_failure <<<"$line"

     if [ "$job_status" == "pending" ]; then
        echo "job $job_name is pending" >&2
        exit 1
     elif [ "$job_status" == "failed" ] && [ ! "$allow_failure" == "true" ]; then
        echo "job $job_name failed" >&2
        exit 1
     fi
  done


.. _upgrade_v8-commands-multibranch-releases:

Multibranch releases
""""""""""""""""""""

Prior to v8, Python Semantic Release would perform ``git checkout`` to switch to your
configured release branch and determine if a release would need to be made. In v8 this
has been changed - you must manually check out the branch which you would like to release
against, and if you would like to create releases against this branch you must also ensure
that it belongs to a :ref:`release group <multibranch-releases-configuring>`.

.. _upgrade_v8-commands-changelog:

``changelog`` command
"""""""""""""""""""""
A new option, :ref:`cmd-changelog-option-post-to-release-tag` has been added. If you
omit this argument on the command line then the changelog rendering process, which is
described in more detail at :ref:`changelog-templates-template-rendering`, will be
triggered, but the new changelog will not be posted to any release.
If you use this new command-line option, it should be set to a tag within the remote
which has a corresponding release.
For example, to update the changelog and post it to the release corresponding to the
tag ``v1.1.4``, you should run::

    semantic-release changelog --post-to-release-tag v1.1.4

.. _upgrade_v8-changelog-customization:

Changelog customization
"""""""""""""""""""""""

A number of options relevant to customizing the changelog have been removed. This is
because Python Semantic Release now supports authoring a completely custom `Jinja`_
template with the contents of your changelog.
Historically, the number of options added to Python Semantic Release in order to
allow this customization has grown significantly; it now uses templates in order to
fully open up customizing the changelog's appearance.

.. _Jinja: https://jinja.palletsprojects.com/en/3.1.x/


.. _upgrade_v8-configuration:

Configuration
-------------

The configuration structure has been completely reworked, so you should read
:ref:`configuration` carefully during the process of upgrading to v8+. However,
some common pitfalls and potential sources of confusion are summarized here.

.. _upgrade_v8-configuration-setup-cfg-unsupported:

``setup.cfg`` is no longer supported
""""""""""""""""""""""""""""""""""""

Python Semantic Release no longer supports configuration via ``setup.cfg``. This is
because the Python ecosystem is centering around ``pyproject.toml`` as universal tool
and project configuration file, and TOML allows expressions via configuration, such as
the mechanism for declaring configuration via environment variables, which introduce
much greater complexity to support in the otherwise equivalent ``ini``-format
configuration.

You can use :ref:`cmd-generate-config` to generate new-format configuration that can
be added to ``pyproject.toml``, and adjust the default settings according to your
needs.

.. warning::

   If you don't already have a ``pyproject.toml`` configuration file, ``pip`` can
   change its behavior once you add one, as a result of `PEP-517`_. If you find
   that this breaks your packaging, you can add your Python Semantic Release
   configuration to a separate file such as ``semantic-release.toml``, and use
   the :ref:`--config <cmd-main-option-config>` option to reference this alternative
   configuration file.

   More detail about this issue can be found in this `pip issue`_.

.. _PEP-517: https://peps.python.org/pep-0517/#evolutionary-notes
.. _pip issue: https://github.com/pypa/pip/issues/8437#issuecomment-805313362


.. _upgrade_v8-commit-parser-options:

Commit parser options
"""""""""""""""""""""

Options such as ``major_emoji``, ``parser_angular_patch_types`` or
``parser_angular_default_level_bump`` have been removed. Instead, these have been
replaced with a single set of recognized commit parser options, ``allowed_tags``,
``major_tags``, ``minor_tags``, and ``patch_tags``, though the interpretation of
these is up to the specific parsers in use. You can read more detail about using
commit parser options in :ref:`commit_parser_options <config-commit_parser_options>`,
and if you need to parse multiple commit styles for a single project it's recommended
that you create a parser following :ref:`commit_parser-custom_parser` that
is tailored to the specific needs of your project.

.. _upgrade_v8-version-variable-rename:

``version_variable``
""""""""""""""""""""

This option has been renamed to :ref:`version_variables <config-version_variables>`
as it refers to a list of variables which can be updated.

.. _upgrade_v8-version-pattern-removed:

``version_pattern``
"""""""""""""""""""

This option has been removed. It's recommended to use an alternative tool to perform
substitution using arbitrary regular expressions, such as ``sed``.
You can always use Python Semantic Release to identify the next version to be created
for a project and store this in an environment variable like so::

    export VERSION=$(semantic-release version --print)

.. _upgrade_v8-version-toml-type:

``version_toml``
""""""""""""""""

This option will no longer accept a string or comma-separated string of version
locations to be updated in TOML files. Instead, you must supply a ``List[str]``.
For existing configurations using a single location in this option, you can
simply wrap the value in ``[]``:

.. code-block:: toml

   # Python Semantic Release v7 configuration
   [tool.semantic_release]
   version_toml = "pyproject.toml:tool.poetry.version"

   # Python Semantic Release v8 configuration
   [tool.semantic_release]
   version_toml = ["pyproject.toml:tool.poetry.version"]


.. _upgrade_v8-tag-format-validation:

``tag_format``
""""""""""""""

This option has the same effect as it did in Python Semantic Release prior to v8,
but Python Semantic Release will now verify that it has a ``{version}`` format
key and raise an error if this is not the case.

.. _upgrade_v8-upload-to-release-rename:

``upload_to_release``
"""""""""""""""""""""

This option has been renamed to
:ref:`upload_to_vcs_release <config-publish-upload_to_vcs_release>`.

.. _upgrade_v8-custom-commit-parsers:

Custom Commit Parsers
---------------------

Previously, a custom commit parser had to satisfy the following criteria:

  * It should be ``import``-able from the virtual environment where the
    ``semantic-release`` is run
  * It should be a function which accepts the commit message as its only
    argument and returns a
    :py:class:`semantic_release.history.parser_helpers.ParsedCommit` if the commit is
    parsed successfully, or raise a
    :py:class:`semantic_release.UnknownCommitMessageStyleError` if parsing is
    unsuccessful.

It is still possible to implement custom commit parsers, but the interface for doing
so has been modified with stronger support for Python type annotations and broader
input provided to the parser to enable capturing more information from each commit,
such as the commit's date and author, if desired. A full guide to implementing a
custom commit parser can be found at :ref:`commit_parser-custom_parser`.
