.. _commit-parsing:

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
  if you plan to use any similar programs in tadem with PSR, you should be aware of the
  differences in feature support and fall back to the official format guidelines if
  necessary.

.. _Semantic Versioning: https://semver.org/

----

.. _commit_parser-builtin:

Built-in Commit Parsers
-----------------------

The following parsers are built in to Python Semantic Release:

- :ref:`AngularCommitParser <commit_parser-builtin-angular>`
- :ref:`EmojiCommitParser <commit_parser-builtin-emoji>`
- :ref:`ScipyCommitParser <commit_parser-builtin-scipy>`
- :ref:`TagCommitParser <commit_parser-builtin-tag>` *(deprecated in v9.12.0)*

----

.. _commit_parser-builtin-angular:

Angular Commit Parser
"""""""""""""""""""""

A parser that is designed to parse commits formatted according to the
`Angular Commit Style Guidelines`_.  The parser is implemented with the following
logic in relation to how PSR's core features:

- **Version Bump Determination**: This parser extracts the commit type from the subject
  line of the commit (the first line of a commit messsage). This type is matched against
  the configuration mapping to determine the level bump for the specific commit. If the
  commit type is not found in the configuration mapping, the commit is considered a
  non-conformative commit and will return it as a ParseError object and ultimately a commit
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

**Limitations:**

- Squash commits are not currently supported. This means that the level bump for a squash
  commit is only determined by the subject line of the squash commit. Our default changelog
  template currently writes out the entire commit message body in the changelog in order to
  provide the full detail of the changes. Track the implementation of this feature with
  the issues `#733`_, `#1085`_, and `PR#1112`_.

- Commits with the ``revert`` type are not currently supported. Track the implementation
  of this feature in the issue `#402`_.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.angular.AngularParserOptions>`.

.. _#402: https://github.com/python-semantic-release/python-semantic-release/issues/402
.. _#733: https://github.com/python-semantic-release/python-semantic-release/issues/733
.. _#1085: https://github.com/python-semantic-release/python-semantic-release/issues/1085
.. _Angular Commit Style Guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
.. _PR#1112: https://github.com/python-semantic-release/python-semantic-release/pull/1112

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
  line of the commit (the first line of a commit messsage). If more than one emoji is
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

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.emoji.EmojiParserOptions>`.

.. _Gitmoji Specification: https://gitmoji.dev/specification

----

.. _commit_parser-builtin-scipy:

Scipy Commit Parser
"""""""""""""""""""

A parser that is designed to parse commits formatted according to the
`Scipy Commit Style Guidlines`_. This is essentially a variation of the `Angular Commit Style
Guidelines`_ with all different commit types. Because of this small variance, this parser
only extends our :ref:`commit_parser-builtin-angular` parser with pre-defined scipy commit types
in the default Scipy Parser Options and all other features are inherited.

If no commit parser options are provided via the configuration, the parser will use PSR's
built-in :py:class:`defaults <semantic_release.commit_parser.scipy.ScipyParserOptions>`.

.. _Scipy Commit Style Guidlines: https://scipy.github.io/devdocs/dev/contributor/development_workflow.html#writing-the-commit-message

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
VCS platform. The parsers evaluate the subject line for a paranthesis-enclosed number
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
the need of extra git trailors (although PSR does support multiple git trailors). PSR support
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
used to attempt to dynamically import a custom commit parser class. As such you will
need to ensure that your custom commit parser is import-able from the environment in
which you are running Python Semantic Release. The string should be structured in the
standard ``module:attr`` format; for example, to import the class ``MyCommitParser``
from the file ``custom_parser.py`` at the root of your repository, you should specify
``"commit_parser=custom_parser:MyCommitParser"`` in your configuration, and run the
``semantic-release`` command line interface from the root of your repository. Equally
you can ensure that the module containing your parser class is installed in the same
virtual environment as semantic-release. If you can run
``python -c "from $MODULE import $CLASS"`` successfully, specifying
``commit_parser="$MODULE:$CLASS"`` is sufficient. You may need to set the
``PYTHONPATH`` environment variable to the directory containing the module with
your commit parser.

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

.. _commit-parsing-parser-options:

Parser Options
""""""""""""""

To provide options to the commit parser which is configured in the :ref:`configuration file
<configuration>`, Python Semantic Release includes a
:py:class:`ParserOptions <semantic_release.commit_parser._base.ParserOptions>`
class. Each parser built into Python Semantic Release has a corresponding "options" class, which
subclasses :py:class:`ParserOptions <semantic_release.commit_parser._base.ParserOptions>`.

The configuration in :ref:`commit_parser_options <config-commit_parser_options>` is passed to the
"options" class which is specified by the configured :ref:`commit_parser <config-commit_parser>` -
more information on how this is specified is below.

The "options" class is used to validate the options which are configured in the repository,
and to provide default values for these options where appropriate.

If you are writing your own parser, you should accompany it with an "options" class
which accepts the appropriate keyword arguments. This class' ``__init__`` method should
store the values that are needed for parsing appropriately.

.. _commit-parsing-commit-parsers:

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

By default, the constructor for :py:class:`CommitParser <semantic_release.commit_parser._base.CommitParser>`
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

.. _angular commit guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
.. _gitpython-commit-object: https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit
