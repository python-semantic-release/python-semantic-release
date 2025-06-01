.. _changelog-templates:

Version Change Reports
======================

When using the :ref:`cmd-version` and :ref:`cmd-changelog` commands, Python
Semantic Release (PSR) will generate a changelog and release notes for your
project automatically in the default configuration. The changelog is rendered
using the `Jinja`_ template engine, and in the default configuration, PSR will
use a built-in template file to render the changelog at the file location
defined by the :ref:`changelog_file <config-changelog-changelog_file>` setting.

Through the use of the templating engine & the
:ref:`template_dir <config-changelog-template_dir>` configuration setting, you
can customize the appearance of your changelog and release notes content. You
may also generate a set of files using your custom template directory and the
templates will be rendered relative to the root of your repository.

Because PSR uses a third-party library, `Jinja`_, as its template engine, we do
not include all the syntax within our documentation but rather you should refer
to the `Template Designer Documentation`_ for guidance on how to customize the
appearance of your release files. If you would like to customize the template
environment itself, then certain options are available to you via
:ref:`changelog environment configuration <config-changelog-environment>`.

If you do not want to use the changelog generation features, you can disable
changelog generation entirely during the :ref:`cmd-version` command by providing
the :ref:`--no-changelog <cmd-version-option-changelog>` command-line option.

.. _Jinja: https://jinja.palletsprojects.com/en/3.1.x/
.. _Template Designer Documentation: https://jinja.palletsprojects.com/en/3.1.x/templates/


.. _changelog-templates-default_changelog:

Using the Default Changelog
---------------------------

If you don't provide any custom templates in the
:ref:`changelog.template_dir <config-changelog-template_dir>`, the default changelog
templates will be used to render the changelog.

PSR provides two default changelog output formats:

1.  Markdown (``.md``), *default*

2.  reStructuredText (``.rst``), *available since v9.11.0*

Both formats are kept in sync with one another to display the equivalent information
in the respective format. The default changelog template is located in the
``data/templates/`` directory within the PSR package. The templates are written in
modular style (ie. multiple files) and during the render process are ultimately
combined together to render the final changelog output. The rendering start point
is the ``CHANGELOG.{FORMAT_EXT}.j2`` underneath the respective format directory.

PSR provides a few configuration options to customize the default changelog output
and can be found under the
:ref:`changelog.default_templates <config-changelog-default_templates>` section
as well as some common configuration options under the :ref:`config-changelog`
section.

To toggle the output format, you only need to set the
:ref:`changelog.default_templates.changelog_file <config-changelog-default_templates-changelog_file>`
file name to include the desired file extension (``.md`` or ``.rst``). If you would
like a different extension for the resulting changelog file, but would like
to still have control over the template format, you can set the
:ref:`changelog.default_templates.output_format <config-changelog-default_templates-output_format>`
configuration setting to the desired format.

A common and *highly-recommended* configuration option is the
:ref:`changelog.exclude_commit_patterns <config-changelog-exclude_commit_patterns>`
setting which allows the user to define regular expressions that will exclude commits
from the changelog output. This is useful to filter out change messages that are not
relevant to your external consumers (ex. ``ci`` and ``test`` in the conventional commit
standard) and only include the important changes that impact the consumer of your
software.

Another important configuration option is the :ref:`changelog.mode <config-changelog-mode>`
setting which determines the behavior of the changelog generation. There are 2
modes that available that described in detail below.

1.  :ref:`changelog-templates-default_changelog-init` when ``mode = "init"``.

2.  :ref:`changelog-templates-default_changelog-update` when ``mode = "update"``.


.. _changelog-templates-default_changelog-init:

Initialization Mode
^^^^^^^^^^^^^^^^^^^

When using the initialization mode, the changelog file will be created from
scratch using the entire git history and **overwrite** any existing changelog
file. This is the default behavior introduced in ``v8.0.0``. This is useful
when you are trying to convert over to Python Semantic Release for the first
time or when you want to automatically update the entire format of your
changelog file.

.. warning::
    If you have an existing changelog in the location you have configured with
    the :ref:`changelog.changelog_file <config-changelog-changelog_file>` setting, PSR
    will overwrite the contents of this file on each release.

    Please make sure to refer to :ref:`changelog-templates-migrating-existing-changelog`.


.. _changelog-templates-default_changelog-update:

Update Mode
^^^^^^^^^^^^

.. note::
  Introduced in ``v9.10.0``.

When using the update mode, only the change information from the last release will
be prepended into the existing changelog file (defined by the
:ref:`changelog.changelog_file <config-changelog-changelog_file>`). This mimics the
behavior that was used in versions prior to ``v8.0.0`` before the conversion to a
templating engine but now uses the `Jinja`_ to accomplish the update. This mode is
best suited for managing changes over the lifetime of your project when you may have
a need to make manual changes or adjustments to the changelog and its not easily
recreated with a template.

**How It Works**

In order to insert the new release information into an existing changelog file, your
changelog file must have an insertion flag to indicate where the new release information
should be inserted. The default template will read in your existing changelog file,
split the content based on the insertion flag, and then recombine the content (including
the insertion flag) with the new release information added after the insertion flag.

The insertion flag is customizable through the
:ref:`changelog.insertion_flag <config-changelog-insertion_flag>` setting. Generally,
your insertion flag should be unique text to your changelog file to avoid any
unexpected behavior. See the examples below.

In the case where the insertion flag is **NOT** found in the existing changelog file, the
changelog file will be re-written without any changes.

If there is no existing changelog file found, then the changelog file will be initialized
from scratch as if the mode was set to ``init``, except the
:ref:`changelog.insertion_flag <config-changelog-insertion_flag>` will be included into the
newly created changelog file.

.. tip::
    We have accomplished changelog updating through the use of the `Jinja`_ templating
    and additional context filters and context variables. This is notable because
    in the case that you want to customize your changelog template, you now can use the
    same logic to enable changelog updates of your custom template!

.. seealso::
    - :ref:`changelog-templates-migrating-existing-changelog`.

**Example**

Given your existing changelog looks like the following with a
:ref:`changelog.insertion_flag <config-changelog-insertion_flag>` set to
``<!-- version list -->``, when you run the :ref:`cmd-version` command, the new release
information will be inserted after the insertion flag.

**Before**

.. code:: markdown

    # CHANGELOG

    <!-- version list -->

    ## 1.0.0

    - Initial Release

**After**

.. code:: markdown

    # CHANGELOG

    <!-- version list -->

    ## v1.1.0

    ### Feature

    - feat: added a new feature

    ### Fix

    - fix: resolved divide by zero error

    ## 1.0.0

    - Initial Release


.. _changelog-templates-default_changelog-examples:

Configuration Examples
^^^^^^^^^^^^^^^^^^^^^^

1.  Goal: Configure an updating reStructuredText changelog with a custom insertion
    flag within ``pyproject.toml``.

    .. code:: toml

        [tool.semantic_release.changelog]
        mode = "update"
        insertion_flag = "..\n    All versions below are listed in reverse chronological order"

        [tool.semantic_release.changelog.default_templates]
        changelog_file = "CHANGELOG.rst"
        output_format = "rst"  # optional because of the file extension

2.  Goal: Configure an updating Markdown changelog with custom file name and default
    insertion flag within a separate config file ``releaserc.json``.

    .. code:: json

        {
          "semantic_release": {
            "changelog": {
              "mode": "update",
              "default_templates": {
                "changelog_file": "docs/HISTORY",
                "output_format": "md"
              }
            }
          }
        }

3.  Goal: Configure an initializing reStructuredText changelog with filtered conventional
    commits patterns and merge commits within a custom config file ``releaserc.toml``.

    .. code:: toml

        [semantic_release.changelog]
        mode = "init"
        default_templates = { changelog_file = "docs/CHANGELOG.rst" }
        exclude_commit_patterns = [
          '''chore(?:\([^)]*?\))?: .+''',
          '''ci(?:\([^)]*?\))?: .+''',
          '''refactor(?:\([^)]*?\))?: .+''',
          '''style(?:\([^)]*?\))?: .+''',
          '''test(?:\([^)]*?\))?: .+''',
          '''build\((?!deps\): .+)''',
          '''Merged? .*''',
        ]

If identified or supported by the parser, the default changelog templates will include
a separate section of breaking changes and additional release information. Refer to the
:ref:`commit parsing <commit_parsing>` section to see how to write commit messages that
will be properly parsed and displayed in these sections.


.. _changelog-templates-default_release_notes:

Using the Default Release Notes
-------------------------------

PSR has the capability to generate release notes as part of the publishing of a
new version similar to the changelog. The release notes are generated using a
`Jinja`_ template and posted to the your remote version control server (VCS) such
as GitHub, GitLab, etc during the :ref:`cmd-version` command. PSR provides a
default built-in template out-of-the-box for generating release notes.

The difference between the changelog and release notes is that the release notes
only contain the changes for the current release. Due to the modularity of the
PSR templates, the format is similar to an individual version of the default
changelog but may include other version specific information.

At this time, the default template for version release notes is only available
in Markdown format for all VCS types.

If you want to review what the default release notes look like you can use the
following command to print the release notes to the console (remove any configuration
for defining a custom template directory):

.. code:: console

    # Create a current tag
    git tag v1.0.0
    semantic-release --noop changelog --post-to-release-tag v1.0.0

The default template provided by PSR will respect the
:ref:`config-changelog-default_templates-mask_initial_release` setting and
will also add a comparison link to the previous release if one exists without
customization.

As of ``v9.18.0``, the default release notes will also include a statement to
declare which license the project was released under. PSR determines which license
to declare based on the value of ``project.license-expression`` in the ``pyproject.toml``
file as defined in the `PEP 639`_ specification.

.. seealso::
    - To personalize your release notes, see the
      :ref:`changelog-templates-custom_release_notes` section.

.. _PEP 639: https://peps.python.org/pep-0639/

.. _changelog-templates-template-rendering:

Custom Changelogs
-----------------

If you would like to customize the appearance of your changelog, you can create
your own custom templates and configure PSR to render your templates instead
during the :ref:`cmd-version` and :ref:`cmd-changelog` commands.

To use a custom template, you need to create a directory within your repository
and set the :ref:`template_dir <config-changelog-template_dir>` setting to the name
of this directory. The default name is ``"templates"``.

Templates are identified by giving a ``.j2`` extension to the template file. Any such
templates have the ``.j2`` extension removed from the target file. Therefore, to render
an output file ``foo.csv``, you should create a template called ``foo.csv.j2`` within
your template directory.

If you have additional files that you would like to render alongside your changelog,
you can place these files within the template directory. A file within your template
directory which does *not* end in ``.j2`` will not be treated as a template; it will
be copied to its target location without being rendered by the template engine.

.. tip::
    Hidden files within the template directory (i.e. filenames that begin with a
    period ``"."``) are *excluded* from the rendering process. Hidden folders
    within the template directory are also excluded, *along with all files and
    folders contained within them*. This is useful for defining macros or other
    template components that should not be rendered individually.

.. tip::
    When initially starting out at customizing your own changelog templates, you
    should reference the default template embedded within PSR. The template directory
    is located at ``data/templates/`` within the PSR package. Within our templates
    directory we separate out each type of commit parser (e.g. conventional) and the
    content format type (e.g. markdown). You can copy this directory to your
    repository's templates directory and then customize the templates to your liking.


.. _changelog-templates-template-rendering-directory-structure:

Directory Structure
^^^^^^^^^^^^^^^^^^^

When the templates are rendered, files within the templates directory tree are output
to the location within your repository that has the *same relative path* to the root
of your project as the *relative path of the template within the templates directory*.

**Example**

An example project has the following structure:

.. code-block::

    example-project/
    ├── src/
    │   └── example_project/
    │       └── __init__.py
    └── ch-templates/
        ├── CHANGELOG.md.j2
        ├── .components/
        │   └── authors.md.j2
        ├── .macros.j2
        ├── src/
        │   └── example_project/
        │       └── data/
        │           └── data.json.j2
        └── static/
            └── config.cfg

And a custom templates folder configured via the following snippet in ``pyproject.toml``:

.. code-block:: toml

    [tool.semantic_release.changelog]
    template_dir = "ch-templates"

After running a release with Python Semantic Release, the directory structure
of the project will now look like this (excluding the template directory):

.. code-block::

    example-project/
    ├── CHANGELOG.md
    ├── src/
    │   └── example_project/
    │       ├── data/
    │       │   └── data.json
    │       └── __init__.py
    └── static/
        └── config.cfg

Importantly, note the following:

* There is no top-level ``.macros`` file created, because hidden files are excluded
  from the rendering process.

* There is no top-level ``.components`` directory created, because hidden folders and
  all files and folders contained within it are excluded from the rendering process.

* The ``.components/authors.md.j2`` file is not rendered directly, however, it is
  used as a component to the ``CHANGELOG.md.j2`` via an ``include`` statement in the
  changelog template.

* To render data files into the ``src/`` folder, the path to which the template should
  be rendered has to be created within the ``ch-templates`` directory.

* The ``ch-templates/static`` folder is created at the top-level of the project, and the
  file ``ch-templates/static/config.cfg`` is *copied, not rendered* to the new top-level
  ``static`` folder.

You may wish to leverage this behavior to modularize your changelog template, to
define macros in a separate file, or to reference static data which you would like
to avoid duplicating between your template environment and the remainder of your
project.


.. _changelog-templates-template-rendering-template-context:

Changelog Template Context
^^^^^^^^^^^^^^^^^^^^^^^^^^

During the rendering of a directory tree, Python Semantic Release provides information
about the history of the project available within the templating environment in order
for it to be used to generate the changelog and other desired documents.

Important project information is provided to the templating environment through
the global variable ``context`` or ``ctx`` for short. Within the template environment,
the ``context`` object has the following attributes:

* ``changelog_insertion_flag (str)``: the insertion flag used to determine where the new
  release information should be inserted into the changelog file. This value is passed
  directly from :ref:`changelog.insertion_flag <config-changelog-insertion_flag>`.

  *Introduced in v9.10.0.*

  **Example Usage:**

  .. code:: jinja

      {%  set changelog_parts = prev_changelog_contents.split(
              ctx.changelog_insertion_flag, maxsplit=1
          )
      %}

* ``changelog_mode (Literal["init", "update"])``: the mode of the changelog generation
  currently being used. This can be used to determine different rendering logic. This
  value is passed directly from the :ref:`changelog.mode <config-changelog-mode>`
  configuration setting.

  *Introduced in v9.10.0.*

  **Example Usage:**

  .. code:: jinja

      {%    if ctx.changelog_mode == "init"
      %}{%    include ".changelog_init.md.j2"
      %}{#
      #}{%  elif ctx.changelog_mode == "update"
      %}{%    include ".changelog_update.md.j2"
      %}{#
      #}{%  endif
      %}

* ``history (ReleaseHistory)``: the
  :class:`ReleaseHistory <semantic_release.changelog.release_history.ReleaseHistory>`
  instance for the project (See the
  :ref:`Release History <changelog-templates-template-rendering-template-context-release-history>`
  section for more information).

  **Example Usage:**

  .. code:: jinja

      {%    set unreleased_commits = ctx.history.unreleased | dictsort
      %}{%  for release in context.history.released.values()
      %}{%    include ".versioned_changes.md.j2"
      #}{%  endfor
      %}

* ``hvcs_type (str)``: the name of the VCS server type currently configured. This can
  be used to determine which filters are available or different rendering logic.

  *Introduced in v9.6.0.*

  **Example Usage:**

  .. code:: jinja

      {%    if ctx.hvcs_type == "github"
      %}{{   "29" | pull_request_url
      }}{#
      #}{%  elif ctx.hvcs_type == "gitlab"
      %}{{    "29" | merge_request_url
      }}{#
      #}{%  endif
      %}

* ``mask_initial_release (bool)``: a boolean value indicating whether the initial release
  should be masked with a generic message. This value is passed directly from the
  :ref:`changelog.default_templates.mask_initial_release <config-changelog-default_templates-mask_initial_release>`
  configuration setting.

  *Introduced in v9.14.0.*

  **Example Usage:**

  .. code:: jinja

      #}{%  if releases | length == 1 and ctx.mask_initial_release
      %}{#    # On a first release, generate a generic message
      #}{%    include ".components/first_release.md.j2"
      %}{%  else
      %}{#    # Not the first release
      #}{%    include ".components/versioned_changes.md.j2"
      %}{%  endif
      %}

* ``repo_name (str)``: the name of the current repository parsed from the Git url.

  **Example Usage:**

  .. code:: jinja

      {{ ctx.repo_name }}

  .. code:: markdown

      example_repo

* ``repo_owner (str)``: the owner of the current repository parsed from the Git url.

  **Example Usage:**

  .. code:: jinja

      {{ ctx.repo_owner }}

  .. code:: markdown

      example_org

* ``prev_changelog_file (str)``: the path to the previous changelog file that should
  be updated with the new release information. This value is passed directly from
  :ref:`changelog.changelog_file <config-changelog-changelog_file>`.

  *Introduced in v9.10.0.*

  **Example Usage:**

  .. code:: jinja

      {% set prev_changelog_contents = prev_changelog_file | read_file | safe %}


.. _changelog-templates-template-rendering-template-context-release-history:

Release History
"""""""""""""""

A :py:class:`ReleaseHistory <semantic_release.changelog.release_history.ReleaseHistory>`
object has two attributes: ``released`` and ``unreleased``.

The ``unreleased`` attribute is of type ``Dict[str, List[ParseResult]]``. Each commit
in the current branch's commit history since the last release on this branch is grouped
by the ``type`` attribute of the
:py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`
returned by the commit parser, or if the parser returned a
:py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`
then the result is grouped under the ``"unknown"`` key.

For this reason, every element of ``ReleaseHistory.unreleased["unknown"]`` is a
:py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`, and
every element of every other value in ``ReleaseHistory.unreleased`` is of type
:py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`.

Typically, commit types will be ``"feature"``, ``"fix"``, ``"breaking"``, though the
specific types are determined by the parser. For example, the
:py:class:`EmojiCommitParser <semantic_release.commit_parser.emoji.EmojiCommitParser>`
uses a textual representation of the emoji corresponding to the most significant change
introduced in a commit (e.g. ``":boom:"``) as the different commit types. As a template
author, you are free to customize how these are presented in the rendered template.

.. note::
   If you are using a custom commit parser following the guide at
   :ref:`commit_parser-custom_parser`, your custom implementations of
   :py:class:`ParseResult <semantic_release.commit_parser.token.ParseResult>`,
   :py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`
   and :py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>`
   will be used in place of the built-in types.

The ``released`` attribute is of type ``Dict[Version, Release]``. The keys of this
dictionary correspond to each version released within this branch's history, and
are of type :py:class:`Version <semantic_release.version.version.Version>`. You can
use the ``as_tag()`` method to render these as the Git tag that they correspond to
inside your template.

A :py:class:`Release <semantic_release.changelog.release_history.Release>` object
has an ``elements`` attribute, which has the same structure as the ``unreleased``
attribute of a
:py:class:`ReleaseHistory <semantic_release.changelog.release_history.ReleaseHistory>`;
that is, ``elements`` is of type ``Dict[str, List[ParseResult]]``, where every element
of ``elements["unknown"]`` is a
:py:class:`ParseError <semantic_release.commit_parser.token.ParseError>`, and elements
of every other value correspond to the ``type`` attribute of the
:py:class:`ParsedCommit <semantic_release.commit_parser.token.ParsedCommit>` returned
by the commit parser.

The commits represented within each ``ReleaseHistory.released[version].elements``
grouping are the commits which were made between version and the release corresponding
to the previous version. That is, given two releases ``Version(1, 0, 0)`` and
``Version(1, 1, 0)``, ``ReleaseHistory.released[Version(1, 0, 0)].elements`` contains
only commits made after the release of ``Version(1, 0, 0)`` up to and including the
release of ``Version(1, 1, 0)``.

To maintain a consistent order of subsections in the changelog headed by the commit
type, it's recommended to use Jinja's
`dictsort <https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.dictsort>`_
filter.

Each :py:class:`Release <semantic_release.changelog.release_history.Release>`
object also has the following attributes:

* ``tagger: git.Actor``: The tagger who tagged the release.

* ``committer: git.Actor``: The committer who made the release commit.

* ``tagged_date: datetime``: The date and time at which the release was tagged.

.. seealso::
   * :ref:`commit_parser-builtin`
   * :ref:`Commit Parser Tokens <commit_parser-tokens>`
   * `git.Actor <https://gitpython.readthedocs.io/en/stable/reference.html#git.objects.util.Actor>`_
   * `datetime.strftime Format Codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_


.. _changelog-templates-custom_templates-filters:

Changelog Template Filters
^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the context variables, PSR seeds the template environment with a set of
custom functions (commonly called ``filters`` in `Jinja`_ terminology) for use within the
template. Filter's first argument is always piped (``|``) to the function while any additional
arguments are passed in parentheses like normal function calls.

The filters provided vary based on the VCS configured and available features:

* ``autofit_text_width (Callable[[textStr, maxWidthInt, indent_sizeInt], textStr])``: given a
  text string, fit the text to the maximum width provided. This filter is useful when you want
  to wrap text to a specific width. The filter will attempt to break the text at word boundaries
  and will indent the text by the amount specified in the ``indent_size`` parameter.

  *Introduced in v9.12.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "This is a long string that needs to be wrapped to a specific width" | autofit_text_width(40, 4) }}

  **Markdown Output:**

  .. code:: markdown

      This is a long string that needs to be
          wrapped to a specific width

* ``convert_md_to_rst (Callable[[MdStr], RstStr])``: given a markdown string, convert it to
  reStructuredText format. This filter is useful when building a reStructuredText changelog
  but your commit messages are in markdown format. It is utilized by the default RST changelog
  template. It is limited in its ability to convert all markdown to reStructuredText, but it
  handles most common cases (bold, italics, inline-raw, etc.) within commit messages.

  *Introduced in v9.11.0.*

  **Example Usage:**

  .. code:: jinja

      {{  "\n* %s (`%s`_)\n" | format(
            commit.message.rstrip() | convert_md_to_rst,
            commit.short_hash,
          )
      }}

* ``create_pypi_url(package_name: str, version: str = "")``: given a package name and an optional
  version, return a URL to the PyPI page for the package. If a version is provided, the URL will
  point to the specific version page. If no version is provided, the URL will point to the package
  page.

  *Introduced in v9.18.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "example-package" | create_pypi_url }}
      {{ "example-package" | create_pypi_url("1.0.0") }}

  **Markdown Output:**

  .. code:: markdown

      https://pypi.org/project/example-package
      https://pypi.org/project/example-package/1.0.0

* ``create_release_url (Callable[[TagStr], UrlStr])``: given a tag, return a URL to the release
  page on the remote vcs. This filter is useful when you want to link to the release page on the
  remote vcs.

  *Introduced in v9.18.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "v1.0.0" | create_release_url }}

  **Markdown Output:**

  .. code:: markdown

      https://example.com/example/repo/releases/tag/v1.0.0

* ``create_server_url (Callable[[PathStr, AuthStr | None, QueryStr | None, FragmentStr | None], UrlStr])``:
  when given a path, prepend the configured vcs server host and url scheme.  Optionally you
  can provide, a auth string, a query string or a url fragment to be normalized into the
  resulting url. Parameter order is as described above respectively.

  *Introduced in v9.6.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "example/repo.git" | create_server_url }}
      {{ "example/repo" | create_server_url(None, "results=1", "section-header") }}

  **Markdown Output:**

  .. code:: markdown

      https://example.com/example/repo.git
      https://example.com/example/repo?results=1#section-header


* ``create_repo_url (Callable[[RepoPathStr, QueryStr | None, FragmentStr | None], UrlStr])``:
  when given a repository path, prepend the configured vcs server host, and repo namespace.
  Optionally you can provide, an additional query string and/or a url fragment to also put
  in the url. Parameter order is as described above respectively. This is similar to
  ``create_server_url`` but includes the repo namespace and owner automatically.

  *Introduced in v9.6.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "releases/tags/v1.0.0" | create_repo_url }}
      {{ "issues" | create_repo_url("q=is%3Aissue+is%3Aclosed") }}

  **Markdown Output:**

  .. code:: markdown

      https://example.com/example/repo/releases/tags/v1.0.0
      https://example.com/example/repo/issues?q=is%3Aissue+is%3Aclosed

* ``commit_hash_url (Callable[[hashStr], UrlStr])``: given a commit hash, return a URL to the
  commit in the remote.

  *Introduced in v8.0.0.*

  **Example Usage:**

  .. code:: jinja

      {{ commit.hexsha | commit_hash_url }}

  **Markdown Output:**

  .. code:: markdown

      https://example.com/example/repo/commit/a1b2c3d435657f5d339ba10c7b1ed81b460af51d

* ``compare_url (Callable[[StartRefStr, StopRefStr], UrlStr])``: given a starting git reference
  and a ending git reference create a comparison url between the two references that can be
  opened on the remote

  *Introduced in v9.6.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "v1.0.0" | compare_url("v1.1.0") }}

  **Markdown Output:**

  .. code:: markdown

      https://example.com/example/repo/compare/v1.0.0...v1.1.0

* ``issue_url (Callable[[IssueNumStr | IssueNumInt], UrlStr])``: given an issue
  number, return a URL to the issue on the remote vcs. In v9.12.2, this filter
  was updated to handle a string that has leading prefix symbols (ex. ``#32``)
  and will strip the prefix before generating the URL.

  *Introduced in v9.6.0, Modified in v9.12.2.*

  **Example Usage:**

  .. code:: jinja

      {# Add Links to issues annotated in the commit message
       # NOTE: commit.linked_issues is only available in v9.15.0 or greater
       #
      #}{% for issue_ref in commit.linked_issues
      %}{{     "- [%s](%s)" | format(issue_ref, issue_ref | issue_url)
      }}{% endfor
      %}

  **Markdown Output:**

  .. code:: markdown

      - [#32](https://example.com/example/repo/issues/32)

* ``merge_request_url (Callable[[MergeReqStr | MergeReqInt], UrlStr])``: given a
  merge request number, return a URL to the merge request in the remote. This is
  an alias to the ``pull_request_url`` but only available for the VCS that uses
  the merge request terminology. In v9.12.2, this filter was updated to handle
  a string that has leading prefix symbols (ex. ``#29``) and will strip the prefix
  before generating the URL.

  *Introduced in v9.6.0, Modified in v9.12.2.*

  **Example Usage:**

  .. code:: jinja

      {{
          "[%s](%s)" | format(
            commit.linked_merge_request,
            commit.linked_merge_request | merge_request_url
          )
      }}
      {# commit.linked_merge_request is only available in v9.13.0 or greater #}

  **Markdown Output:**

  .. code:: markdown

      [#29](https://example.com/example/repo/-/merge_requests/29)

* ``pull_request_url (Callable[[PullReqStr | PullReqInt], UrlStr])``: given a pull
  request number, return a URL to the pull request in the remote. For remote vcs'
  that use merge request terminology, this filter is an alias to the
  ``merge_request_url`` filter function. In v9.12.2, this filter was updated to
  handle a string that has leading prefix symbols (ex. ``#29``) and will strip
  the prefix before generating the URL.

  *Introduced in v9.6.0, Modified in v9.12.2.*

  **Example Usage:**

  .. code:: jinja

      {# Create a link to the merge request associated with the commit
       # NOTE: commit.linked_merge_request is only available in v9.13.0 or greater
      #}{{
          "[%s](%s)" | format(
            commit.linked_merge_request,
            commit.linked_merge_request | pull_request_url
          )
      }}

  **Markdown Output:**

  .. code:: markdown

      [#29](https://example.com/example/repo/pull/29)

* ``format_w_official_vcs_name (Callable[[str], str])``: given a format string, insert
  the official VCS type name into the string and return. This filter is useful when you want to
  display the proper name of the VCS type in a changelog or release notes. The filter supports
  three different replace formats: ``%s``, ``{}``, and ``{vcs_name}``.

  *Introduced in v9.18.0.*

  **Example Usage:**

  .. code:: jinja

      {{ "%s Releases" | format_w_official_vcs_name }}
      {{ "{} Releases" | format_w_official_vcs_name }}
      {{ "{vcs_name} Releases" | format_w_official_vcs_name }}

  **Markdown Output:**

  .. code:: markdown

      GitHub Releases
      GitHub Releases
      GitHub Releases

* ``read_file (Callable[[str], str])``: given a file path, read the file and
  return the contents as a string. This function was added specifically to
  enable the changelog update feature where it would load the existing changelog
  file into the templating environment to be updated.

  *Introduced in v9.10.0.*

  **Example Usage:**

  .. code:: jinja

      {% set prev_changelog_contents = prev_changelog_file | read_file | safe %}


* ``sort_numerically (Callable[[Iterable[str], bool], list[str]])``: given a
  sequence of strings with possibly some non-number characters as a prefix or suffix,
  sort the strings as if they were just numbers from lowest to highest. This filter
  is useful when you want to sort issue numbers or other strings that have a numeric
  component in them but cannot be cast to a number directly to sort them. If you want
  to sort the strings in reverse order, you can pass a boolean value of ``True`` as the
  second argument.

  *Introduced in v9.16.0.*

  **Example Usage:**

  .. code:: jinja

      {{ ["#222", "#1023", "#444"] | sort_numerically }}
      {{ ["#222", "#1023", "#444"] | sort_numerically(True) }}

  **Markdown Output:**

  .. code:: markdown

        ['#222', '#444', '#1023']
        ['#1023', '#444', '#222']


Availability of the documented filters can be found in the table below:

==========================  =========  =====  ======  ======
**filter - hvcs_type**      bitbucket  gitea  github  gitlab
==========================  =========  =====  ======  ======
autofit_text_width             ✅       ✅      ✅      ✅
convert_md_to_rst              ✅       ✅      ✅      ✅
create_pypi_url                ✅       ✅      ✅      ✅
create_server_url              ✅       ✅      ✅      ✅
create_release_url             ❌       ✅      ✅      ✅
create_repo_url                ✅       ✅      ✅      ✅
commit_hash_url                ✅       ✅      ✅      ✅
compare_url                    ✅       ❌      ✅      ✅
format_w_official_vcs_name     ✅       ✅      ✅      ✅
issue_url                      ❌       ✅      ✅      ✅
merge_request_url              ❌       ❌      ❌      ✅
pull_request_url               ✅       ✅      ✅      ✅
read_file                      ✅       ✅      ✅      ✅
sort_numerically               ✅       ✅      ✅      ✅
==========================  =========  =====  ======  ======

.. seealso::
   * `Filters <https://jinja.palletsprojects.com/en/3.1.x/templates/#filters>`_


.. _changelog-templates-template-rendering-example:

Example
^^^^^^^

The following template is a simple example of how to render a changelog using
the PSR template context to create a changelog in Markdown format.

**Configuration:** ``pyproject.toml``

.. code:: toml

    [tool.semantic_release.changelog]
    template_dir = "templates"

**Template:** ``templates/CHANGELOG.md.j2``

.. code:: jinja

    # CHANGELOG

    {%    for version, release in ctx.history.released.items()
    %}{{
            "## %s (%s)" | format(version.as_tag(), release.tagged_date.strftime("%Y-%m-%d"))

    }}{%    for type_, commits in release["elements"] if type_ != "unknown" | dictsort
    %}{{
              "### %s" | format(type_ | title)

    }}{%      for commit in commits
    %}{{
                "* %s ([`%s`](%s))" | format(
                  commit.descriptions[0] | capitalize,
                  commit.hexsha[:7],
                  commit.hexsha | commit_hash_url,
                )

    }}{%      endfor
    %}{%    endfor
    %}{%  endfor
    %}

**Result:** ``CHANGELOG.md``

.. code:: markdown

    # CHANGELOG

    ## v1.1.0 (2022-01-01)

    ### Feature

    * Added a new feature ([`a1b2c3d`](https://github.com/example/repo/commit/a1b2c3d))

    ## v1.0.0 (2021-12-31)

    ### Fix

    * Resolved divide by zero error ([`e4f5g6h`](https://github.com/example/repo/commit/e4f5g6h))

It is important to note that the template utilizes the ``context`` variable to extract
the project history as well as the ``commit_hash_url`` filter to generate a URL to
the remote VCS for each commit. Both of these are injected into the template environment
by PSR.


.. _changelog-templates-custom_release_notes:

Custom Release Notes
--------------------

If you would like to customize the appearance of your release notes, you can add a
hidden file named ``.release_notes.md.j2`` at the root of your
:ref:`changelog.template_dir <config-changelog-template_dir>`. This file will
automatically be detected and used to render the release notes during the
:ref:`cmd-version` and :ref:`cmd-changelog` commands.

A similar :ref:`template rendering <changelog-templates-template-rendering>`
mechanism is used to render the release notes as is used for the changelog. There
are minor differences in the context available to the release notes template but
the template directory structure and modularity is maintained.

.. tip::
    When initially starting out at customizing your own release notes template, you
    should reference the default template embedded within PSR. The release notes template
    can be found in the directory ``data/templates/<parser>/md`` within the PSR package.


.. _changelog-templates-custom_release_notes-context:

Release Notes Context
^^^^^^^^^^^^^^^^^^^^^

All of the changelog's
:ref:`template context <changelog-templates-template-rendering-template-context>` is
exposed to the `Jinja`_ template when rendering the release notes.

Additionally, the following two globals are available to the template:

* ``release`` (:py:class:`Release <semantic_release.changelog.release_history.Release>`):
  contains metadata about the content of the release, as parsed from commit logs

  *Introduced in v8.0.0.*

* ``version`` (:py:class:`Version <semantic_release.version.version.Version>`): contains
  metadata about the software version to be released and its ``git`` tag

  *Introduced in v8.0.0.*


.. _changelog-templates-release-notes-template-example:

Example
^^^^^^^

Below is an example template that can be used to render release notes (it's similar to
GitHub's `automatically generated release notes`_):

.. _Automatically generated release notes: https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes

**Configuration:** ``pyproject.toml``

.. code:: toml

    [tool.semantic_release.changelog]
    template_dir = "templates"

**Template:** ``templates/.release_notes.md.j2``

.. code:: jinja

    ## What's Changed
    {%    for type_, commits in release["elements"] | dictsort
    %}{%-   if type_ != "unknown"
    %}{{
              "### %s" | format(type_ | title)

    }}{%      for commit in commits
    %}{{
                "* %s by %s in [`%s`](%s)" | format(
                  commit.descriptions[0] | capitalize,
                  commit.commit.author.name,
                  commit.hexsha[:7],
                  commit.hexsha | commit_hash_url,
                )

    }}{%-     endfor
    %}{%    endif
    %}{%  endfor
    %}

**Result:** ``https://github.com/example/repo/releases/tag/v1.1.0``

.. code:: markdown

      ## What's Changed

      ### Feature

      * Added a new feature by John Doe in [`a1b2c3d`](https://github.com/example/repo/commit/a1b2c3d)


.. _changelog-templates-migrating-existing-changelog:

Migrating an Existing Changelog
-------------------------------

**v9.10.0 or greater**

Migrating an existing changelog is simple with Python Semantic Release! To preserve your
existing changelog, follow these steps:

1.  **Set the changelog.mode to "update"** in your configuration file. This will ensure that
    only the new release information is added to your existing changelog file.

2.  **Set the changelog.insertion_flag to a unique string.** You may use the default value
    or set it to a unique string that is not present in your existing changelog file. This
    flag is used to determine where the new release information should be inserted into your
    existing changelog.

3.  **Add the insertion flag to your changelog file.** This must match the value you set in
    step 2. The insertion flag should be placed in the location above where you would like
    the new release information to be inserted.

.. note::
    If you are trying to convert an existing changelog to a new format, you will need to do
    most of the conversion manually (or rebuild via init and modify) and make sure to include
    your insertion flag into the format of the new changelog.

**Prior to v9.10.0**

If you have an existing changelog that you would like to preserve, you will need to
add the contents of the changelog file to your changelog template - either directly
or via Jinja's `include <https://jinja.palletsprojects.com/en/3.1.x/templates/#include>`_
tag.

If you would like only the history from your next release onwards to be rendered
into the changelog in addition to the existing changelog, you can add an `if statement
<https://jinja.palletsprojects.com/en/3.1.x/templates/#if>`_ based upon the versions in
the keys of ``context.released``.


.. _changelog-templates-upgrading-templates:

Upgrading Templates
-------------------

As PSR evolves, new features and improvements are added to the templating engine. If you
have created your own custom templates, you may need to update them to take advantage of
some new features. Below are some instructions on how to upgrade your templates to gain
the benefits of the new features.

.. _changelog-templates-upgrading-updating_changelog:

Incrementally Updating Changelog Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    This section is only relevant if you are upgrading from a version of PSR
    greater than v8.0.0 and prior to ``v9.10.0`` and have created your own
    custom templates.

If you have previously created your own custom templates and would like to gain
the benefits of the new updating changelog feature, you will need to make a few
changes to your existing templates.

The following steps are a few suggestions to help upgrade your templates but
primarily you should review the embedded default templates in the PSR package
for a full example. You can find the default templates at `data/templates/`__
directory.

__ https://github.com/python-semantic-release/python-semantic-release/tree/master/src/semantic_release/data/templates

1.  **Add a conditional to check the changelog_mode.** This will allow you
    to determine if you should render the entire changelog or just the new
    release information. See ``data/templates/*/md/CHANGELOG.md.j2`` for reference.

2.  **Use the new read_file filter** to read in the existing changelog file
    ``ctx.prev_changelog_file``. This will allow you to include the existing
    changelog content in your new changelog file. See
    ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.

3.  **Split the changelog content based on the insertion flag.** This will
    allow you to insert the new release information after the insertion flag
    (``ctx.changelog_insertion_flag``). See
    ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.

4.  **Print the leading content before the insertion flag.** This ensures you
    maintain any content that should be included before the new release information.
    See ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.

5.  **Print your insertion flag.** This is imperative to ensure that the resulting
    changelog can be updated in the future. See
    ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.

6.  **Print the new release information.** Be sure to consider both unreleased
    and released commits during this step because of the :ref:`cmd-changelog`
    command that can be run at any time. See
    ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.

7.  **Print the trailing content after the insertion flag.** This ensures you
    maintain any content that should be included after the new release information.
    See ``data/templates/*/md/.components/changelog_update.md.j2`` for reference.


.. tip::
    Modularity of your templates is key to handling both modes of changelog
    generation. Reference the default templates for examples on how we handle
    both modes and defensively handle numerous breaking scenarios.

.. tip::
    If you are having trouble upgrading your templates, please post a question
    on the `PSR GitHub`__

    __ https://github.com/python-semantic-release/python-semantic-release/issues
