# CHANGELOG



## v8.0.0-alpha.3 (2023-02-04)

### Fix

* fix: resolve bug in changelog logic, enable upload to pypi ([`f9e4bb2`](https://github.com/python-semantic-release/python-semantic-release/commit/f9e4bb20d576ecaaa75910e73ff2b2d132b445f0))

### Unknown

* Merge branch &#39;master&#39; into 8.0.x ([`33e778a`](https://github.com/python-semantic-release/python-semantic-release/commit/33e778a61d613f86aec5976808b2f2df4c9e0b5f))


## v7.33.1 (2023-02-01)

### Fix

* fix(action): mark container fs as safe for git (#552)

See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124 and https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956 ([`2a55f68`](https://github.com/python-semantic-release/python-semantic-release/commit/2a55f68e2b3cb9ffa9204c00ddbf12706af5c070))

### Style

* style: beautify 2a55f68e2b3cb9ffa9204c00ddbf12706af5c070 ([`30ad440`](https://github.com/python-semantic-release/python-semantic-release/commit/30ad44019904c30aba86fb0d48dc88ce5e9eba39))


## v8.0.0-alpha.2 (2023-02-01)

### Fix

* fix(action): quotation for git config command ([`6e35625`](https://github.com/python-semantic-release/python-semantic-release/commit/6e35625c59bea3d14d618a27e9cd390f553d7477))

* fix(action): mark container fs as safe for git to operate on ([`49080c5`](https://github.com/python-semantic-release/python-semantic-release/commit/49080c510a68cccd2f6c7a8d540b483751901207))

* fix: cleanup comments and unused logic ([`63e613e`](https://github.com/python-semantic-release/python-semantic-release/commit/63e613e8298f87e3fd54613c8a3de2f3ba519fc8))

* fix: correct logic for generating release notes (#550) ([`74deffa`](https://github.com/python-semantic-release/python-semantic-release/commit/74deffab3ed1540a83c6038a4d3e0ce5c80dd60f))

### Style

* style: beautify 49080c510a68cccd2f6c7a8d540b483751901207 ([`8b99cf0`](https://github.com/python-semantic-release/python-semantic-release/commit/8b99cf0416b0ac4fe4e436f8355ad126eab07e1b))

### Unknown

* Merge branch &#39;master&#39; into 8.0.x ([`96cd31c`](https://github.com/python-semantic-release/python-semantic-release/commit/96cd31cce6f8c52d49b9d887ddb084478f7fdca4))


## v7.33.0 (2023-01-15)

### Ci

* ci: fix GHA conditional ([`8edfbc9`](https://github.com/python-semantic-release/python-semantic-release/commit/8edfbc9eec8804fe14ed9f9f281a89376a03ef9d))

* ci: remove python3.6 from GHA, add python3.10 and python3.11 (#541)

* ci: remove python3.6 from GHA, add python3.10 and python3.11

GHA workflows are failing without this, due to
https://github.com/actions/setup-python/issues/544\#issuecomment-1332535877

* fix: upgrade pytest ([`8e4aa0e`](https://github.com/python-semantic-release/python-semantic-release/commit/8e4aa0e30438291ade98604a18aeb372f0d0b52f))

### Fix

* fix: changelog release commit search logic (#530)

* Fixes changelog release commit search logic

Running `semantic-release changelog` currently fails to identify &#34;the last commit in [a] release&#34; because the compared commit messages have superfluous whitespace.
Likely related to the issue causing: https://github.com/relekang/python-semantic-release/issues/490

* Removes a couple of extra `strip()`s. ([`efb3410`](https://github.com/python-semantic-release/python-semantic-release/commit/efb341036196c39b4694ca4bfa56c6b3e0827c6c))

### Style

* style: beautify 8e4aa0e30438291ade98604a18aeb372f0d0b52f ([`729c2a7`](https://github.com/python-semantic-release/python-semantic-release/commit/729c2a741705523ee16c0be790f54f013c07adcf))


## v8.0.0-alpha.1 (2022-12-19)

### Breaking

* feat!: 8.0.x (#538)

Co-authored-by: Johan &lt;johanhmr@gmail.com&gt;
Co-authored-by: U-NEO\johan &lt;johan.hammar@ombea.com&gt; ([`24f1b45`](https://github.com/python-semantic-release/python-semantic-release/commit/24f1b45491782caec4ef18ed14e23b3d42993742))

### Chore

* chore: remove stale.yml

It is spamming to much. We can bring it back if we get the time to fix the spamming. ([`08c535e`](https://github.com/python-semantic-release/python-semantic-release/commit/08c535e3280733e9e76af1783ce03bb5554c4136))

### Feature

* feat: add signing options to action ([`31ad5eb`](https://github.com/python-semantic-release/python-semantic-release/commit/31ad5eb5a25f0ea703afc295351104aefd66cac1))

* feat(repository): add support for TWINE_CERT (#522)

Fixes #521 ([`d56e85d`](https://github.com/python-semantic-release/python-semantic-release/commit/d56e85d1f2ac66fb0b59af2178164ca915dbe163))

* feat: Update action with configuration options (#518)

Co-authored-by: Kevin Watson &lt;Kevmo92@users.noreply.github.com&gt; ([`4664afe`](https://github.com/python-semantic-release/python-semantic-release/commit/4664afe5f80a04834e398fefb841b166a51d95b7))

### Fix

* fix: remove commit amending behaviour

this was not working when there were no source code changes to be made, as it lead
to attempting to amend a HEAD commit that wasn&#39;t produced by PSR ([`d868d9f`](https://github.com/python-semantic-release/python-semantic-release/commit/d868d9fcf2c48398ebbdd30350e27269593928fc))

* fix: resolve branch checkout logic in GHA ([`b1a07ac`](https://github.com/python-semantic-release/python-semantic-release/commit/b1a07ac049c66f2cdd18077090147ac54674dfca))

* fix: correct Dockerfile CLI command and GHA fetch ([`67c6946`](https://github.com/python-semantic-release/python-semantic-release/commit/67c6946900cd7074366a3663a397fe806ef68dff))

* fix: bump Dockerfile to use Python 3.10 image (#536)

Fixes #533

Co-authored-by: Bernard Cooke &lt;bernard.cooke@iotics.com&gt; ([`8f2185d`](https://github.com/python-semantic-release/python-semantic-release/commit/8f2185d570b3966b667ac591ae523812e9d2e00f))

* fix: fix mypy errors for publish ([`b40dd48`](https://github.com/python-semantic-release/python-semantic-release/commit/b40dd484387c1b3f78df53ee2d35e281e8e799c8))

* fix: formatting in docs ([`2e8227a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8227a8a933683250f8dace019df15fdb35a857))

* fix: update documentaton ([`5cbdad2`](https://github.com/python-semantic-release/python-semantic-release/commit/5cbdad296034a792c9bf05e3700eac4f847eb469))

* fix(action): fix environment variable names ([`3c66218`](https://github.com/python-semantic-release/python-semantic-release/commit/3c66218640044adf263fcf9b2714cfc4b99c2e90))

### Style

* style: beautify b40dd484387c1b3f78df53ee2d35e281e8e799c8 ([`2aab9bd`](https://github.com/python-semantic-release/python-semantic-release/commit/2aab9bd4fba532dfa632d2008bd10b2fe1e3eb05))


## v7.32.2 (2022-10-22)

### Ci

* ci: Update stale github action config ([`69ddb4e`](https://github.com/python-semantic-release/python-semantic-release/commit/69ddb4e31646f7d355a55f2d60e42c55d25eb679))

* ci: Update deprecated actions (#511)

* ci: update depreated actions

* ci: replace deprecated set-output in workflow

According to https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/ ([`bb09233`](https://github.com/python-semantic-release/python-semantic-release/commit/bb09233b84d153a15784fdf68d7274c9d682c336))

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

### Chore

* chore(dependencies): pin tomlkit major version only (#492)

Resolve #491 ([`bd2201f`](https://github.com/python-semantic-release/python-semantic-release/commit/bd2201f099bc38ce233fce08648bd5da44bcb194))

### Fix

* fix: account for trailing newlines in commit messages (#495)

Fixes #490 ([`111b151`](https://github.com/python-semantic-release/python-semantic-release/commit/111b1518e8c8e2bd7535bd4c4b126548da384605))


## v7.31.3 (2022-08-22)

### Fix

* fix: use `commit_subject` when searching for release commits (#488)

Co-authored-by: Dzmitry Ryzhykau &lt;d.ryzhykau@onesoil.ai&gt; ([`3849ed9`](https://github.com/python-semantic-release/python-semantic-release/commit/3849ed992c3cff9054b8690bcf59e49768f84f47))

### Style

* style: beautify 3849ed992c3cff9054b8690bcf59e49768f84f47 ([`c84b1b7`](https://github.com/python-semantic-release/python-semantic-release/commit/c84b1b749fb5e6262652210f4275fe4fbbd2b3c3))


## v7.31.2 (2022-07-29)

### Chore

* chore: Fix deprecation warnings in tests ([`47130a4`](https://github.com/python-semantic-release/python-semantic-release/commit/47130a40a1f24214caa71041bb5a645814538076))

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

### Refactor

* refactor: Fix type errors related to loading of repo ([`e09cc3c`](https://github.com/python-semantic-release/python-semantic-release/commit/e09cc3c5fbb38caceb68b20198a98fea97599826))


## v7.31.1 (2022-07-29)

### Fix

* fix: Update git email in action

Fixes #473 ([`0ece6f2`](https://github.com/python-semantic-release/python-semantic-release/commit/0ece6f263ff02a17bb1e00e7ed21c490f72e3d00))


## v7.31.0 (2022-07-29)

### Chore

* chore: gitignore vim swp files ([`d6fcb5f`](https://github.com/python-semantic-release/python-semantic-release/commit/d6fcb5fb524a5750eb8f504afb4a8ce07d9a4123))

### Feature

* feat: override repository_url w REPOSITORY_URL env var (#439) ([`cb7578c`](https://github.com/python-semantic-release/python-semantic-release/commit/cb7578cf005b8bd65d9b988f6f773e4c060982e3))

* feat: add prerelease-patch and no-prerelease-patch flags for whether to auto-bump prereleases ([`b4e5b62`](https://github.com/python-semantic-release/python-semantic-release/commit/b4e5b626074f969e4140c75fdac837a0625cfbf6))

### Fix

* fix: :bug: fix get_current_release_version for tag_only version_source ([`cad09be`](https://github.com/python-semantic-release/python-semantic-release/commit/cad09be9ba067f1c882379c0f4b28115a287fc2b))

### Style

* style: beautify cad09be9ba067f1c882379c0f4b28115a287fc2b ([`76eb536`](https://github.com/python-semantic-release/python-semantic-release/commit/76eb536299195b2ce0d0411e9bc5c662526abd33))


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

### Style

* style: beautify 51bcb780a9f55fadfaf01612ff65c1f92642c2c1 ([`b47a323`](https://github.com/python-semantic-release/python-semantic-release/commit/b47a3230c0778a67096dd9ba2ded5729247733d0))


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

### Style

* style: beautify dd26888a923b2f480303c19f1916647de48b02bf ([`9cb0b45`](https://github.com/python-semantic-release/python-semantic-release/commit/9cb0b459702a98ee5d42aa66a141a965413ef7a1))


## v7.29.4 (2022-06-29)

### Fix

* fix: add text for empty ValueError (#461) ([`733254a`](https://github.com/python-semantic-release/python-semantic-release/commit/733254a99320d8c2f964d799ac4ec29737867faa))

### Style

* style: beautify 733254a99320d8c2f964d799ac4ec29737867faa ([`55c9f4d`](https://github.com/python-semantic-release/python-semantic-release/commit/55c9f4d44853b003d0822cc80cdf7f352d80f869))


## v7.29.3 (2022-06-26)

### Fix

* fix: Ensure that assets can be uploaded successfully on custom GitHub servers (#458)

Signed-off-by: Chris Butler &lt;cbutler@australiacloud.com.au&gt; ([`32b516d`](https://github.com/python-semantic-release/python-semantic-release/commit/32b516d7aded4afcafe4aa56d6a5a329b3fc371d))

### Style

* style: beautify 32b516d7aded4afcafe4aa56d6a5a329b3fc371d ([`fc5a703`](https://github.com/python-semantic-release/python-semantic-release/commit/fc5a703ede88539ebc0624b59f9490976f5f96cf))

* style: beautify c8087fea6ce9f638e3fc7ea21e8cae62e43016f8 ([`772573f`](https://github.com/python-semantic-release/python-semantic-release/commit/772573f6636f0a93c617cff29297e98edcb240df))

### Test

* test: refactor to pytest (#459) ([`c8087fe`](https://github.com/python-semantic-release/python-semantic-release/commit/c8087fea6ce9f638e3fc7ea21e8cae62e43016f8))


## v7.29.2 (2022-06-20)

### Fix

* fix: ensure should_bump checks against release version if not prerelease (#457)

Co-authored-by: Sebastian Seith &lt;sebastian@vermill.io&gt; ([`da0606f`](https://github.com/python-semantic-release/python-semantic-release/commit/da0606f0d67ada5f097c704b9423ead3b5aca6b2))

### Style

* style: beautify da0606f0d67ada5f097c704b9423ead3b5aca6b2 ([`5d363fa`](https://github.com/python-semantic-release/python-semantic-release/commit/5d363fadc05a9cc074ce1cf2a777a879b4a82bc8))


## v7.29.1 (2022-06-01)

### Fix

* fix: Capture correct release version when patch has more than one digit (#448) ([`426cdc7`](https://github.com/python-semantic-release/python-semantic-release/commit/426cdc7d7e0140da67f33b6853af71b2295aaac2))

### Style

* style: beautify 426cdc7d7e0140da67f33b6853af71b2295aaac2 ([`1c5184d`](https://github.com/python-semantic-release/python-semantic-release/commit/1c5184db55efc9c1b4b2c59e6e7a7564396fb02a))


## v7.29.0 (2022-05-27)

### Chore

* chore: fix test and doc failures ([`0778516`](https://github.com/python-semantic-release/python-semantic-release/commit/077851677930f0f4d779bbb4c6e3c5eef3bed83e))

### Ci

* ci: adjust actions test phase to use fetch-depth: 0 to fix ci tests (#446)

Co-authored-by: Sebastian Seith &lt;sebastian@vermill.io&gt;
Co-authored-by: github-actions &lt;action@github.com&gt; ([`3329eef`](https://github.com/python-semantic-release/python-semantic-release/commit/3329eeffb077f628e4a965bc7fd922d09d6b63da))

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

### Ci

* ci: update `github-actions-x/commit` action ([`2a25668`](https://github.com/python-semantic-release/python-semantic-release/commit/2a25668b29e89ce656bc710c260e0bc5233d2997))

### Fix

* fix: fix getting current version when `version_source=tag_only` (#437) ([`b247936`](https://github.com/python-semantic-release/python-semantic-release/commit/b247936a81c0d859a34bf9f17ab8ca6a80488081))

### Style

* style: beautify 2a25668b29e89ce656bc710c260e0bc5233d2997 ([`3575317`](https://github.com/python-semantic-release/python-semantic-release/commit/357531782705de13901ec668b9ed489fad4a9e02))


## v7.28.0 (2022-04-11)

### Feature

* feat: add `tag_only` option for `version_source` (#436)

Fixes #354 ([`cf74339`](https://github.com/python-semantic-release/python-semantic-release/commit/cf743395456a86c62679c2c0342502af043bfc3b))


## v7.27.1 (2022-04-03)

### Chore

* chore(dependencies): unpin tomlkit dependency (#429)

- tests for a tomlkit regression don&#39;t fail anymore with newer tomlkit
- keep comment in setup.py about tomlkit being pinned at some point in time

refs #336 ([`8515879`](https://github.com/python-semantic-release/python-semantic-release/commit/85158798ca438c1dafc84036d13c2988c934f02f))

### Fix

* fix(prerelase): pass prerelease option to get_current_version (#432)

The `get_current_version` function accepts a `prerelease` argument which
was never passed. ([`aabab0b`](https://github.com/python-semantic-release/python-semantic-release/commit/aabab0b7ce647d25e0c78ae6566f1132ece9fcb9))

### Style

* style: beautify aabab0b7ce647d25e0c78ae6566f1132ece9fcb9 ([`e17f83a`](https://github.com/python-semantic-release/python-semantic-release/commit/e17f83a3b6657489f31d71dd916c682da5ff8aa9))


## v7.27.0 (2022-03-15)

### Chore

* chore(dependencies): extend allowed version range for python-gitlab (#417)

* chore(dependencies): extend allowed version range for python-gitlab
* fix(type): ignore mypy errors for dynamic RESTObject ([`8ee4d4b`](https://github.com/python-semantic-release/python-semantic-release/commit/8ee4d4b8dabfa5c6cd2aa6180d4a8da8f3c9554c))

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

### Style

* style: beautify 7064265627a2aba09caa2873d823b594e0e23e77 ([`fab060a`](https://github.com/python-semantic-release/python-semantic-release/commit/fab060ac0028fde527317418f6e88ccd152c6333))


## v7.25.2 (2022-02-24)

### Fix

* fix(gitea): use form-data from asset upload (#421) ([`e011944`](https://github.com/python-semantic-release/python-semantic-release/commit/e011944987885f75b80fe16a363f4befb2519a91))


## v7.25.1 (2022-02-23)

### Fix

* fix(gitea): build status and asset upload (#420)

* fix(gitea): handle list build status response
* fix(gitea): use form-data for upload_asset ([`57db81f`](https://github.com/python-semantic-release/python-semantic-release/commit/57db81f4c6b96da8259e3bad9137eaccbcd10f6e))

### Style

* style: beautify 57db81f4c6b96da8259e3bad9137eaccbcd10f6e ([`9fbb28f`](https://github.com/python-semantic-release/python-semantic-release/commit/9fbb28f932400d4c55cef2e03fe016345b6562bb))

* style: beautify aba6f5e1583c10a001b4ba1623b5806f6d506d69 ([`a4a8743`](https://github.com/python-semantic-release/python-semantic-release/commit/a4a87432f5124098af1c889109746edc416f746a))

### Test

* test: fix test_repo_with_custom_* on Windows (#416)

Prevent test_repo_with_custom_* from failing when run on Windows due to different path seperator. ([`aba6f5e`](https://github.com/python-semantic-release/python-semantic-release/commit/aba6f5e1583c10a001b4ba1623b5806f6d506d69))


## v7.25.0 (2022-02-17)

### Documentation

* docs: document tag_commit

Fixes #410 ([`b631ca0`](https://github.com/python-semantic-release/python-semantic-release/commit/b631ca0a79cb2d5499715d43688fc284cffb3044))

### Feature

* feat(hvcs): add gitea support (#412) ([`b7e7936`](https://github.com/python-semantic-release/python-semantic-release/commit/b7e7936331b7939db09abab235c8866d800ddc1a))

### Style

* style: beautify b7e7936331b7939db09abab235c8866d800ddc1a ([`f1e3ecb`](https://github.com/python-semantic-release/python-semantic-release/commit/f1e3ecb79122fd2571660661441bc1ab4295cc92))

* style: beautify b631ca0a79cb2d5499715d43688fc284cffb3044 ([`c59095e`](https://github.com/python-semantic-release/python-semantic-release/commit/c59095ed5953af2efd418ac7aec772e880b3ece3))


## v7.24.0 (2022-01-24)

### Feature

* feat: include additional changes in release commits

Add new config keys, `pre_commit_command` and `commit_additional_files`,
to allow custom file changes alongside the release commits. ([`3e34f95`](https://github.com/python-semantic-release/python-semantic-release/commit/3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9))

### Style

* style: beautify 3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9 ([`1ad5183`](https://github.com/python-semantic-release/python-semantic-release/commit/1ad518379df054a089a2b6903c33ad622fc19ce7))


## v7.23.0 (2021-11-30)

### Chore

* chore: sync changes with upstream ([`c9ac06d`](https://github.com/python-semantic-release/python-semantic-release/commit/c9ac06d98ecb8e9140523d5ac262ab8ce11a324e))

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

### Style

* style: beautify 01eea03a2c4db790bfa881037cdd2d6e8c1511a3 ([`6cf85a7`](https://github.com/python-semantic-release/python-semantic-release/commit/6cf85a7ddb9cd6957eb761159cf75dc4df5ed58e))

### Test

* test: Fix tests of angular options ([`01eea03`](https://github.com/python-semantic-release/python-semantic-release/commit/01eea03a2c4db790bfa881037cdd2d6e8c1511a3))


## v7.21.0 (2021-11-21)

### Style

* style: beautify 02569161e57b96a36294626012c311ae0d55a707 ([`6afa90c`](https://github.com/python-semantic-release/python-semantic-release/commit/6afa90c3c357830a7357d3cc73a1098be78b68d3))

### Unknown

* Merge branch &#39;pr-364&#39; ([`0256916`](https://github.com/python-semantic-release/python-semantic-release/commit/02569161e57b96a36294626012c311ae0d55a707))


## v7.20.0 (2021-11-21)

### Chore

* chore: update GitHub Actions with new variable names ([`7bd3a73`](https://github.com/python-semantic-release/python-semantic-release/commit/7bd3a735e87a872355b1312ab9ab7e1e4d35d0a1))

* chore: update GitHub Actions Dockerfile to Python 3.9

Fixes #388 ([`f010a15`](https://github.com/python-semantic-release/python-semantic-release/commit/f010a15dd03f4ef34e4093cc1a7ee357c6db12eb))

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

### Style

* style: beautify d7406ef55287c5a4a70e79c63292f5416ab0f00d ([`2cf59cc`](https://github.com/python-semantic-release/python-semantic-release/commit/2cf59ccc28920df686a1fdcfef1894892d07e02c))

### Unknown

* Merge pull request #395 from fleXible-public/feature/repository ([`d7406ef`](https://github.com/python-semantic-release/python-semantic-release/commit/d7406ef55287c5a4a70e79c63292f5416ab0f00d))

* Merge branch &#39;master&#39; into feature/repository

# Conflicts:
#	semantic_release/cli.py
#	semantic_release/defaults.cfg
#	semantic_release/pypi.py
#	tests/test_cli.py
#	tests/test_pypi.py
#	tests/test_settings.py ([`55bdbb9`](https://github.com/python-semantic-release/python-semantic-release/commit/55bdbb9964311a00bf117325f8e84326c1b74c20))


## v7.19.2 (2021-09-04)

### Fix

* fix: Fixed ImproperConfig import error (#377) ([`b011a95`](https://github.com/python-semantic-release/python-semantic-release/commit/b011a9595df4240cb190bfb1ab5b6d170e430dfc))


## v7.19.1 (2021-08-17)

### Fix

* fix: add get_formatted_tag helper instead of hardcoded v-prefix in the git tags ([`1a354c8`](https://github.com/python-semantic-release/python-semantic-release/commit/1a354c86abad77563ebce9a6944256461006f3c7))

### Style

* style: beautify 1a354c86abad77563ebce9a6944256461006f3c7 ([`a3fc6c8`](https://github.com/python-semantic-release/python-semantic-release/commit/a3fc6c8974d471366696545bb17218d509fb75d3))


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

### Chore

* chore: bump responses to latest version (#343)

The current version has a Deprecation warning:

inspect.getargspec() is deprecated since Python 3.0,
use inspect.signature() or inspect.getfullargspec() ([`e953157`](https://github.com/python-semantic-release/python-semantic-release/commit/e953157125f4528759453218f75b6e51cafd2cc3))

### Ci

* ci: place beautify and release in the same concurrency group

Otherwise, an older release job could push while a newer beautify job is
running. ([`26d45b3`](https://github.com/python-semantic-release/python-semantic-release/commit/26d45b3d495d41f458fee1f50e09062050321725))

* ci: install types-requests to fix mypy check (#347) ([`421e908`](https://github.com/python-semantic-release/python-semantic-release/commit/421e9089d4a8029ef791a4cfff088cec0645db37))

* ci: install types-requests to fix mypy check (#345) ([`cd33df6`](https://github.com/python-semantic-release/python-semantic-release/commit/cd33df6221fa26fd875bedc40a34427ff1997ba2))

### Documentation

* docs: update trove classifiers to reflect supported versions (#344) ([`7578004`](https://github.com/python-semantic-release/python-semantic-release/commit/7578004ed4b20c2bd553782443dfd77535faa377))

* docs: recommend setting a concurrency group for GitHub Actions ([`34b0735`](https://github.com/python-semantic-release/python-semantic-release/commit/34b07357ab3f4f4aa787b71183816ec8aaf334a8))

### Fix

* fix: use release-api for gitlab ([`1ef5cab`](https://github.com/python-semantic-release/python-semantic-release/commit/1ef5caba2d8dd0f2647bc51ede0ef7152d8b7b8d))

### Refactor

* refactor: update VersionDeclaration to pathlib ([`e9d2916`](https://github.com/python-semantic-release/python-semantic-release/commit/e9d2916094dd6a537adc6c643d759c3f49100941))

### Style

* style: beautify 60393d730f16300df02cd071c7a21c5f9b591930 ([`a0015c7`](https://github.com/python-semantic-release/python-semantic-release/commit/a0015c73d4d2e6eb4d610f50db2c2be1863c0e39))

### Test

* test: added releases to gitlab mock ([`60393d7`](https://github.com/python-semantic-release/python-semantic-release/commit/60393d730f16300df02cd071c7a21c5f9b591930))

* test: add a failing test to reproduce tomlkit bug

Ref #336
Ref #338 ([`2041f10`](https://github.com/python-semantic-release/python-semantic-release/commit/2041f10c722b8f381593eefb8f3fd80ea126edde))


## v7.16.1 (2021-06-08)

### Fix

* fix: tomlkit should stay at 0.7.0

See https://github.com/relekang/python-semantic-release/pull/339#discussion_r647629387 ([`769a5f3`](https://github.com/python-semantic-release/python-semantic-release/commit/769a5f31115cdb1f43f19a23fe72b96a8c8ba0fc))


## v7.16.0 (2021-06-08)

### Feature

* feat: add option to omit tagging (#341) ([`20603e5`](https://github.com/python-semantic-release/python-semantic-release/commit/20603e53116d4f05e822784ce731b42e8cbc5d8f))

### Style

* style: beautify 20603e53116d4f05e822784ce731b42e8cbc5d8f ([`db49709`](https://github.com/python-semantic-release/python-semantic-release/commit/db49709c6da5cb7834fdfbe1909ba80ae070fefc))


## v7.15.6 (2021-06-08)

### Ci

* ci: update beautify job ([`b5ad0d7`](https://github.com/python-semantic-release/python-semantic-release/commit/b5ad0d7186bbde254e90450b3812c573c0d56f1e))

### Fix

* fix: update click and tomlkit (#339) ([`947ea3b`](https://github.com/python-semantic-release/python-semantic-release/commit/947ea3bc0750735941446cf4a87bae20e750ba12))

### Style

* style: beautify b5ad0d7186bbde254e90450b3812c573c0d56f1e ([`b8fb692`](https://github.com/python-semantic-release/python-semantic-release/commit/b8fb692793ba6868ae11ef25f64750d3c87ffcf1))


## v7.15.5 (2021-05-26)

### Fix

* fix: pin tomlkit to 0.7.0 ([`2cd0db4`](https://github.com/python-semantic-release/python-semantic-release/commit/2cd0db4537bb9497b72eb496f6bab003070672ab))


## v7.15.4 (2021-04-29)

### Fix

* fix: Change log level of failed toml loading

Fixes #235 ([`24bb079`](https://github.com/python-semantic-release/python-semantic-release/commit/24bb079cbeff12e7043dd35dd0b5ae03192383bb))

### Test

* test: Fix test for bad toml syntax ([`e52ee3c`](https://github.com/python-semantic-release/python-semantic-release/commit/e52ee3c4c9b0254822bf80a9369b9cdb2e50ba57))


## v7.15.3 (2021-04-03)

### Fix

* fix: Add venv to path in github action ([`583c5a1`](https://github.com/python-semantic-release/python-semantic-release/commit/583c5a13e40061fc544b82decfe27a6c34f6d265))


## v7.15.2 (2021-04-03)

### Ci

* ci: Add python 3.9 to test runs ([`2a99b65`](https://github.com/python-semantic-release/python-semantic-release/commit/2a99b65f10c8e7230a80885d2ebe6cacf6541450))

### Documentation

* docs: clarify that HVCS should be lowercase

Fixes #330 ([`da0ab0c`](https://github.com/python-semantic-release/python-semantic-release/commit/da0ab0c62c4ce2fa0d815e5558aeec1a1e23bc89))

### Fix

* fix: Use absolute path for venv in github action ([`d4823b3`](https://github.com/python-semantic-release/python-semantic-release/commit/d4823b3b6b1fcd5c33b354f814643c9aaf85a06a))

* fix: Set correct path for venv in action script ([`aac02b5`](https://github.com/python-semantic-release/python-semantic-release/commit/aac02b5a44a6959328d5879578aa3536bdf856c2))

* fix: Run semantic-release in virtualenv in the github action

Fixes #331 ([`b508ea9`](https://github.com/python-semantic-release/python-semantic-release/commit/b508ea9f411c1cd4f722f929aab9f0efc0890448))


## v7.15.1 (2021-03-26)

### Chore

* chore: Clean up imports ([`fe444b7`](https://github.com/python-semantic-release/python-semantic-release/commit/fe444b77c91f829916870e46d64635fe36993466))

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

### Style

* style: improve code formatting ([`6ebc3b1`](https://github.com/python-semantic-release/python-semantic-release/commit/6ebc3b15bb46fdbbfdd7381188826bc5204730b8))


## v7.15.0 (2021-02-18)

### Documentation

* docs: add documentation for releasing on a Jenkins instance (#324) ([`77ad988`](https://github.com/python-semantic-release/python-semantic-release/commit/77ad988a2057be59e4559614a234d6871c06ee37))

### Feature

* feat: allow the use of .pypirc for twine uploads (#325) ([`6bc56b8`](https://github.com/python-semantic-release/python-semantic-release/commit/6bc56b8aa63069a25a828a2d1a9038ecd09b7d5d))

### Style

* style: improve code formatting ([`a0cc0aa`](https://github.com/python-semantic-release/python-semantic-release/commit/a0cc0aa51308fa109ff84668f46345fd6352bb95))


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

### Style

* style: improve code formatting ([`0b128ae`](https://github.com/python-semantic-release/python-semantic-release/commit/0b128ae3b2e01722e949be92755e4e944d16c7d1))


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

### Style

* style: improve code formatting ([`0c0c45d`](https://github.com/python-semantic-release/python-semantic-release/commit/0c0c45deae4bbf237608b0107d91884a9c5d5dc3))


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

### Style

* style: improve code formatting ([`a13dfde`](https://github.com/python-semantic-release/python-semantic-release/commit/a13dfdefbbdc7b4031de39637220d6dc9d96f517))


## v7.12.0 (2021-01-25)

### Documentation

* docs(actions): PAT must be passed to checkout step too

Fixes #311 ([`e2d8e47`](https://github.com/python-semantic-release/python-semantic-release/commit/e2d8e47d2b02860881381318dcc088e150c0fcde))

### Feature

* feat(github): retry GitHub API requests on failure (#314)

* refactor(github): use requests.Session to call raise_for_status

* fix(github): add retries to github API requests ([`ac241ed`](https://github.com/python-semantic-release/python-semantic-release/commit/ac241edf4de39f4fc0ff561a749fa85caaf9e2ae))

### Style

* style: improve code formatting ([`be87196`](https://github.com/python-semantic-release/python-semantic-release/commit/be8719605e0a9fa9fda2335556742e09cfa06189))


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

### Style

* style: improve code formatting ([`1dd8484`](https://github.com/python-semantic-release/python-semantic-release/commit/1dd84847a9eaf8d2467ae5b4ee82492ef563612f))


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

### Style

* style: improve code formatting ([`766bd2e`](https://github.com/python-semantic-release/python-semantic-release/commit/766bd2e12cb8aca36d4deb937033334c77144fb2))

### Test

* test(build): add tests for should_build() and should_remove_dist() ([`527f02b`](https://github.com/python-semantic-release/python-semantic-release/commit/527f02bded40c46bc61f0aad57b707762ef0fba5))

### Unknown

* Merge branch &#39;master&#39; into feature/repository ([`b85fec5`](https://github.com/python-semantic-release/python-semantic-release/commit/b85fec5c28191beb53b6a3552e5b88dbcc97db5f))


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

### Refactor

* refactor: use raise_for_status and enhance error reporting for github uploads ([`69aef9f`](https://github.com/python-semantic-release/python-semantic-release/commit/69aef9f8ea11547cceb326068f7d3ab0bfa4afa7))

### Style

* style: improve code formatting ([`6eec4b4`](https://github.com/python-semantic-release/python-semantic-release/commit/6eec4b42cbfc546ee035de07451584a2672be485))


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

### Style

* style: improve code formatting ([`8182668`](https://github.com/python-semantic-release/python-semantic-release/commit/81826680a30b062ebd3e2a21b62d655b1ac6a962))


## v7.7.0 (2020-12-12)

### Feature

* feat(changelog): add PR links in markdown (#282)

GitHub release notes automagically link to the PR, but changelog
markdown doesn&#39;t. Replace a PR number at the end of a message
with a markdown link. ([`0448f6c`](https://github.com/python-semantic-release/python-semantic-release/commit/0448f6c350bbbf239a81fe13dc5f45761efa7673))

### Style

* style: improve code formatting ([`38cf32e`](https://github.com/python-semantic-release/python-semantic-release/commit/38cf32e986fc45c42101098e194cff881c111ea5))


## v7.6.0 (2020-12-06)

### Documentation

* docs: add documentation for option `major_on_zero` ([`2e8b26e`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8b26e4ee0316a2cf2a93c09c783024fcd6b3ba))

### Feature

* feat: add `major_on_zero` option

To control if bump major or not when current major version is zero. ([`d324154`](https://github.com/python-semantic-release/python-semantic-release/commit/d3241540e7640af911eb24c71e66468feebb0d46))

### Refactor

* refactor(history): move changelog_scope default (#284)

* Move the default for changelog_scope from inline to defaults.cfg.
* Add missing header in docs. ([`b7e1376`](https://github.com/python-semantic-release/python-semantic-release/commit/b7e1376ee1688e5e6dcc069ce623f49e3a389052))

### Style

* style(settings): alphabetize boolean settings (#283)

A few settings were not in alphabetical order. ([`60a3535`](https://github.com/python-semantic-release/python-semantic-release/commit/60a3535f21380de8c9eaec7fe4dea9eb3d04dee1))


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

### Style

* style: improve code formatting ([`eaf0064`](https://github.com/python-semantic-release/python-semantic-release/commit/eaf00643363f7040a4078d282e5589b2973c2dec))


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

### Style

* style: improve code formatting ([`b9016cd`](https://github.com/python-semantic-release/python-semantic-release/commit/b9016cd234e5dea140a9aa61a52f99cec7f3726f))


## v7.3.0 (2020-09-28)

### Chore

* chore: make env statement uppercase in Dockerfile (#262) ([`911670d`](https://github.com/python-semantic-release/python-semantic-release/commit/911670d78c7a5f2e9816161f6ef5344e0c8034e9))

### Ci

* ci: check commit logs with commitlint (#263)

The contributing guide says that the project should itself follow the
Angular commit convention, but there is nothing to enforce it AFAIK.

I had a similar problem on a project where I&#39;m using
`python-semantic-release` and I&#39;ve added a Github action to
test it on CI, you might find it useful too. ([`016fde6`](https://github.com/python-semantic-release/python-semantic-release/commit/016fde683924d380d25579bd0cff0c7f8b7b2240))

### Documentation

* docs: fix docstring

Stumbled upon this docstring which first line seems copy/pasted from
the method above. ([`5a5e2cf`](https://github.com/python-semantic-release/python-semantic-release/commit/5a5e2cfb5e6653fb2e95e6e23e56559953b2c2b4))

### Feature

* feat: Generate `changelog.md` file (#266) ([`2587dfe`](https://github.com/python-semantic-release/python-semantic-release/commit/2587dfed71338ec6c816f58cdf0882382c533598))

### Style

* style: improve code formatting ([`8b62e79`](https://github.com/python-semantic-release/python-semantic-release/commit/8b62e797dbab33a4a716d70c3abec6f46e36473f))


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

### Chore

* chore: update with username change ([`48972fb`](https://github.com/python-semantic-release/python-semantic-release/commit/48972fb761ed9b0fb376fa3ad7028d65ff407ee6))

### Documentation

* docs: link to getting started guide in README ([`f490e01`](https://github.com/python-semantic-release/python-semantic-release/commit/f490e0194fa818db4d38c185bc5e6245bfde546b))

* docs: create &#39;getting started&#39; instructions (#256) ([`5f4d000`](https://github.com/python-semantic-release/python-semantic-release/commit/5f4d000c3f153d1d23128acf577e389ae879466e))

### Fix

* fix: support multiline version_pattern matching by default ([`82f7849`](https://github.com/python-semantic-release/python-semantic-release/commit/82f7849dcf29ba658e0cb3b5d21369af8bf3c16f))

### Style

* style: improve code formatting ([`71fdb9f`](https://github.com/python-semantic-release/python-semantic-release/commit/71fdb9ff83e56b22367dd810b09e2eaec51c6155))


## v7.2.2 (2020-07-26)

### Ci

* ci: pin isort version ([`cf80ad3`](https://github.com/python-semantic-release/python-semantic-release/commit/cf80ad3dc01b35706b1da50e178373c010c22acf))

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

### Style

* style: improve code formatting ([`904ed7e`](https://github.com/python-semantic-release/python-semantic-release/commit/904ed7eb60332b1984529b2a38afaee3f5facdd3))


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

### Style

* style: improve code formatting ([`f040bb9`](https://github.com/python-semantic-release/python-semantic-release/commit/f040bb96b677589be30c866dc0a483195b6ec74b))


## v7.1.1 (2020-05-28)

### Fix

* fix(changelog): swap sha and message in table changelog ([`6741370`](https://github.com/python-semantic-release/python-semantic-release/commit/6741370ab09b1706ff6e19b9fbe57b4bddefc70d))


## v7.1.0 (2020-05-24)

### Feature

* feat(changelog): add changelog_table component (#242)

Add an alternative changelog component which displays each section as a
row in a table.

Fixes #237 ([`fe6a7e7`](https://github.com/python-semantic-release/python-semantic-release/commit/fe6a7e7fa014ffb827a1430dbcc10d1fc84c886b))

### Style

* style: improve code formatting ([`a43beb5`](https://github.com/python-semantic-release/python-semantic-release/commit/a43beb56f1bf4645be47399ded14756fb48d95c6))


## v7.0.0 (2020-05-22)

### Documentation

* docs: add conda-forge badge ([`e9536bb`](https://github.com/python-semantic-release/python-semantic-release/commit/e9536bbe119c9e3b90c61130c02468e0e1f14141))

### Feature

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

### Style

* style: improve code formatting ([`1dfca97`](https://github.com/python-semantic-release/python-semantic-release/commit/1dfca97c3856e496e9e2cda429b8aa093799bd5b))


## v6.4.1 (2020-05-15)

### Fix

* fix: convert \r\n to \n in commit messages

Fixes #239 ([`34acbbc`](https://github.com/python-semantic-release/python-semantic-release/commit/34acbbcd25320a9d18dcd1a4f43e1ce1837b2c9f))

### Style

* style: improve code formatting ([`9684c0f`](https://github.com/python-semantic-release/python-semantic-release/commit/9684c0f3a96af46182f4ffcee041768a24ad9b71))


## v6.4.0 (2020-05-15)

### Feature

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

### Style

* style: improve code formatting ([`52bbd72`](https://github.com/python-semantic-release/python-semantic-release/commit/52bbd729bc6a688b422b4abada6826231573f7ce))

* style: improve code formatting ([`2a88ef6`](https://github.com/python-semantic-release/python-semantic-release/commit/2a88ef62da022fc7deb1985d09825a4067c1824d))

### Test

* test: capture logging output

Adapt the CLI tests so that pytest can capture the log output, and display it if there is a failure. This helps with debugging. ([`32cfd90`](https://github.com/python-semantic-release/python-semantic-release/commit/32cfd903f6f5fe8f31eb0dc1d45464071e54423d))


## v6.3.1 (2020-05-11)

### Ci

* ci: update stale to v3 ([`ce5cd0c`](https://github.com/python-semantic-release/python-semantic-release/commit/ce5cd0c894a65dd4cef4aba6658e7d45803fe833))

* ci: create annotations for test failures ([`233a6f4`](https://github.com/python-semantic-release/python-semantic-release/commit/233a6f480ff67165f0f54522230e139b918bb032))

### Fix

* fix: use getboolean for commit_version_number

Fixes #186 ([`a60e0b4`](https://github.com/python-semantic-release/python-semantic-release/commit/a60e0b4e3cadf310c3e0ad67ebeb4e69d0ee50cb))

### Style

* style: improve code formatting ([`49b3389`](https://github.com/python-semantic-release/python-semantic-release/commit/49b3389a316d221923b4957d83d4e005e85102d3))


## v6.3.0 (2020-05-09)

### Documentation

* docs: rewrite commit-log-parsing.rst ([`4c70f4f`](https://github.com/python-semantic-release/python-semantic-release/commit/4c70f4f2aa3343c966d1b7ab8566fcc782242ab9))

* docs: document compare_link option ([`e52c355`](https://github.com/python-semantic-release/python-semantic-release/commit/e52c355c0d742ddd2cfa65d42888296942e5bec5))

### Feature

* feat(history): support linking compare page in changelog

Fixes #218 ([`79a8e02`](https://github.com/python-semantic-release/python-semantic-release/commit/79a8e02df82fbc2acecaad9e9ff7368e61df3e54))

### Style

* style: improve code formatting ([`ae4f1d6`](https://github.com/python-semantic-release/python-semantic-release/commit/ae4f1d69866c3830d691e9bd6b48627d70f705ae))

* style: improve code formatting ([`7a85403`](https://github.com/python-semantic-release/python-semantic-release/commit/7a8540322f1308399653d10657e24a7b28943767))

### Test

* test: split history tests into multiple files ([`14e4ae2`](https://github.com/python-semantic-release/python-semantic-release/commit/14e4ae2a527b29026f49ee1346cab708114e60c9))


## v6.2.0 (2020-05-02)

### Ci

* ci: add help-wanted automatically

Add the help-wanted label to bug reports and feature requests which have not had any activity in 3 weeks. This is implemented using stale, however it is set such that the issues will not be closed. ([`56e092a`](https://github.com/python-semantic-release/python-semantic-release/commit/56e092ab498bb24e43570ffb184f170b5c041ca8))

* ci: close stale questions automatically (#226)

Any issues which are labelled as a question will be closed after two weeks of inactivity. This doesn&#39;t affect other types of issues. ([`539918c`](https://github.com/python-semantic-release/python-semantic-release/commit/539918cdb97e5578cbace8d74a6680e6662cb9bb))

* ci: pass SHA from beautify to release

Checkout the current SHA from the end of the beautify job for releasing, 
instead of master. This will either be the same as the commit we are 
running for, or the SHA of a style commit. This prevents releasing of 
untested code.

See 
https://github.community/t5/GitHub-Actions/Checkout-commit-pushed-by-previous-job/m-p/55847#M9670 ([`76e34b6`](https://github.com/python-semantic-release/python-semantic-release/commit/76e34b6b52b8019e87eaddf295d0781b6aa51541))

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

### Style

* style: improve code formatting ([`a1d324c`](https://github.com/python-semantic-release/python-semantic-release/commit/a1d324c4d1824fe521d9e21fbd43589d26d3406c))

### Test

* test: test against Python 3.6 ([`a88efb9`](https://github.com/python-semantic-release/python-semantic-release/commit/a88efb9c581fe4c90577b578b4e86efea7944ecc))


## v6.1.0 (2020-04-26)

### Documentation

* docs: add documentation for PYPI_TOKEN ([`a8263a0`](https://github.com/python-semantic-release/python-semantic-release/commit/a8263a066177d1d42f2844e4cb42a76a23588500))

### Feature

* feat(actions): support PYPI_TOKEN on GitHub Actions

Add support for the new PYPI_TOKEN environment variable to be used on GitHub Actions. ([`df2c080`](https://github.com/python-semantic-release/python-semantic-release/commit/df2c0806f0a92186e914cfc8cc992171d74422df))

* feat(pypi): support easier use of API tokens

Allow setting the environment variable PYPI_TOKEN to automatically fill the username as __token__.

Fixes #213 ([`bac135c`](https://github.com/python-semantic-release/python-semantic-release/commit/bac135c0ae7a6053ecfc7cdf2942c3c89640debf))

### Refactor

* refactor(history): combine = and : into one regex

Use a [=:] group instead of running two separate searches. ([`bbaf6b9`](https://github.com/python-semantic-release/python-semantic-release/commit/bbaf6b926532314c41c733be24847a6ab5686a74))

### Style

* style: improve code formatting ([`0a4d8ba`](https://github.com/python-semantic-release/python-semantic-release/commit/0a4d8ba209c8fad7f254278e8bb382505885741d))

* style: improve code formatting ([`149e426`](https://github.com/python-semantic-release/python-semantic-release/commit/149e426c7bf70482e14e41c69f96236090df7ed5))


## v6.0.1 (2020-04-15)

### Fix

* fix(hvcs): convert get_hvcs to use LoggedFunction

This was missed in 213530fb0c914e274b81d1dacf38ea7322b5b91f ([`3084249`](https://github.com/python-semantic-release/python-semantic-release/commit/308424933fd3375ca3730d9eaf8abbad2435830b))


## v6.0.0 (2020-04-15)

### Breaking

* refactor(debug): use logging and click_log instead of ndebug

BREAKING CHANGE: `DEBUG=&#34;*&#34;` no longer has an effect, instead use 
`--verbosity DEBUG`. ([`15b1f65`](https://github.com/python-semantic-release/python-semantic-release/commit/15b1f650f29761e1ab2a91b767cbff79b2057a4c))

### Build

* build(pip): store requirements in setup.py

Remove the requirements directory and instead store all required 
libraries directly inside setup.py. Development, testing and docs 
dependencies are included as extras. ([`401468f`](https://github.com/python-semantic-release/python-semantic-release/commit/401468f312cf4f3b52006c68c58c4645b5e19802))

### Chore

* chore(tox): clean up tox.ini

Allow mypy and coverage to run on any Python version. ([`28feba6`](https://github.com/python-semantic-release/python-semantic-release/commit/28feba6801315422f492b38b2299a283fb7a3462))

### Ci

* ci: always checkout most recent commit to release

This should pull a beautify commit if one has been created, allowing the 
new version to be pushed. ([`6c98aab`](https://github.com/python-semantic-release/python-semantic-release/commit/6c98aab932724e3aab08e68b75439bc8c31bd877))

* ci: cache testing dependencies

This should help improve the speed of the testing workflow by caching 
downloaded dependencies. ([`4f53e35`](https://github.com/python-semantic-release/python-semantic-release/commit/4f53e351960a6b658f50265384c9e8f678718f68))

* ci: move beautification to separate workflow

See https://github.com/relekang/python-semantic-release/pull/214#issuecomment-613916623 ([`6ed42dc`](https://github.com/python-semantic-release/python-semantic-release/commit/6ed42dc83027f48865e4309d520c8b6654b88058))

* ci: beautify code automatically (#214)

Run isort and Black on pushes to master. Any edits made are committed. isort and flake8 no longer run as a check. ([`d49c4ac`](https://github.com/python-semantic-release/python-semantic-release/commit/d49c4ac8d0eb6086693dfbd3e06c63d7e9b5d94c))

### Documentation

* docs: create Read the Docs config file ([`aa5a1b7`](https://github.com/python-semantic-release/python-semantic-release/commit/aa5a1b700a1c461c81c6434686cb6f0504c4bece))

* docs: include README.rst in index.rst

These files were very similar so it makes sense to simply include one 
inside the other. ([`8673a9d`](https://github.com/python-semantic-release/python-semantic-release/commit/8673a9d92a9bf348bb3409e002a830741396c8ca))

* docs: rewrite README.rst ([`e049772`](https://github.com/python-semantic-release/python-semantic-release/commit/e049772cf14cdd49538cf357db467f0bf3fe9587))

* docs: move action.rst into main documentation ([`509ccaf`](https://github.com/python-semantic-release/python-semantic-release/commit/509ccaf307a0998eced69ad9fee1807132babe28))

* docs: rewrite troubleshooting page ([`0285de2`](https://github.com/python-semantic-release/python-semantic-release/commit/0285de215a8dac3fcc9a51f555fa45d476a56dff))

### Refactor

* refactor(debug): improve debug output ([`213530f`](https://github.com/python-semantic-release/python-semantic-release/commit/213530fb0c914e274b81d1dacf38ea7322b5b91f))

### Style

* style: improve code formatting ([`a8fdab5`](https://github.com/python-semantic-release/python-semantic-release/commit/a8fdab5b9dbc3dbf092181f30edbdd626a8f668c))

* style: improve code formatting ([`d1efc22`](https://github.com/python-semantic-release/python-semantic-release/commit/d1efc22605b06e8901e82d7ddb865ef69f143c54))

### Unknown

* doc: updated doc with new ParsedCommit object instead of nested Tuple ([`ac565dc`](https://github.com/python-semantic-release/python-semantic-release/commit/ac565dc824ea575e8899b932db148ac28e27fce2))


## v5.2.0 (2020-04-09)

### Ci

* ci: fetch full history in release job

I didn&#39;t realise that actions/checkout@v2 only fetches 1 commit by 
default. ([`a02a9b7`](https://github.com/python-semantic-release/python-semantic-release/commit/a02a9b7e34d8e7f8bb3b9c8aa1b5e1ef8bdd406c))

* ci: run tests on pull_request

The tests didn&#39;t run for #211 which caused a flake8 failure to be 
missed. ([`32fd77e`](https://github.com/python-semantic-release/python-semantic-release/commit/32fd77ed835bcfc943abeacec4e327df045b2ec9))

* ci: run tests on GitHub Actions ([`39ff283`](https://github.com/python-semantic-release/python-semantic-release/commit/39ff283312a0c686bfc5be71e1da9b6456652d95))

### Documentation

* docs: automate API docs

Automatically create pages in the API docs section using sphinx-autodoc. This is added as an event handler in conf.py. ([`7d4fea2`](https://github.com/python-semantic-release/python-semantic-release/commit/7d4fea266cc75007de51609131eb6d1e324da608))

### Feature

* feat(github): add tag as default release name ([`2997908`](https://github.com/python-semantic-release/python-semantic-release/commit/2997908f80f4fcec56917d237a079b961a06f990))

### Refactor

* refactor(vcs): add functools.wraps to check_repo ([`4d97187`](https://github.com/python-semantic-release/python-semantic-release/commit/4d971873669d7ed5427108b180cbd5530375d8f3))

### Style

* style: fix styling from 2997908

These code style problems were introduced because tests didn&#39;t run on 
#211. ([`172391e`](https://github.com/python-semantic-release/python-semantic-release/commit/172391ec5b5e490081b9b0ea58a94dfd5be33937))


## v5.1.0 (2020-04-04)

### Chore

* chore(github): create issue templates ([`0f57662`](https://github.com/python-semantic-release/python-semantic-release/commit/0f57662ce7f6ce540b80aa7ad857bcc24edbc897))

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

### Refactor

* refactor(history): use a named tuple for parsed commits

This improves readability as we can use attributes such as &#39;bump&#39; and 
&#39;descriptions&#39; instead of confusing numeric indices. ([`bff40d5`](https://github.com/python-semantic-release/python-semantic-release/commit/bff40d53174ffe27451d82132c31b112c7bee9fd))


## v5.0.2 (2020-03-22)

### Fix

* fix(history): leave case of other characters unchanged

Previously, use of str.capitalize() would capitalize the first letter as expected, but all subsequent letters became lowercase. Now, the other letters remain unchanged. ([`96ba94c`](https://github.com/python-semantic-release/python-semantic-release/commit/96ba94c4b4593997343ec61ecb6c823c1494d0e2))

### Test

* test: Run --help in docker image to make testing of image easier ([`b41e6b2`](https://github.com/python-semantic-release/python-semantic-release/commit/b41e6b27d63321bba8a6bb717de734df300ee1cc))


## v5.0.1 (2020-03-22)

### Fix

* fix: Make action use current version of semantic-release

This gives two benefits:
* In this repo it will work as a smoketest
* In other repos when they specify version int the github workflow they
will get the version they specify. ([`123984d`](https://github.com/python-semantic-release/python-semantic-release/commit/123984d735181c622f3d99088a1ad91321192a11))


## v5.0.0 (2020-03-22)

### Documentation

* docs(pypi): update docstings in pypi.py ([`6502d44`](https://github.com/python-semantic-release/python-semantic-release/commit/6502d448fa65e5dc100e32595e83fff6f62a881a))

### Feature

* feat(build): allow config setting for build command (#195)

* feat(build): allow config setting for build command

BREAKING CHANGE: Previously the build_commands configuration variable set the types of bundles sent to `python setup.py`. It has been replaced by the configuration variable `build_command` which takes the full command e.g. `python setup.py sdist` or `poetry build`.

Closes #188 ([`740f4bd`](https://github.com/python-semantic-release/python-semantic-release/commit/740f4bdb26569362acfc80f7e862fc2c750a46dd))

### Fix

* fix: Rename default of build_command config ([`d5db22f`](https://github.com/python-semantic-release/python-semantic-release/commit/d5db22f9f7acd05d20fd60a8b4b5a35d4bbfabb8))

### Refactor

* refactor(cli): improve readability of cli.py and some log messages ([`646dd81`](https://github.com/python-semantic-release/python-semantic-release/commit/646dd81944bad27f5defe4a33b0ebeb5c9ed0c4e))

* refactor: make check_repo a decorator ([`3799d8b`](https://github.com/python-semantic-release/python-semantic-release/commit/3799d8b595d0b36e59e5486c9b5f1070a47f3903))

### Style

* style: improve readability of history/__init__.py ([`c878cd3`](https://github.com/python-semantic-release/python-semantic-release/commit/c878cd3eb84fe8776913d082270720d4209e6007))

* style: improve readability of parsers ([`f84f317`](https://github.com/python-semantic-release/python-semantic-release/commit/f84f31754240212822227f6880ff110a8dd95214))

* style: improve readability of history/logs.py ([`2f22892`](https://github.com/python-semantic-release/python-semantic-release/commit/2f228921d30e6664986e1ab5a5e840297f52e2f0))

* style: improve readability of vcs_helpers.py ([`e46a358`](https://github.com/python-semantic-release/python-semantic-release/commit/e46a35833c816e570ceea9d67297a725b8ffc9ff))

* style: improve readability of settings.py ([`af4df82`](https://github.com/python-semantic-release/python-semantic-release/commit/af4df82603d9aac70e47672f196a0a5e5160f817))


## v4.11.0 (2020-03-22)

### Ci

* ci: use GitHub Action from this repo ([`4352ea8`](https://github.com/python-semantic-release/python-semantic-release/commit/4352ea8d116abcd5d6c86e897b8d2d5ef72bd663))

* ci: store PyPI username in secrets ([`b6de1a6`](https://github.com/python-semantic-release/python-semantic-release/commit/b6de1a6324ebe3ad6bd8735e16711877e773fea8))

* ci: set up releasing with GitHub Actions

#109: Setup github actions for releasing this project by calling on the current source code. ([`a80cc45`](https://github.com/python-semantic-release/python-semantic-release/commit/a80cc45df47cba6e730afc3c80d959fcba56485c))

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

### Refactor

* refactor(history): remove unnecessary newlines

Since simplifying the capitalization, the comment is no longer needed and so the statement can be compacted onto one line again. ([`ffc3f8b`](https://github.com/python-semantic-release/python-semantic-release/commit/ffc3f8bada5f9a031ffe3af1e00c01b0edb05740))

* refactor(history): use capitalize method for readability

Co-Authored-By: Rolf Erik Lekang &lt;me@rolflekang.com&gt; ([`289349a`](https://github.com/python-semantic-release/python-semantic-release/commit/289349a314f63069ff6f7e40a9d0f2bf0f6063cf))


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

### Test

* test: better test coverage

Adds some coverage mainly on cli and vcs_helpers ([`b7bf6fe`](https://github.com/python-semantic-release/python-semantic-release/commit/b7bf6fe4ea0f1d11e56ec6e39a242253061dc5fc))


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

### Chore

* chore: Add tools requirements file ([`bbf1109`](https://github.com/python-semantic-release/python-semantic-release/commit/bbf110913cfe323bf174986fe7f4b38d88e41bd6))

* chore: Remove tox and mypy from dev requirements ([`9dcfaf0`](https://github.com/python-semantic-release/python-semantic-release/commit/9dcfaf05ee1f8055221d1959ca1accb1017e2d53))

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

### Test

* test: Fix test name ([`aff4454`](https://github.com/python-semantic-release/python-semantic-release/commit/aff4454aa329bcab54b969ed0c41ed429a9b5683))

* test: Add mocking of reading of repo owner

Fixes #108 ([`04cc6b5`](https://github.com/python-semantic-release/python-semantic-release/commit/04cc6b5af969275b1096cbf45f9dc03a105d7034))


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

### Chore

* chore: ignore venv

venv is ignored in config for flake8 and isort.
Should be ignored in git as well. ([`ff58962`](https://github.com/python-semantic-release/python-semantic-release/commit/ff5896242a65c3f6d897eb911137956175d74ebd))

* chore: ignore vscode settings ([`bf9da4c`](https://github.com/python-semantic-release/python-semantic-release/commit/bf9da4ca9754c21d69598d956664e2fa3e6b9d5e))

### Documentation

* docs: DEBUG usage and related

Debug functionality lack documentation.
Thoubleshooting is helped by documenting other
environment variables as well. ([`f08e594`](https://github.com/python-semantic-release/python-semantic-release/commit/f08e5943a9876f2d17a7c02f468720995c7d9ffd))

* docs: correct usage of changelog ([`f4f59b0`](https://github.com/python-semantic-release/python-semantic-release/commit/f4f59b08c73700c6ee04930221bfcb1355cbc48d))

* docs: describing the commands

The commands is lacking from the documentation. ([`b6fa04d`](https://github.com/python-semantic-release/python-semantic-release/commit/b6fa04db3044525a1ee1b5952fb175a706842238))

* docs: update url for commit guidelinesThe guidelines can now be found in theDEVELOPERS.md in angular. ([`90c1b21`](https://github.com/python-semantic-release/python-semantic-release/commit/90c1b217f86263301b91d19d641c7b348e37d960))

### Refactor

* refactor: added debug to hvcshvcs 

 
module did not have any debug ([`0c6237b`](https://github.com/python-semantic-release/python-semantic-release/commit/0c6237bc01ec39608fb768925091c755d9bb25bd))

* refactor: fix import sorting ([`01e4c5d`](https://github.com/python-semantic-release/python-semantic-release/commit/01e4c5d743f2f237d2c85481118e467d4f5fde15))

* refactor: add debug output ([`06f3788`](https://github.com/python-semantic-release/python-semantic-release/commit/06f378819fea7c007176f0950db33b3d485a246a))


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

### Unknown

* Merge pr #89

This was merged locally to fix conflicts. ([`0dad451`](https://github.com/python-semantic-release/python-semantic-release/commit/0dad451617cc752ad3830c9442cf0b0e0993a454))


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

### Test

* test: Update test after adding cleaning of dist ([`202fba5`](https://github.com/python-semantic-release/python-semantic-release/commit/202fba50c287d3df99b22a4f30a96a3d8d9c8141))

* test(angular): Fix pep8 violations ([`a504f26`](https://github.com/python-semantic-release/python-semantic-release/commit/a504f262a05dc27b87e2c766f185b17cd8b39765))


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

### Refactor

* refactor: Fix typing errors ([`5c37d47`](https://github.com/python-semantic-release/python-semantic-release/commit/5c37d477053f3bf25b858c80ef176dada8110e7e))

### Style

* style(vcs_helpers): Add r prefix to regular expression match string

This &#39;raw&#39; designator gets rid of flake8 complaints ([`29c25d3`](https://github.com/python-semantic-release/python-semantic-release/commit/29c25d34f61ae4c2058ffc3ae4219ae6ad8b2775))

### Test

* test: Fix tests ([`d3862e8`](https://github.com/python-semantic-release/python-semantic-release/commit/d3862e890f27d11ba4978de3f79746873731001a))

### Unknown

* Typo, link broken

Change `.. _angular commit guidelins:` to `.. _angular commit guidelines:` ([`721a6dd`](https://github.com/python-semantic-release/python-semantic-release/commit/721a6dd895aa5f0072fc76fe0325f23e565492c4))


## v3.11.2 (2018-06-10)

### Fix

* fix: Upgrade twine ([`9722313`](https://github.com/python-semantic-release/python-semantic-release/commit/9722313eb63c7e2c32c084ad31bed7ee1c48a928))

### Unknown

* 3.11.2 ([`762fbcf`](https://github.com/python-semantic-release/python-semantic-release/commit/762fbcfb72f3ed269eaa1bbb8b0de433166a0a47))


## v3.11.1 (2018-06-06)

### Chore

* chore: Divide circle ci into different jobs for better feedback on prs ([`11f7c8a`](https://github.com/python-semantic-release/python-semantic-release/commit/11f7c8a8d671e1e9d48c39c8876eee750e0406ec))

### Documentation

* docs: Add retry option to cli docs ([`021da50`](https://github.com/python-semantic-release/python-semantic-release/commit/021da5001934f3199c98d7cf29f62a3ad8c2e56a))

### Fix

* fix: change Gitpython version number

Change the Gitpython version number to fix a bug described in #80. ([`23c9d4b`](https://github.com/python-semantic-release/python-semantic-release/commit/23c9d4b6a1716e65605ed985881452898d5cf644))

### Unknown

* 3.11.1 ([`ddb3353`](https://github.com/python-semantic-release/python-semantic-release/commit/ddb3353876601b5bb39563a8fbcced63e9769c8d))


## v3.11.0 (2018-04-12)

### Chore

* chore: Replace travis and frigg with circleci ([`c53d11e`](https://github.com/python-semantic-release/python-semantic-release/commit/c53d11eaf897b5bbcf938bf32650f2a1ea227259))

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

### Style

* style: Fix flake8 ([`c9686a2`](https://github.com/python-semantic-release/python-semantic-release/commit/c9686a2edafbb23dbf0955f124d5d0b431bd4786))

* style: Fix flake8 ([`d9239ea`](https://github.com/python-semantic-release/python-semantic-release/commit/d9239ea32ffbce37e7c3b852a46660ea6aed75b9))

* style: Fix flake8 ([`a40f56f`](https://github.com/python-semantic-release/python-semantic-release/commit/a40f56f7774382a100f27aa824aef5a0ae796c9a))

* style: Fix isort warnings ([`5411c8d`](https://github.com/python-semantic-release/python-semantic-release/commit/5411c8d8b31229941fd32b0ffee937f4d36ff367))

### Test

* test: Fix broken tests and add a test after 3e312c0 ([`c3e0339`](https://github.com/python-semantic-release/python-semantic-release/commit/c3e0339c5d3d7ca05fef6714a91f1f321220785b))

### Unknown

* 3.11.0 ([`54e003c`](https://github.com/python-semantic-release/python-semantic-release/commit/54e003c8e9c358427067326a2507a279474761b7))


## v3.10.3 (2018-01-29)

### Fix

* fix: error when not in git repository (#75)

Fix an error when the program was run in a non-git repository. It would
not allow the help options to be run.

issue #74 ([`251b190`](https://github.com/python-semantic-release/python-semantic-release/commit/251b190a2fd5df68892346926d447cbc1b32475a))

### Unknown

* 3.10.3 ([`c15e0de`](https://github.com/python-semantic-release/python-semantic-release/commit/c15e0debb4dcdc7f15aa1ff6e1f23a99c83579a6))


## v3.10.2 (2017-08-03)

### Fix

* fix: update call to upload to work with twine 1.9.1 (#72) ([`8f47643`](https://github.com/python-semantic-release/python-semantic-release/commit/8f47643c54996e06c358537115e7e17b77cb02ca))

### Unknown

* 3.10.2 ([`0907db4`](https://github.com/python-semantic-release/python-semantic-release/commit/0907db4044e20895d1b9c4f9fb1de33a5d79c06e))


## v3.10.1 (2017-07-22)

### Chore

* chore: Fix config in travis ([`57e969f`](https://github.com/python-semantic-release/python-semantic-release/commit/57e969f8d937cc2335588f538bd8bc4aa522852a))

### Fix

* fix: Update Twine (#69)

The publishing API is under development and older versions of Twine have problems to deal with newer versions of the API. Namely the logic of register/upload has changed (it was simplified). ([`9f268c3`](https://github.com/python-semantic-release/python-semantic-release/commit/9f268c373a932621771abbe9607b739b1e331409))

### Unknown

* 3.10.1 ([`500972c`](https://github.com/python-semantic-release/python-semantic-release/commit/500972c0f9c0393a02bdfd8afea628772a0611c1))

* revert: &#34;chore: Remove travis&#34;

This reverts commit 93e5507da6d53ecf63405507390633ef480c52fb. ([`195ed8d`](https://github.com/python-semantic-release/python-semantic-release/commit/195ed8ddc004b736cd4e0301e5d7c7f6394cf4a5))


## v3.10.0 (2017-05-05)

### Chore

* chore: Remove a print statement ([`fe908d4`](https://github.com/python-semantic-release/python-semantic-release/commit/fe908d45048aecc4d4b94c7c8cb821bc941fe70c))

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

### Test

* test: Make the tests green again ([`874307b`](https://github.com/python-semantic-release/python-semantic-release/commit/874307b5deb6c5a3fcb1212ab54dd81f49f8459e))

### Unknown

* 3.10.0 ([`7cfe01d`](https://github.com/python-semantic-release/python-semantic-release/commit/7cfe01d9dd35b74892d64238c4aa0d50b845b113))


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

### Refactor

* refactor: simplify code with clearer logic

add version_source to default.cfg to remove all get_option calls
remove some duplicate codes ([`4f11a86`](https://github.com/python-semantic-release/python-semantic-release/commit/4f11a86b3b4b0d7a58cee83898d7568acecb5f94))

### Style

* style: flake8 check ([`20422b4`](https://github.com/python-semantic-release/python-semantic-release/commit/20422b4f1192c52c6706a4a7ddbc895e3e9208c8))

### Test

* test: correct tests for tag version ([`1230fe9`](https://github.com/python-semantic-release/python-semantic-release/commit/1230fe9add99bce2323f40e955d880fbb3f60216))

* test: change repo owner for online CI ([`2107813`](https://github.com/python-semantic-release/python-semantic-release/commit/210781354458a9a952044dfadaf0f3e839109e29))

### Unknown

* 3.9.0 ([`52bf48b`](https://github.com/python-semantic-release/python-semantic-release/commit/52bf48b93be7d8feeef5207f0dc9f7ddbd583da4))

* Merge pull request #54 from KenMercusLai/master

add option to use tag instead of creating new commit when versioning ([`8e9c021`](https://github.com/python-semantic-release/python-semantic-release/commit/8e9c021cdf6bf8ed3d7cc7dc9c42187e893f23bf))


## v3.8.1 (2016-04-17)

### Chore

* chore: Grammar fix (#61) ([`1f424c8`](https://github.com/python-semantic-release/python-semantic-release/commit/1f424c8ad48d6c1054cf3d93712d408a2e8bef3d))

### Fix

* fix: Add search_parent_directories option to gitpython (#62) ([`8bf9ce1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bf9ce11137399906f18bc8b25698b6e03a65034))

### Unknown

* 3.8.1 ([`378e2eb`](https://github.com/python-semantic-release/python-semantic-release/commit/378e2eb6d228cc8b6e5c57e78cae3fe801fc974b))


## v3.8.0 (2016-03-21)

### Chore

* chore: Change pull in after_success to git fetch --unshallow

This will retrieve the whole git history before trying to make a
release. ([`6f3b9d8`](https://github.com/python-semantic-release/python-semantic-release/commit/6f3b9d897bfc67137beb0b104e572ef5ac1b3756))

* chore: Pull master in after success ([`325d216`](https://github.com/python-semantic-release/python-semantic-release/commit/325d216c8a25c38e080181a37a9ada17ece7d857))

* chore: Run correct tox environments on frigg ([`0d4bdad`](https://github.com/python-semantic-release/python-semantic-release/commit/0d4bdad0348a01e8eb868fcfdeb9750cad03a20b))

* chore: Fix indentation in frigg settings ([`f9cecc5`](https://github.com/python-semantic-release/python-semantic-release/commit/f9cecc56fc034c554670aa238de4d36aeb4d3882))

* chore: Add release in after success in frigg settings ([`7bb4d7e`](https://github.com/python-semantic-release/python-semantic-release/commit/7bb4d7e1f317d0ddef28e9c8ca42452ae20d8af9))

* chore: Remove travis ([`93e5507`](https://github.com/python-semantic-release/python-semantic-release/commit/93e5507da6d53ecf63405507390633ef480c52fb))

* chore: Move coverage to tox ([`9865e9c`](https://github.com/python-semantic-release/python-semantic-release/commit/9865e9c2aaa1519beed71c301865e8e117face64))

* chore: Add tox and sphinx as dev dependencies ([`0237fcd`](https://github.com/python-semantic-release/python-semantic-release/commit/0237fcdc883be32d4e96ca3d4b32e89c8612220c))

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

### Test

* test: Add tests for circle ci checks ([`fa1223c`](https://github.com/python-semantic-release/python-semantic-release/commit/fa1223c661d60033b7d7aba2a27151d6ee18a299))

* test: Mock to fix cli tests ([`24e5f7a`](https://github.com/python-semantic-release/python-semantic-release/commit/24e5f7a85bea75101b60baeeb36d6915464830c1))

* test: Make sure all publish tests mocks checkout

If not the tests will checkout master ([`742b2e9`](https://github.com/python-semantic-release/python-semantic-release/commit/742b2e9e082c15f22052d64dea66f2d997d3d69b))

* test: Restructure ci checks tests ([`f36eb2e`](https://github.com/python-semantic-release/python-semantic-release/commit/f36eb2ede0d6c4cb09861e5497629929c0ce4749))

### Unknown

* 3.8.0 ([`8779773`](https://github.com/python-semantic-release/python-semantic-release/commit/8779773444f54a8090b9d341b644f68a70ddb785))

* Merge pull request #57 from relekang/feat/add-circle-ci-checks

Add circle ci checks ([`7af9816`](https://github.com/python-semantic-release/python-semantic-release/commit/7af9816610669a9c697bfe198e98da33e5ed0a29))

* Merge pull request #58 from relekang/refactor-cli-py

fix: Refactoring cli.py to improve --help and error messages ([`a0bf0ff`](https://github.com/python-semantic-release/python-semantic-release/commit/a0bf0ff0eb0cd0140f851b9f7b7e18c2710dbad5))

* Merge pull request #60 from relekang/test/fix-cli-tests

test: Mock to fix cli tests ([`d6df71d`](https://github.com/python-semantic-release/python-semantic-release/commit/d6df71d6fb990c84bf5e01d45d5b0cab399da4d8))

* Merge pull request #59 from relekang/test/fix-structure

fix: Make tag parser work correctly with breaking changes ([`1e9a581`](https://github.com/python-semantic-release/python-semantic-release/commit/1e9a581e89757fb603a340bbc519e07b59b143e9))

* Merge pull request #56 from relekang/dev-deps

chore: Add tox and sphinx as dev dependencies ([`3beb444`](https://github.com/python-semantic-release/python-semantic-release/commit/3beb444ba34da785a2c3bcf2359e561c9be7abdd))


## v3.7.2 (2016-03-19)

### Fix

* fix: move code around a bit to make flake8 happy ([`41463b4`](https://github.com/python-semantic-release/python-semantic-release/commit/41463b49b5d44fd94c11ab6e0a81e199510fabec))

### Unknown

* 3.7.2 ([`dde8bbf`](https://github.com/python-semantic-release/python-semantic-release/commit/dde8bbfd71d048d05a92d87bae0c6e45056b52e2))

* Merge pull request #55 from relekang/flake8-fixes

fix: move code around a bit to make flake8 happy ([`2184549`](https://github.com/python-semantic-release/python-semantic-release/commit/218454986be540b90e7d3af45a76c02d3c5f6ee2))


## v3.7.1 (2016-03-15)

### Documentation

* docs(configuration): Fix typo in setup.cfg section ([`725d87d`](https://github.com/python-semantic-release/python-semantic-release/commit/725d87dc45857ef2f9fb331222845ac83a3af135))

### Unknown

* 3.7.1 ([`0aaa112`](https://github.com/python-semantic-release/python-semantic-release/commit/0aaa112880559e968f8c0053cfb84cf7eaed64cf))

* Merge pull request #50 from edwelker/doc_fix

documentation typo ([`b3c52c2`](https://github.com/python-semantic-release/python-semantic-release/commit/b3c52c27293f8944ea34a6a42b348082e80275fe))

* documentation typo ([`b77d484`](https://github.com/python-semantic-release/python-semantic-release/commit/b77d484e119daa0c2fe86bc558eda972d4852a83))


## v3.7.0 (2016-01-10)

### Feature

* feat: Add ci_checks for Frigg CI ([`577c374`](https://github.com/python-semantic-release/python-semantic-release/commit/577c374396fe303b6fe7d64630d2959998d3595c))

### Unknown

* 3.7.0 ([`10825b5`](https://github.com/python-semantic-release/python-semantic-release/commit/10825b5fe633f7cc2ea618ac3402be36fc10e8ee))


## v3.6.1 (2016-01-10)

### Fix

* fix: Add requests as dependency ([`4525a70`](https://github.com/python-semantic-release/python-semantic-release/commit/4525a70d5520b44720d385b0307e46fae77a7463))

### Unknown

* 3.6.1 ([`8f5dd02`](https://github.com/python-semantic-release/python-semantic-release/commit/8f5dd025577c8d66c2d762070bfebbe31c77ab00))


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

### Unknown

* 3.6.0 ([`4916f16`](https://github.com/python-semantic-release/python-semantic-release/commit/4916f16c0a6602fafd52222f3c930ceebade686a))


## v3.5.0 (2015-12-22)

### Chore

* chore: Re-add git user config to travis config ([`2c2809e`](https://github.com/python-semantic-release/python-semantic-release/commit/2c2809ea360977c1e4010c84ac2d43ef94dc6154))

* chore: Remove unecessary git commands from travis after_success ([`a863b62`](https://github.com/python-semantic-release/python-semantic-release/commit/a863b620012b4528f1a5edcea3f8a428a2c690d5))

### Documentation

* docs: Convert readme to rst ([`e8a8d26`](https://github.com/python-semantic-release/python-semantic-release/commit/e8a8d265aa2147824f18065b39a8e7821acb90ec))

### Feature

* feat: Checkout master before publishing

Related to #39 ([`dc4077a`](https://github.com/python-semantic-release/python-semantic-release/commit/dc4077a2d07e0522b625336dcf83ee4e0e1640aa))

* feat: Add author in commit

Fixes #40 ([`020efaa`](https://github.com/python-semantic-release/python-semantic-release/commit/020efaaadf588e3fccd9d2f08a273c37e4158421))

### Fix

* fix: Remove &#34; from git push command ([`031318b`](https://github.com/python-semantic-release/python-semantic-release/commit/031318b3268bc37e6847ec049b37425650cebec8))

### Refactor

* refactor: Use gitpython instead of invoke in vcs_helpers

Fixes #3 ([`0d9b9a7`](https://github.com/python-semantic-release/python-semantic-release/commit/0d9b9a76f8292889dc7fbb802988073ffbe59a4e))

### Unknown

* 3.5.0 ([`fb67b5f`](https://github.com/python-semantic-release/python-semantic-release/commit/fb67b5ffb2df7d11b1daf6d7eef46f843f5cfd62))


## v3.4.0 (2015-12-22)

### Chore

* chore: Convert cli tests to pytest ([`40da8bb`](https://github.com/python-semantic-release/python-semantic-release/commit/40da8bb2bd96c06c044da2abc77d8f57f9a11347))

* chore: Add checkout master to travis after_success ([`b79310a`](https://github.com/python-semantic-release/python-semantic-release/commit/b79310aa2f532680b33d30271aeb04dfd906019a))

### Feature

* feat: Add travis environment checks

These checks will ensure that semantic release only runs against master
and not in a pull-request. ([`f386db7`](https://github.com/python-semantic-release/python-semantic-release/commit/f386db75b77acd521d2f5bde2e1dde99924dc096))

### Unknown

* 3.4.0 ([`397ba66`](https://github.com/python-semantic-release/python-semantic-release/commit/397ba668f4bbb1f6a0385390ce1f4e4efbf98dbf))


## v3.3.3 (2015-12-22)

### Fix

* fix: Do git push and git push --tags instead of --follow-tags ([`8bc70a1`](https://github.com/python-semantic-release/python-semantic-release/commit/8bc70a183fd72f595c72702382bc0b7c3abe99c8))

### Unknown

* 3.3.3 ([`d1664bb`](https://github.com/python-semantic-release/python-semantic-release/commit/d1664bbaa83ea60c15c5652f7dfe2084e458d48d))

* 3.3.2 ([`68510b6`](https://github.com/python-semantic-release/python-semantic-release/commit/68510b6f27923d407087db07c56deb2f2f404fe4))


## v3.3.2 (2015-12-21)

### Documentation

* docs: Update docstrings for generate_changelog ([`987c6a9`](https://github.com/python-semantic-release/python-semantic-release/commit/987c6a96d15997e38c93a9d841c618c76a385ce7))

### Fix

* fix: Change build badge ([`0dc068f`](https://github.com/python-semantic-release/python-semantic-release/commit/0dc068fff2f8c6914f4abe6c4e5fb2752669159e))


## v3.3.1 (2015-12-21)

### Chore

* chore: Use python 2 travis env ([`22c8d67`](https://github.com/python-semantic-release/python-semantic-release/commit/22c8d678358ea8d1808a9c058861d4055d13e0fd))

* chore: Fix version number ([`7041a4c`](https://github.com/python-semantic-release/python-semantic-release/commit/7041a4c40b7dec5ea201a051e2e4ec572f93e358))

### Fix

* fix: Only list commits from the last version tag

Fixes #28 ([`191369e`](https://github.com/python-semantic-release/python-semantic-release/commit/191369ebd68526e5b1afcf563f7d13e18c8ca8bf))

* fix: Add pandoc to travis settings ([`17d40a7`](https://github.com/python-semantic-release/python-semantic-release/commit/17d40a73062ffa774542d0abc0f59fc16b68be37))

### Refactor

* refactor: Fix quantified code warnings ([`6d16953`](https://github.com/python-semantic-release/python-semantic-release/commit/6d1695320e09320f43efca403992d7d1791ff2a7))

### Unknown

* 3.3.1 ([`0334b81`](https://github.com/python-semantic-release/python-semantic-release/commit/0334b81c247be5bf222975d894f5ced9d38fb812))

* Merge remote-tracking branch &#39;origin/depsy/click-equals-6.2&#39; ([`f0f7937`](https://github.com/python-semantic-release/python-semantic-release/commit/f0f7937cca61c53b25e1e39b78356345e73b2033))


## v3.3.0 (2015-12-20)

### Chore

* chore: Fix pep8 warnings ([`07977b5`](https://github.com/python-semantic-release/python-semantic-release/commit/07977b5db86cd0a36172f11dbd035bde9348618b))

* chore: Use semantic-release for publishing ([`e5b6119`](https://github.com/python-semantic-release/python-semantic-release/commit/e5b6119b76007345a8fe8e60d18c4c0587b437b7))

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

### Chore

* chore: Update travis pypi password ([`7437c80`](https://github.com/python-semantic-release/python-semantic-release/commit/7437c809f8599714e143155b66858a47857b98d7))

### Fix

* fix: Add requirements to manifest ([`ed25ecb`](https://github.com/python-semantic-release/python-semantic-release/commit/ed25ecbaeec0e20ad3040452a5547bb7d6faf6ad))

* fix(pypi): Add sdist as default in addition to bdist_wheel

There are a lot of outdated pip installations around which leads to
confusions if a package have had an sdist release at some point and
then suddenly is only available as wheel packages, because old pip
clients will then download the latest sdist package available. ([`a1a35f4`](https://github.com/python-semantic-release/python-semantic-release/commit/a1a35f43175187091f028474db2ebef5bfc77bc0))

### Unknown

* 3.2.1 ([`ab83167`](https://github.com/python-semantic-release/python-semantic-release/commit/ab83167d630bde385622178147037856641e2118))


## v3.2.0 (2015-12-20)

### Chore

* chore: Fix command in travis file ([`edb12d1`](https://github.com/python-semantic-release/python-semantic-release/commit/edb12d1d7d1c6c0539f28b6d5e9581ea8af105cb))

* chore: Add git config to travis setup ([`7cc1510`](https://github.com/python-semantic-release/python-semantic-release/commit/7cc15107ceca1aa1ef25d5ae06e6119c6d9ee4c3))

* chore: Make travis have one environment ([`ec2a003`](https://github.com/python-semantic-release/python-semantic-release/commit/ec2a003230040303e768db1c03e87770bc701e52))

* chore: Setup travis ([`f283875`](https://github.com/python-semantic-release/python-semantic-release/commit/f2838755163dad9ab5766e6bbf494daf37667cec))

### Feature

* feat(git): Add push to GH_TOKEN@github-url ([`546b5bf`](https://github.com/python-semantic-release/python-semantic-release/commit/546b5bf15466c6f5dfe93c1c03ca34604b0326f2))

* feat(angular-parser): Remove scope requirement ([`90c9d8d`](https://github.com/python-semantic-release/python-semantic-release/commit/90c9d8d4cd6d43be094cda86579e00b507571f98))

### Fix

* fix(deps): Use one file for requirements ([`4868543`](https://github.com/python-semantic-release/python-semantic-release/commit/486854393b24803bb2356324e045ccab17510d46))

### Test

* test: Update test setup ([`ac1e686`](https://github.com/python-semantic-release/python-semantic-release/commit/ac1e6862d8990bb35250478d38af170ccedc81eb))

### Unknown

* 3.2.0 ([`bf85122`](https://github.com/python-semantic-release/python-semantic-release/commit/bf85122335173076fa6c018a506a546fa16b0aa6))

* Merge pull request #29 from relekang/depsy-decisive-upgrade-15_10_17_07_51_03

[Depsy] Upgrade dependencies ([`4987a31`](https://github.com/python-semantic-release/python-semantic-release/commit/4987a31ae78e8fc202497a01591ba0881e82437e))

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

### Chore

* chore(imports): Make all imports relative ([`d6ce17b`](https://github.com/python-semantic-release/python-semantic-release/commit/d6ce17b85a6d18a526a9a68e7ec51e7f635ca15b))

### Feature

* feat(pypi): Add option to disable pypi upload ([`f5cd079`](https://github.com/python-semantic-release/python-semantic-release/commit/f5cd079edb219de5ad03a71448d578f5f477da9c))

### Unknown

* 3.1.0 ([`93cb147`](https://github.com/python-semantic-release/python-semantic-release/commit/93cb147ca0d360cd5c51b642f8d7ce2abb576698))


## v3.0.0 (2015-08-25)

### Chore

* chore(pytest): Use assert in pytest-test ([`d8d1f9d`](https://github.com/python-semantic-release/python-semantic-release/commit/d8d1f9d5ace0db71cf256e809ebf44ff090d9237))

* chore(setup.py): Remove uneded variable ([`e54774c`](https://github.com/python-semantic-release/python-semantic-release/commit/e54774c897245b4da2f1e407d9ac848e6f712ef9))

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

### Unknown

* 3.0.0 ([`592fedb`](https://github.com/python-semantic-release/python-semantic-release/commit/592fedb52633de40e0b07b418acc6c9d796179a4))

* Merge branch &#39;tag-parser&#39; ([`2519b42`](https://github.com/python-semantic-release/python-semantic-release/commit/2519b42c7381fe8217b34150bd1ad06b23c9a56d))


## v2.1.4 (2015-08-23)

### Fix

* fix(github): Fix property calls

Properties can only be used from instances. ([`7ecdeb2`](https://github.com/python-semantic-release/python-semantic-release/commit/7ecdeb22de96b6b55c5404ebf54a751911c4d8cd))

### Refactor

* refactor(parsers): Move the parsing of the parts after line one to helpers ([`cefc8c6`](https://github.com/python-semantic-release/python-semantic-release/commit/cefc8c68ed1d454010a5d81e752ec7b0b1761ebb))

### Unknown

* 2.1.4 ([`a05210f`](https://github.com/python-semantic-release/python-semantic-release/commit/a05210f4274f10ddd5385241c99b6d77996c9544))


## v2.1.3 (2015-08-22)

### Chore

* chore(qc): Fix warnings from quantifiedcode ([`73c5da2`](https://github.com/python-semantic-release/python-semantic-release/commit/73c5da25810e89c66777664a64c0a34b7ddbffb0))

* chore(test): Use mock package instead of unittest.mock ([`5376a56`](https://github.com/python-semantic-release/python-semantic-release/commit/5376a5602889fdae542eb7b13ae529ee001ad0aa))

### Documentation

* docs(readme): Update readme with information about the changelog command ([`56a745e`](https://github.com/python-semantic-release/python-semantic-release/commit/56a745ef6fa4edf6f6ba09c78fcc141102cf2871))

* docs(parsers): Add documentation about commit parsers ([`9b55422`](https://github.com/python-semantic-release/python-semantic-release/commit/9b554222768036024a133153a559cdfc017c1d91))

* docs(api): Update apidocs ([`6185380`](https://github.com/python-semantic-release/python-semantic-release/commit/6185380babedbbeab2a2a342f17b4ff3d4df6768))

### Fix

* fix(hvcs): Make Github.token an property ([`37d5e31`](https://github.com/python-semantic-release/python-semantic-release/commit/37d5e3110397596a036def5f1dccf0860964332c))

### Unknown

* 2.1.3 ([`4979071`](https://github.com/python-semantic-release/python-semantic-release/commit/4979071d9330f2f3648358000de3a642a385a828))


## v2.1.2 (2015-08-20)

### Fix

* fix(cli): Fix call to generate_changelog in publish ([`5f8bce4`](https://github.com/python-semantic-release/python-semantic-release/commit/5f8bce4cbb5e1729e674efd6c651e2531aea2a16))

### Unknown

* 2.1.2 ([`dfb37cb`](https://github.com/python-semantic-release/python-semantic-release/commit/dfb37cbde0a877ca482095711cbb08f52ab3cf45))


## v2.1.1 (2015-08-20)

### Fix

* fix(history): Fix issue in get_previous_version ([`f961786`](https://github.com/python-semantic-release/python-semantic-release/commit/f961786aa3eaa3a620f47cc09243340fd329b9c2))

### Unknown

* 2.1.1 ([`7cf3a7d`](https://github.com/python-semantic-release/python-semantic-release/commit/7cf3a7d9aa2adc5a3cebf9d1151b113388117312))


## v2.1.0 (2015-08-19)

### Chore

* chore(pep8): Fix pep8 warning ([`5108b17`](https://github.com/python-semantic-release/python-semantic-release/commit/5108b177ed2b50b50e3476997f9d1f73adaa3f95))

### Feature

* feat(cli): Add the possibility to repost the changelog ([`4d028e2`](https://github.com/python-semantic-release/python-semantic-release/commit/4d028e21b9da01be8caac8f23f2c11e0c087e485))

### Fix

* fix(cli): Fix check of token in changelog command ([`cc6e6ab`](https://github.com/python-semantic-release/python-semantic-release/commit/cc6e6abe1e91d3aa24e8d73e704829669bea5fd7))

* fix(github): Fix the github releases integration ([`f0c3c1d`](https://github.com/python-semantic-release/python-semantic-release/commit/f0c3c1db97752b71f2153ae9f623501b0b8e2c98))

* fix(history): Fix changelog generation

This enables regeneration of a given versions changelog. ([`f010272`](https://github.com/python-semantic-release/python-semantic-release/commit/f01027203a8ca69d21b4aff689e60e8c8d6f9af5))

### Test

* test(github): Fix broken tests ([`a140ecd`](https://github.com/python-semantic-release/python-semantic-release/commit/a140ecdc81c8e639b8d9adbedc7ac850c17f09cc))

### Unknown

* 2.1.0 ([`4b78940`](https://github.com/python-semantic-release/python-semantic-release/commit/4b789409936a5997d6c2f277083930b6e4b3b643))


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

### Refactor

* refactor(test): Move exit code assertion in cli tests ([`345c299`](https://github.com/python-semantic-release/python-semantic-release/commit/345c299cbf4c0e626eb482b2f577dc8c5fd9426a))

* refactor(history): Move evaluate_version_bump ([`c448d9b`](https://github.com/python-semantic-release/python-semantic-release/commit/c448d9b056d48d607a8bf7d38b8cf8a8ba038ca6))

### Style

* style(pep8): Fix pep8 and isort warnings ([`87695b1`](https://github.com/python-semantic-release/python-semantic-release/commit/87695b1684ad55e26e1489ab9d835cf8a9854654))

### Unknown

* 2.0.0 ([`6493a58`](https://github.com/python-semantic-release/python-semantic-release/commit/6493a58727ecd082e3ae12619fef6c3c982cc6e2))

* Add badges in readme ([`ad7c9c6`](https://github.com/python-semantic-release/python-semantic-release/commit/ad7c9c69329efe8af42112f716c39e810ed22718))

* Add cumulative coverage ([`15c5ea0`](https://github.com/python-semantic-release/python-semantic-release/commit/15c5ea0106ed08ef8d896d100cf1987c0b5fc17a))

* Update api-docs ([`4654655`](https://github.com/python-semantic-release/python-semantic-release/commit/4654655c33afc7cead9c238a14e4b71cc7121aa5))

* Fix #19, add config documentation ([`354b2ca`](https://github.com/python-semantic-release/python-semantic-release/commit/354b2cabfc7e4a8d2c95ebd2801cc4dbca67fa5a))


## v1.0.0 (2015-08-04)

### Unknown

* 1.0.0 ([`a91662c`](https://github.com/python-semantic-release/python-semantic-release/commit/a91662c55d01af096cc45bf8844bcc6d87c1bcee))

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

* 0.9.1 ([`240971f`](https://github.com/python-semantic-release/python-semantic-release/commit/240971f4de808be27a5d8c54bd40156d80d38913))

* :bug: Fix get_current_head_hash, ensure it only returns the hash ([`7c28832`](https://github.com/python-semantic-release/python-semantic-release/commit/7c2883209e5bf4a568de60dbdbfc3741d34f38b4))


## v0.9.0 (2015-08-03)

### Unknown

* 0.9.0 ([`85bfaae`](https://github.com/python-semantic-release/python-semantic-release/commit/85bfaaec2236e6c144bfb31ea12240ed6150c28b))

* Merge pull request #15 from jezdez/python-2

Add Python 2.7 support. Fix #10.
:sparkles: ([`5daabb7`](https://github.com/python-semantic-release/python-semantic-release/commit/5daabb75eb9145566a2a7c2a9e64439df7cd85f1))

* Add Python 2.7 support. Fix #10. ([`c05e13f`](https://github.com/python-semantic-release/python-semantic-release/commit/c05e13f22163237e963c493ffeda7e140f0202c6))

* Merge pull request #14 from jezdez/assertion-fix

Fixed name of assertion function. ([`aeb62df`](https://github.com/python-semantic-release/python-semantic-release/commit/aeb62dfcb6aa123f47f612dc209415c7fb4fe889))

* Fixed cli tests to use correct params for call assertion. ([`456b26b`](https://github.com/python-semantic-release/python-semantic-release/commit/456b26be7130e51a7a46310f65dffb615b30a097))

* Fixed name of assertion function. ([`9b16098`](https://github.com/python-semantic-release/python-semantic-release/commit/9b1609813ae71d5605b8ec9754d737ba38465537))


## v0.8.0 (2015-08-03)

### Unknown

* 0.8.0 ([`6ec8a3e`](https://github.com/python-semantic-release/python-semantic-release/commit/6ec8a3e22f0914dd0d995c809f5b5d078825bc9a))

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

* 0.7.0 ([`aeb11f7`](https://github.com/python-semantic-release/python-semantic-release/commit/aeb11f74a93fe7e64e9507f9a62202b833ee5733))

* :sparkles: Add patch_without_tag option, fixes #6 ([`3734a88`](https://github.com/python-semantic-release/python-semantic-release/commit/3734a889f753f1b9023876e100031be6475a90d1))

* Move defaults to cfg file ([`cb1257a`](https://github.com/python-semantic-release/python-semantic-release/commit/cb1257a60a81cb5aadbc8f6470ec2ec2c904506c))

* Add contributing.rst ([`a27e282`](https://github.com/python-semantic-release/python-semantic-release/commit/a27e28223b8186bda66cc882454746a5595d8643))

* Fix docstring in setup_hook() ([`1e47f1c`](https://github.com/python-semantic-release/python-semantic-release/commit/1e47f1c6c68b5a74515f2f86275e3c749c999e1c))

* Fix #1, Add basic setup of sphinx based docs ([`41fba78`](https://github.com/python-semantic-release/python-semantic-release/commit/41fba78a389a8d841316946757a23a7570763c39))

* Add docstrings to all functions ([`6555d5a`](https://github.com/python-semantic-release/python-semantic-release/commit/6555d5a5944fa4b7823f70fd720e193915186307))


## v0.6.0 (2015-08-02)

### Unknown

* 0.6.0 ([`3acd8db`](https://github.com/python-semantic-release/python-semantic-release/commit/3acd8dbdd25f3973a536924985a37726d8665cdd))

* :sparkles: Fix #13, Add twine for uploads to pypi ([`eec2561`](https://github.com/python-semantic-release/python-semantic-release/commit/eec256115b28b0a18136a26d74cfc3232502f1a6))

* Add tests for the setup.py hook ([`ecd9e9a`](https://github.com/python-semantic-release/python-semantic-release/commit/ecd9e9a3f97bdf9489b6dc750d736855a2c109c2))

* Add test for git helpers ([`8354cfd`](https://github.com/python-semantic-release/python-semantic-release/commit/8354cfd953bb09723abcff7fefe620fc4aa6b855))

* Fix typo ([`9585217`](https://github.com/python-semantic-release/python-semantic-release/commit/9585217d95a4bb2447ae8860971575bd4c847070))

* Add link to blogpost in readme ([`1966e52`](https://github.com/python-semantic-release/python-semantic-release/commit/1966e52ab4f08d3cbabe88881c0e51e600e44567))


## v0.5.4 (2015-07-29)

### Unknown

* 0.5.4 ([`b66939b`](https://github.com/python-semantic-release/python-semantic-release/commit/b66939bff790c21bd1093e9b8ae6a5dff5f38235))

* Add tests for upload_to_pypi ([`778923f`](https://github.com/python-semantic-release/python-semantic-release/commit/778923fab86d423b6ed254c569fddee1b9650f56))

* :bug: Add python2 not supported warning

Related: #9, #10 ([`e84c4d8`](https://github.com/python-semantic-release/python-semantic-release/commit/e84c4d8b6f212aec174baccd188185627b5039b6))

* Add note about python 3 only

related to #9 ([`a71b536`](https://github.com/python-semantic-release/python-semantic-release/commit/a71b53609db75316e3c14df0ece7f474393641bc))


## v0.5.3 (2015-07-28)

### Unknown

* 0.5.3 ([`bed6e58`](https://github.com/python-semantic-release/python-semantic-release/commit/bed6e583161fd7651c69660ef9c6ab3252907cb9))

* Add wheel as a dependency ([`971e479`](https://github.com/python-semantic-release/python-semantic-release/commit/971e4795a8b8fea371fcc02dc9221f58a0559f32))


## v0.5.2 (2015-07-28)

### Unknown

* 0.5.2 ([`f66a1f9`](https://github.com/python-semantic-release/python-semantic-release/commit/f66a1f92072d9927c35ac4ac54153bd9b5a8b3a0))

* :bug: Fix python wheel tag ([`f9ac163`](https://github.com/python-semantic-release/python-semantic-release/commit/f9ac163491666022c809ad49846f3c61966e10c1))


## v0.5.1 (2015-07-28)

### Unknown

* 0.5.1 ([`6a2311a`](https://github.com/python-semantic-release/python-semantic-release/commit/6a2311adb7c4745908c0fa0ea4e5759b0e46d2b6))

* :bug: Fix push commands ([`8374ef6`](https://github.com/python-semantic-release/python-semantic-release/commit/8374ef6bd78eb564a6d846b882c99a67e116394e))


## v0.5.0 (2015-07-28)

### Unknown

* 0.5.0 ([`e888160`](https://github.com/python-semantic-release/python-semantic-release/commit/e8881604c94808d0e86387cc18ee81885870e1e7))

* :sparkles: Add setup.py hook for the cli interface ([`c363bc5`](https://github.com/python-semantic-release/python-semantic-release/commit/c363bc5d3cb9e9a113de3cd0c49dd54a5ea9cf35))


## v0.4.0 (2015-07-28)

### Unknown

* 0.4.0 ([`bfb1434`](https://github.com/python-semantic-release/python-semantic-release/commit/bfb1434f1861fe99dd28b653467034db1e271dfb))

* :sparkles: Add publish command ([`d8116c9`](https://github.com/python-semantic-release/python-semantic-release/commit/d8116c9dec472d0007973939363388d598697784))


## v0.3.2 (2015-07-28)

### Unknown

* 0.3.2 ([`1d3ee00`](https://github.com/python-semantic-release/python-semantic-release/commit/1d3ee00c3601f06f900bc1694f3c7c32106a6e14))


## v0.3.1 (2015-07-27)

### Unknown

* 0.3.1 ([`fec284c`](https://github.com/python-semantic-release/python-semantic-release/commit/fec284cdec7516b7b8067d5de2738e62434d3f31))

* :bug: Fix wheel settings ([`1e860e8`](https://github.com/python-semantic-release/python-semantic-release/commit/1e860e8a4d9ec580449a0b87be9660a9482fa2a4))


## v0.3.0 (2015-07-27)

### Unknown

* 0.3.0 ([`d633a28`](https://github.com/python-semantic-release/python-semantic-release/commit/d633a2811f2e14581793ebdf08b852dc6024dd44))

* Add info about tagging in readme ([`914c78f`](https://github.com/python-semantic-release/python-semantic-release/commit/914c78f0e1e15043c080e6d1ee56eccb5a70dd7d))

* :sparkles: Add support for tagging releases ([`5f4736f`](https://github.com/python-semantic-release/python-semantic-release/commit/5f4736f4e41bc96d36caa76ca58be0e1e7931069))

* :bug: Fix issue with committing the same version # ([`441798a`](https://github.com/python-semantic-release/python-semantic-release/commit/441798a223195138c0d3d2c51fc916137fef9a6c))

* Remove patch as default for untagged history ([`e44e2a1`](https://github.com/python-semantic-release/python-semantic-release/commit/e44e2a166033b75f75351825f7e4e0866bb7c45b))

* Restructure and add tests ([`4546e1e`](https://github.com/python-semantic-release/python-semantic-release/commit/4546e1e11429026c1a5410e17f8c5f866cfe5833))


## v0.2.0 (2015-07-27)

### Unknown

* 0.2.0 ([`c3bad90`](https://github.com/python-semantic-release/python-semantic-release/commit/c3bad90b53cc3312795da18881e6405d9cb8cdfc))

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

* 0.1.1 ([`54a98fe`](https://github.com/python-semantic-release/python-semantic-release/commit/54a98fedbf5f8a3898d0d9c27bca20e9b8a382e5))

* Fix libgit install in frigg settings ([`bd991c3`](https://github.com/python-semantic-release/python-semantic-release/commit/bd991c3b3e1f69f86b1f6ca538e57b3ba365e376))

* :bug: Fix entry point ([`bd7ce7f`](https://github.com/python-semantic-release/python-semantic-release/commit/bd7ce7f47c49e2027767fb770024a0d4033299fa))

* Fix badges ([`1e5df79`](https://github.com/python-semantic-release/python-semantic-release/commit/1e5df79aa104768078e6e66d559ab88b751cc0a3))

* Add libgit2 to frigg settings ([`d55f25c`](https://github.com/python-semantic-release/python-semantic-release/commit/d55f25cac13625037c5154e3cdd7dbb9bb88e350))

* Update readme ([`e8a6dd9`](https://github.com/python-semantic-release/python-semantic-release/commit/e8a6dd9e264a3e2d4186c323f7b544d4e42754b1))


## v0.1.0 (2015-07-27)

### Unknown

* 0.1.0 ([`30d5f43`](https://github.com/python-semantic-release/python-semantic-release/commit/30d5f4376dc540548f68da921bd87ae7b21e7996))

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
