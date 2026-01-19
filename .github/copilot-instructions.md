# Copilot Instructions for python-semantic-release

This document explains how GitHub Copilot-like automated agents should interact with
the python-semantic-release repository.

## Project Overview

Python Semantic Release is a tool for automating semantic versioning and marking releases for
various types of software projects. It analyzes commit messages with various commit parsers
(the most notable being the Conventional Commits specification) to determine what the next
version should be and facilitates release steps that the developer generally has to do. This
includes generating changelogs, stamping the code with version strings, creating a repository
tag and annotating releases on a remote Git server with version-specific release notes.

**Key Components:**
- **CLI**: Command-line interface for version management, changelog generation, and publishing
- **Commit Parsers**: Parse commit messages to determine version bumps
  (Supports Conventional-Commits, Emoji, and Scipy format)
- **HVCS Integration**: Integrations with GitHub, GitLab, Gitea, and Bitbucket for releasing
- **Version Management**: Semantic versioning logic and version calculation
- **Changelog Generation**: Automated and customizable changelog creation using Jinja2 templates

## Development Setup

### Installation

Requires 3.9+ for development dependencies, but runtime supports 3.8+.

```bash
# Set up for development
pip install -e .[build,dev,docs,mypy,test]
```

### Running the Application

```bash
# See the CLI help
semantic-release --help

# Common commands
semantic-release version
semantic-release changelog
semantic-release publish
```

### Making Changes

Minimal PR checklist (run locally before proposing a PR):

- [ ] Run pre-PR checklist script (see below)
- [ ] If you added dependencies: update `pyproject.toml` and mention them in the PR.
- [ ] Review the helpful tips at the bottom of this document to ensure best practices.
- [ ] Verify that commit messages follow the Commit Message Conventions section below.

Runnable pre-PR checklist script (copyable):

```bash
# lint & format
ruff format .
ruff check --unsafe-fixes .
# run type checks
mypy .
# run unit tests
pytest -m unit
# run e2e tests
pytest -m e2e
# optional docs build when docs changed
sphinx-build -b html docs docs/_build/html
```

## Code Style and Quality

### Linting and Formatting

- **Ruff**: Primary linter and formatter (replaces Black, isort, flake8)

  ```bash
  # run check for lint errors
  ruff check --unsafe-fixes .

  # apply lint fixes
  ruff check --unsafe-fixes --fix .

  # check for formatting issues
  ruff format --check .

  # apply formatting fixes
  ruff format .
  ```

- **Type Checking**: Use mypy for type checking

  ```bash
  mypy .
  ```

### Code Style Guidelines

1. **Type Hints**: All functions must have complete type hints (enforced by mypy)

2. **Docstrings**: Use sphinx-style docstrings (though currently many are missing - add
   only when modifying a function or adding new code)

3. **Line Length**: 88 characters (enforced by Ruff)

4. **Import Style**:

   - Absolute imports only (no relative imports)
   - All files must use `from __future__ import annotations` for ignoring type hints at runtime
   - Prefer `from module import Class` over `import module` when using classes/functions
   - Running Ruff with `--unsafe-fixes` and `--fix` will automatically sort and group imports
   - All files should have a `if TYPE_CHECKING:  # pragma: no cover` block for type-only imports
   - Prefer renaming `re` imports for clarity (e.g. `from re import compile as regexp, escape as regexp_escape`)

5. **String Quotes**: Use double quotes for strings

6. **Error Handling**: Create specific exception classes inheriting from `SemanticReleaseBaseError`
   and defined in `errors.py`

### Common Patterns

- Configuration uses Pydantic models (v2) for validation
- CLI uses Click framework with click-option-group for organization
- Git operations use GitPython library
- Templating uses Jinja2 for changelogs and release notes

## Testing

### Test Structure

- **Unit Tests**: `tests/unit/` - Fast, isolated tests

- **E2E Tests**: `tests/e2e/` - End-to-end integration tests performed on real git repos
  (as little mocking as possible, external network calls to HVCS should be mocked). Repos are
  cached into `.pytest_cache/` for faster test setup/runs after the first build. E2E tests are
  built to exercise the CLI commands and options against real git repositories with various commit
  histories and configurations.

- **Fixtures**: `tests/fixtures/` - Reusable test data and fixtures

- **Repository Fixtures**: `tests/fixtures/repos/` - Example git repositories for testing and rely on
  `tests/fixtures/example_project.py` and `tests/fixtures/git_repo.py` for setup

- **Monorepo Fixtures**: `tests/fixtures/monorepo/` - Example monorepos for testing monorepo support

- **GitHub Action Tests**: `tests/gh_action/` - Tests for simulating GitHub Docker Action functionality

### Running Tests

```bash
# Run only unit tests
pytest -m unit

# Run only e2e tests
pytest -m e2e

# Run comprehensive (unit & e2e) test suite with full verbosity (all variations of repositories)
# Warning: long runtime (14mins+) only necessary for testing all git repository variations
pytest -vv --comprehensive

# Run GitHub Docker Action tests (requires Docker, see .github/workflows/validate.yml for setup)
# Only required when modifying the GitHub Action code (src/gh_action/, and action.yml)
bash tests/gh_action/run.sh
```

### Testing Guidelines

1.  **Test Organization**:

    - Group unit tests by module structure mirroring `src/` under `tests/unit/`
    - Group e2e tests by CLI command under `tests/e2e/`
    - Use descriptive test function names that clearly indicate the scenario being tested
    - Test docstrings should follow the format: `"""Given <context>, when <action>, then <expected outcome>."""`

2.  **Fixtures**: Use pytest fixtures from `tests/conftest.py` and `tests/fixtures/`

3.  **Markers**: Apply appropriate markers (`@pytest.mark.unit`, `@pytest.mark.e2e`, `@pytest.mark.comprehensive`)

4.  **Mocking**: Use `pytest-mock` for mocking, `responses` for HTTP mocking

5.  **Parametrization**: Use `@pytest.mark.parametrize` for testing multiple scenarios

6.  **Test Data**: Use `tests/fixtures/repos/` for specific git repository workflow strategies

    - Git repository strategies include:

      - Git Flow:
        - branch & merge commit strategy
        - varying number of branches & release branches

      - GitHub Flow:
        - squash merge strategy
        - branch & merge commit strategy
        - varying number of release branches & simulated simultaneous work branches
        - varying branch update strategies (e.g. rebasing, merging)

      - Trunk-Based Development (no branches):
        - unreleased repo (no tags)
        - trunk with only official release tags
        - trunk with mixed release and pre-release tags
        - concurrent major version support

      - ReleaseFlow (Not supported yet)

      - Monorepo (multiple packages):
        - trunk based development with only official release tags
        - github flow with squash merge strategy
        - github flow with branch & merge commit strategy

### Test Coverage

- Maintain high test coverage for core functionality
- Unit tests should be fast and not touch filesystem/network when possible
- E2E tests should test realistic workflows with actual git operations

### Pull Request testing

Each PR will be evaluated through an GitHub Actions workflow before it can be merged.
The workflow is very specialized to run the tests in a specific order and with specific
parameters. Please refer to `.github/workflows/ci.yml` for details on how the tests are
structured and run.

## Commit Message Conventions

This project uses **Conventional Commits** specification and is versioned by itself. See
the `CHANGELOG.rst` for reference of how the conventional commits and specific rules this
project uses are used in practice to communicate changes to users.

It is highly important to separate the code changes into their respective commit types
and scopes to ensure that the changelog is generated correctly and that users can
understand the changes in each release. The commit message format is strictly enforced
and should be followed for all commits.

When submitting a pull request, it is recommended to commit any end-2-end test cases
first as a `test` type commit, then the implementation changes as `feat`, `fix`, etc.
This order allows reviewers to run the test which demonstrates the failure case before
validating the implementation changes by doing a `git merge origin/<branch>` to run the
test again and see it pass. Unit test cases will need to be committed after the source
code implementation changes as they will not run without the implementation code.
Documentation changes should be committed last and the commit scope should be a short
reference to the page its modifying (e.g. `docs(github-actions): <description>` or
`docs(configuration): <description>`). Commit types should be chosen based on reference
to the default branch as opposed to its previous commits on the branch. For example, if
you are fixing a bug in a feature that was added in the same branch, the commit type
should be `refactor` instead of `fix` since the bug was introduced in the same branch
and is not present in the default branch.

### Format

```
<type>(<scope>): <summary>

<body - short code level description focusing on what and why, not how>

[optional footer(s)]
```

Scopes by the specification are optional but for this project, they are required and
only by exception can they be omitted.

Footers include:

- `BREAKING CHANGE: <description>` for breaking changes

- `NOTICE: <description>` for additional release information that should be included
  in the changelog to give users more context about the release

- `Resolves: #<issue_num>` for linking to bug fixes. Use `Implements: #<issue_num>`
   for new features.

You should not have a breaking change and a notice in the same commit. If you have a
breaking change, the breaking change description should include all relevant information
about the change and how to update.

### Types

- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `perf`: Performance improvement (patch version bump)
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without feature changes or bug fixes
- `test`: Adding or updating tests
- `build`: Changes to build system or dependencies
- `ci`: Changes to CI configuration
- `chore`: Other changes that don't modify src or test files

### Breaking Changes

- Add `!` after the scope: `feat(scope)!: breaking change` and add
  `BREAKING CHANGE:` in footer with detailed description of what was changed,
  why, and how to update.

### Notices

- Add `NOTICE: <description>` in footer to include important information about the
  release that should be included in the changelog. This is for things that require
  more explanation than a simple commit message and are not breaking changes.

### Scopes

Use scopes as categories to indicate the area of change. They are most important for the
types of changes that are included in the changelog (bug fixes, features, performance
improvements, documentation, build dependencies) to tell the user what area was changed.

Common scopes include:

- `changelog`: Changes related to changelog generation
- `config`: Changes related to user configuration
- `fixtures`: Changes related to test fixtures
- `deps`: Changes related to runtime dependencies
- `deps-dev`: Changes related to development dependencies
  (as defined in `pyproject.toml:project.optional-dependencies.dev`)
- `deps-build`: Changes related to build dependencies
  (as defined in `pyproject.toml:project.optional-dependencies.build`)
- `deps-docs`: Changes related to documentation dependencies
  (as defined in `pyproject.toml:project.optional-dependencies.docs`)
- `deps-test`: Changes related to testing dependencies
  (as defined in `pyproject.toml:project.optional-dependencies.test`)

We use hyphenated scopes to group related changes together in a category to subcategory
format. The most common categories are:

- `cmd-<command>`: Changes related to a specific CLI command
- `parser-<parser>`: Changes related to a specific commit parser
- `hvcs-<service>`: Changes related to a specific hosting service integration

## Architecture

The project's primary entrypoint is `src/semantic_release/__main__.py:main`, as defined
in `pyproject.toml:project.scripts`. This is the CLI interface that users interact with.
The CLI is built using Click and lazy-loaded subcommands for version management,
changelog generation, and publishing.

Although the project is primarily a CLI tool, the code is under development to become
more modular and pluggable to allow for more flexible usage in other contexts (e.g. as a
library).

This repository also is provided as a GitHub Action (see `src/gh_action/`) for users
who want a pre-built solution for their GitHub repositories. The action is built using Docker
and wraps the built wheel of the project before it runs the CLI version command in a
containerized environment. The publish command is also available as a GitHub Action but
that code is hosted in a separate repository (https://github.com/python-semantic-release/publish-action).

### Key Components

- `src/semantic_release/cli/`: Click-based CLI interface
  - `commands/`: Individual CLI commands (version, changelog, publish)
  - `config.py`: Configuration loading and validation with Pydantic

- `src/semantic_release/commit_parser/`: Commit message parsers
  - `_base.py`: Base parser interface
  - `conventional/parser.py`: Conventional Commits parser
  - `conventional/options.py`: Conventional Commits parser options
  - `conventional/parser_monorepo.py`: Conventional Commits parser for monorepos
  - `conventional/options_monorepo.py`: Conventional Commits monorepo parser options
  - `angular.py`, `emoji.py`, `scipy.py`, `tag.py`: Parser implementations

- `src/semantic_release/hvcs/`: Hosting service integrations
  - `_base.py`: Base HVCS interface
  - `remote_hvcs_base.py`: Base class for remote HVCS implementations
  - `github.py`, `gitlab.py`, `gitea.py`, `bitbucket.py`: Service implementations

- `src/semantic_release/version/`: Version management
  - `version.py`: Version class and comparison logic
  - `declarations/`: Implementations of how to stamp versions into various types of code
    from users' configuration
  - `translator.py`: Version translation between different formats

- `src/gh_action/`: GitHub Docker Action implementation
  - `action.sh`: Main entrypoint for the action
  - `Dockerfile`: Dockerfile for the action

- `action.yml`: GitHub Action definition

### Design Patterns

- **Strategy Pattern**: Commit parsers and HVCS implementations are pluggable
- **Template Method**: Base classes define workflow, subclasses implement specifics
- **Builder Pattern**: Version calculation builds up changes from commits
- **Factory Pattern**: Parser and HVCS selection based on configuration
- **Composition Pattern**: The future of the project's design for pluggable components

## Building and Releasing

### Local Build

```bash
pip install -e .[build]
bash scripts/build.sh
```

### Release Process

This project is released via GitHub Actions (see `.github/workflows/cicd.yml`) after
a successful validation workflow. During release, it runs a previous version of
itself to perform the release steps. The release process includes:

1. Commits are analyzed from the last tag that exists on the current branch
2. Version is determined based on commit types
3. Changelog is generated from commits
4. Source code is stamped with new version
5. Documentation is stamped with the new version (`$NEW_VERSION`)
   or new release tag (`$NEW_RELEASE_TAG`) (see `scripts/bump_version_in_docs.py` for details)
6. Package is built with stamped version
7. Code changes from steps 4-6 are committed and pushed to the repository
8. A new tag is created for the release and pushed to the repository
9. A new release is created on the hosting service with version-specific generated release notes
10. Assets are uploaded to the release
11. The package is published to PyPI
12. ReadTheDocs is triggered to build & publish the documentation

### Version Configuration

- Version stored in `pyproject.toml:project.version`
- Additional version locations in `tool.semantic_release.version_variables`
- Follows semantic versioning: MAJOR.MINOR.PATCH

## Common Tasks

### Adding a New Commit Parser

1. Create new parser in `src/semantic_release/commit_parser/`
2. Inherit from `CommitParser` base class
3. Implement `parse()` method
4. Add parser to `KNOWN_COMMIT_PARSERS` in config
5. Add tests in `tests/unit/semantic_release/commit_parser/`
6. Add fixtures that can select the new parser for e2e tests

### Adding a New HVCS Integration

1. Create new HVCS in `src/semantic_release/hvcs/`
2. Inherit from `HvcsBase` base class or `RemoteHvcsBase` if it is a remote service
3. Implement required methods (token creation, asset upload, release creation)
4. Add HVCS to configuration options
5. Add tests in `tests/unit/semantic_release/hvcs/`
6. Add fixtures that can select the new HVCS for e2e tests

### Adding a New CLI Command

1. Create command in `src/semantic_release/cli/commands/`
2. Use Click decorators for arguments/options
3. Access shared context via `ctx.obj` (RuntimeContext)
4. Add command to main command group in `src/semantic_release/cli/commands/main.py`
5. Add tests in `tests/e2e/cmd_<command>/`
6. Add documentation for the command in `docs/api/commands.rst`

### Modifying the included default changelog templates source

1.  Update the default templates in `src/semantic_release/data/templates/<parser_type>/<format_type>/`
2.  Update the fixtures in `tests/fixtures/git_repo.py` to correctly replicate the
    format of the new templates via code.
3.  Update the unit tests for changelog generation

### Adding a new configuration option

1.  Update the Pydantic models in `cli/config.py` with validation
2.  Add option over into the RuntimeContext if necessary
3.  Add option description to documentation in
    `docs/configuration/configuration.rst`
4.  Add unit tests for the validation of the option in `tests/unit/semantic_release/cli/config.py`
5.  Add e2e tests for the option in `tests/e2e/` depending on the option's scope
    and functionality.

### Adding a new command line option

1.  Add the option to the appropriate CLI command in
    `src/semantic_release/cli/commands/`
2.  Add the option to the GitHub Action if it is for the `version` command
3.  Add the option to the documentation in `docs/api/commands.rst`
4.  Add the option to the GitHub Action documentation in
    `docs/configuration/automatic-releases/github-actions.rst`
5.  Add e2e tests for the option in `tests/e2e/cmd_<command>/`

### Adding a new changelog context filter

1.  Implement the filter in `src/semantic_release/changelog/context.py`
2.  Add the filter to the changelog context and release notes context objects
3.  Add unit tests for the filter in `tests/unit/semantic_release/changelog/**`
4.  Add description and example of how to use the filter in the documentation
    in `docs/concepts/changelog_templates.rst`

## Important Files

- `pyproject.toml`: Project configuration, dependencies, tool settings
- `action.yml`: GitHub Action definition
- `config/release-templates/`: Project-specific Jinja2 templates for changelog and release notes
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `.readthedocs.yml`: ReadTheDocs configuration
- `CONTRIBUTING.rst`: Contribution guidelines

## Documentation

- Hosted on ReadTheDocs: https://python-semantic-release.readthedocs.io
- Source in `docs/` directory
- Uses Sphinx with Furo theme
- Build locally: `sphinx-build -b html docs docs/_build/html`
- View locally: open `docs/_build/html/index.html`

## Python Version Support

- Runtime Minimum: Python 3.8
- Development Dependencies: Python 3.9+
- Tested on: Python 3.8, 3.14
- Target version for type checking: Python 3.8

## Dependencies to Know

- **Click**: CLI framework
- **GitPython**: Git operations
- **Pydantic v2**: Configuration validation and models
- **Jinja2**: Template engine for changelogs
- **requests**: HTTP client for HVCS APIs
- **python-gitlab**: GitLab API client
- **tomlkit**: TOML parsing with formatting preservation
- **rich**: Rich terminal output

## Helpful Tips

- Never add real secrets, tokens, or credentials to source, commits, fixtures, or logs.

- All proposed changes must include tests (unit and/or e2e as appropriate) and pass the
  local quality gate before creating a PR.

- When modifying configuration, update the Pydantic models in `cli/config.py`

- Jinja2 changelog templates for this project are in `config/release-templates/`, whereas
  the default changelog templates provided to users as a part of this project are in
  `src/semantic_release/data/templates/<parser_type>/<format_type>/**`.

- The `RuntimeContext` object holds shared state across CLI commands

- Use `--noop` flag to test commands without making changes

- Version detection respects git tags - use annotated tags

- The project uses its own tool for versioning, so commit messages matter!

- When creating a Pull Request, create a PR description that fills out the
  PR template found in `.github/PULL_REQUEST_TEMPLATE.md`. This will help
  reviewers understand the changes and the impact of the PR.

- If creating an issue, fill out one of the issue templates found in
  `.github/ISSUE_TEMPLATE/` related to the type of issue (bug, feature request, etc.).
  This will help maintainers understand the issue and its impact.

- When adding new features, consider how they will affect the changelog and
  versioning. Make as few breaking changes as possible by adding backwards compatibility
  and if you do make a breaking change, be sure to include a detailed description in the
  `BREAKING CHANGE` footer of the commit message.
