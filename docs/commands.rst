.. _commands:

Commands
--------

.. _cmd-changelog:

changelog
^^^^^^^^^
When executed this command will print the changelog to stdout.

If the option ``--post`` is used then the program will check if
there is a authentication token configured for your vcs provider
(`GH_TOKEN` for github) and it will be posted to the provider
if supported.


.. _cmd-publish:

publish
^^^^^^^
Publish will do a sequence of things.

#. Run same as the :ref:`cmd-version` command
#. Push changes to git
#. If ``upload_to_pypi`` is not ``false`` in the :ref:`configuration`
   it will create the wheel and upload to pypi using twine.
#. If the environment variable ``GH_TOKEN`` (or equivalent for your
   vcs provider) is set then :ref:`cmd-changelog` will be executed and
   the changelog will be posted to your vcs provider if supported.


.. _cmd-version:

version
^^^^^^^
This will figure out the new version number using
:ref:`commit-log-parsing`, and commit + tag in git.

This will not push anything to any remote. All changes
are local.
