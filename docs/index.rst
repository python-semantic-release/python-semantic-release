python-semantic-release |Build status| |Coverage status|
========================================================

Automatic semantic versioning for python projects. `This blogpost
explains in more
detail <http://rolflekang.com/python-semantic-release/>`__.

Install
-------

::

    pip3 install python-semantic-release

Python 2 is currently not supported. See
`#10 <https://github.com/relekang/python-semantic-release/issues/10>`__
for more information.

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
      --help   Show this message and exit.

Documentation Contents:
=======================

.. toctree::
   :maxdepth: 2

   Quickstart <readme>
   API docs <api/semantic_release>
   Contributors <contributors>

.. |Build status| image:: https://ci.frigg.io/relekang/python-semantic-release.svg
                  :target: https://ci.frigg.io/relekang/python-semantic-release/last/
.. |Coverage status| image:: https://ci.frigg.io/relekang/python-semantic-release/coverage.svg
                  :target: https://ci.frigg.io/relekang/python-semantic-release/last/
