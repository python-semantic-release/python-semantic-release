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
indicates certain types of changes. If a commit message lacks a tag it is
ignored. Running release can be run locally or from a CI service.

::

  Usage: semantic-release [OPTIONS] COMMAND [ARGS]...

  Options:
  --major            Force major version.
  --minor            Force minor version.
  --patch            Force patch version.
  --post             Post changelog.
  --retry            Retry the same release, do not bump.
  --noop             No-operations mode, finds the new version number without
                     changing it.
  -D, --define TEXT  setting="value", override a configuration value.
  --help             Show this message and exit.

  Commands:
  changelog  Generate the changelog since the last release.
  publish    Run the version task, then push to git and upload distributions.
  version    Detect the new version according to git log and semver.


Documentation Contents
======================

.. toctree::
   :maxdepth: 1

   Quickstart <../readme>
   Commands <commands>
   Parsing of commit logs <commit-log-parsing>
   Automatic releases <automatic-releases/index>
   Configuration <configuration>
   Environment Variables <envvars>
   API docs <api/modules>
   Troubleshooting <troubleshooting>
   Contributors <contributors>
