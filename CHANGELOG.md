# Changelog

<!--next-version-placeholder-->

## v7.33.1 (2023-02-01)
### Fix
* **action:** Mark container fs as safe for git ([#552](https://github.com/python-semantic-release/python-semantic-release/issues/552)) ([`2a55f68`](https://github.com/python-semantic-release/python-semantic-release/commit/2a55f68e2b3cb9ffa9204c00ddbf12706af5c070))

## v7.33.0 (2023-01-15)
### Feature
* Add signing options to action ([`31ad5eb`](https://github.com/python-semantic-release/python-semantic-release/commit/31ad5eb5a25f0ea703afc295351104aefd66cac1))
* **repository:** Add support for TWINE_CERT ([#522](https://github.com/python-semantic-release/python-semantic-release/issues/522)) ([`d56e85d`](https://github.com/python-semantic-release/python-semantic-release/commit/d56e85d1f2ac66fb0b59af2178164ca915dbe163))
* Update action with configuration options ([#518](https://github.com/python-semantic-release/python-semantic-release/issues/518)) ([`4664afe`](https://github.com/python-semantic-release/python-semantic-release/commit/4664afe5f80a04834e398fefb841b166a51d95b7))

### Fix
* Changelog release commit search logic ([#530](https://github.com/python-semantic-release/python-semantic-release/issues/530)) ([`efb3410`](https://github.com/python-semantic-release/python-semantic-release/commit/efb341036196c39b4694ca4bfa56c6b3e0827c6c))
* Bump Dockerfile to use Python 3.10 image ([#536](https://github.com/python-semantic-release/python-semantic-release/issues/536)) ([`8f2185d`](https://github.com/python-semantic-release/python-semantic-release/commit/8f2185d570b3966b667ac591ae523812e9d2e00f))
* Fix mypy errors for publish ([`b40dd48`](https://github.com/python-semantic-release/python-semantic-release/commit/b40dd484387c1b3f78df53ee2d35e281e8e799c8))
* Formatting in docs ([`2e8227a`](https://github.com/python-semantic-release/python-semantic-release/commit/2e8227a8a933683250f8dace019df15fdb35a857))
* Update documentaton ([`5cbdad2`](https://github.com/python-semantic-release/python-semantic-release/commit/5cbdad296034a792c9bf05e3700eac4f847eb469))
* **action:** Fix environment variable names ([`3c66218`](https://github.com/python-semantic-release/python-semantic-release/commit/3c66218640044adf263fcf9b2714cfc4b99c2e90))

## v7.32.2 (2022-10-22)
### Fix
* Fix changelog generation in tag-mode ([#171](https://github.com/relekang/python-semantic-release/issues/171)) ([`482a62e`](https://github.com/relekang/python-semantic-release/commit/482a62ec374208b2d57675cb0b7f0ab9695849b9))

### Documentation
* Fix code blocks ([#506](https://github.com/relekang/python-semantic-release/issues/506)) ([`24b7673`](https://github.com/relekang/python-semantic-release/commit/24b767339fcef1c843f7dd3188900adab05e03b1))

## v7.32.1 (2022-10-07)
### Fix
* Corrections for deprecation warnings ([#505](https://github.com/relekang/python-semantic-release/issues/505)) ([`d47afb6`](https://github.com/relekang/python-semantic-release/commit/d47afb6516238939e174f946977bf4880062a622))

### Documentation
* Correct spelling mistakes ([#504](https://github.com/relekang/python-semantic-release/issues/504)) ([`3717e0d`](https://github.com/relekang/python-semantic-release/commit/3717e0d8810f5d683847c7b0e335eeefebbf2921))

## v7.32.0 (2022-09-25)
### Feature
* Add setting for enforcing textual changelog sections ([#502](https://github.com/relekang/python-semantic-release/issues/502)) ([`988437d`](https://github.com/relekang/python-semantic-release/commit/988437d21e40d3e3b1c95ed66b535bdd523210de))

### Documentation
* Correct documented default behaviour for `commit_version_number` ([#497](https://github.com/relekang/python-semantic-release/issues/497)) ([`ffae2dc`](https://github.com/relekang/python-semantic-release/commit/ffae2dc68f7f4bc13c5fd015acd43b457e568ada))

## v7.31.4 (2022-08-23)
### Fix
* Account for trailing newlines in commit messages ([#495](https://github.com/relekang/python-semantic-release/issues/495)) ([`111b151`](https://github.com/relekang/python-semantic-release/commit/111b1518e8c8e2bd7535bd4c4b126548da384605))

## v7.31.3 (2022-08-22)
### Fix
* Use `commit_subject` when searching for release commits ([#488](https://github.com/relekang/python-semantic-release/issues/488)) ([`3849ed9`](https://github.com/relekang/python-semantic-release/commit/3849ed992c3cff9054b8690bcf59e49768f84f47))

## v7.31.2 (2022-07-29)
### Fix
* Add better handling of missing changelog placeholder ([`e7a0e81`](https://github.com/relekang/python-semantic-release/commit/e7a0e81c004ade73ed927ba4de8c3e3ccaf0047c))
* Add repo=None when not in git repo ([`40be804`](https://github.com/relekang/python-semantic-release/commit/40be804c09ab8a036fb135c9c38a63f206d2742c))

### Documentation
* Add example for pyproject.toml ([`2a4b8af`](https://github.com/relekang/python-semantic-release/commit/2a4b8af1c2893a769c02476bb92f760c8522bd7a))

## v7.31.1 (2022-07-29)
### Fix
* Update git email in action ([`0ece6f2`](https://github.com/relekang/python-semantic-release/commit/0ece6f263ff02a17bb1e00e7ed21c490f72e3d00))

## v7.31.0 (2022-07-29)
### Feature
* Override repository_url w REPOSITORY_URL env var ([#439](https://github.com/relekang/python-semantic-release/issues/439)) ([`cb7578c`](https://github.com/relekang/python-semantic-release/commit/cb7578cf005b8bd65d9b988f6f773e4c060982e3))
* Add prerelease-patch and no-prerelease-patch flags for whether to auto-bump prereleases ([`b4e5b62`](https://github.com/relekang/python-semantic-release/commit/b4e5b626074f969e4140c75fdac837a0625cfbf6))

### Fix
* :bug: fix get_current_release_version for tag_only version_source ([`cad09be`](https://github.com/relekang/python-semantic-release/commit/cad09be9ba067f1c882379c0f4b28115a287fc2b))

## v7.30.2 (2022-07-26)
### Fix
* Declare additional_options as action inputs ([#481](https://github.com/relekang/python-semantic-release/issues/481)) ([`cb5d8c7`](https://github.com/relekang/python-semantic-release/commit/cb5d8c7ce7d013fcfabd7696b5ffb846a8a6f853))

## v7.30.1 (2022-07-25)
### Fix
* Don't use commit_subject for tag pattern matching ([#480](https://github.com/relekang/python-semantic-release/issues/480)) ([`ac3f11e`](https://github.com/relekang/python-semantic-release/commit/ac3f11e689f4a290d20b68b9c5c214098eb61b5f))

## v7.30.0 (2022-07-25)
### Feature
* Add `additional_options` input for GitHub Action ([#477](https://github.com/relekang/python-semantic-release/issues/477)) ([`aea60e3`](https://github.com/relekang/python-semantic-release/commit/aea60e3d290c6fe3137bff21e0db1ed936233776))

### Fix
* Allow empty additional options ([#479](https://github.com/relekang/python-semantic-release/issues/479)) ([`c9b2514`](https://github.com/relekang/python-semantic-release/commit/c9b2514d3e164b20e78b33f60989d78c2587e1df))

## v7.29.7 (2022-07-24)
### Fix
* Ignore dependency version bumps when parsing version from commit logs ([#476](https://github.com/relekang/python-semantic-release/issues/476)) ([`51bcb78`](https://github.com/relekang/python-semantic-release/commit/51bcb780a9f55fadfaf01612ff65c1f92642c2c1))

## v7.29.6 (2022-07-15)
### Fix
* Allow changing prerelease tag using CLI flags ([#466](https://github.com/relekang/python-semantic-release/issues/466)) ([`395bf4f`](https://github.com/relekang/python-semantic-release/commit/395bf4f2de73663c070f37cced85162d41934213))

## v7.29.5 (2022-07-14)
### Fix
* **publish:** Get version bump for current release ([#467](https://github.com/relekang/python-semantic-release/issues/467)) ([`dd26888`](https://github.com/relekang/python-semantic-release/commit/dd26888a923b2f480303c19f1916647de48b02bf))
* Add packaging module requirement ([#469](https://github.com/relekang/python-semantic-release/issues/469)) ([`b99c9fa`](https://github.com/relekang/python-semantic-release/commit/b99c9fa88dc25e5ceacb131cd93d9079c4fb2c86))

## v7.29.4 (2022-06-29)
### Fix
* Add text for empty ValueError ([#461](https://github.com/relekang/python-semantic-release/issues/461)) ([`733254a`](https://github.com/relekang/python-semantic-release/commit/733254a99320d8c2f964d799ac4ec29737867faa))

## v7.29.3 (2022-06-26)
### Fix
* Ensure that assets can be uploaded successfully on custom GitHub servers ([#458](https://github.com/relekang/python-semantic-release/issues/458)) ([`32b516d`](https://github.com/relekang/python-semantic-release/commit/32b516d7aded4afcafe4aa56d6a5a329b3fc371d))

## v7.29.2 (2022-06-20)
### Fix
* Ensure should_bump checks against release version if not prerelease ([#457](https://github.com/relekang/python-semantic-release/issues/457)) ([`da0606f`](https://github.com/relekang/python-semantic-release/commit/da0606f0d67ada5f097c704b9423ead3b5aca6b2))

## v7.29.1 (2022-06-01)
### Fix
* Capture correct release version when patch has more than one digit ([#448](https://github.com/relekang/python-semantic-release/issues/448)) ([`426cdc7`](https://github.com/relekang/python-semantic-release/commit/426cdc7d7e0140da67f33b6853af71b2295aaac2))

## v7.29.0 (2022-05-27)
### Feature
* Allow using ssh-key to push version while using token to publish to hvcs ([#419](https://github.com/relekang/python-semantic-release/issues/419)) ([`7b2dffa`](https://github.com/relekang/python-semantic-release/commit/7b2dffadf43c77d5e0eea307aefcee5c7744df5c))

### Fix
* Fix and refactor prerelease ([#435](https://github.com/relekang/python-semantic-release/issues/435)) ([`94c9494`](https://github.com/relekang/python-semantic-release/commit/94c94942561f85f48433c95fd3467e03e0893ab4))

## v7.28.1 (2022-04-14)
### Fix
* Fix getting current version when `version_source=tag_only` ([#437](https://github.com/relekang/python-semantic-release/issues/437)) ([`b247936`](https://github.com/relekang/python-semantic-release/commit/b247936a81c0d859a34bf9f17ab8ca6a80488081))

## v7.28.0 (2022-04-11)
### Feature
* Add `tag_only` option for `version_source` ([#436](https://github.com/relekang/python-semantic-release/issues/436)) ([`cf74339`](https://github.com/relekang/python-semantic-release/commit/cf743395456a86c62679c2c0342502af043bfc3b))

## v7.27.1 (2022-04-03)
### Fix
* **prerelase:** Pass prerelease option to get_current_version ([#432](https://github.com/relekang/python-semantic-release/issues/432)) ([`aabab0b`](https://github.com/relekang/python-semantic-release/commit/aabab0b7ce647d25e0c78ae6566f1132ece9fcb9))

## v7.27.0 (2022-03-15)
### Feature
* Add git-lfs to docker container ([#427](https://github.com/relekang/python-semantic-release/issues/427)) ([`184e365`](https://github.com/relekang/python-semantic-release/commit/184e3653932979b82e5a62b497f2a46cbe15ba87))

## v7.26.0 (2022-03-07)
### Feature
* Add prerelease functionality ([#413](https://github.com/relekang/python-semantic-release/issues/413)) ([`7064265`](https://github.com/relekang/python-semantic-release/commit/7064265627a2aba09caa2873d823b594e0e23e77))

## v7.25.2 (2022-02-24)
### Fix
* **gitea:** Use form-data from asset upload ([#421](https://github.com/relekang/python-semantic-release/issues/421)) ([`e011944`](https://github.com/relekang/python-semantic-release/commit/e011944987885f75b80fe16a363f4befb2519a91))

## v7.25.1 (2022-02-23)
### Fix
* **gitea:** Build status and asset upload ([#420](https://github.com/relekang/python-semantic-release/issues/420)) ([`57db81f`](https://github.com/relekang/python-semantic-release/commit/57db81f4c6b96da8259e3bad9137eaccbcd10f6e))

## v7.25.0 (2022-02-17)
### Feature
* **hvcs:** Add gitea support ([#412](https://github.com/relekang/python-semantic-release/issues/412)) ([`b7e7936`](https://github.com/relekang/python-semantic-release/commit/b7e7936331b7939db09abab235c8866d800ddc1a))

### Documentation
* Document tag_commit ([`b631ca0`](https://github.com/relekang/python-semantic-release/commit/b631ca0a79cb2d5499715d43688fc284cffb3044))

## v7.24.0 (2022-01-24)
### Feature
* Include additional changes in release commits ([`3e34f95`](https://github.com/relekang/python-semantic-release/commit/3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9))

## v7.23.0 (2021-11-30)
### Feature
* Support Github Enterprise server ([`b4e01f1`](https://github.com/relekang/python-semantic-release/commit/b4e01f1b7e841263fa84f57f0ac331f7c0b31954))

## v7.22.0 (2021-11-21)
### Feature
* **parser_angular:** Allow customization in parser ([`298eebb`](https://github.com/relekang/python-semantic-release/commit/298eebbfab5c083505036ba1df47a5874a1eed6e))

### Fix
* Address PR feedback for `parser_angular.py` ([`f7bc458`](https://github.com/relekang/python-semantic-release/commit/f7bc45841e6a5c762f99f936c292cee25fabcd02))

## v7.21.0 (2021-11-21)
### Feature
* Use gitlab-ci or github actions env vars ([`8ca8dd4`](https://github.com/relekang/python-semantic-release/commit/8ca8dd40f742f823af147928bd75a9577c50d0fd))

### Fix
* Remove invalid repository exception ([`746b62d`](https://github.com/relekang/python-semantic-release/commit/746b62d4e207a5d491eecd4ca96d096eb22e3bed))

## v7.20.0 (2021-11-21)
### Feature
* Rewrite Twine adapter for uploading to artifact repositories ([`cfb20af`](https://github.com/relekang/python-semantic-release/commit/cfb20af79a8e25a77aee9ff72deedcd63cb7f62f))
* Allow custom environment variable names ([#392](https://github.com/relekang/python-semantic-release/issues/392)) ([`372cda3`](https://github.com/relekang/python-semantic-release/commit/372cda3497f16ead2209e6e1377d38f497144883))
* **repository:** Add to settings artifact repository ([`f4ef373`](https://github.com/relekang/python-semantic-release/commit/f4ef3733b948282fba5a832c5c0af134609b26d2))

### Fix
* Mypy errors in vcs_helpers ([`13ca0fe`](https://github.com/relekang/python-semantic-release/commit/13ca0fe650125be2f5e953f6193fdc4d44d3c75a))
* Skip removing the build folder if it doesn't exist ([`8e79fdc`](https://github.com/relekang/python-semantic-release/commit/8e79fdc107ffd852a91dfb5473e7bd1dfaba4ee5))
* Don't use linux commands on windows ([#393](https://github.com/relekang/python-semantic-release/issues/393)) ([`5bcccd2`](https://github.com/relekang/python-semantic-release/commit/5bcccd21cc8be3289db260e645fec8dc6a592abd))

### Documentation
* Clean typos and add section for repository upload ([`1efa18a`](https://github.com/relekang/python-semantic-release/commit/1efa18a3a55134d6bc6e4572ab025e24082476cd))

## v7.19.2 (2021-09-04)
### Fix
* Fixed ImproperConfig import error ([#377](https://github.com/relekang/python-semantic-release/issues/377)) ([`b011a95`](https://github.com/relekang/python-semantic-release/commit/b011a9595df4240cb190bfb1ab5b6d170e430dfc))

## v7.19.1 (2021-08-17)
### Fix
* Add get_formatted_tag helper instead of hardcoded v-prefix in the git tags ([`1a354c8`](https://github.com/relekang/python-semantic-release/commit/1a354c86abad77563ebce9a6944256461006f3c7))

## v7.19.0 (2021-08-16)
### Feature
* Custom git tag format support ([#373](https://github.com/relekang/python-semantic-release/issues/373)) ([`1d76632`](https://github.com/relekang/python-semantic-release/commit/1d76632043bf0b6076d214a63c92013624f4b95e))

### Documentation
* **parser:** Documentation for scipy-parser ([`45ee34a`](https://github.com/relekang/python-semantic-release/commit/45ee34aa21443860a6c2cd44a52da2f353b960bf))

## v7.18.0 (2021-08-09)
### Feature
* Add support for non-prefixed tags ([#366](https://github.com/relekang/python-semantic-release/issues/366)) ([`0fee4dd`](https://github.com/relekang/python-semantic-release/commit/0fee4ddb5baaddf85ed6b76e76a04474a5f97d0a))

### Documentation
* Clarify second argument of ParsedCommit ([`086ddc2`](https://github.com/relekang/python-semantic-release/commit/086ddc28f06522453328f5ea94c873bd202ff496))

## v7.17.0 (2021-08-07)
### Feature
* **parser:** Add scipy style parser ([#369](https://github.com/relekang/python-semantic-release/issues/369)) ([`51a3921`](https://github.com/relekang/python-semantic-release/commit/51a39213ea120c4bbd7a57b74d4f0cc3103da9f5))

## v7.16.4 (2021-08-03)
### Fix
* Correct rendering of gitlab issue references ([`07429ec`](https://github.com/relekang/python-semantic-release/commit/07429ec4a32d32069f25ec77b4bea963bd5d2a00))

## v7.16.3 (2021-07-29)
### Fix
* Print right info if token is not set (#360) ([#361](https://github.com/relekang/python-semantic-release/issues/361)) ([`a275a7a`](https://github.com/relekang/python-semantic-release/commit/a275a7a17def85ff0b41d254e4ee42772cce1981))

## v7.16.2 (2021-06-25)
### Fix
* Use release-api for gitlab ([`1ef5cab`](https://github.com/relekang/python-semantic-release/commit/1ef5caba2d8dd0f2647bc51ede0ef7152d8b7b8d))

### Documentation
* Update trove classifiers to reflect supported versions ([#344](https://github.com/relekang/python-semantic-release/issues/344)) ([`7578004`](https://github.com/relekang/python-semantic-release/commit/7578004ed4b20c2bd553782443dfd77535faa377))
* Recommend setting a concurrency group for GitHub Actions ([`34b0735`](https://github.com/relekang/python-semantic-release/commit/34b07357ab3f4f4aa787b71183816ec8aaf334a8))

## v7.16.1 (2021-06-08)
### Fix
* Tomlkit should stay at 0.7.0 ([`769a5f3`](https://github.com/relekang/python-semantic-release/commit/769a5f31115cdb1f43f19a23fe72b96a8c8ba0fc))

## v7.16.0 (2021-06-08)
### Feature
* Add option to omit tagging ([#341](https://github.com/relekang/python-semantic-release/issues/341)) ([`20603e5`](https://github.com/relekang/python-semantic-release/commit/20603e53116d4f05e822784ce731b42e8cbc5d8f))

## v7.15.6 (2021-06-08)
### Fix
* Update click and tomlkit ([#339](https://github.com/relekang/python-semantic-release/issues/339)) ([`947ea3b`](https://github.com/relekang/python-semantic-release/commit/947ea3bc0750735941446cf4a87bae20e750ba12))

## v7.15.5 (2021-05-26)
### Fix
* Pin tomlkit to 0.7.0 ([`2cd0db4`](https://github.com/relekang/python-semantic-release/commit/2cd0db4537bb9497b72eb496f6bab003070672ab))

## v7.15.4 (2021-04-29)
### Fix
* Change log level of failed toml loading ([`24bb079`](https://github.com/relekang/python-semantic-release/commit/24bb079cbeff12e7043dd35dd0b5ae03192383bb))

## v7.15.3 (2021-04-03)
### Fix
* Add venv to path in github action ([`583c5a1`](https://github.com/relekang/python-semantic-release/commit/583c5a13e40061fc544b82decfe27a6c34f6d265))

## v7.15.2 (2021-04-03)
### Fix
* Use absolute path for venv in github action ([`d4823b3`](https://github.com/relekang/python-semantic-release/commit/d4823b3b6b1fcd5c33b354f814643c9aaf85a06a))
* Set correct path for venv in action script ([`aac02b5`](https://github.com/relekang/python-semantic-release/commit/aac02b5a44a6959328d5879578aa3536bdf856c2))
* Run semantic-release in virtualenv in the github action ([`b508ea9`](https://github.com/relekang/python-semantic-release/commit/b508ea9f411c1cd4f722f929aab9f0efc0890448))

### Documentation
* Clarify that HVCS should be lowercase ([`da0ab0c`](https://github.com/relekang/python-semantic-release/commit/da0ab0c62c4ce2fa0d815e5558aeec1a1e23bc89))

## v7.15.1 (2021-03-26)
### Fix
* Add support for setting build_command to "false" ([`520cf1e`](https://github.com/relekang/python-semantic-release/commit/520cf1eaa7816d0364407dbd17b5bc7c79806086))
* Upgrade python-gitlab range ([`abfacc4`](https://github.com/relekang/python-semantic-release/commit/abfacc432300941d57488842e41c06d885637e6c))

### Documentation
* Add common options to documentation ([`20d79a5`](https://github.com/relekang/python-semantic-release/commit/20d79a51bffa26d40607c1b77d10912992279112))

## v7.15.0 (2021-02-18)
### Feature
* Allow the use of .pypirc for twine uploads ([#325](https://github.com/relekang/python-semantic-release/issues/325)) ([`6bc56b8`](https://github.com/relekang/python-semantic-release/commit/6bc56b8aa63069a25a828a2d1a9038ecd09b7d5d))

### Documentation
* Add documentation for releasing on a Jenkins instance ([#324](https://github.com/relekang/python-semantic-release/issues/324)) ([`77ad988`](https://github.com/relekang/python-semantic-release/commit/77ad988a2057be59e4559614a234d6871c06ee37))

## v7.14.0 (2021-02-11)
### Feature
* **checks:** Add support for Jenkins CI ([#322](https://github.com/relekang/python-semantic-release/issues/322)) ([`3e99855`](https://github.com/relekang/python-semantic-release/commit/3e99855c6bc72b3e9a572c58cc14e82ddeebfff8))

### Documentation
* Correct casing on proper nouns ([#320](https://github.com/relekang/python-semantic-release/issues/320)) ([`d51b999`](https://github.com/relekang/python-semantic-release/commit/d51b999a245a4e56ff7a09d0495c75336f2f150d))

## v7.13.2 (2021-01-29)
### Fix
* Fix crash when TOML has no PSR section ([#319](https://github.com/relekang/python-semantic-release/issues/319)) ([`5f8ab99`](https://github.com/relekang/python-semantic-release/commit/5f8ab99bf7254508f4b38fcddef2bdde8dd15a4c))

### Documentation
* Fix `version_toml` example for Poetry ([#318](https://github.com/relekang/python-semantic-release/issues/318)) ([`39acb68`](https://github.com/relekang/python-semantic-release/commit/39acb68bfffe8242040e476893639ba26fa0d6b5))

## v7.13.1 (2021-01-26)
### Fix
* Use multiline version_pattern match in replace ([#315](https://github.com/relekang/python-semantic-release/issues/315)) ([`1a85af4`](https://github.com/relekang/python-semantic-release/commit/1a85af434325ce52e11b49895e115f7a936e417e))

## v7.13.0 (2021-01-26)
### Feature
* Support toml files for version declaration ([#307](https://github.com/relekang/python-semantic-release/issues/307)) ([`9b62a7e`](https://github.com/relekang/python-semantic-release/commit/9b62a7e377378667e716384684a47cdf392093fa))

## v7.12.0 (2021-01-25)
### Feature
* **github:** Retry GitHub API requests on failure ([#314](https://github.com/relekang/python-semantic-release/issues/314)) ([`ac241ed`](https://github.com/relekang/python-semantic-release/commit/ac241edf4de39f4fc0ff561a749fa85caaf9e2ae))

### Documentation
* **actions:** PAT must be passed to checkout step too ([`e2d8e47`](https://github.com/relekang/python-semantic-release/commit/e2d8e47d2b02860881381318dcc088e150c0fcde))

## v7.11.0 (2021-01-08)
### Feature
* **print-version:** Add print-version command to output version ([`512e3d9`](https://github.com/relekang/python-semantic-release/commit/512e3d92706055bdf8d08b7c82927d3530183079))

### Fix
* **actions:** Fix github actions with new main location ([`6666672`](https://github.com/relekang/python-semantic-release/commit/6666672d3d97ab7cdf47badfa3663f1a69c2dbdf))
* Avoid Unknown bump level 0 message ([`8ab624c`](https://github.com/relekang/python-semantic-release/commit/8ab624cf3508b57a9656a0a212bfee59379d6f8b))
* Add dot to --define option help ([`eb4107d`](https://github.com/relekang/python-semantic-release/commit/eb4107d2efdf8c885c8ae35f48f1b908d1fced32))

## v7.10.0 (2021-01-08)
### Feature
* **build:** Allow falsy values for build_command to disable build step ([`c07a440`](https://github.com/relekang/python-semantic-release/commit/c07a440f2dfc45a2ad8f7c454aaac180c4651f70))

### Documentation
* Fix incorrect reference syntax ([`42027f0`](https://github.com/relekang/python-semantic-release/commit/42027f0d2bb64f4c9eaec65112bf7b6f67568e60))
* Rewrite getting started page ([`97a9046`](https://github.com/relekang/python-semantic-release/commit/97a90463872502d1207890ae1d9dd008b1834385))

## v7.9.0 (2020-12-21)
### Feature
* **hvcs:** Add hvcs_domain config option ([`ab3061a`](https://github.com/relekang/python-semantic-release/commit/ab3061ae93c49d71afca043b67b361e2eb2919e6))

### Fix
* **history:** Coerce version to string ([#298](https://github.com/relekang/python-semantic-release/issues/298)) ([`d4cdc3d`](https://github.com/relekang/python-semantic-release/commit/d4cdc3d3cd2d93f2a78f485e3ea107ac816c7d00))
* **history:** Require semver >= 2.10 ([`5087e54`](https://github.com/relekang/python-semantic-release/commit/5087e549399648cf2e23339a037b33ca8b62d954))

## v7.8.2 (2020-12-19)
### Fix
* **cli:** Skip remove_dist where not needed ([`04817d4`](https://github.com/relekang/python-semantic-release/commit/04817d4ecfc693195e28c80455bfbb127485f36b))

## v7.8.1 (2020-12-18)
### Fix
* **logs:** Fix TypeError when enabling debug logs ([`2591a94`](https://github.com/relekang/python-semantic-release/commit/2591a94115114c4a91a48f5b10b3954f6ac932a1))
* Filenames with unknown mimetype are now properly uploaded to github release ([`f3ece78`](https://github.com/relekang/python-semantic-release/commit/f3ece78b2913e70f6b99907b192a1e92bbfd6b77))

## v7.8.0 (2020-12-18)
### Feature
* Add `upload_to_pypi_glob_patterns` option ([`42305ed`](https://github.com/relekang/python-semantic-release/commit/42305ed499ca08c819c4e7e65fcfbae913b8e6e1))

### Fix
* **netrc:** Prefer using token defined in GH_TOKEN instead of .netrc file ([`3af32a7`](https://github.com/relekang/python-semantic-release/commit/3af32a738f2f2841fd75ec961a8f49a0b1c387cf))
* **changelog:** Use "issues" link vs "pull" ([`93e48c9`](https://github.com/relekang/python-semantic-release/commit/93e48c992cb8b763f430ecbb0b7f9c3ca00036e4))

## v7.7.0 (2020-12-12)
### Feature
* **changelog:** Add PR links in markdown ([#282](https://github.com/relekang/python-semantic-release/pull/282)) ([`0448f6c`](https://github.com/relekang/python-semantic-release/commit/0448f6c350bbbf239a81fe13dc5f45761efa7673))

## v7.6.0 (2020-12-06)
### Feature
* Add `major_on_zero` option ([`d324154`](https://github.com/relekang/python-semantic-release/commit/d3241540e7640af911eb24c71e66468feebb0d46))

### Documentation
* Add documentation for option `major_on_zero` ([`2e8b26e`](https://github.com/relekang/python-semantic-release/commit/2e8b26e4ee0316a2cf2a93c09c783024fcd6b3ba))

## v7.5.0 (2020-12-04)
### Feature
* **logs:** Include scope in changelogs (#281) ([`21c96b6`](https://github.com/relekang/python-semantic-release/commit/21c96b688cc44cc6f45af962ffe6d1f759783f37))

## v7.4.1 (2020-12-04)
### Fix
* Add "changelog_capitalize" to flags (#279) ([`37716df`](https://github.com/relekang/python-semantic-release/commit/37716dfa78eb3f848f57a5100d01d93f5aafc0bf))

## v7.4.0 (2020-11-24)
### Feature
* Add changelog_capitalize configuration ([`7cacca1`](https://github.com/relekang/python-semantic-release/commit/7cacca1eb436a7166ba8faf643b53c42bc32a6a7))

### Documentation
* Fix broken internal references (#270) ([`da20b9b`](https://github.com/relekang/python-semantic-release/commit/da20b9bdd3c7c87809c25ccb2a5993a7ea209a22))
* Update links to Github docs (#268) ([`c53162e`](https://github.com/relekang/python-semantic-release/commit/c53162e366304082a3bd5d143b0401da6a16a263))

## v7.3.0 (2020-09-28)
### Feature
* Generate `changelog.md` file (#266) ([`2587dfe`](https://github.com/relekang/python-semantic-release/commit/2587dfed71338ec6c816f58cdf0882382c533598))

### Documentation
* Fix docstring ([`5a5e2cf`](https://github.com/relekang/python-semantic-release/commit/5a5e2cfb5e6653fb2e95e6e23e56559953b2c2b4))
