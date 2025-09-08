.. _commit_parsing:

Commit Parsing
==============

One of the core components of Python Semantic Release (PSR) is the commit parser. The
commit parser is responsible for parsing a Project's Git Repository commit history
to extract insights about project changes and make decisions based on this insight.

The primary decision that PSR makes based on the commit history is whether or not
to release a new version of the project, and if so, what version number to release.
This decision is made based on the commit message descriptions of the change impact
introduced by the commit. The change impact describes the impact to the end consumers
of the project. Depending on the type of change, the version number will be
incremented according to the `Semantic Versioning`_ specification (semver).
It is the commit parser's job to extract the change impact from the commit message to
determine the severity of the changes and then subsequently determine the semver level
that the version should be bumped to for the next release.

The commit parser is also responsible for interpreting other aspects of the commit
message which can be used to generate a helpful and detailed changelog. This includes
extracting the type of change, the scope of the change, any breaking change descriptions,
any linked pull/merge request numbers, and any linked issue numbers.

PSR provides several :ref:`built-in commit parsers <commit_parser-builtin>` to handle
a variety of different commit message styles. If the built-in parsers do not meet your
needs, you can write your own :ref:`custom parser <commit_parser-custom_parser>`
to handle your specific commit message style.

.. warning::
  PSR's built-in commit parsers are designed to be flexible enough to provide a
  convenient way to generate the most effective changelogs we can, which means some
  features are added beyond the scope of the original commit message style guidelines.

  Other tools may not follow the same conventions as PSR's guideline extensions, so
  if you plan to use any similar programs in tandem with PSR, you should be aware of the
  differences in feature support and fall back to the official format guidelines if
  necessary.

.. _Semantic Versioning: https://semver.org/

----

.. _commit_parser-builtin:

Built-in Commit Parsers
-----------------------

The following parsers are built in to Python Semantic Release:

- :ref:`ConventionalCommitParser <commit_parser-builtin-conventional>`
- :ref:`ConventionalCommitMonorepoParser <commit_parser-builtin-conventional-monorepo>` *(available in v10.4.0+)*
- :ref:`AngularCommitParser <commit_parser-builtin-angular>` *(deprecated in v9.19.0)*
- :ref:`EmojiCommitParser <commit_parser-builtin-emoji>`
- :ref:`ScipyCommitParser <commit_parser-builtin-scipy>`
- :ref:`TagCommitParser <commit_parser-builtin-tag>` *(deprecated in v9.12.0)*

----

.. _commit_parser-builtin-conventional:

Conventional Commits Parser
"""""""""""""""""""""""""""

*Introduced in v9.19.0*

A parser that is designed to parse commits formatted according to the
`Conventional Commits Specification`_.  The parser is implemented with the following
logic in relation to PSR's core features:

- **Version Bump Determination**: This parser extracts the commit type from the subject
  line of the commit (the first line of a commit message). This type is matched against
  the configuration mapping to determine the level bump for the specific commit. If the
  commit type is not found in the configuration mapping, the commit is considered a
  non-parsable commit and will return it as a ParseError object and ultimately a commit
  of type ``"unknown"``. The configuration mapping contains lists of commit types that
  correspond to the level bump for each commit type. Some commit types are still valid
  do not trigger a level bump, such as ``"chore"`` or ``"docs"``. You can also configure
  the default level bump
  :ref:`commit_parser_options.default_level_bump <config-commit_parser_options>` if desired.
  To trigger a major release, the commit message body must contain a paragraph that begins
  with ``BREAKING CHANGE:``. This will override the level bump determined by the commit type.

- **Changelog Generation**: PSR will group commits in the changelog by the commit type used
  in the commit message. The commit type shorthand is converted to a more human-friendly
  section heading and then used as the version section title of the changelog and release
  notes. Under the section title, the parsed commit descriptions are listed out in full. If
  the commit includes an optional scope, then the scope is prefixed on to the first line of
  the commit description. If a commit has any breaking change prefixed paragraphs in the
  commit message body, those paragraphs are separated out into a "Breaking Changes" section
  in the changelog (Breaking Changes section is available from the default changelog in
  v9.15.0). Each breaking change paragraph is listed in a bulleted list format across the
  entire version. A single commit is allowed to have more than one breaking change
  prefixed paragraph (as opposed to the `Conventional Commits Specification`_). Commits
  with an optional scope and a breaking change will have the scope prefixed on to the
  breaking change paragraph. Parsing errors will return a ParseError object and ultimately
  a commit of type ``"unknown"``. Unknown commits are consolidated into an "Unknown" section
  in the changelog by the default template. To remove unwanted commits from the changelog
  that normally are placed in the "unknown" section, consider the use of the configuration
  option :ref:`changelog.exclude_commit_patterns <config-changelog-exclude_commit_patterns>`
  to ignore those commit styles.

- **Pull/Merge Request Identifier Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-linked_merge_request_detection` to identify and extract
  pull/merge request numbers. The parser will return a string value if a pull/merge
  request number is found in the commit message. If no pull/merge request number is
  found, the parser will return an empty string.

- **Linked Issue Identifier Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-issue_number_detection` to identify and extract issue numbers.
  The parser will return a tuple of issue numbers as strings if any are found in the commit
  message. If no issue numbers are found, the parser will return an empty tuple.

- **Squash Commit Evaluation**: This parser implements PSR's
  :ref:`commit_parser-builtin-squash_commit_evaluation` to identify and extract each commit
  message as a separate commit message within a single squashed commit. You can toggle this
  feature on/off via the :ref:`config-commit_parser_options` setting.

- **Release Notice Footer Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-release_notice_footer_detection`, which is a custom extension
  to traditional `Conventional Commits Specification`_ to use the ``NOTICE`` keyword as a git
  footer to document additional release information that is not considered a breaking change.

**Limitations**:

- Commits with the ``revert`` type are not currently supported. Track the implementation
  of this feature in the issue `#402`_.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in
:py:class:`defaults <semantic_release.commit_parser.conventional.options.ConventionalCommitParserOptions>`.

.. _#402: https://github.com/python-semantic-release/python-semantic-release/issues/402
.. _Conventional Commits Specification: https://www.conventionalcommits.org/en/v1.0.0

----

.. _commit_parser-builtin-conventional-monorepo:

Conventional Commits Monorepo Parser
""""""""""""""""""""""""""""""""""""

*Introduced in v10.4.0*

.. important::
  In order for this parser to be effective, please review the section titled
  :ref:`monorepos` for details on file structure, configurations, and release actions.

This parser is an extension of the :ref:`commit_parser-builtin-conventional`, designed specifically
for monorepo environments. A monorepo environment is defined as a single source control repository
that contains multiple packages, each of which can be released independently and may have different
version numbers.

This parser introduces two new configuration options that determine which packages are affected
by a commit. These options control whether a commit is considered for version determination,
changelog generation, and other release actions for the relevant packages. The 2 new
configuration options are
:py:class:`path_filters <semantic_release.commit_parser.conventional.options_monorepo.ConventionalCommitMonorepoParserOptions.path_filters>`
and
:py:class:`scope_prefix <semantic_release.commit_parser.conventional.options_monorepo.ConventionalCommitMonorepoParserOptions.scope_prefix>`.

**Features**:

- **Package Specific Commit Filtering**: For monorepo support, this parser uses 2 filtering rules
  to determine if a commit should be considered for a specific package. The first rule is based on
  file paths that are changed in the commit and the second rule is based on the optional scope
  prefix defined in the commit message. If either rule matches, then the commit is considered
  relevant to that package and will be used in version determination, changelog generation, etc,
  for that package. If neither rule matches, then the commit is ignored for that package. File
  path filtering rules are applied first and are the primary way to determine package relevance. The
  :py:class:`path_filters <semantic_release.commit_parser.conventional.options_monorepo.ConventionalCommitMonorepoParserOptions.path_filters>`
  option allows for specifying a list of file path patterns and will also support negated patterns
  to ignore specific paths that otherwise would be selected from the file glob pattern.  Negated
  patterns are defined by prefixing the pattern with an exclamation point (``!``). File path
  filtering is quite effective by itself but to handle the edge cases, the parser has the
  :py:class:`scope_prefix <semantic_release.commit_parser.conventional.options_monorepo.ConventionalCommitMonorepoParserOptions.scope_prefix>`
  configuration option to allow the developer to specifically define when the commit is relevant
  to the package. In monorepo setups, there are often shared files between packages (generally at
  the root project level) that are modified occasionally but not always relevant to the package
  being released. Since you do not want to define this path in the package configuration as it may
  not be relevant to the release, then this parser will look for a match with the scope prefix.
  The scope prefix is a regular expression that is used to match the text inside the scope field
  of a Conventional Commit. The scope prefix is optional and is used only if file path filtering
  does not match. Commits that have matching files in the commit will be considered relevant to
  the package **regardless** if a scope prefix exists or if it matches.

- **Version Bump Determination**: Once package-specific commit filtering is applied, the relevant
  commits are passed to the Conventional Commits Parser for evaluation and then used for version
  bump determination. See :ref:`commit_parser-builtin-conventional` for details.

- **Changelog Generation**: Once package-specific commit filtering is applied, the relevant
  commits are passed to the Conventional Commits Parser for evaluation and then used for
  changelog generation. See :ref:`commit_parser-builtin-conventional` for details.

- **Pull/Merge Request Identifier Detection**: Once package-specific commit filtering is applied,
  the relevant commits are passed to the Conventional Commits Parser for pull/merge request
  identifier detection. See :ref:`commit_parser-builtin-linked_merge_request_detection` for details.

- **Linked Issue Identifier Detection**: Once package-specific commit filtering is applied, the
  relevant commits are passed to the Conventional Commits Parser for linked issue identifier
  detection. See :ref:`commit_parser-builtin-issue_number_detection` for details.

- **Squash Commit Evaluation**: Squashed commits are separated out into individual commits with
  the same set of changed files **BEFORE** the package-specific commit filtering is applied.
  Each pseudo-commit is then subjected to the same filtering rules as regular commits. See
  :ref:`commit_parser-builtin-squash_commit_evaluation` for details.

- **Release Notice Footer Detection**: Once package-specific commit filtering is applied, the
  relevant commits are passed to the Conventional Commits Parser for release notice footer
  detection. See :ref:`commit_parser-builtin-release_notice_footer_detection` for details.

**Limitations**:

- ``revert`` commit type is NOT supported, see :ref:`commit_parser-builtin-conventional`'s
  limitations for details.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in
:py:class:`defaults <semantic_release.commit_parser.conventional.options_monorepo.ConventionalCommitMonorepoParserOptions>`.

----

.. _commit_parser-builtin-angular:

Angular Commit Parser
"""""""""""""""""""""

.. warning::
  This parser was deprecated in ``v9.19.0``. It will be removed in a future release.
  This parser is being replaced by the :ref:`commit_parser-builtin-conventional`.

A parser that is designed to parse commits formatted according to the
`Angular Commit Style Guidelines`_.  The parser is implemented with the following
logic in relation to how PSR's core features:

- **Version Bump Determination**: This parser extracts the commit type from the subject
  line of the commit (the first line of a commit message). This type is matched against
  the configuration mapping to determine the level bump for the specific commit. If the
  commit type is not found in the configuration mapping, the commit is considered a
  non-parsable commit and will return it as a ParseError object and ultimately a commit
  of type ``"unknown"``. The configuration mapping contains lists of commit types that
  correspond to the level bump for each commit type. Some commit types are still valid
  do not trigger a level bump, such as ``"chore"`` or ``"docs"``. You can also configure
  the default level bump
  :ref:`commit_parser_options.default_level_bump <config-commit_parser_options>` if desired.
  To trigger a major release, the commit message body must contain a paragraph that begins
  with ``BREAKING CHANGE:``. This will override the level bump determined by the commit type.

- **Changelog Generation**: PSR will group commits in the changelog by the commit type used
  in the commit message. The commit type shorthand is converted to a more human-friendly
  section heading and then used as the version section title of the changelog and release
  notes. Under the section title, the parsed commit descriptions are listed out in full. If
  the commit includes an optional scope, then the scope is prefixed on to the first line of
  the commit description. If a commit has any breaking change prefixed paragraphs in the
  commit message body, those paragraphs are separated out into a "Breaking Changes" section
  in the changelog (Breaking Changes section is available from the default changelog in
  v9.15.0). Each breaking change paragraph is listed in a bulleted list format across the
  entire version. A single commit is allowed to have more than one breaking change
  prefixed paragraph (as opposed to the `Angular Commit Style Guidelines`_). Commits
  with an optional scope and a breaking change will have the scope prefixed on to the
  breaking change paragraph. Parsing errors will return a ParseError object and ultimately
  a commit of type ``"unknown"``. Unknown commits are consolidated into an "Unknown" section
  in the changelog by the default template. To remove unwanted commits from the changelog
  that normally are placed in the "unknown" section, consider the use of the configuration
  option :ref:`changelog.exclude_commit_patterns <config-changelog-exclude_commit_patterns>`
  to ignore those commit styles.

- **Pull/Merge Request Identifier Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-linked_merge_request_detection` to identify and extract
  pull/merge request numbers. The parser will return a string value if a pull/merge
  request number is found in the commit message. If no pull/merge request number is
  found, the parser will return an empty string. *Feature available in v9.13.0+.*

- **Linked Issue Identifier Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-issue_number_detection` to identify and extract issue numbers.
  The parser will return a tuple of issue numbers as strings if any are found in the commit
  message. If no issue numbers are found, the parser will return an empty tuple. *Feature
  available in v9.15.0+.*

- **Squash Commit Evaluation**: This parser implements PSR's
  :ref:`commit_parser-builtin-squash_commit_evaluation` to identify and extract each commit
  message as a separate commit message within a single squashed commit. You can toggle this
  feature on/off via the :ref:`config-commit_parser_options` setting. *Feature available in
  v9.17.0+.*

- **Release Notice Footer Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-release_notice_footer_detection`, which is a custom extension
  to traditional `Angular Commit Style Guidelines`_ to use the ``NOTICE`` keyword as a git
  footer to document additional release information that is not considered a breaking change.
  *Feature available in v9.18.0+.*

**Limitations**:

- Commits with the ``revert`` type are not currently supported. Track the implementation
  of this feature in the issue `#402`_.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.angular.AngularParserOptions>`.

.. _#402: https://github.com/python-semantic-release/python-semantic-release/issues/402
.. _Angular Commit Style Guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits

----

.. _commit_parser-builtin-emoji:

Emoji Commit Parser
"""""""""""""""""""

A parser that is designed to parse commits formatted to the `Gitmoji Specification`_
with a few additional features that the specification does not cover but provide similar
functionality expected from a Semantic Release tool.  As the `Gitmoji Specification`_
describes, the emojis can be specified in either the unicode format or the shortcode
text format. See the `Gitmoji Specification`_ for the pros and cons for which format
to use, but regardless, the configuration options must match the format used in the
commit messages. The parser is implemented with the following logic in relation to
how PSR's core features:

- **Version Bump Determination**: This parser only looks for emojis in the subject
  line of the commit (the first line of a commit message). If more than one emoji is
  found, the emoji configured with the highest priority is selected for the change impact
  for the specific commit. The emoji with the highest priority is the one configured in the
  ``major`` configuration option, followed by the ``minor``, and ``patch`` in descending
  priority order. If no emoji is found in the subject line, the commit is classified as
  other and will default to the level bump defined by the configuration option
  :ref:`commit_parser_options.default_level_bump <config-commit_parser_options>`.

- **Changelog Generation**: PSR will group commits in the changelog by the emoji type used
  in the commit message. The emoji is used as the version section title and the commit
  descriptions are listed under that section. No emojis are removed from the commit message
  so each will be listed in the changelog and release notes. When more than one emoji is
  found in the subject line of a commit, the emoji with the highest priority is the one
  that will influence the grouping of the commit in the changelog. Commits containing no
  emojis or non-configured emojis are consolidated into an "Other" section. To remove
  unwanted commits from the changelog that would normally be added into the "other"
  section, consider the use of the configuration option
  :ref:`changelog.exclude_commit_patterns <config-changelog-exclude_commit_patterns>`
  to ignore those commit styles.

- **Pull/Merge Request Identifier Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-linked_merge_request_detection` to identify and extract
  pull/merge request numbers. The parser will return a string value if a pull/merge
  request number is found in the commit message. If no pull/merge request number is
  found, the parser will return an empty string. *Feature available in v9.13.0+.*

- **Linked Issue Identifier Detection**: [Disabled by default] This parser implements PSR's
  :ref:`commit_parser-builtin-issue_number_detection` to identify and extract issue numbers.
  The parser will return a tuple of issue numbers as strings if any are found in the commit
  message. If no issue numbers are found, the parser will return an empty tuple. This feature
  is disabled by default since it is not a part of the `Gitmoji Specification`_ but can be
  enabled by setting the configuration option ``commit_parser_options.parse_linked_issues``
  to ``true``. *Feature available in v9.15.0+.*

- **Squash Commit Evaluation**: This parser implements PSR's
  :ref:`commit_parser-builtin-squash_commit_evaluation` to identify and extract each commit
  message as a separate commit message within a single squashed commit. You can toggle this
  feature on/off via the :ref:`config-commit_parser_options` setting. *Feature available in
  v9.17.0+.*

- **Release Notice Footer Detection**: This parser implements PSR's
  :ref:`commit_parser-builtin-release_notice_footer_detection`, which is a custom extension
  that uses the ``NOTICE`` keyword as a git footer to document additional release information
  that is not considered a breaking change. *Feature available in v9.18.0+.*

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.emoji.EmojiParserOptions>`.

.. _Gitmoji Specification: https://gitmoji.dev/specification

----

.. _commit_parser-builtin-scipy:

Scipy Commit Parser
"""""""""""""""""""

A parser that is designed to parse commits formatted according to the
`Scipy Commit Style Guidelines`_. This is essentially a variation of the `Angular Commit Style
Guidelines`_ with all different commit types. Because of this small variance, this parser
only extends our :ref:`commit_parser-builtin-angular` parser with pre-defined scipy commit types
in the default Scipy Parser Options and all other features are inherited.

**Limitations**:

- Commits with the ``REV`` type are not currently supported. Track the implementation
  of this feature in the issue `#402`_.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.scipy.ScipyParserOptions>`.

.. _Scipy Commit Style Guidelines: https://scipy.github.io/devdocs/dev/contributor/development_workflow.html#writing-the-commit-message

----

.. _commit_parser-builtin-tag:

Tag Commit Parser
"""""""""""""""""

.. warning::
  This parser was deprecated in ``v9.12.0``. It will be removed in a future release.

The original parser from v1.0.0 of Python Semantic Release. Similar to the
emoji parser above, but with less features.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.tag.TagParserOptions>`.

----

.. _commit_parser-builtin-linked_merge_request_detection:

Common Linked Merge Request Detection
"""""""""""""""""""""""""""""""""""""

*Introduced in v9.13.0*

All of the PSR built-in parsers implement common pull/merge request identifier detection
logic to extract pull/merge request numbers from the commit message regardless of the
VCS platform. The parsers evaluate the subject line for a parenthesis-enclosed number
at the end of the line. PSR's parsers will return a string value if a pull/merge request
number is found in the commit message. If no pull/merge request number is found, the
parsers will return an empty string.

**Examples**:

*All of the following will extract a MR number of "x123", where 'x' is the character prefix*

1. BitBucket: ``Merged in feat/my-awesome-feature  (pull request #123)``

2. GitHub: ``feat: add new feature  (#123)``

3. GitLab: ``fix: resolve an issue (!123)``

----

.. _commit_parser-builtin-issue_number_detection:

Common Issue Identifier Detection
"""""""""""""""""""""""""""""""""

*Introduced in v9.15.0*

All of the PSR built-in parsers implement common issue identifier detection logic,
which is similar to many VCS platforms such as GitHub, GitLab, and BitBucket. The
parsers will look for common issue closure text prefixes in the `Git Trailer format`_
in the commit message to identify and extract issue numbers. The detection logic is
not strict to any specific issue tracker as we try to provide a flexible approach
to identifying issue numbers but in order to be flexible, it is **required** to the
use the `Git Trailer format`_ with a colon (``:``) as the token separator.

PSR attempts to support all variants of issue closure text prefixes, but not all will work
for your VCS. PSR supports the following case-insensitive prefixes and their conjugations
(plural, present, & past tense):

- close (closes, closing, closed)

- fix (fixes, fixing, fixed)

- resolve (resolves, resolving, resolved)

- implement (implements, implementing, implemented)

PSR also allows for a more flexible approach to identifying more than one issue number without
the need of extra git trailers (although PSR does support multiple git trailers). PSR support
various list formats which can be used to identify more than one issue in a list. This format
will not necessarily work on your VCS. PSR currently support the following list formats:

- comma-separated (ex. ``Closes: #123, #456, #789``)
- space-separated (ex. ``resolve: #123 #456 #789``)
- semicolon-separated (ex. ``Fixes: #123; #456; #789``)
- slash-separated (ex. ``close: #123/#456/#789``)
- ampersand-separated (ex. ``Implement: #123 & #789``)
- and-separated (ex. ``Resolve: #123 and #456 and #789``)
- mixed (ex. ``Closed: #123, #456, and #789`` or ``Fixes: #123, #456 & #789``)

All the examples above use the most common issue number prefix (``#``) but PSR is flexible
to support other prefixes used by VCS platforms or issue trackers such as JIRA (ex. ``ABC-###``).

The parsers will return a tuple of issue numbers as strings if any are found in the commit
message. Strings are returned to ensure that the any issue number prefix characters are
preserved (ex. ``#123`` or ``ABC-123``). If no issue numbers are found, the parsers will
return an empty tuple.

**References**:

- `BitBucket: Resolving Issues Automatically <https://support.atlassian.com/bitbucket-cloud/docs/resolve-issues-automatically-when-users-push-code/>`_
- `GitHub: Linking Issue to PR <https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue>`_
- `GitLab: Default Closing Patterns <https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#default-closing-pattern>`_

.. _Git Trailer format: https://git-scm.com/docs/git-interpret-trailers

----

.. _commit_parser-builtin-release_notice_footer_detection:

Common Release Notice Footer Detection
""""""""""""""""""""""""""""""""""""""

*Introduced in v9.18.0**

All of the PSR built-in parsers implement common release notice footer detection logic
to identify and extract a ``NOTICE`` git trailer that documents any additional release
information the developer wants to provide to the software consumer. The idea extends
from the concept of the ``BREAKING CHANGE:`` git trailer to document any breaking change
descriptions but the ``NOTICE`` trailer is intended to document any information that is
below the threshold of a breaking change while still important for the software consumer
to be aware of. Common uses would be to provide deprecation warnings or more detailed
change usage information for that release. Parsers will collapse single newlines after
the ``NOTICE`` trailer into a single line paragraph. Commits may have more than one
``NOTICE`` trailer in a single commit message. Each
:py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>` will have
a ``release_notices`` attribute that is a tuple of string paragraphs to identify each
release notice.

In the default changelog and release notes template, these release notices will be
formatted into their own section called **Additional Release Information**. Each will
include any commit scope defined and each release notice in alphabetical order.

----

.. _commit_parser-builtin-squash_commit_evaluation:

Common Squash Commit Evaluation
"""""""""""""""""""""""""""""""

*Introduced in v9.17.0*

All of the PSR built-in parsers implement common squash commit evaluation logic to identify
and extract individual commit messages from a single squashed commit. The parsers will
look for common squash commit delimiters and multiple matches of the commit message
format to identify each individual commit message that was squashed. The parsers will
return a list containing each commit message as a separate commit object. Squashed commits
will be evaluated individually for both the level bump and changelog generation. If no
squash commits are found, a list with the single commit object will be returned.

Currently, PSR has been tested against GitHub, BitBucket, and official ``git`` squash
merge commit messages. GitLab does not have a default template for squash commit messages
but can be customized per project or server. If you are using GitLab, you will need to
ensure that the squash commit message format is similar to the example below.

**Example**:

*The following example will extract three separate commit messages from a single GitHub
formatted squash commit message of conventional commit style:*

.. code-block:: text

    feat(config): add new config option (#123)

    * refactor(config): change the implementation of config loading

    * docs(configuration): defined new config option for the project

When parsed with the default conventional-commit parser with squash commits toggled on,
the version bump will be determined by the highest level bump of the three commits (in
this case, a minor bump because of the feature commit) and the release notes would look
similar to the following:

.. code-block:: markdown

    ## Features

    - **config**: add new config option (#123)

    ## Documentation

    - **configuration**: defined new config option for the project (#123)

    ## Refactoring

    - **config**: change the implementation of config loading (#123)

Merge request numbers and commit hash values will be the same across all extracted
commits. Additionally, any :ref:`config-changelog-exclude_commit_patterns` will be
applied individually to each extracted commit so if you are have an exclusion match
for ignoring ``refactor`` commits, the second commit in the example above would be
excluded from the changelog.

.. important::
  When squash commit evaluation is enabled, if you squashed a higher level bump commit
  into the body of a lower level bump commit, the higher level bump commit will be
  evaluated as the level bump for the entire squashed commit. This includes breaking
  change descriptions.

----

.. _commit_parser-builtin-customization:

Customization
"""""""""""""

Each of the built-in parsers can be customized by providing overrides in the
:ref:`config-commit_parser_options` setting of the configuration file. This can
be used to toggle parsing features on and off or to add, modify, or remove the
commit types that are used to determine the level bump for a commit. Review the
API documentation for the specific parser's options class to see what changes to
the default behavior can be made.

----

.. _commit_parser-custom_parser:

Custom Parsers
--------------

Custom parsers can be written to handle commit message styles that are not covered
by the built-in parsers or by option customization of the built-in parsers.

Python Semantic Release provides several building blocks to help you write your parser.
To maintain compatibility with how Python Semantic Release will invoke your parser, you
should use the appropriate object as described below, or create your own object as a
subclass of the original which maintains the same interface. Type parameters are defined
where appropriate to assist with static type-checking.

The :ref:`commit_parser <config-commit_parser>` option, if set to a string which
does not match one of Python Semantic Release's built-in commit parsers, will be
used to attempt to dynamically import a custom commit parser class.

In order to use your custom parser, you must provide how to import the module and class
via the configuration option. There are two ways to provide the import string:

1.  **File Path & Class**: The format is ``"path/to/module_file.py:ClassName"``. This
    is the easiest way to provide a custom parser. This method allows you to store your
    custom parser directly in the repository with no additional installation steps. PSR
    will locate the file, load the module, and instantiate the class. Relative paths are
    recommended and it should be provided relative to the current working directory. This
    import variant is available in v9.16.0 and later.

2.  **Module Path & Class**: The format is ``"package.module_name:ClassName"``. This
    method allows you to store your custom parser in a package that is installed in the
    same environment as PSR. This method is useful if you want to share your custom parser
    across multiple repositories. To share it across multiple repositories generally you will
    need to publish the parser as its own separate package and then ``pip install`` it into
    the current virtual environment. You can also keep it in the same repository as your
    project as long as it is in the current directory of the virtual environment and is
    locatable by the Python import system. You may need to set the ``PYTHONPATH`` environment
    variable if you have a more complex directory structure.  This import variant is available
    in v8.0.0 and later.

    To test that your custom parser is importable, you can run the following command in the
    directory where PSR will be executed:

    .. code-block:: bash

        python -c "from package.module_name import ClassName"

    .. note::
      Remember this is basic python import rules so the package name is optional and generally
      packages are defined by a directory with ``__init__.py`` files.


.. _commit_parser-tokens:

Tokens
""""""
The tokens built into Python Semantic Release's commit parsing mechanism are inspired
by both the error-handling mechanism in `Rust's error handling`_ and its
implementation in `black`_. It is documented that `catching exceptions in Python is
slower`_ than the equivalent guard implemented using ``if/else`` checking when
exceptions are actually caught, so although ``try/except`` blocks are cheap if no
exception is raised, commit parsers should always return an object such as
:py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`
instead of raising an error immediately. This is to avoid catching a potentially large
number of parsing errors being caught as the commit history of a repository is being
parsed. Python Semantic Release does not raise an exception if a commit cannot be parsed.

Python Semantic Release uses :py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`
as the return type of a successful parse operation, and
:py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`
as the return type from an unsuccessful parse of a commit. You should review the API
documentation linked to understand the fields available on each of these objects.

It is important to note, the :py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`
implements an additional method, ``raise_error``. This method raises a
:py:class:`CommitParseError <semantic_release.errors.CommitParseError>` with the message
contained in the ``error`` field, as a convenience.

In Python Semantic Release, the type ``semantic_release.commit_parser.token.ParseResult``
is defined as ``ParseResultType[ParsedCommit, ParseError]``, as a convenient shorthand.

:py:class:`ParseResultType <semantic_release.commit_parser.token.ParseResultType>` is a
generic type, which is the ``Union`` of its two type parameters. One of the types in this
union should be the type returned on a successful parse of the ``commit``, while the other
should be the type returned on an unsuccessful parse of the ``commit``.

A custom parser result type, therefore, could be implemented as follows:

* ``MyParsedCommit`` subclasses :py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`

* ``MyParseError`` subclasses :py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`

* ``MyParseResult = ParseResultType[MyParsedCommit, MyParseError]``

Internally, Python Semantic Release uses ``isinstance()`` to determine if the result
of parsing a commit was a success or not, so you should check that your custom result
and error types return ``True`` from ``isinstance(<object>, ParsedCommit)`` and
``isinstance(<object>, ParseError)`` respectively.

While it's not advisable to remove any of the fields that are available in the built-in
token types, currently only the ``bump`` field of the successful result type is used to
determine how the version should be incremented as part of this release. However, it's
perfectly possible to add additional fields to your tokens which can be populated by
your parser; these fields will then be available on each commit in your
:ref:`changelog template <changelog-templates>`, so you can make additional information
available.

.. _Rust's error handling: https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
.. _black: https://github.com/psf/black/blob/main/src/black/rusty.py
.. _catching exceptions in Python is slower: https://docs.python.org/3/faq/design.html#how-fast-are-exceptions
.. _namedtuple: https://docs.python.org/3/library/typing.html#typing.NamedTuple

.. _commit_parser-parser-options:

Parser Options
""""""""""""""

When writing your own parser, you should accompany the parser with an "options" class
which accepts the appropriate keyword arguments. This class' ``__init__`` method should
store the values that are needed for parsing appropriately. Python Semantic Release will
pass any configuration options from the configuration file's
:ref:`commit_parser_options <config-commit_parser_options>`, into your custom parser options
class. To ensure that the configuration options are passed correctly, the options class
should inherit from the
:py:class:`ParserOptions <semantic_release.commit_parser._base.ParserOptions>` class.

The "options" class is used to validate the options which are configured in the repository,
and to provide default values for these options where appropriate.

.. _commit_parsing-commit-parsers:

Commit Parsers
""""""""""""""

The commit parsers that are built into Python Semantic Release implement an instance
method called ``parse``, which takes a single parameter ``commit`` of type
`git.objects.commit.Commit <gitpython-commit-object>`_, and returns the type
``ParseResultType``.

To be compatible with Python Semantic Release, a commit parser must subclass
:py:class:`CommitParser <semantic_release.commit_parser._base.CommitParser>`.
A subclass must implement the following:

* A class-level attribute ``parser_options``, which must be set to
  :py:class:`ParserOptions <semantic_release.commit_parser._base.ParserOptions>` or a
  subclass of this.

* An ``__init__`` method which takes a single parameter, ``options``, that should be
  of the same type as the class' ``parser_options`` attribute.

* A method, ``parse``, which takes a single parameter ``commit`` that is of type
  `git.objects.commit.Commit <gitpython-commit-object>`_, and returns
  :py:class:`ParseResult <semantic_release.commit_parser.token.ParseResult>`, or a
  subclass of this.

By default, the constructor for
:py:class:`CommitParser <semantic_release.commit_parser._base.CommitParser>`
will set the ``options`` parameter on the ``options`` attribute of the parser, so there
is no need to override this in order to access ``self.options`` during the ``parse``
method. However, if you have any parsing logic that needs to be done only once, it may
be a good idea to perform this logic during parser instantiation rather than inside the
``parse`` method. The parse method will be called once per commit in the repository's
history during parsing, so the effect of slow parsing logic within the ``parse`` method
will be magnified significantly for projects with sizeable Git histories.

Commit Parsers have two type parameters, "TokenType" and "OptionsType". The first
is the type which is returned by the ``parse`` method, and the second is the type
of the "options" class for this parser.

Therefore, a custom commit parser could be implemented via:

.. code-block:: python

    class MyParserOptions(semantic_release.ParserOptions):
        def __init__(self, message_prefix: str) -> None:
            self.prefix = message_prefix * 2


    class MyCommitParser(
        semantic_release.CommitParser[semantic_release.ParseResult, MyParserOptions]
    ):
        def parse(self, commit: git.objects.commit.Commit) -> semantic_release.ParseResult:
            ...

.. _gitpython-commit-object: https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit
