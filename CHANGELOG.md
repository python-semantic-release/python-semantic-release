# CHANGELOG



## v9.7.0 (2024-05-06)

### Documentation

* docs(configuration): add description of build command available env variables ([`c882dc6`](https://github.com/python-semantic-release/python-semantic-release/commit/c882dc62b860b2aeaa925c21d1524f4ae25ef567))

### Feature

* feat(version-cmd): pass `NEW_VERSION` &amp; useful env vars to build command ([`ee6b246`](https://github.com/python-semantic-release/python-semantic-release/commit/ee6b246df3bb211ab49c8bce075a4c3f6a68ed77))

### Fix

* fix(gha): add missing `tag` option to GitHub Action definition (#908)

  Resolves: #906 ([`6b24288`](https://github.com/python-semantic-release/python-semantic-release/commit/6b24288a96302cd6982260e46fad128ec4940da9))


## v9.6.0 (2024-04-29)

### Feature

* feat: changelog filters are specialized per vcs type (#890)

* test(github): sync pr url expectation with GitHub api documentation

* fix(github): correct changelog filter for pull request urls

* refactor(hvcs-base): change to an abstract class &amp; simplify interface

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

* refactor(config): adjust default token resolution w/ subclasses ([`76ed593`](https://github.com/python-semantic-release/python-semantic-release/commit/76ed593ea33c851005994f0d1a6a33cc890fb908))

### Fix

* fix(parser-custom): gracefully handle custom parser import errors ([`67f6038`](https://github.com/python-semantic-release/python-semantic-release/commit/67f60389e3f6e93443ea108c0e1b4d30126b8e06))

* fix: correct version `--prerelease` use &amp; enable `--as-prerelease` (#647)

* test(version): add validation of `--as-prerelease` and `--prerelease opts`

* fix(version-cmd): correct `--prerelease` use

  Prior to this change, `--prerelease` performed the role of converting whichever forced
version into a prerelease version declaration, which was an unintentional breaking
change to the CLI compared to v7.

  `--prerelease` now forces the next version to increment the prerelease revision,
which makes it consistent with `--patch`, `--minor` and `--major`. Temporarily disabled
the ability to force a prerelease.

  Resolves: #639

* feat(version-cmd): add `--as-prerelease` option to force the next version to be a prerelease

  Prior to this change, `--prerelease` performed the role that `--as-prerelease` now does,
which was an unintentional breaking change to the CLI compared to v7.

  `--prerelease` is used to force the next version to increment the prerelease revision,
which makes it consistent with `--patch`, `--minor` and `--major`, while `--as-prerelease`
forces for the next version to be converted to a prerelease version type before it is
applied to the project regardless of the bump level.

  Resolves: #639

* docs(commands): update version command options definition about prereleases

---------

Co-authored-by: codejedi365 &lt;codejedi365@gmail.com&gt; ([`2acb5ac`](https://github.com/python-semantic-release/python-semantic-release/commit/2acb5ac35ae79d7ae25ca9a03fb5c6a4a68b3673))


## v9.5.0 (2024-04-23)

### Build

* build(deps): bump ruff from 0.3.5 to 0.3.7 (#894) ([`6bf2849`](https://github.com/python-semantic-release/python-semantic-release/commit/6bf28496d8631ada9009aec5f1000f68b7f7ee16))

### Feature

* feat: extend support to on-prem GitHub Enterprise Server (#896)

* test(github): adjust init test to match the Enterprise Server api url

* feat(github): extend support to on-prem GitHub Enterprise Server

  Resolves: #895 ([`4fcb737`](https://github.com/python-semantic-release/python-semantic-release/commit/4fcb737958d95d1a3be24db7427e137b46f5075f))


## v9.4.2 (2024-04-14)

### Build

* build(deps): update rich requirement from ~=12.5 to ~=13.0 (#877)

Updates the requirements on [rich](https://github.com/Textualize/rich) to permit the latest version.
- [Release notes](https://github.com/Textualize/rich/releases)
- [Changelog](https://github.com/Textualize/rich/blob/master/CHANGELOG.md)

Resolves: #888

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`4a22a8c`](https://github.com/python-semantic-release/python-semantic-release/commit/4a22a8c1a69bcf7b1ddd6db56e6883c617a892b3))

### Fix

* fix(hvcs): allow insecure http connections if configured (#886)

* fix(gitlab): allow insecure http connections if configured

* test(hvcs-gitlab): fix tests for clarity &amp; insecure urls

* test(conftest): refactor netrc generation into common fixture

* refactor(hvcsbase): remove extrenous non-common functionality

* fix(gitea): allow insecure http connections if configured

* test(hvcs-gitea): fix tests for clarity &amp; insecure urls

* refactor(gitlab): adjust init function signature

* fix(github): allow insecure http connections if configured

* test(hvcs-github): fix tests for clarity &amp; insecure urls

* fix(bitbucket): allow insecure http connections if configured

* test(hvcs-bitbucket): fix tests for clarity &amp; insecure urls

* fix(config): add flag to allow insecure connections

* fix(version-cmd): handle HTTP exceptions more gracefully

* style(hvcs): resolve typing issues &amp; mimetype executions

* test(cli-config): adapt default token test for env resolution

* test(changelog-cmd): isolate env &amp; correct the expected api url

* test(fixtures): adapt repo builder for new hvcs init() signature

* style: update syntax for 3.8 compatiblity &amp; formatting

* docs(configuration): update `remote` settings section with missing values

  Resolves: #868

* style(docs): improve configuration &amp; api readability ([`db13438`](https://github.com/python-semantic-release/python-semantic-release/commit/db1343890f7e0644bc8457f995f2bd62087513d3))

* fix(hvcs): prevent double url schemes urls in changelog (#676)

* fix(hvcs): prevent double protocol scheme urls in changelogs

  Due to a typo and conditional stripping of the url scheme the
  hvcs_domain and hvcs_api_domain values would contain protocol schemes
  when a user specified one but the defaults would not. It would cause
  the api_url and remote_url to end up as &#34;https://https://domain.com&#34;

* fix(bitbucket): correct url parsing &amp; prevent double url schemes

* fix(gitea): correct url parsing &amp; prevent double url schemes

* fix(github): correct url parsing &amp; prevent double url schemes

* fix(gitlab): correct url parsing &amp; prevent double url schemes

* test(hvcs): ensure api domains are derived correctly

---------

Co-authored-by: codejedi365 &lt;codejedi365@gmail.com&gt; ([`5cfdb24`](https://github.com/python-semantic-release/python-semantic-release/commit/5cfdb248c003a2d2be5fe65fb61d41b0d4c45db5))


## v9.4.1 (2024-04-06)

### Fix

* fix(gh-actions-output): fixed trailing newline to match GITHUB_OUTPUT format (#885)

* test(gh-actions-output): fix unit tests to manage proper whitespace

  tests were adjusted for clarity and to replicate error detailed in #884.

* fix(gh-actions-output): fixed trailing newline to match GITHUB_OUTPUT format

  Resolves: #884 ([`2c7b6ec`](https://github.com/python-semantic-release/python-semantic-release/commit/2c7b6ec85b6e3182463d7b695ee48e9669a25b3b))


## v9.4.0 (2024-03-31)

### Feature

* feat(gitea): derives gitea api domain from base domain when unspecified (#675)

* test(gitea): add test of custom server path &amp; custom api domain

* feat(gitea): derives gitea api domain from base domain when unspecified

* refactor(hvcs-gitea): uniformly handle protocol prefixes

---------

Co-authored-by: codejedi365 &lt;codejedi365@gmail.com&gt; ([`2ee3f8a`](https://github.com/python-semantic-release/python-semantic-release/commit/2ee3f8a918d2e5ea9ab64df88f52e62a1f589c38))


## v9.3.1 (2024-03-24)

### Fix

* fix(cli-version): change implementation to only push the tag we generated

Restricts the git push command to only push the explicit tag we created
which will eliminate the possibility of pushing another tag that could
cause an error.

Resolves: #803 ([`8a9da4f`](https://github.com/python-semantic-release/python-semantic-release/commit/8a9da4feb8753e3ab9ea752afa25decd2047675a))

* fix(algorithm): handle merge-base errors gracefully

Merge-base errors generally occur from a shallow clone that is
primarily used by CI environments and will cause PSR to explode
prior to this change. Now it exits with an appropriate error.

Resolves: #724 ([`4c998b7`](https://github.com/python-semantic-release/python-semantic-release/commit/4c998b77a3fe5e12783d1ab2d47789a10b83f247))

### Performance

* perf(algorithm): simplify logs &amp; use lookup when searching for commit &amp; tag match ([`3690b95`](https://github.com/python-semantic-release/python-semantic-release/commit/3690b9511de633ab38083de4d2505b6d05853346))


## v9.3.0 (2024-03-21)

### Feature

* feat(cmd-version): changelog available to bundle (#779)

* test(util): fix overlooked file differences in folder comparison

* test(version): tracked changelog as changed file on version create

Removes the temporary release_notes hack to prevent CHANGELOG generation on
execution of version command.  Now that it is implemented we can remove the
fixture to properly pass the tests.

* feat(cmd-version): create changelog prior to build enabling doc bundling ([`37fdb28`](https://github.com/python-semantic-release/python-semantic-release/commit/37fdb28e0eb886d682b5dea4cc83a7c98a099422))


## v9.2.2 (2024-03-19)

### Fix

* fix(cli): enable subcommand help even if config is invalid

Refactors configuration loading to use lazy loading by subcommands
triggered by the property access of the runtime_ctx object. Resolves
the issues when running `--help` on subcommands when a configuration
is invalid

Resolves: #840 ([`91d221a`](https://github.com/python-semantic-release/python-semantic-release/commit/91d221a01266e5ca6de5c73296b0a90987847494))


## v9.2.1 (2024-03-19)

### Fix

* fix(parse-git-url): handle urls with url-safe special characters ([`27cd93a`](https://github.com/python-semantic-release/python-semantic-release/commit/27cd93a0a65ee3787ca51be4c91c48f6ddb4269c))


## v9.2.0 (2024-03-18)

### Build

* build(deps): add click-option-group for grouping exclusive flags ([`bd892b8`](https://github.com/python-semantic-release/python-semantic-release/commit/bd892b89c26df9fccc9335c84e2b3217e3e02a37))

### Documentation

* docs(configuration): clarify the `major_on_zero` configuration option ([`f7753cd`](https://github.com/python-semantic-release/python-semantic-release/commit/f7753cdabd07e276bc001478d605fca9a4b37ec4))

* docs(configuration): add description of `allow-zero-version` configuration option ([`4028f83`](https://github.com/python-semantic-release/python-semantic-release/commit/4028f8384a0181c8d58c81ae81cf0b241a02a710))

### Feature

* feat(version-config): add option to disable 0.x.x versions ([`dedb3b7`](https://github.com/python-semantic-release/python-semantic-release/commit/dedb3b765c8530379af61d3046c3bb9c160d54e5))

* feat(version): add new version print flags to display the last released version and tag ([`814240c`](https://github.com/python-semantic-release/python-semantic-release/commit/814240c7355df95e9be9a6ed31d004b800584bc0))

### Fix

* fix(changelog-generation): fix incorrect release timezone determination ([`f802446`](https://github.com/python-semantic-release/python-semantic-release/commit/f802446bd0693c4c9f6bdfdceae8b89c447827d2))

* fix(changelog): make sure default templates render ending in 1 newline ([`0b4a45e`](https://github.com/python-semantic-release/python-semantic-release/commit/0b4a45e3673d0408016dc8e7b0dce98007a763e3))


## v9.1.1 (2024-02-25)

### Fix

* fix(parse_git_url): fix bad url with dash ([`1c25b8e`](https://github.com/python-semantic-release/python-semantic-release/commit/1c25b8e6f1e43c15ca7d5a59dca0a13767f9bc33))


## v9.1.0 (2024-02-14)

### Build

* build(deps): bump minimum required `tomlkit` to `&gt;=0.11.0`

TOMLDocument is missing the `unwrap()` function in `v0.10.2` which
causes an AttributeError to occur when attempting to read a the text
in `pyproject.toml` as discovered with #834

Resolves: #834 ([`291aace`](https://github.com/python-semantic-release/python-semantic-release/commit/291aacea1d0429a3b27e92b0a20b598f43f6ea6b))

### Documentation

* docs: add bitbucket to token table ([`56f146d`](https://github.com/python-semantic-release/python-semantic-release/commit/56f146d9f4c0fc7f2a84ad11b21c8c45e9221782))

* docs: add bitbucket authentication ([`b78a387`](https://github.com/python-semantic-release/python-semantic-release/commit/b78a387d8eccbc1a6a424a183254fc576126199c))

* docs: fix typo ([`b240e12`](https://github.com/python-semantic-release/python-semantic-release/commit/b240e129b180d45c1d63d464283b7dfbcb641d0c))

### Feature

* feat: add bitbucket hvcs ([`bbbbfeb`](https://github.com/python-semantic-release/python-semantic-release/commit/bbbbfebff33dd24b8aed2d894de958d532eac596))

### Fix

* fix: remove unofficial environment variables ([`a5168e4`](https://github.com/python-semantic-release/python-semantic-release/commit/a5168e40b9a14dbd022f62964f382b39faf1e0df))


## v9.0.3 (2024-02-08)

### Fix

* fix(algorithm): correct bfs to not abort on previously visited node ([`02df305`](https://github.com/python-semantic-release/python-semantic-release/commit/02df305db43abfc3a1f160a4a52cc2afae5d854f))

### Performance

* perf(algorithm): refactor bfs search to use queue rather than recursion ([`8b742d3`](https://github.com/python-semantic-release/python-semantic-release/commit/8b742d3db6652981a7b5f773a74b0534edc1fc15))


## v9.0.2 (2024-02-08)

### Documentation

* docs: Remove duplicate note in configuration.rst (#807) ([`fb6f243`](https://github.com/python-semantic-release/python-semantic-release/commit/fb6f243a141642c02469f1080180ecaf4f3cec66))

### Fix

* fix(util): properly parse windows line-endings in commit messages

Due to windows line-endings `\r\n`, it would improperly split the commit
description (it failed to split at all) and cause detection of Breaking changes
to fail. The breaking changes regular expression looks to the start of the line
for the proper syntax.

Resolves: #820 ([`70193ba`](https://github.com/python-semantic-release/python-semantic-release/commit/70193ba117c1a6d3690aed685fee8a734ba174e5))


## v9.0.1 (2024-02-06)

### Fix

* fix(config): set commit parser opt defaults based on parser choice (#782) ([`9c594fb`](https://github.com/python-semantic-release/python-semantic-release/commit/9c594fb6efac7e4df2b0bfbd749777d3126d03d7))


## v9.0.0 (2024-02-06)

### Breaking

* fix!: drop support for Python 3.7 (#828) ([`ad086f5`](https://github.com/python-semantic-release/python-semantic-release/commit/ad086f5993ae4741d6e20fee618d1bce8df394fb))


## v8.7.2 (2024-01-03)

### Fix

* fix(lint): correct linter errors ([`c9556b0`](https://github.com/python-semantic-release/python-semantic-release/commit/c9556b0ca6df6a61e9ce909d18bc5be8b6154bf8))


## v8.7.1 (2024-01-03)

### Documentation

* docs(contributing): add docs-build, testing conf, &amp; build instructions (#787) ([`011b072`](https://github.com/python-semantic-release/python-semantic-release/commit/011b0729cba3045b4e7291fd970cb17aad7bae60))

* docs(configuration): change defaults definition of token default to table (#786) ([`df1df0d`](https://github.com/python-semantic-release/python-semantic-release/commit/df1df0de8bc655cbf8f86ae52aff10efdc66e6d2))

* docs: add note on default envvar behaviour (#780) ([`0b07cae`](https://github.com/python-semantic-release/python-semantic-release/commit/0b07cae71915c5c82d7784898b44359249542a64))

### Fix

* fix(cli-generate-config): ensure configuration types are always toml parsable (#785) ([`758e649`](https://github.com/python-semantic-release/python-semantic-release/commit/758e64975fe46b961809f35977574729b7c44271))


## v8.7.0 (2023-12-22)

### Feature

* feat(config): enable default environment token per hvcs (#774) ([`26528eb`](https://github.com/python-semantic-release/python-semantic-release/commit/26528eb8794d00dfe985812269702fbc4c4ec788))


## v8.6.0 (2023-12-22)

### Documentation

* docs: minor correction to commit-parsing documentation (#777) ([`245e878`](https://github.com/python-semantic-release/python-semantic-release/commit/245e878f02d5cafec6baf0493c921c1e396b56e8))

### Feature

* feat(utils): expand parsable valid git remote url formats (#771)

Git remote url parsing now supports additional formats (ssh, https, file, git) ([`cf75f23`](https://github.com/python-semantic-release/python-semantic-release/commit/cf75f237360488ebb0088e5b8aae626e97d9cbdd))


## v8.5.2 (2023-12-19)

### Fix

* fix(cli): gracefully output configuration validation errors (#772)

* test(fixtures): update example project workflow &amp; add config modifier

* test(cli-main): add test for raw config validation error

* fix(cli): gracefully output configuration validation errors ([`e8c9d51`](https://github.com/python-semantic-release/python-semantic-release/commit/e8c9d516c37466a5dce75a73766d5be0f9e74627))


## v8.5.1 (2023-12-12)

### Documentation

* docs(configuration): adjust wording and improve clarity (#766)

* docs(configuration): fix typo in text

* docs(configuration): adjust wording and improve clarity ([`6b2fc8c`](https://github.com/python-semantic-release/python-semantic-release/commit/6b2fc8c156e122ee1b43fdb513b2dc3b8fd76724))

### Fix

* fix(config): gracefully fail when repo is in a detached HEAD state (#765)

* fix(config): cleanly handle repository in detached HEAD state

* test(cli-main): add detached head cli test ([`ac4f9aa`](https://github.com/python-semantic-release/python-semantic-release/commit/ac4f9aacb72c99f2479ae33369822faad011a824))

* fix(cmd-version): handle committing of git-ignored file gracefully (#764)

* fix(version): only commit non git-ignored files during version commit

* test(version): set version file as ignored file

Tweaks tests to use one committed change file and the version file
as an ignored change file. This allows us to verify that our commit
mechanism does not crash if a file that is changed is ignored by user ([`ea89fa7`](https://github.com/python-semantic-release/python-semantic-release/commit/ea89fa72885e15da91687172355426a22c152513))


## v8.5.0 (2023-12-07)

### Feature

* feat: allow template directories to contain a &#39;.&#39; at the top-level (#762) ([`07b232a`](https://github.com/python-semantic-release/python-semantic-release/commit/07b232a3b34be0b28c6af08aea4852acb1b9bd56))


## v8.4.0 (2023-12-07)

### Documentation

* docs(migration): fix comments about publish command (#747) ([`90380d7`](https://github.com/python-semantic-release/python-semantic-release/commit/90380d797a734dcca5040afc5fa00e3e01f64152))

### Feature

* feat(cmd-version): add `--tag/--no-tag` option to version command (#752)

* fix(version): separate push tags from commit push when not committing changes

* feat(version): add `--no-tag` option to turn off tag creation

* test(version): add test for `--tag` option &amp; `--no-tag/commit`

* docs(commands): update `version` subcommand options ([`de6b9ad`](https://github.com/python-semantic-release/python-semantic-release/commit/de6b9ad921e697b5ea2bb2ea8f180893cecca920))

### Unknown

* Revert &#34;feat(action): use composite action for semantic release (#692)&#34;

This reverts commit 4648d87bac8fb7e6cc361b765b4391b30a8caef8. ([`f145257`](https://github.com/python-semantic-release/python-semantic-release/commit/f1452578cc064edbe64d61ae3baab4bc9bd4b666))


## v8.3.0 (2023-10-23)

### Feature

* feat(action): use composite action for semantic release (#692)

Co-authored-by: Bernard Cooke &lt;bernard-cooke@hotmail.com&gt; ([`4648d87`](https://github.com/python-semantic-release/python-semantic-release/commit/4648d87bac8fb7e6cc361b765b4391b30a8caef8))


## v8.2.0 (2023-10-23)

### Documentation

* docs: add PYTHONPATH mention for commit parser ([`3284258`](https://github.com/python-semantic-release/python-semantic-release/commit/3284258b9fa1a3fe165f336181aff831d50fddd3))

### Feature

* feat: Allow user customization of release notes template (#736)

Signed-off-by: Bryant Finney &lt;bryant.finney@outlook.com&gt; ([`94a1311`](https://github.com/python-semantic-release/python-semantic-release/commit/94a131167e1b867f8bc112a042b9766e050ccfd1))


## v8.1.2 (2023-10-13)

### Fix

* fix: correct lint errors

GitHub.upload_asset now raises ValueError instead of requests.HTTPError ([`a13a6c3`](https://github.com/python-semantic-release/python-semantic-release/commit/a13a6c37e180dc422599939a5725835306c18ff2))

* fix: Error when running build command on windows systems (#732) ([`2553657`](https://github.com/python-semantic-release/python-semantic-release/commit/25536574760b407410f435441da533fafbf94402))


## v8.1.1 (2023-09-19)

### Fix

* fix: attribute error when logging non-strings (#711) ([`75e6e48`](https://github.com/python-semantic-release/python-semantic-release/commit/75e6e48129da8238a62d5eccac1ae55d0fee0f9f))


## v8.1.0 (2023-09-19)

### Documentation

* docs: update project urls (#715) ([`5fd5485`](https://github.com/python-semantic-release/python-semantic-release/commit/5fd54856dfb6774feffc40d36d5bb0f421f04842))

* docs: fix typos (#708) ([`2698b0e`](https://github.com/python-semantic-release/python-semantic-release/commit/2698b0e006ff7e175430b98450ba248ed523b341))

### Feature

* feat: upgrade pydantic to v2 (#714) ([`5a5c5d0`](https://github.com/python-semantic-release/python-semantic-release/commit/5a5c5d0ee347750d7c417c3242d52e8ada50b217))


## v8.0.8 (2023-08-26)

### Fix

* fix: dynamic_import() import path split (#686) ([`1007a06`](https://github.com/python-semantic-release/python-semantic-release/commit/1007a06d1e16beef6d18f44ff2e0e09921854b54))


## v8.0.7 (2023-08-16)

### Fix

* fix: use correct upload url for github (#661)

Co-authored-by: github-actions &lt;action@github.com&gt; ([`8a515ca`](https://github.com/python-semantic-release/python-semantic-release/commit/8a515caf1f993aa653e024beda2fdb9e629cc42a))


## v8.0.6 (2023-08-13)

### Fix

* fix(publish): improve error message when no tags found (#683) ([`bdc06ea`](https://github.com/python-semantic-release/python-semantic-release/commit/bdc06ea061c19134d5d74bd9f168700dd5d9bcf5))


## v8.0.5 (2023-08-10)

### Documentation

* docs: fix typo missing &#39;s&#39; in version_variable[s] in configuration.rst (#668) ([`879186a`](https://github.com/python-semantic-release/python-semantic-release/commit/879186aa09a3bea8bbe2b472f892cf7c0712e557))

### Fix

* fix: don&#39;t warn about vcs token if ignore_token_for_push is true. (#670)

* fix: don&#39;t warn about vcs token if ignore_token_for_push is true.

* docs: `password` should be `token`. ([`f1a54a6`](https://github.com/python-semantic-release/python-semantic-release/commit/f1a54a6c9a05b225b6474d50cd610eca19ec0c34))


## v8.0.4 (2023-07-26)

### Documentation

* docs: clarify usage of assets config option (#655) ([`efa2b30`](https://github.com/python-semantic-release/python-semantic-release/commit/efa2b3019b41eb427f0e1c8faa21ad10664295d0))

* docs: add Python 3.11 to classifiers in metadata (#651) ([`5a32a24`](https://github.com/python-semantic-release/python-semantic-release/commit/5a32a24bf4128c39903f0c5d3bd0cb1ccba57e18))

### Fix

* fix(changelog): use version as semver tag by default (#653) ([`5984c77`](https://github.com/python-semantic-release/python-semantic-release/commit/5984c7771edc37f0d7d57894adecc2591efc414d))


## v8.0.3 (2023-07-21)

### Fix

* fix: skip unparseable versions when calculating next version (#649) ([`88f25ea`](https://github.com/python-semantic-release/python-semantic-release/commit/88f25eae62589cdf53dbc3dfcb167a3ae6cba2d3))


## v8.0.2 (2023-07-18)

### Documentation

* docs: correct version_toml example in migrating_from_v7.rst (#641) ([`325d5e0`](https://github.com/python-semantic-release/python-semantic-release/commit/325d5e048bd89cb2a94c47029d4878b27311c0f0))

* docs: clarify v8 breaking changes in GitHub action inputs (#643) ([`cda050c`](https://github.com/python-semantic-release/python-semantic-release/commit/cda050cd9e789d81458157ee240ff99ec65c6f25))

* docs: better description for tag_format usage ([`2129b72`](https://github.com/python-semantic-release/python-semantic-release/commit/2129b729837eccc41a33dbb49785a8a30ce6b187))

### Fix

* fix: handle missing configuration (#644) ([`f15753c`](https://github.com/python-semantic-release/python-semantic-release/commit/f15753ce652f36cc03b108c667a26ab74bcbf95d))


## v8.0.1 (2023-07-17)

### Documentation

* docs: reduce readthedocs formats and add entries to migration from v7 guide ([`9b6ddfe`](https://github.com/python-semantic-release/python-semantic-release/commit/9b6ddfef448f9de30fa2845034f76655d34a9912))

* docs(migration): fix hyperlink (#631) ([`5fbd52d`](https://github.com/python-semantic-release/python-semantic-release/commit/5fbd52d7de4982b5689651201a0e07b445158645))

### Fix

* fix: invalid version in Git history should not cause a release failure (#632) ([`254430b`](https://github.com/python-semantic-release/python-semantic-release/commit/254430b5cc5f032016b4c73168f0403c4d87541e))


## v8.0.0 (2023-07-16)

### Breaking

* feat!: v8 (#619)

* feat!: 8.0.x (#538)

Co-authored-by: Johan &lt;johanhmr@gmail.com&gt;
Co-authored-by: U-NEO\johan &lt;johan.hammar@ombea.com&gt;

* fix: correct Dockerfile CLI command and GHA fetch

* fix: resolve branch checkout logic in GHA

* fix: remove commit amending behaviour

this was not working when there were no source code changes to be made, as it lead
to attempting to amend a HEAD commit that wasn&#39;t produced by PSR

* 8.0.0-alpha.1

Automatically generated by python-semantic-release

* fix: correct logic for generating release notes (#550)

* fix: cleanup comments and unused logic

* fix(action): mark container fs as safe for git to operate on

* style: beautify 49080c510a68cccd2f6c7a8d540b483751901207

* fix(action): quotation for git config command

* 8.0.0-alpha.2

Automatically generated by python-semantic-release

* fix: resolve bug in changelog logic, enable upload to pypi

* 8.0.0-alpha.3

Automatically generated by python-semantic-release

* test: add tests for ReleaseHistory.release

* fix: resolve loss of tag_format configuration

* 8.0.0-alpha.4

Automatically generated by python-semantic-release

* feat: various improvements

* Added sorting to test parameterisation, so that pytest-xdist works again - dramatic speedup for testing
* Reworked the CI verification code so it&#39;s a bit prettier
* Added more testing for the version CLI command, and split some logic out of the command itself
* Removed a redundant double-regex match in VersionTranslator and Version, for some speedup

* chore(test): proper env patching for tests in CI

* style: beautify bcb27a4a8ce4789d083226f088c1810f45cd4c77

* refactor!: remove verify-ci command

* 8.0.0-alpha.5

Automatically generated by python-semantic-release

* fix(docs): fixup docs and remove reference to dist publication

* feat!: remove publication of dists to artefact repository

* feat: rename &#39;upload&#39; configuration section to &#39;publish&#39;

* feat!: removed build status checking

* feat: add GitHub Actions output

* fix(action): remove default for &#39;force&#39;

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

Automatically generated by python-semantic-release

* docs: update docs with additional required permissions

* feat: add option to specify tag to publish to in publish command

* feat: add Strict Mode

* docs: convert to Furo theme

* feat: add --skip-build option

* 8.0.0-alpha.7

Automatically generated by python-semantic-release

* test: separate command line tests by stdout and stderr

* ci: pass tag output and conditionally execute publish steps

* fix: correct assets type in configuration (#603)

* change raw config assets type

* fix: correct assets type-annotation for RuntimeContext

---------

Co-authored-by: Bernard Cooke &lt;bernard-cooke@hotmail.com&gt;

* 8.0.0-alpha.8

Automatically generated by python-semantic-release

* fix: pin Debian version in Dockerfile

* feat: promote to rc

* 8.0.0-rc.1

Automatically generated by python-semantic-release

* ci: fix conditionals in workflow and update documentation

* ci: correct conditionals

* fix: only call Github Action output callback once defaults are set

* 8.0.0-rc.2

Automatically generated by python-semantic-release

* fix: create_or_update_release for Gitlab hvcs

* ci: remove separate v8 workflow

* chore: tweak issue templates

* chore: bump docs dependencies

* 8.0.0-rc.3

Automatically generated by python-semantic-release

* fix(deps): add types-click, and downgrade sphinx/furo for 3.7

* 8.0.0-rc.4

Automatically generated by python-semantic-release

* docs: fix typo (#623)

* docs: correct typo in docs/changelog_templates.rst

Co-authored-by: Micael Jarniac &lt;micael@jarniac.com&gt;

---------

Co-authored-by: Johan &lt;johanhmr@gmail.com&gt;
Co-authored-by: U-NEO\johan &lt;johan.hammar@ombea.com&gt;
Co-authored-by: semantic-release &lt;semantic-release&gt;
Co-authored-by: github-actions &lt;action@github.com&gt;
Co-authored-by: smeng9 &lt;38666763+smeng9@users.noreply.github.com&gt;
Co-authored-by: Micael Jarniac &lt;micael@jarniac.com&gt; ([`ec30564`](https://github.com/python-semantic-release/python-semantic-release/commit/ec30564b4ec732c001d76d3c09ba033066d2b6fe))


## v7.34.6 (2023-06-17)

### Fix

* fix: relax invoke dependency constraint ([`18ea200`](https://github.com/python-semantic-release/python-semantic-release/commit/18ea200633fd67e07f3d4121df5aa4c6dd29d154))


## v7.34.5 (2023-06-17)

### Fix

* fix: consider empty commits (#608) ([`6f2e890`](https://github.com/python-semantic-release/python-semantic-release/commit/6f2e8909636595d3cb5e858f42c63820cda45974))


## v7.34.4 (2023-06-15)

### Fix

* fix: docker build fails installing git (#605)

git was installed from bullseye-backports, but base image is referencing latest python:3.10
since bookworm was recently released, this now points at bookworm and installing the backport of git is actually trying to downgrade, resulting in this error:

&gt; E: Packages were downgraded and -y was used without --allow-downgrades.

&gt; ERROR: failed to solve: process &#34;/bin/sh -c echo \&#34;deb http://deb.debian.org/debian bullseye-backports main\&#34; &gt;&gt; /etc/apt/sources.list;     apt-get update;    apt-get install -y git/bullseye-backports&#34; did not complete successfully: exit code: 100 ([`9e3eb97`](https://github.com/python-semantic-release/python-semantic-release/commit/9e3eb979783bc39ca564c2967c6c77eecba682e6))


## v7.34.3 (2023-06-01)

### Fix

* fix: generate markdown linter compliant changelog headers &amp; lists (#597)

In #594, I missed that there are 2 places where the version header is formatted ([`cc87400`](https://github.com/python-semantic-release/python-semantic-release/commit/cc87400d4a823350de7d02dc3172d2488c9517db))


## v7.34.2 (2023-05-29)

### Fix

* fix: open all files with explicit utf-8 encoding (#596) ([`cb71f35`](https://github.com/python-semantic-release/python-semantic-release/commit/cb71f35c26c1655e675fa735fa880d39a2c8af9c))


## v7.34.1 (2023-05-28)

### Fix

* fix: generate markdown linter compliant changelog headers &amp; lists (#594)

Add an extra new line after each header and between sections to fix 2 markdownlint errors
for changelogs generated by this package ([`9d9d403`](https://github.com/python-semantic-release/python-semantic-release/commit/9d9d40305c499c907335abe313e3ed122db0b154))


## v7.34.0 (2023-05-28)

### Feature

* feat: add option to only parse commits for current working directory (#509)

When running the application from a sub-directory in the VCS, the option
use_only_cwd_commits will filter out commits that does not changes the
current working directory, similar to running commands like
`git log -- .` in a sub-directory. ([`cdf8116`](https://github.com/python-semantic-release/python-semantic-release/commit/cdf8116c1e415363b10a01f541873e04ad874220))


## v7.33.5 (2023-05-19)

### Documentation

* docs: update broken badge and add links (#591)

The &#34;Test Status&#34; badge was updated to address a recent breaking change in the
GitHub actions API. All the badges updated to add links to the appropriate
resources for end-user convenience. ([`0c23447`](https://github.com/python-semantic-release/python-semantic-release/commit/0c234475d27ad887b19170c82deb80293b3a95f1))

### Fix

* fix: update docs and default config for gitmoji changes (#590)

* fix: update docs and default config for gitmoji changes

PR #582 updated to the latest Gitmojis release however the documentation and
default config options still referenced old and unsupported Gitmojis.

* fix: update sphinx dep

I could only build the documentation locally by updating Sphinx to the latest
1.x version. ([`192da6e`](https://github.com/python-semantic-release/python-semantic-release/commit/192da6e1352298b48630423d50191070a1c5ab24))


## v7.33.4 (2023-05-14)

### Fix

* fix: if prerelease, publish prerelease (#587)

Co-authored-by: Ondrej Winter &lt;ondrej.winter@gmail.com&gt; ([`927da9f`](https://github.com/python-semantic-release/python-semantic-release/commit/927da9f8feb881e02bc08b33dc559bd8e7fc41ab))


## v7.33.3 (2023-04-24)

### Documentation

* docs: update repository name (#559)

In order to avoid &#39;Repository not found: relekang/python-semantic-release.&#39; ([`5cdb05e`](https://github.com/python-semantic-release/python-semantic-release/commit/5cdb05e20f17b12890e1487c42d317dcbadd06c8))

* docs: spelling and grammar in `travis.rst` (#556)

- spelling
- subject-verb agreement
- remove verbiage

Signed-off-by: Vladislav Doster &lt;mvdoster@gmail.com&gt; ([`3a76e9d`](https://github.com/python-semantic-release/python-semantic-release/commit/3a76e9d7505c421009eb3e953c32cccac2e70e07))

* docs: grammar in `docs/troubleshooting.rst` (#557)

- change contraction to a possessive pronoun

Signed-off-by: Vladislav Doster &lt;mvdoster@gmail.com&gt; ([`bbe754a`](https://github.com/python-semantic-release/python-semantic-release/commit/bbe754a3db9ce7132749e7902fe118b52f48ee42))

### Fix

* fix: update Gitmojis according to official node module (#582) ([`806fcfa`](https://github.com/python-semantic-release/python-semantic-release/commit/806fcfa4cfdd3df4b380afd015a68dc90d54215a))

* fix: trim emojis from config (#583) ([`02902f7`](https://github.com/python-semantic-release/python-semantic-release/commit/02902f73ee961565c2470c000f00947d9ef06cb1))


## v7.33.2 (2023-02-17)

### Fix

* fix: inconsistent versioning between print-version and publish (#524) ([`17d60e9`](https://github.com/python-semantic-release/python-semantic-release/commit/17d60e9bf66f62e5845065486c9d5e450f74839a))


## v7.33.1 (2023-02-01)

### Fix

* fix(action): mark container fs as safe for git (#552)

See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124 and https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956 ([`2a55f68`](https://github.com/python-semantic-release/python-semantic-release/commit/2a55f68e2b3cb9ffa9204c00ddbf12706af5c070))


## v7.33.0 (2023-01-15)

### Feature

* feat: add signing options to action ([`31ad5eb`](https://github.com/python-semantic-release/python-semantic-release/commit/31ad5eb5a25f0ea703afc295351104aefd66cac1))

* feat(repository): add support for TWINE_CERT (#522)

Fixes #521 ([`d56e85d`](https://github.com/python-semantic-release/python-semantic-release/commit/d56e85d1f2ac66fb0b59af2178164ca915dbe163))

* feat: Update action with configuration options (#518)

Co-authored-by: Kevin Watson &lt;Kevmo92@users.noreply.github.com&gt; ([`4664afe`](https://github.com/python-semantic-release/python-semantic-release/commit/4664afe5f80a04834e398fefb841b166a51d95b7))

### Fix

* fix: changelog release commit search logic (#530)

* Fixes changelog release commit search logic

Running `semantic-release changelog` currently fails to identify &#34;the last commit in [a] release&#34; because the compared commit messages have superfluous whitespace.
Likely related to the issue causing: https://github.com/relekang/python-semantic-release/issues/490

* Removes a couple of extra `strip()`s. ([`efb3410`](https://github.com/python-semantic-release/python-semantic-release/commit/efb341036196c39b4694ca4bfa56c6b3e0827c6c))

* fix: bump Dockerfile to use Python 3.10 image (#536)

Fixes #533

Co-authored-by: Bernard Cooke &lt;bernard.cooke@iotics.com&gt; ([`8f2185d`](https://github.com/python-semantic-release/python-semantic-release/commit/8f2185d570b3966b667ac591ae523812e9d2e00f))

* fix: fix mypy errors for publish ([`b40dd48`](https://github.com/python-semantic-release/python-semantic-release/commit/b40dd484387c1b3f78df53ee2d35e281e8e799c8))

* fix: formatting in docs ([`2e8227a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8227a8a933683250f8dace019df15fdb35a857))

* fix: update documentaton ([`5cbdad2`](https://github.com/python-semantic-release/python-semantic-release/commit/5cbdad296034a792c9bf05e3700eac4f847eb469))

* fix(action): fix environment variable names ([`3c66218`](https://github.com/python-semantic-release/python-semantic-release/commit/3c66218640044adf263fcf9b2714cfc4b99c2e90))


## v7.32.2 (2022-10-22)

### Documentation

* docs: fix code blocks (#506)

Previously: https://i.imgur.com/XWFhG7a.png ([`24b7673`](https://github.com/python-semantic-release/python-semantic-release/commit/24b767339fcef1c843f7dd3188900adab05e03b1))

### Fix

* fix: fix changelog generation in tag-mode (#171) ([`482a62e`](https://github.com/python-semantic-release/python-semantic-release/commit/482a62ec374208b2d57675cb0b7f0ab9695849b9))


## v7.32.1 (2022-10-07)

### Documentation

* docs: correct spelling mistakes (#504) ([`3717e0d`](https://github.com/python-semantic-release/python-semantic-release/commit/3717e0d8810f5d683847c7b0e335eeefebbf2921))

### Fix

* fix: corrections for deprecation warnings (#505) ([`d47afb6`](https://github.com/python-semantic-release/python-semantic-release/commit/d47afb6516238939e174f946977bf4880062a622))


## v7.32.0 (2022-09-25)

### Documentation

* docs: correct documented default behaviour for `commit_version_number` (#497) ([`ffae2dc`](https://github.com/python-semantic-release/python-semantic-release/commit/ffae2dc68f7f4bc13c5fd015acd43b457e568ada))

### Feature

* feat: add setting for enforcing textual changelog sections (#502)

Resolves #498

Add the `use_textual_changelog_sections` setting flag for enforcing that
changelog section headings will always be regular ASCII when using the Emoji
parser. ([`988437d`](https://github.com/python-semantic-release/python-semantic-release/commit/988437d21e40d3e3b1c95ed66b535bdd523210de))


## v7.31.4 (2022-08-23)

### Fix

* fix: account for trailing newlines in commit messages (#495)

Fixes #490 ([`111b151`](https://github.com/python-semantic-release/python-semantic-release/commit/111b1518e8c8e2bd7535bd4c4b126548da384605))


## v7.31.3 (2022-08-22)

### Fix

* fix: use `commit_subject` when searching for release commits (#488)

Co-authored-by: Dzmitry Ryzhykau &lt;d.ryzhykau@onesoil.ai&gt; ([`3849ed9`](https://github.com/python-semantic-release/python-semantic-release/commit/3849ed992c3cff9054b8690bcf59e49768f84f47))


## v7.31.2 (2022-07-29)

### Documentation

* docs: Add example for pyproject.toml ([`2a4b8af`](https://github.com/python-semantic-release/python-semantic-release/commit/2a4b8af1c2893a769c02476bb92f760c8522bd7a))

### Fix

* fix: Add better handling of missing changelog placeholder

There is still one case where we don&#39;t add it, but in those
corner cases it would be better to do it manually than to make it
mangled.

Fixes #454 ([`e7a0e81`](https://github.com/python-semantic-release/python-semantic-release/commit/e7a0e81c004ade73ed927ba4de8c3e3ccaf0047c))

* fix: Add repo=None when not in git repo

Fixes #422 ([`40be804`](https://github.com/python-semantic-release/python-semantic-release/commit/40be804c09ab8a036fb135c9c38a63f206d2742c))


## v7.31.1 (2022-07-29)

### Fix

* fix: Update git email in action

Fixes #473 ([`0ece6f2`](https://github.com/python-semantic-release/python-semantic-release/commit/0ece6f263ff02a17bb1e00e7ed21c490f72e3d00))


## v7.31.0 (2022-07-29)

### Feature

* feat: override repository_url w REPOSITORY_URL env var (#439) ([`cb7578c`](https://github.com/python-semantic-release/python-semantic-release/commit/cb7578cf005b8bd65d9b988f6f773e4c060982e3))

* feat: add prerelease-patch and no-prerelease-patch flags for whether to auto-bump prereleases ([`b4e5b62`](https://github.com/python-semantic-release/python-semantic-release/commit/b4e5b626074f969e4140c75fdac837a0625cfbf6))

### Fix

* fix: :bug: fix get_current_release_version for tag_only version_source ([`cad09be`](https://github.com/python-semantic-release/python-semantic-release/commit/cad09be9ba067f1c882379c0f4b28115a287fc2b))


## v7.30.2 (2022-07-26)

### Fix

* fix: declare additional_options as action inputs (#481) ([`cb5d8c7`](https://github.com/python-semantic-release/python-semantic-release/commit/cb5d8c7ce7d013fcfabd7696b5ffb846a8a6f853))


## v7.30.1 (2022-07-25)

### Fix

* fix: don&#39;t use commit_subject for tag pattern matching (#480) ([`ac3f11e`](https://github.com/python-semantic-release/python-semantic-release/commit/ac3f11e689f4a290d20b68b9c5c214098eb61b5f))


## v7.30.0 (2022-07-25)

### Feature

* feat: add `additional_options` input for GitHub Action (#477) ([`aea60e3`](https://github.com/python-semantic-release/python-semantic-release/commit/aea60e3d290c6fe3137bff21e0db1ed936233776))

### Fix

* fix: allow empty additional options (#479) ([`c9b2514`](https://github.com/python-semantic-release/python-semantic-release/commit/c9b2514d3e164b20e78b33f60989d78c2587e1df))


## v7.29.7 (2022-07-24)

### Fix

* fix: ignore dependency version bumps when parsing version from commit logs (#476) ([`51bcb78`](https://github.com/python-semantic-release/python-semantic-release/commit/51bcb780a9f55fadfaf01612ff65c1f92642c2c1))


## v7.29.6 (2022-07-15)

### Fix

* fix: allow changing prerelease tag using CLI flags (#466)

Delay construction of version and release patterns until runtime.
This will allow to use non-default prerelease tag.

Co-authored-by: Dzmitry Ryzhykau &lt;d.ryzhykau@onesoil.ai&gt; ([`395bf4f`](https://github.com/python-semantic-release/python-semantic-release/commit/395bf4f2de73663c070f37cced85162d41934213))


## v7.29.5 (2022-07-14)

### Fix

* fix(publish): get version bump for current release (#467)

Replicate the behavior of &#34;version&#34; command in version calculation.

Co-authored-by: Dzmitry Ryzhykau &lt;d.ryzhykau@onesoil.ai&gt; ([`dd26888`](https://github.com/python-semantic-release/python-semantic-release/commit/dd26888a923b2f480303c19f1916647de48b02bf))

* fix: add packaging module requirement (#469) ([`b99c9fa`](https://github.com/python-semantic-release/python-semantic-release/commit/b99c9fa88dc25e5ceacb131cd93d9079c4fb2c86))


## v7.29.4 (2022-06-29)

### Fix

* fix: add text for empty ValueError (#461) ([`733254a`](https://github.com/python-semantic-release/python-semantic-release/commit/733254a99320d8c2f964d799ac4ec29737867faa))


## v7.29.3 (2022-06-26)

### Fix

* fix: Ensure that assets can be uploaded successfully on custom GitHub servers (#458)

Signed-off-by: Chris Butler &lt;cbutler@australiacloud.com.au&gt; ([`32b516d`](https://github.com/python-semantic-release/python-semantic-release/commit/32b516d7aded4afcafe4aa56d6a5a329b3fc371d))


## v7.29.2 (2022-06-20)

### Fix

* fix: ensure should_bump checks against release version if not prerelease (#457)

Co-authored-by: Sebastian Seith &lt;sebastian@vermill.io&gt; ([`da0606f`](https://github.com/python-semantic-release/python-semantic-release/commit/da0606f0d67ada5f097c704b9423ead3b5aca6b2))


## v7.29.1 (2022-06-01)

### Fix

* fix: Capture correct release version when patch has more than one digit (#448) ([`426cdc7`](https://github.com/python-semantic-release/python-semantic-release/commit/426cdc7d7e0140da67f33b6853af71b2295aaac2))


## v7.29.0 (2022-05-27)

### Feature

* feat: allow using ssh-key to push version while using token to publish to hvcs (#419)

* feat(config): add ignore_token_for_push param

Add ignore_token_for_push parameter that allows using the underlying
git authentication mechanism for pushing a new version commit and tags
while also using an specified token to upload dists

* test(config): add test for ignore_token_for_push

Test push_new_version with token while ignore_token_for_push is True
and False

* docs: add documentation for ignore_token_for_push

* fix(test): override GITHUB_ACTOR env

push_new_version is using GITHUB_ACTOR env var but we did not
contemplate in our new tests that actually Github actions running the
tests will populate that var and change the test outcome

Now we control the value of that env var and test for it being present
or not ([`7b2dffa`](https://github.com/python-semantic-release/python-semantic-release/commit/7b2dffadf43c77d5e0eea307aefcee5c7744df5c))

### Fix

* fix: fix and refactor prerelease (#435) ([`94c9494`](https://github.com/python-semantic-release/python-semantic-release/commit/94c94942561f85f48433c95fd3467e03e0893ab4))


## v7.28.1 (2022-04-14)

### Fix

* fix: fix getting current version when `version_source=tag_only` (#437) ([`b247936`](https://github.com/python-semantic-release/python-semantic-release/commit/b247936a81c0d859a34bf9f17ab8ca6a80488081))


## v7.28.0 (2022-04-11)

### Feature

* feat: add `tag_only` option for `version_source` (#436)

Fixes #354 ([`cf74339`](https://github.com/python-semantic-release/python-semantic-release/commit/cf743395456a86c62679c2c0342502af043bfc3b))


## v7.27.1 (2022-04-03)

### Fix

* fix(prerelase): pass prerelease option to get_current_version (#432)

The `get_current_version` function accepts a `prerelease` argument which
was never passed. ([`aabab0b`](https://github.com/python-semantic-release/python-semantic-release/commit/aabab0b7ce647d25e0c78ae6566f1132ece9fcb9))


## v7.27.0 (2022-03-15)

### Feature

* feat: add git-lfs to docker container (#427) ([`184e365`](https://github.com/python-semantic-release/python-semantic-release/commit/184e3653932979b82e5a62b497f2a46cbe15ba87))


## v7.26.0 (2022-03-07)

### Feature

* feat: add prerelease functionality (#413)

* chore: add initial todos
* feat: add prerelease tag option
* feat: add prerelease cli flag
* feat: omit_pattern for previouse and current version getters
* feat: print_version with prerelease bump
* feat: make print_version prerelease ready
* feat: move prerelease determination to get_new_version
* test: improve get_last_version test
* docs: added basic infos about prereleases
* feat: add prerelease flag to version and publish
* feat: remove leftover todos

Co-authored-by: Mario Jäckle &lt;m.jaeckle@careerpartner.eu&gt; ([`7064265`](https://github.com/python-semantic-release/python-semantic-release/commit/7064265627a2aba09caa2873d823b594e0e23e77))


## v7.25.2 (2022-02-24)

### Fix

* fix(gitea): use form-data from asset upload (#421) ([`e011944`](https://github.com/python-semantic-release/python-semantic-release/commit/e011944987885f75b80fe16a363f4befb2519a91))


## v7.25.1 (2022-02-23)

### Fix

* fix(gitea): build status and asset upload (#420)

* fix(gitea): handle list build status response
* fix(gitea): use form-data for upload_asset ([`57db81f`](https://github.com/python-semantic-release/python-semantic-release/commit/57db81f4c6b96da8259e3bad9137eaccbcd10f6e))


## v7.25.0 (2022-02-17)

### Documentation

* docs: document tag_commit

Fixes #410 ([`b631ca0`](https://github.com/python-semantic-release/python-semantic-release/commit/b631ca0a79cb2d5499715d43688fc284cffb3044))

### Feature

* feat(hvcs): add gitea support (#412) ([`b7e7936`](https://github.com/python-semantic-release/python-semantic-release/commit/b7e7936331b7939db09abab235c8866d800ddc1a))


## v7.24.0 (2022-01-24)

### Feature

* feat: include additional changes in release commits

Add new config keys, `pre_commit_command` and `commit_additional_files`,
to allow custom file changes alongside the release commits. ([`3e34f95`](https://github.com/python-semantic-release/python-semantic-release/commit/3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9))


## v7.23.0 (2021-11-30)

### Feature

* feat: Support Github Enterprise server ([`b4e01f1`](https://github.com/python-semantic-release/python-semantic-release/commit/b4e01f1b7e841263fa84f57f0ac331f7c0b31954))


## v7.22.0 (2021-11-21)

### Feature

* feat(parser_angular): allow customization in parser

- `parser_angular_allowed_types` controls allowed types
  - defaults stay the same: build, chore, ci, docs, feat, fix, perf, style,
    refactor, test
- `parser_angular_default_level_bump` controls the default level to bump the
  version by
  - default stays at 0
- `parser_angular_minor_types` controls which types trigger a minor version
  bump
  - default stays at only &#39;feat&#39;
- `parser_angular_patch_types` controls which types trigger a patch version
  - default stays at &#39;fix&#39; or &#39;perf&#39; ([`298eebb`](https://github.com/python-semantic-release/python-semantic-release/commit/298eebbfab5c083505036ba1df47a5874a1eed6e))

### Fix

* fix: address PR feedback for `parser_angular.py`

- `angular_parser_default_level_bump` should have plain-english
  settings
- rename `TYPES` variable to `LONG_TYPE_NAMES` ([`f7bc458`](https://github.com/python-semantic-release/python-semantic-release/commit/f7bc45841e6a5c762f99f936c292cee25fabcd02))


## v7.21.0 (2021-11-21)


## v7.20.0 (2021-11-21)

### Documentation

* docs: clean typos and add section for repository upload

Add more details and external links ([`1efa18a`](https://github.com/python-semantic-release/python-semantic-release/commit/1efa18a3a55134d6bc6e4572ab025e24082476cd))

### Feature

* feat: rewrite Twine adapter for uploading to artifact repositories

Artifact upload generalised to fully support custom repositories like
GitLab. Rewritten to use twine python api instead of running the
executable. No-op mode now respected by artifact upload. ([`cfb20af`](https://github.com/python-semantic-release/python-semantic-release/commit/cfb20af79a8e25a77aee9ff72deedcd63cb7f62f))

* feat: allow custom environment variable names (#392)

* GH_TOKEN can now be customized by setting github_token_var
* GL_TOKEN can now be customized by setting gitlab_token_var
* PYPI_PASSWORD can now be customized by setting pypi_pass_var
* PYPI_TOKEN can now be customized by setting pypi_token_var
* PYPI_USERNAME can now be customized by setting pypi_user_var ([`372cda3`](https://github.com/python-semantic-release/python-semantic-release/commit/372cda3497f16ead2209e6e1377d38f497144883))

* feat: use gitlab-ci or github actions env vars

return owner and project name from Gitlab/Github environment variables if available

Issue #363 ([`8ca8dd4`](https://github.com/python-semantic-release/python-semantic-release/commit/8ca8dd40f742f823af147928bd75a9577c50d0fd))

### Fix

* fix: mypy errors in vcs_helpers ([`13ca0fe`](https://github.com/python-semantic-release/python-semantic-release/commit/13ca0fe650125be2f5e953f6193fdc4d44d3c75a))

* fix: remove invalid repository exception ([`746b62d`](https://github.com/python-semantic-release/python-semantic-release/commit/746b62d4e207a5d491eecd4ca96d096eb22e3bed))

* fix: skip removing the build folder if it doesn&#39;t exist

https://github.com/relekang/python-semantic-release/issues/391#issuecomment-950667599 ([`8e79fdc`](https://github.com/python-semantic-release/python-semantic-release/commit/8e79fdc107ffd852a91dfb5473e7bd1dfaba4ee5))

* fix: don&#39;t use linux commands on windows (#393) ([`5bcccd2`](https://github.com/python-semantic-release/python-semantic-release/commit/5bcccd21cc8be3289db260e645fec8dc6a592abd))


## v7.19.2 (2021-09-04)

### Fix

* fix: Fixed ImproperConfig import error (#377) ([`b011a95`](https://github.com/python-semantic-release/python-semantic-release/commit/b011a9595df4240cb190bfb1ab5b6d170e430dfc))


## v7.19.1 (2021-08-17)

### Fix

* fix: add get_formatted_tag helper instead of hardcoded v-prefix in the git tags ([`1a354c8`](https://github.com/python-semantic-release/python-semantic-release/commit/1a354c86abad77563ebce9a6944256461006f3c7))


## v7.19.0 (2021-08-16)

### Documentation

* docs(parser): documentation for scipy-parser ([`45ee34a`](https://github.com/python-semantic-release/python-semantic-release/commit/45ee34aa21443860a6c2cd44a52da2f353b960bf))

### Feature

* feat: custom git tag format support (#373)

* feat: custom git tag format support
* test: add git tag format check
* docs: add tag_format config option ([`1d76632`](https://github.com/python-semantic-release/python-semantic-release/commit/1d76632043bf0b6076d214a63c92013624f4b95e))


## v7.18.0 (2021-08-09)

### Documentation

* docs: clarify second argument of ParsedCommit ([`086ddc2`](https://github.com/python-semantic-release/python-semantic-release/commit/086ddc28f06522453328f5ea94c873bd202ff496))

### Feature

* feat: Add support for non-prefixed tags (#366) ([`0fee4dd`](https://github.com/python-semantic-release/python-semantic-release/commit/0fee4ddb5baaddf85ed6b76e76a04474a5f97d0a))


## v7.17.0 (2021-08-07)

### Feature

* feat(parser): add scipy style parser (#369) ([`51a3921`](https://github.com/python-semantic-release/python-semantic-release/commit/51a39213ea120c4bbd7a57b74d4f0cc3103da9f5))


## v7.16.4 (2021-08-03)

### Fix

* fix: correct rendering of gitlab issue references

resolves #358 ([`07429ec`](https://github.com/python-semantic-release/python-semantic-release/commit/07429ec4a32d32069f25ec77b4bea963bd5d2a00))


## v7.16.3 (2021-07-29)

### Fix

* fix: print right info if token is not set (#360) (#361)

Co-authored-by: Laercio Barbosa &lt;laercio.barbosa@scania.com&gt; ([`a275a7a`](https://github.com/python-semantic-release/python-semantic-release/commit/a275a7a17def85ff0b41d254e4ee42772cce1981))


## v7.16.2 (2021-06-25)

### Documentation

* docs: update trove classifiers to reflect supported versions (#344) ([`7578004`](https://github.com/python-semantic-release/python-semantic-release/commit/7578004ed4b20c2bd553782443dfd77535faa377))

* docs: recommend setting a concurrency group for GitHub Actions ([`34b0735`](https://github.com/python-semantic-release/python-semantic-release/commit/34b07357ab3f4f4aa787b71183816ec8aaf334a8))

### Fix

* fix: use release-api for gitlab ([`1ef5cab`](https://github.com/python-semantic-release/python-semantic-release/commit/1ef5caba2d8dd0f2647bc51ede0ef7152d8b7b8d))


## v7.16.1 (2021-06-08)

### Fix

* fix: tomlkit should stay at 0.7.0

See https://github.com/relekang/python-semantic-release/pull/339#discussion_r647629387 ([`769a5f3`](https://github.com/python-semantic-release/python-semantic-release/commit/769a5f31115cdb1f43f19a23fe72b96a8c8ba0fc))


## v7.16.0 (2021-06-08)

### Feature

* feat: add option to omit tagging (#341) ([`20603e5`](https://github.com/python-semantic-release/python-semantic-release/commit/20603e53116d4f05e822784ce731b42e8cbc5d8f))


## v7.15.6 (2021-06-08)

### Fix

* fix: update click and tomlkit (#339) ([`947ea3b`](https://github.com/python-semantic-release/python-semantic-release/commit/947ea3bc0750735941446cf4a87bae20e750ba12))


## v7.15.5 (2021-05-26)

### Fix

* fix: pin tomlkit to 0.7.0 ([`2cd0db4`](https://github.com/python-semantic-release/python-semantic-release/commit/2cd0db4537bb9497b72eb496f6bab003070672ab))


## v7.15.4 (2021-04-29)

### Fix

* fix: Change log level of failed toml loading

Fixes #235 ([`24bb079`](https://github.com/python-semantic-release/python-semantic-release/commit/24bb079cbeff12e7043dd35dd0b5ae03192383bb))


## v7.15.3 (2021-04-03)

### Fix

* fix: Add venv to path in github action ([`583c5a1`](https://github.com/python-semantic-release/python-semantic-release/commit/583c5a13e40061fc544b82decfe27a6c34f6d265))


## v7.15.2 (2021-04-03)

### Documentation

* docs: clarify that HVCS should be lowercase

Fixes #330 ([`da0ab0c`](https://github.com/python-semantic-release/python-semantic-release/commit/da0ab0c62c4ce2fa0d815e5558aeec1a1e23bc89))

### Fix

* fix: Use absolute path for venv in github action ([`d4823b3`](https://github.com/python-semantic-release/python-semantic-release/commit/d4823b3b6b1fcd5c33b354f814643c9aaf85a06a))

* fix: Set correct path for venv in action script ([`aac02b5`](https://github.com/python-semantic-release/python-semantic-release/commit/aac02b5a44a6959328d5879578aa3536bdf856c2))

* fix: Run semantic-release in virtualenv in the github action

Fixes #331 ([`b508ea9`](https://github.com/python-semantic-release/python-semantic-release/commit/b508ea9f411c1cd4f722f929aab9f0efc0890448))


## v7.15.1 (2021-03-26)

### Documentation

* docs: add common options to documentation

These can be found by running `semantic-release --help`, but including them
in the documentation will be helpful for CI users who don&#39;t have the command
installed locally.

Related to #327. ([`20d79a5`](https://github.com/python-semantic-release/python-semantic-release/commit/20d79a51bffa26d40607c1b77d10912992279112))

### Fix

* fix: Add support for setting build_command to &#34;false&#34;

Fixes #328 ([`520cf1e`](https://github.com/python-semantic-release/python-semantic-release/commit/520cf1eaa7816d0364407dbd17b5bc7c79806086))

* fix: Upgrade python-gitlab range

Keeping both 1.x and 2.x since only change that is breaking is dropping
python 3.6 support. I hope that leaving the lower limit will make it
still work with python 3.6.

Fixes #329 ([`abfacc4`](https://github.com/python-semantic-release/python-semantic-release/commit/abfacc432300941d57488842e41c06d885637e6c))


## v7.15.0 (2021-02-18)

### Documentation

* docs: add documentation for releasing on a Jenkins instance (#324) ([`77ad988`](https://github.com/python-semantic-release/python-semantic-release/commit/77ad988a2057be59e4559614a234d6871c06ee37))

### Feature

* feat: allow the use of .pypirc for twine uploads (#325) ([`6bc56b8`](https://github.com/python-semantic-release/python-semantic-release/commit/6bc56b8aa63069a25a828a2d1a9038ecd09b7d5d))


## v7.14.0 (2021-02-11)

### Documentation

* docs: correct casing on proper nouns (#320)

* docs: correcting Semantic Versioning casing

Semantic Versioning is the name of the specification.
Therefore it is a proper noun.
This patch corrects the incorrect casing for Semantic Versioning.

* docs: correcting Python casing

This patch corrects the incorrect casing for Python. ([`d51b999`](https://github.com/python-semantic-release/python-semantic-release/commit/d51b999a245a4e56ff7a09d0495c75336f2f150d))

### Feature

* feat(checks): add support for Jenkins CI (#322)

Includes a ci check handler to verify jenkins.
Unlike other ci systems jenkins doesn&#39;t generally prefix things with
`JENKINS` or simply inject `JENKINS=true` Really the only thing that is
immediately identifiable is `JENKINS_URL` ([`3e99855`](https://github.com/python-semantic-release/python-semantic-release/commit/3e99855c6bc72b3e9a572c58cc14e82ddeebfff8))


## v7.13.2 (2021-01-29)

### Documentation

* docs: fix `version_toml` example for Poetry (#318) ([`39acb68`](https://github.com/python-semantic-release/python-semantic-release/commit/39acb68bfffe8242040e476893639ba26fa0d6b5))

### Fix

* fix: fix crash when TOML has no PSR section (#319)

* test: reproduce issue with TOML without PSR section

* fix: crash when TOML has no PSR section

* chore: remove unused imports ([`5f8ab99`](https://github.com/python-semantic-release/python-semantic-release/commit/5f8ab99bf7254508f4b38fcddef2bdde8dd15a4c))


## v7.13.1 (2021-01-26)

### Fix

* fix: use multiline version_pattern match in replace (#315)

Fixes #306 ([`1a85af4`](https://github.com/python-semantic-release/python-semantic-release/commit/1a85af434325ce52e11b49895e115f7a936e417e))


## v7.13.0 (2021-01-26)

### Feature

* feat: support toml files for version declaration (#307)

This introduce a new `version_toml` configuration property that behaves
like `version_pattern` and `version_variable`.

For poetry support, user should now set `version_toml = pyproject.toml:tool.poetry.version`.

This introduce an ABC class, `VersionDeclaration`, that
can be implemented to add other version declarations with ease.

`toml` dependency has been replaced by `tomlkit`, as this is used
the library used by poetry to generate the `pyproject.toml` file, and
is able to keep the ordering of data defined in the file.

Existing `VersionPattern` class has been renamed to
`PatternVersionDeclaration` and now implements `VersionDeclaration`.

`load_version_patterns()` function has been renamed to
`load_version_declarations()` and now return a list of
`VersionDeclaration` implementations.

Close #245
Close #275 ([`9b62a7e`](https://github.com/python-semantic-release/python-semantic-release/commit/9b62a7e377378667e716384684a47cdf392093fa))


## v7.12.0 (2021-01-25)

### Documentation

* docs(actions): PAT must be passed to checkout step too

Fixes #311 ([`e2d8e47`](https://github.com/python-semantic-release/python-semantic-release/commit/e2d8e47d2b02860881381318dcc088e150c0fcde))

### Feature

* feat(github): retry GitHub API requests on failure (#314)

* refactor(github): use requests.Session to call raise_for_status

* fix(github): add retries to github API requests ([`ac241ed`](https://github.com/python-semantic-release/python-semantic-release/commit/ac241edf4de39f4fc0ff561a749fa85caaf9e2ae))


## v7.11.0 (2021-01-08)

### Build

* build: add __main__.py magic file

This file allow to run the package from sources properly with
`python -m semantic_release`. ([`e93f36a`](https://github.com/python-semantic-release/python-semantic-release/commit/e93f36a7a10e48afb42c1dc3d860a5e2a07cf353))

### Feature

* feat(print-version): add print-version command to output version

This new command can be integrated in the build process before the
effective release, ie. to rename some files with the version number.

Users may invoke `VERSION=$(semantic-release print-version)` to retrieve the
version that will be generated during the release before it really occurs. ([`512e3d9`](https://github.com/python-semantic-release/python-semantic-release/commit/512e3d92706055bdf8d08b7c82927d3530183079))

### Fix

* fix(actions): fix github actions with new main location ([`6666672`](https://github.com/python-semantic-release/python-semantic-release/commit/6666672d3d97ab7cdf47badfa3663f1a69c2dbdf))

* fix: avoid Unknown bump level 0 message

This issue occurs when some commits are available but are all to level 0. ([`8ab624c`](https://github.com/python-semantic-release/python-semantic-release/commit/8ab624cf3508b57a9656a0a212bfee59379d6f8b))

* fix: add dot to --define option help ([`eb4107d`](https://github.com/python-semantic-release/python-semantic-release/commit/eb4107d2efdf8c885c8ae35f48f1b908d1fced32))


## v7.10.0 (2021-01-08)

### Documentation

* docs: fix incorrect reference syntax ([`42027f0`](https://github.com/python-semantic-release/python-semantic-release/commit/42027f0d2bb64f4c9eaec65112bf7b6f67568e60))

* docs: rewrite getting started page ([`97a9046`](https://github.com/python-semantic-release/python-semantic-release/commit/97a90463872502d1207890ae1d9dd008b1834385))

### Feature

* feat(build): allow falsy values for build_command to disable build step ([`c07a440`](https://github.com/python-semantic-release/python-semantic-release/commit/c07a440f2dfc45a2ad8f7c454aaac180c4651f70))

* feat(repository): Add to settings artifact repository

- Add new config var to set repository (repository_url)
- Remove &#39;Pypi&#39; word when it refers generically to an artifact repository system
- Depreciate &#39;PYPI_USERNAME&#39; and &#39;PYPI_PASSWORD&#39; and prefer &#39;REPOSITORY_USERNAME&#39; and &#39;REPOSITORY_PASSWORD&#39; env vars
- Depreciate every config key with &#39;pypi&#39; and prefer repository
- Update doc in accordance with those changes ([`f4ef373`](https://github.com/python-semantic-release/python-semantic-release/commit/f4ef3733b948282fba5a832c5c0af134609b26d2))


## v7.9.0 (2020-12-21)

### Feature

* feat(hvcs): add hvcs_domain config option

While Gitlab already has an env var that should provide the vanity URL,
this supports a generic &#39;hvcs_domain&#39; parameter that makes the hostname
configurable for both GHE and Gitlab.

This will also use the configured hostname (from either source) in the
changelog links

Fixes: #277 ([`ab3061a`](https://github.com/python-semantic-release/python-semantic-release/commit/ab3061ae93c49d71afca043b67b361e2eb2919e6))

### Fix

* fix(history): coerce version to string (#298)

The changes in #297 mistakenly omitted coercing the return value to a
string. This resulted in errors like:
&#34;can only concatenate str (not &#34;VersionInfo&#34;) to str&#34;

Add test case asserting it&#39;s type str ([`d4cdc3d`](https://github.com/python-semantic-release/python-semantic-release/commit/d4cdc3d3cd2d93f2a78f485e3ea107ac816c7d00))

* fix(history): require semver &gt;= 2.10

This resolves deprecation warnings, and updates this to a more 3.x
compatible syntax ([`5087e54`](https://github.com/python-semantic-release/python-semantic-release/commit/5087e549399648cf2e23339a037b33ca8b62d954))


## v7.8.2 (2020-12-19)

### Fix

* fix(cli): skip remove_dist where not needed

Skip removing dist files when upload_pypi or upload_release are not set ([`04817d4`](https://github.com/python-semantic-release/python-semantic-release/commit/04817d4ecfc693195e28c80455bfbb127485f36b))


## v7.8.1 (2020-12-18)

### Fix

* fix(logs): fix TypeError when enabling debug logs

Some logger invocation were raising the following error:
TypeError: not all arguments converted during string formatting.

This also refactor some other parts to use f-strings as much as possible. ([`2591a94`](https://github.com/python-semantic-release/python-semantic-release/commit/2591a94115114c4a91a48f5b10b3954f6ac932a1))

* fix: filenames with unknown mimetype are now properly uploaded to github release

When mimetype can&#39;t be guessed, content-type header is set to None.
But it&#39;s mandatory for the file upload to work properly.
In this case, application/octect-stream is now used as a fallback. ([`f3ece78`](https://github.com/python-semantic-release/python-semantic-release/commit/f3ece78b2913e70f6b99907b192a1e92bbfd6b77))


## v7.8.0 (2020-12-18)

### Feature

* feat: add `upload_to_pypi_glob_patterns` option ([`42305ed`](https://github.com/python-semantic-release/python-semantic-release/commit/42305ed499ca08c819c4e7e65fcfbae913b8e6e1))

### Fix

* fix(netrc): prefer using token defined in GH_TOKEN instead of .netrc file

.netrc file will only be used when available and no GH_TOKEN environment variable is defined.

This also add a test to make sure .netrc is used properly when no GH_TOKEN is defined. ([`3af32a7`](https://github.com/python-semantic-release/python-semantic-release/commit/3af32a738f2f2841fd75ec961a8f49a0b1c387cf))

* fix(changelog): use &#34;issues&#34; link vs &#34;pull&#34;

While, e.g., https://github.com/owner/repos/pull/123 will work,
https://github.com/owner/repos/issues/123 should be safer / more
consistent, and should avoid a failure if someone adds an issue link at
the end of a PR that is merged via rebase merge or merge commit. ([`93e48c9`](https://github.com/python-semantic-release/python-semantic-release/commit/93e48c992cb8b763f430ecbb0b7f9c3ca00036e4))


## v7.7.0 (2020-12-12)

### Feature

* feat(changelog): add PR links in markdown (#282)

GitHub release notes automagically link to the PR, but changelog
markdown doesn&#39;t. Replace a PR number at the end of a message
with a markdown link. ([`0448f6c`](https://github.com/python-semantic-release/python-semantic-release/commit/0448f6c350bbbf239a81fe13dc5f45761efa7673))


## v7.6.0 (2020-12-06)

### Documentation

* docs: add documentation for option `major_on_zero` ([`2e8b26e`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8b26e4ee0316a2cf2a93c09c783024fcd6b3ba))

### Feature

* feat: add `major_on_zero` option

To control if bump major or not when current major version is zero. ([`d324154`](https://github.com/python-semantic-release/python-semantic-release/commit/d3241540e7640af911eb24c71e66468feebb0d46))


## v7.5.0 (2020-12-04)

### Feature

* feat(logs): include scope in changelogs (#281)

When the scope is set, include it in changelogs, e.g.
&#34;feat(x): some description&#34; becomes &#34;**x**: some description&#34;.
This is similar to how the Node semantic release (and
conventional-changelog-generator) generates changelogs.
If scope is not given, it&#39;s omitted.

Add a new config parameter changelog_scope to disable this behavior when
set to &#39;False&#39; ([`21c96b6`](https://github.com/python-semantic-release/python-semantic-release/commit/21c96b688cc44cc6f45af962ffe6d1f759783f37))


## v7.4.1 (2020-12-04)

### Fix

* fix: add &#34;changelog_capitalize&#34; to flags (#279)

Fixes #278 (or so I hope). ([`37716df`](https://github.com/python-semantic-release/python-semantic-release/commit/37716dfa78eb3f848f57a5100d01d93f5aafc0bf))


## v7.4.0 (2020-11-24)

### Documentation

* docs: fix broken internal references (#270) ([`da20b9b`](https://github.com/python-semantic-release/python-semantic-release/commit/da20b9bdd3c7c87809c25ccb2a5993a7ea209a22))

* docs: update links to Github docs (#268) ([`c53162e`](https://github.com/python-semantic-release/python-semantic-release/commit/c53162e366304082a3bd5d143b0401da6a16a263))

### Feature

* feat: add changelog_capitalize configuration

Fixes #260 ([`7cacca1`](https://github.com/python-semantic-release/python-semantic-release/commit/7cacca1eb436a7166ba8faf643b53c42bc32a6a7))


## v7.3.0 (2020-09-28)

### Documentation

* docs: fix docstring

Stumbled upon this docstring which first line seems copy/pasted from
the method above. ([`5a5e2cf`](https://github.com/python-semantic-release/python-semantic-release/commit/5a5e2cfb5e6653fb2e95e6e23e56559953b2c2b4))

### Feature

* feat: Generate `changelog.md` file (#266) ([`2587dfe`](https://github.com/python-semantic-release/python-semantic-release/commit/2587dfed71338ec6c816f58cdf0882382c533598))


## v7.2.5 (2020-09-16)

### Fix

* fix: add required to inputs in action metadata (#264)

According to the documentation, `inputs.&lt;input_id&gt;.required` is a
required field. ([`e76b255`](https://github.com/python-semantic-release/python-semantic-release/commit/e76b255cf7d3d156e3314fc28c54d63fa126e973))


## v7.2.4 (2020-09-14)

### Fix

* fix: Use range for toml dependency

Fixes #241 ([`45707e1`](https://github.com/python-semantic-release/python-semantic-release/commit/45707e1b7dcab48103a33de9d7f9fdb5a34dae4a))


## v7.2.3 (2020-09-12)

### Documentation

* docs: link to getting started guide in README ([`f490e01`](https://github.com/python-semantic-release/python-semantic-release/commit/f490e0194fa818db4d38c185bc5e6245bfde546b))

* docs: create &#39;getting started&#39; instructions (#256) ([`5f4d000`](https://github.com/python-semantic-release/python-semantic-release/commit/5f4d000c3f153d1d23128acf577e389ae879466e))

### Fix

* fix: support multiline version_pattern matching by default ([`82f7849`](https://github.com/python-semantic-release/python-semantic-release/commit/82f7849dcf29ba658e0cb3b5d21369af8bf3c16f))


## v7.2.2 (2020-07-26)

### Documentation

* docs: add quotation marks to the pip commands in CONTRIBUTING.rst (#253) ([`e20fa43`](https://github.com/python-semantic-release/python-semantic-release/commit/e20fa43098c06f5f585c81b9cd7e287dcce3fb5d))

### Fix

* fix(changelog): send changelog to stdout

Fixes #250 ([`87e2bb8`](https://github.com/python-semantic-release/python-semantic-release/commit/87e2bb881387ff3ac245ab9923347a5a616e197b))


## v7.2.1 (2020-06-29)

### Documentation

* docs: give example of multiple build commands (#248)

I had a little trouble figuring out how to use a non-setup.py build
command, so I thought it would be helpful to update the docs with an
example of how to do this. ([`65f1ffc`](https://github.com/python-semantic-release/python-semantic-release/commit/65f1ffcc6cac3bf382f4b821ff2be59d04f9f867))

### Fix

* fix: commit all files with bumped versions (#249) ([`b3a1766`](https://github.com/python-semantic-release/python-semantic-release/commit/b3a1766be7edb7d2eb76f2726d35ab8298688b3b))


## v7.2.0 (2020-06-15)

### Feature

* feat: bump versions in multiple files (#246)

- Add the `version_pattern` setting, which allows version numbers to be
  identified using arbitrary regular expressions.
- Refactor the config system to allow non-string data types to be
  specified in `pyproject.toml`.
- Multiple files can now be specified by setting `version_variable` or
  `version_pattern` to a list in `pyproject.toml`.

Fixes #175 ([`0ba2c47`](https://github.com/python-semantic-release/python-semantic-release/commit/0ba2c473c6e44cc326b3299b6ea3ddde833bdb37))


## v7.1.1 (2020-05-28)

### Fix

* fix(changelog): swap sha and message in table changelog ([`6741370`](https://github.com/python-semantic-release/python-semantic-release/commit/6741370ab09b1706ff6e19b9fbe57b4bddefc70d))


## v7.1.0 (2020-05-24)

### Feature

* feat(changelog): add changelog_table component (#242)

Add an alternative changelog component which displays each section as a
row in a table.

Fixes #237 ([`fe6a7e7`](https://github.com/python-semantic-release/python-semantic-release/commit/fe6a7e7fa014ffb827a1430dbcc10d1fc84c886b))


## v7.0.0 (2020-05-22)

### Breaking

* feat(changelog): add changelog components (#240)

* feat(changelog): add changelog components

Add the ability to configure sections of the changelog using a
`changelog_components` option.  Component outputs are separated by a blank
line and appear in the same order as they were configured.

It is possible to create your own custom components. Each component is a
function which returns either some text to be added, or None in which case it
will be skipped.

BREAKING CHANGE: The `compare_url` option has been removed in favor of using
`changelog_components`. This functionality is now available as the
`semantic_release.changelog.compare_url` component.

* docs: add documentation for changelog_components

* feat: pass changelog_sections to components

Changelog components may now receive the value of `changelog_sections`,
split and ready to use. ([`3e17a98`](https://github.com/python-semantic-release/python-semantic-release/commit/3e17a98d7fa8468868a87e62651ac2c010067711))

### Documentation

* docs: add conda-forge badge ([`e9536bb`](https://github.com/python-semantic-release/python-semantic-release/commit/e9536bbe119c9e3b90c61130c02468e0e1f14141))


## v6.4.1 (2020-05-15)

### Fix

* fix: convert \r\n to \n in commit messages

Fixes #239 ([`34acbbc`](https://github.com/python-semantic-release/python-semantic-release/commit/34acbbcd25320a9d18dcd1a4f43e1ce1837b2c9f))


## v6.4.0 (2020-05-15)

### Breaking

* feat(history): create emoji parser (#238)

Add a commit parser which uses emojis from https://gitmoji.carloscuesta.me/
to determine the type of change.

* fix: add emojis to default changelog_sections

* fix: include all parsed types in changelog

This allows emojis to appear in the changelog, as well as configuring
other types to appear with the Angular parser (I remember someone asking
for that feature a while ago). All filtering is now done in the
markdown_changelog function.

* refactor(history): get breaking changes in parser

Move the task of detecting breaking change descriptions into the commit
parser function, instead of during changelog generation.

This has allowed the emoji parser to also return the regular descriptions as
breaking change descriptions for commits with :boom:.

BREAKING CHANGE: Custom commit parser functions are now required to pass
a fifth argument to `ParsedCommit`, which is a list of breaking change
descriptions.

* docs: add documentation for emoji parser ([`2e1c50a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e1c50a865628b372f48945a039a3edb38a7cdf0))


## v6.3.1 (2020-05-11)

### Fix

* fix: use getboolean for commit_version_number

Fixes #186 ([`a60e0b4`](https://github.com/python-semantic-release/python-semantic-release/commit/a60e0b4e3cadf310c3e0ad67ebeb4e69d0ee50cb))


## v6.3.0 (2020-05-09)

### Documentation

* docs: rewrite commit-log-parsing.rst ([`4c70f4f`](https://github.com/python-semantic-release/python-semantic-release/commit/4c70f4f2aa3343c966d1b7ab8566fcc782242ab9))

* docs: document compare_link option ([`e52c355`](https://github.com/python-semantic-release/python-semantic-release/commit/e52c355c0d742ddd2cfa65d42888296942e5bec5))

### Feature

* feat(history): support linking compare page in changelog

Fixes #218 ([`79a8e02`](https://github.com/python-semantic-release/python-semantic-release/commit/79a8e02df82fbc2acecaad9e9ff7368e61df3e54))


## v6.2.0 (2020-05-02)

### Documentation

* docs: add = to verbosity option

Fixes #227 ([`a0f4c9c`](https://github.com/python-semantic-release/python-semantic-release/commit/a0f4c9cd397fcb98f880097319c08160adb3c3e6))

* docs: use references where possible

Fixes #221 ([`f38e5d4`](https://github.com/python-semantic-release/python-semantic-release/commit/f38e5d4a1597cddb69ce47a4d79b8774e796bf41))

### Feature

* feat(history): check all paragraphs for breaking changes

Check each paragraph of the commit&#39;s description for breaking changes,
instead of only a body and footer. This ensures that breaking changes
are detected when squashing commits together.

Fixes #200 ([`fec08f0`](https://github.com/python-semantic-release/python-semantic-release/commit/fec08f0dbd7ae15f95ca9c41a02c9fe6d448ede0))


## v6.1.0 (2020-04-26)

### Documentation

* docs: add documentation for PYPI_TOKEN ([`a8263a0`](https://github.com/python-semantic-release/python-semantic-release/commit/a8263a066177d1d42f2844e4cb42a76a23588500))

### Feature

* feat(actions): support PYPI_TOKEN on GitHub Actions

Add support for the new PYPI_TOKEN environment variable to be used on GitHub Actions. ([`df2c080`](https://github.com/python-semantic-release/python-semantic-release/commit/df2c0806f0a92186e914cfc8cc992171d74422df))

* feat(pypi): support easier use of API tokens

Allow setting the environment variable PYPI_TOKEN to automatically fill the username as __token__.

Fixes #213 ([`bac135c`](https://github.com/python-semantic-release/python-semantic-release/commit/bac135c0ae7a6053ecfc7cdf2942c3c89640debf))


## v6.0.1 (2020-04-15)

### Fix

* fix(hvcs): convert get_hvcs to use LoggedFunction

This was missed in 213530fb0c914e274b81d1dacf38ea7322b5b91f ([`3084249`](https://github.com/python-semantic-release/python-semantic-release/commit/308424933fd3375ca3730d9eaf8abbad2435830b))


## v6.0.0 (2020-04-15)

### Documentation

* docs: create Read the Docs config file ([`aa5a1b7`](https://github.com/python-semantic-release/python-semantic-release/commit/aa5a1b700a1c461c81c6434686cb6f0504c4bece))

* docs: include README.rst in index.rst

These files were very similar so it makes sense to simply include one 
inside the other. ([`8673a9d`](https://github.com/python-semantic-release/python-semantic-release/commit/8673a9d92a9bf348bb3409e002a830741396c8ca))

* docs: rewrite README.rst ([`e049772`](https://github.com/python-semantic-release/python-semantic-release/commit/e049772cf14cdd49538cf357db467f0bf3fe9587))

* docs: move action.rst into main documentation ([`509ccaf`](https://github.com/python-semantic-release/python-semantic-release/commit/509ccaf307a0998eced69ad9fee1807132babe28))

* docs: rewrite troubleshooting page ([`0285de2`](https://github.com/python-semantic-release/python-semantic-release/commit/0285de215a8dac3fcc9a51f555fa45d476a56dff))

### Unknown

* doc: updated doc with new ParsedCommit object instead of nested Tuple ([`ac565dc`](https://github.com/python-semantic-release/python-semantic-release/commit/ac565dc824ea575e8899b932db148ac28e27fce2))


## v5.2.0 (2020-04-09)

### Documentation

* docs: automate API docs

Automatically create pages in the API docs section using sphinx-autodoc. This is added as an event handler in conf.py. ([`7d4fea2`](https://github.com/python-semantic-release/python-semantic-release/commit/7d4fea266cc75007de51609131eb6d1e324da608))

### Feature

* feat(github): add tag as default release name ([`2997908`](https://github.com/python-semantic-release/python-semantic-release/commit/2997908f80f4fcec56917d237a079b961a06f990))


## v5.1.0 (2020-04-04)

### Documentation

* docs: update index.rst ([`b27c26c`](https://github.com/python-semantic-release/python-semantic-release/commit/b27c26c66e7e41843ab29076f7e724908091b46e))

* docs: improve formatting of envvars page ([`b376a56`](https://github.com/python-semantic-release/python-semantic-release/commit/b376a567bfd407a507ce0752614b0ca75a0f2973))

* docs: improve formatting of configuration page ([`9a8e22e`](https://github.com/python-semantic-release/python-semantic-release/commit/9a8e22e838d7dbf3bfd941397c3b39560aca6451))

### Feature

* feat(history): allow customizing changelog_sections (#207) ([`d5803d5`](https://github.com/python-semantic-release/python-semantic-release/commit/d5803d5c1668d86482a31ac0853bac7ecfdc63bc))


## v5.0.3 (2020-03-26)

### Fix

* fix: Bump dependencies and fix Windows issues on Development (#173)

* Bump dependencies and fix windows issues

* Correctly pass temp dir to test settings

* Remove print call on test settings

* chore: remove py34 and py35 classifiers

* chore: bump twine, requests and python-gitlab

* chore: update tox config to be more granular

* fix: missing mime types on Windows

* chore: bump circleCI and tox python to 3.8

* chore: remove py36 from tox envlist

* chore: isort errors ([`0a6f8c3`](https://github.com/python-semantic-release/python-semantic-release/commit/0a6f8c3842b05f5f424dad5ce1fa5e3823c7e688))


## v5.0.2 (2020-03-22)

### Fix

* fix(history): leave case of other characters unchanged

Previously, use of str.capitalize() would capitalize the first letter as expected, but all subsequent letters became lowercase. Now, the other letters remain unchanged. ([`96ba94c`](https://github.com/python-semantic-release/python-semantic-release/commit/96ba94c4b4593997343ec61ecb6c823c1494d0e2))


## v5.0.1 (2020-03-22)

### Fix

* fix: Make action use current version of semantic-release

This gives two benefits:
* In this repo it will work as a smoketest
* In other repos when they specify version int the github workflow they
will get the version they specify. ([`123984d`](https://github.com/python-semantic-release/python-semantic-release/commit/123984d735181c622f3d99088a1ad91321192a11))


## v5.0.0 (2020-03-22)

### Breaking

* feat(build): allow config setting for build command (#195)

* feat(build): allow config setting for build command

BREAKING CHANGE: Previously the build_commands configuration variable set the types of bundles sent to `python setup.py`. It has been replaced by the configuration variable `build_command` which takes the full command e.g. `python setup.py sdist` or `poetry build`.

Closes #188 ([`740f4bd`](https://github.com/python-semantic-release/python-semantic-release/commit/740f4bdb26569362acfc80f7e862fc2c750a46dd))

### Documentation

* docs(pypi): update docstings in pypi.py ([`6502d44`](https://github.com/python-semantic-release/python-semantic-release/commit/6502d448fa65e5dc100e32595e83fff6f62a881a))

### Fix

* fix: Rename default of build_command config ([`d5db22f`](https://github.com/python-semantic-release/python-semantic-release/commit/d5db22f9f7acd05d20fd60a8b4b5a35d4bbfabb8))


## v4.11.0 (2020-03-22)

### Documentation

* docs: make AUTHORS.rst dynamic ([`db2e076`](https://github.com/python-semantic-release/python-semantic-release/commit/db2e0762f3189d0f1a6ba29aad32bdefb7e0187f))

* docs(readme): fix minor typo ([`c22f69f`](https://github.com/python-semantic-release/python-semantic-release/commit/c22f69f62a215ff65e1ab6dcaa8e7e9662692e64))

### Feature

* feat(actions): create GitHub Action ([`350245d`](https://github.com/python-semantic-release/python-semantic-release/commit/350245dbfb07ed6a1db017b1d9d1072b368b1497))


## v4.10.0 (2020-03-03)

### Feature

* feat: make commit message configurable (#184) ([`eb0762c`](https://github.com/python-semantic-release/python-semantic-release/commit/eb0762ca9fea5cecd5c7b182504912a629be473b))


## v4.9.0 (2020-03-02)

### Feature

* feat(pypi): add build_commands config

Add a config option to set the commands passed to setup.py when building distributions. This allows for things like adding custom commands to the build process. ([`22146ea`](https://github.com/python-semantic-release/python-semantic-release/commit/22146ea4b94466a90d60b94db4cc65f46da19197))

### Fix

* fix(pypi): change bdist_wheels to bdist_wheel

Change the incorrect command bdist_wheels to bdist_wheel. ([`c4db509`](https://github.com/python-semantic-release/python-semantic-release/commit/c4db50926c03f3d551c8331932c567c7bdaf4f3d))


## v4.8.0 (2020-02-28)

### Feature

* feat(git): Add a new config for commit author ([`aa2c22c`](https://github.com/python-semantic-release/python-semantic-release/commit/aa2c22c469448fe57f02bea67a02f998ce519ac3))


## v4.7.1 (2020-02-28)

### Fix

* fix: repair parsing of remotes in the gitlab ci format

Format is:
&#34;https://gitlab-ci-token:MySuperToken@gitlab.example.com/group/project.git&#34;

Problem was due to the regex modification for #179

Fixes #181 ([`0fddbe2`](https://github.com/python-semantic-release/python-semantic-release/commit/0fddbe2fb70d24c09ceddb789a159162a45942dc))


## v4.7.0 (2020-02-28)

### Feature

* feat: Upload distribution files to GitHub Releases (#177)

* refactor(github): create upload_asset function

Create a function to call the asset upload API. This will soon be used 
to upload assets specified by the user.

* refactor(github): infer Content-Type from file extension

Infer the Content-Type header based on the file extension instead of setting it manually.

* refactor(pypi): move building of dists to cli.py

Refactor to have the building/removal of distributions in cli.py instead 
of within the upload_to_pypi function. This makes way for uploading to 
other locations, such as GitHub Releases, too.

* feat(github): upload dists to release

Upload Python wheels to the GitHub release. Configured with the option 
upload_to_release, on by default if using GitHub.

* docs: document upload_to_release config option

* test(github): add tests for Github.upload_dists

* fix(github): fix upload of .whl files

Fix uploading of .whl files due to a missing MIME type (defined custom type as application/x-wheel+zip). Additionally, continue with other uploads even if one fails.

* refactor(cli): additional output during publish

Add some additional output during the publish command.

* refactor(github): move api calls to separate methods

Move each type of GitHub API request into its own method to improve readability.

Re-implementation of #172

* fix: post changelog after PyPI upload

Post the changelog in-between uploading to PyPI and uploading to GitHub Releases. This is so that if the PyPI upload fails, GitHub users will not be notified. GitHub uploads still need to be processed after creating the changelog as the release notes must be published to upload assets to them. ([`e427658`](https://github.com/python-semantic-release/python-semantic-release/commit/e427658e33abf518191498c3142a0f18d3150e07))

### Fix

* fix: support repository owner names containing dots

Fixes #179 ([`a6c4da4`](https://github.com/python-semantic-release/python-semantic-release/commit/a6c4da4c0e6bd8a37f64544f7813fa027f5054ed))

* fix(github): use application/octet-stream for .whl files

application/octet-stream is more generic, but it is better than using a non-official MIME type. ([`90a7e47`](https://github.com/python-semantic-release/python-semantic-release/commit/90a7e476a04d26babc88002e9035cad2ed485b07))


## v4.6.0 (2020-02-19)

### Feature

* feat(history): capitalize changelog messages

Capitalize the first letter of messages in the changelog regardless of 
whether they are capitalized in the commit itself. ([`1a8e306`](https://github.com/python-semantic-release/python-semantic-release/commit/1a8e3060b8f6d6362c27903dcfc69d17db5f1d36))

### Fix

* fix: Only overwrite with patch if bump is None

Fixes #159 ([`1daa4e2`](https://github.com/python-semantic-release/python-semantic-release/commit/1daa4e23ec2dd40c6b490849276524264787e24e))

* fix: Add more debug statements in logs ([`bc931ec`](https://github.com/python-semantic-release/python-semantic-release/commit/bc931ec46795fde4c1ccee004eec83bf73d5de7a))


## v4.5.1 (2020-02-16)

### Documentation

* docs: fix broken list in readme

Fix the syntax of a broken bullet-point list in README.rst. ([`7aa572b`](https://github.com/python-semantic-release/python-semantic-release/commit/7aa572b2a323ddbc69686309226395f40c52b469))

* docs: Add note about automatic releases in readme ([`e606e75`](https://github.com/python-semantic-release/python-semantic-release/commit/e606e7583a30167cf7679c6bcada2f9e768b3abe))

* docs: Update readme and getting started docs ([`07b3208`](https://github.com/python-semantic-release/python-semantic-release/commit/07b3208ff64301e544c4fdcb48314e49078fc479))

### Fix

* fix(github): send token in request header

Use an Authorization header instead of deprecated query parameter 
authorization.

Fixes relekang/python-semantic-release#167 ([`be9972a`](https://github.com/python-semantic-release/python-semantic-release/commit/be9972a7b1fb183f738fb31bd370adb30281e4d5))


## v4.5.0 (2020-02-08)

### Feature

* feat(history): enable colon defined version

The get_current_version_by_config_file  and the replace_version_string methods now check for both variables defined as &#34;variable= version&#34; and &#34;variable: version&#34;
This allows for using a yaml file to store the version.

Closes #165 ([`7837f50`](https://github.com/python-semantic-release/python-semantic-release/commit/7837f5036269328ef29996b9ea63cccd5a6bc2d5))

### Fix

* fix: Remove erroneous submodule ([`762bfda`](https://github.com/python-semantic-release/python-semantic-release/commit/762bfda728c266b8cd14671d8da9298fc99c63fb))

* fix(cli): --noop flag works when before command

The entry point of the app is changed from main() to entry().
Entry takes any arguments before commands and moves them to after commands, then calls main()

Closes #73 ([`4fcc781`](https://github.com/python-semantic-release/python-semantic-release/commit/4fcc781d1a3f9235db552f0f4431c9f5e638d298))


## v4.4.1 (2020-01-18)

### Fix

* fix: Add quotes around twine arguments

Fixes #163 ([`46a83a9`](https://github.com/python-semantic-release/python-semantic-release/commit/46a83a94b17c09d8f686c3ae7b199d7fd0e0e5e5))


## v4.4.0 (2020-01-17)

### Feature

* feat(parser): make BREAKING-CHANGE synonymous with BREAKING CHANGE

According to point 16 in the conventional commit specification, this
should be implemented. They especially mention the footer, but I kept
the body for backwards compatibility. This should probably be removed
one day. The regex is in the helpers to make it easier to re-use, but I
didn&#39;t updated parser_tag since it looks like a legacy parser. ([`beedccf`](https://github.com/python-semantic-release/python-semantic-release/commit/beedccfddfb360aeebef595342ee980446012ec7))

* feat(parser): add support for exclamation point for breaking changes

According to the documentation for conventional commits, breaking
changes can be described using exclamation points, just before the colon
between type/scope and subject. In that case, the breaking change footer
is optional, and the subject is used as description of the breaking
change. If the footer exists, it is used for the description.

Fixes #156 ([`a4f8a10`](https://github.com/python-semantic-release/python-semantic-release/commit/a4f8a10afcc358a8fbef83be2041129480350be2))

### Fix

* fix(github): add check for GITHUB_ACTOR for git push (#162) ([`c41e9bb`](https://github.com/python-semantic-release/python-semantic-release/commit/c41e9bb986d01b92d58419cbdc88489d630a11f1))


## v4.3.4 (2019-12-17)

### Fix

* fix: fallback to whole log if correct tag is not available (#157)

The method getting all commits to consider for the release will now test
whether the version in input is a valid reference. If it is not, it will
consider the whole log for the repository.

evaluate_version_bump will still consider a message starting with the
version number as a breaking condition to stop analyzing.

Fixes #51 ([`252bffd`](https://github.com/python-semantic-release/python-semantic-release/commit/252bffd3be7b6dfcfdb384d24cb1cd83d990fc9a))


## v4.3.3 (2019-11-06)

### Fix

* fix: Set version of click to &gt;=2.0,&lt;8.0. (#155)

* fix: Upgrade to click 7.0.

Fixes #117

* fix: Instead of requiring click 7.0, looks like all tests will pass with at least 2.0.

* Upstream is at ~=7.0, so let&#39;s set the range to less than 8.0.

* The string template has no variables, so remove the call to .format() ([`f07c7f6`](https://github.com/python-semantic-release/python-semantic-release/commit/f07c7f653be1c018e443f071d9a196d9293e9521))


## v4.3.2 (2019-10-05)

### Fix

* fix: update regex to get repository owner and name for project with dots

Remove the dot from the second capture group to allow project names
containing dots to be matched.
Instead of a greedy &#39;+&#39; operator, use &#39;*?&#39; to allow the second group to
give back the &#39;.git&#39; (to avoid including it in the project name)

Fixes #151 ([`2778e31`](https://github.com/python-semantic-release/python-semantic-release/commit/2778e316a0c0aa931b1012cb3862d04659c05e73))


## v4.3.1 (2019-09-29)

### Fix

* fix: support repo urls without git terminator ([`700e9f1`](https://github.com/python-semantic-release/python-semantic-release/commit/700e9f18dafde1833f482272a72bb80b54d56bb3))


## v4.3.0 (2019-09-06)

### Feature

* feat: allow users to get version from tag and write/commit bump to file

Before this commit, version was bumped in the file, but only committed
if version was obtained from `version_variable` (version_source == `commit`).
Also added a relevant test and a description for this new option.

Fixes #104 ([`1f9fe1c`](https://github.com/python-semantic-release/python-semantic-release/commit/1f9fe1cc7666d47cc0c348c4705b63c39bf10ecc))

* feat: make the vcs functionalities work with gitlab

Adds python-gitlab as requirement.
Refactored github specific methods while keeping default behavior.
Also removed an unused return value for post_release_changelog.
Also refactored the secret filtering method.
Updated the related tests.

Fixes #121 ([`82d555d`](https://github.com/python-semantic-release/python-semantic-release/commit/82d555d45b9d9e295ef3f9546a6ca2a38ca4522e))

* feat: allow the override of configuration options from cli

config can now be overriden with the &#34;-D&#34; flag.
Also adds the related tests and documentation.

Also introduces a fixture in tests/__init__.py that reloads module using
config. It is necessary since all tests run in the same environment.
A better way would be to box the execution of tests (using the --forked
option of pytest for example) but it does not work in non-unix systems.
Also some tests should not break if config is changed, but it is outside
of the scope of this issue.

Fixes #119 ([`f0ac82f`](https://github.com/python-semantic-release/python-semantic-release/commit/f0ac82fe59eb59a768a73a1bf2ea934b9d448c58))

* feat: add the possibility to load configuration from pyproject.toml

Adds the toml library to base requirements.
Also adds the related tests and documentation.
Also adds the description of the version_source configuration option

Relates to #119 ([`35f8bfe`](https://github.com/python-semantic-release/python-semantic-release/commit/35f8bfef443c8b69560c918f4b13bc766fb3daa2))

### Fix

* fix: update list of commit types to include build, ci and perf

Also added perf to the types that trigger a patch update

Fixes #145 ([`41ea12f`](https://github.com/python-semantic-release/python-semantic-release/commit/41ea12fa91f97c0046178806bce3be57c3bc2308))

* fix: manage subgroups in git remote url

This is a necessary fix for gitlab integration.
For an illustration of the need and use for this fix, test was edited.

Fixes #139
Fixes #140 ([`4b11875`](https://github.com/python-semantic-release/python-semantic-release/commit/4b118754729094e330389712cf863e1c6cefee69))


## v4.2.0 (2019-08-05)

### Feature

* feat: Add support for showing unreleased changelog

Fixes #134 ([`41ef794`](https://github.com/python-semantic-release/python-semantic-release/commit/41ef7947ad8a07392c96c7540980476e989c1d83))

* feat: Add support for configuring branch

Fixes #43 ([`14abb05`](https://github.com/python-semantic-release/python-semantic-release/commit/14abb05e7f878e88002f896812d66b4ea5c219d4))

* feat: Add configuration to customize handling of dists

Relates to #115 ([`2af6f41`](https://github.com/python-semantic-release/python-semantic-release/commit/2af6f41b21205bdd192514a434fca2feba17725a))

### Fix

* fix: Remove deletion of build folder

Fixes #115 ([`b45703d`](https://github.com/python-semantic-release/python-semantic-release/commit/b45703dad38c29b28575060b21e5fb0f8482c6b1))

* fix: updated the tag tests ([`3303eef`](https://github.com/python-semantic-release/python-semantic-release/commit/3303eefa49a0474bbd85df10ae186ccbf9090ec1))

* fix: kept setting new version for tag source ([`0e24a56`](https://github.com/python-semantic-release/python-semantic-release/commit/0e24a5633f8f94b48da97b011634d4f9d84f7b4b))

* fix: Add commit hash when generating breaking changes

Fixes #120 ([`0c74faf`](https://github.com/python-semantic-release/python-semantic-release/commit/0c74fafdfa81cf2e13db8f4dcf0a6f7347552504))

* fix: Upgrade click to 7.0 ([`2c5dd80`](https://github.com/python-semantic-release/python-semantic-release/commit/2c5dd809b84c2157a5e6cdcc773c43ec864f0328))


## v4.1.2 (2019-08-04)

### Documentation

* docs(circleci): point badge to master branch ([`9c7302e`](https://github.com/python-semantic-release/python-semantic-release/commit/9c7302e184a1bd88f39b3039691b55cd77f0bb07))

### Fix

* fix: Make sure the history only breaks loop for version commit

Fixes #135 ([`5dc6cfc`](https://github.com/python-semantic-release/python-semantic-release/commit/5dc6cfc634254f09997bb3cb0f17abd296e2c01f))

* fix: correct isort build fail

build fail:  https://circleci.com/gh/relekang/python-semantic-release/379 ([`0037210`](https://github.com/python-semantic-release/python-semantic-release/commit/00372100b527ff9308d9e43fe5c65cdf179dc4dc))

* fix(vcs): allow cli to be run from subdirectory ([`fb7bb14`](https://github.com/python-semantic-release/python-semantic-release/commit/fb7bb14300e483626464795b8ff4f033a194cf6f))

### Unknown

* Fix minor sematic typo ([`76123f4`](https://github.com/python-semantic-release/python-semantic-release/commit/76123f410180599a19e7c48da413880185bbea20))


## v4.1.1 (2019-02-15)

### Documentation

* docs: DEBUG usage and related

Debug functionality lack documentation.
Thoubleshooting is helped by documenting other
environment variables as well. ([`f08e594`](https://github.com/python-semantic-release/python-semantic-release/commit/f08e5943a9876f2d17a7c02f468720995c7d9ffd))

* docs: correct usage of changelog ([`f4f59b0`](https://github.com/python-semantic-release/python-semantic-release/commit/f4f59b08c73700c6ee04930221bfcb1355cbc48d))

* docs: describing the commands

The commands is lacking from the documentation. ([`b6fa04d`](https://github.com/python-semantic-release/python-semantic-release/commit/b6fa04db3044525a1ee1b5952fb175a706842238))

* docs: update url for commit guidelinesThe guidelines can now be found in theDEVELOPERS.md in angular. ([`90c1b21`](https://github.com/python-semantic-release/python-semantic-release/commit/90c1b217f86263301b91d19d641c7b348e37d960))


## v4.1.0 (2019-01-31)

### Documentation

* docs(readme): add testing instructions ([`bb352f5`](https://github.com/python-semantic-release/python-semantic-release/commit/bb352f5b6616cc42c9f2f2487c51dedda1c68295))

* docs: Add installation instructions for development (#106) ([`9168d0e`](https://github.com/python-semantic-release/python-semantic-release/commit/9168d0ea56734319a5d77e890f23ff6ba51cc97d))

### Feature

* feat(ci_checks): add support for bitbucket ([`9fc120d`](https://github.com/python-semantic-release/python-semantic-release/commit/9fc120d1a7e4acbbca609628e72651685108b364))

### Fix

* fix: Maintain version variable formatting on bump (#103)

Small change to the way the version is written to the config file it is read from.  This allows the formatting to be the same as before semantic-release changed it.

Prior behavior
`my_version_var=&#34;1.2.3&#34;` =&gt; `my_version_var = &#39;1.2.4&#39;`

New behavior
`my_version_var=&#34;1.2.3&#34;` =&gt; `my_version_var=&#34;1.2.4&#34;`

I am using python-semantic-release with a Julia project and this change will allow for consistent formatting in my Project.toml file where the version is maintained ([`bf63156`](https://github.com/python-semantic-release/python-semantic-release/commit/bf63156f60340614fae94c255fb2f097cf317b2b))

* fix: initialize git Repo from current folder

This allows to run the program also from inner repository folders ([`c7415e6`](https://github.com/python-semantic-release/python-semantic-release/commit/c7415e634c0affbe6396e0aa2bafe7c1b3368914))

* fix: Use same changelog code for command as post

See #27 for background. ([`248f622`](https://github.com/python-semantic-release/python-semantic-release/commit/248f62283c59182868c43ff105a66d85c923a894))


## v4.0.1 (2019-01-12)

### Documentation

* docs: Remove reference to gitter

Fixes #90 ([`896e37b`](https://github.com/python-semantic-release/python-semantic-release/commit/896e37b95cc43218e8f593325dd4ea63f8b895d9))

### Fix

* fix: Use correct syntax to exclude tests in package

This implements #92 without deleting __init__.py files. ([`3e41e91`](https://github.com/python-semantic-release/python-semantic-release/commit/3e41e91c318663085cd28c8165ece21d7e383475))

* fix: Filter out pypi secrets from exceptions

Fixes #41 ([`5918371`](https://github.com/python-semantic-release/python-semantic-release/commit/5918371c1e82b06606087c9945d8eaf2604a0578))

* fix: Clean out dist and build before building

This should fix the problem with uploading old versions.

Fixes #86 ([`b628e46`](https://github.com/python-semantic-release/python-semantic-release/commit/b628e466f86bc27cbe45ec27a02d4774a0efd3bb))

* fix: Add better error message when pypi credentials are empty

Fixes #96 ([`c4e5dcb`](https://github.com/python-semantic-release/python-semantic-release/commit/c4e5dcbeda0ce8f87d25faefb4d9ae3581029a8f))

* fix: Unfreeze dependencies

This uses ~= for most dependencies instead of pinning them.

Fixes #100 ([`847833b`](https://github.com/python-semantic-release/python-semantic-release/commit/847833bf48352a4935f906d0c3f75e1db596ca1c))

* fix(parser_angular): Fix non-match when special chars in scope ([`8a33123`](https://github.com/python-semantic-release/python-semantic-release/commit/8a331232621b26767e4268079f9295bf695047ab))


## v4.0.0 (2018-11-22)

### Breaking

* fix: Remove support for python 2

BREAKING CHANGE: This will only work with python 3 after this commit. ([`85fe638`](https://github.com/python-semantic-release/python-semantic-release/commit/85fe6384c15db317bc7142f4c8bbf2da58cece58))

* feat: Add support for commit_message config variable

This variable can allow you to skip CI pipelines in CI tools like GitLab
CI by adding [CI skip] in the body. There are likely many uses for this
beyond that particular example...

BREAKING CHANGE: If you rely on the commit message to be the version
number only, this will break your code

re #88 #32 ([`4de5400`](https://github.com/python-semantic-release/python-semantic-release/commit/4de540011ab10483ee1865f99c623526cf961bb9))

### Documentation

* docs: Add type hints and more complete docstrings

Includes a few style changes suggested by pylint and type safety checks
suggested by mypy

re #81 ([`a6d5e9b`](https://github.com/python-semantic-release/python-semantic-release/commit/a6d5e9b1ccbe75d59e7240528593978a19d8d040))

* docs: Fix typo in documentation index

The word role -- &#39;an actor&#39;s part in a play, movie, etc.&#39; does not fit
in this context. &#34;ready to roll&#34; is a phrase meaning &#34;fully prepared to
start functioning or moving&#34; or simply &#34;ready&#34;. I believe this is what
was meant to be written. ([`da6844b`](https://github.com/python-semantic-release/python-semantic-release/commit/da6844bce0070a0020bf13950bd136fe28262602))

### Feature

* feat(CI checks): Add support for GitLab CI checks

Check `GITLAB_CI` environment variable and then verify
`CI_COMMIT_REF_NAME` matches the given branch.

Includes tests

Closes #88  re #32 ([`8df5e2b`](https://github.com/python-semantic-release/python-semantic-release/commit/8df5e2bdd33a620e683f3adabe174e94ceaa88d9))

### Fix

* fix: Add credentials check ([`0694604`](https://github.com/python-semantic-release/python-semantic-release/commit/0694604f3b3d2159a4037620605ded09236cdef5))

* fix: Add check of credentials ([`7d945d4`](https://github.com/python-semantic-release/python-semantic-release/commit/7d945d44b36b3e8c0b7771570cb2305e9e09d0b2))

* fix: Add dists to twine call ([`1cec2df`](https://github.com/python-semantic-release/python-semantic-release/commit/1cec2df8bcb7f877c813d6470d454244630b050a))

* fix: Re-add skip-existing ([`366e9c1`](https://github.com/python-semantic-release/python-semantic-release/commit/366e9c1d0b9ffcde755407a1de18e8295f6ad3a1))

* fix: Use twine through cli call ([`ab84beb`](https://github.com/python-semantic-release/python-semantic-release/commit/ab84beb8f809e39ae35cd3ce5c15df698d8712fd))

* fix: Use new interface for twine ([`c04872d`](https://github.com/python-semantic-release/python-semantic-release/commit/c04872d00a26e9bf0f48eeacb360b37ce0fba01e))

* fix: Remove repository argument in twine ([`e24543b`](https://github.com/python-semantic-release/python-semantic-release/commit/e24543b96adb208897f4ce3eaab96b2f4df13106))

* fix: Update twine ([`c4ae7b8`](https://github.com/python-semantic-release/python-semantic-release/commit/c4ae7b8ecc682855a8568b247690eaebe62d2d26))

* fix: Remove universal from setup config ([`18b2402`](https://github.com/python-semantic-release/python-semantic-release/commit/18b24025e397aace03dd5bb9eed46cfdd13491bd))

* fix: Change requests from fixed version to version range (#93)

* Change requests version to be more flexible to aid in using this with dev requirements for a release.

* revert changes to vcs helpers ([`af3ad59`](https://github.com/python-semantic-release/python-semantic-release/commit/af3ad59f018876e11cc3acdda0b149f8dd5606bd))

### Unknown

* Typo, link broken

Change `.. _angular commit guidelins:` to `.. _angular commit guidelines:` ([`721a6dd`](https://github.com/python-semantic-release/python-semantic-release/commit/721a6dd895aa5f0072fc76fe0325f23e565492c4))


## v3.11.2 (2018-06-10)

### Fix

* fix: Upgrade twine ([`9722313`](https://github.com/python-semantic-release/python-semantic-release/commit/9722313eb63c7e2c32c084ad31bed7ee1c48a928))


## v3.11.1 (2018-06-06)

### Documentation

* docs: Add retry option to cli docs ([`021da50`](https://github.com/python-semantic-release/python-semantic-release/commit/021da5001934f3199c98d7cf29f62a3ad8c2e56a))

### Fix

* fix: change Gitpython version number

Change the Gitpython version number to fix a bug described in #80. ([`23c9d4b`](https://github.com/python-semantic-release/python-semantic-release/commit/23c9d4b6a1716e65605ed985881452898d5cf644))


## v3.11.0 (2018-04-12)

### Documentation

* docs: Remove old notes about trello board ([`7f50c52`](https://github.com/python-semantic-release/python-semantic-release/commit/7f50c521a522bb0c4579332766248778350e205b))

* docs: Update status badges ([`cfa13b8`](https://github.com/python-semantic-release/python-semantic-release/commit/cfa13b8260e3f3b0bfcb395f828ad63c9c5e3ca5))

### Feature

* feat: Add support to finding previous version from tags if not using commit messages (#68)

* feat: Be a bit more forgiving to find previous tags

Now grabs the previous version from tag names if it can&#39;t find it in the commit

* quantifiedcode and flake8 fixes

* Update cli.py

* Switch to ImproperConfigurationError ([`6786487`](https://github.com/python-semantic-release/python-semantic-release/commit/6786487ebf4ab481139ef9f43cd74e345debb334))

* feat: Add --retry cli option (#78)

* Add --retry cli option
* Post changelog correctly
* Add comments
* Add --retry to the docs ([`3e312c0`](https://github.com/python-semantic-release/python-semantic-release/commit/3e312c0ce79a78d25016a3b294b772983cfb5e0f))

### Fix

* fix: Make repo non if it is not a git repository

Fixes #74 ([`1dc306b`](https://github.com/python-semantic-release/python-semantic-release/commit/1dc306b9b1db2ac360211bdc61fd815302d0014c))

* fix: Add pytest cache to gitignore ([`b8efd5a`](https://github.com/python-semantic-release/python-semantic-release/commit/b8efd5a6249c79c8378bffea3e245657e7094ec9))


## v3.10.3 (2018-01-29)

### Fix

* fix: error when not in git repository (#75)

Fix an error when the program was run in a non-git repository. It would
not allow the help options to be run.

issue #74 ([`251b190`](https://github.com/python-semantic-release/python-semantic-release/commit/251b190a2fd5df68892346926d447cbc1b32475a))


## v3.10.2 (2017-08-03)

### Fix

* fix: update call to upload to work with twine 1.9.1 (#72) ([`8f47643`](https://github.com/python-semantic-release/python-semantic-release/commit/8f47643c54996e06c358537115e7e17b77cb02ca))


## v3.10.1 (2017-07-22)

### Fix

* fix: Update Twine (#69)

The publishing API is under development and older versions of Twine have problems to deal with newer versions of the API. Namely the logic of register/upload has changed (it was simplified). ([`9f268c3`](https://github.com/python-semantic-release/python-semantic-release/commit/9f268c373a932621771abbe9607b739b1e331409))

### Unknown

* revert: &#34;chore: Remove travis&#34;

This reverts commit 93e5507da6d53ecf63405507390633ef480c52fb. ([`195ed8d`](https://github.com/python-semantic-release/python-semantic-release/commit/195ed8ddc004b736cd4e0301e5d7c7f6394cf4a5))


## v3.10.0 (2017-05-05)

### Documentation

* docs: Fix typo in cli.py docstring (#64) ([`0d13985`](https://github.com/python-semantic-release/python-semantic-release/commit/0d139859cd71f2d483f4360f196d6ef7c8726c18))

### Feature

* feat: Add git hash to the changelog (#65)

* feat(*): add git hash to the changelog

Add git hash to the changelog to ease finding the specific commit. The hash now is also easily viewable in Github&#39;s tag. see #63 for more information.

* chore(test_history): fix test errors

Fix the test errors that would happen after the modification of get_commit_log. ([`628170e`](https://github.com/python-semantic-release/python-semantic-release/commit/628170ebc440fc6abf094dd3e393f40576dedf9b))

### Fix

* fix: Make changelog problems not fail whole publish

Can be fixed with changelog command later. ([`b5a68cf`](https://github.com/python-semantic-release/python-semantic-release/commit/b5a68cf6177dc0ed80eda722605db064f3fe2062))


## v3.9.0 (2016-07-03)

### Feature

* feat: add option for choosing between versioning by commit or tag

default versioning behaviour is commiting ([`c0cd1f5`](https://github.com/python-semantic-release/python-semantic-release/commit/c0cd1f5b2e0776d7b636c3dd9e5ae863125219e6))

* feat: don&#39;t use file to track version, only tag to commit for versioning ([`cd25862`](https://github.com/python-semantic-release/python-semantic-release/commit/cd258623ee518c009ae921cd6bb3119dafae43dc))

* feat: get repo version from historical tags instead of config file

repo version will get from historical tags. init 0.0.0 if fail of find any version tag ([`a45a9bf`](https://github.com/python-semantic-release/python-semantic-release/commit/a45a9bfb64538efeb7f6f42bb6e7ede86a4ddfa8))

### Fix

* fix: can&#39;t get the proper last tag from commit history

repo.tags returns a list sorted by the name rather than date, fix it by sorting them before iteration ([`5a0e681`](https://github.com/python-semantic-release/python-semantic-release/commit/5a0e681e256ec511cd6c6a8edfee9d905891da10))


## v3.8.1 (2016-04-17)

### Fix

* fix: Add search_parent_directories option to gitpython (#62) ([`8bf9ce1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bf9ce11137399906f18bc8b25698b6e03a65034))


## v3.8.0 (2016-03-21)

### Documentation

* docs: Add info about trello board in readme ([`5229557`](https://github.com/python-semantic-release/python-semantic-release/commit/5229557099d76b3404ea3677292332442a57ae2e))

* docs: Update info about releases in contributing.md ([`466f046`](https://github.com/python-semantic-release/python-semantic-release/commit/466f0460774cad86e7e828ffb50c7d1332b64e7b))

* docs: Add info about correct commit guidelines ([`af35413`](https://github.com/python-semantic-release/python-semantic-release/commit/af35413fae80889e2c5fc6b7d28f77f34b3b4c02))

* docs: Fix badges in readme ([`7f4e549`](https://github.com/python-semantic-release/python-semantic-release/commit/7f4e5493edb6b3fb3510d0bb78fcc8d23434837f))

### Feature

* feat: Add ci checks for circle ci ([`151d849`](https://github.com/python-semantic-release/python-semantic-release/commit/151d84964266c8dca206cef8912391cb73c8f206))

### Fix

* fix: Refactoring cli.py to improve --help and error messages ([`c79fc34`](https://github.com/python-semantic-release/python-semantic-release/commit/c79fc3469fb99bf4c7f52434fa9c0891bca757f9))

* fix: Add git fetch to frigg after success ([`74a6cae`](https://github.com/python-semantic-release/python-semantic-release/commit/74a6cae2b46c5150e63136fde0599d98b9486e36))

* fix: Make tag parser work correctly with breaking changes

The tag parser did not work correctly, this went undiscovered for a
while because the tests was not ran by pytest. ([`9496f6a`](https://github.com/python-semantic-release/python-semantic-release/commit/9496f6a502c79ec3acb4e222e190e76264db02cf))


## v3.7.2 (2016-03-19)

### Fix

* fix: move code around a bit to make flake8 happy ([`41463b4`](https://github.com/python-semantic-release/python-semantic-release/commit/41463b49b5d44fd94c11ab6e0a81e199510fabec))


## v3.7.1 (2016-03-15)

### Documentation

* docs(configuration): Fix typo in setup.cfg section ([`725d87d`](https://github.com/python-semantic-release/python-semantic-release/commit/725d87dc45857ef2f9fb331222845ac83a3af135))

### Unknown

* documentation typo ([`b77d484`](https://github.com/python-semantic-release/python-semantic-release/commit/b77d484e119daa0c2fe86bc558eda972d4852a83))


## v3.7.0 (2016-01-10)

### Feature

* feat: Add ci_checks for Frigg CI ([`577c374`](https://github.com/python-semantic-release/python-semantic-release/commit/577c374396fe303b6fe7d64630d2959998d3595c))


## v3.6.1 (2016-01-10)

### Fix

* fix: Add requests as dependency ([`4525a70`](https://github.com/python-semantic-release/python-semantic-release/commit/4525a70d5520b44720d385b0307e46fae77a7463))


## v3.6.0 (2015-12-28)

### Documentation

* docs: Add step by step guide for configuring travis ci ([`6f23414`](https://github.com/python-semantic-release/python-semantic-release/commit/6f2341442f61f0284b1119a2c49e96f0be678929))

* docs: Remove duplicate readme

It was created by pandoc earlier when the original readme was written in
markdown. ([`42a9421`](https://github.com/python-semantic-release/python-semantic-release/commit/42a942131947cd1864c1ba29b184caf072408742))

* docs: Add note about node semantic release ([`0d2866c`](https://github.com/python-semantic-release/python-semantic-release/commit/0d2866c528098ecaf1dd81492f28d3022a2a54e0))

* docs: Move automatic-releases to subfolder ([`ed68e5b`](https://github.com/python-semantic-release/python-semantic-release/commit/ed68e5b8d3489463e244b078ecce8eab2cba2bb1))

* docs: Add documentation for configuring on CI ([`7806940`](https://github.com/python-semantic-release/python-semantic-release/commit/7806940ae36cb0d6ac0f966e5d6d911bd09a7d11))

### Feature

* feat: Add checks for semaphore

Fixes #44 ([`2d7ef15`](https://github.com/python-semantic-release/python-semantic-release/commit/2d7ef157b1250459060e99601ec53a00942b6955))


## v3.5.0 (2015-12-22)

### Documentation

* docs: Convert readme to rst ([`e8a8d26`](https://github.com/python-semantic-release/python-semantic-release/commit/e8a8d265aa2147824f18065b39a8e7821acb90ec))

### Feature

* feat: Checkout master before publishing

Related to #39 ([`dc4077a`](https://github.com/python-semantic-release/python-semantic-release/commit/dc4077a2d07e0522b625336dcf83ee4e0e1640aa))

* feat: Add author in commit

Fixes #40 ([`020efaa`](https://github.com/python-semantic-release/python-semantic-release/commit/020efaaadf588e3fccd9d2f08a273c37e4158421))

### Fix

* fix: Remove &#34; from git push command ([`031318b`](https://github.com/python-semantic-release/python-semantic-release/commit/031318b3268bc37e6847ec049b37425650cebec8))


## v3.4.0 (2015-12-22)

### Feature

* feat: Add travis environment checks

These checks will ensure that semantic release only runs against master
and not in a pull-request. ([`f386db7`](https://github.com/python-semantic-release/python-semantic-release/commit/f386db75b77acd521d2f5bde2e1dde99924dc096))


## v3.3.3 (2015-12-22)

### Fix

* fix: Do git push and git push --tags instead of --follow-tags ([`8bc70a1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bc70a183fd72f595c72702382bc0b7c3abe99c8))


## v3.3.2 (2015-12-21)

### Documentation

* docs: Update docstrings for generate_changelog ([`987c6a9`](https://github.com/python-semantic-release/python-semantic-release/commit/987c6a96d15997e38c93a9d841c618c76a385ce7))

### Fix

* fix: Change build badge ([`0dc068f`](https://github.com/python-semantic-release/python-semantic-release/commit/0dc068fff2f8c6914f4abe6c4e5fb2752669159e))


## v3.3.1 (2015-12-21)

### Fix

* fix: Only list commits from the last version tag

Fixes #28 ([`191369e`](https://github.com/python-semantic-release/python-semantic-release/commit/191369ebd68526e5b1afcf563f7d13e18c8ca8bf))

* fix: Add pandoc to travis settings ([`17d40a7`](https://github.com/python-semantic-release/python-semantic-release/commit/17d40a73062ffa774542d0abc0f59fc16b68be37))


## v3.3.0 (2015-12-20)

### Feature

* feat: Add support for environment variables for pypi credentials ([`3b383b9`](https://github.com/python-semantic-release/python-semantic-release/commit/3b383b92376a7530e89b11de481c4dfdfa273f7b))

### Fix

* fix: Downgrade twine to version 1.5.0 ([`66df378`](https://github.com/python-semantic-release/python-semantic-release/commit/66df378330448a313aff7a7c27067adda018904f))

* fix: Add missing parameters to twine.upload ([`4bae22b`](https://github.com/python-semantic-release/python-semantic-release/commit/4bae22bae9b9d9abf669b028ea3af4b3813a1df0))

* fix: Push to master by default ([`a0bb023`](https://github.com/python-semantic-release/python-semantic-release/commit/a0bb023438a1503f9fdb690d976d71632f19a21f))

* fix: Better filtering of github token in push error ([`9b31da4`](https://github.com/python-semantic-release/python-semantic-release/commit/9b31da4dc27edfb01f685e6036ddbd4c715c9f60))

* fix: Make sure the github token is not in the output ([`55356b7`](https://github.com/python-semantic-release/python-semantic-release/commit/55356b718f74d94dd92e6c2db8a15423a6824eb5))

### Unknown

* Upgrade dependency click to ==6.2 ([`1c5f3cd`](https://github.com/python-semantic-release/python-semantic-release/commit/1c5f3cde6a8a892b1fe48eae39424d3d483b5935))


## v3.2.1 (2015-12-20)

### Fix

* fix: Add requirements to manifest ([`ed25ecb`](https://github.com/python-semantic-release/python-semantic-release/commit/ed25ecbaeec0e20ad3040452a5547bb7d6faf6ad))

* fix(pypi): Add sdist as default in addition to bdist_wheel

There are a lot of outdated pip installations around which leads to
confusions if a package have had an sdist release at some point and
then suddenly is only available as wheel packages, because old pip
clients will then download the latest sdist package available. ([`a1a35f4`](https://github.com/python-semantic-release/python-semantic-release/commit/a1a35f43175187091f028474db2ebef5bfc77bc0))


## v3.2.0 (2015-12-20)

### Feature

* feat(git): Add push to GH_TOKEN@github-url ([`546b5bf`](https://github.com/python-semantic-release/python-semantic-release/commit/546b5bf15466c6f5dfe93c1c03ca34604b0326f2))

* feat(angular-parser): Remove scope requirement ([`90c9d8d`](https://github.com/python-semantic-release/python-semantic-release/commit/90c9d8d4cd6d43be094cda86579e00b507571f98))

### Fix

* fix(deps): Use one file for requirements ([`4868543`](https://github.com/python-semantic-release/python-semantic-release/commit/486854393b24803bb2356324e045ccab17510d46))

### Unknown

* Add links to the node project ([`3567952`](https://github.com/python-semantic-release/python-semantic-release/commit/3567952d8e84235c58aa7e310689de8d4b07f7ad))

* Upgrade dependency twine to ==1.6.3 ([`f96e9b2`](https://github.com/python-semantic-release/python-semantic-release/commit/f96e9b2e066465e657b3d25708713f5d20b6942f))

* Upgrade dependency semver to ==2.2.1 ([`63b4b99`](https://github.com/python-semantic-release/python-semantic-release/commit/63b4b9949816cef110a2ce3c10707525623bd8ef))

* Upgrade dependency invoke to ==0.11.1 ([`b9fe5eb`](https://github.com/python-semantic-release/python-semantic-release/commit/b9fe5eb8bf1f44df53ffe7924c999142d65b5520))

* Upgrade dependency click to ==5.1 ([`662bc2d`](https://github.com/python-semantic-release/python-semantic-release/commit/662bc2dea8f4f9792bd63d8a6490181547aa1499))

* Upgrade dependency twine to ==1.6.3 ([`571dd43`](https://github.com/python-semantic-release/python-semantic-release/commit/571dd43f10498882b2828afb334c9e82f839e040))

* Upgrade dependency semver to ==2.2.1 ([`e656bea`](https://github.com/python-semantic-release/python-semantic-release/commit/e656bea8c0004e6952f8868569a7460a13ae3e40))

* Upgrade dependency invoke to ==0.11.1 ([`31a2051`](https://github.com/python-semantic-release/python-semantic-release/commit/31a205143492a13bc796cf9755ae78231ae35c00))

* Upgrade dependency click to ==5.1 ([`d0b6c7d`](https://github.com/python-semantic-release/python-semantic-release/commit/d0b6c7d968961d7bc84560ca22f3b9a8634e08a9))

* Upgrade dependency responses to ==0.5.0 ([`fcf9e1a`](https://github.com/python-semantic-release/python-semantic-release/commit/fcf9e1a806236fc09a472ba6e58cf44f57b2147f))


## v3.1.0 (2015-08-31)

### Feature

* feat(pypi): Add option to disable pypi upload ([`f5cd079`](https://github.com/python-semantic-release/python-semantic-release/commit/f5cd079edb219de5ad03a71448d578f5f477da9c))


## v3.0.0 (2015-08-25)

### Feature

* feat(parser): Add tag parser

This parser is based on the same commit style as 1.x.x of
python-semantic-release. However, it requires &#34;BREAKING CHANGE:
&lt;explanation&gt; for a breaking change ([`a7f392f`](https://github.com/python-semantic-release/python-semantic-release/commit/a7f392fd4524cc9207899075631032e438e2593c))

### Fix

* fix(errors): Add exposing of errors in package ([`3662d76`](https://github.com/python-semantic-release/python-semantic-release/commit/3662d7663291859dd58a91b4b4ccde4f0edc99b2))

* fix(version): Parse file instead for version

This makes it possible to use the version command without a setup.py
file. ([`005dba0`](https://github.com/python-semantic-release/python-semantic-release/commit/005dba0094eeb4098315ef383a746e139ffb504d))


## v2.1.4 (2015-08-24)

### Fix

* fix(github): Fix property calls

Properties can only be used from instances. ([`7ecdeb2`](https://github.com/python-semantic-release/python-semantic-release/commit/7ecdeb22de96b6b55c5404ebf54a751911c4d8cd))


## v2.1.3 (2015-08-22)

### Documentation

* docs(readme): Update readme with information about the changelog command ([`56a745e`](https://github.com/python-semantic-release/python-semantic-release/commit/56a745ef6fa4edf6f6ba09c78fcc141102cf2871))

* docs(parsers): Add documentation about commit parsers ([`9b55422`](https://github.com/python-semantic-release/python-semantic-release/commit/9b554222768036024a133153a559cdfc017c1d91))

* docs(api): Update apidocs ([`6185380`](https://github.com/python-semantic-release/python-semantic-release/commit/6185380babedbbeab2a2a342f17b4ff3d4df6768))

### Fix

* fix(hvcs): Make Github.token an property ([`37d5e31`](https://github.com/python-semantic-release/python-semantic-release/commit/37d5e3110397596a036def5f1dccf0860964332c))


## v2.1.2 (2015-08-20)

### Fix

* fix(cli): Fix call to generate_changelog in publish ([`5f8bce4`](https://github.com/python-semantic-release/python-semantic-release/commit/5f8bce4cbb5e1729e674efd6c651e2531aea2a16))


## v2.1.1 (2015-08-20)

### Fix

* fix(history): Fix issue in get_previous_version ([`f961786`](https://github.com/python-semantic-release/python-semantic-release/commit/f961786aa3eaa3a620f47cc09243340fd329b9c2))


## v2.1.0 (2015-08-20)

### Feature

* feat(cli): Add the possibility to repost the changelog ([`4d028e2`](https://github.com/python-semantic-release/python-semantic-release/commit/4d028e21b9da01be8caac8f23f2c11e0c087e485))

### Fix

* fix(cli): Fix check of token in changelog command ([`cc6e6ab`](https://github.com/python-semantic-release/python-semantic-release/commit/cc6e6abe1e91d3aa24e8d73e704829669bea5fd7))

* fix(github): Fix the github releases integration ([`f0c3c1d`](https://github.com/python-semantic-release/python-semantic-release/commit/f0c3c1db97752b71f2153ae9f623501b0b8e2c98))

* fix(history): Fix changelog generation

This enables regeneration of a given versions changelog. ([`f010272`](https://github.com/python-semantic-release/python-semantic-release/commit/f01027203a8ca69d21b4aff689e60e8c8d6f9af5))


## v2.0.0 (2015-08-19)

### Breaking

* feat(history): Set angular parser as the default

BREAKING CHANGE: This changes the default parser. Thus, the default
behaviour of the commit log evaluator will change. From now on it will
use the angular commit message spec to determine the new version. ([`c2cf537`](https://github.com/python-semantic-release/python-semantic-release/commit/c2cf537a42beaa60cd372c7c9f8fb45db8085917))

### Feature

* feat(publish): Add publishing of changelog to github ([`74324ba`](https://github.com/python-semantic-release/python-semantic-release/commit/74324ba2749cdbbe80a92b5abbecfeab04617699))

* feat(github): Add github release changelog helper ([`da18795`](https://github.com/python-semantic-release/python-semantic-release/commit/da187951af31f377ac57fe17462551cfd776dc6e))

* feat(history): Add markdown changelog formatter ([`d77b58d`](https://github.com/python-semantic-release/python-semantic-release/commit/d77b58db4b66aec94200dccab94f483def4dacc9))

* feat(cli): Add command for printing the changelog

Usage: `semantic_release changelog` ([`336b8bc`](https://github.com/python-semantic-release/python-semantic-release/commit/336b8bcc01fc1029ff37a79c92935d4b8ea69203))

* feat(history): Add generate_changelog function

It generates a dict with changelog information to each of the given
section types. ([`347f21a`](https://github.com/python-semantic-release/python-semantic-release/commit/347f21a1f8d655a71a0e7d58b64d4c6bc6d0bf31))

* feat(settings): Add loading of current parser ([`7bd0916`](https://github.com/python-semantic-release/python-semantic-release/commit/7bd0916f87a1f9fe839c853eab05cae1af420cd2))

* feat(history): Add angular parser

This adds a parser that follows the angular specification. The parser is
not hooked into the history evaluation yet. However, it will become the
default parser of commit messages when the evaluator starts using
exchangeable parsers.

Related to #17 ([`91e4f0f`](https://github.com/python-semantic-release/python-semantic-release/commit/91e4f0f4269d01b255efcd6d7121bbfd5a682e12))

### Fix

* fix(cli): Change output indentation on changelog ([`2ca41d3`](https://github.com/python-semantic-release/python-semantic-release/commit/2ca41d3bd1b8b9d9fe7e162772560e3defe2a41e))

* fix(history): Support unexpected types in changelog generator ([`13deacf`](https://github.com/python-semantic-release/python-semantic-release/commit/13deacf5d33ed500e4e94ea702a2a16be2aa7c48))

* fix(history): Fix regex in angular parser

This fixes a problem where multiline commit messages where not correctly
parsed. ([`974ccda`](https://github.com/python-semantic-release/python-semantic-release/commit/974ccdad392d768af5e187dabc184be9ac3e133d))

* fix(history): Fix level id&#39;s in angular parser ([`2918d75`](https://github.com/python-semantic-release/python-semantic-release/commit/2918d759bf462082280ede971a5222fe01634ed8))

### Unknown

* Add badges in readme ([`ad7c9c6`](https://github.com/python-semantic-release/python-semantic-release/commit/ad7c9c69329efe8af42112f716c39e810ed22718))

* Add cumulative coverage ([`15c5ea0`](https://github.com/python-semantic-release/python-semantic-release/commit/15c5ea0106ed08ef8d896d100cf1987c0b5fc17a))

* Update api-docs ([`4654655`](https://github.com/python-semantic-release/python-semantic-release/commit/4654655c33afc7cead9c238a14e4b71cc7121aa5))

* Fix #19, add config documentation ([`354b2ca`](https://github.com/python-semantic-release/python-semantic-release/commit/354b2cabfc7e4a8d2c95ebd2801cc4dbca67fa5a))


## v1.0.0 (2015-08-04)

### Unknown

* :boom: Restructure helpers into history and pypi ([`00f64e6`](https://github.com/python-semantic-release/python-semantic-release/commit/00f64e623db0e21470d55488c5081e12d6c11fd3))

* Rename git_helpers to vcs_helpers ([`77d701b`](https://github.com/python-semantic-release/python-semantic-release/commit/77d701b89c93a761c83965f7c267c7ec35989ec2))

* Make authors file a list ([`31b0f3a`](https://github.com/python-semantic-release/python-semantic-release/commit/31b0f3a3c6a0c5e9d4d9521aba0a303adefdeeec))

* Fix #18, add docs for automatic publishing ([`58076e6`](https://github.com/python-semantic-release/python-semantic-release/commit/58076e60bf20a5835b112b5e99a86c7425ffe7d9))

* Set alabaster as sphinx theme ([`1f698fe`](https://github.com/python-semantic-release/python-semantic-release/commit/1f698fe249a3cc646006b6f922e6b7ec8e12563f))

* Add @jezdez to AUTHORS.rst ([`985df2d`](https://github.com/python-semantic-release/python-semantic-release/commit/985df2dd052668f72e99274370e335e47d5c5d39))

* Add pytest-xdist as requirements ([`35961d7`](https://github.com/python-semantic-release/python-semantic-release/commit/35961d7cc17a862710661b9f9e25aa276d2f505b))

* Fix current head hash test ([`ed9a879`](https://github.com/python-semantic-release/python-semantic-release/commit/ed9a8795d2e72cbdd6689eec4fea2622a5654bc6))


## v0.9.1 (2015-08-04)

### Unknown

* :bug: Fix get_current_head_hash, ensure it only returns the hash ([`7c28832`](https://github.com/python-semantic-release/python-semantic-release/commit/7c2883209e5bf4a568de60dbdbfc3741d34f38b4))


## v0.9.0 (2015-08-03)

### Unknown

* Add Python 2.7 support. Fix #10. ([`c05e13f`](https://github.com/python-semantic-release/python-semantic-release/commit/c05e13f22163237e963c493ffeda7e140f0202c6))

* Fixed cli tests to use correct params for call assertion. ([`456b26b`](https://github.com/python-semantic-release/python-semantic-release/commit/456b26be7130e51a7a46310f65dffb615b30a097))

* Fixed name of assertion function. ([`9b16098`](https://github.com/python-semantic-release/python-semantic-release/commit/9b1609813ae71d5605b8ec9754d737ba38465537))


## v0.8.0 (2015-08-03)

### Unknown

* Fix version test, add missing mock ([`71842d4`](https://github.com/python-semantic-release/python-semantic-release/commit/71842d4d50fa16fbdba0487d1c8f6d0eb6b7d407))

* Set check_build_status in semantic-release config ([`00f1a4e`](https://github.com/python-semantic-release/python-semantic-release/commit/00f1a4ef5283733d580c6bb02ed25d511a8b0c0b))

* :bug: Fix test_defaults in settings test ([`b269d27`](https://github.com/python-semantic-release/python-semantic-release/commit/b269d27ca1c1cfc9efd25abab2de619b6f3ef9d6))

* Add release schedule note ([`8bc8fba`](https://github.com/python-semantic-release/python-semantic-release/commit/8bc8fba7dc3bd6bcea0cc5e5946e85f6f8e1c6d7))

* Add output when running check_build_status ([`8bdda5a`](https://github.com/python-semantic-release/python-semantic-release/commit/8bdda5aba626fcbed8d357551f6d77fca5d1839d))

* Add default value in check_build_status docs ([`eb0c46d`](https://github.com/python-semantic-release/python-semantic-release/commit/eb0c46d00e0f07e1e902b33470dbf7309146964f))

* :sparkles: Fix #5, Add check_build_status option ([`310bb93`](https://github.com/python-semantic-release/python-semantic-release/commit/310bb9371673fcf9b7b7be48422b89ab99753f04))

* :sparkles: Add get_current_head_hash in git helpers ([`d864282`](https://github.com/python-semantic-release/python-semantic-release/commit/d864282c498f0025224407b3eeac69522c2a7ca0))

* :sparkles: Add git helper to get owner and name of repo ([`f940b43`](https://github.com/python-semantic-release/python-semantic-release/commit/f940b435537a3c93ab06170d4a57287546bd8d3b))


## v0.7.0 (2015-08-02)

### Unknown

* :sparkles: Add patch_without_tag option, fixes #6 ([`3734a88`](https://github.com/python-semantic-release/python-semantic-release/commit/3734a889f753f1b9023876e100031be6475a90d1))

* Move defaults to cfg file ([`cb1257a`](https://github.com/python-semantic-release/python-semantic-release/commit/cb1257a60a81cb5aadbc8f6470ec2ec2c904506c))

* Add contributing.rst ([`a27e282`](https://github.com/python-semantic-release/python-semantic-release/commit/a27e28223b8186bda66cc882454746a5595d8643))

* Fix docstring in setup_hook() ([`1e47f1c`](https://github.com/python-semantic-release/python-semantic-release/commit/1e47f1c6c68b5a74515f2f86275e3c749c999e1c))

* Fix #1, Add basic setup of sphinx based docs ([`41fba78`](https://github.com/python-semantic-release/python-semantic-release/commit/41fba78a389a8d841316946757a23a7570763c39))

* Add docstrings to all functions ([`6555d5a`](https://github.com/python-semantic-release/python-semantic-release/commit/6555d5a5944fa4b7823f70fd720e193915186307))


## v0.6.0 (2015-08-02)

### Unknown

* :sparkles: Fix #13, Add twine for uploads to pypi ([`eec2561`](https://github.com/python-semantic-release/python-semantic-release/commit/eec256115b28b0a18136a26d74cfc3232502f1a6))

* Add tests for the setup.py hook ([`ecd9e9a`](https://github.com/python-semantic-release/python-semantic-release/commit/ecd9e9a3f97bdf9489b6dc750d736855a2c109c2))

* Add test for git helpers ([`8354cfd`](https://github.com/python-semantic-release/python-semantic-release/commit/8354cfd953bb09723abcff7fefe620fc4aa6b855))

* Fix typo ([`9585217`](https://github.com/python-semantic-release/python-semantic-release/commit/9585217d95a4bb2447ae8860971575bd4c847070))

* Add link to blogpost in readme ([`1966e52`](https://github.com/python-semantic-release/python-semantic-release/commit/1966e52ab4f08d3cbabe88881c0e51e600e44567))


## v0.5.4 (2015-07-29)

### Unknown

* Add tests for upload_to_pypi ([`778923f`](https://github.com/python-semantic-release/python-semantic-release/commit/778923fab86d423b6ed254c569fddee1b9650f56))

* :bug: Add python2 not supported warning

Related: #9, #10 ([`e84c4d8`](https://github.com/python-semantic-release/python-semantic-release/commit/e84c4d8b6f212aec174baccd188185627b5039b6))

* Add note about python 3 only

related to #9 ([`a71b536`](https://github.com/python-semantic-release/python-semantic-release/commit/a71b53609db75316e3c14df0ece7f474393641bc))


## v0.5.3 (2015-07-28)

### Unknown

* Add wheel as a dependency ([`971e479`](https://github.com/python-semantic-release/python-semantic-release/commit/971e4795a8b8fea371fcc02dc9221f58a0559f32))


## v0.5.2 (2015-07-28)

### Unknown

* :bug: Fix python wheel tag ([`f9ac163`](https://github.com/python-semantic-release/python-semantic-release/commit/f9ac163491666022c809ad49846f3c61966e10c1))


## v0.5.1 (2015-07-28)

### Unknown

* :bug: Fix push commands ([`8374ef6`](https://github.com/python-semantic-release/python-semantic-release/commit/8374ef6bd78eb564a6d846b882c99a67e116394e))


## v0.5.0 (2015-07-28)

### Unknown

* :sparkles: Add setup.py hook for the cli interface ([`c363bc5`](https://github.com/python-semantic-release/python-semantic-release/commit/c363bc5d3cb9e9a113de3cd0c49dd54a5ea9cf35))


## v0.4.0 (2015-07-28)

### Unknown

* :sparkles: Add publish command ([`d8116c9`](https://github.com/python-semantic-release/python-semantic-release/commit/d8116c9dec472d0007973939363388d598697784))


## v0.3.2 (2015-07-28)


## v0.3.1 (2015-07-28)

### Unknown

* :bug: Fix wheel settings ([`1e860e8`](https://github.com/python-semantic-release/python-semantic-release/commit/1e860e8a4d9ec580449a0b87be9660a9482fa2a4))


## v0.3.0 (2015-07-27)

### Unknown

* Add info about tagging in readme ([`914c78f`](https://github.com/python-semantic-release/python-semantic-release/commit/914c78f0e1e15043c080e6d1ee56eccb5a70dd7d))

* :sparkles: Add support for tagging releases ([`5f4736f`](https://github.com/python-semantic-release/python-semantic-release/commit/5f4736f4e41bc96d36caa76ca58be0e1e7931069))

* :bug: Fix issue with committing the same version # ([`441798a`](https://github.com/python-semantic-release/python-semantic-release/commit/441798a223195138c0d3d2c51fc916137fef9a6c))

* Remove patch as default for untagged history ([`e44e2a1`](https://github.com/python-semantic-release/python-semantic-release/commit/e44e2a166033b75f75351825f7e4e0866bb7c45b))

* Restructure and add tests ([`4546e1e`](https://github.com/python-semantic-release/python-semantic-release/commit/4546e1e11429026c1a5410e17f8c5f866cfe5833))


## v0.2.0 (2015-07-27)

### Unknown

* Remove apt dependencies from frigg settings ([`d942a32`](https://github.com/python-semantic-release/python-semantic-release/commit/d942a32bd475b3541c207069bd43d88f60a310a0))

* Fix get_commit_log ([`9af798a`](https://github.com/python-semantic-release/python-semantic-release/commit/9af798abab0d0b69c36134f0189745e9703dbfba))

* Remove pygit2 and add gitpython ([`8165a2e`](https://github.com/python-semantic-release/python-semantic-release/commit/8165a2eef2c6eea88bfa52e6db37abc7374cccba))

* Add test to check which parts of the git log is considered ([`bb384b1`](https://github.com/python-semantic-release/python-semantic-release/commit/bb384b16d649ed2bb0f30cd3356c0e78f6e06e11))

* :sparkles: Add noop mode

Fixes #4 ([`44c2039`](https://github.com/python-semantic-release/python-semantic-release/commit/44c203989aabc9366ba42ed2bc40eaccd7ac891c))

* Add docstrings in cli ([`315f6d2`](https://github.com/python-semantic-release/python-semantic-release/commit/315f6d2e3c80c309e80733234ab123d07c10779d))

* Add installation of python3-cffi to frigg settings ([`aa38ca8`](https://github.com/python-semantic-release/python-semantic-release/commit/aa38ca8c5c64a583ecc4fb78c4789a18a031ceae))

* Add installation of libgit2-dev in frigg settings ([`ff1d72b`](https://github.com/python-semantic-release/python-semantic-release/commit/ff1d72b8f4a8e55317d3f3b0efebaeaf67fb8f63))

* Remove the this is not usable yet warning from readme ([`b14b468`](https://github.com/python-semantic-release/python-semantic-release/commit/b14b468f96211fd754f7441b8c8ca371e9cd5ce1))

* Update usage docs in readme ([`1f753e6`](https://github.com/python-semantic-release/python-semantic-release/commit/1f753e631b9b7e9d4234779ddaac31532ed77b88))

* Remove note about :arrow_up: in readme ([`1554051`](https://github.com/python-semantic-release/python-semantic-release/commit/1554051d9e061094bc191812348c32c22d3d5f40))

* Update config docs in readme ([`06a261f`](https://github.com/python-semantic-release/python-semantic-release/commit/06a261f14426c43713bb9ec32a87066ce2adb010))


## v0.1.1 (2015-07-27)

### Unknown

* Fix libgit install in frigg settings ([`bd991c3`](https://github.com/python-semantic-release/python-semantic-release/commit/bd991c3b3e1f69f86b1f6ca538e57b3ba365e376))

* :bug: Fix entry point ([`bd7ce7f`](https://github.com/python-semantic-release/python-semantic-release/commit/bd7ce7f47c49e2027767fb770024a0d4033299fa))

* Fix badges ([`1e5df79`](https://github.com/python-semantic-release/python-semantic-release/commit/1e5df79aa104768078e6e66d559ab88b751cc0a3))

* Add libgit2 to frigg settings ([`d55f25c`](https://github.com/python-semantic-release/python-semantic-release/commit/d55f25cac13625037c5154e3cdd7dbb9bb88e350))

* Update readme ([`e8a6dd9`](https://github.com/python-semantic-release/python-semantic-release/commit/e8a6dd9e264a3e2d4186c323f7b544d4e42754b1))


## v0.1.0 (2015-07-27)

### Unknown

* Add commiting of new version ([`6865d4b`](https://github.com/python-semantic-release/python-semantic-release/commit/6865d4b9d39027effe1902b9c50479c832650f68))

* Add detection of change level ([`06c5ac4`](https://github.com/python-semantic-release/python-semantic-release/commit/06c5ac4ce945223452c1331371c74130a2fc4b49))

* Fix coverage settings ([`4b80fab`](https://github.com/python-semantic-release/python-semantic-release/commit/4b80fab7433a215c09a68b041fef9db2286f8428))

* :sparkles: Implement setting of new version ([`a2ad75b`](https://github.com/python-semantic-release/python-semantic-release/commit/a2ad75b8dac515d1bbc49c32257c62a7da59e2e1))

* :sparkles: Add loading of config ([`51c5e93`](https://github.com/python-semantic-release/python-semantic-release/commit/51c5e93adf2c4d4193d94cce2b661da7fb75138e))

* Fix readme badges ([`a3cc59b`](https://github.com/python-semantic-release/python-semantic-release/commit/a3cc59b3471294ed0875624889dfde8cf8c6402f))

* Update readme ([`2b64782`](https://github.com/python-semantic-release/python-semantic-release/commit/2b64782e3fd78aec1e9f8d8cd391efc8eb3a4416))

* Fix isort ([`11feb93`](https://github.com/python-semantic-release/python-semantic-release/commit/11feb93c23c2bb51480191c5035fa92a7316e546))

* :sparkles: Add better force options ([`c6b4fe9`](https://github.com/python-semantic-release/python-semantic-release/commit/c6b4fe999531516ff5657541e894c3156deffbcb))

* Remove print usage ([`5ca8957`](https://github.com/python-semantic-release/python-semantic-release/commit/5ca8957b3974fdfa46fb66199f5848aa2711a49e))

* :sparkles: Implement get_new_version with semver ([`4bb1f10`](https://github.com/python-semantic-release/python-semantic-release/commit/4bb1f10fba27256a4982ad2ff4e2478ace7893a7))

* :sparkles: Implement get_current_version ([`49de531`](https://github.com/python-semantic-release/python-semantic-release/commit/49de531900b8d3cde4ae36d1f58f26da196e8177))

* :sparkles: Add basic cli interface ([`ff03d6e`](https://github.com/python-semantic-release/python-semantic-release/commit/ff03d6e796ffee498e21c1457fd1c356418cc5e6))

* :sparkles: Add project structure ([`57f4c2b`](https://github.com/python-semantic-release/python-semantic-release/commit/57f4c2bdbfe88f6318c87bf6b2fbf851bc9f5a90))

* Add a plan to the readme ([`6f87d66`](https://github.com/python-semantic-release/python-semantic-release/commit/6f87d6691f95c6dd652ba5fdadf155e9a194bfb6))

* Initial commit ([`94abb4e`](https://github.com/python-semantic-release/python-semantic-release/commit/94abb4e631d363f1f7ffcf85f026fc57845d4c1c))
