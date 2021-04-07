.. include:: ../README.rst


Getting Started
===============

If you haven't done so already, install Python Semantic Release following the
instructions above.

There is no strict requirement to have it installed locally if you intend on
:ref:`using a CI service <automatic>`, however running with ``--noop`` can be
useful to test your configuration.

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

Python Semantic Release is configured using ``setup.cfg`` or ``pyproject.toml``.
Set :ref:`config-version_variable` to the location of your version variable inside any Python file::

   [semantic_release]
   version_variable = setup.py:__version__

.. seealso::
   - :ref:`config-version_toml` - use `tomlkit <https://github.com/sdispater/tomlkit>`_ to read and update
     the version number in a TOML file.
   - :ref:`config-version_pattern` - use regular expressions to keep the
     version number in a different format.
   - :ref:`config-version_source` - store the version using Git tags.

Setting up commit parsing
-------------------------

We rely on commit messages to detect when a version bump is needed.
By default, Python Semantic Release uses the
`Angular style <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits>`_.
You can find out more about this on :ref:`commit-log-parsing`.

.. seealso::
   - :ref:`config-branch` - change the default branch name.

Setting up the changelog
------------------------

If you already have a `CHANGELOG.md`, you will need to insert a
placeholder tag so we know where to write new versions::

   <!--next-version-placeholder-->

If you don't have a changelog file then one will be set up like this automatically.

.. seealso::
   - :ref:`config-changelog_file` - use a file other than `CHANGELOG.md`.
   - :ref:`config-changelog_placeholder` - use a different placeholder.

Releasing on GitHub / GitLab
----------------------------

Some options and environment variables need to be set in order to push
release notes and new versions to GitHub / GitLab:

- :ref:`config-hvcs` - change this if you are using GitLab.
- :ref:`env-gh_token` - GitHub personal access token.
- :ref:`env-gl_token` - GitLab personal access token.

Releasing on PyPI
-----------------

Unless you disable :ref:`config-upload_to_pypi`, Python Semantic Release will
publish new versions on PyPI. This requires you to obtain an API token
`here <https://pypi.org/help/#apitoken>`_ and store it in the environment
variable :ref:`env-pypi_token`.

.. include:: commands.rst

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

Running on CI
-------------

Getting a fully automated setup with releases from CI can be helpful for some
projects.  See :ref:`automatic`.


Documentation Contents
======================

.. toctree::
   :maxdepth: 1

   configuration
   envvars
   commands
   commit-log-parsing
   automatic-releases/index
   troubleshooting
   contributors
   Internal API <api/modules>
