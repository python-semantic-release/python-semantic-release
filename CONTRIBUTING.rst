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

Install this module and the development dependencies::

    pip install -e ".[test,dev]"

And if you'd like to build the documentation locally::

    pip install -e ".[docs]"

Testing
~~~~~~~

To test your modifications locally:

::

    tox
