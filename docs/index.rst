Python Semantic Release
***********************

|Ruff| |Test Status| |PyPI Version| |conda-forge version| |Read the Docs Status| |Pre-Commit Enabled|

Automatic Semantic Versioning for Python projects. This is a Python
implementation of `semantic-release`_ for JS by Stephan Bönnemann. If
you find this topic interesting you should check out his `talk from
JSConf Budapest`_.

The general idea is to be able to detect what the next version of the
project should be based on the commits. This tool will use that to
automate the whole release, upload to an artifact repository and post changelogs to
GitHub. You can run the tool on a CI service, or just run it locally.

Installation
============

::

  python3 -m pip install python-semantic-release
  semantic-release --help

Python Semantic Release is also available from `conda-forge`_ or as a `GitHub Action`_.
Read more about the setup and configuration in our `getting started guide`_.

.. _semantic-release: https://github.com/semantic-release/semantic-release
.. _talk from JSConf Budapest: https://www.youtube.com/watch?v=tc2UgG5L7WM
.. _getting started guide: https://python-semantic-release.readthedocs.io/en/latest/#getting-started
.. _GitHub Action: https://python-semantic-release.readthedocs.io/en/latest/automatic-releases/github-actions.html
.. _conda-forge: https://anaconda.org/conda-forge/python-semantic-release

.. |Test Status| image:: https://img.shields.io/github/actions/workflow/status/python-semantic-release/python-semantic-release/main.yml?branch=master&label=Test%20Status&logo=github
   :target: https://github.com/python-semantic-release/python-semantic-release/actions/workflows/main.yml
   :alt: test-status
.. |PyPI Version| image:: https://img.shields.io/pypi/v/python-semantic-release?label=PyPI&logo=pypi
   :target: https://pypi.org/project/python-semantic-release/
   :alt: pypi
.. |conda-forge Version| image:: https://img.shields.io/conda/vn/conda-forge/python-semantic-release?logo=anaconda
   :target: https://anaconda.org/conda-forge/python-semantic-release
   :alt: conda-forge
.. |Read the Docs Status| image:: https://img.shields.io/readthedocs/python-semantic-release?label=Read%20the%20Docs&logo=Read%20the%20Docs
   :target: https://python-semantic-release.readthedocs.io/en/latest/
   :alt: docs
.. |Pre-Commit Enabled| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff


Documentation Contents
======================

.. toctree::
   :maxdepth: 1

   commands
   Strict Mode <strict_mode>
   configuration
   commit-parsing
   Changelog Templates <changelog_templates>
   Multibranch Releases <multibranch_releases>
   automatic-releases/index
   troubleshooting
   contributing
   contributors
   Migrating from Python Semantic Release v7 <migrating_from_v7>
   Internal API <api/modules>
   Algorithm <algorithm>
   View on GitHub <https://github.com/python-semantic-release/python-semantic-release>

Getting Started
===============

If you haven't done so already, install Python Semantic Release following the
instructions above.

There is no strict requirement to have it installed locally if you intend on
:ref:`using a CI service <automatic>`, however running with :ref:`cmd-main-option-noop` can be
useful to test your configuration.

Generating your configuration
-----------------------------

Python Semantic Release ships with a command-line interface, ``semantic-release``. You can
inspect the default configuration in your terminal by running

``semantic-release generate-config``

You can also use the :ref:`-f/--format <cmd-generate-config-option-format>` option to specify what format you would like this configuration
to be. The default is TOML, but JSON can also be used.

You can append the configuration to your existing ``pyproject.toml`` file using a standard redirect,
for example:

``semantic-release generate-config --pyproject >> pyproject.toml``

and then editing to your project's requirements.

.. seealso::
   - :ref:`cmd-generate-config`
   - :ref:`configuration`


Setting up version numbering
----------------------------

Create a variable set to the current version number.  This could be anywhere in
your project, for example ``setup.py``::

   from setuptools import setup

   __version__ = "0.0.0"

   setup(
      name="my-package",
      version=__version__,
      # And so on...
   )

Python Semantic Release can be configured using a TOML or JSON file; the default configuration file is
``pyproject.toml``, if you wish to use another file you will need to use the ``-c/--config`` option to
specify the file.

Set :ref:`version_variables <config-version_variables>` to a list, the only element of which should be the location of your
version variable inside any Python file, specified in standard ``module:attribute`` syntax:

``pyproject.toml``::

   [tool.semantic_release]
   version_variables = ["setup.py:__version__"]

.. seealso::
   - :ref:`configuration` - tailor Python Semantic Release to your project

Setting up commit parsing
-------------------------

We rely on commit messages to detect when a version bump is needed.
By default, Python Semantic Release uses the
`Angular style <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits>`_.
You can find out more about this in :ref:`commit-parsing`.

.. seealso::
   - :ref:`config-branches` - Adding configuration for releases from multiple branches.
   - :ref:`commit_parser <config-commit_parser>` - use a different parser for commit messages.
     For example, Python Semantic Release also ships with emoji and scipy-style parsers.
   - :ref:`remote.type <config-remote-type>` - specify the type of your remote VCS.

Setting up the changelog
------------------------

.. seealso::
   - :ref:`Changelog <config-changelog>` - Customize the changelog generated by Python Semantic Release.
   - :ref:`changelog-templates-migrating-existing-changelog`

.. _index-creating-vcs-releases:

Creating VCS Releases
---------------------

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
#. Use an `App Secret`_, store the secret in the ``BITBUCKET_TOKEN`` environment variable and the username in ``BITBUCKET_USER``.
#. Use an `Access Token`_ for the repository and store it in the ``BITBUCKET_TOKEN`` environment variable.

.. _App Secret: https://support.atlassian.com/bitbucket-cloud/docs/push-back-to-your-repository/#App-secret
.. _Access Token: https://support.atlassian.com/bitbucket-cloud/docs/repository-access-tokens

.. seealso::
   - :ref:`Changelog <config-changelog>` - customize your project's changelog.
   - :ref:`changelog-templates-custom_release_notes` - customize the published release notes
   - :ref:`upload_to_vcs_release <config-publish-upload_to_vcs_release>` -
     enable/disable uploading artefacts to VCS releases
   - :ref:`version --vcs-release/--no-vcs-release <cmd-version-option-vcs-release>` - enable/disable VCS release
     creation.
   - `upload-to-gh-release`_, a GitHub Action for running ``semantic-release publish``

.. _upload-to-gh-release: https://github.com/python-semantic-release/upload-to-gh-release

.. _running-from-setuppy:

Running from setup.py
---------------------

Add the following hook to your ``setup.py`` and you will be able to run
``python setup.py <command>`` as you would ``semantic-release <command>``::

   try:
       from semantic_release import setup_hook
       setup_hook(sys.argv)
   except ImportError:
       pass

.. note::
   Only the :ref:`version <cmd-version>`, :ref:`publish <cmd-publish>`, and
   :ref:`changelog <cmd-changelog>` commands may be invoked from setup.py in this way.

Running on CI
-------------

Getting a fully automated setup with releases from CI can be helpful for some
projects.  See :ref:`automatic`.
