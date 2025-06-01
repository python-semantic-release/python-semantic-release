.. _contributing_guide:

Contributing
------------

If you want to contribute that is awesome. Remember to be nice to others in issues and reviews.

Please remember to write tests for the cool things you create or fix.

Unsure about something? No worries, `open an issue`_.

.. _open an issue: https://github.com/python-semantic-release/python-semantic-release/issues/new

Commit messages
~~~~~~~~~~~~~~~

Since python-semantic-release is released with python-semantic-release we need the commit messages
to adhere to the `Conventional Commits Specification`_.  Although scopes are optional, scopes are
expected where applicable. Changes should be committed separately with the commit type they represent,
do not combine them all into one commit.

If you are unsure how to describe the change correctly just try and ask about it in your pr. If we
think it should be something else or there is a pull-request without tags we will help out in
adding or changing them.

.. _Conventional Commits Specification: https://www.conventionalcommits.org/en/v1.0.0

Releases
~~~~~~~~

This package is released by python-semantic-release on each master build, thus if there are changes
that should result in a new release it will happen if the build is green.


Development
~~~~~~~~~~~

Install this module and the development dependencies

.. code-block:: bash

    pip install -e .[dev,mypy,test]

And if you'd like to build the documentation locally

.. code-block:: bash

    pip install -e .[docs]
    sphinx-autobuild --open-browser docs docs/_build/html

Testing
~~~~~~~

To test your modifications locally:

.. code-block:: bash

    # Run type-checking, all tests across all supported Python versions
    tox

    # Run all tests for your current installed Python version (with full error output)
    pytest -vv --comprehensive

    # Run unit tests for your current installed Python version
    pytest
    # or
    pytest -vv -m unit

    # Run end-to-end tests for your current installed Python version (with full error output)
    pytest -vv -m e2e [--comprehensive]

The ``--comprehensive`` flag is optional and will run all the variations of tests and it does
take significantly longer to run.

Building
~~~~~~~~

This project is designed to be versioned and built by itself using the ``tool.semantic_release``
configuration in ``pyproject.toml``. The setting ``tool.semantic_release.build_command`` defines
the command to run to build the package.

The following is a copy of the ``build_command`` setting which can be run manually to build the
package locally:

.. code-block:: bash

    pip install -e .[build]
    python -m build .
