.. _configuration:

Configuration
=============

Configuration is read from a file which can be specified using the
:ref:`\\\\-\\\\-config <cmd-main-option-config>` option to :ref:`cmd-main`. Python Semantic
Release currently supports a configuration in either TOML or JSON format, and will
attempt to auto-detect and parse either format.

When using a JSON-format configuration file, Python Semantic Release looks for its
settings beneath a top-level ``semantic_release`` key; when using a TOML-format
configuration file, Python Semantic Release first checks for its configuration under
the table ``[tool.semantic_release]`` (in line with the convention for Python tools to
require their configuration under the top-level ``tool`` table in their
``pyproject.toml`` file), followed by ``[semantic_release]``, which may be more desirable
if using a file other than the default ``pyproject.toml`` for configuration.

The examples on this page are given in TOML format, however there is no limitation on
using JSON instead. In fact, if you would like to convert any example below to its
JSON equivalent, the following commands will do this for you (in Bash):

.. code-block:: bash

    export TEXT="<the TOML to convert>"

    cat <<EOF | python3
    import tomlkit, json
    print(json.dumps(tomlkit.loads('''$TEXT'''), indent=4))
    EOF



A note on null
--------------

In TOML, there is no such thing as a "null" or "nil" value, and this isn't planned
as a language feature according to the relevant `GitHub issue`_.
In Python Semantic Release, options which default to ``None`` are inferred from the
relevant configuration settings not being present at all in your configuration.
Because of this limitation, it's currently not possible to *explicitly* specify those
settings as "null" in TOML-format configuration. Technically it is possible in
JSON-format configuration, but it's recommended to keep consistency and just omit
the relevant settings.

.. _`GitHub issue`: https://github.com/toml-lang/toml/issues/30

.. _config-environment-variables:

Environment Variables
---------------------

Some settings are best pulled from environment variables rather than being stored
in plaintext in your configuration file. Python Semantic Release can be configured
to look for an environment variable value to use for a given setting, but this feature
is not available for all settings. In order to use an environment variable for a setting,
you must indicate in your configuration file the name of the environment variable to use.

The traditional and most common use case for environment variable use is for passing
authentication tokens to Python Semantic Release. You do **NOT** want to hard code your
authentication token in your configuration file, as this is a **security risk**. A plaintext
token in your configuration file could be exposed to anyone with access to your repository,
including long after its deleted if a token is in your git history. Instead, define the name
of the environment variable which contains your :ref:`remote.token <config-remote-token>`,
such as ``GH_TOKEN``, in your configuration file, and Python Semantic Release will do the
rest, as seen below.

.. code-block:: toml

    [tool.semantic_release.remote.token]
    env = "GH_TOKEN"

Given basic TOML syntax compatibility, this is equivalent to:

.. code-block:: toml

    [tool.semantic_release.remote]
    token = { env = "GH_TOKEN" }

The general format for specifying that some configuration should be sourced from an
environment variable is:

.. code-block:: toml

    [tool.semantic_release.<setting>]
    env = "ENV_VAR"
    default_env = "FALLBACK_ENV_VAR"
    default = "default value"

In this structure:
  * ``env`` represents the environment variable that Python Semantic Release will search for
  * ``default_env`` is a fallback environment variable to read in case the variable specified
    by ``env`` is not set. This is optional - if not specified then no fallback will be used.
  * ``default`` is a default value to use in case the environment variable specified by ``env``
    is not set. This is optional - if ``default`` is not specified then the environment variable
    specified by ``env`` is considered required.

.. _config-settings:

Settings
--------

.. _config-root:

``[tool.semantic_release]``
***************************

.. _config-assets:

``assets (List[str])``
""""""""""""""""""""""

One or more paths to additional assets that should committed to the remote repository
in addition to any files modified by writing the new version.

**Default:** ``[]``

.. _config-branches:

``branches``
""""""""""""

This setting is discussed in more detail at :ref:`multibranch-releases`

**Default:**

.. code-block:: toml

    [tool.semantic_release.branches.main]
    match = "(main|master)"
    prerelease_token = "rc"
    prerelease = false

.. _config-build-command:

``build_command (Optional[str])``
"""""""""""""""""""""""""""""""""

Command to use when building the current project during :ref:`cmd-version`

**Default:** ``None`` (not specified)

.. _config-commit_author:

``commit_author (str)``
"""""""""""""""""""""""
Author used in commits in the format ``name <email>``.

.. note::
  If you are using the built-in GitHub Action, the default value is set to
  ``github-actions <actions@github.com>``. You can modify this with the
  ``git_committer_name`` and ``git_committer_name`` inputs.

.. seealso::
   - :ref:`github-actions`

**Default:** ``semantic-release <semantic-release>``

.. _config-commit-message:

``commit_message (str)``
""""""""""""""""""""""""

Commit message to use when making release commits. The message can use ``{version}``
as a format key, in which case the version being released will be formatted into
the message.

If at some point in your project's lifetime you change this, you may wish to consider,
adding the old message pattern(s) to :ref:`exclude_commit_patterns <config-changelog-exclude-commit-patterns>`.

**Default:** ``"{version}\n\nAutomatically generated by python-semantic-release"``

.. _config-commit-parser:

``commit_parser (str)``
"""""""""""""""""""""""

Specify which commit parser Python Semantic Release should use to parse the commits
within the Git repository.

Built-in parsers:
    * ``angular`` - :ref:`AngularCommitParser <commit-parser-angular>`
    * ``emoji`` - :ref:`EmojiCommitParser <commit-parser-emoji>`
    * ``scipy`` - :ref:`ScipyCommitParser <commit-parser-scipy>`
    * ``tag`` - :ref:`TagCommitParser <commit-parser-tag>`

You can set any of the built-in parsers by their keyword but you can also specify
your own commit parser in ``module:attr`` form.

For more information see :ref:`commit-parsing`.

**Default:** ``"angular"``

.. _config-commit-parser-options:

``commit_parser_options (Dict[str, Any])``
""""""""""""""""""""""""""""""""""""""""""

These options are passed directly to the ``parser_options`` method of
:ref:`the commit parser <config-commit-parser>`, without validation
or transformation.

For more information, see :ref:`commit-parsing-parser-options`.

The default value for this setting depends on what you specify as
:ref:`commit_parser <config-commit-parser>`. The table below outlines
the expections from ``commit_parser`` value to default options value.

==================  ==   =================================
``commit_parser``        Default ``commit_parser_options``
==================  ==   =================================
``"angular"``       ->   .. code-block:: toml

                             [tool.semantic_release.commit_parser_options]
                             allowed_types = [
                                 "build", "chore", "ci", "docs", "feat", "fix",
                                 "perf", "style", "refactor", "test"
                             ]
                             minor_types = ["feat"]
                             patch_types = ["fix", "perf"]

``"emoji"``         ->   .. code-block:: toml

                             [tool.semantic_release.commit_parser_options]
                             major_tags = [":boom:"]
                             minor_tags = [
                                 ":sparkles:", ":children_crossing:", ":lipstick:",
                                 ":iphone:", ":egg:", ":chart_with_upwards_trend:"
                             ]
                             patch_tags = [
                                 ":ambulance:", ":lock:", ":bug:", ":zap:", ":goal_net:",
                                 ":alien:", ":wheelchair:", ":speech_balloon:", ":mag:",
                                 ":apple:", ":penguin:", ":checkered_flag:", ":robot:",
                                 ":green_apple:"
                             ]

``"scipy"``         ->   .. code-block:: toml

                             [tool.semantic_release.commit_parser_options]
                             allowed_tags = [
                                "API", "DEP", "ENH", "REV", "BUG", "MAINT", "BENCH",
                                "BLD", "DEV", "DOC", "STY", "TST", "REL", "FEAT", "TEST",
                             ]
                             major_tags = ["API",]
                             minor_tags = ["DEP", "DEV", "ENH", "REV", "FEAT"]
                             patch_tags = ["BLD", "BUG", "MAINT"]

``"tag"``           ->   .. code-block:: toml

                             [tool.semantic_release.commit_parser_options]
                             minor_tag = ":sparkles:"
                             patch_tag = ":nut_and_bolt:"

``"module:class"``  ->   ``**module:class.parser_options()``
==================  ==   =================================

**Default:** ``ParserOptions { ... }``, where ``...`` depends on
:ref:`commit_parser <config-commit-parser>` as indicated above.


.. _config-logging-use-named-masks:

``logging_use_named_masks (bool)``
""""""""""""""""""""""""""""""""""

Whether or not to replace secrets identified in logging messages with named masks
identifying which secrets were replaced, or use a generic string to mask them.

**Default:** ``false``

.. _config-allow-zero-version:

``allow_zero_version (bool)``
"""""""""""""""""""""""""""""

This flag controls whether or not Python Semantic Release will use version
numbers aligning with the ``0.x.x`` pattern.

If set to ``true`` and starting at ``0.0.0``, a minor bump would set the
next version as ``0.1.0`` whereas a patch bump would set the next version as
``0.0.1``. A breaking change (ie. major bump) would set the next version as
``1.0.0`` unless the :ref:`major_on_zero` is set to ``false``.

If set to ``false``, Python Semantic Release will consider the first possible
version to be ``1.0.0``, regardless of patch, minor, or major change level.
Additionally, when ``allow_zero_version`` is set to ``false``,
the :ref:`major_on_zero` setting is ignored.

**Default:** ``true``

.. _config-major-on-zero:

``major_on_zero (bool)``
""""""""""""""""""""""""

This flag controls whether or not Python Semantic Release will increment the major
version upon a breaking change when the version matches ``0.y.z``. This value is
set to ``true`` by default, where breaking changes will increment the ``0`` major
version to ``1.0.0`` like normally expected.

If set to ``false``, major (breaking) releases will increment the minor digit of the
version while the major version is ``0``, instead of the major digit. This allows for
continued breaking changes to be made while the major version remains ``0``.

From the `Semantic Versioning Specification`_:

   Major version zero (0.y.z) is for initial development. Anything MAY change at
   any time. The public API SHOULD NOT be considered stable.

.. _Semantic Versioning Specification: https://semver.org/spec/v2.0.0.html#spec-item-4

When you are ready to release a stable version, set ``major_on_zero`` to ``true`` and
run Python Semantic Release again. This will increment the major version to ``1.0.0``.

When :ref:`allow_zero_version` is set to ``false``, this setting is ignored.

**Default:** ``true``

.. _config-tag-format:

``tag_format (str)``
""""""""""""""""""""

Specify the format to be used for the Git tag that will be added to the repo during
a release invoked via :ref:`cmd-version`. The format string is a regular expression,
which also must include the format keys below, otherwise an exception will be thrown.
It *may* include any of the optional format keys, in which case the contents
described will be formatted into the specified location in the Git tag that is created.

For example, ``"(dev|stg|prod)-v{version}"`` is a valid ``tag_format`` matching tags such
as:

- ``dev-v1.2.3``
- ``stg-v0.1.0-rc.1``
- ``prod-v2.0.0+20230701``

This format will also be used for parsing tags already present in the repository into
semantic versions; therefore if the tag format changes at some point in the
repository's history, historic versions that no longer match this pattern will not be
considered as versions.

================ =========  ========
Format Key       Mandatory  Contents
================ =========  ========
``{version}``    Yes        The new semantic version number, for example ``1.2.3``, or
                            ``2.1.0-alpha.1+build.1234``
================ =========  ========

Tags which do not match this format will not be considered as versions of your project.

**Default:** ``"v{version}"``

.. _config-version-variables:

``version_variables (List[str])``
"""""""""""""""""""""""""""""""""

Each entry represents a location where the version is stored in the source code,
specified in ``file:variable`` format. For example:

.. code-block:: toml

    [tool.semantic_release]
    version_variables = [
        "semantic_release/__init__.py:__version__",
        "docs/conf.py:version",
    ]

**Default:** ``[]``

.. _config-version-toml:

``version_toml (List[str])``
""""""""""""""""""""""""""""
Similar to :ref:`config-version-variables`, but allows the version number to be
identified safely in a toml file like ``pyproject.toml``, with each entry using
dotted notation to indicate the key for which the value represents the version:

.. code-block:: toml

    [tool.semantic_release]
    version_toml = [
        "pyproject.toml:tool.poetry.version",
    ]

**Default:** ``[]``

.. _config-changelog:

``[tool.semantic_release.changelog]``
*************************************

.. _config-changelog-template-dir:

``template_dir (str)``
""""""""""""""""""""""

If given, specifies a directory of templates that will be rendered during creation
of the changelog. If not given, the default changelog template will be used.

This option is discussed in more detail at :ref:`changelog-templates`

**Default:** ``"templates"``

.. _config-changelog-changelog-file:

``changelog_file (str)``
""""""""""""""""""""""""

Specify the name of the changelog file (after template rendering has taken place).

**Default:** ``"CHANGELOG.md"``

.. _config-changelog-exclude-commit-patterns:

``exclude_commit_patterns (List[str])``
"""""""""""""""""""""""""""""""""""""""

Any patterns specified here will be excluded from the commits which are available
to your changelog. This allows, for example, automated commits to be removed if desired.
Python Semantic Release also removes its own commits from the Changelog via this mechanism;
therefore if you change the automated commit message that Python Semantic Release uses when
making commits, you may wish to add the *old* commit message pattern here.

The patterns in this list are treated as regular expressions.

**Default:** ``[]``

.. _config-changelog-environment:

``[tool.semantic_release.changelog.environment]``
*************************************************

.. note::
   This section of the configuration contains options which customize the template
   environment used to render templates such as the changelog. Most options are
   passed directly to the `jinja2.Environment`_ constructor, and further
   documentation one these parameters can be found there.

.. _`jinja2.Environment`: https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment

.. _config-changelog-environment-block-start-string:

``block_start_string (str)``
""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"{%"``

.. _config-changelog-environment-block-end-string:

``block_end_string (str)``
""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"%}"``

.. _config-changelog-environment-variable-start-string:

``variable_start_string (str)``
"""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"{{"``

.. _config-changelog-environment-variable-end-string:

``variable_end_string (str)``
"""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"}}"``

.. _config-changelog-environment-comment-start-string:

``comment_start_string (str)``
""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``{#``

.. _config-changelog-environment-comment-end-string:

``comment_end_string (str)``
""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"#}"``

.. _config-changelog-environment-line-statement-prefix:

``line_statement_prefix (Optional[str])``
"""""""""""""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``None`` (not specified)

.. _config-changelog-environment-line-comment-prefix:

``line_comment_prefix (Optional[str])``
"""""""""""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``None`` (not specified)

.. _config-changelog-environment-trim-blocks:

``trim_blocks (bool)``
""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

.. _config-changelog-environment-lstrip-blocks:

``lstrip_blocks (bool)``
""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

.. _config-changelog-environment-newline-sequence:

``newline_sequence (Literal["\n", "\r", "\r\n"])``
""""""""""""""""""""""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"\n"``

.. _config-changelog-environment-keep-trailing-newline:

``keep_trailing_newline (bool)``
""""""""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

.. _config-changelog-environment-extensions:

``extensions (List[str])``
""""""""""""""""""""""""""

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``[]``


.. _config-changelog-environment-autoescape:

``autoescape (Union[str, bool])``
""""""""""""""""""""""""""""""""""

If this setting is a string, it should be given in ``module:attr`` form; Python
Semantic Release will attempt to dynamically import this string, which should
represent a path to a suitable callable that satisfies the following:

    As of Jinja 2.4 this can also be a callable that is passed the template name
    and has to return ``True`` or ``False`` depending on autoescape should be
    enabled by default.

The result of this dynamic import is passed directly to the `jinja2.Environment`_
constructor.

If this setting is a boolean, it is passed directly to the `jinja2.Environment`_
constructor.

**Default:** ``true``

.. _config-remote:

``[tool.semantic_release.remote]``
**********************************

.. _config-remote-name:

``name (str)``
""""""""""""""

Name of the remote to push to using ``git push -u $name <branch_name>``

**Default:** ``"origin"``

.. _config-remote-type:

``type (str)``
""""""""""""""

The type of the remote VCS. Currently, Python Semantic Release supports ``"github"``,
``"gitlab"``, ``"gitea"`` and ``"bitbucket"``. Not all functionality is available with all
remote types, but we welcome pull requests to help improve this!

**Default:** ``"github"``

.. _config-remote-ignore-token-for-push:

``ignore_token_for_push (bool)``
""""""""""""""""""""""""""""""""

If set to ``True``, ignore the authentication token when pushing changes to the remote.
This is ideal, for example, if you already have SSH keys set up which can be used for
pushing.

**Default:** ``False``

.. _config-remote-token:

``token (Dict['env': str])``
""""""""""""""""""""""""""""

:ref:`Environment Variable <config-environment-variables>` from which to source the
authentication token for the remote VCS. Common examples include ``"GH_TOKEN"``,
``"GITLAB_TOKEN"`` or ``"GITEA_TOKEN"``, however, you may choose to use a custom
environment variable if you wish.

.. note::
   By default, this is a **mandatory** environment variable that must be set before
   using any functionality that requires authentication with your remote VCS. If you
   are using this token to enable push access to the repository, it must also be set
   before attempting to push.

   If your push access is enabled via SSH keys instead, then you do not need to set
   this environment variable in order to push the version increment, changelog and
   modified source code assets to the remote using :ref:`cmd-version`. However,
   you will need to disable release creation using the :ref:`cmd-version-option-vcs-release`
   option, among other options, in order to use Python Semantic Release without
   configuring the environment variable for your remote VCS authentication token.


The default value for this setting depends on what you specify as
:ref:`remote.type <config-remote-type>`. Review the table below to see what the
default token value will be for each remote type.

================  ==  ===============================
``remote.type``       Default ``remote.token``
================  ==  ===============================
``"github"``      ->  ``{ env = "GH_TOKEN" }``
``"gitlab"``      ->  ``{ env = "GITLAB_TOKEN" }``
``"gitea"``       ->  ``{ env = "GITEA_TOKEN" }``
``"bitbucket"``   ->  ``{ env = "BITBUCKET_TOKEN" }``
================  ==  ===============================

**Default:** ``{ env = "<envvar name>" }``, where ``<envvar name>`` depends on
:ref:`remote.type <config-remote-type>` as indicated above.


.. _config-publish:

``[tool.semantic_release.publish]``
***********************************

.. _config-publish-dist-glob-patterns:

``dist_glob_patterns (List[str])``
""""""""""""""""""""""""""""""""""

Upload any files matching any of these globs to your VCS release. Each item in this
list should be a string containing a Unix-style glob pattern.

**Default:** ``["dist/*"]``

.. _config-publish-upload-to-vcs-release:

``upload_to_vcs_release (bool)``
""""""""""""""""""""""""""""""""

If set to ``true``, upload any artifacts matched by the
:ref:`dist_glob_patterns <config-publish-dist-glob-patterns>` to the release created
in the remote VCS corresponding to the latest tag. Artifacts are only uploaded if
release artifact uploads are supported by the :ref:`VCS type <config-remote-type>`.

**Default:** ``true``
