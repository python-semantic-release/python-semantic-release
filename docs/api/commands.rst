.. _commands:

Command Line Interface (CLI)
============================

All commands accept a ``-h/--help`` option, which displays the help text for the
command and exits immediately.

``semantic-release`` does not allow interspersed arguments and options, which
means that the options for ``semantic-release`` are not necessarily accepted
one of the subcommands. In particular, the :ref:`cmd-main-option-noop` and
:ref:`cmd-main-option-verbosity` flags must be given to the top-level
``semantic-release`` command, before the name of the subcommand.

For example:

Incorrect::

   semantic-release version --print --noop -vv

Correct::

   semantic-release -vv --noop version --print

With the exception of :ref:`cmd-main` and :ref:`cmd-generate-config`, all
commands require that you have set up your project's configuration.

To help with setting up your project configuration, :ref:`cmd-generate-config`
will print out the default configuration to the console, which
you can then modify it to match your project & environment.

.. _cmd-main:

``semantic-release``
~~~~~~~~~~~~~~~~~~~~

.. _cmd-main-options:

Options:
--------

.. _cmd-main-option-version:

``--version``
**************

Display the version of Python Semantic Release and exit

.. _cmd-main-option-noop:

``--noop``
**********

Use this flag to see what ``semantic-release`` intends to do without making changes
to your project. When using this option, ``semantic-release`` can be run as many times
as you wish without any side-effects.

.. _cmd-main-option-verbosity:

``-v/--verbose``
******************

Can be supplied more than once. Controls the verbosity of ``semantic-releases`` logging
output (default level is ``WARNING``, use ``-v`` for ``INFO`` and ``-vv`` for ``DEBUG``).

.. _cmd-main-option-config:

``-c/--config [FILE]``
**********************

Specify the configuration file which Python Semantic Release should use. This can
be any of the supported formats valid for :ref:`cmd-generate-config-option-format`

**Default:** pyproject.toml

.. seealso::
   - :ref:`configuration`

.. _cmd-main-option-strict:

``--strict``
************

Enable Strict Mode. This will cause a number of conditions to produce a non-zero
exit code when passed, where they would otherwise have produced an exit code of 0.
Enabling this allows, for example, certain conditions to cause failure of a CI
pipeline, while omitting this flag would allow the pipeline to continue to run.

.. seealso::
   - :ref:`strict-mode`


.. _cmd-version:

``semantic-release version``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Detect the semantically correct next version that should be applied to your
project and release it.

By default (in order):

  #.  Write this new version to the project metadata locations
      specified in the configuration file

  #.  Update the changelog file with the new version and any changes
      introduced since the last release, using the configured changelog template

  #.  Build the project using :ref:`config-build_command`, if specified

  #.  Create a new commit with these locations and any other assets configured
      to be included in a release

  #.  Tag this commit according the configured format, with a tag that uniquely
      identifies the version being released

  #.  Push the new tag and commit to the remote for the repository

  #.  Create a release in the remote VCS for this tag (if supported)

.. note::

  Before pushing changes to the remote (step 6), Python Semantic Release automatically
  verifies that the upstream branch has not changed since the commit that triggered
  the release. This prevents push conflicts when another commit was made to the
  upstream branch while the release was being prepared. If the upstream branch has
  changed, the command will exit with an error, and you will need to pull the latest
  changes and run the command again.

  This verification only occurs when committing changes (``--commit``). If you are
  running with ``--no-commit``, the verification will not be performed.

All of these steps can be toggled on or off using the command line options
described below. Some of the steps rely on others, so some options may implicitly
disable others.

Changelog generation is done identically to the way it is done in :ref:`cmd-changelog`,
but this command additionally ensures the updated changelog is included in the release
commit that is made.

  **Common Variations**

  .. code-block:: bash

    # Print the next version that will be applied
    semantic-release version --print

    # Print the next version that will be applied, including the tag prefix
    semantic-release version --print-tag

    # Print the last released version
    semantic-release version --print-last-released

    # Print the last released version, including the tag prefix
    semantic-release version --print-last-released-tag

    # Only stamp the next version in the project metadata locations
    semantic-release version --no-changelog --skip-build --no-commit --no-tag

    # Stamp the version, update the changelog, and run the build command, then stop
    semantic-release version --no-commit --no-tag

    # Make all local changes but do not publish them to the remote (changelog, build, commit & tag)
    semantic-release version --no-push

    # Don't ever create a changelog (but do everything else)
    semantic-release version --no-changelog

    # Don't create a release in the remote VCS (but do publish the commit and tag)
    semantic-release version --no-vcs-release

    # Do everything
    semantic-release version


.. seealso::
    - :ref:`Ultraviolet (uv) integration <config-guides-uv_integration>`
    - :ref:`cmd-changelog`
    - :ref:`changelog-templates`
    - :ref:`config-tag_format`
    - :ref:`config-assets`
    - :ref:`config-version_toml`
    - :ref:`config-version_variables`


.. _cmd-version-options:

Options:
--------

.. _cmd-version-option-print:

``--print``
***********

Print the next version that will be applied, respecting the other command line options
that are supplied, and exit. This flag is useful if you just want to see what the next
version will be.
Note that instead of printing nothing at all, if no release will be made, the current
version is printed.

For example, you can experiment with which versions would be applied using the other
command line options::

    semantic-release version --print
    semantic-release version --patch --print
    semantic-release version --prerelease --print

.. _cmd-version-option-print-tag:

``--print-tag``
***************

Same as the :ref:`cmd-version-option-print` flag but prints the complete tag
name (ex. ``v1.0.0`` or ``py-v1.0.0``) instead of the raw version number
(``1.0.0``).

.. _cmd-version-option-print-last-released:

``--print-last-released``
*************************

Print the last released version based on the Git tags.  This flag is useful if you just
want to see the released version without determining what the next version will be.
Note if the version can not be found nothing will be printed.

.. _cmd-version-option-print-last-released-tag:

``--print-last-released-tag``
*****************************

Same as the :ref:`cmd-version-option-print-last-released` flag but prints the
complete tag name (ex. ``v1.0.0`` or ``py-v1.0.0``) instead of the raw version
number (``1.0.0``).

.. _cmd-version-option-force-level:

``--major/--minor/--patch/--prerelease``
****************************************

Force the next version to increment the major, minor or patch digits, or the prerelease revision,
respectively. These flags are optional but mutually exclusive, so only one may be supplied, or
none at all. Using these flags overrides the usual calculation for the next version; this can
be useful, say, when a project wants to release its initial 1.0.0 version.

.. warning::

    Using these flags will override the configured value of ``prerelease`` (configured
    in your :ref:`Release Group<multibranch-releases-configuring>`),
    **regardless of your configuration or the current version**.

    To produce a prerelease with the appropriate digit incremented you should also
    supply the :ref:`cmd-version-option-as-prerelease` flag. If you do not, using these flags will force
    a full (non-prerelease) version to be created.

For example, suppose your project's current version is ``0.2.1-rc.1``. The following
shows how these options can be combined with ``--as-prerelease`` to force different
versions:

.. code-block:: bash

   semantic-release version --prerelease --print
   # 0.2.1-rc.2

   semantic-release version --patch --print
   # 0.2.2

   semantic-release version --minor --print
   # 0.3.0

   semantic-release version --major --print
   # 1.0.0

   semantic-release version --minor --as-prerelease --print
   # 0.3.0-rc.1

   semantic-release version --prerelease --as-prerelease --print
   # 0.2.1-rc.2

These options are forceful overrides, but there is no action required for subsequent releases
performed using the usual calculation algorithm.

Supplying ``--prerelease`` will cause Python Semantic Release to scan your project history
for any previous prereleases with the same major, minor and patch versions as the latest
version and the same :ref:`prerelease token<cmd-version-option-prerelease-token>` as the
one passed by command-line or configuration. If one is not found, ``--prerelease`` will
produce the next version according to the following format:

.. code-block:: python

    f"{latest_version.major}.{latest_version.minor}.{latest_version.patch}-{prerelease_token}.1"

However, if Python Semantic Release identifies a previous *prerelease* version with the same
major, minor and patch digits as the latest version, *and* the same prerelease token as the
one supplied by command-line or configuration, then Python Semantic Release will increment
the revision found on that previous prerelease version in its new version.

For example, if ``"0.2.1-rc.1"`` and already exists as a previous version, and the latest version
is ``"0.2.1"``, invoking the following command will produce ``"0.2.1-rc.2"``:

.. code-block:: bash

   semantic-release version --prerelease --prerelease-token "rc" --print

.. warning::

   This is true irrespective of the branch from which ``"0.2.1-rc.1"`` was released from.
   The check for previous prereleases "leading up to" this normal version is intended to
   help prevent collisions in git tags to an extent, but isn't foolproof. As the example
   shows it is possible to release a prerelease for a normal version that's already been
   released when using this flag, which would in turn be ignored by tools selecting
   versions by `SemVer precedence rules`_.


.. _SemVer precedence rules: https://semver.org/#spec-item-11


.. seealso::
    - :ref:`configuration`
    - :ref:`config-branches`

.. _cmd-version-option-as-prerelease:

``--as-prerelease``
*******************

After performing the normal calculation of the next version, convert the resulting next version
to a prerelease before applying it. As with :ref:`cmd-version-option-force-level`, this option
is a forceful override, but no action is required to resume calculating versions as normal on the
subsequent releases. The main distinction between ``--prerelease`` and ``--as-prerelease`` is that
the latter will not *force* a new version if one would not have been released without supplying
the flag.

This can be useful when making a single prerelease on a branch that would typically release
normal versions.

If not specified in :ref:`cmd-version-option-prerelease-token`, the prerelease token is identified
using the :ref:`Multibranch Release Configuration <multibranch-releases-configuring>`

See the examples alongside :ref:`cmd-version-option-force-level` for how to use this flag.

.. _cmd-version-option-prerelease-token:

``--prerelease-token [VALUE]``
******************************

Force the next version to use the value as the prerelease token. This overrides the configured
value if one is present. If not used during a release producing a prerelease version, this
option has no effect.

.. _cmd-version-option-build-metadata:

``--build-metadata [VALUE]``
****************************

If given, append the value to the newly calculated version. This can be used, for example,
to attach a run number from a CI service or a date to the version and tag that are created.

This value can also be set using the environment variable ``PSR_BUILD_METADATA``

For example, assuming a project is currently at version 1.2.3::

    $ semantic-release version --minor --print
    1.3.0

    $ semantic-release version --minor --print --build-metadata "run.12345"
    1.3.0+run.12345

.. _cmd-version-option-commit:

``--commit/--no-commit``
************************

Whether or not to perform a ``git commit`` on modifications to source files made by ``semantic-release`` during this
command invocation, and to run ``git tag`` on this new commit with a tag corresponding to the new version.

If ``--no-commit`` is supplied, it may disable other options derivatively; please see below.

**Default:** ``--commit``

.. seealso::
   - :ref:`tag_format <config-tag_format>`

.. _cmd-version-option-tag:

``--tag/--no-tag``
************************

Whether or not to perform a ``git tag`` to apply a tag of the corresponding to the new version during this
command invocation. This option manages the tag application separate from the commit handled by the ``--commit``
option.

If ``--no-tag`` is supplied, it may disable other options derivatively; please see below.

**Default:** ``--tag``

.. _cmd-version-option-changelog:

``--changelog/--no-changelog``
******************************

Whether or not to update the changelog file with changes introduced as part of the new
version released.

**Default:** ``--changelog``

.. seealso::
    - :ref:`config-changelog`
    - :ref:`changelog-templates`

.. _cmd-version-option-push:

``--push/--no-push``
********************

Whether or not to push new commits and/or tags to the remote repository.

**Default:** ``--no-push`` if :ref:`--no-commit <cmd-version-option-commit>` and
:ref:`--no-tag <cmd-version-option-tag>` is also supplied, otherwise ``push`` is the default.

.. _cmd-version-option-vcs-release:

``--vcs-release/--no-vcs-release``
**********************************

Whether or not to create a "release" in the remote VCS service, if supported. If
releases aren't supported in a remote VCS, this option will not cause a command
failure, but will produce a warning.

**Default:** ``--no-vcs-release`` if ``--no-push`` is supplied (including where this is
implied by supplying only ``--no-commit``), otherwise ``--vcs-release``

.. _cmd-version-option-skip_build:

``--skip-build``
****************

If passed, skip execution of the :ref:`build_command <config-build_command>` after
version stamping and changelog generation.

.. _cmd-publish:

``semantic-release publish``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Publish a distribution to a VCS release. Uploads using :ref:`config-publish`

.. seealso::
    - :ref:`config-publish`
    - :ref:`config-build_command`

.. _cmd-publish-options:

Options:
--------

.. _cmd-publish-option-tag:

``--tag``
*********

The tag associated with the release to publish to. If not given or set to
"latest", then Python Semantic Release will examine the Git tags in your
repository to identify the latest version, and attempt to publish to a
Release corresponding to this version.

**Default:** "latest"

.. _cmd-generate-config:

``semantic-release generate-config``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate default configuration for semantic-release, to help you get started
quickly. You can inspect the defaults, write to a file and then edit according to
your needs. For example, to append the default configuration to your ``pyproject.toml``
file, you can use the following command (in POSIX-Compliant shells):

.. code-block:: bash

    semantic-release generate-config --pyproject >> pyproject.toml

On Windows PowerShell, the redirection operators (`>`/`>>`) default to UTF-16LE,
which can introduce NUL characters. Prefer one of the following to keep UTF-8:

.. code-block:: console

    # 2 File output Piping Options in PowerShell (Out-File or Set-Content)

    # Example for writing to pyproject.toml using Out-File:
    semantic-release generate-config --pyproject | Out-File -Encoding utf8 pyproject.toml

    # Example for writing to a releaserc.toml file using Set-Content:
    semantic-release generate-config -f toml | Set-Content -Encoding utf8 releaserc.toml

If your project doesn't already leverage TOML files for configuration, it might better
suit your project to use JSON instead:

.. code-block:: bash

    # POSIX-Compliant shell example
    semantic-release generate-config -f json | tee releaserc.json

    # Windows PowerShell example
    semantic-release generate-config -f json | Out-File -Encoding utf8 releaserc.json

If you would like to add JSON configuration to a shared file, e.g. ``package.json``, you
can then simply add the output from this command as a **top-level** key to the file.

**Note:** Because there is no "null" or "nil" concept in TOML (see the relevant
`GitHub issue`_), configuration settings which are ``None`` by default are omitted
from the default configuration.

.. _`GitHub issue`: https://github.com/toml-lang/toml/issues/30

.. seealso::
    - :ref:`configuration`

.. _cmd-generate-config-options:

Options:
--------

.. _cmd-generate-config-option-format:

``-f/--format [FORMAT]``
************************

The format that the default configuration should be generated in. Valid choices are
``toml`` and ``json`` (case-insensitive).

**Default:** toml

.. _cmd-generate-config-option-pyproject:

``--pyproject``
***************

If used alongside ``--format json``, this option has no effect. When using
``--format=toml``, if specified the configuration will sit under a top-level key
of ``tool.semantic_release`` to comply with `PEP 518`_; otherwise, the configuration
will sit under a top-level key of ``semantic_release``.

.. _PEP 518: https://peps.python.org/pep-0518/#tool-table


.. _cmd-changelog:

``semantic-release changelog``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate and optionally publish a changelog for your project. The changelog
is generated based on a template which can be customized.

Python Semantic Release uses Jinja_ as its templating engine; as a result templates
need to be written according to the `Template Designer Documentation`_.

.. _Jinja: https://jinja.palletsprojects.com/
.. _`Template Designer Documentation`: https://jinja.palletsprojects.com/en/3.1.x/templates/

.. seealso::
    - :ref:`config-changelog`
    - :ref:`config-changelog-environment`
    - :ref:`changelog-templates`

Options:
--------

.. _cmd-changelog-option-post-to-release-tag:

``--post-to-release-tag [TAG]``
*******************************

If supplied, attempt to find a release in the remote VCS corresponding to the Git tag
``TAG``, and post the generated changelog to that release. If the tag exists but no
corresponding release is found in the remote VCS, then Python Semantic Release will
attempt to create one.

If using this option, the relevant authentication token *must* be supplied via the
relevant environment variable.
