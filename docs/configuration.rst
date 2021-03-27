.. _configuration:

Configuration
*************

Configuration options can be given in three ways:

- ``setup.cfg`` file in a ``[semantic_release]`` section
- ``pyproject.toml`` file in a ``[tool.semantic_release]`` section
- ``-D`` option, like so::

    semantic-release <command> -D <option_name>=<option_value>

Each location has priority over the ones listed above it.


Releases
========

.. _config-branch:

``branch``
----------
The branch to run releases from.

Default: `master`

.. _config-version_variable:

``version_variable``
--------------------
The file and variable name of where the version number is stored, for example::

    semantic_release/__init__.py:__version__

You can specify multiple version variables (i.e. in different files) by 
providing comma-separated list of such strings::

    semantic_release/__init__.py:__version__,docs/conf.py:version

In ``pyproject.toml`` specifically, you can also use the TOML list syntax to 
specify multiple versions:

.. code-block:: toml

    [tool.semantic_release]
    version_variable = [
        'semantic_release/__init__.py:__version__',
        'docs/conf.py:version',
    ]

.. _config-version_toml:

``version_toml``
-------------------
Similar to :ref:`config-version_variable`, but allows the version number to be
identified safely in a toml file like ``pyproject.toml``, using a dotted notation to the key path::

    pyproject.toml:tool.poetry.version

.. _config-version_pattern:

``version_pattern``
-------------------
Similar to :ref:`config-version_variable`, but allows the version number to be
identified using an arbitrary regular expression::

    README.rst:VERSION (\d+\.\d+\.\d+)

The regular expression must contain a parenthesized group that matches the 
version number itself.  Anything outside that group is just context.  For 
example, the above specifies that there is a version number in ``README.rst`` 
preceded by the string "VERSION".

If the pattern contains the string ``{version}``, it will be replaced with the 
regular expression used internally by ``python-semantic-release`` to match 
semantic version numbers.  So the above example would probably be better 
written as::

    README.rst:VERSION {version}

As with :ref:`config-version_variable`, it is possible to specify multiple version
patterns in ``pyproject.toml``.

.. _config-version_source:

``version_source``
------------------
The way we get and set the new version. Can be `commit` or `tag`.

- If set to `tag`, will get the current version from the latest tag matching ``vX.Y.Z``.
  This won't change the source defined in :ref:`config-version_variable`.
- If set to `commit`, will get the current version from the source defined in
  :ref:`config-version_variable`, edit the file and commit it.

Default: `commit`

.. _config-patch_without_tag:

``patch_without_tag``
---------------------
If this is set to `true`, semantic-release will create a new patch release even if there is
no tag in any commits since the last release.

Default: `false`

``major_on_zero``
-----------------
If this is set to `false`, semantic-release will create a new minor release
instead of major release when current major version is zero.

Quote from `Semantic Versioning Specification`_:

  Major version zero (0.y.z) is for initial development. Anything MAY change at
  any time. The public API SHOULD NOT be considered stable.

.. _Semantic Versioning Specification: https://semver.org/spec/v2.0.0.html#spec-item-4

If you do not want to bump version to 1.0.0 from 0.y.z automatically, you can
set this option to `false`.

Default: `true`.

Commit Parsing
==============

.. _config-commit_parser:

``commit_parser``
-----------------
Import path of a Python function that can parse commit messages and return
information about the commit as described in :ref:`commit-log-parsing`.

The following parsers are built in to Python Semantic Release:

- :py:func:`semantic_release.history.angular_parser`

  The default parser, which uses the `Angular commit style <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits>`_ with the following differences:

  - Multiple ``BREAKING CHANGE:`` paragraphs are supported
  - ``revert`` is not currently supported

- :py:func:`semantic_release.history.emoji_parser`

  Parser for commits using one or more emojis as tags in the subject line.

  If a commit contains multiple emojis, the one with the highest priority
  (major, minor, patch, none) or the one listed first is used as the changelog
  section for that commit. Commits containing no emojis go into an "Other"
  section.

  See :ref:`config-major_emoji`, :ref:`config-minor_emoji` and
  :ref:`config-patch_emoji`. The default settings are for
  `Gitmoji <https://gitmoji.carloscuesta.me/>`_.

- :py:func:`semantic_release.history.tag_parser`

  The original parser from v1.0.0 of Python Semantic Release. Similar to the
  emoji parser above, but with less features.

.. _config-major_emoji:

``major_emoji``
---------------

Comma-separated list of emojis used by :py:func:`semantic_release.history.emoji_parser` to
create major releases.

Default: `:boom:`

.. _config-minor_emoji:

``minor_emoji``
---------------

Comma-separated list of emojis used by :py:func:`semantic_release.history.emoji_parser` to
create minor releases.

Default: `:sparkles:, :children_crossing:, :lipstick:, :iphone:, :egg:, :chart_with_upwards_trend:`

.. _config-patch_emoji:

``patch_emoji``
---------------

Comma-separated list of emojis used by :py:func:`semantic_release.history.emoji_parser` to
create patch releases.

Default: `:ambulance:, :lock:, :bug:, :zap:, :goal_net:, :alien:, :wheelchair:, :speech_balloon:, :mag:, :apple:, :penguin:, :checkered_flag:, :robot:, :green_apple:`

Commits
=======

.. _config-commit_version_number:

``commit_version_number``
-------------------------
Whether or not to commit changes when bumping version.

Default: True if :ref:`config-version_source` is `tag`, False if :ref:`config-version_source` is `commit`

.. _config-commit_subject:

``commit_subject``
------------------
Git commit subject line. Accepts the following variables as format fields:

================  ========
Variable          Contents
================  ========
``{version}``     The new version number in the format ``X.Y.Z``.
================  ========

Default: ``{version}``

.. _config-commit_message:

``commit_message``
------------------
Git commit message body. Accepts the following variables as format fields:

================  ========
Variable          Contents
================  ========
``{version}``     The new version number in the format ``X.Y.Z``.
================  ========

Default: `Automatically generated by python-semantic-release`

.. _config-commit_author:

``commit_author``
-----------------
Author used in commits in the format ``name <email>``.

Default: ``semantic-release <semantic-release>``

.. note::
  If you are using the built-in GitHub Action, this is always set to
  ``github-actions <actions@github.com>``.

Changelog
=========

.. _config-changelog_sections:

``changelog_sections``
-----------------------
Comma-separated list of sections to display in the changelog.
They will be displayed in the order they are given.

The available options depend on the commit parser used.

Default: `feature, fix, breaking, documentation, performance` plus all
the default emojis for :py:class:`semantic_release.history.emoji_parser`.

.. _config-changelog_components:

``changelog_components``
------------------------
A comma-separated list of the import paths of components to include in the
changelog.

The following components are included in Python Semantic Release:

- :py:func:`semantic_release.changelog.changelog_headers`

  **Only component displayed by default.**

  List of commits between this version and the previous one, with sections and
  headings for each type of change present in the release.

- :py:func:`semantic_release.changelog.changelog_table`

  List of commits between this version and the previous one, dsplayed in a
  table.

- :py:func:`semantic_release.changelog.compare_url`

  Link to view a comparison between this release and the previous one on
  GitHub. Only appears when running through :ref:`cmd-publish`.

  If you are using a different HVCS, the link will not be included.

It is also possible to create your own components. Each component is simply a
function which returns a string, or ``None`` if it should be skipped, and may
take any of the following values as keyword arguments:

+------------------------+------------------------------------------------------------------------+
| ``changelog``          | A dictionary with section names such as ``feature`` as keys, and the   |
|                        | values are lists of (SHA, message) tuples. There is a special section  |
|                        | named ``breaking`` for breaking changes, where the same commit can     |
|                        | appear more than once with a different message.                        |
+------------------------+------------------------------------------------------------------------+
| ``changelog_sections`` | A list of sections from ``changelog`` which the user has set to be     |
|                        | displayed.                                                             |
+------------------------+------------------------------------------------------------------------+
| ``version``            | The current version number in the format ``X.X.X``, or the new version |
|                        | number when publishing.                                                |
+------------------------+------------------------------------------------------------------------+
| ``previous_version``   | The previous version number. Only present when publishing, ``None``    |
|                        | otherwise.                                                             |
+------------------------+------------------------------------------------------------------------+

You can should use ``**kwargs`` to capture any arguments you don't need.

.. _config-changelog_file:

``changelog_file``
------------------
The name of the file where the changelog is kept, relative to the root of the repo.

If this file doesn't exist, it will be created.

Default: ``CHANGELOG.md``.

``changelog_placeholder``
-------------------------
A placeholder used to inject the changelog of the current release in the :ref:`config-changelog_file`.

If the placeholder isn't present in the file, a warning will be logged and nothing
will be updated.

Default: ``<!--next-version-placeholder-->``.

.. _config-changelog_scope:

``changelog_scope``
-------------------------
If set to false, `**scope:**` (when scope is set for a commit) will not be
prepended to the description when generating the changelog.

Default: ``True``.

``changelog_capitalize``
-------------------------
If set to false commit messages will not be automatically capitalized when generating the changelog.

Default: ``True``.

Distributions
=============

.. _config-upload_to_pypi:

``upload_to_pypi``
------------------
If set to false the pypi uploading will be disabled.
See :ref:`env-pypi_token` which must also be set for this to work.

.. _config-upload_to_pypi_glob_patterns:

``upload_to_pypi_glob_patterns``
------------------
A comma `,` separated list of glob patterns to use when uploading to pypi.

Default: `*`

.. _config-repository:

``repository``
------------------
The repository (package index) to upload to. Should be a section in the ``.pypirc`` file.

.. _config-upload_to_release:

``upload_to_release``
---------------------
If set to false, do not upload distributions to GitHub releases.
If you are not using GitHub, this will be skipped regardless.

.. _config-dist_path:

``dist_path``
-------------
The relative path to the folder for dists configured for setuptools. This allows for
customized setuptools processes.

Default: `dist/`

.. _config-remove_dist:

``remove_dist``
---------------
Flag for whether the dist folder should be removed after a release.

Default: `true`

.. _config-build_command:

``build_command``
-----------------
Command to build dists. Build output should be stored in the directory configured in
``dist_path``.  If necessary, multiple commands can be specified using ``&&``, e.g.
``pip install -m flit && flit build``. If set to false, build command is disabled and
files should be placed manually in the directory configured in
``dist_path``.

Default: ``python setup.py sdist bdist_wheel``

HVCS
====

.. _config-hvcs:

``hvcs``
--------
The name of your hvcs. Currently only ``github`` and ``gitlab`` are supported.

Default: `github`

.. _config-check_build_status:

``check_build_status``
----------------------
If enabled, the status of the head commit will be checked and a release will only be created
if the status is success.

Default: `false`
