.. include:: ../README.rst


Getting Started
===============

If you haven't done so already, install Python Semantic Release following the
instructions above.

There is no strict requirement to have it installed locally if you intend on
:ref:`using a CI service <automatic>`, however running with ``--noop`` can be
useful to test your configuration.

Configure
---------

Set :ref:`config-version_variable` in either ``setup.cfg`` or
``pyproject.toml``.  This option tells Python Semantic Release where to find
and update the version number. ::

   [semantic_release]
   version_variable = semantic_release/__init__.py:__version__

The example above uses the variable ``__version__`` in
``semantic_release/__init__.py``. This variable must be initially created by
hand - set it to the current version number::

   __version__ = "0.0.0"

.. seealso::
   - :ref:`config-branch` - change the default branch.
   - :ref:`config-commit_parser` - use a different parser for commit messages.
     For example, there is an emoji parser.
   - :ref:`config-upload_to_pypi` - disable uploading the package to PyPI.
   - :ref:`hvcs` - change this if you are using GitLab.

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
