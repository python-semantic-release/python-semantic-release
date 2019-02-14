python-semantic-release
=======================

Automatic semantic versioning for python projects. This is an python
implementation of the
`semantic-release <https://github.com/semantic-release/semantic-release>`__
for js by Stephan Bönnemann. If you find this topic interesting you
should check out his `talk from JSConf
Budapest <https://www.youtube.com/watch?v=tc2UgG5L7WM>`__.

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
      --retry  Retry the same release, do not bump.
      --help   Show this message and exit.

    Commands:
      changelog  Generates the changelog since the last...
      publish    Runs the version task before pushing to git...
      version    Detects the new version according to git log...


Documentation Contents:
=======================

.. toctree::
   :maxdepth: 1

   Quickstart <../readme>
   Commands <commands>
   Parsing of commit logs <commit-log-parsing>
   Automatic releases <automatic-releases/index>
   Configuration <configuration>
   Environment Variables <envvars>
   API docs <api/semantic_release>
   Troubleshooting <troubleshooting>
   Contributors <contributors>
