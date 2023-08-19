Python Semantic Release
***********************

|Black| |Ruff| |Test Status| |PyPI Version| |conda-forge version| |Read the Docs Status| |Pre-Commit Enabled|

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

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: black
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
