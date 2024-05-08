Contributing
------------

If you want to contribute that is awesome. Remember to be nice to others in issues and reviews.

Please remember to write tests for the cool things you create or fix.

Unsure about something? No worries, `open an issue`_.

.. _open an issue: https://github.com/relekang/python-semantic-release/issues/new

Commit messages
~~~~~~~~~~~~~~~

Since python-semantic-release is released with python-semantic-release we need the commit messages
to adhere to the `angular commit guidelines`_. If you are unsure how to describe the change correctly
Just try and ask in your pr, or ask on gitter. If we think it should be something else or there is a
pull-request without tags we will help out in adding or changing them.

.. _angular commit guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits

Releases
~~~~~~~~

This package is released by python-semantic-release on each master build, thus if there are changes
that should result in a new release it will happen if the build is green.


Development
~~~~~~~~~~~

Install this module and the development dependencies

.. code-block:: bash

    pip install -e ".[dev,mypy,test]"

And if you'd like to build the documentation locally

.. code-block:: bash

    pip install -e ".[docs]"
    sphinx-autobuild --open-browser docs docs/_build/html

Testing
~~~~~~~

To test your modifications locally:

.. code-block:: bash

    # Run type-checking, all tests across all supported Python versions
    tox

    # Run all tests for your current installed Python version (with full error output)
    pytest -vv tests/

If you need to run tests in a debugger, such as VSCode, you will need to adjust
``pyproject.toml`` temporarily:

.. code-block:: diff

    diff --git a/pyproject.toml b/pyproject.toml

      [tool.pytest.ini_options]
      addopts = [
    +     "-n0",
    -     "-nauto",
          "-ra",
          "--cache-clear",
    -     "--cov=semantic_release",
    -     "--cov-context=test",
    -     "--cov-report",
    -     "html:coverage-html",
    -     "--cov-report",
    -     "term",
      ]

.. note::

    The ``-n0`` option disables ``xdist``'s parallel testing. The removal of the coverage options
    is to avoid a bug in ``pytest-cov`` that prevents VSCode from stopping at the breakpoints.

Building
~~~~~~~~

This project is designed to be versioned and built by itself using the ``tool.semantic_release``
configuration in ``pyproject.toml``. The setting ``tool.semantic_release.build_command`` defines
the command to run to build the package.

The following is a copy of the ``build_command`` setting which can be run manually to build the
package locally:

.. code-block:: bash

    python -m pip install build~=1.2.1
    python -m build .
