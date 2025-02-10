.. _troubleshooting:

Troubleshooting
===============

- Check your configuration file for :ref:`configuration`
- Check your Git tags match your :ref:`tag_format <config-tag_format>`; tags using
  other formats are ignored during calculation of the next version.

.. _troubleshooting-verbosity:

Increasing Verbosity
--------------------

If you are having trouble with Python Semantic Release or would like to see additional
information about the actions that it is taking, you can use the top-level
:ref:`cmd-main-option-verbosity` option. This can be supplied multiple times to increase
the logging verbosity of the :ref:`cmd-main` command or any of its subcommands during
their execution. You can supply this as many times as you like, but supplying more than
twice has no effect.

Supply :ref:`cmd-main-option-verbosity` once for ``INFO`` output, and twice for ``DEBUG``.

For example::

    semantic-release -vv version --print

.. note::
   The :ref:`cmd-main-option-verbosity` option must be supplied to the top-level
   ``semantic-release`` command, before the name of any sub-command.

.. warning::
   The volume of logs when using ``DEBUG`` verbosity may be significantly increased,
   compared to ``INFO`` or the default ``WARNING``, and as a result executing commands
   with ``semantic-release`` may be significantly slower than when using ``DEBUG``.

.. note::
   The provided GitHub action sets the verbosity level to INFO by default.
