.. _getting-started-guide:

Getting Started
===============

If you haven't done so already, install Python Semantic Release locally following the
:ref:`installation instructions <installation>`.

If you are using a CI/CD service, you may not have to add Python Semantic Release to your
project's dependencies permanently, but for the duration of this guide for the initial
setup, you will need to have it installed locally.


Configuring PSR
---------------

Python Semantic Release ships with a reasonable default configuration but some aspects **MUST** be
customized to your project. To view the default configuration, run the following command:

.. code-block:: bash

    semantic-release generate-config

The output of the above command is the default configuration in TOML format without any modifications.
If this is fine for your project, then you do not need to configure anything else.

PSR accepts overrides to the default configuration keys individually. If you don't define the
key-value pair in your configuration file, the default value will be used.

By default, Python Semantic Release will look for configuration overrides in ``pyproject.toml`` under
the TOML table ``[tool.semantic_release]``. You may specify a different file using the
``-c/--config`` option, for example:

.. code-block:: bash

    # In TOML format with top level table [semantic_release]
    semantic-release -c releaserc.toml

    # In JSON format with top level object key {"semantic_release": {}}
    semantic-release -c releaserc.json

The easiest way to get started is to output the default configuration to a file,
delete keys you do not need to override, and then edit the remaining keys to suit your project.

To set up in ``pyproject.toml``, run the following command:

.. code-block:: bash

    # In file redirect in bash
    semantic-release generate-config --pyproject >> pyproject.toml

    # Open your editor to edit the configuration
    vim pyproject.toml

.. seealso::
   - :ref:`cmd-generate-config`
   - :ref:`configuration`


Configuring the Version Stamp Feature
'''''''''''''''''''''''''''''''''''''

One of the best features of Python Semantic Release is the ability to automatically stamp the
new version number into your project files, so you don't have to manually update the version upon
each release. The version that is stamped is automatically determined by Python Semantic Release
from your commit messages which compliments automated versioning seamlessly.

The most crucial version stamp is the one in your project metadata, which is used by
the Python Package Index (PyPI) and other package managers to identify the version of your package.

For Python projects, this is typically the ``version`` field in your ``pyproject.toml`` file. First,
set up your project metadata with the base ``version`` value. If you are starting with a brand new project,
set ``project.version = "0.0.0"``.  If you are working on an existing project, set it to the last
version number you released. Do not include any ``v`` prefix.

.. important::
   The version number must be a valid SemVer version, which means it should follow the format
   ``MAJOR.MINOR.PATCH`` (e.g., ``1.0.0``). Python Semantic Release does NOT support Canonical
   version values defined in the `PEP 440`_ specification at this time. See
   `Issue #455 <https://github.com/python-semantic-release/python-semantic-release/issues/455>`_
   for more details. Note that you can still define a SemVer version in the ``project.version``
   field, and when your build is generated, the build tool will automatically generate a PEP 440
   compliant version as long as you do **NOT** use a non-pep440 compliant pre-release token.

.. _PEP 440: https://peps.python.org/pep-0440/

Your project metadata might look like this in ``pyproject.toml``::

   [project]
   name = "my-package"
   version = "0.0.0"  # Set this to the last released version or "0.0.0" for new projects
   description = "A sample Python package"

To configure PSR to automatically update this version number, you need to specify the file and value
to update in your configuration. Since ``pyproject.toml`` uses TOML format, you will add the
replacement specification to the ``tool.semantic_release.version_toml`` list. Update the following
configuration in your ``pyproject.toml`` file to include the version variable location:

.. code-block:: toml

    [tool.semantic_release]
    version_toml = ["pyproject.toml:project.version"]

    # Alternatively, if you are using poetry's 'version' key, then you would use:
    version_toml = ["pyproject.toml:tool.poetry.version"]

If you have other TOML files where you want to stamp the version, you can add them to the
``version_toml`` list as well. In the above example, there is an implicit assumption that
you only want the version as the raw number format. If you want to specify the full tag
value (e.g. v-prefixed version), then include ``:tf`` for "tag format" at the end of the
version variable specification.

For non-TOML formatted files (such as JSON or YAML files), you can use the
:ref:`config-version_variables` configuration key instead. This feature uses an advanced
Regular Expression to find and replace the version variable in the specified files.

For Python files, its much more effective to use ``importlib`` instead which will allow you to
dynamically import the version from your package metadata and not require your project to commit
the version number bump to the repository. For example, in your package's base ``__init__.py``

.. code-block:: python

    # my_package/__init__.py
    from importlib.metadata import version as get_version

    __version__ = get_version(__package__)
    # Note: __package__ must match your 'project.name' as defined in pyproject.toml

.. seealso::
    - Configuration specification of :ref:`config-version_toml`
    - Configuration specification of :ref:`config-version_variables`


Using PSR to Build your Project
'''''''''''''''''''''''''''''''

PSR provides a convenient way to build your project artifacts as part of the versioning process
now that you have stamped the version into your project files. To enable this, you will need
to specify the build command in your configuration. This command will be executed after
the next version has been determined, and stamped into your files but before a release tag has
been created.

To set up the build command, add the following to your ``pyproject.toml`` file:

.. code-block:: toml

    [tool.semantic_release]
    build_command = "python -m build --sdist --wheel ."

.. seealso::
   - :ref:`config-build_command` - Configuration specification for the build command.
   - :ref:`config-build_command_env` - Configuration specification for the build command environment variables.


Choosing a Commit Message Parser
''''''''''''''''''''''''''''''''

PSR uses commit messages to determine the type of version bump that should be applied
to your project. PSR supports multiple commit message parsing styles, allowing you to choose
the one that best fits your project's needs. Choose **one** of the supported commit parsers
defined in :ref:`commit_parsing`, or provide your own and configure it in your
``pyproject.toml`` file.

Each commit parser has its own default configuration options so if you want to customize the parser
behavior, you will need to specify the parser options you want to override.

.. code-block:: toml

    [tool.semantic_release]
    commit_parser = "conventional"

    [tool.semantic_release.commit_parser_options]
    minor_tags = ["feat"]
    patch_tags = ["fix", "perf"]
    parse_squash_commits = true
    ignore_merge_commits = true


Choosing your Changelog
'''''''''''''''''''''''

Prior to creating a release, PSR will generate a changelog from the commit messages of your
project. The changelog is extremely customizable from the format to the content of each section.
PSR ships with a default changelog template that will be used if you do not provide custom
templates. The default should be sufficient for most projects and has its own set of configuration
options.

For basic customization, you can choose either an traditional Markdown formatted changelog (default)
or if you want to integrate with a Sphinx Documentation project, you can use the
reStructuredText (RST) format. You can also choose the file name and location of where to write the
default changelog.

To set your changelog location and changelog format, add the following to your ``pyproject.toml`` file:

.. code-block:: toml

    [tool.semantic_release.changelog.default_templates]
    changelog_file = "docs/source/CHANGELOG.rst"
    output_format = "rst" # or "md" for Markdown format

Secondly, the more important aspect of configuring your changelog is to define Commit Exclusion
Patterns or patterns that will be used to filter out commits from the changelog. PSR does **NOT** (yet)
come with a built-in set of exclusion patterns, so you will need to define them yourself. These commit
patterns should be in line with your project's commit parser configuration.

To set commit exclusion patterns for a conventional commits parsers, add the following to your
``pyproject.toml`` file:

.. code-block:: toml

    [tool.semantic_release.changelog]
    # Recommended patterns for conventional commits parser that is scope aware
    exclude_commit_patterns = [
        '''chore(?:\([^)]*?\))?: .+''',
        '''ci(?:\([^)]*?\))?: .+''',
        '''refactor(?:\([^)]*?\))?: .+''',
        '''style(?:\([^)]*?\))?: .+''',
        '''test(?:\([^)]*?\))?: .+''',
        '''build\((?!deps\): .+)''',
        '''Initial [Cc]ommit.*''',
    ]

.. seealso::
   - :ref:`Changelog <config-changelog>` - Customize your changelog
   - :ref:`changelog.mode <config-changelog-mode>` - Choose the changelog mode ('update' or 'init')
   - :ref:`changelog-templates-migrating-existing-changelog`


Defining your Release Branches
''''''''''''''''''''''''''''''

PSR provides a powerful feature to manage release types across multiple branches which can
allow you to configure your project to have different release branches for different purposes,
such as pre-release branches, beta branches, and your stable releases.

.. note::
    Most projects that do **NOT** publish pre-releases will be fine with PSR's built-in default.

To define an alpha pre-release branch when you are working on a fix or new feature, you can
add the following to your ``pyproject.toml`` file:

.. code-block:: toml

    [tool.semantic_release.branches.alpha]
    # Matches branches with the prefixes 'feat/', 'fix/', or 'perf/'.
    match = "^(feat|fix|perf)/.+"
    prerelease = true
    prerelease_token = "alpha"

Any time you execute ``semantic-release version`` on a branch with the prefix
``feat/``, ``fix/``, or ``perf/``, PSR will determine if a version bump is needed and if so,
the resulting version will be a pre-release version with the ``alpha`` token. For example,

+-----------+--------------+-----------------+-------------------+
| Branch    | Version Bump | Current Version | Next Version      |
+===========+==============+=================+===================+
| main      | Patch        | ``1.0.0``       | ``1.0.1``         |
+-----------+--------------+-----------------+-------------------+
| fix/bug-1 | Patch        | ``1.0.0``       | ``1.0.1-alpha.1`` |
+-----------+--------------+-----------------+-------------------+

.. seealso::
   - :ref:`multibranch-releases` - Learn about multi-branch releases and how to configure them.


Configuring VCS Releases
''''''''''''''''''''''''

You can set up Python Semantic Release to create Releases in your remote version
control system, so you can publish assets and release notes for your project.

In order to do so, you will need to place an authentication token in the
appropriate environment variable so that Python Semantic Release can authenticate
with the remote VCS to push tags, create releases, or upload files.

GitHub (``GH_TOKEN``)
"""""""""""""""""""""

For local publishing to GitHub, you should use a personal access token and
store it in your environment variables. Specify the name of the environment
variable in your configuration setting :ref:`remote.token <config-remote-token>`.
The default is ``GH_TOKEN``.

To generate a token go to https://github.com/settings/tokens and click on
"Generate new token".

For Personal Access Token (classic), you will need the ``repo`` scope to write
(ie. push) to the repository.

For fine-grained Personal Access Tokens, you will need the `contents`__
permission.

__ https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens#repository-permissions-for-contents

GitLab (``GITLAB_TOKEN``)
"""""""""""""""""""""""""

A personal access token from GitLab. This is used for authenticating when pushing
tags, publishing releases etc. This token should be stored in the ``GITLAB_TOKEN``
environment variable.

Gitea (``GITEA_TOKEN``)
"""""""""""""""""""""""

A personal access token from Gitea. This token should be stored in the ``GITEA_TOKEN``
environment variable.

Bitbucket (``BITBUCKET_TOKEN``)
"""""""""""""""""""""""""""""""

Bitbucket does not support uploading releases but can still benefit from automated tags
and changelogs. The user has three options to push changes to the repository:

#. Use SSH keys.

#. Use an `App Secret`_, store the secret in the ``BITBUCKET_TOKEN`` environment variable
   and the username in ``BITBUCKET_USER``.

#. Use an `Access Token`_ for the repository and store it in the ``BITBUCKET_TOKEN``
   environment variable.

.. _App Secret: https://support.atlassian.com/bitbucket-cloud/docs/push-back-to-your-repository/#App-secret
.. _Access Token: https://support.atlassian.com/bitbucket-cloud/docs/repository-access-tokens

.. seealso::
   - :ref:`Changelog <config-changelog>` - customize your project's changelog.

   - :ref:`changelog-templates-custom_release_notes` - customize the published release notes

   - :ref:`version --vcs-release/--no-vcs-release <cmd-version-option-vcs-release>` - enable/disable VCS release
     creation.


Testing your Configuration
--------------------------

It's time to test your configuration!

.. code-block:: bash

    # 1. Run the command in no-operation mode to see what would happen
    semantic-release -v --noop version

    # 2. If the output looks reasonable, try to run the command without any history changes
    #    '-vv' will give you verbose debug output, which is useful for troubleshooting
    #    commit parsing issues.
    semantic-release -vv version --no-commit --no-tag

    # 3. Evaluate your repository to see the changes that were made but not committed
    #    - Check the version number in your pyproject.toml
    #    - Check the distribution files from the build command
    #    - Check the changelog file for the new release notes

    # 4. If everything looks good, make sure to commit/save your configuration changes
    git add pyproject.toml
    git commit -m "chore(config): configure Python Semantic Release"

    # 5. Now, try to run the release command with your history changes but without pushing
    semantic-release -v version --no-push --no-vcs-release

    # 6. Check the result on your local repository
    git status
    git log --graph --decorate --all

    # 7a. If you are happy with the release history and resulting commit & tag,
    #     reverse your changes before trying the full release command.
    git tag -d v0.0.1  # replace with the actual version you released
    git reset --hard HEAD~1

    # 7b. [Optional] Once you have configured a remote VCS token, try
    #     running the full release command to update the remote repository.
    semantic-release version --push --vcs-release
    #    This is optional as you may not want a personal access token set up or make
    #    make the release permanent yet.

.. seealso::
   - :ref:`cmd-version`
   - :ref:`troubleshooting-verbosity`

Configuring CI/CD
-----------------

PSR is meant to help you release at speed! See our CI/CD Configuration guides under the
:ref:`automatic` section.
