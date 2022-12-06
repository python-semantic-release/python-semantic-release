.. _migrating-from-v7:

Migrating from Python Semantic Release v7
=========================================

Python Semantic Release 8.0.0 introduced a number of breaking changes.
The internals have been changed significantly to better support highly-requested
features and to streamline the maintenance of the project.

As a result, certain things have been removed, reimplemented differently, or now
exhibit different behaviour to earlier versions of Python Semantic Release. This
page is a guide to help projects to ``pip install python-semantic-release>=8.0.0`` with
fewer surprises.

.. _breaking-github-action:

Python Semantic Release GitHub Action
-------------------------------------

.. _breaking-github-action-removed-pypi-token:

Removal of ``pypi_token`` input
"""""""""""""""""""""""""""""""
The ``pypi_token`` input of the GitHub action has been removed. You should
supply the token as the value of the ``repository_username`` instead,
and if using only the token for authentication, remember to set the
``repository_username`` input equal to ``__token__``.

.. _breaking-commands:

Commands
--------

.. _breaking-commands-repurposed-version-and-publish:

Repurposing of ``version`` and ``publish`` commands
"""""""""""""""""""""""""""""""""""""""""""""""""""
Python Semantic Release's primary purpose is to enable automation of correct semantic
versioning for software projects. Over the years, this automation has been extended to
include other actions such as building/publishing the project and its artefacts to
artefact repositories, creating releases in remote version control systems, and writing
changelogs.

In Python Semantic Release <8.0.0, the ``publish`` command was a one-stop-shop for
performing every piece of automation provided. This has been changed - the ``version``
command now handles determining the next version, applying the changes to the project
metadata according to the configuration, writing a changelog, and committing/pushing
changes to the remote Git repository. It also handles creating a release in the remote
VCS. It does *not* publish software artefacts to remote repositories such as PyPI, and
it does *not* publish software artefacts to releases in the remote version control
system - this is still handled by the ``publish`` command.

In fact, the ``publish`` command is now just a lightweight wrapper on `twine upload`_,
plus the functionality to publish a software artefact (e.g. a wheel) to a release.

.. _twine upload: https://twine.readthedocs.io/en/stable/#twine-upload

To achieve a similar flow of logic such as

    1. Determine the next version
    2. Write this version to the configured metadata locations
    3. Write the changelog
    4. Push the changes to the metadata and changelog to the remote repository
    5. Create a release in the remote version control system
    6. Build a wheel
    7. Publish the wheel to PyPI and to the release in the remote VCS

You should run::

    semantic-release version && semantic-release publish

With steps 1-5 being handled by the :ref:`cmd-version` command, and steps 6 and 7
handled by the :ref:`cmd-publish` command.

.. _breaking-commands-multibranch-releases:

Multibranch releases
""""""""""""""""""""

Prior to v8, Python Semantic Release would perform ``git checkout`` to switch to your
configured release branch and determine if a release would need to be made. In v8 this
has been changed - you must manually check out the branch which you would like to release
against, and if you would like to create releases against this branch you must also ensure
that it belongs to a :ref:`release group <multibranch-releases-configuring>`.

.. _breaking-commands-changelog:

``changelog`` command
"""""""""""""""""""""
A new option, :ref:`cmd-changelog-option-post-to-release-tag` has been added. If you
omit this argument on the command line then the changelog rendering process, which is
described in more detail at :ref:`changelog-templates-template-rendering`, will be
triggered, but the new changelog will not be posted to any release.
If you use this new command-line option, it should be set to a tag within the remote
which has a corresponding release.
For example, to update the changelog and post it to the release corresponding to the
tag ``v1.1.4``, you should run::

    semantic-release changelog --post-to-release-tag v1.1.4

.. _breaking-changelog-customisation:

Changelog customisation
"""""""""""""""""""""""

A number of options relevant to customising the changelog have been removed. This is
because Python Semantic Release now supports authoring a completely custom `Jinja`_
template with the contents of your changelog.
Historically, the number of options added to Python Semantic Release in order to
allow this customisation has grown significantly; it now uses templates in order to
fully open up customising the changelog's appearance.

.. _Jinja: https://jinja.palletsprojects.com/en/3.1.x/

.. _breaking-configuration:

Configuration
-------------

The configuration structure has been completely reworked, so you should read 
:ref:`configuration` carefully during the process of upgrading to v8+. However,
some common pitfalls and potential sources of confusion are summarised here.

.. _breaking-configuration-setup-cfg-unsupported:

``setup.cfg`` is no longer supported
""""""""""""""""""""""""""""""""""""

Python Semantic Release no longer supports configuration via ``setup.cfg``. This is
because the Python ecosystem is centering around ``pyproject.toml`` as universal tool
and project configuration file, and TOML allows expressions via configuration, such as
the mechanism for declaring configuration via environment variables, which introduce
much greater complexity to support in the otherwise equivalent ``ini``-format
configuration.

You can use :ref:`cmd-generate-config` to generate new-format configuration that can
be added to ``pyproject.toml``, and adjust the default settings according to your
needs.

.. warning::

   If you don't already have a ``pyproject.toml`` configuration file, ``pip`` can
   change its behaviour once you add one, as a result of `PEP-517`_. If you find
   that this breaks your packaging, you can add your Python Semantic Release
   configuration to a separate file such as ``semantic-release.toml``, and use
   the :ref:`--config <cmd-main-option-config>` option to reference this alternative
   configuration file.

   More detail about this issue can be found in this `pip issue`_.

.. _PEP-517: https://peps.python.org/pep-0517/#evolutionary-notes
.. _pip issue: https://github.com/pypa/pip/issues/8437#issuecomment-805313362


.. _breaking-configuration-undeprecating-pypi-token:

``pypi_token`` is un-deprecated
"""""""""""""""""""""""""""""""

As this is passed directly to `twine upload`_, the configuration option has been
un-deprecated for consistency and to avoid confusion.

.. _breaking-commit-parser-options:

Commit parser options
"""""""""""""""""""""

Options such as ``major_emoji``, ``parser_angular_patch_types`` or
``parser_angular_default_level_bump`` have been removed. Instead, these have been
replaced with a single set of recognised commit parser options, ``allowed_tags``,
``major_tags``, ``minor_tags``, and ``patch_tags``, though the interpretation of
these is up to the specific parsers in use. You can read more detail about using
commit parser options in :ref:`commit_parser_options <config-commit-parser-options>`,
and if you need to parse multiple commit styles for a single project it's recommended
that you create a parser following :ref:`commit-parser-writing-your-own-parser` that
is tailored to the specific needs of your project.

.. _breaking-version-variable-rename:

``version_variable``
""""""""""""""""""""

This option has been renamed to :ref:`version_variables <config-version-variables>`
as it refers to a list of variables which can be updated.

.. _breaking-version-pattern-removed:

``version_pattern``
"""""""""""""""""""

This option has been removed. It's recommended to use an alternative tool to perform
substitution using arbitrary regular expressions, such as ``sed``.
You can always use Python Semantic Release to identify the next version to be created
for a project and store this in an environment variable like so::

    export VERSION=$(semantic-release version --print)

.. _breaking-tag-format-validation:

``tag_format``
""""""""""""""

This option has the same effect as it did in Python Semantic Release prior to v8,
but Python Semantic Release will now verify that it has a ``{version}`` format
key and raise an error if this is not the case.

.. _breaking-upload-to-release-rename:

``upload_to_release``
"""""""""""""""""""""

This option has been renamed to
:ref:`upload_to_vcs_release <config-upload-upload-to-vcs-release>`.

.. _breaking-custom-commit-parsers:

Custom Commit Parsers
---------------------

Previously, a custom commit parser had to satisfy the following criteria:

  * It should be ``import``-able from the virtual environment where the
    ``semantic-release`` is run
  * It should be a function which accepts the commit message as its only
    argument and returns a
    :py:class:`semantic_release.history.parser_helpers.ParsedCommit` if the commit is
    parsed successfully, or raise a
    :py:class:`semantic_release.UnknownCommitMessageStyleError` if parsing is
    unsuccessful. 

It is still possible to implement custom commit parsers, but the interface for doing
so has been modified with stronger support for Python type annotations and broader
input provided to the parser to enable capturing more information from each commit,
such as the commit's date and author, if desired. A full guide to implementing a
custom commit parser can be found at :ref:`commit-parser-writing-your-own-parser`.

