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


.. _cmd-publish:

``semantic-release publish``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Publish will do a sequence of things:

#. Run :ref:`cmd-version`.
#. Push changes to git.
#. Run :ref:`config-build_command` and upload the created files to PyPI.
#. Run :ref:`cmd-changelog` and post to your vcs provider.
#. Attach the files created by :ref:`config-build_command` to GitHub releases.

Some of these steps may be disabled based on your configuration.
