Python Semantic Release
***********************

|PyPI Version| |conda-forge version| |Last Release| |Monthly Downloads| |PSR License| |Issues|

**Python Semantic Release (PSR)** provides an automated release mechanism
determined by SemVer and Commit Message Conventions for your Git projects.

The purpose of this project is to detect what the next version of the
project should be from parsing the latest commit messages. If the commit messages
describe changes that would require a major, minor or patch version bump, PSR
will automatically bump the version number accordingly. PSR, however, does not
stop there but will help automate the whole release process. It will update the
project code and distribution artifact, upload the artifact and post changelogs
to a remotely hosted Version Control System (VCS).

The tool is designed to run inside of a CI/CD pipeline service, but it can
also be run locally.

This project was originally inspired by the `semantic-release`_ project for JavaScript
by *Stephan Bönnemann*, but the codebases have significantly deviated since then, as
PSR as driven towards the goal of providing flexible changelogs and simple initial setup.

.. include:: concepts/installation.rst

Read more about the setup and configuration in our :ref:`Getting Started Guide <inline-getting-started-guide>`.

.. _semantic-release: https://github.com/semantic-release/semantic-release

.. |PyPI Version| image:: https://img.shields.io/pypi/v/python-semantic-release?label=PyPI&logo=pypi
   :target: https://pypi.org/project/python-semantic-release/
   :alt: pypi

.. |conda-forge Version| image:: https://img.shields.io/conda/vn/conda-forge/python-semantic-release?logo=anaconda
   :target: https://anaconda.org/conda-forge/python-semantic-release
   :alt: conda-forge

.. |Last Release| image:: https://img.shields.io/github/release-date/python-semantic-release/python-semantic-release?display_date=published_at
   :target: https://github.com/python-semantic-release/python-semantic-release/releases/latest
   :alt: GitHub Release Date

.. |PSR License| image:: https://img.shields.io/pypi/l/python-semantic-release?color=blue
   :target: https://github.com/python-semantic-release/python-semantic-release/blob/master/LICENSE
   :alt: PyPI - License

.. |Issues| image:: https://img.shields.io/github/issues/python-semantic-release/python-semantic-release
   :target: https://github.com/python-semantic-release/python-semantic-release/issues
   :alt: GitHub Issues

.. |Monthly Downloads| image:: https://img.shields.io/pypi/dm/python-semantic-release
   :target: https://pypistats.org/packages/python-semantic-release
   :alt: PyPI - Downloads


Documentation Contents
======================

.. toctree::
   :maxdepth: 1

   What's New <misc/psr_changelog>
   Concepts <concepts/index>
   CLI <api/commands>
   configuration/index
   upgrading/index
   misc/troubleshooting
   API <api/modules/modules>
   Contributing <contributing/index>
   View on GitHub <https://github.com/python-semantic-release/python-semantic-release>

----

.. _inline-getting-started-guide:

.. include:: concepts/getting_started.rst
   :start-after: .. _getting-started-guide:
