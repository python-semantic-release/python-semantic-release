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

    [semantic_release.remote.token]
    env = "GH_TOKEN"

Given basic TOML syntax compatibility, this is equivalent to:

.. code-block:: toml

    [semantic_release.remote]
    token = { env = "GH_TOKEN" }

The general format for specifying that some configuration should be sourced from an
environment variable is:

.. code-block:: toml

    [semantic_release.variable]
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

.. _config-root:

``semantic_release`` settings
-----------------------------

The following sections outline all the definitions and descriptions of each supported
configuration setting. If there are type mis-matches, PSR will throw validation errors upon load.
If a setting is not provided, than PSR will fill in the value with the default value.

Python Semantic Release expects a root level key to start the configuration definition. Make
sure to use the correct root key dependending on the configuration format you are using.

.. note:: If you are using ``pyproject.toml``, this heading should include the `tool`` prefix
          as specified within PEP 517, resulting in ``[tool.semantic_release]``.

.. note:: If you are using a ``releaserc.toml``, use ``[semantic_release]`` as the root key

.. note:: If you are using a ``releaserc.json``, ``semantic_release`` must be the root key in the
          top level dictionary.

----

.. _config-allow_zero_version:

``allow_zero_version``
""""""""""""""""""""""

**Type:** ``bool``

This flag controls whether or not Python Semantic Release will use version
numbers aligning with the ``0.x.x`` pattern.

If set to ``true`` and starting at ``0.0.0``, a minor bump would set the
next version as ``0.1.0`` whereas a patch bump would set the next version as
``0.0.1``. A breaking change (ie. major bump) would set the next version as
``1.0.0`` unless the :ref:`config-major_on_zero` is set to ``false``.

If set to ``false``, Python Semantic Release will consider the first possible
version to be ``1.0.0``, regardless of patch, minor, or major change level.
Additionally, when ``allow_zero_version`` is set to ``false``,
the :ref:`config-major_on_zero` setting is ignored.

**Default:** ``true``

----

.. _config-assets:

``assets``
""""""""""

**Type:** ``list[str]``

One or more paths to additional assets that should committed to the remote repository
in addition to any files modified by writing the new version.

**Default:** ``[]``

----

.. _config-branches:

``branches``
""""""""""""

This setting is discussed in more detail at :ref:`multibranch-releases`

**Default:**

.. code-block:: toml

    [semantic_release.branches.main]
    match = "(main|master)"
    prerelease_token = "rc"
    prerelease = false

----

.. _config-build_command:

``build_command``
"""""""""""""""""

**Type:** ``Optional[str]``

Command to use to build the current project during :ref:`cmd-version`.

Python Semantic Release will execute the build command in the OS default
shell with a subset of environment variables. PSR provides the variable
``NEW_VERSION`` in the environment with the value of the next determined
version. The following table summarizes all the environment variables that
are passed on to the ``build_command`` runtime if they exist in the parent
process.

If you would like to pass additional environment variables to your build
command, see :ref:`config-build_command_env`.

========================  ======================================================================
Variable Name             Description
========================  ======================================================================
CI                        Pass-through ``true`` if exists in process env, unset otherwise
BITBUCKET_CI              ``true`` if Bitbucket CI variables exist in env, unset otherwise
GITHUB_ACTIONS            Pass-through ``true`` if exists in process env, unset otherwise
GITEA_ACTIONS             Pass-through ``true`` if exists in process env, unset otherwise
GITLAB_CI                 Pass-through ``true`` if exists in process env, unset otherwise
HOME                      Pass-through ``HOME`` of parent process
NEW_VERSION               Semantically determined next version (ex. ``1.2.3``)
PATH                      Pass-through ``PATH`` of parent process
PSR_DOCKER_GITHUB_ACTION  Pass-through ``true`` if exists in process env, unset otherwise
VIRTUAL_ENV               Pass-through ``VIRTUAL_ENV`` if exists in process env, unset otherwise
========================  ======================================================================

**Default:** ``None`` (not specified)

----

.. _config-build_command_env:

``build_command_env``
"""""""""""""""""""""

**Type:** ``Optional[list[str]]``

List of environment variables to include or pass-through on to the build command that executes
during :ref:`cmd-version`.

This configuration option allows the user to extend the list of environment variables
from the table above in :ref:`config-build_command`. The input is a list of strings
where each individual string handles a single variable definition. There are two formats
accepted and are detailed in the following table:

==================  ===================================================================
FORMAT              Description
==================  ===================================================================
``VAR_NAME``        Detects value from the PSR process environment, and passes value to
                    ``build_command`` process

``VAR_NAME=value``  Sets variable name to value inside of ``build_command`` process
==================  ===================================================================

.. note:: Although variable name capitalization is not required, it is recommended as
          to be in-line with the POSIX-compliant recommendation for shell variable names.

**Default:** ``None`` (not specified)

----

.. _config-changelog:

``changelog``
"""""""""""""

This section outlines the configuration options available that modify changelog generation.

.. note::
    **pyproject.toml:** ``[tool.semantic_release.changelog]``

    **releaserc.toml:** ``[semantic_release.changelog]``

    **releaserc.json:** ``{ "semantic_release": { "changelog": {} } }``

----

.. _config-changelog-changelog_file:

``changelog_file``
******************

**Type:** ``str``

Specify the name of the changelog file (after template rendering has taken place).

**Default:** ``"CHANGELOG.md"``

----

.. _config-changelog-environment:

``environment``
***************

.. note::
   This section of the configuration contains options which customize the template
   environment used to render templates such as the changelog. Most options are
   passed directly to the `jinja2.Environment`_ constructor, and further
   documentation one these parameters can be found there.

.. _`jinja2.Environment`: https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment

.. note::
    **pyproject.toml:** ``[tool.semantic_release.changelog.environment]``

    **releaserc.toml:** ``[semantic_release.changelog.environment]``

    **releaserc.json:** ``{ "semantic_release": { "changelog": { "environment": {} } } }``

----

.. _config-changelog-environment-autoescape:

``autoescape``
''''''''''''''

**Type:** ``Union[str, bool]``

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

----

.. _config-changelog-environment-block_start_string:

``block_start_string``
''''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"{%"``

----

.. _config-changelog-environment-block_end_string:

``block_end_string``
''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"%}"``

----

.. _config-changelog-environment-comment_start_string:

``comment_start_string``
''''''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``{#``

----

.. _config-changelog-environment-comment_end_string:

``comment_end_string``
''''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"#}"``

----

.. _config-changelog-environment-extensions:

``extensions``
''''''''''''''

**Type:** ``list[str]``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``[]``

----

.. _config-changelog-environment-keep_trailing_newline:

``keep_trailing_newline``
'''''''''''''''''''''''''

**Type:** ``bool``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

----

.. _config-changelog-environment-line_comment_prefix:

``line_comment_prefix``
'''''''''''''''''''''''

**Type:** ``Optional[str]``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``None`` (not specified)

----

.. _config-changelog-environment-line_statement_prefix:

``line_statement_prefix``
'''''''''''''''''''''''''

**Type:** ``Optional[str]``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``None`` (not specified)

----

.. _config-changelog-environment-lstrip_blocks:

``lstrip_blocks``
'''''''''''''''''

**Type:** ``bool``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

----

.. _config-changelog-environment-newline_sequence:

``newline_sequence``
''''''''''''''''''''

**Type:** ``Literal["\n", "\r", "\r\n"]``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"\n"``

----

.. _config-changelog-environment-trim_blocks:

``trim_blocks``
'''''''''''''''

**Type:** ``bool``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``false``

----

.. _config-changelog-environment-variable_start_string:

``variable_start_string``
'''''''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"{{"``

----

.. _config-changelog-environment-variable_end_string:

``variable_end_string``
'''''''''''''''''''''''

**Type:** ``str``

This setting is passed directly to the `jinja2.Environment`_ constructor.

**Default:** ``"}}"``

----

.. _config-changelog-exclude_commit_patterns:

``exclude_commit_patterns``
***************************

**Type:** ``list[str]``

Any patterns specified here will be excluded from the commits which are available
to your changelog. This allows, for example, automated commits to be removed if desired.
Python Semantic Release also removes its own commits from the Changelog via this mechanism;
therefore if you change the automated commit message that Python Semantic Release uses when
making commits, you may wish to add the *old* commit message pattern here.

The patterns in this list are treated as regular expressions.

**Default:** ``[]``

----

.. _config-changelog-template_dir:

``template_dir``
****************

**Type:** ``str``

If given, specifies a directory of templates that will be rendered during creation
of the changelog. If not given, the default changelog template will be used.

This option is discussed in more detail at :ref:`changelog-templates`

**Default:** ``"templates"``

----

.. _config-commit_author:

``commit_author``
"""""""""""""""""

**Type:** ``str``

Author used in commits in the format ``name <email>``.

.. note::
  If you are using the built-in GitHub Action, the default value is set to
  ``github-actions <actions@github.com>``. You can modify this with the
  ``git_committer_name`` and ``git_committer_name`` inputs.

.. seealso::
   - :ref:`github-actions`

**Default:** ``semantic-release <semantic-release>``

----

.. _config-commit_message:

``commit_message``
""""""""""""""""""

**Type:** ``str``

Commit message to use when making release commits. The message can use ``{version}``
as a format key, in which case the version being released will be formatted into
the message.

If at some point in your project's lifetime you change this, you may wish to consider,
adding the old message pattern(s) to :ref:`exclude_commit_patterns <config-changelog-exclude_commit_patterns>`.

**Default:** ``"{version}\n\nAutomatically generated by python-semantic-release"``

----

.. _config-commit_parser:

``commit_parser``
"""""""""""""""""

**Type:** ``str``

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

----

.. _config-commit_parser_options:

``commit_parser_options``
"""""""""""""""""""""""""

**Type:** ``dict[str, Any]``

These options are passed directly to the ``parser_options`` method of
:ref:`the commit parser <config-commit_parser>`, without validation
or transformation.

For more information, see :ref:`commit-parsing-parser-options`.

The default value for this setting depends on what you specify as
:ref:`commit_parser <config-commit_parser>`. The table below outlines
the expections from ``commit_parser`` value to default options value.

==================  ==   =================================
``commit_parser``        Default ``commit_parser_options``
==================  ==   =================================
``"angular"``       ->   .. code-block:: toml

                             [semantic_release.commit_parser_options]
                             allowed_types = [
                                 "build", "chore", "ci", "docs", "feat", "fix",
                                 "perf", "style", "refactor", "test"
                             ]
                             minor_types = ["feat"]
                             patch_types = ["fix", "perf"]

``"emoji"``         ->   .. code-block:: toml

                             [semantic_release.commit_parser_options]
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

                             [semantic_release.commit_parser_options]
                             allowed_tags = [
                                "API", "DEP", "ENH", "REV", "BUG", "MAINT", "BENCH",
                                "BLD", "DEV", "DOC", "STY", "TST", "REL", "FEAT", "TEST",
                             ]
                             major_tags = ["API",]
                             minor_tags = ["DEP", "DEV", "ENH", "REV", "FEAT"]
                             patch_tags = ["BLD", "BUG", "MAINT"]

``"tag"``           ->   .. code-block:: toml

                             [semantic_release.commit_parser_options]
                             minor_tag = ":sparkles:"
                             patch_tag = ":nut_and_bolt:"

``"module:class"``  ->   ``**module:class.parser_options()``
==================  ==   =================================

**Default:** ``ParserOptions { ... }``, where ``...`` depends on
:ref:`config-commit_parser` as indicated above.

----

.. _config-logging_use_named_masks:

``logging_use_named_masks``
"""""""""""""""""""""""""""

**Type:** ``bool``

Whether or not to replace secrets identified in logging messages with named masks
identifying which secrets were replaced, or use a generic string to mask them.

**Default:** ``false``

----

.. _config-major_on_zero:

``major_on_zero``
"""""""""""""""""

**Type:** ``bool``

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

When :ref:`config-allow_zero_version` is set to ``false``, this setting is ignored.

**Default:** ``true``

----

.. _config-no_git_verify:

``no_git_verify``
"""""""""""""""""

**Type:** ``bool``

This flag is passed along to ``git`` upon performing a ``git commit`` during :ref:`cmd-version`.

When true, it will bypass any git hooks that are set for the repository when Python Semantic
Release makes a version commit.  When false, the commit is performed as normal. This option
has no effect when there are not any git hooks configured nor when the ``--no-commit`` option
is passed.

**Default:** ``false``

----

.. _config-publish:

``publish``
"""""""""""

This section defines configuration options that modify :ref:`cmd-publish`.

.. note::
    **pyproject.toml:** ``[tool.semantic_release.publish]``

    **releaserc.toml:** ``[semantic_release.publish]``

    **releaserc.json:** ``{ "semantic_release": { "publish": {} } }``

----

.. _config-publish-dist_glob_patterns:

``dist_glob_patterns``
**********************

**Type:** ``list[str]``

Upload any files matching any of these globs to your VCS release. Each item in this
list should be a string containing a Unix-style glob pattern.

**Default:** ``["dist/*"]``

----

.. _config-publish-upload_to_vcs_release:

``upload_to_vcs_release``
*************************

**Type:** ``bool``

If set to ``true``, upload any artifacts matched by the
:ref:`dist_glob_patterns <config-publish-dist_glob_patterns>` to the release created
in the remote VCS corresponding to the latest tag. Artifacts are only uploaded if
release artifact uploads are supported by the :ref:`VCS type <config-remote-type>`.

**Default:** ``true``

----

.. _config-remote:

``remote``
""""""""""

The remote configuration is a group of settings that configure PSR's integration
with remote version control systems.

.. note::
    **pyproject.toml:** ``[tool.semantic_release.remote]``

    **releaserc.toml:** ``[semantic_release.remote]``

    **releaserc.json:** ``{ "semantic_release": { "remote": {} } }``

----

.. _config-remote-api_domain:

``api_domain``
**************

**Type:** ``Optional[str | Dict['env', str]]``

The hosting domain for the API of your remote HVCS if different than the ``domain``.
Generally, this will be used to specify a separate subdomain that is used for API
calls rather than the primary domain (ex. ``api.github.com``).

**Most on-premise HVCS installations will NOT use this setting!** Whether or not
this value is used depends on the HVCS configured (and your server administration)
in the :ref:`remote.type <config-remote-type>` setting and used in tadem with the
:ref:`remote.domain <config-remote-domain>` setting.

When using a custom :ref:`remote.domain <config-remote-domain>` and a HVCS
:ref:`remote.type <config-remote-type>` that is configured with a separate domain
or sub-domain for API requests, this value is used to configure the location of API
requests that are sent from PSR.

Most on-premise or self-hosted HVCS environments will use a path prefix to handle inbound
API requests, which means this value will ignored.

PSR knows the expected api domains for known cloud services and their associated
api domains which means this value is not necessary to explicitly define for services
as ``bitbucket.org``, and ``github.com``.

Including the protocol schemes, such as ``https://``, for the API domain is optional.
Secure ``HTTPS`` connections are assumed unless the setting of
:ref:`remote.insecure <config-remote-insecure>` is ``True``.

**Default:** ``None``

----

.. _config-remote-domain:

``domain``
**********

**Type:** ``Optional[str | Dict['env', str]]``

The host domain for your HVCS server. This setting is used to support on-premise
installations of HVCS providers with custom domain hosts.

If you are using the official domain of the associated
:ref:`remote.type <config-remote-type>`, this value is not required. PSR will use the
default domain value for the :ref:`remote.type <config-remote-type>` when not specified.
For example, when ``remote.type="github"`` is specified the default domain of
``github.com`` is used.

Including the protocol schemes, such as ``https://``, for the domain value is optional.
Secure ``HTTPS`` connections are assumed unless the setting of
:ref:`remote.insecure <config-remote-insecure>` is ``True``.

This setting also supports reading from an environment variable for ease-of-use
in CI pipelines. See :ref:`Environment Variable <config-environment-variables>` for
more information. Depending on the :ref:`remote.type <config-remote-type>`, the default
environment variable for the default domain's CI pipeline environment will automatically
be checked so this value is not required in default environments.  For example, when
``remote.type="gitlab"`` is specified, PSR will look to the ``CI_SERVER_URL`` environment
variable when ``remote.domain`` is not specified.

**Default:** ``None``

.. seealso::
   - :ref:`remote.api_domain <config-remote-api_domain>`

----

.. _config-remote-ignore_token_for_push:

``ignore_token_for_push``
*************************

**Type:** ``bool``

If set to ``True``, ignore the authentication token when pushing changes to the remote.
This is ideal, for example, if you already have SSH keys set up which can be used for
pushing.

**Default:** ``False``

----

.. _config-remote-insecure:

``insecure``
************

**Type:** ``bool``

Insecure is used to allow non-secure ``HTTP`` connections to your HVCS server. If set to
``True``, any domain value passed will assume ``http://`` if it is not specified and allow
it. When set to ``False`` (implicitly or explicitly), it will force ``https://`` communications.

When a custom ``domain`` or ``api_domain`` is provided as a configuration, this flag governs
the protocol scheme used for those connections. If the protocol scheme is not provided in
the field value, then this ``insecure`` option defines whether ``HTTP`` or ``HTTPS`` is
used for the connection. If the protocol scheme is provided in the field value, it must
match this setting or it will throw an error.

The purpose of this flag is to prevent any typos in provided ``domain`` and ``api_domain``
values that accidently specify an insecure connection but allow users to toggle the protection
scheme off when desired.

**Default:** ``False``

----

.. _config-remote-name:

``name``
********

**Type:** ``str``

Name of the remote to push to using ``git push -u $name <branch_name>``

**Default:** ``"origin"``

----

.. _config-remote-token:

``token``
*********

**Type:** ``Optional[str | Dict['env', str]]``

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

----

.. _config-remote-type:

``type``
********

**Type:** ``Literal["bitbucket", "gitea", "github", "gitlab"]``

The type of the remote VCS. Currently, Python Semantic Release supports ``"github"``,
``"gitlab"``, ``"gitea"`` and ``"bitbucket"``. Not all functionality is available with all
remote types, but we welcome pull requests to help improve this!

**Default:** ``"github"``

----

.. _config-remote-url:

``url``
*******

**Type:** ``Optional[str | Dict['env', str]]``

An override setting used to specify the remote upstream location of ``git push``.

**Not commonly used!** This is used to override the derived upstream location when
the desired push location is different than the location the repository was cloned
from.

This setting will override the upstream location url that would normally be derived
from the :ref:`remote.name <config-remote-name>` location of your git repository.

**Default:** ``None``

----

.. _config-tag_format:

``tag_format``
""""""""""""""

**Type:** ``str``

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

================ =========  ==========================================================
Format Key       Mandatory  Contents
================ =========  ==========================================================
``{version}``    Yes        The new semantic version number, for example ``1.2.3``, or
                            ``2.1.0-alpha.1+build.1234``
================ =========  ==========================================================

Tags which do not match this format will not be considered as versions of your project.

**Default:** ``"v{version}"``

----

.. _config-version_toml:

``version_toml``
""""""""""""""""

**Type:** ``list[str]``

Similar to :ref:`config-version_variables`, but allows the version number to be
identified safely in a toml file like ``pyproject.toml``, with each entry using
dotted notation to indicate the key for which the value represents the version:

.. code-block:: toml

    [semantic_release]
    version_toml = [
        "pyproject.toml:tool.poetry.version",
    ]

**Default:** ``[]``

----

.. _config-version_variables:

``version_variables``
"""""""""""""""""""""

**Type:** ``list[str]``

Each entry represents a location where the version is stored in the source code,
specified in ``file:variable`` format. For example:

.. code-block:: toml

    [semantic_release]
    version_variables = [
        "semantic_release/__init__.py:__version__",
        "docs/conf.py:version",
    ]

**Default:** ``[]``
