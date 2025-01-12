# CHANGELOG


## v9.16.1 (2025-01-12)

### Bug Fixes

- **parser-custom**: Handle relative parent directory paths to module file better
  ([#1142](https://github.com/python-semantic-release/python-semantic-release/pull/1142),
  [`c4056fc`](https://github.com/python-semantic-release/python-semantic-release/commit/c4056fc2e1fb3bddb78728793716ac6fb8522b1a))

The dynamic import originally would just replace "/" with "." to make the import module name more
  pythonic, however this would be problematic in monorepos which would use
  "../../misc/commit_parser.py" to locate the parser and so the resulting `sys.modules` entry would
  have numerous periods (.) as a prefix. This removes that possibility. Still always an issue if the
  imported module name matches an existing module but the likelihood is low.

### Documentation

- **github-actions**: Update PSR versions in github workflow examples
  ([#1140](https://github.com/python-semantic-release/python-semantic-release/pull/1140),
  [`9bdd626`](https://github.com/python-semantic-release/python-semantic-release/commit/9bdd626bf8f8359d35725cebe803931063260cac))


## v9.16.0 (2025-01-12)

### Bug Fixes

- **changelog**: Fixes PSR release commit exclusions for customized commit messages
  ([#1139](https://github.com/python-semantic-release/python-semantic-release/pull/1139),
  [`f9a2078`](https://github.com/python-semantic-release/python-semantic-release/commit/f9a20787437d0f26074fe2121bf0a29576a96df0))

* fix(config-changelog): validate `changelog.exclude_commit_patterns` on config load

* test(fixtures): relocate sanitize changelog functions

* test(cmd-version): add test to validate that custom release messages are ignored in changelog

* test(config): add `changelog.exclude_commit_patterns` validation check

* style(config): refactor import names of `re` module

- **cmd-version**: Fix `--print-tag` result to match configured tag format
  ([#1134](https://github.com/python-semantic-release/python-semantic-release/pull/1134),
  [`a990aa7`](https://github.com/python-semantic-release/python-semantic-release/commit/a990aa7ab0a9d52d295c04d54d20e9c9f2db2ca5))

* test(fixtures): add new trunk repo that has a different tag format

* test(fixtures): add helper to extract config settings from repo action definition

* test(cmd-version): expand testing of `--print-tag` & `--print-last-released-tag`

PSR did not have enough testing to demonstrate testing of the tag generation when the tag format was
  configured differently than normal. This commit adds a significant portion of testing to exercise
  the print tag functionality which must match the configured tag format.

- **cmd-version**: Fix tag format on default version when force bump for initial release
  ([#1138](https://github.com/python-semantic-release/python-semantic-release/pull/1138),
  [`007fd00`](https://github.com/python-semantic-release/python-semantic-release/commit/007fd00a3945ed211ece4baab0b79ad93dc018f5))

Resolves: #1137

* test(fixtures): add new unreleased trunk repo with a different tag format

* test(cmd-version): ensure forced bump version on initial release follows tag format

ref: #1137

### Features

- **config**: Expand dynamic parser import to handle a filepath to module
  ([#1135](https://github.com/python-semantic-release/python-semantic-release/pull/1135),
  [`0418fd8`](https://github.com/python-semantic-release/python-semantic-release/commit/0418fd8d27aac14925aafa50912e751e3aeff2f7))

* test(fixtures): remove import checking/loading of custom parser in `use_custom_parser`

* test(config): extend import parser unit tests to evaluate file paths to modules

* docs(commit-parsing): add the new custom parser import spec description for direct path imports

Resolves: #687

* docs(configuration): adjust `commit_parser` option definition for direct path imports


## v9.15.2 (2024-12-16)

### Bug Fixes

- **changelog**: Ensures user rendered files are trimmed to end with a single newline
  ([#1118](https://github.com/python-semantic-release/python-semantic-release/pull/1118),
  [`6dfbbb0`](https://github.com/python-semantic-release/python-semantic-release/commit/6dfbbb0371aef6b125cbcbf89b80dc343ed97360))

- **cli**: Add error message of how to gather full error output
  ([#1116](https://github.com/python-semantic-release/python-semantic-release/pull/1116),
  [`ba85532`](https://github.com/python-semantic-release/python-semantic-release/commit/ba85532ddd6fcf1a2205f7ce0b88ea5be76cb621))

- **cmd-version**: Enable maintenance prereleases
  ([#864](https://github.com/python-semantic-release/python-semantic-release/pull/864),
  [`b88108e`](https://github.com/python-semantic-release/python-semantic-release/commit/b88108e189e1894e36ae4fdf8ad8a382b5c8c90a))

* test(fixtures): improve changelog generator to filter by max version

* test(fixtures): add repo fixture of a trunk only repo w/ dual version support

* test(fixtures): add repo fixture of a trunk only repo w/ dual version support & prereleases

* test(cmd-version): add rebuild repo tests for new dual version support repos

* test(version-determination): adjust unit tests of increment_version logic

This clarifies repeated function calls and pytest parameter names included the unclear assert diff.
  Adds additional tests to check bad states for failures and refactored to match new function
  signature.

* fix(version-bump): increment based on current commit's history only

Refactor duplicate logging messages and flow to process out odd cases in a fail fast methodology.
  This removes the reliance on any last full release that is not within the history of the current
  branch.

Resolves: #861

- **cmd-version**: Fix handling of multiple prerelease token variants & git flow merges
  ([#1120](https://github.com/python-semantic-release/python-semantic-release/pull/1120),
  [`8784b9a`](https://github.com/python-semantic-release/python-semantic-release/commit/8784b9ad4bc59384f855b5af8f1b8fb294397595))

* refactor: define a custom logging level of silly

* fix(version): remove some excessive log msgs from debug to silly level

* test(fixtures): refactor builder functions for version file updates

* test(fixtures): adjust build command to handle versions w/ build metadata

* test(fixtures): fix gitflow repo that included an invalid build metadata string

* test(fixtures): fix major_on_zero setting in repos to match expected behavior

* test(cmd-version): add test cases to run an example repo rebuild w/ psr

* test(cmd-version): enable git flow repo rebuild w/ psr test cases

* fix(cmd-version): handle multiple prerelease token variants properly

In the case where there are alpha and beta releases, we must only consider the previous beta release
  even if alpha releases exist due to merging into beta release only branches which have no changes
  considerable changes from alphas but must be marked otherwise.

Resolves: #789

* fix(cmd-version): fix version determination algorithm to capture commits across merged branches

* perf(cmd-version): refactor version determination algorithm for accuracy & speed

* test(algorithm): refactor test to match new function signature

* style(algorithm): drop unused functions & imports

* test(algorithm): adapt test case for new DFS commit traversal implementation

- **cmd-version**: Forces tag timestamp to be same time as release commit
  ([#1117](https://github.com/python-semantic-release/python-semantic-release/pull/1117),
  [`7898b11`](https://github.com/python-semantic-release/python-semantic-release/commit/7898b1185fc1ad10e96bf3f5e48d9473b45d2b51))

- **config**: Ensure default config loads on network mounted windows environments
  ([#1124](https://github.com/python-semantic-release/python-semantic-release/pull/1124),
  [`a64cbc9`](https://github.com/python-semantic-release/python-semantic-release/commit/a64cbc96c110e32f1ec5d1a7b61e950472491b87))

Resolves: #1123

* test(cmd-generate-config): added noop version execution to validate config at runtime

ref: #1123


## v9.15.1 (2024-12-03)

### Bug Fixes

- **changelog-md**: Fix commit sort of breaking descriptions section
  ([`75b342e`](https://github.com/python-semantic-release/python-semantic-release/commit/75b342e6259412cb82d8b7663e5ee4536d14f407))

- **parser-angular**: Ensure issues are sorted by numeric value rather than text sorted
  ([`3858add`](https://github.com/python-semantic-release/python-semantic-release/commit/3858add582fe758dc2ae967d0cd051d43418ecd0))

- **parser-emoji**: Ensure issues are sorted by numeric value rather than text sorted
  ([`7b8d2d9`](https://github.com/python-semantic-release/python-semantic-release/commit/7b8d2d92e135ab46d1be477073ccccc8c576f121))


## v9.15.0 (2024-12-02)

### Bug Fixes

- **cmd-version**: Ensure release utilizes a timezone aware datetime
  ([`ca817ed`](https://github.com/python-semantic-release/python-semantic-release/commit/ca817ed9024cf84b306a047675534cc36dc116b2))

- **default-changelog**: Alphabetically sort commit descriptions in version type sections
  ([`bdaaf5a`](https://github.com/python-semantic-release/python-semantic-release/commit/bdaaf5a460ca77edc40070ee799430122132dc45))

### Features

- **commit-parser**: Enable parsers to flag commit to be ignored for changelog
  ([#1108](https://github.com/python-semantic-release/python-semantic-release/pull/1108),
  [`0cc668c`](https://github.com/python-semantic-release/python-semantic-release/commit/0cc668c36490401dff26bb2c3141f6120a2c47d0))

This adds an attribute to the ParsedCommit object that allows custom parsers to set to false if it
  is desired to ignore the commit completely from entry into the changelog.

Resolves: #778

* test(parser-custom): add test w/ parser that toggles if a parsed commit is included in changelog

- **default-changelog**: Add a separate formatted breaking changes section
  ([#1110](https://github.com/python-semantic-release/python-semantic-release/pull/1110),
  [`4fde30e`](https://github.com/python-semantic-release/python-semantic-release/commit/4fde30e0936ecd186e448f1caf18d9ba377c55ad))

Resolves: #244

* test(fixtures): update repo changelog generator to add breaking descriptions

* test(default-changelog): add unit tests to demonstrate breaking change descriptions

* test(release-notes): add unit tests to demonstrate breaking change descriptions

* feat(changelog-md): add a breaking changes section to default Markdown template

* feat(changelog-rst): add a breaking changes section to default reStructuredText template

* feat(changelog-md): alphabetize breaking change descriptions in markdown changelog template

* feat(changelog-rst): alphabetize breaking change descriptions in ReStructuredText template

- **default-changelog**: Alphabetize commit summaries & scopes in change sections
  ([#1111](https://github.com/python-semantic-release/python-semantic-release/pull/1111),
  [`8327068`](https://github.com/python-semantic-release/python-semantic-release/commit/83270683fd02b626ed32179d94fa1e3c7175d113))

* test(fixtures): force non-alphabetical release history to validate template sorting

* test(default-changelog): update unit test to enforce sorting of commit desc in version sections

* test(release-notes): update unit test to enforce sorting of commit desc in version sections

* feat(changelog-md): alphabetize commit summaries & scopes in markdown changelog template

* feat(changelog-rst): alphabetize commit summaries & scopes in ReStructuredText template

- **parsers**: Enable parsers to identify linked issues on a commit
  ([#1109](https://github.com/python-semantic-release/python-semantic-release/pull/1109),
  [`f90b8dc`](https://github.com/python-semantic-release/python-semantic-release/commit/f90b8dc6ce9f112ef2c98539d155f9de24398301))

* refactor(parsers): add parser option validation to commit parsing

* docs(api-parsers): add option documentation to parser options

* feat(parsers): add `other_allowed_tags` option for commit parser options

* feat(parser-custom): enable custom parsers to identify linked issues on a commit

* test(parser-angular): add unit tests to verify parsing of issue numbers

* test(parser-emoji): add unit tests to verify parsing of issue numbers

* test(parser-scipy): add unit tests to verify parsing of issue numbers

* fix(util): prevent git footers from being collapsed during parse

* feat(parser-angular): automatically parse angular issue footers from commit messages

* feat(parser-emoji): parse issue reference footers from commit messages

* docs(commit-parsing): improve & expand commit parsing w/ parser descriptions

* docs(changelog-templates): update examples using new `commit.linked_issues` attribute

* chore(docs): update documentation configuration for team publishing

- **release-notes**: Add tag comparison link to release notes when supported
  ([#1107](https://github.com/python-semantic-release/python-semantic-release/pull/1107),
  [`9073344`](https://github.com/python-semantic-release/python-semantic-release/commit/9073344164294360843ef5522e7e4c529985984d))

* test(release-notes): adjust test case to include a version compare link

* test(cmd-changelog): add test to ensure multiple variants of release notes are published


## v9.14.0 (2024-11-11)

### Bug Fixes

- **release-notes**: Override default wordwrap to non-wrap for in default template
  ([`99ab99b`](https://github.com/python-semantic-release/python-semantic-release/commit/99ab99bb0ba350ca1913a2bde9696f4242278972))

### Documentation

- **changelog-templates**: Document new `mask_initial_release` changelog context variable
  ([`f294957`](https://github.com/python-semantic-release/python-semantic-release/commit/f2949577dfb2dbf9c2ac952c1bbcc4ab84da080b))

- **configuration**: Document new `mask_initial_release` option usage & effect
  ([`3cabcdc`](https://github.com/python-semantic-release/python-semantic-release/commit/3cabcdcd9473e008604e74cc2d304595317e921d))

- **homepage**: Fix reference to new ci workflow for test status badge
  ([`6760069`](https://github.com/python-semantic-release/python-semantic-release/commit/6760069e7489f50635beb5aedbbeb2cb82b7c584))

### Features

- **changelog**: Add md to rst conversion for markdown inline links
  ([`cb2af1f`](https://github.com/python-semantic-release/python-semantic-release/commit/cb2af1f17cf6c8ae037c6cd8bb8b4d9c019bb47e))

- **changelog**: Define first release w/o change descriptions for default MD template
  ([`fa89dec`](https://github.com/python-semantic-release/python-semantic-release/commit/fa89dec239efbae7544b187f624a998fa9ecc309))

- **changelog**: Define first release w/o change descriptions for default RST template
  ([`e30c94b`](https://github.com/python-semantic-release/python-semantic-release/commit/e30c94bffe62b42e8dc6ed4fed6260e57b4d532b))

- **changelog-md**: Add markdown inline link format macro
  ([`c6d8211`](https://github.com/python-semantic-release/python-semantic-release/commit/c6d8211c859442df17cb41d2ff19fdb7a81cdb76))

- **changelogs**: Prefix scopes on commit descriptions in default template
  ([#1093](https://github.com/python-semantic-release/python-semantic-release/pull/1093),
  [`560fd2c`](https://github.com/python-semantic-release/python-semantic-release/commit/560fd2c0d58c97318377cb83af899a336d24cfcc))

* test(changelog): update default changelog unit tests to handle commit scope

* test(release-notes): update default release notes unit tests to handle commit scope

* test(fixtures): update changelog generator fixture to handle scope additions

* test(cmd-version): update implementation for test resiliency

* feat(changelog-md): prefix scopes on commit descriptions in Markdown changelog template

* feat(changelog-rst): prefix scopes on commit descriptions in ReStructuredText template

- **configuration**: Add `changelog.default_templates.mask_initial_release` option
  ([`595a70b`](https://github.com/python-semantic-release/python-semantic-release/commit/595a70bcbc8fea1f8ccf6c5069c41c35ec4efb8d))

- **context**: Add `mask_initial_release` setting to changelog context
  ([`6f2ee39`](https://github.com/python-semantic-release/python-semantic-release/commit/6f2ee39414b3cf75c0b67dee4db0146bbc1041bb))

- **release-notes**: Define first release w/o change descriptions in default template
  ([`83167a3`](https://github.com/python-semantic-release/python-semantic-release/commit/83167a3dcceb7db16b790e1b0efd5fc75fee8942))


## v9.13.0 (2024-11-10)

### Bug Fixes

- **changelog-rst**: Ignore unknown parsed commit types in default RST changelog
  ([`77609b1`](https://github.com/python-semantic-release/python-semantic-release/commit/77609b1917a00b106ce254e6f6d5edcd1feebba7))

- **parser-angular**: Drop the `breaking` category but still maintain a major level bump
  ([`f1ffa54`](https://github.com/python-semantic-release/python-semantic-release/commit/f1ffa5411892de34cdc842fd55c460a24b6685c6))

- **parsers**: Improve reliability of text unwordwrap of descriptions
  ([`436374b`](https://github.com/python-semantic-release/python-semantic-release/commit/436374b04128d1550467ae97ba90253f1d1b3878))

### Documentation

- **changelog-templates**: Add `linked_merge_request` field to examples
  ([`d4376bc`](https://github.com/python-semantic-release/python-semantic-release/commit/d4376bc2ae4d3708d501d91211ec3ee3a923e9b5))

- **changelog-templates**: Fix api class reference links
  ([`7a5bdf2`](https://github.com/python-semantic-release/python-semantic-release/commit/7a5bdf29b3df0f9a1346ea5301d2a7fee953667b))

- **commit-parsing**: Add `linked_merge_request` field to Parsed Commit definition
  ([`ca61889`](https://github.com/python-semantic-release/python-semantic-release/commit/ca61889d4ac73e9864fbf637fb87ab2d5bc053ea))

### Features

- **changelog**: Add PR/MR url linking to default Markdown changelog
  ([`cd8d131`](https://github.com/python-semantic-release/python-semantic-release/commit/cd8d1310a4000cc79b529fbbdc58933f4c6373c6))

Resolves: #924, #953

- **changelog**: Add PR/MR url linking to default reStructuredText template
  ([`5f018d6`](https://github.com/python-semantic-release/python-semantic-release/commit/5f018d630b4c625bdf6d329b27fd966eba75b017))

Resolves: #924, #953

- **parsed-commit**: Add linked merge requests list to the `ParsedCommit` object
  ([`9a91062`](https://github.com/python-semantic-release/python-semantic-release/commit/9a9106212d6c240e9d3358e139b4c4694eaf9c4b))

- **parser-angular**: Automatically parse PR/MR numbers from subject lines in commits
  ([`2ac798f`](https://github.com/python-semantic-release/python-semantic-release/commit/2ac798f92e0c13c1db668747f7e35a65b99ae7ce))

- **parser-emoji**: Automatically parse PR/MR numbers from subject lines in commits
  ([`bca9909`](https://github.com/python-semantic-release/python-semantic-release/commit/bca9909c1b61fdb1f9ccf823fceb6951cd059820))

- **parser-scipy**: Automatically parse PR/MR numbers from subject lines in commits
  ([`2b3f738`](https://github.com/python-semantic-release/python-semantic-release/commit/2b3f73801f5760bac29acd93db3ffb2bc790cda0))

### Performance Improvements

- **parser-angular**: Simplify commit parsing type pre-calculation
  ([`a86a28c`](https://github.com/python-semantic-release/python-semantic-release/commit/a86a28c5e26ed766cda71d26b9382c392e377c61))

- **parser-emoji**: Increase speed of commit parsing
  ([`2c9c468`](https://github.com/python-semantic-release/python-semantic-release/commit/2c9c4685a66feb35cd78571cf05f76344dd6d66a))

- **parser-scipy**: Increase speed & decrease complexity of commit parsing
  ([`2b661ed`](https://github.com/python-semantic-release/python-semantic-release/commit/2b661ed122a6f0357a6b92233ac1351c54c7794e))


## v9.12.2 (2024-11-07)

### Bug Fixes

- **cli**: Gracefully capture all exceptions unless in very verbose debug mode
  ([#1088](https://github.com/python-semantic-release/python-semantic-release/pull/1088),
  [`13ca44f`](https://github.com/python-semantic-release/python-semantic-release/commit/13ca44f4434098331f70e6937684679cf1b4106a))

* refactor(cli): consolidate entrypoints into the module execute file

- **hvcs-***: Add flexibility to issue & MR/PR url jinja filters
  ([#1089](https://github.com/python-semantic-release/python-semantic-release/pull/1089),
  [`275ec88`](https://github.com/python-semantic-release/python-semantic-release/commit/275ec88e6d1637c47065bb752a60017ceba9876c))

* fix(github): fix `issue_url` filter to ignore an issue prefix gracefully

* fix(github): fix `pull_request_url` filter to ignore an PR prefix gracefully

* fix(gitlab): fix `issue_url` filter to ignore an issue prefix gracefully

* fix(gitlab): fix `merge_request_url` filter to ignore an PR prefix gracefully

* fix(gitea): fix `issue_url` filter to ignore an issue prefix gracefully

* fix(gitea): fix `pull_request_url` filter to ignore an PR prefix gracefully

* fix(bitbucket): fix `pull_request_url` filter to ignore an PR prefix gracefully

* test(bitbucket): add test case for prefixed PR numbers

* test(gitea): add test case for prefixed PR & issue numbers

* test(gitlab): add test case for prefixed PR & issue numbers

* test(github): add test case for prefixed PR & issue numbers

* style(hvcs): fix logical lint errors

* docs(changelog-templates): update descriptions of issue & MR/PR url jinja filters


## v9.12.1 (2024-11-06)

### Bug Fixes

- **changelog**: Fix raw-inline pattern replacement in `convert_md_to_rst` filter
  ([`2dc70a6`](https://github.com/python-semantic-release/python-semantic-release/commit/2dc70a6106776106b0fba474b0029071317d639f))

- **cmd-version**: Fix `--as-prerelease` when no commit change from last full release
  ([#1076](https://github.com/python-semantic-release/python-semantic-release/pull/1076),
  [`3b7b772`](https://github.com/python-semantic-release/python-semantic-release/commit/3b7b77246100cedd8cc8f289395f7641187ffdec))

- **release-notes**: Add context variable shorthand `ctx` like docs claim & changelog has
  ([`d618d83`](https://github.com/python-semantic-release/python-semantic-release/commit/d618d83360c4409fc149f70b97c5fe338fa89968))

### Documentation

- **contributing**: Update local testing instructions
  ([`74f03d4`](https://github.com/python-semantic-release/python-semantic-release/commit/74f03d44684b7b2d84f9f5e471425b02f8bf91c3))


## v9.12.0 (2024-10-18)

### Bug Fixes

- **changelog**: Ignore commit exclusion when a commit causes a version bump
  ([`e8f886e`](https://github.com/python-semantic-release/python-semantic-release/commit/e8f886ef2abe8ceaea0a24a0112b92a167abd6a9))

- **parser-angular**: Change `Fixes` commit type heading to `Bug Fixes`
  ([#1064](https://github.com/python-semantic-release/python-semantic-release/pull/1064),
  [`09e3a4d`](https://github.com/python-semantic-release/python-semantic-release/commit/09e3a4da6237740de8e9932d742b18d990e9d079))

* test(fixtures): update expected changelog heading to `Bug Fixes`

* test(unit): update expected changelog heading to `Bug Fixes`

- **parser-emoji**: Enable the default bump level option
  ([`bc27995`](https://github.com/python-semantic-release/python-semantic-release/commit/bc27995255a96b9d6cc743186e7c35098822a7f6))

### Documentation

- **commit-parsers**: Add deprecation message for the tag parser
  ([`af94540`](https://github.com/python-semantic-release/python-semantic-release/commit/af94540f2b1c63bf8a4dc977d5d0f66176962b64))

- **configuration**: Add deprecation message for the tag parser
  ([`a83b7e4`](https://github.com/python-semantic-release/python-semantic-release/commit/a83b7e43e4eaa99790969a6c85f44e01cde80d0a))

### Features

- **changelog**: Add `autofit_text_width` filter to template environment
  ([#1062](https://github.com/python-semantic-release/python-semantic-release/pull/1062),
  [`83e4b86`](https://github.com/python-semantic-release/python-semantic-release/commit/83e4b86abd4754c2f95ec2e674f04deb74b9a1e6))

This change adds an equivalent style formatter that can apply a text alignment to a maximum width
  and also maintain an indent over paragraphs of text

* docs(changelog-templates): add definition & usage of `autofit_text_width` template filter

* test(changelog-context): add test cases to check `autofit_text_width` filter use


## v9.11.1 (2024-10-15)

### Bug Fixes

- **changelog**: Prevent custom template errors when components are in hidden folders
  ([#1060](https://github.com/python-semantic-release/python-semantic-release/pull/1060),
  [`a7614b0`](https://github.com/python-semantic-release/python-semantic-release/commit/a7614b0db8ce791e4252209e66f42b5b5275dffd))


## v9.11.0 (2024-10-12)

### Features

- **changelog**: Add default changelog template in reStructuredText format
  ([#1055](https://github.com/python-semantic-release/python-semantic-release/pull/1055),
  [`c2e8831`](https://github.com/python-semantic-release/python-semantic-release/commit/c2e883104d3c11e56f229638e988d8b571f86e34))

* test(fixtures): update repo generation to create rst & md changelogs

* test(release-history): refactor fragile test to utilize repo fixture definitions

* test(changelog-cmd): update tests to evaluate rst changelog generation & updates

* test(version-cmd): update tests to evaluate rst changelog generation & updates

* test(version-cmd): update test code to match new commit definition functions

* test(config): add test to validate `insertion_flag` default determination

* feat(changelog): add `convert_md_to_rst` filter to changelog environment

* feat(changelog): add default changelog in re-structured text format

This change adds the templates to create an equivalent CHANGELOG.RST file in angular changelog
  style. It can be enabled via the `output_format` configuration setting.

Resolves: #399

* feat(config): enable target changelog filename to trigger RST output format

* feat(config): enable default `changelog.insertion_flag` based on output format

* refactor(config): move `changelog_file` setting under `changelog.default_templates`

This change adds a secondary `changelog_file` setting under the default_templates section while
  deprecating the top level one. Since this is not intended to be a breaking change we provided a
  warning message and compatibility code to pass along the current `changelog_file` value to the new
  setting location while giving the user a notification to update before the next version.

* fix(changelog): correct spacing for default markdown template during updates

* docs(configuration): update details of `insertion_flag`'s dynamic defaults with rst

* docs(configuration): update `output_format` description for reStructuredText support

* docs(configuration): update `changelog_file` with deprecation notice of setting relocation

* docs(changelog): clarify the `convert_md_to_rst` filter added to the template environment

* docs(changelog): increase detail about configuration options of default changelog creation


## v9.10.1 (2024-10-10)

### Bug Fixes

- **config**: Handle branch match regex errors gracefully
  ([#1054](https://github.com/python-semantic-release/python-semantic-release/pull/1054),
  [`4d12251`](https://github.com/python-semantic-release/python-semantic-release/commit/4d12251c678a38de6b71cac5b9c1390eb9dd8ad6))

prevents stacktrace error when user provided regex for a branch name match is invalid. Translates
  most common failure of a plain wildcard `*` character to the implied proper regex


## v9.10.0 (2024-10-08)

### Documentation

- **github-actions**: Update primary example with workflow sha controlled pipeline
  ([`14f04df`](https://github.com/python-semantic-release/python-semantic-release/commit/14f04dffc7366142faecebb162d4449501cbf1fd))

### Features

- **changelog**: Modify changelog template to support changelog updates
  ([#1045](https://github.com/python-semantic-release/python-semantic-release/pull/1045),
  [`c18c245`](https://github.com/python-semantic-release/python-semantic-release/commit/c18c245df51a9778af09b9dc7a315e3f11cdcda0))

* feat(changelog): add `read_file` function to changelog template context

This feature adds a filter that will enable jinja templates to read a file from the repository into
  memory to then use as output within the template. The primary use for this is to read in a
  previous changelog file which then the template can give the illusion of insertion as it re-writes
  the entire file.

* feat(changelog): add `changelog_mode` to changelog template context

Adds a flag that can be passed to the templating environment to allow for triggering an update mode
  of a changelog versions an initialization mode. The usage is up to the template developer but for
  PSR it is used to handle changelog generation vs changelog updating.

* feat(changelog): add `prev_changelog_file` to changelog template context

This adds a string that represents a filename to a previous changelog file which can be read from
  inside the template context. The primary use is for enabling the updating of a changelog through
  jinja templating.

* feat(changelog): add `changelog_insertion_flag` to changelog template context

This adds a customizable string to the jinja templating context which allows users to use the PSR
  configuration to pass a custom insertion flag into the templating context. This is intended for
  use with initializing a changelog and then updating it from that point forward.

* feat(changelog): add shorthand `ctx` variable to changelog template env

* refactor(changelog): change recursive render to not use file streaming

It would be nice to maintain file streaming for better memory usage but it prevents the ability to
  read the file contents previously from within the template which is a desire in order to insert
  into a previous changelog. In this case, the memory usage is likely not a problem for large text
  files.

* fix(config): prevent jinja from autoescaping markdown content by default

Since this project is generally rendering non-html content such as RST or MD, change the default of
  the jinja autoescape parameter to false instead of true. When it was true, it would automatically
  convert any `&` ampersands to its htmlentity equivalent `&amp;` which is completely unnecessary
  and unreadable in non-html documents.

* docs(configuration): update `changelog.environment.autoescape` default to `false` to match code

* docs(configuration): standardize all true/false to lowercase ensuring toml-compatibility

* feat(config): add `changelog.mode` as configuration option

* feat(config): add `changelog.insertion_flag` as configuration option

* refactor(config): use `changelog.changelog_file` as previous changelog file for target for update

* style(config): alphabetize changelog configuration options

* docs(configuration): add `changelog.mode` and `changelog.insertion_flag` config definitions

* fix(changelog): adjust angular heading names for readability

* feat(changelog): modify changelog template to support changelog updates

By popular demand, the desire to only prepend new information to the changelog is now possible given
  the `changelog.mode = update` configuration option.

Resolves: #858, #722

* refactor(errors): add new generic internal error for tragic improbable flaws

* fix(changelog): ensure changelog templates can handle complex directory includes

* feat(config): add `changelog.default_templates.output_format` config option

* fix(changelog): only render user templates when files exist

This change ensures that we will use our default even when the user only overrides the release notes
  template. It also must have jinja templates in the folder otherwise we will render the default
  changelog.

* refactor(changelog): enable default changelog rendering of multiple template parts

* refactor(changelog): change rendering of default release notes to new template structure

* refactor(context): use pathlib instead of context manager to read file

* test(fixtures): update changelog generator format & angular heading names

* test(angular): adjust test of commit type to section header

* test(changelog): update make changelog context function call

* test(release-notes): update test related to release notes generation

* test(fixtures): add processing to filter out repo definitions for partial changelogs

* test(fixtures): update repo generators to update changelogs w/ every version

* test(fixtures): slow down repo generators to prevent git failures from same timestamps

* test(fixtures): update changelog generator to include insertion flag

* refactor(changelog): fix template to handle update when no releases exist

* refactor(changelog): adjust template to use improved release object

* refactor(changelog): improve resilence & non-existant initial changelog

* style(changelog-templates): maintain 2-spaces indentation throughout jinja templates

* refactor(changelog): ensure cross-platform template includes with jinja compatibility

* test(changelog-cmd): add tests to evaluate variations of the changelog update mode

* test(version-cmd): add tests to evaluate variations of the changelog update mode

* refactor(release-notes): normalize line endings to universal newlines & always end with newline

* refactor(changelog): ensure default changelog renders w/ universal newlines & writes as
  os-specific

* test(changelog): update changelog testing implementation to be newline aware

* test: update tests to use cross-platform newlines where appropriate

* docs(changelog-templates): improve detail & describe new `changelog.mode="update"`

* docs(configuration): mark version of configuration setting introduction

* docs(homepage): update custom changelog reference

* refactor(changelog): adjust read_file filter to read file as os-newline aware

* refactor(changelog): apply forced universal newline normalizer on default changelog

* test(changelog): adjust implementation to consistently work on windows

* test(version): adjust implementation to consistently work on windows

* refactor(changelog-template): only add insertion flag if in update mode

* test(changelog): adjust test to handle changelog regeneration in init mode

* refactor(changelog-templates): adjust init template to clean up extra newlines

* test(changelog): adjust expected output after cleaned up newlines

* docs(configuration): define the new `changelog.default_templates.output_format` option

- **github-actions**: Add an action `build` directive to toggle the `--skip-build` option
  ([#1044](https://github.com/python-semantic-release/python-semantic-release/pull/1044),
  [`26597e2`](https://github.com/python-semantic-release/python-semantic-release/commit/26597e24a80a37500264aa95a908ba366699099e))

* docs(commands): update definition of the version commands `--skip-build` option

* docs(github-actions): add description of the `build` input directive


## v9.9.0 (2024-09-28)

### Documentation

- **github-actions**: Clarify & consolidate GitHub Actions usage docs
  ([#1011](https://github.com/python-semantic-release/python-semantic-release/pull/1011),
  [`2135c68`](https://github.com/python-semantic-release/python-semantic-release/commit/2135c68ccbdad94378809902b52fcad546efd5b3))

Resolves: #907

* chore(scripts): remove non-existant file from version bump script

* docs(automatic-releases): drop extrenous github push configuration

* docs(homepage): remove link to old github config & update token scope config

* docs(github-actions): expand descriptions & clarity of actions configs

* docs(github-actions): add configuration & description of publish action

* docs(github-actions): revert removal of namespace prefix from examples

### Features

- **github-actions**: Add `is_prerelease` output to the version action
  ([#1038](https://github.com/python-semantic-release/python-semantic-release/pull/1038),
  [`6a5d35d`](https://github.com/python-semantic-release/python-semantic-release/commit/6a5d35d0d9124d6a6ee7910711b4154b006b8773))

* test(github-actions): add test to ensure `is_prerelease` is a action output

* docs(github-actions): add description of new `is_prerelease` output for version action


## v9.8.9 (2024-09-27)

### Bug Fixes

- **version-cmd**: Improve `version_variables` flexibility w/ quotes (ie. json, yaml, etc)
  ([#1028](https://github.com/python-semantic-release/python-semantic-release/pull/1028),
  [`156915c`](https://github.com/python-semantic-release/python-semantic-release/commit/156915c7d759098f65cf9de7c4e980b40b38d5f1))

* fix(version-cmd): increase `version_variable` flexibility with quotations (ie. json, yaml, etc)

Previously json would not work due to the key being wrapped in quotes, yaml also has issues when it
  does not usually use quotes. The regex we created originally only wrapped the version to be
  replaced in quotes but now both the key and version can optionally be wrapped in different kind of
  quotations.

Resolves: #601, #706, #962, #1026

* docs(configuration): add clarity to `version_variables` usage & limitations

Ref: #941

* fix(version-cmd): ensure `version_variables` do not match partial variable names

* build(deps-test): add `PyYAML` as a test dependency

* test(fixtures): refactor location of fixture for global use of cli runner

* test(stamp-version): add test cases to stamp json, python, & yaml files

### Documentation

- Update docstrings to resolve sphinx failures
  ([#1030](https://github.com/python-semantic-release/python-semantic-release/pull/1030),
  [`d84efc7`](https://github.com/python-semantic-release/python-semantic-release/commit/d84efc7719a8679e6979d513d1c8c60904af7384))

set `ignore-module-all` for `autodoc_default_options` to resolve some Sphinx errors about duplicate
  / ambiguous references https://github.com/sphinx-doc/sphinx/issues/4961#issuecomment-1543858623

Standardize some non-standard (Google-ish) docstrings to Sphinx format, to avoid ruff and Sphinx
  arguing about underline length.

Fix indents and other minor whitespace / formatting changes.

Fixes #1029


## v9.8.8 (2024-09-01)

### Bug Fixes

- **config**: Fix path traversal detection for windows compatibility
  ([#1014](https://github.com/python-semantic-release/python-semantic-release/pull/1014),
  [`16e6daa`](https://github.com/python-semantic-release/python-semantic-release/commit/16e6daaf851ce1eabf5fbd5aa9fe310a8b0f22b3))

The original implementation of the path traversal detection expected that `resolve()` works the same
  on windows as it does with Linux/Mac. Windows requires the folder paths to exist to be resolved
  and that is not the case when the `template_dir` is not being used.

Resolves: #994

### Documentation

- **configuration**: Update `build_command` env table for windows to use all capital vars
  ([`0e8451c`](https://github.com/python-semantic-release/python-semantic-release/commit/0e8451cf9003c6a3bdcae6878039d7d9a23d6d5b))

- **github-actions**: Update version in examples to latest version
  ([`3c894ea`](https://github.com/python-semantic-release/python-semantic-release/commit/3c894ea8a555d20b454ebf34785e772959bbb4fe))


## v9.8.7 (2024-08-20)

### Bug Fixes

- Provide `context.history` global in release notes templates
  ([#1005](https://github.com/python-semantic-release/python-semantic-release/pull/1005),
  [`5bd91b4`](https://github.com/python-semantic-release/python-semantic-release/commit/5bd91b4d7ac33ddf10446f3e66d7d11e0724aeb2))

* fix(release-notes): provide `context.history` global in release note templates

Temporarily return the `context.history` variable to release notes generation as many users are
  using it in their release documentation. It was never intended to be provided and will be removed
  in the future.

context was removed in `v9.8.3` during a refactor and condensing of changelog and release notes
  functionality.

Resolves: #984

* fix(release-notes): fix noop-changelog to print raw release notes

Some markdown sequences can be interpreted as ansi escape sequences which dilute debugging of
  release note templates by the user. This change ensures the raw content is displayed to the
  console as expected.

### Documentation

- Use pinned version for GHA examples
  ([#1004](https://github.com/python-semantic-release/python-semantic-release/pull/1004),
  [`5fdf761`](https://github.com/python-semantic-release/python-semantic-release/commit/5fdf7614c036a77ffb051cd30f57d0a63c062c0d))

* docs(github-actions): use pinned version for GHA examples

Fixes #1003

* chore(scripts): add auto version bump to non dynamic docs text (i.e. code snippets)

* docs(github-actions): adjust formatting & version warning in code snippets

* style(docs-github-actions): adjust formatting for readability

---------

Co-authored-by: codejedi365 <codejedi365@gmail.com>

- **changelog**: Clarify description of the default changelog generation process
  ([`399fa65`](https://github.com/python-semantic-release/python-semantic-release/commit/399fa6521d5c6c4397b1d6e9b13ea7945ae92543))

- **configuration**: Clarify `changelog_file` vs `template_dir` option usage
  ([`a7199c8`](https://github.com/python-semantic-release/python-semantic-release/commit/a7199c8cd6041a9de017694302e49b139bbcb034))

Provided additional description that warns about the mutually-exclusive nature of the
  `changelog_file` option and the `template_dir` option.

Resolves: #983

- **configuration**: Fix build_command_env table rendering
  ([#996](https://github.com/python-semantic-release/python-semantic-release/pull/996),
  [`a5eff0b`](https://github.com/python-semantic-release/python-semantic-release/commit/a5eff0bfe41d2fd5d9ead152a132010b718b7772))


## v9.8.6 (2024-07-20)

### Bug Fixes

- **version-cmd**: Resolve build command execution in powershell
  ([#980](https://github.com/python-semantic-release/python-semantic-release/pull/980),
  [`32c8e70`](https://github.com/python-semantic-release/python-semantic-release/commit/32c8e70915634d8e560b470c3cf38c27cebd7ae0))

Fixes the command line option for passing a shell command to Powershell. Also included a similar
  shell detection result for pwsh (Powershell Core)

### Documentation

- **configuration**: Correct GHA parameter name for commit email
  ([#981](https://github.com/python-semantic-release/python-semantic-release/pull/981),
  [`ce9ffdb`](https://github.com/python-semantic-release/python-semantic-release/commit/ce9ffdb82c2358184b288fa18e83a4075f333277))

`git_committer_name` was repeated; replace one instance of it with `git_committer_email`


## v9.8.5 (2024-07-06)

### Bug Fixes

- Enable `--print-last-released*` when in detached head or non-release branch
  ([#926](https://github.com/python-semantic-release/python-semantic-release/pull/926),
  [`782c0a6`](https://github.com/python-semantic-release/python-semantic-release/commit/782c0a6109fb49e168c37f279928c0a4959f8ac6))

* test(version-cmd): add tests to print when detached or non-release branch

ref: #900

* fix(version-cmd): drop branch restriction for `--print-last-released*` opts

Resolves: #900

### Performance Improvements

- Improve git history processing for changelog generation
  ([#972](https://github.com/python-semantic-release/python-semantic-release/pull/972),
  [`bfda159`](https://github.com/python-semantic-release/python-semantic-release/commit/bfda1593af59e9e728c584dd88d7927fc52c879f))

* perf(changelog): improve git history parser changelog generation

This converts the double for-loop (`O(n^2)`) down to `O(n)` using a lookup table to match the
  current commit with a known tag rather than iterating through all the tags of the repository every
  time.

* fix(changelog): resolve commit ordering issue when dates are similar


## v9.8.4 (2024-07-04)

### Bug Fixes

- **changelog-cmd**: Remove usage strings when error occured
  ([`348a51d`](https://github.com/python-semantic-release/python-semantic-release/commit/348a51db8a837d951966aff3789aa0c93d473829))

Resolves: #810

- **changelog-cmd**: Render default changelog when user template directory exist but is empty
  ([`bded8de`](https://github.com/python-semantic-release/python-semantic-release/commit/bded8deae6c92f6dde9774802d9f3716a5cb5705))

- **config**: Prevent path traversal manipulation of target changelog location
  ([`43e35d0`](https://github.com/python-semantic-release/python-semantic-release/commit/43e35d0972e8a29239d18ed079d1e2013342fcbd))

- **config**: Prevent path traversal manipulation of target changelog location
  ([`3eb3dba`](https://github.com/python-semantic-release/python-semantic-release/commit/3eb3dbafec4223ee463b90e927e551639c69426b))

- **publish-cmd**: Prevent error when provided tag does not exist locally
  ([`16afbbb`](https://github.com/python-semantic-release/python-semantic-release/commit/16afbbb8fbc3a97243e96d7573f4ad2eba09aab9))

- **publish-cmd**: Remove usage strings when error occured
  ([`afbb187`](https://github.com/python-semantic-release/python-semantic-release/commit/afbb187d6d405fdf6765082e2a1cecdcd7d357df))

Resolves: #810

- **version-cmd**: Remove usage strings when error occurred
  ([`a7c17c7`](https://github.com/python-semantic-release/python-semantic-release/commit/a7c17c73fd7becb6d0e042e45ff6765605187e2a))

Resolves: #810


## v9.8.3 (2024-06-18)

### Bug Fixes

- **parser**: Strip DOS carriage-returns in commits
  ([#956](https://github.com/python-semantic-release/python-semantic-release/pull/956),
  [`0b005df`](https://github.com/python-semantic-release/python-semantic-release/commit/0b005df0a8c7730ee0c71453c9992d7b5d2400a4))

The default template can result in mixed (UNIX / DOS style) carriage returns in the generated
  changelog. Use a string replace in the commit parser to strip the DOS CRs ("\r"). This is only
  needed in the case when we are _not_ byte decoding.

Fixes #955


## v9.8.2 (2024-06-17)

### Bug Fixes

- **templates**: Suppress extra newlines in default changelog
  ([#954](https://github.com/python-semantic-release/python-semantic-release/pull/954),
  [`7b0079b`](https://github.com/python-semantic-release/python-semantic-release/commit/7b0079bf3e17c0f476bff520b77a571aeac469d0))

Suppress extra newlines in default generated changelog output


## v9.8.1 (2024-06-05)

### Bug Fixes

- Improve build cmd env on windows
  ([#942](https://github.com/python-semantic-release/python-semantic-release/pull/942),
  [`d911fae`](https://github.com/python-semantic-release/python-semantic-release/commit/d911fae993d41a8cb1497fa8b2a7e823576e0f22))

* fix(version-cmd): pass windows specific env vars to build cmd when on windows

* test(version-cmd): extend build cmd tests to include windows vars

* docs(configuration): define windows specific env vars for build cmd

* refactor(version-cmd): only add windows vars when windows is detected

---------

Co-authored-by: Juan Cruz Mencia Naranjo <jcmencia@arsys.es>


## v9.8.0 (2024-05-27)

### Documentation

- **migration-v8**: Update version references in migration instructions
  ([#938](https://github.com/python-semantic-release/python-semantic-release/pull/938),
  [`d6ba16a`](https://github.com/python-semantic-release/python-semantic-release/commit/d6ba16aa8e01bae1a022a9b06cd0b9162c51c345))

### Features

- Extend gitlab to edit a previous release if exists
  ([#934](https://github.com/python-semantic-release/python-semantic-release/pull/934),
  [`23e02b9`](https://github.com/python-semantic-release/python-semantic-release/commit/23e02b96dfb2a58f6b4ecf7b7812e4c1bc50573d))

* style(hvcs-github): update function docstrings for params

* feat(hvcs-gitlab): enable gitlab to edit a previous release if found

* fix(hvcs-gitlab): add tag message to release creation

* fix(gitlab): adjust release name to mirror other hvcs release names

* refactor(gitlab): consolidate & simplify usage of gitlab client

* test(gitlab): neuter test cases that used the internet & add new tests

* refactor(gitlab): handle errors in release retrieval gracefully

* refactor(gitlab): update release notes editing implementation

---------

Co-authored-by: bdorsey <brentadorsey@gmail.com>

- **gha**: Configure ssh signed tags in GitHub Action
  ([#937](https://github.com/python-semantic-release/python-semantic-release/pull/937),
  [`dfb76b9`](https://github.com/python-semantic-release/python-semantic-release/commit/dfb76b94b859a7f3fa3ad778eec7a86de2874d68))

Resolves: #936

- **version-cmd**: Add toggle of `--no-verify` option to `git commit`
  ([#927](https://github.com/python-semantic-release/python-semantic-release/pull/927),
  [`1de6f78`](https://github.com/python-semantic-release/python-semantic-release/commit/1de6f7834c6d37a74bc53f91609d40793556b52d))

* test(version-cmd): add test w/ failing pre-commit hook--preventing version commit

* feat(version-cmd): add toggle of `--no-verify` option to `git commit`

This commit adds a configuration option that toggles the addition of `--no-verify` command line
  switch on git commit operations that are run with the `version` command.

* docs(configuration): add `no_git_verify` description to the configuration page

---------

Co-authored-by: bdorsey <brentadorsey@gmail.com>


## v9.7.3 (2024-05-15)

### Bug Fixes

- Enabled `prelease-token` parameter in github action
  ([#929](https://github.com/python-semantic-release/python-semantic-release/pull/929),
  [`1bb26b0`](https://github.com/python-semantic-release/python-semantic-release/commit/1bb26b0762d94efd97c06a3f1b6b10fb76901f6d))


## v9.7.2 (2024-05-13)

### Bug Fixes

- Enable user configuration of `build_command` env vars
  ([#925](https://github.com/python-semantic-release/python-semantic-release/pull/925),
  [`6b5b271`](https://github.com/python-semantic-release/python-semantic-release/commit/6b5b271453874b982fbf2827ec1f6be6db1c2cc7))

- test(version): add test of user defined env variables in build command

ref: #922

- fix(version): enable user config of `build_command` env variables

Resolves: #922

- docs(configuration): document `build_command_env` configuration option

### Documentation

- **configuration**: Clarify TOC & alphabetize configuration descriptions
  ([`19add16`](https://github.com/python-semantic-release/python-semantic-release/commit/19add16dcfdfdb812efafe2d492a933d0856df1d))

- **configuration**: Clarify TOC & standardize heading links
  ([`3a41995`](https://github.com/python-semantic-release/python-semantic-release/commit/3a4199542d0ea4dbf88fa35e11bec41d0c27dd17))


## v9.7.1 (2024-05-07)

### Bug Fixes

- **gha**: Fix missing `git_committer_*` definition in action
  ([#919](https://github.com/python-semantic-release/python-semantic-release/pull/919),
  [`ccef9d8`](https://github.com/python-semantic-release/python-semantic-release/commit/ccef9d8521be12c0640369b3c3a80b81a7832662))

Resolves: #918


## v9.7.0 (2024-05-06)

### Bug Fixes

- **gha**: Add missing `tag` option to GitHub Action definition
  ([#908](https://github.com/python-semantic-release/python-semantic-release/pull/908),
  [`6b24288`](https://github.com/python-semantic-release/python-semantic-release/commit/6b24288a96302cd6982260e46fad128ec4940da9))

Resolves: #906

### Documentation

- **configuration**: Add description of build command available env variables
  ([`c882dc6`](https://github.com/python-semantic-release/python-semantic-release/commit/c882dc62b860b2aeaa925c21d1524f4ae25ef567))

### Features

- **version-cmd**: Pass `NEW_VERSION` & useful env vars to build command
  ([`ee6b246`](https://github.com/python-semantic-release/python-semantic-release/commit/ee6b246df3bb211ab49c8bce075a4c3f6a68ed77))


## v9.6.0 (2024-04-29)

### Bug Fixes

- Correct version `--prerelease` use & enable `--as-prerelease`
  ([#647](https://github.com/python-semantic-release/python-semantic-release/pull/647),
  [`2acb5ac`](https://github.com/python-semantic-release/python-semantic-release/commit/2acb5ac35ae79d7ae25ca9a03fb5c6a4a68b3673))

* test(version): add validation of `--as-prerelease` and `--prerelease opts`

* fix(version-cmd): correct `--prerelease` use

Prior to this change, `--prerelease` performed the role of converting whichever forced version into
  a prerelease version declaration, which was an unintentional breaking change to the CLI compared
  to v7.

`--prerelease` now forces the next version to increment the prerelease revision, which makes it
  consistent with `--patch`, `--minor` and `--major`. Temporarily disabled the ability to force a
  prerelease.

Resolves: #639

* feat(version-cmd): add `--as-prerelease` option to force the next version to be a prerelease

Prior to this change, `--prerelease` performed the role that `--as-prerelease` now does, which was
  an unintentional breaking change to the CLI compared to v7.

`--prerelease` is used to force the next version to increment the prerelease revision, which makes
  it consistent with `--patch`, `--minor` and `--major`, while `--as-prerelease` forces for the next
  version to be converted to a prerelease version type before it is applied to the project
  regardless of the bump level.

* docs(commands): update version command options definition about prereleases

---------

Co-authored-by: codejedi365 <codejedi365@gmail.com>

- **parser-custom**: Gracefully handle custom parser import errors
  ([`67f6038`](https://github.com/python-semantic-release/python-semantic-release/commit/67f60389e3f6e93443ea108c0e1b4d30126b8e06))

### Features

- Changelog filters are specialized per vcs type
  ([#890](https://github.com/python-semantic-release/python-semantic-release/pull/890),
  [`76ed593`](https://github.com/python-semantic-release/python-semantic-release/commit/76ed593ea33c851005994f0d1a6a33cc890fb908))

* test(github): sync pr url expectation with GitHub api documentation

* fix(github): correct changelog filter for pull request urls

* refactor(hvcs-base): change to an abstract class & simplify interface

* refactor(remote-hvcs-base): extend the base abstract class with common remote base class

* refactor(github): adapt to new abstract base class

* refactor(gitea): adapt to new abstract base class

* refactor(gitlab): adapt to new abstract base class

* refactor(bitbucket): adapt to new abstract base class

* refactor(cmds): prevent hvcs from executing if not remote hosted vcs

* feat(changelog): changelog filters are hvcs focused

* test(hvcs): add validation for issue_url generation

* feat(changelog-github): add issue url filter to changelog context

* feat(changelog-gitea): add issue url filter to changelog context

* refactor(cmd-version): consolidate asset uploads with release creation

* style: resolve ruff errors

* feat(changelog-context): add flag to jinja env for which hvcs is available

* test(changelog-context): demonstrate per hvcs filters upon render

* docs(changelog-context): explain new hvcs specific context filters

* refactor(config): adjust default token resolution w/ subclasses


## v9.5.0 (2024-04-23)

### Build System

- **deps**: Bump ruff from 0.3.5 to 0.3.7
  ([#894](https://github.com/python-semantic-release/python-semantic-release/pull/894),
  [`6bf2849`](https://github.com/python-semantic-release/python-semantic-release/commit/6bf28496d8631ada9009aec5f1000f68b7f7ee16))

### Features

- Extend support to on-prem GitHub Enterprise Server
  ([#896](https://github.com/python-semantic-release/python-semantic-release/pull/896),
  [`4fcb737`](https://github.com/python-semantic-release/python-semantic-release/commit/4fcb737958d95d1a3be24db7427e137b46f5075f))

* test(github): adjust init test to match the Enterprise Server api url

* feat(github): extend support to on-prem GitHub Enterprise Server

Resolves: #895


## v9.4.2 (2024-04-14)

### Bug Fixes

- **hvcs**: Allow insecure http connections if configured
  ([#886](https://github.com/python-semantic-release/python-semantic-release/pull/886),
  [`db13438`](https://github.com/python-semantic-release/python-semantic-release/commit/db1343890f7e0644bc8457f995f2bd62087513d3))

* fix(gitlab): allow insecure http connections if configured

* test(hvcs-gitlab): fix tests for clarity & insecure urls

* test(conftest): refactor netrc generation into common fixture

* refactor(hvcsbase): remove extrenous non-common functionality

* fix(gitea): allow insecure http connections if configured

* test(hvcs-gitea): fix tests for clarity & insecure urls

* refactor(gitlab): adjust init function signature

* fix(github): allow insecure http connections if configured

* test(hvcs-github): fix tests for clarity & insecure urls

* fix(bitbucket): allow insecure http connections if configured

* test(hvcs-bitbucket): fix tests for clarity & insecure urls

* fix(config): add flag to allow insecure connections

* fix(version-cmd): handle HTTP exceptions more gracefully

* style(hvcs): resolve typing issues & mimetype executions

* test(cli-config): adapt default token test for env resolution

* test(changelog-cmd): isolate env & correct the expected api url

* test(fixtures): adapt repo builder for new hvcs init() signature

* style: update syntax for 3.8 compatiblity & formatting

* docs(configuration): update `remote` settings section with missing values

Resolves: #868

* style(docs): improve configuration & api readability

- **hvcs**: Prevent double url schemes urls in changelog
  ([#676](https://github.com/python-semantic-release/python-semantic-release/pull/676),
  [`5cfdb24`](https://github.com/python-semantic-release/python-semantic-release/commit/5cfdb248c003a2d2be5fe65fb61d41b0d4c45db5))

* fix(hvcs): prevent double protocol scheme urls in changelogs

Due to a typo and conditional stripping of the url scheme the hvcs_domain and hvcs_api_domain values
  would contain protocol schemes when a user specified one but the defaults would not. It would
  cause the api_url and remote_url to end up as "https://https://domain.com"

* fix(bitbucket): correct url parsing & prevent double url schemes

* fix(gitea): correct url parsing & prevent double url schemes

* fix(github): correct url parsing & prevent double url schemes

* fix(gitlab): correct url parsing & prevent double url schemes

* test(hvcs): ensure api domains are derived correctly

---------

Co-authored-by: codejedi365 <codejedi365@gmail.com>

### Build System

- **deps**: Update rich requirement from ~=12.5 to ~=13.0
  ([#877](https://github.com/python-semantic-release/python-semantic-release/pull/877),
  [`4a22a8c`](https://github.com/python-semantic-release/python-semantic-release/commit/4a22a8c1a69bcf7b1ddd6db56e6883c617a892b3))

Updates the requirements on [rich](https://github.com/Textualize/rich) to permit the latest version.
  - [Release notes](https://github.com/Textualize/rich/releases) -
  [Changelog](https://github.com/Textualize/rich/blob/master/CHANGELOG.md)

Resolves: #888

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v9.4.1 (2024-04-06)

### Bug Fixes

- **gh-actions-output**: Fixed trailing newline to match GITHUB_OUTPUT format
  ([#885](https://github.com/python-semantic-release/python-semantic-release/pull/885),
  [`2c7b6ec`](https://github.com/python-semantic-release/python-semantic-release/commit/2c7b6ec85b6e3182463d7b695ee48e9669a25b3b))

* test(gh-actions-output): fix unit tests to manage proper whitespace

tests were adjusted for clarity and to replicate error detailed in #884.

* fix(gh-actions-output): fixed trailing newline to match GITHUB_OUTPUT format

Resolves: #884


## v9.4.0 (2024-03-31)

### Features

- **gitea**: Derives gitea api domain from base domain when unspecified
  ([#675](https://github.com/python-semantic-release/python-semantic-release/pull/675),
  [`2ee3f8a`](https://github.com/python-semantic-release/python-semantic-release/commit/2ee3f8a918d2e5ea9ab64df88f52e62a1f589c38))

* test(gitea): add test of custom server path & custom api domain

* feat(gitea): derives gitea api domain from base domain when unspecified

* refactor(hvcs-gitea): uniformly handle protocol prefixes

---------

Co-authored-by: codejedi365 <codejedi365@gmail.com>


## v9.3.1 (2024-03-24)

### Bug Fixes

- **algorithm**: Handle merge-base errors gracefully
  ([`4c998b7`](https://github.com/python-semantic-release/python-semantic-release/commit/4c998b77a3fe5e12783d1ab2d47789a10b83f247))

Merge-base errors generally occur from a shallow clone that is primarily used by CI environments and
  will cause PSR to explode prior to this change. Now it exits with an appropriate error.

Resolves: #724

- **cli-version**: Change implementation to only push the tag we generated
  ([`8a9da4f`](https://github.com/python-semantic-release/python-semantic-release/commit/8a9da4feb8753e3ab9ea752afa25decd2047675a))

Restricts the git push command to only push the explicit tag we created which will eliminate the
  possibility of pushing another tag that could cause an error.

Resolves: #803

### Performance Improvements

- **algorithm**: Simplify logs & use lookup when searching for commit & tag match
  ([`3690b95`](https://github.com/python-semantic-release/python-semantic-release/commit/3690b9511de633ab38083de4d2505b6d05853346))


## v9.3.0 (2024-03-21)

### Features

- **cmd-version**: Changelog available to bundle
  ([#779](https://github.com/python-semantic-release/python-semantic-release/pull/779),
  [`37fdb28`](https://github.com/python-semantic-release/python-semantic-release/commit/37fdb28e0eb886d682b5dea4cc83a7c98a099422))

* test(util): fix overlooked file differences in folder comparison

* test(version): tracked changelog as changed file on version create

Removes the temporary release_notes hack to prevent CHANGELOG generation on execution of version
  command. Now that it is implemented we can remove the fixture to properly pass the tests.

* feat(cmd-version): create changelog prior to build enabling doc bundling


## v9.2.2 (2024-03-19)

### Bug Fixes

- **cli**: Enable subcommand help even if config is invalid
  ([`91d221a`](https://github.com/python-semantic-release/python-semantic-release/commit/91d221a01266e5ca6de5c73296b0a90987847494))

Refactors configuration loading to use lazy loading by subcommands triggered by the property access
  of the runtime_ctx object. Resolves the issues when running `--help` on subcommands when a
  configuration is invalid

Resolves: #840


## v9.2.1 (2024-03-19)

### Bug Fixes

- **parse-git-url**: Handle urls with url-safe special characters
  ([`27cd93a`](https://github.com/python-semantic-release/python-semantic-release/commit/27cd93a0a65ee3787ca51be4c91c48f6ddb4269c))


## v9.2.0 (2024-03-18)

### Bug Fixes

- **changelog**: Make sure default templates render ending in 1 newline
  ([`0b4a45e`](https://github.com/python-semantic-release/python-semantic-release/commit/0b4a45e3673d0408016dc8e7b0dce98007a763e3))

- **changelog-generation**: Fix incorrect release timezone determination
  ([`f802446`](https://github.com/python-semantic-release/python-semantic-release/commit/f802446bd0693c4c9f6bdfdceae8b89c447827d2))

### Build System

- **deps**: Add click-option-group for grouping exclusive flags
  ([`bd892b8`](https://github.com/python-semantic-release/python-semantic-release/commit/bd892b89c26df9fccc9335c84e2b3217e3e02a37))

### Documentation

- **configuration**: Add description of `allow-zero-version` configuration option
  ([`4028f83`](https://github.com/python-semantic-release/python-semantic-release/commit/4028f8384a0181c8d58c81ae81cf0b241a02a710))

- **configuration**: Clarify the `major_on_zero` configuration option
  ([`f7753cd`](https://github.com/python-semantic-release/python-semantic-release/commit/f7753cdabd07e276bc001478d605fca9a4b37ec4))

### Features

- **version**: Add new version print flags to display the last released version and tag
  ([`814240c`](https://github.com/python-semantic-release/python-semantic-release/commit/814240c7355df95e9be9a6ed31d004b800584bc0))

- **version-config**: Add option to disable 0.x.x versions
  ([`dedb3b7`](https://github.com/python-semantic-release/python-semantic-release/commit/dedb3b765c8530379af61d3046c3bb9c160d54e5))


## v9.1.1 (2024-02-25)

### Bug Fixes

- **parse_git_url**: Fix bad url with dash
  ([`1c25b8e`](https://github.com/python-semantic-release/python-semantic-release/commit/1c25b8e6f1e43c15ca7d5a59dca0a13767f9bc33))


## v9.1.0 (2024-02-14)

### Bug Fixes

- Remove unofficial environment variables
  ([`a5168e4`](https://github.com/python-semantic-release/python-semantic-release/commit/a5168e40b9a14dbd022f62964f382b39faf1e0df))

### Build System

- **deps**: Bump minimum required `tomlkit` to `>=0.11.0`
  ([`291aace`](https://github.com/python-semantic-release/python-semantic-release/commit/291aacea1d0429a3b27e92b0a20b598f43f6ea6b))

TOMLDocument is missing the `unwrap()` function in `v0.10.2` which causes an AttributeError to occur
  when attempting to read a the text in `pyproject.toml` as discovered with #834

Resolves: #834

### Documentation

- Add bitbucket authentication
  ([`b78a387`](https://github.com/python-semantic-release/python-semantic-release/commit/b78a387d8eccbc1a6a424a183254fc576126199c))

- Add bitbucket to token table
  ([`56f146d`](https://github.com/python-semantic-release/python-semantic-release/commit/56f146d9f4c0fc7f2a84ad11b21c8c45e9221782))

- Fix typo
  ([`b240e12`](https://github.com/python-semantic-release/python-semantic-release/commit/b240e129b180d45c1d63d464283b7dfbcb641d0c))

### Features

- Add bitbucket hvcs
  ([`bbbbfeb`](https://github.com/python-semantic-release/python-semantic-release/commit/bbbbfebff33dd24b8aed2d894de958d532eac596))


## v9.0.3 (2024-02-08)

### Bug Fixes

- **algorithm**: Correct bfs to not abort on previously visited node
  ([`02df305`](https://github.com/python-semantic-release/python-semantic-release/commit/02df305db43abfc3a1f160a4a52cc2afae5d854f))

### Performance Improvements

- **algorithm**: Refactor bfs search to use queue rather than recursion
  ([`8b742d3`](https://github.com/python-semantic-release/python-semantic-release/commit/8b742d3db6652981a7b5f773a74b0534edc1fc15))


## v9.0.2 (2024-02-08)

### Bug Fixes

- **util**: Properly parse windows line-endings in commit messages
  ([`70193ba`](https://github.com/python-semantic-release/python-semantic-release/commit/70193ba117c1a6d3690aed685fee8a734ba174e5))

Due to windows line-endings `\r\n`, it would improperly split the commit description (it failed to
  split at all) and cause detection of Breaking changes to fail. The breaking changes regular
  expression looks to the start of the line for the proper syntax.

Resolves: #820

### Documentation

- Remove duplicate note in configuration.rst
  ([#807](https://github.com/python-semantic-release/python-semantic-release/pull/807),
  [`fb6f243`](https://github.com/python-semantic-release/python-semantic-release/commit/fb6f243a141642c02469f1080180ecaf4f3cec66))


## v9.0.1 (2024-02-06)

### Bug Fixes

- **config**: Set commit parser opt defaults based on parser choice
  ([#782](https://github.com/python-semantic-release/python-semantic-release/pull/782),
  [`9c594fb`](https://github.com/python-semantic-release/python-semantic-release/commit/9c594fb6efac7e4df2b0bfbd749777d3126d03d7))


## v9.0.0 (2024-02-06)

### Bug Fixes

- Drop support for Python 3.7
  ([#828](https://github.com/python-semantic-release/python-semantic-release/pull/828),
  [`ad086f5`](https://github.com/python-semantic-release/python-semantic-release/commit/ad086f5993ae4741d6e20fee618d1bce8df394fb))


## v8.7.2 (2024-01-03)

### Bug Fixes

- **lint**: Correct linter errors
  ([`c9556b0`](https://github.com/python-semantic-release/python-semantic-release/commit/c9556b0ca6df6a61e9ce909d18bc5be8b6154bf8))


## v8.7.1 (2024-01-03)

### Bug Fixes

- **cli-generate-config**: Ensure configuration types are always toml parsable
  ([#785](https://github.com/python-semantic-release/python-semantic-release/pull/785),
  [`758e649`](https://github.com/python-semantic-release/python-semantic-release/commit/758e64975fe46b961809f35977574729b7c44271))

### Documentation

- Add note on default envvar behaviour
  ([#780](https://github.com/python-semantic-release/python-semantic-release/pull/780),
  [`0b07cae`](https://github.com/python-semantic-release/python-semantic-release/commit/0b07cae71915c5c82d7784898b44359249542a64))

- **configuration**: Change defaults definition of token default to table
  ([#786](https://github.com/python-semantic-release/python-semantic-release/pull/786),
  [`df1df0d`](https://github.com/python-semantic-release/python-semantic-release/commit/df1df0de8bc655cbf8f86ae52aff10efdc66e6d2))

- **contributing**: Add docs-build, testing conf, & build instructions
  ([#787](https://github.com/python-semantic-release/python-semantic-release/pull/787),
  [`011b072`](https://github.com/python-semantic-release/python-semantic-release/commit/011b0729cba3045b4e7291fd970cb17aad7bae60))


## v8.7.0 (2023-12-22)

### Features

- **config**: Enable default environment token per hvcs
  ([#774](https://github.com/python-semantic-release/python-semantic-release/pull/774),
  [`26528eb`](https://github.com/python-semantic-release/python-semantic-release/commit/26528eb8794d00dfe985812269702fbc4c4ec788))


## v8.6.0 (2023-12-22)

### Documentation

- Minor correction to commit-parsing documentation
  ([#777](https://github.com/python-semantic-release/python-semantic-release/pull/777),
  [`245e878`](https://github.com/python-semantic-release/python-semantic-release/commit/245e878f02d5cafec6baf0493c921c1e396b56e8))

### Features

- **utils**: Expand parsable valid git remote url formats
  ([#771](https://github.com/python-semantic-release/python-semantic-release/pull/771),
  [`cf75f23`](https://github.com/python-semantic-release/python-semantic-release/commit/cf75f237360488ebb0088e5b8aae626e97d9cbdd))

Git remote url parsing now supports additional formats (ssh, https, file, git)


## v8.5.2 (2023-12-19)

### Bug Fixes

- **cli**: Gracefully output configuration validation errors
  ([#772](https://github.com/python-semantic-release/python-semantic-release/pull/772),
  [`e8c9d51`](https://github.com/python-semantic-release/python-semantic-release/commit/e8c9d516c37466a5dce75a73766d5be0f9e74627))

* test(fixtures): update example project workflow & add config modifier

* test(cli-main): add test for raw config validation error

* fix(cli): gracefully output configuration validation errors


## v8.5.1 (2023-12-12)

### Bug Fixes

- **cmd-version**: Handle committing of git-ignored file gracefully
  ([#764](https://github.com/python-semantic-release/python-semantic-release/pull/764),
  [`ea89fa7`](https://github.com/python-semantic-release/python-semantic-release/commit/ea89fa72885e15da91687172355426a22c152513))

* fix(version): only commit non git-ignored files during version commit

* test(version): set version file as ignored file

Tweaks tests to use one committed change file and the version file as an ignored change file. This
  allows us to verify that our commit mechanism does not crash if a file that is changed is ignored
  by user

- **config**: Gracefully fail when repo is in a detached HEAD state
  ([#765](https://github.com/python-semantic-release/python-semantic-release/pull/765),
  [`ac4f9aa`](https://github.com/python-semantic-release/python-semantic-release/commit/ac4f9aacb72c99f2479ae33369822faad011a824))

* fix(config): cleanly handle repository in detached HEAD state

* test(cli-main): add detached head cli test

### Documentation

- **configuration**: Adjust wording and improve clarity
  ([#766](https://github.com/python-semantic-release/python-semantic-release/pull/766),
  [`6b2fc8c`](https://github.com/python-semantic-release/python-semantic-release/commit/6b2fc8c156e122ee1b43fdb513b2dc3b8fd76724))

* docs(configuration): fix typo in text

* docs(configuration): adjust wording and improve clarity


## v8.5.0 (2023-12-07)

### Features

- Allow template directories to contain a '.' at the top-level
  ([#762](https://github.com/python-semantic-release/python-semantic-release/pull/762),
  [`07b232a`](https://github.com/python-semantic-release/python-semantic-release/commit/07b232a3b34be0b28c6af08aea4852acb1b9bd56))


## v8.4.0 (2023-12-07)

### Documentation

- **migration**: Fix comments about publish command
  ([#747](https://github.com/python-semantic-release/python-semantic-release/pull/747),
  [`90380d7`](https://github.com/python-semantic-release/python-semantic-release/commit/90380d797a734dcca5040afc5fa00e3e01f64152))

### Features

- **cmd-version**: Add `--tag/--no-tag` option to version command
  ([#752](https://github.com/python-semantic-release/python-semantic-release/pull/752),
  [`de6b9ad`](https://github.com/python-semantic-release/python-semantic-release/commit/de6b9ad921e697b5ea2bb2ea8f180893cecca920))

* fix(version): separate push tags from commit push when not committing changes

* feat(version): add `--no-tag` option to turn off tag creation

* test(version): add test for `--tag` option & `--no-tag/commit`

* docs(commands): update `version` subcommand options


## v8.3.0 (2023-10-23)

### Features

- **action**: Use composite action for semantic release
  ([#692](https://github.com/python-semantic-release/python-semantic-release/pull/692),
  [`4648d87`](https://github.com/python-semantic-release/python-semantic-release/commit/4648d87bac8fb7e6cc361b765b4391b30a8caef8))

Co-authored-by: Bernard Cooke <bernard-cooke@hotmail.com>


## v8.2.0 (2023-10-23)

### Documentation

- Add PYTHONPATH mention for commit parser
  ([`3284258`](https://github.com/python-semantic-release/python-semantic-release/commit/3284258b9fa1a3fe165f336181aff831d50fddd3))

### Features

- Allow user customization of release notes template
  ([#736](https://github.com/python-semantic-release/python-semantic-release/pull/736),
  [`94a1311`](https://github.com/python-semantic-release/python-semantic-release/commit/94a131167e1b867f8bc112a042b9766e050ccfd1))

Signed-off-by: Bryant Finney <bryant.finney@outlook.com>


## v8.1.2 (2023-10-13)

### Bug Fixes

- Correct lint errors
  ([`a13a6c3`](https://github.com/python-semantic-release/python-semantic-release/commit/a13a6c37e180dc422599939a5725835306c18ff2))

GitHub.upload_asset now raises ValueError instead of requests.HTTPError

- Error when running build command on windows systems
  ([#732](https://github.com/python-semantic-release/python-semantic-release/pull/732),
  [`2553657`](https://github.com/python-semantic-release/python-semantic-release/commit/25536574760b407410f435441da533fafbf94402))


## v8.1.1 (2023-09-19)

### Bug Fixes

- Attribute error when logging non-strings
  ([#711](https://github.com/python-semantic-release/python-semantic-release/pull/711),
  [`75e6e48`](https://github.com/python-semantic-release/python-semantic-release/commit/75e6e48129da8238a62d5eccac1ae55d0fee0f9f))


## v8.1.0 (2023-09-19)

### Documentation

- Fix typos ([#708](https://github.com/python-semantic-release/python-semantic-release/pull/708),
  [`2698b0e`](https://github.com/python-semantic-release/python-semantic-release/commit/2698b0e006ff7e175430b98450ba248ed523b341))

- Update project urls
  ([#715](https://github.com/python-semantic-release/python-semantic-release/pull/715),
  [`5fd5485`](https://github.com/python-semantic-release/python-semantic-release/commit/5fd54856dfb6774feffc40d36d5bb0f421f04842))

### Features

- Upgrade pydantic to v2
  ([#714](https://github.com/python-semantic-release/python-semantic-release/pull/714),
  [`5a5c5d0`](https://github.com/python-semantic-release/python-semantic-release/commit/5a5c5d0ee347750d7c417c3242d52e8ada50b217))


## v8.0.8 (2023-08-26)

### Bug Fixes

- Dynamic_import() import path split
  ([#686](https://github.com/python-semantic-release/python-semantic-release/pull/686),
  [`1007a06`](https://github.com/python-semantic-release/python-semantic-release/commit/1007a06d1e16beef6d18f44ff2e0e09921854b54))


## v8.0.7 (2023-08-16)

### Bug Fixes

- Use correct upload url for github
  ([#661](https://github.com/python-semantic-release/python-semantic-release/pull/661),
  [`8a515ca`](https://github.com/python-semantic-release/python-semantic-release/commit/8a515caf1f993aa653e024beda2fdb9e629cc42a))

Co-authored-by: github-actions <action@github.com>


## v8.0.6 (2023-08-13)

### Bug Fixes

- **publish**: Improve error message when no tags found
  ([#683](https://github.com/python-semantic-release/python-semantic-release/pull/683),
  [`bdc06ea`](https://github.com/python-semantic-release/python-semantic-release/commit/bdc06ea061c19134d5d74bd9f168700dd5d9bcf5))


## v8.0.5 (2023-08-10)

### Bug Fixes

- Don't warn about vcs token if ignore_token_for_push is true.
  ([#670](https://github.com/python-semantic-release/python-semantic-release/pull/670),
  [`f1a54a6`](https://github.com/python-semantic-release/python-semantic-release/commit/f1a54a6c9a05b225b6474d50cd610eca19ec0c34))

* fix: don't warn about vcs token if ignore_token_for_push is true.

* docs: `password` should be `token`.

### Documentation

- Fix typo missing 's' in version_variable[s] in configuration.rst
  ([#668](https://github.com/python-semantic-release/python-semantic-release/pull/668),
  [`879186a`](https://github.com/python-semantic-release/python-semantic-release/commit/879186aa09a3bea8bbe2b472f892cf7c0712e557))


## v8.0.4 (2023-07-26)

### Bug Fixes

- **changelog**: Use version as semver tag by default
  ([#653](https://github.com/python-semantic-release/python-semantic-release/pull/653),
  [`5984c77`](https://github.com/python-semantic-release/python-semantic-release/commit/5984c7771edc37f0d7d57894adecc2591efc414d))

### Documentation

- Add Python 3.11 to classifiers in metadata
  ([#651](https://github.com/python-semantic-release/python-semantic-release/pull/651),
  [`5a32a24`](https://github.com/python-semantic-release/python-semantic-release/commit/5a32a24bf4128c39903f0c5d3bd0cb1ccba57e18))

- Clarify usage of assets config option
  ([#655](https://github.com/python-semantic-release/python-semantic-release/pull/655),
  [`efa2b30`](https://github.com/python-semantic-release/python-semantic-release/commit/efa2b3019b41eb427f0e1c8faa21ad10664295d0))


## v8.0.3 (2023-07-21)

### Bug Fixes

- Skip unparseable versions when calculating next version
  ([#649](https://github.com/python-semantic-release/python-semantic-release/pull/649),
  [`88f25ea`](https://github.com/python-semantic-release/python-semantic-release/commit/88f25eae62589cdf53dbc3dfcb167a3ae6cba2d3))


## v8.0.2 (2023-07-18)

### Bug Fixes

- Handle missing configuration
  ([#644](https://github.com/python-semantic-release/python-semantic-release/pull/644),
  [`f15753c`](https://github.com/python-semantic-release/python-semantic-release/commit/f15753ce652f36cc03b108c667a26ab74bcbf95d))

### Documentation

- Better description for tag_format usage
  ([`2129b72`](https://github.com/python-semantic-release/python-semantic-release/commit/2129b729837eccc41a33dbb49785a8a30ce6b187))

- Clarify v8 breaking changes in GitHub action inputs
  ([#643](https://github.com/python-semantic-release/python-semantic-release/pull/643),
  [`cda050c`](https://github.com/python-semantic-release/python-semantic-release/commit/cda050cd9e789d81458157ee240ff99ec65c6f25))

- Correct version_toml example in migrating_from_v7.rst
  ([#641](https://github.com/python-semantic-release/python-semantic-release/pull/641),
  [`325d5e0`](https://github.com/python-semantic-release/python-semantic-release/commit/325d5e048bd89cb2a94c47029d4878b27311c0f0))


## v8.0.1 (2023-07-17)

### Bug Fixes

- Invalid version in Git history should not cause a release failure
  ([#632](https://github.com/python-semantic-release/python-semantic-release/pull/632),
  [`254430b`](https://github.com/python-semantic-release/python-semantic-release/commit/254430b5cc5f032016b4c73168f0403c4d87541e))

### Documentation

- Reduce readthedocs formats and add entries to migration from v7 guide
  ([`9b6ddfe`](https://github.com/python-semantic-release/python-semantic-release/commit/9b6ddfef448f9de30fa2845034f76655d34a9912))

- **migration**: Fix hyperlink
  ([#631](https://github.com/python-semantic-release/python-semantic-release/pull/631),
  [`5fbd52d`](https://github.com/python-semantic-release/python-semantic-release/commit/5fbd52d7de4982b5689651201a0e07b445158645))


## v8.0.0 (2023-07-16)

### Features

- V8 ([#619](https://github.com/python-semantic-release/python-semantic-release/pull/619),
  [`ec30564`](https://github.com/python-semantic-release/python-semantic-release/commit/ec30564b4ec732c001d76d3c09ba033066d2b6fe))

* feat!: 8.0.x (#538)

Co-authored-by: Johan <johanhmr@gmail.com>

Co-authored-by: U-NEO\johan <johan.hammar@ombea.com>

* fix: correct Dockerfile CLI command and GHA fetch

* fix: resolve branch checkout logic in GHA

* fix: remove commit amending behaviour

this was not working when there were no source code changes to be made, as it lead to attempting to
  amend a HEAD commit that wasn't produced by PSR

* 8.0.0-alpha.1

Automatically generated by python-semantic-release

* fix: correct logic for generating release notes (#550)

* fix: cleanup comments and unused logic

* fix(action): mark container fs as safe for git to operate on

* style: beautify 49080c510a68cccd2f6c7a8d540b483751901207

* fix(action): quotation for git config command

* 8.0.0-alpha.2

* fix: resolve bug in changelog logic, enable upload to pypi

* 8.0.0-alpha.3

* test: add tests for ReleaseHistory.release

* fix: resolve loss of tag_format configuration

* 8.0.0-alpha.4

* feat: various improvements

* Added sorting to test parameterisation, so that pytest-xdist works again - dramatic speedup for
  testing * Reworked the CI verification code so it's a bit prettier * Added more testing for the
  version CLI command, and split some logic out of the command itself * Removed a redundant
  double-regex match in VersionTranslator and Version, for some speedup

* chore(test): proper env patching for tests in CI

* style: beautify bcb27a4a8ce4789d083226f088c1810f45cd4c77

* refactor!: remove verify-ci command

* 8.0.0-alpha.5

* fix(docs): fixup docs and remove reference to dist publication

* feat!: remove publication of dists to artefact repository

* feat: rename 'upload' configuration section to 'publish'

* feat!: removed build status checking

* feat: add GitHub Actions output

* fix(action): remove default for 'force'

* fix(ci): different workflow for v8

* fix(action): correct input parsing

* fix: correct handling of build commands

* feat: make it easier to access commit messages in ParsedCommits

* fix: make additional attributes available for template authors

* fix: add logging for token auth, use token for push

* ci: add verbosity

* fix: caching for repo owner and name

* ci: contents permission for workflow

* 8.0.0-alpha.6

* docs: update docs with additional required permissions

* feat: add option to specify tag to publish to in publish command

* feat: add Strict Mode

* docs: convert to Furo theme

* feat: add --skip-build option

* 8.0.0-alpha.7

* test: separate command line tests by stdout and stderr

* ci: pass tag output and conditionally execute publish steps

* fix: correct assets type in configuration (#603)

* change raw config assets type

* fix: correct assets type-annotation for RuntimeContext

---------

Co-authored-by: Bernard Cooke <bernard-cooke@hotmail.com>

* 8.0.0-alpha.8

* fix: pin Debian version in Dockerfile

* feat: promote to rc

* 8.0.0-rc.1

* ci: fix conditionals in workflow and update documentation

* ci: correct conditionals

* fix: only call Github Action output callback once defaults are set

* 8.0.0-rc.2

* fix: create_or_update_release for Gitlab hvcs

* ci: remove separate v8 workflow

* chore: tweak issue templates

* chore: bump docs dependencies

* 8.0.0-rc.3

* fix(deps): add types-click, and downgrade sphinx/furo for 3.7

* 8.0.0-rc.4

* docs: fix typo (#623)

* docs: correct typo in docs/changelog_templates.rst

Co-authored-by: Micael Jarniac <micael@jarniac.com>

Co-authored-by: semantic-release <semantic-release>

Co-authored-by: github-actions <action@github.com>

Co-authored-by: smeng9 <38666763+smeng9@users.noreply.github.com>


## v7.34.6 (2023-06-17)

### Bug Fixes

- Relax invoke dependency constraint
  ([`18ea200`](https://github.com/python-semantic-release/python-semantic-release/commit/18ea200633fd67e07f3d4121df5aa4c6dd29d154))


## v7.34.5 (2023-06-17)

### Bug Fixes

- Consider empty commits
  ([#608](https://github.com/python-semantic-release/python-semantic-release/pull/608),
  [`6f2e890`](https://github.com/python-semantic-release/python-semantic-release/commit/6f2e8909636595d3cb5e858f42c63820cda45974))


## v7.34.4 (2023-06-15)

### Bug Fixes

- Docker build fails installing git
  ([#605](https://github.com/python-semantic-release/python-semantic-release/pull/605),
  [`9e3eb97`](https://github.com/python-semantic-release/python-semantic-release/commit/9e3eb979783bc39ca564c2967c6c77eecba682e6))

git was installed from bullseye-backports, but base image is referencing latest python:3.10 since
  bookworm was recently released, this now points at bookworm and installing the backport of git is
  actually trying to downgrade, resulting in this error:

> E: Packages were downgraded and -y was used without --allow-downgrades.

> ERROR: failed to solve: process "/bin/sh -c echo \"deb http://deb.debian.org/debian
  bullseye-backports main\" >> /etc/apt/sources.list; apt-get update; apt-get install -y
  git/bullseye-backports" did not complete successfully: exit code: 100


## v7.34.3 (2023-06-01)

### Bug Fixes

- Generate markdown linter compliant changelog headers & lists
  ([#597](https://github.com/python-semantic-release/python-semantic-release/pull/597),
  [`cc87400`](https://github.com/python-semantic-release/python-semantic-release/commit/cc87400d4a823350de7d02dc3172d2488c9517db))

In #594, I missed that there are 2 places where the version header is formatted


## v7.34.2 (2023-05-29)

### Bug Fixes

- Open all files with explicit utf-8 encoding
  ([#596](https://github.com/python-semantic-release/python-semantic-release/pull/596),
  [`cb71f35`](https://github.com/python-semantic-release/python-semantic-release/commit/cb71f35c26c1655e675fa735fa880d39a2c8af9c))


## v7.34.1 (2023-05-28)

### Bug Fixes

- Generate markdown linter compliant changelog headers & lists
  ([#594](https://github.com/python-semantic-release/python-semantic-release/pull/594),
  [`9d9d403`](https://github.com/python-semantic-release/python-semantic-release/commit/9d9d40305c499c907335abe313e3ed122db0b154))

Add an extra new line after each header and between sections to fix 2 markdownlint errors for
  changelogs generated by this package


## v7.34.0 (2023-05-28)

### Features

- Add option to only parse commits for current working directory
  ([#509](https://github.com/python-semantic-release/python-semantic-release/pull/509),
  [`cdf8116`](https://github.com/python-semantic-release/python-semantic-release/commit/cdf8116c1e415363b10a01f541873e04ad874220))

When running the application from a sub-directory in the VCS, the option use_only_cwd_commits will
  filter out commits that does not changes the current working directory, similar to running
  commands like `git log -- .` in a sub-directory.


## v7.33.5 (2023-05-19)

### Bug Fixes

- Update docs and default config for gitmoji changes
  ([#590](https://github.com/python-semantic-release/python-semantic-release/pull/590),
  [`192da6e`](https://github.com/python-semantic-release/python-semantic-release/commit/192da6e1352298b48630423d50191070a1c5ab24))

* fix: update docs and default config for gitmoji changes

PR #582 updated to the latest Gitmojis release however the documentation and default config options
  still referenced old and unsupported Gitmojis.

* fix: update sphinx dep

I could only build the documentation locally by updating Sphinx to the latest 1.x version.

### Documentation

- Update broken badge and add links
  ([#591](https://github.com/python-semantic-release/python-semantic-release/pull/591),
  [`0c23447`](https://github.com/python-semantic-release/python-semantic-release/commit/0c234475d27ad887b19170c82deb80293b3a95f1))

The "Test Status" badge was updated to address a recent breaking change in the GitHub actions API.
  All the badges updated to add links to the appropriate resources for end-user convenience.


## v7.33.4 (2023-05-14)

### Bug Fixes

- If prerelease, publish prerelease
  ([#587](https://github.com/python-semantic-release/python-semantic-release/pull/587),
  [`927da9f`](https://github.com/python-semantic-release/python-semantic-release/commit/927da9f8feb881e02bc08b33dc559bd8e7fc41ab))

Co-authored-by: Ondrej Winter <ondrej.winter@gmail.com>


## v7.33.3 (2023-04-24)

### Bug Fixes

- Trim emojis from config
  ([#583](https://github.com/python-semantic-release/python-semantic-release/pull/583),
  [`02902f7`](https://github.com/python-semantic-release/python-semantic-release/commit/02902f73ee961565c2470c000f00947d9ef06cb1))

- Update Gitmojis according to official node module
  ([#582](https://github.com/python-semantic-release/python-semantic-release/pull/582),
  [`806fcfa`](https://github.com/python-semantic-release/python-semantic-release/commit/806fcfa4cfdd3df4b380afd015a68dc90d54215a))

### Documentation

- Grammar in `docs/troubleshooting.rst`
  ([#557](https://github.com/python-semantic-release/python-semantic-release/pull/557),
  [`bbe754a`](https://github.com/python-semantic-release/python-semantic-release/commit/bbe754a3db9ce7132749e7902fe118b52f48ee42))

- change contraction to a possessive pronoun

Signed-off-by: Vladislav Doster <mvdoster@gmail.com>

- Spelling and grammar in `travis.rst`
  ([#556](https://github.com/python-semantic-release/python-semantic-release/pull/556),
  [`3a76e9d`](https://github.com/python-semantic-release/python-semantic-release/commit/3a76e9d7505c421009eb3e953c32cccac2e70e07))

- spelling - subject-verb agreement - remove verbiage

Signed-off-by: Vladislav Doster <mvdoster@gmail.com>

- Update repository name
  ([#559](https://github.com/python-semantic-release/python-semantic-release/pull/559),
  [`5cdb05e`](https://github.com/python-semantic-release/python-semantic-release/commit/5cdb05e20f17b12890e1487c42d317dcbadd06c8))

In order to avoid 'Repository not found: relekang/python-semantic-release.'


## v7.33.2 (2023-02-17)

### Bug Fixes

- Inconsistent versioning between print-version and publish
  ([#524](https://github.com/python-semantic-release/python-semantic-release/pull/524),
  [`17d60e9`](https://github.com/python-semantic-release/python-semantic-release/commit/17d60e9bf66f62e5845065486c9d5e450f74839a))


## v7.33.1 (2023-02-01)

### Bug Fixes

- **action**: Mark container fs as safe for git
  ([#552](https://github.com/python-semantic-release/python-semantic-release/pull/552),
  [`2a55f68`](https://github.com/python-semantic-release/python-semantic-release/commit/2a55f68e2b3cb9ffa9204c00ddbf12706af5c070))

See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124 and
  https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956


## v7.33.0 (2023-01-15)

### Bug Fixes

- Bump Dockerfile to use Python 3.10 image
  ([#536](https://github.com/python-semantic-release/python-semantic-release/pull/536),
  [`8f2185d`](https://github.com/python-semantic-release/python-semantic-release/commit/8f2185d570b3966b667ac591ae523812e9d2e00f))

Fixes #533

Co-authored-by: Bernard Cooke <bernard.cooke@iotics.com>

- Changelog release commit search logic
  ([#530](https://github.com/python-semantic-release/python-semantic-release/pull/530),
  [`efb3410`](https://github.com/python-semantic-release/python-semantic-release/commit/efb341036196c39b4694ca4bfa56c6b3e0827c6c))

* Fixes changelog release commit search logic

Running `semantic-release changelog` currently fails to identify "the last commit in [a] release"
  because the compared commit messages have superfluous whitespace. Likely related to the issue
  causing: https://github.com/relekang/python-semantic-release/issues/490

* Removes a couple of extra `strip()`s.

- Fix mypy errors for publish
  ([`b40dd48`](https://github.com/python-semantic-release/python-semantic-release/commit/b40dd484387c1b3f78df53ee2d35e281e8e799c8))

- Formatting in docs
  ([`2e8227a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8227a8a933683250f8dace019df15fdb35a857))

- Update documentaton
  ([`5cbdad2`](https://github.com/python-semantic-release/python-semantic-release/commit/5cbdad296034a792c9bf05e3700eac4f847eb469))

- **action**: Fix environment variable names
  ([`3c66218`](https://github.com/python-semantic-release/python-semantic-release/commit/3c66218640044adf263fcf9b2714cfc4b99c2e90))

### Features

- Add signing options to action
  ([`31ad5eb`](https://github.com/python-semantic-release/python-semantic-release/commit/31ad5eb5a25f0ea703afc295351104aefd66cac1))

- Update action with configuration options
  ([#518](https://github.com/python-semantic-release/python-semantic-release/pull/518),
  [`4664afe`](https://github.com/python-semantic-release/python-semantic-release/commit/4664afe5f80a04834e398fefb841b166a51d95b7))

Co-authored-by: Kevin Watson <Kevmo92@users.noreply.github.com>

- **repository**: Add support for TWINE_CERT
  ([#522](https://github.com/python-semantic-release/python-semantic-release/pull/522),
  [`d56e85d`](https://github.com/python-semantic-release/python-semantic-release/commit/d56e85d1f2ac66fb0b59af2178164ca915dbe163))

Fixes #521


## v7.32.2 (2022-10-22)

### Bug Fixes

- Fix changelog generation in tag-mode
  ([#171](https://github.com/python-semantic-release/python-semantic-release/pull/171),
  [`482a62e`](https://github.com/python-semantic-release/python-semantic-release/commit/482a62ec374208b2d57675cb0b7f0ab9695849b9))

### Documentation

- Fix code blocks
  ([#506](https://github.com/python-semantic-release/python-semantic-release/pull/506),
  [`24b7673`](https://github.com/python-semantic-release/python-semantic-release/commit/24b767339fcef1c843f7dd3188900adab05e03b1))

Previously: https://i.imgur.com/XWFhG7a.png


## v7.32.1 (2022-10-07)

### Bug Fixes

- Corrections for deprecation warnings
  ([#505](https://github.com/python-semantic-release/python-semantic-release/pull/505),
  [`d47afb6`](https://github.com/python-semantic-release/python-semantic-release/commit/d47afb6516238939e174f946977bf4880062a622))

### Documentation

- Correct spelling mistakes
  ([#504](https://github.com/python-semantic-release/python-semantic-release/pull/504),
  [`3717e0d`](https://github.com/python-semantic-release/python-semantic-release/commit/3717e0d8810f5d683847c7b0e335eeefebbf2921))


## v7.32.0 (2022-09-25)

### Documentation

- Correct documented default behaviour for `commit_version_number`
  ([#497](https://github.com/python-semantic-release/python-semantic-release/pull/497),
  [`ffae2dc`](https://github.com/python-semantic-release/python-semantic-release/commit/ffae2dc68f7f4bc13c5fd015acd43b457e568ada))

### Features

- Add setting for enforcing textual changelog sections
  ([#502](https://github.com/python-semantic-release/python-semantic-release/pull/502),
  [`988437d`](https://github.com/python-semantic-release/python-semantic-release/commit/988437d21e40d3e3b1c95ed66b535bdd523210de))

Resolves #498

Add the `use_textual_changelog_sections` setting flag for enforcing that changelog section headings
  will always be regular ASCII when using the Emoji parser.


## v7.31.4 (2022-08-23)

### Bug Fixes

- Account for trailing newlines in commit messages
  ([#495](https://github.com/python-semantic-release/python-semantic-release/pull/495),
  [`111b151`](https://github.com/python-semantic-release/python-semantic-release/commit/111b1518e8c8e2bd7535bd4c4b126548da384605))

Fixes #490


## v7.31.3 (2022-08-22)

### Bug Fixes

- Use `commit_subject` when searching for release commits
  ([#488](https://github.com/python-semantic-release/python-semantic-release/pull/488),
  [`3849ed9`](https://github.com/python-semantic-release/python-semantic-release/commit/3849ed992c3cff9054b8690bcf59e49768f84f47))

Co-authored-by: Dzmitry Ryzhykau <d.ryzhykau@onesoil.ai>


## v7.31.2 (2022-07-29)

### Bug Fixes

- Add better handling of missing changelog placeholder
  ([`e7a0e81`](https://github.com/python-semantic-release/python-semantic-release/commit/e7a0e81c004ade73ed927ba4de8c3e3ccaf0047c))

There is still one case where we don't add it, but in those corner cases it would be better to do it
  manually than to make it mangled.

Fixes #454

- Add repo=None when not in git repo
  ([`40be804`](https://github.com/python-semantic-release/python-semantic-release/commit/40be804c09ab8a036fb135c9c38a63f206d2742c))

Fixes #422

### Documentation

- Add example for pyproject.toml
  ([`2a4b8af`](https://github.com/python-semantic-release/python-semantic-release/commit/2a4b8af1c2893a769c02476bb92f760c8522bd7a))


## v7.31.1 (2022-07-29)

### Bug Fixes

- Update git email in action
  ([`0ece6f2`](https://github.com/python-semantic-release/python-semantic-release/commit/0ece6f263ff02a17bb1e00e7ed21c490f72e3d00))

Fixes #473


## v7.31.0 (2022-07-29)

### Bug Fixes

- :bug: fix get_current_release_version for tag_only version_source
  ([`cad09be`](https://github.com/python-semantic-release/python-semantic-release/commit/cad09be9ba067f1c882379c0f4b28115a287fc2b))

### Features

- Add prerelease-patch and no-prerelease-patch flags for whether to auto-bump prereleases
  ([`b4e5b62`](https://github.com/python-semantic-release/python-semantic-release/commit/b4e5b626074f969e4140c75fdac837a0625cfbf6))

- Override repository_url w REPOSITORY_URL env var
  ([#439](https://github.com/python-semantic-release/python-semantic-release/pull/439),
  [`cb7578c`](https://github.com/python-semantic-release/python-semantic-release/commit/cb7578cf005b8bd65d9b988f6f773e4c060982e3))


## v7.30.2 (2022-07-26)

### Bug Fixes

- Declare additional_options as action inputs
  ([#481](https://github.com/python-semantic-release/python-semantic-release/pull/481),
  [`cb5d8c7`](https://github.com/python-semantic-release/python-semantic-release/commit/cb5d8c7ce7d013fcfabd7696b5ffb846a8a6f853))


## v7.30.1 (2022-07-25)

### Bug Fixes

- Don't use commit_subject for tag pattern matching
  ([#480](https://github.com/python-semantic-release/python-semantic-release/pull/480),
  [`ac3f11e`](https://github.com/python-semantic-release/python-semantic-release/commit/ac3f11e689f4a290d20b68b9c5c214098eb61b5f))


## v7.30.0 (2022-07-25)

### Bug Fixes

- Allow empty additional options
  ([#479](https://github.com/python-semantic-release/python-semantic-release/pull/479),
  [`c9b2514`](https://github.com/python-semantic-release/python-semantic-release/commit/c9b2514d3e164b20e78b33f60989d78c2587e1df))

### Features

- Add `additional_options` input for GitHub Action
  ([#477](https://github.com/python-semantic-release/python-semantic-release/pull/477),
  [`aea60e3`](https://github.com/python-semantic-release/python-semantic-release/commit/aea60e3d290c6fe3137bff21e0db1ed936233776))


## v7.29.7 (2022-07-24)

### Bug Fixes

- Ignore dependency version bumps when parsing version from commit logs
  ([#476](https://github.com/python-semantic-release/python-semantic-release/pull/476),
  [`51bcb78`](https://github.com/python-semantic-release/python-semantic-release/commit/51bcb780a9f55fadfaf01612ff65c1f92642c2c1))


## v7.29.6 (2022-07-15)

### Bug Fixes

- Allow changing prerelease tag using CLI flags
  ([#466](https://github.com/python-semantic-release/python-semantic-release/pull/466),
  [`395bf4f`](https://github.com/python-semantic-release/python-semantic-release/commit/395bf4f2de73663c070f37cced85162d41934213))

Delay construction of version and release patterns until runtime. This will allow to use non-default
  prerelease tag.

Co-authored-by: Dzmitry Ryzhykau <d.ryzhykau@onesoil.ai>


## v7.29.5 (2022-07-14)

### Bug Fixes

- Add packaging module requirement
  ([#469](https://github.com/python-semantic-release/python-semantic-release/pull/469),
  [`b99c9fa`](https://github.com/python-semantic-release/python-semantic-release/commit/b99c9fa88dc25e5ceacb131cd93d9079c4fb2c86))

- **publish**: Get version bump for current release
  ([#467](https://github.com/python-semantic-release/python-semantic-release/pull/467),
  [`dd26888`](https://github.com/python-semantic-release/python-semantic-release/commit/dd26888a923b2f480303c19f1916647de48b02bf))

Replicate the behavior of "version" command in version calculation.

Co-authored-by: Dzmitry Ryzhykau <d.ryzhykau@onesoil.ai>


## v7.29.4 (2022-06-29)

### Bug Fixes

- Add text for empty ValueError
  ([#461](https://github.com/python-semantic-release/python-semantic-release/pull/461),
  [`733254a`](https://github.com/python-semantic-release/python-semantic-release/commit/733254a99320d8c2f964d799ac4ec29737867faa))


## v7.29.3 (2022-06-26)

### Bug Fixes

- Ensure that assets can be uploaded successfully on custom GitHub servers
  ([#458](https://github.com/python-semantic-release/python-semantic-release/pull/458),
  [`32b516d`](https://github.com/python-semantic-release/python-semantic-release/commit/32b516d7aded4afcafe4aa56d6a5a329b3fc371d))

Signed-off-by: Chris Butler <cbutler@australiacloud.com.au>


## v7.29.2 (2022-06-20)

### Bug Fixes

- Ensure should_bump checks against release version if not prerelease
  ([#457](https://github.com/python-semantic-release/python-semantic-release/pull/457),
  [`da0606f`](https://github.com/python-semantic-release/python-semantic-release/commit/da0606f0d67ada5f097c704b9423ead3b5aca6b2))

Co-authored-by: Sebastian Seith <sebastian@vermill.io>


## v7.29.1 (2022-06-01)

### Bug Fixes

- Capture correct release version when patch has more than one digit
  ([#448](https://github.com/python-semantic-release/python-semantic-release/pull/448),
  [`426cdc7`](https://github.com/python-semantic-release/python-semantic-release/commit/426cdc7d7e0140da67f33b6853af71b2295aaac2))


## v7.29.0 (2022-05-27)

### Bug Fixes

- Fix and refactor prerelease
  ([#435](https://github.com/python-semantic-release/python-semantic-release/pull/435),
  [`94c9494`](https://github.com/python-semantic-release/python-semantic-release/commit/94c94942561f85f48433c95fd3467e03e0893ab4))

### Features

- Allow using ssh-key to push version while using token to publish to hvcs
  ([#419](https://github.com/python-semantic-release/python-semantic-release/pull/419),
  [`7b2dffa`](https://github.com/python-semantic-release/python-semantic-release/commit/7b2dffadf43c77d5e0eea307aefcee5c7744df5c))

* feat(config): add ignore_token_for_push param

Add ignore_token_for_push parameter that allows using the underlying git authentication mechanism
  for pushing a new version commit and tags while also using an specified token to upload dists

* test(config): add test for ignore_token_for_push

Test push_new_version with token while ignore_token_for_push is True and False

* docs: add documentation for ignore_token_for_push

* fix(test): override GITHUB_ACTOR env

push_new_version is using GITHUB_ACTOR env var but we did not contemplate in our new tests that
  actually Github actions running the tests will populate that var and change the test outcome

Now we control the value of that env var and test for it being present or not


## v7.28.1 (2022-04-14)

### Bug Fixes

- Fix getting current version when `version_source=tag_only`
  ([#437](https://github.com/python-semantic-release/python-semantic-release/pull/437),
  [`b247936`](https://github.com/python-semantic-release/python-semantic-release/commit/b247936a81c0d859a34bf9f17ab8ca6a80488081))


## v7.28.0 (2022-04-11)

### Features

- Add `tag_only` option for `version_source`
  ([#436](https://github.com/python-semantic-release/python-semantic-release/pull/436),
  [`cf74339`](https://github.com/python-semantic-release/python-semantic-release/commit/cf743395456a86c62679c2c0342502af043bfc3b))

Fixes #354


## v7.27.1 (2022-04-03)

### Bug Fixes

- **prerelase**: Pass prerelease option to get_current_version
  ([#432](https://github.com/python-semantic-release/python-semantic-release/pull/432),
  [`aabab0b`](https://github.com/python-semantic-release/python-semantic-release/commit/aabab0b7ce647d25e0c78ae6566f1132ece9fcb9))

The `get_current_version` function accepts a `prerelease` argument which was never passed.


## v7.27.0 (2022-03-15)

### Features

- Add git-lfs to docker container
  ([#427](https://github.com/python-semantic-release/python-semantic-release/pull/427),
  [`184e365`](https://github.com/python-semantic-release/python-semantic-release/commit/184e3653932979b82e5a62b497f2a46cbe15ba87))


## v7.26.0 (2022-03-07)

### Features

- Add prerelease functionality
  ([#413](https://github.com/python-semantic-release/python-semantic-release/pull/413),
  [`7064265`](https://github.com/python-semantic-release/python-semantic-release/commit/7064265627a2aba09caa2873d823b594e0e23e77))

* chore: add initial todos * feat: add prerelease tag option * feat: add prerelease cli flag * feat:
  omit_pattern for previouse and current version getters * feat: print_version with prerelease bump
  * feat: make print_version prerelease ready * feat: move prerelease determination to
  get_new_version * test: improve get_last_version test * docs: added basic infos about prereleases
  * feat: add prerelease flag to version and publish * feat: remove leftover todos

Co-authored-by: Mario Jäckle <m.jaeckle@careerpartner.eu>


## v7.25.2 (2022-02-24)

### Bug Fixes

- **gitea**: Use form-data from asset upload
  ([#421](https://github.com/python-semantic-release/python-semantic-release/pull/421),
  [`e011944`](https://github.com/python-semantic-release/python-semantic-release/commit/e011944987885f75b80fe16a363f4befb2519a91))


## v7.25.1 (2022-02-23)

### Bug Fixes

- **gitea**: Build status and asset upload
  ([#420](https://github.com/python-semantic-release/python-semantic-release/pull/420),
  [`57db81f`](https://github.com/python-semantic-release/python-semantic-release/commit/57db81f4c6b96da8259e3bad9137eaccbcd10f6e))

* fix(gitea): handle list build status response * fix(gitea): use form-data for upload_asset


## v7.25.0 (2022-02-17)

### Documentation

- Document tag_commit
  ([`b631ca0`](https://github.com/python-semantic-release/python-semantic-release/commit/b631ca0a79cb2d5499715d43688fc284cffb3044))

Fixes #410

### Features

- **hvcs**: Add gitea support
  ([#412](https://github.com/python-semantic-release/python-semantic-release/pull/412),
  [`b7e7936`](https://github.com/python-semantic-release/python-semantic-release/commit/b7e7936331b7939db09abab235c8866d800ddc1a))


## v7.24.0 (2022-01-24)

### Features

- Include additional changes in release commits
  ([`3e34f95`](https://github.com/python-semantic-release/python-semantic-release/commit/3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9))

Add new config keys, `pre_commit_command` and `commit_additional_files`, to allow custom file
  changes alongside the release commits.


## v7.23.0 (2021-11-30)

### Features

- Support Github Enterprise server
  ([`b4e01f1`](https://github.com/python-semantic-release/python-semantic-release/commit/b4e01f1b7e841263fa84f57f0ac331f7c0b31954))


## v7.22.0 (2021-11-21)

### Bug Fixes

- Address PR feedback for `parser_angular.py`
  ([`f7bc458`](https://github.com/python-semantic-release/python-semantic-release/commit/f7bc45841e6a5c762f99f936c292cee25fabcd02))

- `angular_parser_default_level_bump` should have plain-english settings - rename `TYPES` variable
  to `LONG_TYPE_NAMES`

### Features

- **parser_angular**: Allow customization in parser
  ([`298eebb`](https://github.com/python-semantic-release/python-semantic-release/commit/298eebbfab5c083505036ba1df47a5874a1eed6e))

- `parser_angular_allowed_types` controls allowed types - defaults stay the same: build, chore, ci,
  docs, feat, fix, perf, style, refactor, test - `parser_angular_default_level_bump` controls the
  default level to bump the version by - default stays at 0 - `parser_angular_minor_types` controls
  which types trigger a minor version bump - default stays at only 'feat' -
  `parser_angular_patch_types` controls which types trigger a patch version - default stays at 'fix'
  or 'perf'


## v7.21.0 (2021-11-21)

### Bug Fixes

- Remove invalid repository exception
  ([`746b62d`](https://github.com/python-semantic-release/python-semantic-release/commit/746b62d4e207a5d491eecd4ca96d096eb22e3bed))

### Features

- Use gitlab-ci or github actions env vars
  ([`8ca8dd4`](https://github.com/python-semantic-release/python-semantic-release/commit/8ca8dd40f742f823af147928bd75a9577c50d0fd))

return owner and project name from Gitlab/Github environment variables if available

Issue #363


## v7.20.0 (2021-11-21)

### Bug Fixes

- Don't use linux commands on windows
  ([#393](https://github.com/python-semantic-release/python-semantic-release/pull/393),
  [`5bcccd2`](https://github.com/python-semantic-release/python-semantic-release/commit/5bcccd21cc8be3289db260e645fec8dc6a592abd))

- Mypy errors in vcs_helpers
  ([`13ca0fe`](https://github.com/python-semantic-release/python-semantic-release/commit/13ca0fe650125be2f5e953f6193fdc4d44d3c75a))

- Skip removing the build folder if it doesn't exist
  ([`8e79fdc`](https://github.com/python-semantic-release/python-semantic-release/commit/8e79fdc107ffd852a91dfb5473e7bd1dfaba4ee5))

https://github.com/relekang/python-semantic-release/issues/391#issuecomment-950667599

### Documentation

- Clean typos and add section for repository upload
  ([`1efa18a`](https://github.com/python-semantic-release/python-semantic-release/commit/1efa18a3a55134d6bc6e4572ab025e24082476cd))

Add more details and external links

### Features

- Allow custom environment variable names
  ([#392](https://github.com/python-semantic-release/python-semantic-release/pull/392),
  [`372cda3`](https://github.com/python-semantic-release/python-semantic-release/commit/372cda3497f16ead2209e6e1377d38f497144883))

* GH_TOKEN can now be customized by setting github_token_var * GL_TOKEN can now be customized by
  setting gitlab_token_var * PYPI_PASSWORD can now be customized by setting pypi_pass_var *
  PYPI_TOKEN can now be customized by setting pypi_token_var * PYPI_USERNAME can now be customized
  by setting pypi_user_var

- Rewrite Twine adapter for uploading to artifact repositories
  ([`cfb20af`](https://github.com/python-semantic-release/python-semantic-release/commit/cfb20af79a8e25a77aee9ff72deedcd63cb7f62f))

Artifact upload generalised to fully support custom repositories like GitLab. Rewritten to use twine
  python api instead of running the executable. No-op mode now respected by artifact upload.


## v7.19.2 (2021-09-04)

### Bug Fixes

- Fixed ImproperConfig import error
  ([#377](https://github.com/python-semantic-release/python-semantic-release/pull/377),
  [`b011a95`](https://github.com/python-semantic-release/python-semantic-release/commit/b011a9595df4240cb190bfb1ab5b6d170e430dfc))


## v7.19.1 (2021-08-17)

### Bug Fixes

- Add get_formatted_tag helper instead of hardcoded v-prefix in the git tags
  ([`1a354c8`](https://github.com/python-semantic-release/python-semantic-release/commit/1a354c86abad77563ebce9a6944256461006f3c7))


## v7.19.0 (2021-08-16)

### Documentation

- **parser**: Documentation for scipy-parser
  ([`45ee34a`](https://github.com/python-semantic-release/python-semantic-release/commit/45ee34aa21443860a6c2cd44a52da2f353b960bf))

### Features

- Custom git tag format support
  ([#373](https://github.com/python-semantic-release/python-semantic-release/pull/373),
  [`1d76632`](https://github.com/python-semantic-release/python-semantic-release/commit/1d76632043bf0b6076d214a63c92013624f4b95e))

* feat: custom git tag format support * test: add git tag format check * docs: add tag_format config
  option


## v7.18.0 (2021-08-09)

### Documentation

- Clarify second argument of ParsedCommit
  ([`086ddc2`](https://github.com/python-semantic-release/python-semantic-release/commit/086ddc28f06522453328f5ea94c873bd202ff496))

### Features

- Add support for non-prefixed tags
  ([#366](https://github.com/python-semantic-release/python-semantic-release/pull/366),
  [`0fee4dd`](https://github.com/python-semantic-release/python-semantic-release/commit/0fee4ddb5baaddf85ed6b76e76a04474a5f97d0a))


## v7.17.0 (2021-08-07)

### Features

- **parser**: Add scipy style parser
  ([#369](https://github.com/python-semantic-release/python-semantic-release/pull/369),
  [`51a3921`](https://github.com/python-semantic-release/python-semantic-release/commit/51a39213ea120c4bbd7a57b74d4f0cc3103da9f5))


## v7.16.4 (2021-08-03)

### Bug Fixes

- Correct rendering of gitlab issue references
  ([`07429ec`](https://github.com/python-semantic-release/python-semantic-release/commit/07429ec4a32d32069f25ec77b4bea963bd5d2a00))

resolves #358


## v7.16.3 (2021-07-29)

### Bug Fixes

- Print right info if token is not set (#360)
  ([#361](https://github.com/python-semantic-release/python-semantic-release/pull/361),
  [`a275a7a`](https://github.com/python-semantic-release/python-semantic-release/commit/a275a7a17def85ff0b41d254e4ee42772cce1981))

Co-authored-by: Laercio Barbosa <laercio.barbosa@scania.com>


## v7.16.2 (2021-06-25)

### Bug Fixes

- Use release-api for gitlab
  ([`1ef5cab`](https://github.com/python-semantic-release/python-semantic-release/commit/1ef5caba2d8dd0f2647bc51ede0ef7152d8b7b8d))

### Documentation

- Recommend setting a concurrency group for GitHub Actions
  ([`34b0735`](https://github.com/python-semantic-release/python-semantic-release/commit/34b07357ab3f4f4aa787b71183816ec8aaf334a8))

- Update trove classifiers to reflect supported versions
  ([#344](https://github.com/python-semantic-release/python-semantic-release/pull/344),
  [`7578004`](https://github.com/python-semantic-release/python-semantic-release/commit/7578004ed4b20c2bd553782443dfd77535faa377))


## v7.16.1 (2021-06-08)

### Bug Fixes

- Tomlkit should stay at 0.7.0
  ([`769a5f3`](https://github.com/python-semantic-release/python-semantic-release/commit/769a5f31115cdb1f43f19a23fe72b96a8c8ba0fc))

See https://github.com/relekang/python-semantic-release/pull/339#discussion_r647629387


## v7.16.0 (2021-06-08)

### Features

- Add option to omit tagging
  ([#341](https://github.com/python-semantic-release/python-semantic-release/pull/341),
  [`20603e5`](https://github.com/python-semantic-release/python-semantic-release/commit/20603e53116d4f05e822784ce731b42e8cbc5d8f))


## v7.15.6 (2021-06-08)

### Bug Fixes

- Update click and tomlkit
  ([#339](https://github.com/python-semantic-release/python-semantic-release/pull/339),
  [`947ea3b`](https://github.com/python-semantic-release/python-semantic-release/commit/947ea3bc0750735941446cf4a87bae20e750ba12))


## v7.15.5 (2021-05-26)

### Bug Fixes

- Pin tomlkit to 0.7.0
  ([`2cd0db4`](https://github.com/python-semantic-release/python-semantic-release/commit/2cd0db4537bb9497b72eb496f6bab003070672ab))


## v7.15.4 (2021-04-29)

### Bug Fixes

- Change log level of failed toml loading
  ([`24bb079`](https://github.com/python-semantic-release/python-semantic-release/commit/24bb079cbeff12e7043dd35dd0b5ae03192383bb))

Fixes #235


## v7.15.3 (2021-04-03)

### Bug Fixes

- Add venv to path in github action
  ([`583c5a1`](https://github.com/python-semantic-release/python-semantic-release/commit/583c5a13e40061fc544b82decfe27a6c34f6d265))


## v7.15.2 (2021-04-03)

### Bug Fixes

- Run semantic-release in virtualenv in the github action
  ([`b508ea9`](https://github.com/python-semantic-release/python-semantic-release/commit/b508ea9f411c1cd4f722f929aab9f0efc0890448))

Fixes #331

- Set correct path for venv in action script
  ([`aac02b5`](https://github.com/python-semantic-release/python-semantic-release/commit/aac02b5a44a6959328d5879578aa3536bdf856c2))

- Use absolute path for venv in github action
  ([`d4823b3`](https://github.com/python-semantic-release/python-semantic-release/commit/d4823b3b6b1fcd5c33b354f814643c9aaf85a06a))

### Documentation

- Clarify that HVCS should be lowercase
  ([`da0ab0c`](https://github.com/python-semantic-release/python-semantic-release/commit/da0ab0c62c4ce2fa0d815e5558aeec1a1e23bc89))

Fixes #330


## v7.15.1 (2021-03-26)

### Bug Fixes

- Add support for setting build_command to "false"
  ([`520cf1e`](https://github.com/python-semantic-release/python-semantic-release/commit/520cf1eaa7816d0364407dbd17b5bc7c79806086))

Fixes #328

- Upgrade python-gitlab range
  ([`abfacc4`](https://github.com/python-semantic-release/python-semantic-release/commit/abfacc432300941d57488842e41c06d885637e6c))

Keeping both 1.x and 2.x since only change that is breaking is dropping python 3.6 support. I hope
  that leaving the lower limit will make it still work with python 3.6.

Fixes #329

### Documentation

- Add common options to documentation
  ([`20d79a5`](https://github.com/python-semantic-release/python-semantic-release/commit/20d79a51bffa26d40607c1b77d10912992279112))

These can be found by running `semantic-release --help`, but including them in the documentation
  will be helpful for CI users who don't have the command installed locally.

Related to #327.


## v7.15.0 (2021-02-18)

### Documentation

- Add documentation for releasing on a Jenkins instance
  ([#324](https://github.com/python-semantic-release/python-semantic-release/pull/324),
  [`77ad988`](https://github.com/python-semantic-release/python-semantic-release/commit/77ad988a2057be59e4559614a234d6871c06ee37))

### Features

- Allow the use of .pypirc for twine uploads
  ([#325](https://github.com/python-semantic-release/python-semantic-release/pull/325),
  [`6bc56b8`](https://github.com/python-semantic-release/python-semantic-release/commit/6bc56b8aa63069a25a828a2d1a9038ecd09b7d5d))


## v7.14.0 (2021-02-11)

### Documentation

- Correct casing on proper nouns
  ([#320](https://github.com/python-semantic-release/python-semantic-release/pull/320),
  [`d51b999`](https://github.com/python-semantic-release/python-semantic-release/commit/d51b999a245a4e56ff7a09d0495c75336f2f150d))

* docs: correcting Semantic Versioning casing

Semantic Versioning is the name of the specification. Therefore it is a proper noun. This patch
  corrects the incorrect casing for Semantic Versioning.

* docs: correcting Python casing

This patch corrects the incorrect casing for Python.

### Features

- **checks**: Add support for Jenkins CI
  ([#322](https://github.com/python-semantic-release/python-semantic-release/pull/322),
  [`3e99855`](https://github.com/python-semantic-release/python-semantic-release/commit/3e99855c6bc72b3e9a572c58cc14e82ddeebfff8))

Includes a ci check handler to verify jenkins. Unlike other ci systems jenkins doesn't generally
  prefix things with `JENKINS` or simply inject `JENKINS=true` Really the only thing that is
  immediately identifiable is `JENKINS_URL`


## v7.13.2 (2021-01-29)

### Bug Fixes

- Fix crash when TOML has no PSR section
  ([#319](https://github.com/python-semantic-release/python-semantic-release/pull/319),
  [`5f8ab99`](https://github.com/python-semantic-release/python-semantic-release/commit/5f8ab99bf7254508f4b38fcddef2bdde8dd15a4c))

* test: reproduce issue with TOML without PSR section

* fix: crash when TOML has no PSR section

* chore: remove unused imports

### Documentation

- Fix `version_toml` example for Poetry
  ([#318](https://github.com/python-semantic-release/python-semantic-release/pull/318),
  [`39acb68`](https://github.com/python-semantic-release/python-semantic-release/commit/39acb68bfffe8242040e476893639ba26fa0d6b5))


## v7.13.1 (2021-01-26)

### Bug Fixes

- Use multiline version_pattern match in replace
  ([#315](https://github.com/python-semantic-release/python-semantic-release/pull/315),
  [`1a85af4`](https://github.com/python-semantic-release/python-semantic-release/commit/1a85af434325ce52e11b49895e115f7a936e417e))

Fixes #306


## v7.13.0 (2021-01-26)

### Features

- Support toml files for version declaration
  ([#307](https://github.com/python-semantic-release/python-semantic-release/pull/307),
  [`9b62a7e`](https://github.com/python-semantic-release/python-semantic-release/commit/9b62a7e377378667e716384684a47cdf392093fa))

This introduce a new `version_toml` configuration property that behaves like `version_pattern` and
  `version_variable`.

For poetry support, user should now set `version_toml = pyproject.toml:tool.poetry.version`.

This introduce an ABC class, `VersionDeclaration`, that can be implemented to add other version
  declarations with ease.

`toml` dependency has been replaced by `tomlkit`, as this is used the library used by poetry to
  generate the `pyproject.toml` file, and is able to keep the ordering of data defined in the file.

Existing `VersionPattern` class has been renamed to `PatternVersionDeclaration` and now implements
  `VersionDeclaration`.

`load_version_patterns()` function has been renamed to `load_version_declarations()` and now return
  a list of `VersionDeclaration` implementations.

Close #245 Close #275


## v7.12.0 (2021-01-25)

### Documentation

- **actions**: Pat must be passed to checkout step too
  ([`e2d8e47`](https://github.com/python-semantic-release/python-semantic-release/commit/e2d8e47d2b02860881381318dcc088e150c0fcde))

Fixes #311

### Features

- **github**: Retry GitHub API requests on failure
  ([#314](https://github.com/python-semantic-release/python-semantic-release/pull/314),
  [`ac241ed`](https://github.com/python-semantic-release/python-semantic-release/commit/ac241edf4de39f4fc0ff561a749fa85caaf9e2ae))

* refactor(github): use requests.Session to call raise_for_status

* fix(github): add retries to github API requests


## v7.11.0 (2021-01-08)

### Bug Fixes

- Add dot to --define option help
  ([`eb4107d`](https://github.com/python-semantic-release/python-semantic-release/commit/eb4107d2efdf8c885c8ae35f48f1b908d1fced32))

- Avoid Unknown bump level 0 message
  ([`8ab624c`](https://github.com/python-semantic-release/python-semantic-release/commit/8ab624cf3508b57a9656a0a212bfee59379d6f8b))

This issue occurs when some commits are available but are all to level 0.

- **actions**: Fix github actions with new main location
  ([`6666672`](https://github.com/python-semantic-release/python-semantic-release/commit/6666672d3d97ab7cdf47badfa3663f1a69c2dbdf))

### Build System

- Add __main__.py magic file
  ([`e93f36a`](https://github.com/python-semantic-release/python-semantic-release/commit/e93f36a7a10e48afb42c1dc3d860a5e2a07cf353))

This file allow to run the package from sources properly with `python -m semantic_release`.

### Features

- **print-version**: Add print-version command to output version
  ([`512e3d9`](https://github.com/python-semantic-release/python-semantic-release/commit/512e3d92706055bdf8d08b7c82927d3530183079))

This new command can be integrated in the build process before the effective release, ie. to rename
  some files with the version number.

Users may invoke `VERSION=$(semantic-release print-version)` to retrieve the version that will be
  generated during the release before it really occurs.


## v7.10.0 (2021-01-08)

### Documentation

- Fix incorrect reference syntax
  ([`42027f0`](https://github.com/python-semantic-release/python-semantic-release/commit/42027f0d2bb64f4c9eaec65112bf7b6f67568e60))

- Rewrite getting started page
  ([`97a9046`](https://github.com/python-semantic-release/python-semantic-release/commit/97a90463872502d1207890ae1d9dd008b1834385))

### Features

- **build**: Allow falsy values for build_command to disable build step
  ([`c07a440`](https://github.com/python-semantic-release/python-semantic-release/commit/c07a440f2dfc45a2ad8f7c454aaac180c4651f70))


## v7.9.0 (2020-12-21)

### Bug Fixes

- **history**: Coerce version to string
  ([#298](https://github.com/python-semantic-release/python-semantic-release/pull/298),
  [`d4cdc3d`](https://github.com/python-semantic-release/python-semantic-release/commit/d4cdc3d3cd2d93f2a78f485e3ea107ac816c7d00))

The changes in #297 mistakenly omitted coercing the return value to a string. This resulted in
  errors like: "can only concatenate str (not "VersionInfo") to str"

Add test case asserting it's type str

- **history**: Require semver >= 2.10
  ([`5087e54`](https://github.com/python-semantic-release/python-semantic-release/commit/5087e549399648cf2e23339a037b33ca8b62d954))

This resolves deprecation warnings, and updates this to a more 3.x compatible syntax

### Features

- **hvcs**: Add hvcs_domain config option
  ([`ab3061a`](https://github.com/python-semantic-release/python-semantic-release/commit/ab3061ae93c49d71afca043b67b361e2eb2919e6))

While Gitlab already has an env var that should provide the vanity URL, this supports a generic
  'hvcs_domain' parameter that makes the hostname configurable for both GHE and Gitlab.

This will also use the configured hostname (from either source) in the changelog links

Fixes: #277


## v7.8.2 (2020-12-19)

### Bug Fixes

- **cli**: Skip remove_dist where not needed
  ([`04817d4`](https://github.com/python-semantic-release/python-semantic-release/commit/04817d4ecfc693195e28c80455bfbb127485f36b))

Skip removing dist files when upload_pypi or upload_release are not set

### Features

- **repository**: Add to settings artifact repository
  ([`f4ef373`](https://github.com/python-semantic-release/python-semantic-release/commit/f4ef3733b948282fba5a832c5c0af134609b26d2))

- Add new config var to set repository (repository_url) - Remove 'Pypi' word when it refers
  generically to an artifact repository system - Depreciate 'PYPI_USERNAME' and 'PYPI_PASSWORD' and
  prefer 'REPOSITORY_USERNAME' and 'REPOSITORY_PASSWORD' env vars - Depreciate every config key with
  'pypi' and prefer repository - Update doc in accordance with those changes


## v7.8.1 (2020-12-18)

### Bug Fixes

- Filenames with unknown mimetype are now properly uploaded to github release
  ([`f3ece78`](https://github.com/python-semantic-release/python-semantic-release/commit/f3ece78b2913e70f6b99907b192a1e92bbfd6b77))

When mimetype can't be guessed, content-type header is set to None. But it's mandatory for the file
  upload to work properly. In this case, application/octect-stream is now used as a fallback.

- **logs**: Fix TypeError when enabling debug logs
  ([`2591a94`](https://github.com/python-semantic-release/python-semantic-release/commit/2591a94115114c4a91a48f5b10b3954f6ac932a1))

Some logger invocation were raising the following error: TypeError: not all arguments converted
  during string formatting.

This also refactor some other parts to use f-strings as much as possible.


## v7.8.0 (2020-12-18)

### Bug Fixes

- **changelog**: Use "issues" link vs "pull"
  ([`93e48c9`](https://github.com/python-semantic-release/python-semantic-release/commit/93e48c992cb8b763f430ecbb0b7f9c3ca00036e4))

While, e.g., https://github.com/owner/repos/pull/123 will work,
  https://github.com/owner/repos/issues/123 should be safer / more consistent, and should avoid a
  failure if someone adds an issue link at the end of a PR that is merged via rebase merge or merge
  commit.

- **netrc**: Prefer using token defined in GH_TOKEN instead of .netrc file
  ([`3af32a7`](https://github.com/python-semantic-release/python-semantic-release/commit/3af32a738f2f2841fd75ec961a8f49a0b1c387cf))

.netrc file will only be used when available and no GH_TOKEN environment variable is defined.

This also add a test to make sure .netrc is used properly when no GH_TOKEN is defined.

### Features

- Add `upload_to_pypi_glob_patterns` option
  ([`42305ed`](https://github.com/python-semantic-release/python-semantic-release/commit/42305ed499ca08c819c4e7e65fcfbae913b8e6e1))


## v7.7.0 (2020-12-12)

### Features

- **changelog**: Add PR links in markdown
  ([#282](https://github.com/python-semantic-release/python-semantic-release/pull/282),
  [`0448f6c`](https://github.com/python-semantic-release/python-semantic-release/commit/0448f6c350bbbf239a81fe13dc5f45761efa7673))

GitHub release notes automagically link to the PR, but changelog markdown doesn't. Replace a PR
  number at the end of a message with a markdown link.


## v7.6.0 (2020-12-06)

### Documentation

- Add documentation for option `major_on_zero`
  ([`2e8b26e`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8b26e4ee0316a2cf2a93c09c783024fcd6b3ba))

### Features

- Add `major_on_zero` option
  ([`d324154`](https://github.com/python-semantic-release/python-semantic-release/commit/d3241540e7640af911eb24c71e66468feebb0d46))

To control if bump major or not when current major version is zero.


## v7.5.0 (2020-12-04)

### Features

- **logs**: Include scope in changelogs
  ([#281](https://github.com/python-semantic-release/python-semantic-release/pull/281),
  [`21c96b6`](https://github.com/python-semantic-release/python-semantic-release/commit/21c96b688cc44cc6f45af962ffe6d1f759783f37))

When the scope is set, include it in changelogs, e.g. "feat(x): some description" becomes "**x**:
  some description". This is similar to how the Node semantic release (and
  conventional-changelog-generator) generates changelogs. If scope is not given, it's omitted.

Add a new config parameter changelog_scope to disable this behavior when set to 'False'


## v7.4.1 (2020-12-04)

### Bug Fixes

- Add "changelog_capitalize" to flags
  ([#279](https://github.com/python-semantic-release/python-semantic-release/pull/279),
  [`37716df`](https://github.com/python-semantic-release/python-semantic-release/commit/37716dfa78eb3f848f57a5100d01d93f5aafc0bf))

Fixes #278 (or so I hope).


## v7.4.0 (2020-11-24)

### Documentation

- Fix broken internal references
  ([#270](https://github.com/python-semantic-release/python-semantic-release/pull/270),
  [`da20b9b`](https://github.com/python-semantic-release/python-semantic-release/commit/da20b9bdd3c7c87809c25ccb2a5993a7ea209a22))

- Update links to Github docs
  ([#268](https://github.com/python-semantic-release/python-semantic-release/pull/268),
  [`c53162e`](https://github.com/python-semantic-release/python-semantic-release/commit/c53162e366304082a3bd5d143b0401da6a16a263))

### Features

- Add changelog_capitalize configuration
  ([`7cacca1`](https://github.com/python-semantic-release/python-semantic-release/commit/7cacca1eb436a7166ba8faf643b53c42bc32a6a7))

Fixes #260


## v7.3.0 (2020-09-28)

### Documentation

- Fix docstring
  ([`5a5e2cf`](https://github.com/python-semantic-release/python-semantic-release/commit/5a5e2cfb5e6653fb2e95e6e23e56559953b2c2b4))

Stumbled upon this docstring which first line seems copy/pasted from the method above.

### Features

- Generate `changelog.md` file
  ([#266](https://github.com/python-semantic-release/python-semantic-release/pull/266),
  [`2587dfe`](https://github.com/python-semantic-release/python-semantic-release/commit/2587dfed71338ec6c816f58cdf0882382c533598))


## v7.2.5 (2020-09-16)

### Bug Fixes

- Add required to inputs in action metadata
  ([#264](https://github.com/python-semantic-release/python-semantic-release/pull/264),
  [`e76b255`](https://github.com/python-semantic-release/python-semantic-release/commit/e76b255cf7d3d156e3314fc28c54d63fa126e973))

According to the documentation, `inputs.<input_id>.required` is a required field.


## v7.2.4 (2020-09-14)

### Bug Fixes

- Use range for toml dependency
  ([`45707e1`](https://github.com/python-semantic-release/python-semantic-release/commit/45707e1b7dcab48103a33de9d7f9fdb5a34dae4a))

Fixes #241


## v7.2.3 (2020-09-12)

### Bug Fixes

- Support multiline version_pattern matching by default
  ([`82f7849`](https://github.com/python-semantic-release/python-semantic-release/commit/82f7849dcf29ba658e0cb3b5d21369af8bf3c16f))

### Documentation

- Create 'getting started' instructions
  ([#256](https://github.com/python-semantic-release/python-semantic-release/pull/256),
  [`5f4d000`](https://github.com/python-semantic-release/python-semantic-release/commit/5f4d000c3f153d1d23128acf577e389ae879466e))

- Link to getting started guide in README
  ([`f490e01`](https://github.com/python-semantic-release/python-semantic-release/commit/f490e0194fa818db4d38c185bc5e6245bfde546b))


## v7.2.2 (2020-07-26)

### Bug Fixes

- **changelog**: Send changelog to stdout
  ([`87e2bb8`](https://github.com/python-semantic-release/python-semantic-release/commit/87e2bb881387ff3ac245ab9923347a5a616e197b))

Fixes #250

### Documentation

- Add quotation marks to the pip commands in CONTRIBUTING.rst
  ([#253](https://github.com/python-semantic-release/python-semantic-release/pull/253),
  [`e20fa43`](https://github.com/python-semantic-release/python-semantic-release/commit/e20fa43098c06f5f585c81b9cd7e287dcce3fb5d))


## v7.2.1 (2020-06-29)

### Bug Fixes

- Commit all files with bumped versions
  ([#249](https://github.com/python-semantic-release/python-semantic-release/pull/249),
  [`b3a1766`](https://github.com/python-semantic-release/python-semantic-release/commit/b3a1766be7edb7d2eb76f2726d35ab8298688b3b))

### Documentation

- Give example of multiple build commands
  ([#248](https://github.com/python-semantic-release/python-semantic-release/pull/248),
  [`65f1ffc`](https://github.com/python-semantic-release/python-semantic-release/commit/65f1ffcc6cac3bf382f4b821ff2be59d04f9f867))

I had a little trouble figuring out how to use a non-setup.py build command, so I thought it would
  be helpful to update the docs with an example of how to do this.


## v7.2.0 (2020-06-15)

### Features

- Bump versions in multiple files
  ([#246](https://github.com/python-semantic-release/python-semantic-release/pull/246),
  [`0ba2c47`](https://github.com/python-semantic-release/python-semantic-release/commit/0ba2c473c6e44cc326b3299b6ea3ddde833bdb37))

- Add the `version_pattern` setting, which allows version numbers to be identified using arbitrary
  regular expressions. - Refactor the config system to allow non-string data types to be specified
  in `pyproject.toml`. - Multiple files can now be specified by setting `version_variable` or
  `version_pattern` to a list in `pyproject.toml`.

Fixes #175


## v7.1.1 (2020-05-28)

### Bug Fixes

- **changelog**: Swap sha and message in table changelog
  ([`6741370`](https://github.com/python-semantic-release/python-semantic-release/commit/6741370ab09b1706ff6e19b9fbe57b4bddefc70d))


## v7.1.0 (2020-05-24)

### Features

- **changelog**: Add changelog_table component
  ([#242](https://github.com/python-semantic-release/python-semantic-release/pull/242),
  [`fe6a7e7`](https://github.com/python-semantic-release/python-semantic-release/commit/fe6a7e7fa014ffb827a1430dbcc10d1fc84c886b))

Add an alternative changelog component which displays each section as a row in a table.

Fixes #237


## v7.0.0 (2020-05-22)

### Documentation

- Add conda-forge badge
  ([`e9536bb`](https://github.com/python-semantic-release/python-semantic-release/commit/e9536bbe119c9e3b90c61130c02468e0e1f14141))

### Features

- **changelog**: Add changelog components
  ([#240](https://github.com/python-semantic-release/python-semantic-release/pull/240),
  [`3e17a98`](https://github.com/python-semantic-release/python-semantic-release/commit/3e17a98d7fa8468868a87e62651ac2c010067711))

* feat(changelog): add changelog components

Add the ability to configure sections of the changelog using a `changelog_components` option.
  Component outputs are separated by a blank line and appear in the same order as they were
  configured.

It is possible to create your own custom components. Each component is a function which returns
  either some text to be added, or None in which case it will be skipped.

BREAKING CHANGE: The `compare_url` option has been removed in favor of using `changelog_components`.
  This functionality is now available as the `semantic_release.changelog.compare_url` component.

* docs: add documentation for changelog_components

* feat: pass changelog_sections to components

Changelog components may now receive the value of `changelog_sections`, split and ready to use.

### BREAKING CHANGES

- **changelog**: The `compare_url` option has been removed in favor of using `changelog_components`.
  This functionality is now available as the `semantic_release.changelog.compare_url` component.


## v6.4.1 (2020-05-15)

### Bug Fixes

- Convert \r\n to \n in commit messages
  ([`34acbbc`](https://github.com/python-semantic-release/python-semantic-release/commit/34acbbcd25320a9d18dcd1a4f43e1ce1837b2c9f))

Fixes #239


## v6.4.0 (2020-05-15)

### Features

- **history**: Create emoji parser
  ([#238](https://github.com/python-semantic-release/python-semantic-release/pull/238),
  [`2e1c50a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e1c50a865628b372f48945a039a3edb38a7cdf0))

Add a commit parser which uses emojis from https://gitmoji.carloscuesta.me/ to determine the type of
  change.

* fix: add emojis to default changelog_sections

* fix: include all parsed types in changelog

This allows emojis to appear in the changelog, as well as configuring other types to appear with the
  Angular parser (I remember someone asking for that feature a while ago). All filtering is now done
  in the markdown_changelog function.

* refactor(history): get breaking changes in parser

Move the task of detecting breaking change descriptions into the commit parser function, instead of
  during changelog generation.

This has allowed the emoji parser to also return the regular descriptions as breaking change
  descriptions for commits with :boom:.

BREAKING CHANGE: Custom commit parser functions are now required to pass a fifth argument to
  `ParsedCommit`, which is a list of breaking change descriptions.

* docs: add documentation for emoji parser

### BREAKING CHANGES

- **history**: Custom commit parser functions are now required to pass a fifth argument to
  `ParsedCommit`, which is a list of breaking change descriptions.


## v6.3.1 (2020-05-11)

### Bug Fixes

- Use getboolean for commit_version_number
  ([`a60e0b4`](https://github.com/python-semantic-release/python-semantic-release/commit/a60e0b4e3cadf310c3e0ad67ebeb4e69d0ee50cb))

Fixes #186


## v6.3.0 (2020-05-09)

### Documentation

- Document compare_link option
  ([`e52c355`](https://github.com/python-semantic-release/python-semantic-release/commit/e52c355c0d742ddd2cfa65d42888296942e5bec5))

- Rewrite commit-log-parsing.rst
  ([`4c70f4f`](https://github.com/python-semantic-release/python-semantic-release/commit/4c70f4f2aa3343c966d1b7ab8566fcc782242ab9))

### Features

- **history**: Support linking compare page in changelog
  ([`79a8e02`](https://github.com/python-semantic-release/python-semantic-release/commit/79a8e02df82fbc2acecaad9e9ff7368e61df3e54))

Fixes #218


## v6.2.0 (2020-05-02)

### Documentation

- Add = to verbosity option
  ([`a0f4c9c`](https://github.com/python-semantic-release/python-semantic-release/commit/a0f4c9cd397fcb98f880097319c08160adb3c3e6))

Fixes #227

- Use references where possible
  ([`f38e5d4`](https://github.com/python-semantic-release/python-semantic-release/commit/f38e5d4a1597cddb69ce47a4d79b8774e796bf41))

Fixes #221

### Features

- **history**: Check all paragraphs for breaking changes
  ([`fec08f0`](https://github.com/python-semantic-release/python-semantic-release/commit/fec08f0dbd7ae15f95ca9c41a02c9fe6d448ede0))

Check each paragraph of the commit's description for breaking changes, instead of only a body and
  footer. This ensures that breaking changes are detected when squashing commits together.

Fixes #200


## v6.1.0 (2020-04-26)

### Documentation

- Add documentation for PYPI_TOKEN
  ([`a8263a0`](https://github.com/python-semantic-release/python-semantic-release/commit/a8263a066177d1d42f2844e4cb42a76a23588500))

### Features

- **actions**: Support PYPI_TOKEN on GitHub Actions
  ([`df2c080`](https://github.com/python-semantic-release/python-semantic-release/commit/df2c0806f0a92186e914cfc8cc992171d74422df))

Add support for the new PYPI_TOKEN environment variable to be used on GitHub Actions.

- **pypi**: Support easier use of API tokens
  ([`bac135c`](https://github.com/python-semantic-release/python-semantic-release/commit/bac135c0ae7a6053ecfc7cdf2942c3c89640debf))

Allow setting the environment variable PYPI_TOKEN to automatically fill the username as __token__.

Fixes #213


## v6.0.1 (2020-04-15)

### Bug Fixes

- **hvcs**: Convert get_hvcs to use LoggedFunction
  ([`3084249`](https://github.com/python-semantic-release/python-semantic-release/commit/308424933fd3375ca3730d9eaf8abbad2435830b))

This was missed in 213530fb0c914e274b81d1dacf38ea7322b5b91f


## v6.0.0 (2020-04-15)

### Documentation

- Create Read the Docs config file
  ([`aa5a1b7`](https://github.com/python-semantic-release/python-semantic-release/commit/aa5a1b700a1c461c81c6434686cb6f0504c4bece))

- Include README.rst in index.rst
  ([`8673a9d`](https://github.com/python-semantic-release/python-semantic-release/commit/8673a9d92a9bf348bb3409e002a830741396c8ca))

These files were very similar so it makes sense to simply include one inside the other.

- Move action.rst into main documentation
  ([`509ccaf`](https://github.com/python-semantic-release/python-semantic-release/commit/509ccaf307a0998eced69ad9fee1807132babe28))

- Rewrite README.rst
  ([`e049772`](https://github.com/python-semantic-release/python-semantic-release/commit/e049772cf14cdd49538cf357db467f0bf3fe9587))

- Rewrite troubleshooting page
  ([`0285de2`](https://github.com/python-semantic-release/python-semantic-release/commit/0285de215a8dac3fcc9a51f555fa45d476a56dff))

### Refactoring

- **debug**: Use logging and click_log instead of ndebug
  ([`15b1f65`](https://github.com/python-semantic-release/python-semantic-release/commit/15b1f650f29761e1ab2a91b767cbff79b2057a4c))

BREAKING CHANGE: `DEBUG="*"` no longer has an effect, instead use `--verbosity DEBUG`.

### BREAKING CHANGES

- **debug**: `debug="*"` no longer has an effect, instead use `--verbosity DEBUG`.


## v5.2.0 (2020-04-09)

### Documentation

- Automate API docs
  ([`7d4fea2`](https://github.com/python-semantic-release/python-semantic-release/commit/7d4fea266cc75007de51609131eb6d1e324da608))

Automatically create pages in the API docs section using sphinx-autodoc. This is added as an event
  handler in conf.py.

### Features

- **github**: Add tag as default release name
  ([`2997908`](https://github.com/python-semantic-release/python-semantic-release/commit/2997908f80f4fcec56917d237a079b961a06f990))


## v5.1.0 (2020-04-04)

### Documentation

- Improve formatting of configuration page
  ([`9a8e22e`](https://github.com/python-semantic-release/python-semantic-release/commit/9a8e22e838d7dbf3bfd941397c3b39560aca6451))

- Improve formatting of envvars page
  ([`b376a56`](https://github.com/python-semantic-release/python-semantic-release/commit/b376a567bfd407a507ce0752614b0ca75a0f2973))

- Update index.rst
  ([`b27c26c`](https://github.com/python-semantic-release/python-semantic-release/commit/b27c26c66e7e41843ab29076f7e724908091b46e))

### Features

- **history**: Allow customizing changelog_sections
  ([#207](https://github.com/python-semantic-release/python-semantic-release/pull/207),
  [`d5803d5`](https://github.com/python-semantic-release/python-semantic-release/commit/d5803d5c1668d86482a31ac0853bac7ecfdc63bc))


## v5.0.3 (2020-03-26)

### Bug Fixes

- Bump dependencies and fix Windows issues on Development
  ([#173](https://github.com/python-semantic-release/python-semantic-release/pull/173),
  [`0a6f8c3`](https://github.com/python-semantic-release/python-semantic-release/commit/0a6f8c3842b05f5f424dad5ce1fa5e3823c7e688))

* Bump dependencies and fix windows issues

* Correctly pass temp dir to test settings

* Remove print call on test settings

* chore: remove py34 and py35 classifiers

* chore: bump twine, requests and python-gitlab

* chore: update tox config to be more granular

* fix: missing mime types on Windows

* chore: bump circleCI and tox python to 3.8

* chore: remove py36 from tox envlist

* chore: isort errors


## v5.0.2 (2020-03-22)

### Bug Fixes

- **history**: Leave case of other characters unchanged
  ([`96ba94c`](https://github.com/python-semantic-release/python-semantic-release/commit/96ba94c4b4593997343ec61ecb6c823c1494d0e2))

Previously, use of str.capitalize() would capitalize the first letter as expected, but all
  subsequent letters became lowercase. Now, the other letters remain unchanged.


## v5.0.1 (2020-03-22)

### Bug Fixes

- Make action use current version of semantic-release
  ([`123984d`](https://github.com/python-semantic-release/python-semantic-release/commit/123984d735181c622f3d99088a1ad91321192a11))

This gives two benefits: * In this repo it will work as a smoketest * In other repos when they
  specify version int the github workflow they will get the version they specify.


## v5.0.0 (2020-03-22)

### Bug Fixes

- Rename default of build_command config
  ([`d5db22f`](https://github.com/python-semantic-release/python-semantic-release/commit/d5db22f9f7acd05d20fd60a8b4b5a35d4bbfabb8))

### Documentation

- **pypi**: Update docstings in pypi.py
  ([`6502d44`](https://github.com/python-semantic-release/python-semantic-release/commit/6502d448fa65e5dc100e32595e83fff6f62a881a))

### Features

- **build**: Allow config setting for build command
  ([#195](https://github.com/python-semantic-release/python-semantic-release/pull/195),
  [`740f4bd`](https://github.com/python-semantic-release/python-semantic-release/commit/740f4bdb26569362acfc80f7e862fc2c750a46dd))

* feat(build): allow config setting for build command

BREAKING CHANGE: Previously the build_commands configuration variable set the types of bundles sent
  to `python setup.py`. It has been replaced by the configuration variable `build_command` which
  takes the full command e.g. `python setup.py sdist` or `poetry build`.

Closes #188

### BREAKING CHANGES

- **build**: Previously the build_commands configuration variable set the types of bundles sent to
  `python setup.py`. It has been replaced by the configuration variable `build_command` which takes
  the full command e.g. `python setup.py sdist` or `poetry build`.


## v4.11.0 (2020-03-22)

### Documentation

- Make AUTHORS.rst dynamic
  ([`db2e076`](https://github.com/python-semantic-release/python-semantic-release/commit/db2e0762f3189d0f1a6ba29aad32bdefb7e0187f))

- **readme**: Fix minor typo
  ([`c22f69f`](https://github.com/python-semantic-release/python-semantic-release/commit/c22f69f62a215ff65e1ab6dcaa8e7e9662692e64))

### Features

- **actions**: Create GitHub Action
  ([`350245d`](https://github.com/python-semantic-release/python-semantic-release/commit/350245dbfb07ed6a1db017b1d9d1072b368b1497))


## v4.10.0 (2020-03-03)

### Features

- Make commit message configurable
  ([#184](https://github.com/python-semantic-release/python-semantic-release/pull/184),
  [`eb0762c`](https://github.com/python-semantic-release/python-semantic-release/commit/eb0762ca9fea5cecd5c7b182504912a629be473b))


## v4.9.0 (2020-03-02)

### Bug Fixes

- **pypi**: Change bdist_wheels to bdist_wheel
  ([`c4db509`](https://github.com/python-semantic-release/python-semantic-release/commit/c4db50926c03f3d551c8331932c567c7bdaf4f3d))

Change the incorrect command bdist_wheels to bdist_wheel.

### Features

- **pypi**: Add build_commands config
  ([`22146ea`](https://github.com/python-semantic-release/python-semantic-release/commit/22146ea4b94466a90d60b94db4cc65f46da19197))

Add a config option to set the commands passed to setup.py when building distributions. This allows
  for things like adding custom commands to the build process.


## v4.8.0 (2020-02-28)

### Features

- **git**: Add a new config for commit author
  ([`aa2c22c`](https://github.com/python-semantic-release/python-semantic-release/commit/aa2c22c469448fe57f02bea67a02f998ce519ac3))


## v4.7.1 (2020-02-28)

### Bug Fixes

- Repair parsing of remotes in the gitlab ci format
  ([`0fddbe2`](https://github.com/python-semantic-release/python-semantic-release/commit/0fddbe2fb70d24c09ceddb789a159162a45942dc))

Format is: "https://gitlab-ci-token:MySuperToken@gitlab.example.com/group/project.git"

Problem was due to the regex modification for #179

Fixes #181


## v4.7.0 (2020-02-28)

### Bug Fixes

- Support repository owner names containing dots
  ([`a6c4da4`](https://github.com/python-semantic-release/python-semantic-release/commit/a6c4da4c0e6bd8a37f64544f7813fa027f5054ed))

Fixes #179

- **github**: Use application/octet-stream for .whl files
  ([`90a7e47`](https://github.com/python-semantic-release/python-semantic-release/commit/90a7e476a04d26babc88002e9035cad2ed485b07))

application/octet-stream is more generic, but it is better than using a non-official MIME type.

### Features

- Upload distribution files to GitHub Releases
  ([#177](https://github.com/python-semantic-release/python-semantic-release/pull/177),
  [`e427658`](https://github.com/python-semantic-release/python-semantic-release/commit/e427658e33abf518191498c3142a0f18d3150e07))

* refactor(github): create upload_asset function

Create a function to call the asset upload API. This will soon be used to upload assets specified by
  the user.

* refactor(github): infer Content-Type from file extension

Infer the Content-Type header based on the file extension instead of setting it manually.

* refactor(pypi): move building of dists to cli.py

Refactor to have the building/removal of distributions in cli.py instead of within the
  upload_to_pypi function. This makes way for uploading to other locations, such as GitHub Releases,
  too.

* feat(github): upload dists to release

Upload Python wheels to the GitHub release. Configured with the option upload_to_release, on by
  default if using GitHub.

* docs: document upload_to_release config option

* test(github): add tests for Github.upload_dists

* fix(github): fix upload of .whl files

Fix uploading of .whl files due to a missing MIME type (defined custom type as
  application/x-wheel+zip). Additionally, continue with other uploads even if one fails.

* refactor(cli): additional output during publish

Add some additional output during the publish command.

* refactor(github): move api calls to separate methods

Move each type of GitHub API request into its own method to improve readability.

Re-implementation of #172

* fix: post changelog after PyPI upload

Post the changelog in-between uploading to PyPI and uploading to GitHub Releases. This is so that if
  the PyPI upload fails, GitHub users will not be notified. GitHub uploads still need to be
  processed after creating the changelog as the release notes must be published to upload assets to
  them.


## v4.6.0 (2020-02-19)

### Bug Fixes

- Add more debug statements in logs
  ([`bc931ec`](https://github.com/python-semantic-release/python-semantic-release/commit/bc931ec46795fde4c1ccee004eec83bf73d5de7a))

- Only overwrite with patch if bump is None
  ([`1daa4e2`](https://github.com/python-semantic-release/python-semantic-release/commit/1daa4e23ec2dd40c6b490849276524264787e24e))

Fixes #159

### Features

- **history**: Capitalize changelog messages
  ([`1a8e306`](https://github.com/python-semantic-release/python-semantic-release/commit/1a8e3060b8f6d6362c27903dcfc69d17db5f1d36))

Capitalize the first letter of messages in the changelog regardless of whether they are capitalized
  in the commit itself.


## v4.5.1 (2020-02-16)

### Bug Fixes

- **github**: Send token in request header
  ([`be9972a`](https://github.com/python-semantic-release/python-semantic-release/commit/be9972a7b1fb183f738fb31bd370adb30281e4d5))

Use an Authorization header instead of deprecated query parameter authorization.

Fixes relekang/python-semantic-release#167

### Documentation

- Add note about automatic releases in readme
  ([`e606e75`](https://github.com/python-semantic-release/python-semantic-release/commit/e606e7583a30167cf7679c6bcada2f9e768b3abe))

- Fix broken list in readme
  ([`7aa572b`](https://github.com/python-semantic-release/python-semantic-release/commit/7aa572b2a323ddbc69686309226395f40c52b469))

Fix the syntax of a broken bullet-point list in README.rst.

- Update readme and getting started docs
  ([`07b3208`](https://github.com/python-semantic-release/python-semantic-release/commit/07b3208ff64301e544c4fdcb48314e49078fc479))


## v4.5.0 (2020-02-08)

### Bug Fixes

- Remove erroneous submodule
  ([`762bfda`](https://github.com/python-semantic-release/python-semantic-release/commit/762bfda728c266b8cd14671d8da9298fc99c63fb))

- **cli**: --noop flag works when before command
  ([`4fcc781`](https://github.com/python-semantic-release/python-semantic-release/commit/4fcc781d1a3f9235db552f0f4431c9f5e638d298))

The entry point of the app is changed from main() to entry(). Entry takes any arguments before
  commands and moves them to after commands, then calls main()

Closes #73

### Features

- **history**: Enable colon defined version
  ([`7837f50`](https://github.com/python-semantic-release/python-semantic-release/commit/7837f5036269328ef29996b9ea63cccd5a6bc2d5))

The get_current_version_by_config_file and the replace_version_string methods now check for both
  variables defined as "variable= version" and "variable: version" This allows for using a yaml file
  to store the version.

Closes #165


## v4.4.1 (2020-01-18)

### Bug Fixes

- Add quotes around twine arguments
  ([`46a83a9`](https://github.com/python-semantic-release/python-semantic-release/commit/46a83a94b17c09d8f686c3ae7b199d7fd0e0e5e5))

Fixes #163


## v4.4.0 (2020-01-17)

### Bug Fixes

- **github**: Add check for GITHUB_ACTOR for git push
  ([#162](https://github.com/python-semantic-release/python-semantic-release/pull/162),
  [`c41e9bb`](https://github.com/python-semantic-release/python-semantic-release/commit/c41e9bb986d01b92d58419cbdc88489d630a11f1))

### Features

- **parser**: Add support for exclamation point for breaking changes
  ([`a4f8a10`](https://github.com/python-semantic-release/python-semantic-release/commit/a4f8a10afcc358a8fbef83be2041129480350be2))

According to the documentation for conventional commits, breaking changes can be described using
  exclamation points, just before the colon between type/scope and subject. In that case, the
  breaking change footer is optional, and the subject is used as description of the breaking change.
  If the footer exists, it is used for the description.

Fixes #156

- **parser**: Make BREAKING-CHANGE synonymous with BREAKING CHANGE
  ([`beedccf`](https://github.com/python-semantic-release/python-semantic-release/commit/beedccfddfb360aeebef595342ee980446012ec7))

According to point 16 in the conventional commit specification, this should be implemented. They
  especially mention the footer, but I kept the body for backwards compatibility. This should
  probably be removed one day. The regex is in the helpers to make it easier to re-use, but I didn't
  updated parser_tag since it looks like a legacy parser.


## v4.3.4 (2019-12-17)

### Bug Fixes

- Fallback to whole log if correct tag is not available
  ([#157](https://github.com/python-semantic-release/python-semantic-release/pull/157),
  [`252bffd`](https://github.com/python-semantic-release/python-semantic-release/commit/252bffd3be7b6dfcfdb384d24cb1cd83d990fc9a))

The method getting all commits to consider for the release will now test whether the version in
  input is a valid reference. If it is not, it will consider the whole log for the repository.

evaluate_version_bump will still consider a message starting with the version number as a breaking
  condition to stop analyzing.

Fixes #51


## v4.3.3 (2019-11-06)

### Bug Fixes

- Set version of click to >=2.0,<8.0.
  ([#155](https://github.com/python-semantic-release/python-semantic-release/pull/155),
  [`f07c7f6`](https://github.com/python-semantic-release/python-semantic-release/commit/f07c7f653be1c018e443f071d9a196d9293e9521))

* fix: Upgrade to click 7.0.

Fixes #117

* fix: Instead of requiring click 7.0, looks like all tests will pass with at least 2.0.

* Upstream is at ~=7.0, so let's set the range to less than 8.0.

* The string template has no variables, so remove the call to .format()


## v4.3.2 (2019-10-05)

### Bug Fixes

- Update regex to get repository owner and name for project with dots
  ([`2778e31`](https://github.com/python-semantic-release/python-semantic-release/commit/2778e316a0c0aa931b1012cb3862d04659c05e73))

Remove the dot from the second capture group to allow project names containing dots to be matched.
  Instead of a greedy '+' operator, use '*?' to allow the second group to give back the '.git' (to
  avoid including it in the project name)

Fixes #151


## v4.3.1 (2019-09-29)

### Bug Fixes

- Support repo urls without git terminator
  ([`700e9f1`](https://github.com/python-semantic-release/python-semantic-release/commit/700e9f18dafde1833f482272a72bb80b54d56bb3))


## v4.3.0 (2019-09-06)

### Bug Fixes

- Manage subgroups in git remote url
  ([`4b11875`](https://github.com/python-semantic-release/python-semantic-release/commit/4b118754729094e330389712cf863e1c6cefee69))

This is a necessary fix for gitlab integration. For an illustration of the need and use for this
  fix, test was edited.

Fixes #139 Fixes #140

- Update list of commit types to include build, ci and perf
  ([`41ea12f`](https://github.com/python-semantic-release/python-semantic-release/commit/41ea12fa91f97c0046178806bce3be57c3bc2308))

Also added perf to the types that trigger a patch update

Fixes #145

### Features

- Add the possibility to load configuration from pyproject.toml
  ([`35f8bfe`](https://github.com/python-semantic-release/python-semantic-release/commit/35f8bfef443c8b69560c918f4b13bc766fb3daa2))

Adds the toml library to base requirements. Also adds the related tests and documentation. Also adds
  the description of the version_source configuration option

Relates to #119

- Allow the override of configuration options from cli
  ([`f0ac82f`](https://github.com/python-semantic-release/python-semantic-release/commit/f0ac82fe59eb59a768a73a1bf2ea934b9d448c58))

config can now be overriden with the "-D" flag. Also adds the related tests and documentation.

Also introduces a fixture in tests/__init__.py that reloads module using config. It is necessary
  since all tests run in the same environment. A better way would be to box the execution of tests
  (using the --forked option of pytest for example) but it does not work in non-unix systems. Also
  some tests should not break if config is changed, but it is outside of the scope of this issue.

Fixes #119

- Allow users to get version from tag and write/commit bump to file
  ([`1f9fe1c`](https://github.com/python-semantic-release/python-semantic-release/commit/1f9fe1cc7666d47cc0c348c4705b63c39bf10ecc))

Before this commit, version was bumped in the file, but only committed if version was obtained from
  `version_variable` (version_source == `commit`). Also added a relevant test and a description for
  this new option.

Fixes #104

- Make the vcs functionalities work with gitlab
  ([`82d555d`](https://github.com/python-semantic-release/python-semantic-release/commit/82d555d45b9d9e295ef3f9546a6ca2a38ca4522e))

Adds python-gitlab as requirement. Refactored github specific methods while keeping default
  behavior. Also removed an unused return value for post_release_changelog. Also refactored the
  secret filtering method. Updated the related tests.

Fixes #121


## v4.2.0 (2019-08-05)

### Bug Fixes

- Add commit hash when generating breaking changes
  ([`0c74faf`](https://github.com/python-semantic-release/python-semantic-release/commit/0c74fafdfa81cf2e13db8f4dcf0a6f7347552504))

Fixes #120

- Kept setting new version for tag source
  ([`0e24a56`](https://github.com/python-semantic-release/python-semantic-release/commit/0e24a5633f8f94b48da97b011634d4f9d84f7b4b))

- Remove deletion of build folder
  ([`b45703d`](https://github.com/python-semantic-release/python-semantic-release/commit/b45703dad38c29b28575060b21e5fb0f8482c6b1))

Fixes #115

- Updated the tag tests
  ([`3303eef`](https://github.com/python-semantic-release/python-semantic-release/commit/3303eefa49a0474bbd85df10ae186ccbf9090ec1))

- Upgrade click to 7.0
  ([`2c5dd80`](https://github.com/python-semantic-release/python-semantic-release/commit/2c5dd809b84c2157a5e6cdcc773c43ec864f0328))

### Features

- Add configuration to customize handling of dists
  ([`2af6f41`](https://github.com/python-semantic-release/python-semantic-release/commit/2af6f41b21205bdd192514a434fca2feba17725a))

Relates to #115

- Add support for configuring branch
  ([`14abb05`](https://github.com/python-semantic-release/python-semantic-release/commit/14abb05e7f878e88002f896812d66b4ea5c219d4))

Fixes #43

- Add support for showing unreleased changelog
  ([`41ef794`](https://github.com/python-semantic-release/python-semantic-release/commit/41ef7947ad8a07392c96c7540980476e989c1d83))

Fixes #134


## v4.1.2 (2019-08-04)

### Bug Fixes

- Correct isort build fail
  ([`0037210`](https://github.com/python-semantic-release/python-semantic-release/commit/00372100b527ff9308d9e43fe5c65cdf179dc4dc))

build fail: https://circleci.com/gh/relekang/python-semantic-release/379

- Make sure the history only breaks loop for version commit
  ([`5dc6cfc`](https://github.com/python-semantic-release/python-semantic-release/commit/5dc6cfc634254f09997bb3cb0f17abd296e2c01f))

Fixes #135

- **vcs**: Allow cli to be run from subdirectory
  ([`fb7bb14`](https://github.com/python-semantic-release/python-semantic-release/commit/fb7bb14300e483626464795b8ff4f033a194cf6f))

### Documentation

- **circleci**: Point badge to master branch
  ([`9c7302e`](https://github.com/python-semantic-release/python-semantic-release/commit/9c7302e184a1bd88f39b3039691b55cd77f0bb07))


## v4.1.1 (2019-02-15)

### Documentation

- Correct usage of changelog
  ([`f4f59b0`](https://github.com/python-semantic-release/python-semantic-release/commit/f4f59b08c73700c6ee04930221bfcb1355cbc48d))

- Debug usage and related
  ([`f08e594`](https://github.com/python-semantic-release/python-semantic-release/commit/f08e5943a9876f2d17a7c02f468720995c7d9ffd))

Debug functionality lack documentation. Thoubleshooting is helped by documenting other environment
  variables as well.

- Describing the commands
  ([`b6fa04d`](https://github.com/python-semantic-release/python-semantic-release/commit/b6fa04db3044525a1ee1b5952fb175a706842238))

The commands is lacking from the documentation.

- Update url for commit guidelinesThe guidelines can now be found in theDEVELOPERS.md in angular.
  ([`90c1b21`](https://github.com/python-semantic-release/python-semantic-release/commit/90c1b217f86263301b91d19d641c7b348e37d960))


## v4.1.0 (2019-01-31)

### Bug Fixes

- Initialize git Repo from current folder
  ([`c7415e6`](https://github.com/python-semantic-release/python-semantic-release/commit/c7415e634c0affbe6396e0aa2bafe7c1b3368914))

This allows to run the program also from inner repository folders

- Maintain version variable formatting on bump
  ([#103](https://github.com/python-semantic-release/python-semantic-release/pull/103),
  [`bf63156`](https://github.com/python-semantic-release/python-semantic-release/commit/bf63156f60340614fae94c255fb2f097cf317b2b))

Small change to the way the version is written to the config file it is read from. This allows the
  formatting to be the same as before semantic-release changed it.

Prior behavior `my_version_var="1.2.3"` => `my_version_var = '1.2.4'`

New behavior `my_version_var="1.2.3"` => `my_version_var="1.2.4"`

I am using python-semantic-release with a Julia project and this change will allow for consistent
  formatting in my Project.toml file where the version is maintained

- Use same changelog code for command as post
  ([`248f622`](https://github.com/python-semantic-release/python-semantic-release/commit/248f62283c59182868c43ff105a66d85c923a894))

See #27 for background.

### Documentation

- Add installation instructions for development
  ([#106](https://github.com/python-semantic-release/python-semantic-release/pull/106),
  [`9168d0e`](https://github.com/python-semantic-release/python-semantic-release/commit/9168d0ea56734319a5d77e890f23ff6ba51cc97d))

- **readme**: Add testing instructions
  ([`bb352f5`](https://github.com/python-semantic-release/python-semantic-release/commit/bb352f5b6616cc42c9f2f2487c51dedda1c68295))

### Features

- **ci_checks**: Add support for bitbucket
  ([`9fc120d`](https://github.com/python-semantic-release/python-semantic-release/commit/9fc120d1a7e4acbbca609628e72651685108b364))


## v4.0.1 (2019-01-12)

### Bug Fixes

- Add better error message when pypi credentials are empty
  ([`c4e5dcb`](https://github.com/python-semantic-release/python-semantic-release/commit/c4e5dcbeda0ce8f87d25faefb4d9ae3581029a8f))

Fixes #96

- Clean out dist and build before building
  ([`b628e46`](https://github.com/python-semantic-release/python-semantic-release/commit/b628e466f86bc27cbe45ec27a02d4774a0efd3bb))

This should fix the problem with uploading old versions.

Fixes #86

- Filter out pypi secrets from exceptions
  ([`5918371`](https://github.com/python-semantic-release/python-semantic-release/commit/5918371c1e82b06606087c9945d8eaf2604a0578))

Fixes #41

- Unfreeze dependencies
  ([`847833b`](https://github.com/python-semantic-release/python-semantic-release/commit/847833bf48352a4935f906d0c3f75e1db596ca1c))

This uses ~= for most dependencies instead of pinning them.

Fixes #100

- Use correct syntax to exclude tests in package
  ([`3e41e91`](https://github.com/python-semantic-release/python-semantic-release/commit/3e41e91c318663085cd28c8165ece21d7e383475))

This implements #92 without deleting __init__.py files.

- **parser_angular**: Fix non-match when special chars in scope
  ([`8a33123`](https://github.com/python-semantic-release/python-semantic-release/commit/8a331232621b26767e4268079f9295bf695047ab))

### Documentation

- Remove reference to gitter
  ([`896e37b`](https://github.com/python-semantic-release/python-semantic-release/commit/896e37b95cc43218e8f593325dd4ea63f8b895d9))

Fixes #90


## v4.0.0 (2018-11-22)

### Bug Fixes

- Add check of credentials
  ([`7d945d4`](https://github.com/python-semantic-release/python-semantic-release/commit/7d945d44b36b3e8c0b7771570cb2305e9e09d0b2))

- Add credentials check
  ([`0694604`](https://github.com/python-semantic-release/python-semantic-release/commit/0694604f3b3d2159a4037620605ded09236cdef5))

- Add dists to twine call
  ([`1cec2df`](https://github.com/python-semantic-release/python-semantic-release/commit/1cec2df8bcb7f877c813d6470d454244630b050a))

- Change requests from fixed version to version range
  ([#93](https://github.com/python-semantic-release/python-semantic-release/pull/93),
  [`af3ad59`](https://github.com/python-semantic-release/python-semantic-release/commit/af3ad59f018876e11cc3acdda0b149f8dd5606bd))

* Change requests version to be more flexible to aid in using this with dev requirements for a
  release.

* revert changes to vcs helpers

- Re-add skip-existing
  ([`366e9c1`](https://github.com/python-semantic-release/python-semantic-release/commit/366e9c1d0b9ffcde755407a1de18e8295f6ad3a1))

- Remove repository argument in twine
  ([`e24543b`](https://github.com/python-semantic-release/python-semantic-release/commit/e24543b96adb208897f4ce3eaab96b2f4df13106))

- Remove support for python 2
  ([`85fe638`](https://github.com/python-semantic-release/python-semantic-release/commit/85fe6384c15db317bc7142f4c8bbf2da58cece58))

BREAKING CHANGE: This will only work with python 3 after this commit.

- Remove universal from setup config
  ([`18b2402`](https://github.com/python-semantic-release/python-semantic-release/commit/18b24025e397aace03dd5bb9eed46cfdd13491bd))

- Update twine
  ([`c4ae7b8`](https://github.com/python-semantic-release/python-semantic-release/commit/c4ae7b8ecc682855a8568b247690eaebe62d2d26))

- Use new interface for twine
  ([`c04872d`](https://github.com/python-semantic-release/python-semantic-release/commit/c04872d00a26e9bf0f48eeacb360b37ce0fba01e))

- Use twine through cli call
  ([`ab84beb`](https://github.com/python-semantic-release/python-semantic-release/commit/ab84beb8f809e39ae35cd3ce5c15df698d8712fd))

### Documentation

- Add type hints and more complete docstrings
  ([`a6d5e9b`](https://github.com/python-semantic-release/python-semantic-release/commit/a6d5e9b1ccbe75d59e7240528593978a19d8d040))

Includes a few style changes suggested by pylint and type safety checks suggested by mypy

re #81

- Fix typo in documentation index
  ([`da6844b`](https://github.com/python-semantic-release/python-semantic-release/commit/da6844bce0070a0020bf13950bd136fe28262602))

The word role -- 'an actor's part in a play, movie, etc.' does not fit in this context. "ready to
  roll" is a phrase meaning "fully prepared to start functioning or moving" or simply "ready". I
  believe this is what was meant to be written.

### Features

- Add support for commit_message config variable
  ([`4de5400`](https://github.com/python-semantic-release/python-semantic-release/commit/4de540011ab10483ee1865f99c623526cf961bb9))

This variable can allow you to skip CI pipelines in CI tools like GitLab CI by adding [CI skip] in
  the body. There are likely many uses for this beyond that particular example...

BREAKING CHANGE: If you rely on the commit message to be the version number only, this will break
  your code

re #88 #32

- **CI checks**: Add support for GitLab CI checks
  ([`8df5e2b`](https://github.com/python-semantic-release/python-semantic-release/commit/8df5e2bdd33a620e683f3adabe174e94ceaa88d9))

Check `GITLAB_CI` environment variable and then verify `CI_COMMIT_REF_NAME` matches the given
  branch.

Includes tests

Closes #88 re #32

### BREAKING CHANGES

- If you rely on the commit message to be the version number only, this will break your code


## v3.11.2 (2018-06-10)

### Bug Fixes

- Upgrade twine
  ([`9722313`](https://github.com/python-semantic-release/python-semantic-release/commit/9722313eb63c7e2c32c084ad31bed7ee1c48a928))


## v3.11.1 (2018-06-06)

### Bug Fixes

- Change Gitpython version number
  ([`23c9d4b`](https://github.com/python-semantic-release/python-semantic-release/commit/23c9d4b6a1716e65605ed985881452898d5cf644))

Change the Gitpython version number to fix a bug described in #80.

### Documentation

- Add retry option to cli docs
  ([`021da50`](https://github.com/python-semantic-release/python-semantic-release/commit/021da5001934f3199c98d7cf29f62a3ad8c2e56a))


## v3.11.0 (2018-04-12)

### Bug Fixes

- Add pytest cache to gitignore
  ([`b8efd5a`](https://github.com/python-semantic-release/python-semantic-release/commit/b8efd5a6249c79c8378bffea3e245657e7094ec9))

- Make repo non if it is not a git repository
  ([`1dc306b`](https://github.com/python-semantic-release/python-semantic-release/commit/1dc306b9b1db2ac360211bdc61fd815302d0014c))

Fixes #74

### Documentation

- Remove old notes about trello board
  ([`7f50c52`](https://github.com/python-semantic-release/python-semantic-release/commit/7f50c521a522bb0c4579332766248778350e205b))

- Update status badges
  ([`cfa13b8`](https://github.com/python-semantic-release/python-semantic-release/commit/cfa13b8260e3f3b0bfcb395f828ad63c9c5e3ca5))

### Features

- Add --retry cli option
  ([#78](https://github.com/python-semantic-release/python-semantic-release/pull/78),
  [`3e312c0`](https://github.com/python-semantic-release/python-semantic-release/commit/3e312c0ce79a78d25016a3b294b772983cfb5e0f))

* Add --retry cli option * Post changelog correctly * Add comments * Add --retry to the docs

- Add support to finding previous version from tags if not using commit messages
  ([#68](https://github.com/python-semantic-release/python-semantic-release/pull/68),
  [`6786487`](https://github.com/python-semantic-release/python-semantic-release/commit/6786487ebf4ab481139ef9f43cd74e345debb334))

* feat: Be a bit more forgiving to find previous tags

Now grabs the previous version from tag names if it can't find it in the commit

* quantifiedcode and flake8 fixes

* Update cli.py

* Switch to ImproperConfigurationError


## v3.10.3 (2018-01-29)

### Bug Fixes

- Error when not in git repository
  ([#75](https://github.com/python-semantic-release/python-semantic-release/pull/75),
  [`251b190`](https://github.com/python-semantic-release/python-semantic-release/commit/251b190a2fd5df68892346926d447cbc1b32475a))

Fix an error when the program was run in a non-git repository. It would not allow the help options
  to be run.

issue #74


## v3.10.2 (2017-08-03)

### Bug Fixes

- Update call to upload to work with twine 1.9.1
  ([#72](https://github.com/python-semantic-release/python-semantic-release/pull/72),
  [`8f47643`](https://github.com/python-semantic-release/python-semantic-release/commit/8f47643c54996e06c358537115e7e17b77cb02ca))


## v3.10.1 (2017-07-22)

### Bug Fixes

- Update Twine ([#69](https://github.com/python-semantic-release/python-semantic-release/pull/69),
  [`9f268c3`](https://github.com/python-semantic-release/python-semantic-release/commit/9f268c373a932621771abbe9607b739b1e331409))

The publishing API is under development and older versions of Twine have problems to deal with newer
  versions of the API. Namely the logic of register/upload has changed (it was simplified).


## v3.10.0 (2017-05-05)

### Bug Fixes

- Make changelog problems not fail whole publish
  ([`b5a68cf`](https://github.com/python-semantic-release/python-semantic-release/commit/b5a68cf6177dc0ed80eda722605db064f3fe2062))

Can be fixed with changelog command later.

### Documentation

- Fix typo in cli.py docstring
  ([#64](https://github.com/python-semantic-release/python-semantic-release/pull/64),
  [`0d13985`](https://github.com/python-semantic-release/python-semantic-release/commit/0d139859cd71f2d483f4360f196d6ef7c8726c18))

### Features

- Add git hash to the changelog
  ([#65](https://github.com/python-semantic-release/python-semantic-release/pull/65),
  [`628170e`](https://github.com/python-semantic-release/python-semantic-release/commit/628170ebc440fc6abf094dd3e393f40576dedf9b))

* feat(*): add git hash to the changelog

Add git hash to the changelog to ease finding the specific commit. The hash now is also easily
  viewable in Github's tag. see #63 for more information.

* chore(test_history): fix test errors

Fix the test errors that would happen after the modification of get_commit_log.


## v3.9.0 (2016-07-03)

### Bug Fixes

- Can't get the proper last tag from commit history
  ([`5a0e681`](https://github.com/python-semantic-release/python-semantic-release/commit/5a0e681e256ec511cd6c6a8edfee9d905891da10))

repo.tags returns a list sorted by the name rather than date, fix it by sorting them before
  iteration

### Features

- Add option for choosing between versioning by commit or tag
  ([`c0cd1f5`](https://github.com/python-semantic-release/python-semantic-release/commit/c0cd1f5b2e0776d7b636c3dd9e5ae863125219e6))

default versioning behaviour is commiting

- Don't use file to track version, only tag to commit for versioning
  ([`cd25862`](https://github.com/python-semantic-release/python-semantic-release/commit/cd258623ee518c009ae921cd6bb3119dafae43dc))

- Get repo version from historical tags instead of config file
  ([`a45a9bf`](https://github.com/python-semantic-release/python-semantic-release/commit/a45a9bfb64538efeb7f6f42bb6e7ede86a4ddfa8))

repo version will get from historical tags. init 0.0.0 if fail of find any version tag


## v3.8.1 (2016-04-17)

### Bug Fixes

- Add search_parent_directories option to gitpython
  ([#62](https://github.com/python-semantic-release/python-semantic-release/pull/62),
  [`8bf9ce1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bf9ce11137399906f18bc8b25698b6e03a65034))


## v3.8.0 (2016-03-21)

### Bug Fixes

- Add git fetch to frigg after success
  ([`74a6cae`](https://github.com/python-semantic-release/python-semantic-release/commit/74a6cae2b46c5150e63136fde0599d98b9486e36))

- Make tag parser work correctly with breaking changes
  ([`9496f6a`](https://github.com/python-semantic-release/python-semantic-release/commit/9496f6a502c79ec3acb4e222e190e76264db02cf))

The tag parser did not work correctly, this went undiscovered for a while because the tests was not
  ran by pytest.

- Refactoring cli.py to improve --help and error messages
  ([`c79fc34`](https://github.com/python-semantic-release/python-semantic-release/commit/c79fc3469fb99bf4c7f52434fa9c0891bca757f9))

### Documentation

- Add info about correct commit guidelines
  ([`af35413`](https://github.com/python-semantic-release/python-semantic-release/commit/af35413fae80889e2c5fc6b7d28f77f34b3b4c02))

- Add info about trello board in readme
  ([`5229557`](https://github.com/python-semantic-release/python-semantic-release/commit/5229557099d76b3404ea3677292332442a57ae2e))

- Fix badges in readme
  ([`7f4e549`](https://github.com/python-semantic-release/python-semantic-release/commit/7f4e5493edb6b3fb3510d0bb78fcc8d23434837f))

- Update info about releases in contributing.md
  ([`466f046`](https://github.com/python-semantic-release/python-semantic-release/commit/466f0460774cad86e7e828ffb50c7d1332b64e7b))

### Features

- Add ci checks for circle ci
  ([`151d849`](https://github.com/python-semantic-release/python-semantic-release/commit/151d84964266c8dca206cef8912391cb73c8f206))


## v3.7.2 (2016-03-19)

### Bug Fixes

- Move code around a bit to make flake8 happy
  ([`41463b4`](https://github.com/python-semantic-release/python-semantic-release/commit/41463b49b5d44fd94c11ab6e0a81e199510fabec))


## v3.7.1 (2016-03-15)

### Documentation

- **configuration**: Fix typo in setup.cfg section
  ([`725d87d`](https://github.com/python-semantic-release/python-semantic-release/commit/725d87dc45857ef2f9fb331222845ac83a3af135))


## v3.7.0 (2016-01-10)

### Features

- Add ci_checks for Frigg CI
  ([`577c374`](https://github.com/python-semantic-release/python-semantic-release/commit/577c374396fe303b6fe7d64630d2959998d3595c))


## v3.6.1 (2016-01-10)

### Bug Fixes

- Add requests as dependency
  ([`4525a70`](https://github.com/python-semantic-release/python-semantic-release/commit/4525a70d5520b44720d385b0307e46fae77a7463))


## v3.6.0 (2015-12-28)

### Documentation

- Add documentation for configuring on CI
  ([`7806940`](https://github.com/python-semantic-release/python-semantic-release/commit/7806940ae36cb0d6ac0f966e5d6d911bd09a7d11))

- Add note about node semantic release
  ([`0d2866c`](https://github.com/python-semantic-release/python-semantic-release/commit/0d2866c528098ecaf1dd81492f28d3022a2a54e0))

- Add step by step guide for configuring travis ci
  ([`6f23414`](https://github.com/python-semantic-release/python-semantic-release/commit/6f2341442f61f0284b1119a2c49e96f0be678929))

- Move automatic-releases to subfolder
  ([`ed68e5b`](https://github.com/python-semantic-release/python-semantic-release/commit/ed68e5b8d3489463e244b078ecce8eab2cba2bb1))

- Remove duplicate readme
  ([`42a9421`](https://github.com/python-semantic-release/python-semantic-release/commit/42a942131947cd1864c1ba29b184caf072408742))

It was created by pandoc earlier when the original readme was written in markdown.

### Features

- Add checks for semaphore
  ([`2d7ef15`](https://github.com/python-semantic-release/python-semantic-release/commit/2d7ef157b1250459060e99601ec53a00942b6955))

Fixes #44


## v3.5.0 (2015-12-22)

### Bug Fixes

- Remove " from git push command
  ([`031318b`](https://github.com/python-semantic-release/python-semantic-release/commit/031318b3268bc37e6847ec049b37425650cebec8))

### Documentation

- Convert readme to rst
  ([`e8a8d26`](https://github.com/python-semantic-release/python-semantic-release/commit/e8a8d265aa2147824f18065b39a8e7821acb90ec))

### Features

- Add author in commit
  ([`020efaa`](https://github.com/python-semantic-release/python-semantic-release/commit/020efaaadf588e3fccd9d2f08a273c37e4158421))

Fixes #40

- Checkout master before publishing
  ([`dc4077a`](https://github.com/python-semantic-release/python-semantic-release/commit/dc4077a2d07e0522b625336dcf83ee4e0e1640aa))

Related to #39


## v3.4.0 (2015-12-22)

### Features

- Add travis environment checks
  ([`f386db7`](https://github.com/python-semantic-release/python-semantic-release/commit/f386db75b77acd521d2f5bde2e1dde99924dc096))

These checks will ensure that semantic release only runs against master and not in a pull-request.


## v3.3.3 (2015-12-22)

### Bug Fixes

- Do git push and git push --tags instead of --follow-tags
  ([`8bc70a1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bc70a183fd72f595c72702382bc0b7c3abe99c8))


## v3.3.2 (2015-12-21)

### Bug Fixes

- Change build badge
  ([`0dc068f`](https://github.com/python-semantic-release/python-semantic-release/commit/0dc068fff2f8c6914f4abe6c4e5fb2752669159e))

### Documentation

- Update docstrings for generate_changelog
  ([`987c6a9`](https://github.com/python-semantic-release/python-semantic-release/commit/987c6a96d15997e38c93a9d841c618c76a385ce7))


## v3.3.1 (2015-12-21)

### Bug Fixes

- Add pandoc to travis settings
  ([`17d40a7`](https://github.com/python-semantic-release/python-semantic-release/commit/17d40a73062ffa774542d0abc0f59fc16b68be37))

- Only list commits from the last version tag
  ([`191369e`](https://github.com/python-semantic-release/python-semantic-release/commit/191369ebd68526e5b1afcf563f7d13e18c8ca8bf))

Fixes #28


## v3.3.0 (2015-12-20)

### Bug Fixes

- Add missing parameters to twine.upload
  ([`4bae22b`](https://github.com/python-semantic-release/python-semantic-release/commit/4bae22bae9b9d9abf669b028ea3af4b3813a1df0))

- Better filtering of github token in push error
  ([`9b31da4`](https://github.com/python-semantic-release/python-semantic-release/commit/9b31da4dc27edfb01f685e6036ddbd4c715c9f60))

- Downgrade twine to version 1.5.0
  ([`66df378`](https://github.com/python-semantic-release/python-semantic-release/commit/66df378330448a313aff7a7c27067adda018904f))

- Make sure the github token is not in the output
  ([`55356b7`](https://github.com/python-semantic-release/python-semantic-release/commit/55356b718f74d94dd92e6c2db8a15423a6824eb5))

- Push to master by default
  ([`a0bb023`](https://github.com/python-semantic-release/python-semantic-release/commit/a0bb023438a1503f9fdb690d976d71632f19a21f))

### Features

- Add support for environment variables for pypi credentials
  ([`3b383b9`](https://github.com/python-semantic-release/python-semantic-release/commit/3b383b92376a7530e89b11de481c4dfdfa273f7b))


## v3.2.1 (2015-12-20)

### Bug Fixes

- Add requirements to manifest
  ([`ed25ecb`](https://github.com/python-semantic-release/python-semantic-release/commit/ed25ecbaeec0e20ad3040452a5547bb7d6faf6ad))

- **pypi**: Add sdist as default in addition to bdist_wheel
  ([`a1a35f4`](https://github.com/python-semantic-release/python-semantic-release/commit/a1a35f43175187091f028474db2ebef5bfc77bc0))

There are a lot of outdated pip installations around which leads to confusions if a package have had
  an sdist release at some point and then suddenly is only available as wheel packages, because old
  pip clients will then download the latest sdist package available.


## v3.2.0 (2015-12-20)

### Bug Fixes

- **deps**: Use one file for requirements
  ([`4868543`](https://github.com/python-semantic-release/python-semantic-release/commit/486854393b24803bb2356324e045ccab17510d46))

### Features

- **angular-parser**: Remove scope requirement
  ([`90c9d8d`](https://github.com/python-semantic-release/python-semantic-release/commit/90c9d8d4cd6d43be094cda86579e00b507571f98))

- **git**: Add push to GH_TOKEN@github-url
  ([`546b5bf`](https://github.com/python-semantic-release/python-semantic-release/commit/546b5bf15466c6f5dfe93c1c03ca34604b0326f2))


## v3.1.0 (2015-08-31)

### Features

- **pypi**: Add option to disable pypi upload
  ([`f5cd079`](https://github.com/python-semantic-release/python-semantic-release/commit/f5cd079edb219de5ad03a71448d578f5f477da9c))


## v3.0.0 (2015-08-25)

### Bug Fixes

- **errors**: Add exposing of errors in package
  ([`3662d76`](https://github.com/python-semantic-release/python-semantic-release/commit/3662d7663291859dd58a91b4b4ccde4f0edc99b2))

- **version**: Parse file instead for version
  ([`005dba0`](https://github.com/python-semantic-release/python-semantic-release/commit/005dba0094eeb4098315ef383a746e139ffb504d))

This makes it possible to use the version command without a setup.py file.

### Features

- **parser**: Add tag parser
  ([`a7f392f`](https://github.com/python-semantic-release/python-semantic-release/commit/a7f392fd4524cc9207899075631032e438e2593c))

This parser is based on the same commit style as 1.x.x of python-semantic-release. However, it
  requires "BREAKING CHANGE: <explanation> for a breaking change


## v2.1.4 (2015-08-24)

### Bug Fixes

- **github**: Fix property calls
  ([`7ecdeb2`](https://github.com/python-semantic-release/python-semantic-release/commit/7ecdeb22de96b6b55c5404ebf54a751911c4d8cd))

Properties can only be used from instances.


## v2.1.3 (2015-08-22)

### Bug Fixes

- **hvcs**: Make Github.token an property
  ([`37d5e31`](https://github.com/python-semantic-release/python-semantic-release/commit/37d5e3110397596a036def5f1dccf0860964332c))

### Documentation

- **api**: Update apidocs
  ([`6185380`](https://github.com/python-semantic-release/python-semantic-release/commit/6185380babedbbeab2a2a342f17b4ff3d4df6768))

- **parsers**: Add documentation about commit parsers
  ([`9b55422`](https://github.com/python-semantic-release/python-semantic-release/commit/9b554222768036024a133153a559cdfc017c1d91))

- **readme**: Update readme with information about the changelog command
  ([`56a745e`](https://github.com/python-semantic-release/python-semantic-release/commit/56a745ef6fa4edf6f6ba09c78fcc141102cf2871))


## v2.1.2 (2015-08-20)

### Bug Fixes

- **cli**: Fix call to generate_changelog in publish
  ([`5f8bce4`](https://github.com/python-semantic-release/python-semantic-release/commit/5f8bce4cbb5e1729e674efd6c651e2531aea2a16))


## v2.1.1 (2015-08-20)

### Bug Fixes

- **history**: Fix issue in get_previous_version
  ([`f961786`](https://github.com/python-semantic-release/python-semantic-release/commit/f961786aa3eaa3a620f47cc09243340fd329b9c2))


## v2.1.0 (2015-08-20)

### Bug Fixes

- **cli**: Fix check of token in changelog command
  ([`cc6e6ab`](https://github.com/python-semantic-release/python-semantic-release/commit/cc6e6abe1e91d3aa24e8d73e704829669bea5fd7))

- **github**: Fix the github releases integration
  ([`f0c3c1d`](https://github.com/python-semantic-release/python-semantic-release/commit/f0c3c1db97752b71f2153ae9f623501b0b8e2c98))

- **history**: Fix changelog generation
  ([`f010272`](https://github.com/python-semantic-release/python-semantic-release/commit/f01027203a8ca69d21b4aff689e60e8c8d6f9af5))

This enables regeneration of a given versions changelog.

### Features

- **cli**: Add the possibility to repost the changelog
  ([`4d028e2`](https://github.com/python-semantic-release/python-semantic-release/commit/4d028e21b9da01be8caac8f23f2c11e0c087e485))


## v2.0.0 (2015-08-19)

### Bug Fixes

- **cli**: Change output indentation on changelog
  ([`2ca41d3`](https://github.com/python-semantic-release/python-semantic-release/commit/2ca41d3bd1b8b9d9fe7e162772560e3defe2a41e))

- **history**: Fix level id's in angular parser
  ([`2918d75`](https://github.com/python-semantic-release/python-semantic-release/commit/2918d759bf462082280ede971a5222fe01634ed8))

- **history**: Fix regex in angular parser
  ([`974ccda`](https://github.com/python-semantic-release/python-semantic-release/commit/974ccdad392d768af5e187dabc184be9ac3e133d))

This fixes a problem where multiline commit messages where not correctly parsed.

- **history**: Support unexpected types in changelog generator
  ([`13deacf`](https://github.com/python-semantic-release/python-semantic-release/commit/13deacf5d33ed500e4e94ea702a2a16be2aa7c48))

### Features

- **cli**: Add command for printing the changelog
  ([`336b8bc`](https://github.com/python-semantic-release/python-semantic-release/commit/336b8bcc01fc1029ff37a79c92935d4b8ea69203))

Usage: `semantic_release changelog`

- **github**: Add github release changelog helper
  ([`da18795`](https://github.com/python-semantic-release/python-semantic-release/commit/da187951af31f377ac57fe17462551cfd776dc6e))

- **history**: Add angular parser
  ([`91e4f0f`](https://github.com/python-semantic-release/python-semantic-release/commit/91e4f0f4269d01b255efcd6d7121bbfd5a682e12))

This adds a parser that follows the angular specification. The parser is not hooked into the history
  evaluation yet. However, it will become the default parser of commit messages when the evaluator
  starts using exchangeable parsers.

Related to #17

- **history**: Add generate_changelog function
  ([`347f21a`](https://github.com/python-semantic-release/python-semantic-release/commit/347f21a1f8d655a71a0e7d58b64d4c6bc6d0bf31))

It generates a dict with changelog information to each of the given section types.

- **history**: Add markdown changelog formatter
  ([`d77b58d`](https://github.com/python-semantic-release/python-semantic-release/commit/d77b58db4b66aec94200dccab94f483def4dacc9))

- **history**: Set angular parser as the default
  ([`c2cf537`](https://github.com/python-semantic-release/python-semantic-release/commit/c2cf537a42beaa60cd372c7c9f8fb45db8085917))

BREAKING CHANGE: This changes the default parser. Thus, the default behaviour of the commit log
  evaluator will change. From now on it will use the angular commit message spec to determine the
  new version.

- **publish**: Add publishing of changelog to github
  ([`74324ba`](https://github.com/python-semantic-release/python-semantic-release/commit/74324ba2749cdbbe80a92b5abbecfeab04617699))

- **settings**: Add loading of current parser
  ([`7bd0916`](https://github.com/python-semantic-release/python-semantic-release/commit/7bd0916f87a1f9fe839c853eab05cae1af420cd2))


## v1.0.0 (2015-08-04)


## v0.9.1 (2015-08-04)


## v0.9.0 (2015-08-03)


## v0.8.0 (2015-08-03)


## v0.7.0 (2015-08-02)


## v0.6.0 (2015-08-02)


## v0.5.4 (2015-07-29)


## v0.5.3 (2015-07-28)


## v0.5.2 (2015-07-28)


## v0.5.1 (2015-07-28)


## v0.5.0 (2015-07-28)


## v0.4.0 (2015-07-28)


## v0.3.2 (2015-07-28)


## v0.3.1 (2015-07-28)


## v0.3.0 (2015-07-27)


## v0.2.0 (2015-07-27)


## v0.1.1 (2015-07-27)


## v0.1.0 (2015-07-27)
