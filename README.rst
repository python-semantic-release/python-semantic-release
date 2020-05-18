Python Semantic Release
=======================

|Test Status| |PyPI Version| |conda-forge version| |Read the Docs Status|

Automatic semantic versioning for python projects. This is a python
implementation of `semantic-release`_ for JS by Stephan Bönnemann. If
you find this topic interesting you should check out his `talk from
JSConf Budapest`_.

The general idea is to be able to detect what the next version of the
project should be based on the commits. This tool will use that to
automate the whole release, upload to PyPI and post changelogs to
GitHub. You can run the tool on a CI service, or just run it locally.

Install
-------

::

   pip install python-semantic-release

Configure
---------

Set up Python Semantic Release using the configuration options shown on
`this page`_.

The only one which is required is ``version_variable``, which tells the
tool where to bump the version number:

::

   [semantic_release]
   version_variable = semantic_release/__init__.py:__version__

Run it
------

There are three different things you can do:

+---------------+-----------------------------------------------------+
| Command       | Description                                         |
+===============+=====================================================+
| ``version``   | Create a new release. Will change the version,      |
|               | commit it and tag it.                               |
+---------------+-----------------------------------------------------+
| ``publish``   | Run ``version`` before pushing to git and uploading |
|               | to PyPI.                                            |
+---------------+-----------------------------------------------------+
| ``changelog`` | Generate the changelog for the next release.        |
+---------------+-----------------------------------------------------+

Run these commands as ``semantic-release <command>``.

.. _running-from-setuppy:

Running from setup.py
---------------------

Add the following hook to your ``setup.py`` and you will be able to run
``python setup.py <command>`` as you would
``semantic-release <command>``.

.. code:: python

   try:
       from semantic_release import setup_hook
       setup_hook(sys.argv)
   except ImportError:
       pass

Running on CI
-------------

Getting a fully automated setup with releases from CI can be helpful for
some projects. It was the main motivation to create this tool.

See `this documentation page`_ for instructions.

.. _semantic-release: https://github.com/semantic-release/semantic-release
.. _talk from JSConf Budapest: https://www.youtube.com/watch?v=tc2UgG5L7WM
.. _this page: https://python-semantic-release.readthedocs.io/en/latest/configuration.html
.. _this documentation page: https://python-semantic-release.readthedocs.io/en/latest/automatic-releases/index.html

.. |Test Status| image:: https://img.shields.io/github/workflow/status/relekang/python-semantic-release/Test%20%26%20Release?label=Tests&logo=github
.. |PyPI Version| image:: https://img.shields.io/pypi/v/python-semantic-release?label=PyPI&logo=pypi
.. |conda-forge Version| image:: https://img.shields.io/conda/vn/conda-forge/python-semantic-release?logo=anaconda
.. |Read the Docs Status| image:: https://img.shields.io/readthedocs/python-semantic-release?label=Read%20the%20Docs&logo=read-the-docs
