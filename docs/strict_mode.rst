.. _strict-mode:

Strict Mode
===========

Strict Mode is enabled by use of the :ref:`strict <cmd-main-option-strict>` parameter
to the main command for Python Semantic Release. Strict Mode alters the behavior of
Python Semantic Release when certain conditions are encountered that prevent Python
Semantic Release from performing an action. Typically, this will result in a warning
becoming an error, or a different exit code (0 vs non-zero) being produced when Python
Semantic Release exits early.

For example:

.. code-block:: bash

   #!/usr/bin/bash

   set -euo pipefail

   git checkout $NOT_A_RELEASE_BRANCH

   pip install \
      black \
      isort \
      twine \
      pytest \
      python-semantic-release

   isort .  # sort imports
   black .  # format the code
   pytest   # test the code
   semantic-release --strict version  # ERROR - not a release branch
   twine upload dist/*  # publish the code


Using Strict Mode with the ``--strict`` flag ensures this simple pipeline will fail
while running ``semantic-release``, as the non-zero exit code will cause it to stop
when combined with the ``-e`` option.

Without Strict Mode, the ``semantic-release`` command will exit with code 0, causing
the above pipeline to continue.

The specific effects of enabling Strict Mode are detailed below.

.. _strict-mode-not-a-release-branch:

Non-Release Branches
~~~~~~~~~~~~~~~~~~~~

When running in Strict Mode, invoking Python Semantic Release on a non-Release
branch will cause an error with a non-zero exit code. This means that you can
prevent an automated script from running further against branches you do not
want to release from, for example in multibranch CI pipelines.

Running without Strict Mode will allow subsequent steps in the pipeline to also
execute, but be aware that certain actions that Python Semantic Release may
perform for you will likely not have been carried out, such as writing to files
or creating a git commit in your repository.

.. seealso::
   - :ref:`multibranch-releases`

.. _strict-mode-version-already-released:

Version Already Released/No Release To Be Made
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Strict Mode is not enabled and Python Semantic Release identifies that
no release needs to be made, it will exit with code 0. You can cause Python
Semantic Release to raise an error if no release needs to be made by enabling
Strict Mode.
