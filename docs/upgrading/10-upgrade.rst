.. _upgrade_v10:

Upgrading to v10
================

The upgrade to v10 is primarily motivated by a command injection security vulnerability
found in the GitHub Actions configuration interpreter (see details
:ref:`below <upgrade_v10-root_options>`). We also bundled a number of other changes,
including new default configuration values and most importantly, a return to 1-line
commit subjects in the default changelog format.

For more specific change details for v10, please refer to the :ref:`changelog-v10.0.0`
section of the :ref:`changelog`.


.. _upgrade_v10-root_options:

Security Fix: Command Injection Vulnerability (GitHub Actions)
--------------------------------------------------------------

In the previous versions of the GitHub Actions configuration, we used a single
``root_options`` parameter to pass any options you wanted to pass to the
``semantic-release`` main command. This parameter was interpreted as a string and
passed directly to the command line, which made it vulnerable to command injection
attacks. An attacker could exploit this by crafting a malicious string as the
:ref:`gh_actions-psr-inputs-root_options` input, and then it would be executed
as part of the command line, potentially allowing them to run arbitrary commands within
the GitHub Actions Docker container. The ability to exploit this vulnerability is limited
to people whom can modify the GitHub Actions workflow file, which is typically only the
repository maintainers unless you are pointing at an organizational workflow file or
another third-party workflow file.

To mitigate this vulnerability, we have removed the ``root_options`` parameter completely
and replaced it with individual boolean flag inputs which are then used to select the proper
cli parameters for the ``semantic-release`` command. Additionally, users can protect themselves
by limiting the access to secrets in their GitHub Actions workflows and the permissions of
the GitHub Actions CI TOKEN.

This vulnerability existed in both the
:ref:`python-semantic-release/python-semantic-release <gh_actions-psr>` and
:ref:`python-semantic-release/publish-action <gh_actions-publish>` actions.

For the main :ref:`python-semantic-release/python-semantic-release <gh_actions-psr>` action,
the following inputs are now available (in place of the old ``root_options`` parameter):
:ref:`gh_actions-psr-inputs-config_file`, :ref:`gh_actions-psr-inputs-noop`,
:ref:`gh_actions-psr-inputs-strict`, and :ref:`gh_actions-psr-inputs-verbosity`.

  **Example migration**

  If you previously had the following in your GitHub Actions workflow file:

  .. code:: yaml

    - uses: python-semantic-release/python-semantic-release@v9
      with:
        root_options: "-vv --strict"

  It would be updated to:

  .. code:: yaml

    - uses: python-semantic-release/python-semantic-release@v10
      with:
        strict: true
        verbosity: 2

For the :ref:`python-semantic-release/publish-action <gh_actions-publish>` action,
the following inputs are now available (in place of the old ``root_options`` parameter):
:ref:`gh_actions-publish-inputs-config_file`, :ref:`gh_actions-publish-inputs-noop`,
and :ref:`gh_actions-publish-inputs-verbosity`.

  **Example migration**

  If you previously had the following in your GitHub Actions workflow file:

  .. code:: yaml

    - uses: python-semantic-release/publish-action@v9
      with:
        root_options: "-v -c /path/to/releaserc.yaml"

  It would be updated to:

  .. code:: yaml

    - uses: python-semantic-release/publish-action@v10
      with:
        config_file: /path/to/releaserc.yaml
        verbosity: 1


.. _upgrade_v10-changelog_format-1_line_commit_subjects:

Changelog Format: 1-Line Commit Subjects
----------------------------------------

In v10, the default changelog format has been changed to use 1-line commit subjects instead of
including the full commit message. This change was made to improve the readability of the changelog
as many commit messages are long and contain unnecessary details for the changelog.

.. important::
    If you use a squash commit merge strategy, it is recommended that you use the default
    ``parse_squash_commits`` commit parser option to ensure that all the squashed commits are
    parsed for version bumping and changelog generation. This is the default behavior in v10 across
    all supported commit parsers. If you are upgrading, you likely will need to manually set this
    option in your configuration file to ensure that the changelog is generated correctly.

    If you do not enable ``parse_squash_commits``, then version will only be determined by the
    commit subject line and the changelog will only include the commit subject line as well.


.. _upgrade_v10-changelog_format-mask_initial_release:

Changelog Format: Mask Initial Release
--------------------------------------

In v10, the default behavior for the changelog generation has been changed to mask the initial
release in the changelog. This means that the first release will not contain a break down of the
different types of changes (e.g., features, fixes, etc.), but instead it will just simply state
that this is the initial release.


.. _upgrade_v10-changelog_format-commit_parsing:

Changelog Format: Commit Parsing
--------------------------------

We have made some minor changes to the commit parsing logic in *v10* to
separate out components of the commit message more clearly. You will find that the
:py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>` object's
descriptions list will no longer contain any Breaking Change footers, Release Notice footers,
PR/MR references, or Issue Closure footers. These were all previously extracted and placed
into their own attributes but were still included in the descriptions list. In *v10*,
the descriptions list will only contain the actual commit subject line and any additional
commit body text that is not part of the pre-defined footers.

If you were relying on the descriptions list to contain these footers, you will need to
update your code and changelog templates to reference the specific attributes you want to use.


.. _upgrade_v10-default_config:

Default Configuration Changes
-----------------------------

The following table summarizes the changes to the default configuration values in v10:

.. list-table::
    :widths: 5 55 20 20
    :header-rows: 1

    * - #
      - Configuration Option
      - Previous Default Value
      - New Default Value

    * - 1
      - :ref:`config-allow_zero_version`
      - ``true``
      - ``false``

    * - 2
      - :ref:`changelog.mode <config-changelog-mode>`
      - ``init``
      - ``update``

    * - 3
      - :ref:`changelog.default_templates.mask_initial_release <config-changelog-default_templates-mask_initial_release>`
      - ``false``
      - ``true``

    * - 4
      - :ref:`commit_parser_options.parse_squash_commits <config-commit_parser_options>`
      - ``false``
      - ``true``

    * - 5
      - :ref:`commit_parser_options.ignore_merge_commits <config-commit_parser_options>`
      - ``false``
      - ``true``


.. _upgrade_v10-deprecations:

Deprecations & Removals
-----------------------

No additional deprecations were made in *v10*, but the following are staged
for removal in v11:

.. list-table:: Deprecated Features & Functions
    :widths: 5 30 10 10 45
    :header-rows: 1

    * - #
      - Component
      - Deprecated
      - Planned Removal
      - Notes

    * - 1
      - :ref:`GitHub Actions root_options <gh_actions-psr-inputs-root_options>`
      - v10.0.0
      - v10.0.0
      - Replaced with individual boolean flag inputs. See :ref:`above <upgrade_v10-root_options>` for details.

    * - 2
      - :ref:`Angular Commit Parser <commit_parser-builtin-angular>`
      - v9.19.0
      - v11.0.0
      - Replaced by the :ref:`Conventional Commit Parser <commit_parser-builtin-conventional>`.

    * - 3
      - :ref:`Tag Commit Parser <commit_parser-builtin-tag>`
      - v9.12.0
      - v11.0.0
      - Replaced by the :ref:`Emoji Commit Parser <commit_parser-builtin-emoji>`.

.. note::
    For the most up-to-date information on the next version deprecations and removals, please
    refer to the issue
    `#1066 <https://github.com/python-semantic-release/python-semantic-release/issues/1066>`_.
