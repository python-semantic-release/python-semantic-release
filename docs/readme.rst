python-semantic-release |Build status| |Coverage status|
========================================================

|semantic-release| |Join the chat at
https://gitter.im/relekang/python-semantic-release| |PyPI version|

Automatic semantic versioning for python projects. `This blogpost
explains in more
detail <http://rolflekang.com/python-semantic-release/>`__.

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
``python setup.py <command>`` as you woul
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

.. |Build status| image:: https://ci.frigg.io/relekang/python-semantic-release.svg
   :target: https://ci.frigg.io/relekang/python-semantic-release/last/
.. |Coverage status| image:: https://ci.frigg.io/relekang/python-semantic-release/coverage.svg
   :target: https://ci.frigg.io/relekang/python-semantic-release/last/
.. |semantic-release| image:: https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg
   :target: https://semantic-release.org
.. |Join the chat at https://gitter.im/relekang/python-semantic-release| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/relekang/python-semantic-release?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |PyPI version| image:: https://badge.fury.io/py/python-semantic-release.svg
