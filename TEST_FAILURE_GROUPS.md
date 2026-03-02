# Test Failure Groups & Fix Guide

**Total failures: 425** across 4 distinct root-cause groups. Fix them in the priority order listed below; each group is fully independent of the others.

---

## Summary Table

| Group | Root Cause | Failure Count | Failure Numbers | Priority |
|-------|-----------|:---:|---|:---:|
| [A](#group-a--missing-worker_id-fixture-pytest-xdist-not-installed) | `worker_id` fixture not found — `pytest-xdist` not active | 27 | #1, #81–#104, #424, #425 | 1 |
| [B](#group-b--default-release-notes-template-appends-unexpected-pypi-registry-section) | Default release notes template appends unexpected PyPi Registry block | 79 | #2–#80 | 3 |
| [C](#group-c--commit-parsers-match-issue-references-without-required-colon-separator) | Parsers match issue refs in commit body without requiring `:` after keyword | 317 | #105–#350, #353–#423 | 2 |
| [D](#group-d--windows-resource-exhaustion-winerror-1450--1455-in-scipy-parser) | Windows resource exhaustion (`WinError 1450/1455`) spawning git subprocess | 2 | #351, #352 | 4 |

---

## Group A — Missing `worker_id` Fixture (pytest-xdist Not Installed)

### Root Cause

`tests/conftest.py` line 313 declares `get_authorization_to_build_repo_cache` with `worker_id` as a required parameter. `worker_id` is injected by `pytest-xdist` when running with `-n`. When tests are run without `-n` (or without xdist installed), pytest cannot find the `worker_id` fixture and every test that transitively depends on any repo-building fixture fails during setup.

The fixture dependency chain is:
```
worker_id  <-- injected by pytest-xdist only
  └─ get_authorization_to_build_repo_cache  (conftest.py:313)
       └─ build_repo_or_copy_cache  (conftest.py:364)
            └─ cached_example_git_project / build_configured_base_repo / build_repo_from_definition
                 └─ every repo fixture → every test that needs a git repo
```

### Affected Files

- [tests/conftest.py](tests/conftest.py) — lines 313–335 (the `get_authorization_to_build_repo_cache` fixture)

### Fix

Add a fallback `worker_id` fixture to `tests/conftest.py` so the test suite works when run without `pytest-xdist`. Insert this near the top of `conftest.py` (before the `get_authorization_to_build_repo_cache` fixture, around line 308):

```python
# Fallback for when pytest-xdist is not active (single-process runs)
@pytest.fixture(scope="session")
def worker_id() -> str:
    return "master"
```

> **Note:** pytest-xdist overrides this fixture with its own when `-n` is passed, so this stub will not interfere with parallel runs.

### Failing Tests (27)

```
test_changelog_context_read_file                                                       (#1)
test_recursive_render                                                                  (#81)
test_recursive_render_with_top_level_dotfolder                                         (#82)
test_commit_author_configurable[mock_env0-semantic-release <semantic-release>]         (#83)
test_commit_author_configurable[mock_env1-foo <foo>]                                   (#84)
test_load_valid_runtime_config                                                         (#85)
test_load_valid_runtime_config_w_custom_parser[tests.util:CustomParserWithNoOpts]      (#86)
test_load_valid_runtime_config_w_custom_parser[tests.util:CustomParserWithOpts]        (#87)
test_load_valid_runtime_config_w_custom_parser[tests/util.py:CustomParserWithNoOpts]   (#88)
test_load_valid_runtime_config_w_custom_parser[tests/util.py:CustomParserWithOpts]     (#89)
test_load_invalid_custom_parser[tests.missing_module:CustomParser]                     (#90)
test_load_invalid_custom_parser[tests.util:MissingCustomParser]                        (#91)
test_load_invalid_custom_parser[tests.util:IncompleteCustomParser]                     (#92)
test_load_invalid_custom_parser[tests/missing_module.py:CustomParser]                  (#93)
test_load_invalid_custom_parser[tests/util.py:MissingCustomParser]                     (#94)
test_load_invalid_custom_parser[tests/util.py:IncompleteCustomParser]                  (#95)
test_git_remote_url_w_insteadof_alias[bitbucket]                                       (#96)
test_git_remote_url_w_insteadof_alias[github]                                          (#97)
test_git_remote_url_w_insteadof_alias[gitlab]                                          (#98)
test_git_remote_url_w_insteadof_alias[gitea]                                           (#99)
test_version_github_actions_output_format[1.2.2-1.2.3-True-False]                     (#100)
test_version_github_actions_output_format[1.2.2-1.2.3-alpha.1-True-True]              (#101)
test_version_github_actions_output_format[1.2.2-1.2.2-False-False]                    (#102)
test_version_github_actions_output_format[1.2.2-alpha.1-1.2.2-alpha.1-False-True]     (#103)
test_version_github_actions_output_format[None-1.2.3-True-False]                      (#104)
test_release_history_releases[repo_w_no_tags_conventional_commits]                    (#424)
test_all_matching_repo_tags_are_released[repo_w_no_tags_conventional_commits]         (#425)
```

---

## Group B — Default Release Notes Template Appends Unexpected PyPi Registry Section

### Root Cause

The default release notes Jinja2 template was modified to unconditionally append the following block at the end of every release notes output:

```
---

**Installable artifacts are available from**:

- [PyPi Registry](https://pypi.org/project/<project_name>/<version>)
```

All 79 tests in `tests/unit/semantic_release/changelog/test_release_notes.py` build their `expected_content` string by hand and none of them include this block in the expectation. The actual output from `generate_release_notes()` now contains this extra section, causing every assertion to fail.

The diff always shows the same pattern — the LHS (expected) ends after the `**Detailed Changes**` link or at the last commit entry, while the RHS (actual) continues with the extra `---\n\n**Installable artifacts are available from**:` section.

### Affected Files

- `src/semantic_release/data/templates/` — The default release notes template (likely `angular/md/` or `conventional/md/` subdirectory). Locate the template file that generates the PyPi Registry block and remove it, OR make it conditional on a configuration option.
- **Alternative:** Update all 79 test expected strings in [tests/unit/semantic_release/changelog/test_release_notes.py](tests/unit/semantic_release/changelog/test_release_notes.py) to include the new block (not recommended — indicates the template change was unintentional).

### Fix (recommended: remove the unconditional block from the template)

In the default release notes Jinja2 template, find and remove (or conditionalize with a template variable) the section that renders:
```
---

**Installable artifacts are available from**:

- [PyPi Registry](https://pypi.org/project/...)
```

If this feature is intentional, a new configuration option should gate it (e.g., `include_pypi_link: bool = False`) and the 79 tests should have that option set to `False` (or left at its default) so the expected strings remain valid.

### Failing Tests (79)

All from `tests/unit/semantic_release/changelog/test_release_notes.py`:

```
# Parametrized over hvcs_client=[Github, Gitlab, Gitea, Bitbucket], license_name=["", "MIT"], mask_initial_release=[True, False]
test_default_release_notes_template[Github--True]                                       (#2)
test_default_release_notes_template[Github--False]                                      (#3)
test_default_release_notes_template[Github-MIT-True]                                    (#4)
test_default_release_notes_template[Github-MIT-False]                                   (#5)
test_default_release_notes_template[Gitlab--True]                                       (#6)
test_default_release_notes_template[Gitlab--False]                                      (#7)
test_default_release_notes_template[Gitlab-MIT-True]                                    (#8)
test_default_release_notes_template[Gitlab-MIT-False]                                   (#9)
test_default_release_notes_template[Gitea--True]                                        (#10)
test_default_release_notes_template[Gitea--False]                                       (#11)
test_default_release_notes_template[Gitea-MIT-True]                                     (#12)
test_default_release_notes_template[Gitea-MIT-False]                                    (#13)
test_default_release_notes_template[Bitbucket--True]                                    (#14)
test_default_release_notes_template[Bitbucket--False]                                   (#15)
test_default_release_notes_template[Bitbucket-MIT-True]                                 (#16)
test_default_release_notes_template[Bitbucket-MIT-False]                                (#17)

# Parametrized over hvcs_client=[Github, Gitlab, Gitea, Bitbucket], mask_initial_release=[True, False]
test_default_release_notes_template_w_a_brk_description[Github-True]                   (#18)
test_default_release_notes_template_w_a_brk_description[Github-False]                  (#19)
test_default_release_notes_template_w_a_brk_description[Gitlab-True]                   (#20)
test_default_release_notes_template_w_a_brk_description[Gitlab-False]                  (#21)
test_default_release_notes_template_w_a_brk_description[Gitea-True]                    (#22)
test_default_release_notes_template_w_a_brk_description[Gitea-False]                   (#23)
test_default_release_notes_template_w_a_brk_description[Bitbucket-True]                (#24)
test_default_release_notes_template_w_a_brk_description[Bitbucket-False]               (#25)

test_default_release_notes_template_w_multiple_brk_changes[Github-True]                (#26)
test_default_release_notes_template_w_multiple_brk_changes[Github-False]               (#27)
test_default_release_notes_template_w_multiple_brk_changes[Gitlab-True]                (#28)
test_default_release_notes_template_w_multiple_brk_changes[Gitlab-False]               (#29)
test_default_release_notes_template_w_multiple_brk_changes[Gitea-True]                 (#30)
test_default_release_notes_template_w_multiple_brk_changes[Gitea-False]                (#31)
test_default_release_notes_template_w_multiple_brk_changes[Bitbucket-True]             (#32)
test_default_release_notes_template_w_multiple_brk_changes[Bitbucket-False]            (#33)

# Parametrized over hvcs_client=[Github, Gitlab, Gitea, Bitbucket], license_name=["", "MIT"]
test_default_release_notes_template_first_release_masked[Github-]                      (#34)
test_default_release_notes_template_first_release_masked[Github-MIT]                   (#35)
test_default_release_notes_template_first_release_masked[Gitlab-]                      (#36)
test_default_release_notes_template_first_release_masked[Gitlab-MIT]                   (#37)
test_default_release_notes_template_first_release_masked[Gitea-]                       (#38)
test_default_release_notes_template_first_release_masked[Gitea-MIT]                    (#39)
test_default_release_notes_template_first_release_masked[Bitbucket-]                   (#40)
test_default_release_notes_template_first_release_masked[Bitbucket-MIT]                (#41)

test_default_release_notes_template_first_release_unmasked[Github-]                    (#42)
test_default_release_notes_template_first_release_unmasked[Github-MIT]                 (#43)
test_default_release_notes_template_first_release_unmasked[Gitlab-]                    (#44)
test_default_release_notes_template_first_release_unmasked[Gitlab-MIT]                 (#45)
test_default_release_notes_template_first_release_unmasked[Gitea-]                     (#46)
test_default_release_notes_template_first_release_unmasked[Gitea-MIT]                  (#47)
test_default_release_notes_template_first_release_unmasked[Bitbucket-]                 (#48)
test_default_release_notes_template_first_release_unmasked[Bitbucket-MIT]              (#49)

test_release_notes_context_release_url_filter[Github]                                  (#50)
test_release_notes_context_release_url_filter[Gitlab]                                  (#51)
test_release_notes_context_release_url_filter[Gitea]                                   (#52)

test_release_notes_context_format_w_official_name_filter[Github]                       (#53)
test_release_notes_context_format_w_official_name_filter[Gitlab]                       (#54)
test_release_notes_context_format_w_official_name_filter[Gitea]                        (#55)
test_release_notes_context_format_w_official_name_filter[Bitbucket]                    (#56)

test_default_release_notes_template_w_a_notice[Github-True]                            (#57)
test_default_release_notes_template_w_a_notice[Github-False]                           (#58)
test_default_release_notes_template_w_a_notice[Gitlab-True]                            (#59)
test_default_release_notes_template_w_a_notice[Gitlab-False]                           (#60)
test_default_release_notes_template_w_a_notice[Gitea-True]                             (#61)
test_default_release_notes_template_w_a_notice[Gitea-False]                            (#62)
test_default_release_notes_template_w_a_notice[Bitbucket-True]                         (#63)
test_default_release_notes_template_w_a_notice[Bitbucket-False]                        (#64)

test_default_release_notes_template_w_a_notice_n_brk_change[Github-True]               (#65)
test_default_release_notes_template_w_a_notice_n_brk_change[Github-False]              (#66)
test_default_release_notes_template_w_a_notice_n_brk_change[Gitlab-True]               (#67)
test_default_release_notes_template_w_a_notice_n_brk_change[Gitlab-False]              (#68)
test_default_release_notes_template_w_a_notice_n_brk_change[Gitea-True]                (#69)
test_default_release_notes_template_w_a_notice_n_brk_change[Gitea-False]               (#70)
test_default_release_notes_template_w_a_notice_n_brk_change[Bitbucket-True]            (#71)
test_default_release_notes_template_w_a_notice_n_brk_change[Bitbucket-False]           (#72)

test_default_release_notes_template_w_multiple_notices[Github-True]                    (#73)
test_default_release_notes_template_w_multiple_notices[Github-False]                   (#74)
test_default_release_notes_template_w_multiple_notices[Gitlab-True]                    (#75)
test_default_release_notes_template_w_multiple_notices[Gitlab-False]                   (#76)
test_default_release_notes_template_w_multiple_notices[Gitea-True]                     (#77)
test_default_release_notes_template_w_multiple_notices[Gitea-False]                    (#78)
test_default_release_notes_template_w_multiple_notices[Bitbucket-True]                 (#79)
test_default_release_notes_template_w_multiple_notices[Bitbucket-False]                (#80)
```

---

## Group C — Commit Parsers Match Issue References Without Required Colon Separator

### Root Cause

Both `ConventionalCommitParser` and `ScipyCommitParser` are matching commit issue references that appear **without** a colon after the closure keyword. Git footer syntax requires `{keyword}: {value}` (colon mandatory). Patterns like `Close #666` (space only, no colon) should not be recognized as an issue-closing footer and should return `[]`, but both parsers currently return `('#666',)`.

The tests document exactly which patterns are valid git footers (with `:`) and which are not (without `:`):

```
# These SHOULD match (colon present — valid git footer):
"Close: #666"    → expected: ['#666']   ✓ (passes)
"close: #666"    → expected: ['#666']   ✓ (passes)
"CLOSE: #666"    → expected: ['#666']   ✓ (passes)

# These should NOT match (no colon — not a valid git footer):
"Close #666"     → expected: []         ✗ (actually returns ('#666',))
"Close #666, #777"  → expected: []      ✗ (actually returns multiple issues)
"Close #666, Close #777"  → expected: [] ✗ (actually returns multiple issues)
```

The same pattern applies to all 16 supported closure prefixes (`close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`, `implement`, `implements`, `implemented`, `address`, `addresses`, `addressed`) and both GitHub-style (`#NNN`) and JIRA-style (`ABC-NNN`) issue reference formats.

### Error Example

```
assert == failed.
LHS: ()          ← expected (no match, no colon)
RHS: ('#666', )  ← actual (parser incorrectly matched it)
```

### Affected Files

- [src/semantic_release/commit_parser/conventional/parser.py](src/semantic_release/commit_parser/conventional/parser.py) — The linked-issue extraction section must require `:` after the closure keyword
- [src/semantic_release/commit_parser/scipy.py](src/semantic_release/commit_parser/scipy.py) — Same fix needed

### Fix

In both parser files, locate the regex that matches linked issues in the commit footer and enforce the colon separator. The pattern currently likely looks something like:

```python
# Current (too permissive — matches with or without colon):
r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|implement(?:ed|s)?|addresse[sd]?)\s+(\#\w+)"

# Required fix (must require colon after keyword):
r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|implement(?:ed|s)?|addresse[sd]?):\s+(\#\w+)"
```

The key change: add `:` (colon) as a required character between the closure keyword and the issue reference. This ensures only valid git footer format lines (`Keyword: #NNN`) are recognized.

### Failing Tests (317)

All from `tests/unit/semantic_release/commit_parser/test_conventional.py` (failures #105–#350) and `tests/unit/semantic_release/commit_parser/test_scipy.py` (failures #353–#423).

The test function name for both is:
```
test_parser_return_linked_issues_from_commit_message[<commit_message>-linked_issuesN]
```

**Pattern for identifying failing cases:** Any parametrize entry where:
- The footer line does NOT contain a `:` immediately after the closure keyword
- i.e., entries matching the 3-pattern group per prefix: `{prefix} #NNN`, `{prefix} #NNN, #MMM`, `{prefix} #NNN, {prefix} #MMM`

This applies to all 16 closure prefixes × 3 invalid patterns × 2 issue styles (GitHub `#NNN` + JIRA `ABC-NNN`) = **96 invalid cases per parser × 2 parsers = 192 parametrized test instances**, plus additional combinations from the scipy test.

**Sample failing test IDs (Conventional parser — failures #105–#350):**
```
# For each of the 16 prefixes and both issue styles, these 3 patterns fail:
test_parser_return_linked_issues_from_commit_message[feat(parser): add magic parser\n\nClose #666-linked_issues25]
test_parser_return_linked_issues_from_commit_message[feat(parser): add magic parser\n\nClose #666, #777-linked_issues26]
test_parser_return_linked_issues_from_commit_message[feat(parser): add magic parser\n\nClose #666, Close #777-linked_issues27]
# ... repeating for closes, closed, fix, fixes, fixed, resolve, resolves, resolved,
#     implement, implements, implemented, address, addresses, addressed
# ... and again for JIRA-style (ABC-NNN) references
```

**Sample failing test IDs (Scipy parser — failures #353–#423):**
```
# Same pattern but with scipy-formatted commit messages:
test_parser_return_linked_issues_from_commit_message[ENH: add magic parser\n\nClose #666-linked_issuesN]
test_parser_return_linked_issues_from_commit_message[ENH: add magic parser\n\nClose #666, #777-linked_issuesN]
test_parser_return_linked_issues_from_commit_message[ENH: add magic parser\n\nClose #666, Close #777-linked_issuesN]
# ... for all 16 prefixes and both issue styles
```

---

## Group D — Windows Resource Exhaustion (WinError 1450 / 1455) in Scipy Parser

### Root Cause

After several hundred earlier tests have run and spawned git repositories and subprocesses, Windows runs out of system handles or virtual memory (pagefile). When `ScipyCommitParser.parse()` calls `unsquash_commit()` which in turn calls `deep_copy_commit()` in `src/semantic_release/commit_parser/util.py`, a `git cat-file --batch` subprocess is spawned via GitPython. At that point in the test run, the OS can no longer allocate the subprocess and raises:

```
git.exc.GitCommandNotFound: Cmd('git') not found due to:
OSError('[WinError 1450] Insufficient system resources exist to complete the requested service')
```
or:
```
OSError('[WinError 1455] The paging file is too small for this operation to complete')
```

**Note:** These are the only 2 failures caused by environment resource exhaustion, not a code logic bug. The test cases themselves are valid (they use correct colon-separated footer syntax and should return matched issues).

### Affected Files

- [src/semantic_release/commit_parser/scipy.py](src/semantic_release/commit_parser/scipy.py) — `unsquash_commit()` (around line 401) calls `deep_copy_commit()`
- [src/semantic_release/commit_parser/util.py](src/semantic_release/commit_parser/util.py) — `deep_copy_commit()` (around line 121) spawns `git cat-file --batch`

### Fix Options

**Short-term (environment fix — no code changes):**
1. Increase Windows pagefile size to at least 8 GB
2. Run tests in smaller batches: `pytest -k "scipy" tests/unit/semantic_release/commit_parser/test_scipy.py` in isolation
3. Run with `pytest-xdist`: `pytest -n auto` so tests are distributed across fresh worker processes (also fixes Group A)

**Long-term (code fix — preferred):**
Investigate whether `deep_copy_commit()` needs to spawn `git cat-file --batch` at all for the data required by `unsquash_commit()`. If the commit data (author, message, parents, etc.) is already loaded in the `git.Commit` object's memory, refactor `deep_copy_commit()` to avoid calling `getattr(commit, key)` for attributes that trigger gitdb lazy-loading, or mock those lazy-loaded attributes during tests.

Alternatively, add proper cleanup of GitPython `Git` command objects between test cases to release OS handles earlier.

### Failing Tests (2)

```
test_parser_return_linked_issues_from_commit_message[ENH: add magic parser\n\nImplemented: #555 & #444-linked_issues449]    (#351)
test_parser_return_linked_issues_from_commit_message[ENH: add magic parser\n\nImplemented: #555 and #444-linked_issues450]  (#352)
```

Both are in `tests/unit/semantic_release/commit_parser/test_scipy.py`.

---

## Recommended Fix Order

1. **Group A first** — One-line fix in `tests/conftest.py`. Unblocks 27 tests immediately without touching any source code.
2. **Group C second** — Two-file regex fix that eliminates 317 failures at once. Highest ROI.
3. **Group B third** — Locate and remove (or conditionalize) the PyPi Registry template block; eliminates 79 failures.
4. **Group D last** — Address after Group C reduces overall subprocess spawning from the scipy tests, which may also reduce the resource pressure. Then consider the long-term `deep_copy_commit()` refactor.

---

## Verification Commands

After applying each fix, run only the related tests to confirm:

```bash
# Group A
pytest tests/unit/semantic_release/changelog/test_changelog_context.py::test_changelog_context_read_file
pytest tests/unit/semantic_release/changelog/test_template_render.py
pytest tests/unit/semantic_release/cli/test_config.py
pytest tests/unit/semantic_release/changelog/test_release_history.py

# Group B
pytest tests/unit/semantic_release/changelog/test_release_notes.py

# Group C
pytest tests/unit/semantic_release/commit_parser/test_conventional.py -k "linked_issues"
pytest tests/unit/semantic_release/commit_parser/test_scipy.py -k "linked_issues"

# Group D (run in isolation after Group C fix)
pytest tests/unit/semantic_release/commit_parser/test_scipy.py -k "linked_issues449 or linked_issues450"

# Full unit suite
pytest -m unit
```
