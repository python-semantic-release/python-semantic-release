.. _commands:

Commands
--------

.. _cmd-changelog:

changelog
^^^^^^^^^
When executed this command will print the changelog to stderr.

If the option ``--post`` is used then the program will check if
there is a authentication token configured for your vcs provider
(:ref:`env-gh_token` for github, :ref:`env-gl_token` for GitLab)
and it will be posted to the provider if supported.


.. _cmd-publish:

publish
^^^^^^^
Publish will do a sequence of things.

#. Run same as the :ref:`cmd-version` command
#. Push changes to git
#. If :ref:`config-upload_to_pypi` is not ``false`` in the :ref:`configuration`
   it will create the wheel and upload to pypi using twine.
#. If the environment variable :ref:`env-gh_token` (or equivalent for your
   vcs provider) is set then :ref:`cmd-changelog` will be executed and
   the changelog will be posted to your vcs provider if supported.


.. _cmd-version:

version
^^^^^^^
This will figure out the new version number using
:ref:`commit-log-parsing`, and commit + tag in git.

This will not push anything to any remote. All changes
are local.
