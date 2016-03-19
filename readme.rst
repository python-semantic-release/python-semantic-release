python-semantic-release
=======================

Automatic semantic versioning for python projects. This is an python
implementation of the
`semantic-release <https://github.com/semantic-release/semantic-release>`__
for js by Stephan Bönnemann. If you find this topic interesting you
should check out his `talk from JSConf
Budapest <https://www.youtube.com/watch?v=tc2UgG5L7WM>`__.

|Build status| |Coverage status| |PyPI version| |Trello|

Install
-------

::

    pip install python-semantic-release

Usage
-----

The general idea is to have some sort of tag in commit messages that
indicates certain types of changes. If a commit message lack a tag it is
ignored. Running release can be run locally or from a CI service.

::

    Usage: semantic-release [OPTIONS] COMMAND

    Options:
      --major  Force major version.
      --minor  Force minor version.
      --patch  Force patch version.
      --noop   No-operations mode, finds the new version number without changing it.
      --post   If used with the changelog command, the changelog will be posted to the release api.
      --help   Show this message and exit.

Commands
~~~~~~~~

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

Configuration belong in ``semantic_release`` section of the setup.cfg
file in your project. Details about configuration options can be found
in `the configuration
documentation <http://python-semantic-release.readthedocs.org/en/latest/configuration.html>`__.

Found a bug
~~~~~~~~~~~

Please create a pull-request with a test case that shows the usage. If you are unsure were to put
it, just create a new file inside tests, and we will point you in the right direction.

Have a feature request
~~~~~~~~~~~~~~~~~~~~~~

Check the `trello board`_ and `roadmap.md`_ to see if it is already in the pipeline. If not make a
pull-request to `roadmap.md`_.

.. _trello board: https://trello.com/b/ylmdOYr1/python-semantic-release
.. _roadmap.md: https://github.com/relekang/python-semantic-release/blob/master/roadmap.md

.. |Build status| image:: https://ci.frigg.io/relekang/python-semantic-release.svg?branch=master
   :target: https://ci.frigg.io/relekang/python-semantic-release
.. |Coverage status| image:: https://ci.frigg.io/relekang/python-semantic-release/coverage.svg?branch=master
   :target: https://ci.frigg.io/relekang/python-semantic-release
.. |PyPI version| image:: https://badge.fury.io/py/python-semantic-release.svg
.. |Trello| image:: https://img.shields.io/badge/trello-board-blue.svg
   :target: https://trello.com/b/ylmdOYr1/python-semantic-release
