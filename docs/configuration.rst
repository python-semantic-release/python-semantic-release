.. _configuration:

Configuration
=============

Configuration is read from a file which can be specified using the
:ref:`--config <cmd-main-option-config>` option to :ref:`cmd-main`. Python Semantic
Release currently supports either TOML- or JSON-formatted configuration, and will
attempt to detect and parse the configuration based on the file extension.

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

Some settings can be configured via environment variables. In order to do this,
you must indicate that Python Semantic Release should use a particular environment
variable as follows.

Suppose for example that you would like to set :ref:`upload.password <config-upload-password>`.
It is possible to do so by pasting your repository password in plaintext into your
configuration file (**Note: this is not advisable**):

.. code-block:: toml

    [tool.semantic_release.upload]
    password = "very secret 123"

Unfortunately, this configuration lives in your Git repository along with your source
code, and this would represent insecure management of your password. It is recommended
to use an environment variable to provide the required password. Suppose you would
like to specify that should be read from the environment variable ``TWINE_PASSWORD``. 
In this case, you should modify your configuration to the following:

.. code-block:: toml

    [tool.semantic_release.upload]
    password = { env = "TWINE_PASSWORD" }

This is equivalent to the default:

.. code-block:: toml

    [tool.semantic_release.upload.password]
    env = "TWINE_PASSWORD"

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

.. note::
  If you are using the built-in GitHub Action, the default value is set to
  ``github-actions <actions@github.com>``. You can modify this with the
  ``git_committer_name`` and ``git_committer_email`` inputs.

.. _config-root:

``[tool.semantic_release]``
***************************

.. _config-assets:

``assets (List[str])``
""""""""""""""""""""""

One or more paths to additional assets that should be attached to VCS releases.

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

``build_command (str)``
"""""""""""""""""""""""

Command to use when building the source code during :ref:`cmd-publish`

**Default:** ``"py setup.py sdist bdist_wheel"`` on Windows,
``"python setup.py sdist bdist_wheel"`` on other operating systems

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

You can choose one of the inbuilt commit parsers - ``"angular"`` for
:ref:`AngularCommitParser <commit-parser-angular>`, ``"emoji"`` for
:ref:`EmojiCommitParser <commit-parser-emoji>`, ``"scipy"`` for
:ref:`<ScipyCommitParser <commit-parser-scipy>` or ``"tag"`` for
:ref:`TagCommitParser <commit-parser-tag>`. However you can also specify your own
commit parser in ``module:attr`` form, in which case this will be imported and used
instead.

For more information see :ref:`commit-parsing`.

**Default:** ``"angular"``

.. _config-commit-parser-options:

``commit_parser_options (Dict[str, Any])``
""""""""""""""""""""""""""""""""""""""""""

These options are passed directly to the ``parser_options`` method of
:ref:`the commit parser <config-commit-parser>`, without validation
or transformation.

For more information, see :ref:`commit-parsing-parser-options`.

The default values are the defaults for :ref:`commit-parser-angular`

**Default:**

.. code-block:: toml

    [tool.semantic_release.commit_parser_options]
    allowed_tags = [
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "style",
        "refactor",
        "test",
    ]
    minor_tags = ["feat"]
    patch_tags = ["fix", "perf"]

.. _config-logging-use-named-masks:

``logging_use_named_masks (bool)``
""""""""""""""""""""""""""""""""""

Whether or not to replace secrets identified in logging messages with named masks
identifying which secrets were replaced, or use a generic string to mask them.

**Default:** ``false``

.. _config-major-on-zero:

``major_on_zero (bool)``
""""""""""""""""""""""""

If set to ``false``, major (breaking) releases will increment the minor digit of the
version while the major version is ``0``, instead of the major digit.

From the `Semantic Versioning Specification`_:

   Major version zero (0.y.z) is for initial development. Anything MAY change at
   any time. The public API SHOULD NOT be considered stable.

.. _Semantic Versioning Specification: https://semver.org/spec/v2.0.0.html#spec-item-4

**Default:** ``true``

.. _config-tag-format:

``tag_format (str)``
""""""""""""""""""""

Specify the format to be used for the Git tag that will be added to the repo during
a release invoked via :ref:`cmd-version`. The format string must include the mandatory
format keys below, otherwise an exception will be thrown. It *may* include any of the
optional format keys, in which case the contents described will be formatted into the
specified location in the Git tag that is created.

This format will also be used for parsing tags already present in the repository into
semantic versions, so unexpected behaviour can occur if the tag format changes at some
point in the repository's history.

================ =========  ========
Format Key       Mandatory  Contents
================ =========  ========
``{version}``    Yes        The new semantic version number, for example ``1.2.3``, or
                            ``2.1.0-alpha.1+build.1234``
================ =========  ========

**Default:** ``"v{version}"``

.. _config-version-variables:

``version_variables (List[str])``
"""""""""""""""""""""""""""""""""

Each entry represents a location where the version is stored in the source code,
specifed in ``file:variable`` format. For example:

.. code-block:: toml

    [tool.semantic_release]
    version_variable = [
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
   This section of the configuration contains options which customise the template
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
``"gitlab"`` and ``"gitea"``. Not all functionality is available with all remote types,
but we welcome pull requests to help improve this!

**Default:** ``"github"``

.. _config-remote-ignore-token-for-push:

``ignore_token_for_push (bool)``
""""""""""""""""""""""""""""""""

If set to ``True``, ignore the authentication token when pushing changes to the remote.
This is ideal, for example, if you already have SSH keys set up which can be used for
pushing.

**Default:** ``False``

.. _config-remote-token:

``token`` (:ref:`Environment Variable <config-environment-variables>`)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Environment variable from which to source the authentication token for the remote VCS.
Common examples include ``"GH_TOKEN"``, ``"GITLAB_TOKEN"`` or ``"GITEA_TOKEN"``, however
you can choose to use a custom environment variable if you wish.

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


**Default:** ``{ env = "GH_TOKEN" }``


.. _config-upload:

``[tool.semantic_release.upload]``
**********************************

.. warning::
   This section of the configuration contains options which customise the behaviour 
   of the upload of artefacts to a repository. This is performed using `Twine`_, and
   more information can be found by consulting the documentation for the
   `twine upload`_ command.

   Many settings can be resolved from :ref:`config-environment-variables`. It is
   possible to specify any settings directly in your configuration file as strings,
   but be aware that those which are marked as environment variables by default are
   also **mandatory** by default. If you wish to use the :ref:`publish command
   <cmd-publish>` without specifying these environment variables, you should adjust
   the configuration accordingly, using appropriate defaults or by setting the string
   values directly in the configuration.

   Please remember that your configuration file should be committed to your source
   control repository and as such that you should avoid placing any sensitive
   information into the configuration file!

.. _`Twine`: https://twine.readthedocs.io/en/stable
.. _`twine upload`: https://twine.readthedocs.io/en/stable/#twine-upload

.. _config-upload-dist-glob-patterns:

``dist_glob_patterns (List[str])``
""""""""""""""""""""""""""""""""""

Once :ref:`config-build-command` has been run, any files matching any of these globs
will be uploaded to your repository. Each item in this list should be a string
containing a Unix-style glob pattern.

**Default:** ``["dist/*"]``

.. _config-upload-upload-to-repository:

``upload_to_repository (bool)``
"""""""""""""""""""""""""""""""

If set to ``true``, upload artefacts matching
:ref:`dist_glob_patterns <config-upload-dist-glob-patterns>` to the configured artefact
repository using `twine upload`_. Set to ``false`` to disable uploading.

**Default:** ``true``

.. _config-upload-upload-to-vcs-release:

``upload_to_vcs_release (bool)``
""""""""""""""""""""""""""""""""

If set to ``true``, upload artefacts matching
:ref:`dist_glob_patterns <config-upload-dist-glob-patterns>` to the release created
in the remote VCS corresponding to the latest tag, if that is supported by the
:ref:`VCS type <config-remote-type>`.

**Default:** ``true``

.. _config-upload-sign:

``sign (bool)``
"""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:** ``false``

.. _config-upload-sign-with:

``sign_with (str)``
"""""""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:** ``"gpg"``

.. _config-upload-config-file:

``config_file (str)``
"""""""""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:**: ``"~/.pypirc"``

.. _config-upload-skip-existing:

``skip_existing (bool)``
""""""""""""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:** ``false``

.. _config-upload-repository-name:

``repository_name (str)``
"""""""""""""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:** ``"pypi"``

.. _config-upload-disable-progress-bar:

``disable_progress_bar (bool)``
"""""""""""""""""""""""""""""""

This setting is passed directly to the `twine upload`_ command.

**Default:** ``false``

.. _config-upload-pypi-token:

``pypi_token`` (:ref:`Environment Variable <config-environment-variables>`)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

.. note::
   By default, this is a **mandatory** environment variable that must be set before
   using the :ref:`publish command <cmd-publish>`.

**Default:** ``{ env = "PYPI_TOKEN" }``

.. _config-upload-identity:

``identity`` (:ref:`Environment Variable <config-environment-variables>`)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

**Default:** ``{ env = "GPG_IDENTITY" }``

.. _config-upload-username:

``username`` (:ref:`Environment Variable <config-environment-variables>`)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

.. note::
   By default, this is a **mandatory** environment variable that must be set before
   using the :ref:`publish command <cmd-publish>`.

**Default:** ``{ env = "REPOSITORY_USERNAME", default_env = "TWINE_USERNAME" }``

.. _config-upload-password:

``password`` (:ref:`Environment Variable <config-environment-variables>`)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

.. note::
   By default, this is a **mandatory** environment variable that must be set before
   using the :ref:`publish command <cmd-publish>`.

**Default:** ``{ env = "REPOSITORY_PASSWORD", default_env = "TWINE_PASSWORD" }``

.. warning::
  You should use token authentication instead of username and password
  authentication for the following reasons:

  - It is `strongly recommended by PyPI <https://pypi.org/help/#apitoken>`_.
  - Tokens can be given access to only a single project, which reduces the
    possible damage if it is compromised.
  - You can change your password without having to update it in CI settings.
  - If your PyPI username is the same as your GitHub username and you have
    it set as a secret in a CI service, it can be scrubbed from the
    build output. This can break things, for example repository links.

  - Find more information on `how to obtain a token <https://pypi.org/help/#apitoken>`_.

.. _config-upload-repository-url:

``repository_url`` (:ref:`Environment Variable <config-environment-variables>`)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

.. note::
   By default, this is a **mandatory** environment variable that must be set before
   using the :ref:`publish command <cmd-publish>`.

**Default:** ``{ env = "REPOSITORY_URL", default_env = "TWINE_REPOSITORY_URL" }``

.. _config-upload-non-interactive:

``non_interactive`` (:ref:`Environment Variable <config-environment-variables>`)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

**Default:** ``{ env = "TWINE_NON_INTERACTIVE", default = "true" }``

.. _config-upload-cacert:

``non_interactive`` (:ref:`Environment Variable <config-environment-variables>`)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

**Default:** ``{ env = "TWINE_CERT" }``

.. _config-upload-client-cert:

``client_cert`` (:ref:`Environment Variable <config-environment-variables>`)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

After resolving the environment variable, this setting is passed directly to the
`twine upload`_ command.

**Default:** ``{ env = "TWINE_CLIENT_CERT" }``
