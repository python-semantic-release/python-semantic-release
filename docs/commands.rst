.. _commands:

Commands
--------

.. _cmd-changelog:

``semantic-release changelog``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Print the changelog to stdout.

If the option ``--post`` is used and there is an authentication token configured
for your vcs provider (:ref:`env-gh_token` for GitHub, :ref:`env-gl_token` for
GitLab), the changelog will be posted there too.


.. _cmd-version:

``semantic-release version``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Figure out the new version number, update and commit it, and create a tag.

This will not push anything to any remote. All changes are local.

.. _cmd-print-version:

``semantic-release print-version``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Print to standard output the new version number.

If the option ``--current`` is used, it will display the current version number.

It can be used to retrieve the next version number in a shell script during the build, before running the effective
release, ie. to rename a distribution binary with the effective version::

    VERSION=$(semantic-release print-version)

.. _cmd-publish:

``semantic-release publish``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Publish will do a sequence of things:

#. Update changelog file.
#. Run :ref:`cmd-version`.
#. Push changes to git.
#. Run :ref:`config-build_command` and upload the created files to PyPI.
#. Run :ref:`cmd-changelog` and post to your vcs provider.
#. Attach the files created by :ref:`config-build_command` to GitHub releases.

Some of these steps may be disabled based on your configuration.

Common Options
~~~~~~~~~~~~~~

Every command understands these flags:

``--patch``
...........

Force a patch release, ignoring the version bump determined from commit messages.

``--minor``
...........

Force a minor release, ignoring the version bump determined from commit messages.

``--major``
...........

Force a major release, ignoring the version bump determined from commit messages.

``--noop``
..........

No operations mode. Do not take any actions, only print what will be done.

``--retry``
...........

Retry the same release, do not bump.

``--define``
............

Override a configuration value. Takes an argument of the format
``setting="value"``.

``--verbosity``
...............

Change the verbosity of Python Semantic Release's logging. See :ref:`debug-usage`.
