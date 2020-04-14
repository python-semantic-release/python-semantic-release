.. _troubleshooting:

Troubleshooting
***************
Things to check...

- Check setup.cfg for :ref:`configuration`
- Check all applicable :ref:`envvars`
- Git tags beginning with ``v``. This is, depending on configuration, used
  for getting the last version.

.. _debug-usage:

Showing debug output
====================
If you are having trouble with `semantic-release` there is a way to get more
information during it's work.

By setting the ``--verbosity`` option to ``DEBUG`` you can display information
from the inner workings of semantic-release.

.. note::
  Debug output is always enabled on GitHub Actions using the built-in action.

::

    semantic-release changelog --verbosity DEBUG
