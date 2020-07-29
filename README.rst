Python Semantic Release
***********************

|Test Status| |PyPI Version| |conda-forge version| |Read the Docs Status|

Automatic semantic versioning for python projects. This is a python
implementation of `semantic-release`_ for JS by Stephan Bönnemann. If
you find this topic interesting you should check out his `talk from
JSConf Budapest`_.

The general idea is to be able to detect what the next version of the
project should be based on the commits. This tool will use that to
automate the whole release, upload to PyPI and post changelogs to
GitHub. You can run the tool on a CI service, or just run it locally.


.. _semantic-release: https://github.com/semantic-release/semantic-release
.. _talk from JSConf Budapest: https://www.youtube.com/watch?v=tc2UgG5L7WM

.. |Test Status| image:: https://img.shields.io/github/workflow/status/relekang/python-semantic-release/Test%20%26%20Release?label=Tests&logo=github
.. |PyPI Version| image:: https://img.shields.io/pypi/v/python-semantic-release?label=PyPI&logo=pypi
.. |conda-forge Version| image:: https://img.shields.io/conda/vn/conda-forge/python-semantic-release?logo=anaconda
.. |Read the Docs Status| image:: https://img.shields.io/readthedocs/python-semantic-release?label=Read%20the%20Docs&logo=read-the-docs
