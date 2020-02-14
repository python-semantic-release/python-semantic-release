python-semantic-release
=======================

Automatic semantic versioning for python projects. This is an python
implementation of the
`semantic-release <https://github.com/semantic-release/semantic-release>`__
for js by Stephan Bönnemann. If you find this topic interesting you
should check out his `talk from JSConf
Budapest <https://www.youtube.com/watch?v=tc2UgG5L7WM>`__.

|Build status| |PyPI version|

The general idea is to be able to detect what the next version of the project
should be based on the commits. This tool will use that to automate the whole
release, upload to PyPI and upload changelogs to Github. You can run the tool
with a CI service or just run it locally.

Setup in your project
---------------------

Install it
~~~~~~~~~~

::

    pip install python-semantic-release


Configure it
~~~~~~~~~~~~

There are a three different ways to configure semantic-release.

-  ``[semantic_release]`` section in ``setup.cfg``
-  ``[tool.semantic_release]`` section in ``pyproject.toml``
-  Passing ``-D`` to the command like ``semantic-release <command> -D <option_name>=<option_value>``

The important thing to configure for all projects is where the version variable is stored. This
is used to get the current version and updating it. The config variable for that is ``version_variable``.
If your project main package is super_package and the version with name ``__version__`` variable is in
``__init__.py`` then you can set it too ``version_variable = super_package/__init__.py:__version__``.

For the basic setup this should be all you need to, for further reading on supported config variables
check the `Configuration page <https://python-semantic-release.readthedocs.io/en/latest/configuration.html>`_
in the documentation

Run it
~~~~~~

There is three different things you can do with this tool. Run the commands below with
``semantic-release <command>``.

-  ``version`` - Create a new release. Will change the version, commit
   it and tag it.
-  ``publish`` - Runs version before pushing to git and uploading to
   pypi.
-  ``changelog`` - Generates the changelog for the next release.

Running commands from setup.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following to your setup.py and you will be able to run
``python setup.py <command>`` as you would
``semantic-release <command>``.

.. code:: python

    try:
        from semantic_release import setup_hook
        setup_hook(sys.argv)
    except ImportError:
        pass

Configuration
~~~~~~~~~~~~~

Configuration belongs in ``semantic_release`` section of the setup.cfg
file in your project. Details about configuration options can be found
in `the configuration documentation <http://python-semantic-release.readthedocs.org/en/latest/configuration.html>`__.


Running it on CI
~~~~~~~~~~~~~~~~

Getting a fully automated setup with automatic releases from CI can be helpful for some projects.
It was the main motivation to create this tool. There is a dedicated documentation page for setting
up with different CI tools:
`Automatic release with CI documentation <https://python-semantic-release.readthedocs.io/en/latest/automatic-releases/index.html>`__


.. |Build status| image:: https://circleci.com/gh/relekang/python-semantic-release/tree/master.svg?style=svg
    :target: https://circleci.com/gh/relekang/python-semantic-release/tree/master
.. |PyPI version| image:: https://badge.fury.io/py/python-semantic-release.svg


