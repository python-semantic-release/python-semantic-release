.. _changelog:

=========
CHANGELOG
=========

.. _changelog-v10.5.3:

v10.5.3 (2025-12-14)
====================

🪲 Bug Fixes
------------

* **cmd-version**: Resolve unauthenticated git repo issues for upstream verification, closes
  `#1373`_ (`PR#1388`_, `e164f68`_)

* **github-action**: Fix failed signing issue when ssh was missing from action environment, closes
  `#1376`_ (`PR#1389`_, `18b7eda`_)

* **parser-conventional-monorepo**: Fix parser opts validator for outside dir path matches, closes
  `#1380`_ (`PR#1382`_, `a51eadd`_)

.. _#1373: https://github.com/python-semantic-release/python-semantic-release/issues/1373
.. _#1376: https://github.com/python-semantic-release/python-semantic-release/issues/1376
.. _#1380: https://github.com/python-semantic-release/python-semantic-release/issues/1380
.. _18b7eda: https://github.com/python-semantic-release/python-semantic-release/commit/18b7edadd7e7dfe42ec43110acf5e1bd8bcd7eb3
.. _a51eadd: https://github.com/python-semantic-release/python-semantic-release/commit/a51eadd8414a7e9cbfa66837ee5a840a6331dfa1
.. _e164f68: https://github.com/python-semantic-release/python-semantic-release/commit/e164f682bfa4ca1e7cbe77aa068202fd8094eec7
.. _PR#1382: https://github.com/python-semantic-release/python-semantic-release/pull/1382
.. _PR#1388: https://github.com/python-semantic-release/python-semantic-release/pull/1388
.. _PR#1389: https://github.com/python-semantic-release/python-semantic-release/pull/1389


.. _changelog-v10.5.2:

v10.5.2 (2025-11-10)
====================

🪲 Bug Fixes
------------

* **cmd-version**: Toggle verify upstream off when no version commit is made (`PR#1370`_,
  `e0b3b70`_)

.. _e0b3b70: https://github.com/python-semantic-release/python-semantic-release/commit/e0b3b7075a4c98cd7af97e0b8470872c11e7aeb9
.. _PR#1370: https://github.com/python-semantic-release/python-semantic-release/pull/1370


.. _changelog-v10.5.1:

v10.5.1 (2025-11-10)
====================

🪲 Bug Fixes
------------

* **cmd-version**: Fix upstream change detection to succeed without branch tracking (`PR#1369`_,
  `7086257`_)

.. _7086257: https://github.com/python-semantic-release/python-semantic-release/commit/7086257b641e241dc9a8d742bd62e3698a8b8173
.. _PR#1369: https://github.com/python-semantic-release/python-semantic-release/pull/1369


.. _changelog-v10.5.0:

v10.5.0 (2025-11-09)
====================

✨ Features
-----------

* **cmd-version**: Add automatic repository un-shallowing to version workflow (`PR#1366`_,
  `90a1ffa`_)

* **cmd-version**: Add functionality to create & update partial version tags (`PR#1115`_,
  `a28f940`_)

* **cmd-version**: Adds c-macro style version definition support to ``version_variables``, closes
  `#1348`_ (`PR#1349`_, `4ce1fca`_)

* **cmd-version**: Adds upstream check into workflow to prevent commit push collisions (`PR#1360`_,
  `d77193e`_)

🪲 Bug Fixes
------------

* **cmd-version**: Prevent regular expression errors on ``tag_format`` (`PR#1367`_, `e7d7aa7`_)

📖 Documentation
----------------

* **commands**: Add description of automated upstream version checking upon version creation
  (`PR#1360`_, `d77193e`_)

* **configuration**: Add description for ``add_partial_tags`` setting & usage examples (`PR#1115`_,
  `a28f940`_)

* **configuration**: Fix ``tag_format`` definition (`PR#1367`_, `e7d7aa7`_)

* **configuration**: Update ``version_variables`` examples with a c-macro style replacement
  (`PR#1349`_, `4ce1fca`_)

* **github-actions**: Adds release job outputs definition to example (`PR#1344`_, `0fb4875`_)

* **github-actions**: Removed verify upstream status step from example workflow (`PR#1360`_,
  `d77193e`_)

* **github-actions**: Update example to remove need to specify repo checkout's fetch depth
  (`PR#1366`_, `90a1ffa`_)

* **uv-integration**: Remove verify upstream check from uv integration example (`PR#1360`_,
  `d77193e`_)

* **uv-integration**: Update example to remove need to specify repo checkout's fetch depth
  (`PR#1366`_, `90a1ffa`_)

⚙️ Build System
----------------

* **deps**: Bump ``tomlkit`` dependency from ~=0.11.0 to ~=0.13.0 (`PR#1355`_, `55c94ec`_)

* **deps**: Change github-actions container image to ``python:3.14-slim-trixie`` (`PR#1346`_,
  `1a23712`_)

💡 Additional Release Information
---------------------------------

* **cmd-version**: If you were previously handling the unshallowing of a repository clone in your
  CI/CD pipelines, you may now remove that step from your workflow. PSR will now detect a shallow
  repository and unshallow it before evaluating the commit history.

.. _#1348: https://github.com/python-semantic-release/python-semantic-release/issues/1348
.. _0fb4875: https://github.com/python-semantic-release/python-semantic-release/commit/0fb4875fa24ed283ed2d97ff6ab1879669a787ca
.. _1a23712: https://github.com/python-semantic-release/python-semantic-release/commit/1a237125badcb597ae7a92db4e01c2ff3293bce8
.. _4ce1fca: https://github.com/python-semantic-release/python-semantic-release/commit/4ce1fcac60ac73657a4aaaaa3cb7c4afc7eac2c1
.. _55c94ec: https://github.com/python-semantic-release/python-semantic-release/commit/55c94ecde1aec47b88aa172d031ab33afa7f795d
.. _90a1ffa: https://github.com/python-semantic-release/python-semantic-release/commit/90a1ffa55c5a1605c59cb26a1797f9a37fdfa784
.. _a28f940: https://github.com/python-semantic-release/python-semantic-release/commit/a28f9401c4b285aa1007b72eb051d42567f33f93
.. _d77193e: https://github.com/python-semantic-release/python-semantic-release/commit/d77193e30807968ba6a26bd356a868db62dc1098
.. _e7d7aa7: https://github.com/python-semantic-release/python-semantic-release/commit/e7d7aa74a216cd2fdd78afc1e0e8b6b8044954ec
.. _PR#1115: https://github.com/python-semantic-release/python-semantic-release/pull/1115
.. _PR#1344: https://github.com/python-semantic-release/python-semantic-release/pull/1344
.. _PR#1346: https://github.com/python-semantic-release/python-semantic-release/pull/1346
.. _PR#1349: https://github.com/python-semantic-release/python-semantic-release/pull/1349
.. _PR#1355: https://github.com/python-semantic-release/python-semantic-release/pull/1355
.. _PR#1360: https://github.com/python-semantic-release/python-semantic-release/pull/1360
.. _PR#1366: https://github.com/python-semantic-release/python-semantic-release/pull/1366
.. _PR#1367: https://github.com/python-semantic-release/python-semantic-release/pull/1367


.. _changelog-v10.4.1:

v10.4.1 (2025-09-13)
====================

🪲 Bug Fixes
------------

* **cmd-version**: Fix error where ``--no-tag`` is not respected, closes `#1304`_ (`PR#1329`_,
  `b090fa2`_)

📖 Documentation
----------------

* **CHANGELOG**: Update hyperlink in v10.4.0's additional info paragraph (`PR#1323`_, `98ef722`_)

* **getting-started-guide**: Remove notice about lack of monorepo support, closes `#1326`_
  (`PR#1327`_, `3f21f3f`_)

* **github-actions**: Fix recommended upstream detection script's upstream name parsing (`PR#1328`_,
  `ccc91c0`_)

.. _#1304: https://github.com/python-semantic-release/python-semantic-release/issues/1304
.. _#1326: https://github.com/python-semantic-release/python-semantic-release/issues/1326
.. _3f21f3f: https://github.com/python-semantic-release/python-semantic-release/commit/3f21f3fc47a0dacc11ec95feb2a23f8cf132e77b
.. _98ef722: https://github.com/python-semantic-release/python-semantic-release/commit/98ef722b65bd6a37492cf7ec8b0425800f719114
.. _b090fa2: https://github.com/python-semantic-release/python-semantic-release/commit/b090fa2efc0ebfb40bdc572fea307d356af95a3f
.. _ccc91c0: https://github.com/python-semantic-release/python-semantic-release/commit/ccc91c09fab45358c7e52b42e6c0607c68c9d8f3
.. _PR#1323: https://github.com/python-semantic-release/python-semantic-release/pull/1323
.. _PR#1327: https://github.com/python-semantic-release/python-semantic-release/pull/1327
.. _PR#1328: https://github.com/python-semantic-release/python-semantic-release/pull/1328
.. _PR#1329: https://github.com/python-semantic-release/python-semantic-release/pull/1329


.. _changelog-v10.4.0:

v10.4.0 (2025-09-08)
====================

✨ Features
-----------

* **config**: Add ``conventional-monorepo`` as valid ``commit_parser`` type (`PR#1143`_, `e18f866`_)

* **parser**: Add new conventional-commits standard parser for monorepos, closes `#614`_
  (`PR#1143`_, `e18f866`_)

📖 Documentation
----------------

* Add configuration guide for monorepo use with PSR (`PR#1143`_, `e18f866`_)

* **commit-parsers**: Introduce conventional commit monorepo parser options & features (`PR#1143`_,
  `e18f866`_)

* **configuration**: Update ``commit_parser`` option with new ``conventional-monorepo`` value
  (`PR#1143`_, `e18f866`_)

💡 Additional Release Information
---------------------------------

* **config**: This release introduces a new built-in parser type that can be utilized for monorepo
  projects. The type value is ``conventional-monorepo`` and when specified it will apply the
  conventional commit parser to a monorepo environment. This parser has specialized options to help
  handle monorepo projects as well. For more information, please refer to the `Monorepo Docs`_.

.. _#614: https://github.com/python-semantic-release/python-semantic-release/issues/614
.. _e18f866: https://github.com/python-semantic-release/python-semantic-release/commit/e18f86640a78b374a327848b9e2ba868003d1a43
.. _Monorepo Docs: /configuration/configuration-guides/monorepos.html
.. _PR#1143: https://github.com/python-semantic-release/python-semantic-release/pull/1143


.. _changelog-v10.3.2:

v10.3.2 (2025-09-06)
====================

🪲 Bug Fixes
------------

* **cmd-version**: Prevent errors when PSR is executed in non-GitHub CI environments, closes
  `#1315`_ (`PR#1322`_, `4df4be4`_)

⚡ Performance Improvements
---------------------------

* **cmd-version**: Re-order operations for faster parsing in version determination (`PR#1310`_,
  `63e435b`_)

📖 Documentation
----------------

* **uv-integration**: Add ``--no-changelog`` to build step to increase job speed (`PR#1316`_,
  `e1aece1`_)

💡 Additional Release Information
---------------------------------

* **cmd-version**: Unfortunately, PSR introduced a bug in 10.3.0 when attempting to provide more CI
  outputs for GitHub Actions. It required our GitHub client interface to be loaded and even if it
  was not using GitHub CI to be run. This caused errors in Gitea and likely GitLab/Bitbucket
  environments. This change prevents that from happening but if any users pipelines were
  intentionally presenting the environment variable "GITHUB_OUTPUT" to enable action output to
  enable passing along internal outputs of PSR then their hack will no longer work after this
  change.

.. _#1315: https://github.com/python-semantic-release/python-semantic-release/issues/1315
.. _4df4be4: https://github.com/python-semantic-release/python-semantic-release/commit/4df4be465710e3b31ba65487069eccef1eeb8be1
.. _63e435b: https://github.com/python-semantic-release/python-semantic-release/commit/63e435ba466e1e980b9680d0f759950e5e598a61
.. _e1aece1: https://github.com/python-semantic-release/python-semantic-release/commit/e1aece18ae1998b1523be65b1e569837a7054251
.. _PR#1310: https://github.com/python-semantic-release/python-semantic-release/pull/1310
.. _PR#1316: https://github.com/python-semantic-release/python-semantic-release/pull/1316
.. _PR#1322: https://github.com/python-semantic-release/python-semantic-release/pull/1322


.. _changelog-v10.3.1:

v10.3.1 (2025-08-06)
====================

🪲 Bug Fixes
------------

* **github-actions**: Refactor the action output error checking for non-release executions, closes
  `#1307`_ (`PR#1308`_, `5385724`_)

📖 Documentation
----------------

* **github-actions**: Adjust docs for direct links to action example workflows, closes `#1303`_
  (`PR#1309`_, `8efebe2`_)

.. _#1303: https://github.com/python-semantic-release/python-semantic-release/issues/1303
.. _#1307: https://github.com/python-semantic-release/python-semantic-release/issues/1307
.. _5385724: https://github.com/python-semantic-release/python-semantic-release/commit/538572426cb30dd4d8c99cea660e290b56361f75
.. _8efebe2: https://github.com/python-semantic-release/python-semantic-release/commit/8efebe281be2deab1b203cd01d9aedf1542c4ad4
.. _PR#1308: https://github.com/python-semantic-release/python-semantic-release/pull/1308
.. _PR#1309: https://github.com/python-semantic-release/python-semantic-release/pull/1309


.. _changelog-v10.3.0:

v10.3.0 (2025-08-04)
====================

✨ Features
-----------

* **github-actions**: Add ``commit_sha`` as a GitHub Actions output value, closes `#717`_
  (`PR#1289`_, `39b647b`_)

* **github-actions**: Add ``previous_version`` as a GitHub Actions output value (`PR#1302`_,
  `c0197b7`_)

* **github-actions**: Add ``release_notes`` as a GitHub Actions output value (`PR#1300`_,
  `a3fd23c`_)

* **github-actions**: Add release ``link`` as a GitHub Actions output value (`PR#1301`_, `888aea1`_)

🪲 Bug Fixes
------------

* **github-actions**: Fix variable output newlines (`PR#1300`_, `a3fd23c`_)

* **util**: Fixes no-op log output when commit message contains square-brackets, closes `#1251`_
  (`PR#1287`_, `f25883f`_)

📖 Documentation
----------------

* **getting-started**: Fixes ``changelog.exclude_commit_patterns`` example in startup guide, closes
  `#1291`_ (`PR#1292`_, `2ce2e94`_)

* **github-actions**: Add description of ``commit_sha`` GitHub Action output in docs (`PR#1289`_,
  `39b647b`_)

* **github-actions**: Add description of ``previous_release`` GitHub Action output (`PR#1302`_,
  `c0197b7`_)

* **github-actions**: Add description of ``release_notes`` GitHub Action output (`PR#1300`_,
  `a3fd23c`_)

* **github-actions**: Add description of release ``link`` GitHub Action output (`PR#1301`_,
  `888aea1`_)

* **README**: Update broken links to match re-located destinations (`PR#1285`_, `f4ec792`_)

.. _#1251: https://github.com/python-semantic-release/python-semantic-release/issues/1251
.. _#1291: https://github.com/python-semantic-release/python-semantic-release/issues/1291
.. _#717: https://github.com/python-semantic-release/python-semantic-release/issues/717
.. _2ce2e94: https://github.com/python-semantic-release/python-semantic-release/commit/2ce2e94e1930987a88c0a5e3d59baa7cb717f557
.. _39b647b: https://github.com/python-semantic-release/python-semantic-release/commit/39b647ba62e242342ef5a0d07cb0cfdfa7769865
.. _888aea1: https://github.com/python-semantic-release/python-semantic-release/commit/888aea1e450513ac7339c72d8b50fabdb4ac177b
.. _a3fd23c: https://github.com/python-semantic-release/python-semantic-release/commit/a3fd23cb0e49f74cb4a345048609d3643a665782
.. _c0197b7: https://github.com/python-semantic-release/python-semantic-release/commit/c0197b711cfa83f5b13f9ae4f37e555b26f544d9
.. _f25883f: https://github.com/python-semantic-release/python-semantic-release/commit/f25883f8403365b787e7c3e86d2d982906804621
.. _f4ec792: https://github.com/python-semantic-release/python-semantic-release/commit/f4ec792d73acb34b8f5183ec044a301b593f16f0
.. _PR#1285: https://github.com/python-semantic-release/python-semantic-release/pull/1285
.. _PR#1287: https://github.com/python-semantic-release/python-semantic-release/pull/1287
.. _PR#1289: https://github.com/python-semantic-release/python-semantic-release/pull/1289
.. _PR#1292: https://github.com/python-semantic-release/python-semantic-release/pull/1292
.. _PR#1300: https://github.com/python-semantic-release/python-semantic-release/pull/1300
.. _PR#1301: https://github.com/python-semantic-release/python-semantic-release/pull/1301
.. _PR#1302: https://github.com/python-semantic-release/python-semantic-release/pull/1302


.. _changelog-v10.2.0:

v10.2.0 (2025-06-29)
====================

✨ Features
-----------

* **cmd-version**: Adds ``PACKAGE_NAME`` value into build command environment (`db9bc13`_)

📖 Documentation
----------------

* **configuration**: Update build command environment definition to include ``PACKAGE_NAME``
  variable (`4aa3805`_)

* **uv-integration**: Fix configuration guide for ``uv`` usage to ensure lock file update
  (`5390145`_)

.. _4aa3805: https://github.com/python-semantic-release/python-semantic-release/commit/4aa38059ce6b33ca23a547473e9fb8a19d3ffbe1
.. _5390145: https://github.com/python-semantic-release/python-semantic-release/commit/5390145503b4d5dcca8f323e1ba6c5bec0bd079b
.. _db9bc13: https://github.com/python-semantic-release/python-semantic-release/commit/db9bc132c8a0398f2cce647730c69a32ca35ba51


.. _changelog-v10.1.0:

v10.1.0 (2025-06-12)
====================

✨ Features
-----------

* **cmd-version**: Always stage version stamped files & changelog even with ``--no-commit``, closes
  `#1211`_ (`PR#1214`_, `de62334`_)

📖 Documentation
----------------

* **cmd-version**: Improve command description & include common uses (`PR#1214`_, `de62334`_)

* **configuration-guide**: Add how-to guide for ``uv`` integration (`PR#1214`_, `de62334`_)

* **github-actions**: Clarify with examples of the ``root_options`` v10 migration change
  (`PR#1271`_, `fbb63ec`_)

⚙️ Build System
----------------

* **deps**: Expand ``python-gitlab`` dependency to include ``v6.0.0`` (`PR#1273`_, `99fc9cc`_)

.. _#1211: https://github.com/python-semantic-release/python-semantic-release/issues/1211
.. _99fc9cc: https://github.com/python-semantic-release/python-semantic-release/commit/99fc9ccabbae9adf5646731591080366eacbe03c
.. _de62334: https://github.com/python-semantic-release/python-semantic-release/commit/de623344cd18b3dbe05823eb90fdd010c5505c92
.. _fbb63ec: https://github.com/python-semantic-release/python-semantic-release/commit/fbb63ec76142ea903d8a0401369ec251abbec0fe
.. _PR#1214: https://github.com/python-semantic-release/python-semantic-release/pull/1214
.. _PR#1271: https://github.com/python-semantic-release/python-semantic-release/pull/1271
.. _PR#1273: https://github.com/python-semantic-release/python-semantic-release/pull/1273


.. _changelog-v10.0.2:

v10.0.2 (2025-05-26)
====================

🪲 Bug Fixes
------------

* **github-actions**: Add filesystem UID/GID fixer after action workspace modification (`PR#1262`_,
  `93e23c8`_)

.. _93e23c8: https://github.com/python-semantic-release/python-semantic-release/commit/93e23c8993fe6f113095bfcd5089684f403cc6b9
.. _PR#1262: https://github.com/python-semantic-release/python-semantic-release/pull/1262


.. _changelog-v10.0.1:

v10.0.1 (2025-05-25)
====================

🪲 Bug Fixes
------------

* **github-actions**: Bump the github-actions dependency to ``v10.0.0`` (`PR#1255`_, `2803676`_)

.. _2803676: https://github.com/python-semantic-release/python-semantic-release/commit/2803676cf26c52177fa98d9144934853744a22bb
.. _PR#1255: https://github.com/python-semantic-release/python-semantic-release/pull/1255


.. _changelog-v10.0.0:

v10.0.0 (2025-05-25)
====================

✨ Features
-----------

* **cmd-version**: Enable ``version_variables`` version stamp of vars with double-equals
  (`PR#1244`_, `080e4bc`_)

* **parser-conventional**: Set parser to evaluate all squashed commits by default (`6fcdc99`_)

* **parser-conventional**: Set parser to ignore merge commits by default (`59bf084`_)

* **parser-emoji**: Set parser to evaluate all squashed commits by default (`514a922`_)

* **parser-emoji**: Set parser to ignore merge commits by default (`8a51525`_)

* **parser-scipy**: Set parser to evaluate all squashed commits by default (`634fffe`_)

* **parser-scipy**: Set parser to ignore merge commits by default (`d4f128e`_)

🪲 Bug Fixes
------------

* **changelog-md**: Change to 1-line descriptions in markdown template, closes `#733`_ (`e7ac155`_)

* **changelog-rst**: Change to 1-line descriptions in the default ReStructuredText template, closes
  `#733`_ (`731466f`_)

* **cli**: Adjust verbosity parameter to enable silly-level logging (`bd3e7bf`_)

* **github-action**: Resolve command injection vulnerability in action script (`fb3da27`_)

* **parser-conventional**: Remove breaking change footer messages from commit descriptions
  (`b271cbb`_)

* **parser-conventional**: Remove issue footer messages from commit descriptions (`b1bb0e5`_)

* **parser-conventional**: Remove PR/MR references from commit subject line (`eed63fa`_)

* **parser-conventional**: Remove release notice footer messages from commit descriptions
  (`7e8dc13`_)

* **parser-emoji**: Remove issue footer messages from commit descriptions (`b757603`_)

* **parser-emoji**: Remove PR/MR references from commit subject line (`16465f1`_)

* **parser-emoji**: Remove release notice footer messages from commit descriptions (`b6307cb`_)

* **parser-scipy**: Remove issue footer messages from commit descriptions (`3cfee76`_)

* **parser-scipy**: Remove PR/MR references from commit subject line (`da4140f`_)

* **parser-scipy**: Remove release notice footer messages from commit descriptions (`58308e3`_)

📖 Documentation
----------------

* Refactor documentation page navigation (`4e52f4b`_)

* **algorithm**: Remove out-of-date algorithm description (`6cd0fbe`_)

* **commit-parsing**: Define limitation of revert commits with the scipy parser (`5310d0c`_)

* **configuration**: Change default value for ``allow_zero_version`` in the description (`203d29d`_)

* **configuration**: Change the default for the base changelog's ``mask_initial_release`` value
  (`5fb02ab`_)

* **configuration**: Change the default value for ``changelog.mode`` in the setting description
  (`0bed906`_)

* **configuration**: Update ``version_variables`` section to include double-equals operand support
  (`PR#1244`_, `080e4bc`_)

* **contributing**: Refactor contributing & contributors layout (`8bed5bc`_)

* **github-actions**: Add reference to manual release workflow example (`6aad7f1`_)

* **github-actions**: Change recommended workflow to separate release from deploy (`67b2ae0`_)

* **github-actions**: Update ``python-semantic-release/publish-action`` parameter notes (`c4d45ec`_)

* **github-actions**: Update PSR action parameter documentation (`a082896`_)

* **upgrading**: Re-locate version upgrade guides into ``Upgrading PSR`` (`a5f5e04`_)

* **upgrading-v10**: Added migration guide for v9 to v10 (`4ea92ec`_)

⚙️ Build System
----------------

* **deps**: Prevent update to ``click@8.2.0`` (`PR#1245`_, `4aa6a6e`_)

♻️ Refactoring
---------------

* **config**: Change ``allow_zero_version`` default to ``false`` (`c6b6eab`_)

* **config**: Change ``changelog.default_templates.mask_initial_release`` default to ``true``
  (`0e114c3`_)

* **config**: Change ``changelog.mode`` default to ``update`` (`7d39e76`_)

💥 Breaking Changes
-------------------

.. seealso::
    *For a summarized walkthrough, check out our* |v10 migration guide|_ *as well.*

.. _v10 migration guide: ../upgrading/10-upgrade.html
.. |v10 migration guide| replace:: *v10 migration guide*

* **changelog-md**: The default Markdown changelog template and release notes template will no
  longer print out the entire commit message contents, instead, it will only print the commit
  subject line. This comes to meet the high demand of better formatted changelogs and requests for
  subject line only. Originally, it was a decision to not hide commit subjects that were included in
  the commit body via the ``git merge --squash`` command and PSR did not have another alternative.
  At this point, all the built-in parsers have the ability to parse squashed commits and separate
  them out into their own entry on the changelog. Therefore, the default template no longer needs to
  write out the full commit body. See the commit parser options if you want to enable/disable
  parsing squash commits.

* **changelog-rst**: The default ReStructured changelog template will no longer print out the entire
  commit message contents, instead, it will only print the commit subject line. This comes to meet
  the high demand of better formatted changelogs and requests for subject line only. Originally, it
  was a decision to not hide commit subjects that were included in the commit body via the ``git
  merge --squash`` command and PSR did not have another alternative. At this point, all the built-in
  parsers have the ability to parse squashed commits and separate them out into their own entry on
  the changelog. Therefore, the default template no longer needs to write out the full commit body.
  See the commit parser options if you want to enable/disable parsing squash commits.

* **config**: This release switches the ``allow_zero_version`` default to ``false``. This change is
  to encourage less ``0.x`` releases as the default but rather allow the experienced developer to
  choose when ``0.x`` is appropriate. There are way too many projects in the ecosystems that never
  leave ``0.x`` and that is problematic for the industry tools that help auto-update based on
  SemVer. We should strive for publishing usable tools and maintaining good forethought for when
  compatibility must break. If your configuration already sets the ``allow_zero_version`` value,
  this change will have no effect on your project. If you want to use ``0.x`` versions, from the
  start then change ``allow_zero_version`` to ``true`` in your configuration.

* **config**: This release switches the ``changelog.default_templates.mask_initial_release`` default
  to ``true``. This change is intended to toggle better recommended outputs of the default
  changelog. Conceptually, the very first release is hard to describe--one can only provide new
  features as nothing exists yet for the end user. No changelog should be written as there is no
  start point to compare the "changes" to. The recommendation instead is to only list a simple
  message as ``Initial Release``. This is now the default for PSR when providing the very first
  release (no pre-existing tags) in the changelog and release notes. If your configuration already
  sets the ``changelog.default_templates.mask_initial_release`` value, then this change will have no
  effect on your project. If you do NOT want to mask the first release information, then set
  ``changelog.default_templates.mask_initial_release`` to ``false`` in your configuration.

* **config**: This release switches the ``changelog.mode`` default to ``update``. In this mode, if a
  changelog exists, PSR will update the changelog **IF AND ONLY IF** the configured insertion flag
  exists in the changelog. The Changelog output will remain unchanged if no insertion flag exists.
  The insertion flag may be configured with the ``changelog.insertion_flag`` setting. When upgrading
  to ``v10``, you must add the insertion flag manually or you can just delete the changelog file and
  run PSR's changelog generation and it will rebuild the changelog (similar to init mode) but it
  will add the insertion flag. If your configuration already sets the ``changelog.mode`` value, then
  this change will have no effect on your project. If you would rather the changelog be generated
  from scratch every release, than set the ``changelog.mode`` value to ``init`` in your
  configuration.

* **github-action**: The ``root_options`` action input parameter has been removed because it created
  a command injection vulnerability for arbitrary code to execute within the container context of
  the GitHub action if a command injection code was provided as part of the ``root_options``
  parameter string. To eliminate the vulnerability, each relevant option that can be provided to
  ``semantic-release`` has been individually added as its own parameter and will be processed
  individually to prevent command injection. Please review our `Github Actions Configuration`__ page
  to review the newly available configuration options that replace the ``root_options`` parameter.

  __ https://github.com/python-semantic-release/python-semantic-release/blob/v10.0.0/docs/configuration/automatic-releases/github-actions.rst

* **parser-conventional**: Any breaking change footer messages that the conventional commit parser
  detects will now be removed from the ``commit.descriptions[]`` list but maintained in and only in
  the ``commit.breaking_descriptions[]`` list. Previously, the descriptions included all text from
  the commit message but that was redundant as the default changelog now handles breaking change
  footers in its own section.

* **parser-conventional, parser-emoji, parser-scipy**: Any issue resolution footers that the parser
  detects will now be removed from the ``commit.descriptions[]`` list. Previously, the descriptions
  included all text from the commit message but now that the parser pulls out the issue numbers the
  numbers will be included in the ``commit.linked_issues`` tuple for user extraction in any
  changelog generation.

* **parser-conventional, parser-emoji, parser-scipy**: Any release notice footer messages that the
  commit parser detects will now be removed from the ``commit.descriptions[]`` list but maintained
  in and only in the ``commit.notices[]`` list. Previously, the descriptions included all text from
  the commit message but that was redundant as the default changelog now handles release notice
  footers in its own section.

* **parser-conventional, parser-emoji, parser-scipy**: Generally, a pull request or merge request
  number reference is included in the subject line at the end within parentheses on some common
  VCS's like GitHub. PSR now looks for this reference and extracts it into the
  ``commit.linked_merge_request`` and the ``commit.linked_pull_request`` attributes of a commit
  object. Since this is now pulled out individually, it is cleaner to remove this from the first
  line of the ``commit.descriptions`` list (ie. the subject line) so that changelog macros do not
  have to replace the text but instead only append a PR/MR link to the end of the line. The
  reference does maintain the PR/MR prefix indicator (`#` or ``!``).

* **parser-conventional, parser-emoji, parser-scipy**: The configuration setting
  ``commit_parser_options.ignore_merge_commits`` is now set to ``true`` by default. The feature to
  ignore squash commits was introduced in ``v9.18.0`` and was originally set to ``false`` to
  prevent unexpected results on a non-breaking update. The ignore merge commits feature prevents
  additional unnecessary processing on a commit message that likely will not match a commit message
  syntax. Most merge commits are syntactically pre-defined by Git or Remote Version Control System
  (ex. GitHub, etc.) and do not follow a commit convention (nor should they). The larger issue with
  merge commits is that they ultimately are a full copy of all the changes that were previously
  created and committed. The merge commit itself ensures that the previous commit tree is
  maintained in history, therefore the commit message always exists. If merge commits are parsed,
  it generally creates duplicate messages that will end up in your changelog, which is less than
  desired in most cases. If you have previously used the ``changelog.exclude_commit_patterns``
  functionality to ignore merge commit messages then you will want this setting set to ``true`` to
  improve parsing speed. You can also now remove the merge commit exclude pattern from the list as
  well to improve parsing speed. If this functionality is not desired, you will need to update your
  configuration to change the new setting to ``false``.

* **parser-conventional, parser-emoji, parser-scipy**: The configuration setting
  ``commit_parser_options.parse_squash_commits`` is now set to ``true`` by default. The feature to
  parse squash commits was introduced in ``v9.17.0`` and was originally set to ``false`` to prevent
  unexpected results on a non-breaking update. The parse squash commits feature attempts to find
  additional commits of the same commit type within the body of a single commit message. When
  squash commits are found, Python Semantic Release will separate out each commit into its own
  artificial commit object and parse them individually. This potentially can change the resulting
  version bump if a larger bump was detected within the squashed components. It also allows for the
  changelog and release notes to separately order and display each commit as originally written. If
  this is not desired, you will need to update your configuration to change the new setting to
  ``false``.

.. _#733: https://github.com/python-semantic-release/python-semantic-release/issues/733
.. _080e4bc: https://github.com/python-semantic-release/python-semantic-release/commit/080e4bcb14048a2dd10445546a7ee3159b3ab85c
.. _0bed906: https://github.com/python-semantic-release/python-semantic-release/commit/0bed9069df67ae806ad0a15f8434ac4efcc6ba31
.. _0e114c3: https://github.com/python-semantic-release/python-semantic-release/commit/0e114c3458a24b87bfd2d6b0cd3f5cfdc9497084
.. _16465f1: https://github.com/python-semantic-release/python-semantic-release/commit/16465f133386b09627d311727a6f8d24dd8f174f
.. _203d29d: https://github.com/python-semantic-release/python-semantic-release/commit/203d29d9d6b8e862eabe2f99dbd27eabf04e75e2
.. _3cfee76: https://github.com/python-semantic-release/python-semantic-release/commit/3cfee76032662bda6fbdd7e2585193213e4f9da2
.. _4aa6a6e: https://github.com/python-semantic-release/python-semantic-release/commit/4aa6a6edbff75889e09f32f7cba52cb90c9fb626
.. _4e52f4b: https://github.com/python-semantic-release/python-semantic-release/commit/4e52f4bba46e96a4762f97d306f15ae52c5cea1b
.. _4ea92ec: https://github.com/python-semantic-release/python-semantic-release/commit/4ea92ec34dcd45d8cbab24e38e55289617b2d728
.. _514a922: https://github.com/python-semantic-release/python-semantic-release/commit/514a922fa87721e2500062dcae841bedd84dc1fe
.. _5310d0c: https://github.com/python-semantic-release/python-semantic-release/commit/5310d0c700840538f27874394b9964bf09cd69b1
.. _58308e3: https://github.com/python-semantic-release/python-semantic-release/commit/58308e31bb6306aac3a985af01eb779dc923d3f0
.. _59bf084: https://github.com/python-semantic-release/python-semantic-release/commit/59bf08440a15269afaac81d78dd03ee418f9fd6b
.. _5fb02ab: https://github.com/python-semantic-release/python-semantic-release/commit/5fb02ab6e3b8278ecbf92ed35083ffb595bc19b8
.. _634fffe: https://github.com/python-semantic-release/python-semantic-release/commit/634fffea29157e9b6305b21802c78ac245454265
.. _67b2ae0: https://github.com/python-semantic-release/python-semantic-release/commit/67b2ae0050cce540a4126fe280cca6dc4bcf5d3f
.. _6aad7f1: https://github.com/python-semantic-release/python-semantic-release/commit/6aad7f17e64fb4717ddd7a9e94d2a730be6a3bd9
.. _6cd0fbe: https://github.com/python-semantic-release/python-semantic-release/commit/6cd0fbeb44e16d394c210216c7099afa51f5a4a3
.. _6fcdc99: https://github.com/python-semantic-release/python-semantic-release/commit/6fcdc99e9462b1186ea9488fc14e4e18f8c7fdb3
.. _731466f: https://github.com/python-semantic-release/python-semantic-release/commit/731466fec4e06fe71f6c4addd4ae2ec2182ae9c1
.. _7d39e76: https://github.com/python-semantic-release/python-semantic-release/commit/7d39e7675f859463b54751d59957b869d5d8395c
.. _7e8dc13: https://github.com/python-semantic-release/python-semantic-release/commit/7e8dc13c0b048a95d01f7aecfbe4eeedcddec9a4
.. _8a51525: https://github.com/python-semantic-release/python-semantic-release/commit/8a5152573b9175f01be06d0c4531ea0ca4de8dd4
.. _8bed5bc: https://github.com/python-semantic-release/python-semantic-release/commit/8bed5bcca4a5759af0e3fb24eadf14aa4e4f53c9
.. _a082896: https://github.com/python-semantic-release/python-semantic-release/commit/a08289693085153effdafe3c6ff235a1777bb1fa
.. _a5f5e04: https://github.com/python-semantic-release/python-semantic-release/commit/a5f5e042ae9af909ee9e3ddf57c78adbc92ce378
.. _b1bb0e5: https://github.com/python-semantic-release/python-semantic-release/commit/b1bb0e55910715754eebef6cb5b21ebed5ee8d68
.. _b271cbb: https://github.com/python-semantic-release/python-semantic-release/commit/b271cbb2d3e8b86d07d1358b2e7424ccff6ae186
.. _b6307cb: https://github.com/python-semantic-release/python-semantic-release/commit/b6307cb649043bbcc7ad9f15ac5ac6728914f443
.. _b757603: https://github.com/python-semantic-release/python-semantic-release/commit/b757603e77ebe26d8a14758d78fd21163a9059b2
.. _bd3e7bf: https://github.com/python-semantic-release/python-semantic-release/commit/bd3e7bfa86d53a03f03ac419399847712c523b02
.. _c4d45ec: https://github.com/python-semantic-release/python-semantic-release/commit/c4d45ec46dfa81f645c25ea18ffffe9635922603
.. _c6b6eab: https://github.com/python-semantic-release/python-semantic-release/commit/c6b6eabbfe100d2c741620eb3fa12a382531fa94
.. _d4f128e: https://github.com/python-semantic-release/python-semantic-release/commit/d4f128e75e33256c0163fbb475c7c41e18f65147
.. _da4140f: https://github.com/python-semantic-release/python-semantic-release/commit/da4140f3e3a2ed03c05064f35561b4584f517105
.. _e7ac155: https://github.com/python-semantic-release/python-semantic-release/commit/e7ac155a91fc2e735d3cbf9b66fb4e5ff40a1466
.. _eed63fa: https://github.com/python-semantic-release/python-semantic-release/commit/eed63fa9f6e762f55700fc85ef3ebdc0d3144f21
.. _fb3da27: https://github.com/python-semantic-release/python-semantic-release/commit/fb3da27650ff15bcdb3b7badc919bd8a9a73238d
.. _PR#1244: https://github.com/python-semantic-release/python-semantic-release/pull/1244
.. _PR#1245: https://github.com/python-semantic-release/python-semantic-release/pull/1245


.. _changelog-v9.21.1:

v9.21.1 (2025-05-05)
====================

🪲 Bug Fixes
------------

* **changelog-filters**: Fixes url resolution when prefix & path share letters, closes `#1204`_
  (`PR#1239`_, `f61f8a3`_)

📖 Documentation
----------------

* **github-actions**: Expound on monorepo example to include publishing actions (`PR#1229`_,
  `550e85f`_)

⚙️ Build System
----------------

* **deps**: Bump ``rich`` dependency from ``13.0`` to ``14.0`` (`PR#1224`_, `691536e`_)

* **deps**: Expand ``python-gitlab`` dependency to include ``v5.0.0`` (`PR#1228`_, `a0cd1be`_)

.. _#1204: https://github.com/python-semantic-release/python-semantic-release/issues/1204
.. _550e85f: https://github.com/python-semantic-release/python-semantic-release/commit/550e85f5ec2695d5aa680014127846d58c680e31
.. _691536e: https://github.com/python-semantic-release/python-semantic-release/commit/691536e98f311d0fc6d29a72c41ce5a65f1f4b6c
.. _a0cd1be: https://github.com/python-semantic-release/python-semantic-release/commit/a0cd1be4e3aa283cbdc544785e5f895c8391dfb8
.. _f61f8a3: https://github.com/python-semantic-release/python-semantic-release/commit/f61f8a38a1a3f44a7a56cf9dcb7dde748f90ca1e
.. _PR#1224: https://github.com/python-semantic-release/python-semantic-release/pull/1224
.. _PR#1228: https://github.com/python-semantic-release/python-semantic-release/pull/1228
.. _PR#1229: https://github.com/python-semantic-release/python-semantic-release/pull/1229
.. _PR#1239: https://github.com/python-semantic-release/python-semantic-release/pull/1239


.. _changelog-v9.21.0:

v9.21.0 (2025-02-23)
====================

✨ Features
-----------

* Add package name variant, ``python-semantic-release``, project script, closes `#1195`_
  (`PR#1199`_, `1ac97bc`_)

📖 Documentation
----------------

* **github-actions**: Update example workflow to handle rapid merges (`PR#1200`_, `1a4116a`_)

.. _#1195: https://github.com/python-semantic-release/python-semantic-release/issues/1195
.. _1a4116a: https://github.com/python-semantic-release/python-semantic-release/commit/1a4116af4b999144998cf94cf84c9c23ff2e352f
.. _1ac97bc: https://github.com/python-semantic-release/python-semantic-release/commit/1ac97bc74c69ce61cec98242c19bf8adc1d37fb9
.. _PR#1199: https://github.com/python-semantic-release/python-semantic-release/pull/1199
.. _PR#1200: https://github.com/python-semantic-release/python-semantic-release/pull/1200


.. _changelog-v9.20.0:

v9.20.0 (2025-02-17)
====================

✨ Features
-----------

* **cmd-version**: Enable stamping of tag formatted versions into files, closes `#846`_ (`PR#1190`_,
  `8906d8e`_)

* **cmd-version**: Extend ``version_variables`` to stamp versions with ``@`` symbol separator,
  closes `#1156`_ (`PR#1185`_, `23f69b6`_)

📖 Documentation
----------------

* **configuration**: Add usage information for tag format version stamping (`PR#1190`_, `8906d8e`_)

* **configuration**: Clarify ``version_variables`` config description & ``@`` separator usage
  (`PR#1185`_, `23f69b6`_)

⚙️ Build System
----------------

* **deps**: Add ``deprecated~=1.2`` for deprecation notices & sphinx documentation (`PR#1190`_,
  `8906d8e`_)

.. _#1156: https://github.com/python-semantic-release/python-semantic-release/issues/1156
.. _#846: https://github.com/python-semantic-release/python-semantic-release/issues/846
.. _23f69b6: https://github.com/python-semantic-release/python-semantic-release/commit/23f69b6ac206d111b1e566367f9b2f033df5c87a
.. _8906d8e: https://github.com/python-semantic-release/python-semantic-release/commit/8906d8e70467af1489d797ec8cb09b1f95e5d409
.. _PR#1185: https://github.com/python-semantic-release/python-semantic-release/pull/1185
.. _PR#1190: https://github.com/python-semantic-release/python-semantic-release/pull/1190


.. _changelog-v9.19.1:

v9.19.1 (2025-02-11)
====================

🪲 Bug Fixes
------------

* **changelog**: Standardize heading format for across all version sections (`PR#1182`_, `81f9e80`_)

* **changelog-md**: Standardize heading format for extra release information (`PR#1182`_,
  `81f9e80`_)

* **changelog-rst**: Standardize heading format for extra release information (`PR#1182`_,
  `81f9e80`_)

* **config**: Handle invalid ``commit_parser`` type gracefully (`PR#1180`_, `903c8ba`_)

* **release-notes**: Standardize heading format for extra release information (`PR#1182`_,
  `81f9e80`_)

📖 Documentation
----------------

* Fix spelling errors & inaccurate descriptions (`55d4a05`_)

* **automatic-releases**: Declutter the table of contents for automatic release guides (`e8343ee`_)

* **commit-parsing**: Update reference to section name of additional release info (`PR#1182`_,
  `81f9e80`_)

.. _55d4a05: https://github.com/python-semantic-release/python-semantic-release/commit/55d4a05ff56321cf9874f8f302fbe7e5163ad4f7
.. _81f9e80: https://github.com/python-semantic-release/python-semantic-release/commit/81f9e80c3df185ef5e553e024b903ce153e14304
.. _903c8ba: https://github.com/python-semantic-release/python-semantic-release/commit/903c8ba68d797f7cd9e5025c9a3a3ad471c805ae
.. _e8343ee: https://github.com/python-semantic-release/python-semantic-release/commit/e8343eeb38d3b4e18953ac0f97538df396d22b76
.. _PR#1180: https://github.com/python-semantic-release/python-semantic-release/pull/1180
.. _PR#1182: https://github.com/python-semantic-release/python-semantic-release/pull/1182


.. _changelog-v9.19.0:

v9.19.0 (2025-02-10)
====================

✨ Features
-----------

* **parser-conventional**: Add official ``conventional-commits`` parser (`PR#1177`_, `27ddf84`_)

📖 Documentation
----------------

* Update references to Angular parser to Conventional Commit Parser (`PR#1177`_, `27ddf84`_)

💡 Additional Release Information
---------------------------------

* **parser-conventional**: The 'angular' commit parser has been renamed to 'conventional' to match
  the official conventional-commits standard for which the 'angular' parser has evolved into. Please
  update your configurations to specify 'conventional' as the 'commit_parser' value in place of
  'angular'. The 'angular' type will be removed in v11.

.. _27ddf84: https://github.com/python-semantic-release/python-semantic-release/commit/27ddf840f8c812361c60bac9cf0b110d401f33d6
.. _PR#1177: https://github.com/python-semantic-release/python-semantic-release/pull/1177


.. _changelog-v9.18.1:

v9.18.1 (2025-02-08)
====================

🪲 Bug Fixes
------------

* **config**: Refactors default token resolution to prevent pre-mature insecure URL error, closes
  `#1074`_, `#1169`_ (`PR#1173`_, `37db258`_)

.. _#1074: https://github.com/python-semantic-release/python-semantic-release/issues/1074
.. _#1169: https://github.com/python-semantic-release/python-semantic-release/issues/1169
.. _37db258: https://github.com/python-semantic-release/python-semantic-release/commit/37db2581620ad02e66716a4b3b365aa28abe65f8
.. _PR#1173: https://github.com/python-semantic-release/python-semantic-release/pull/1173


.. _changelog-v9.18.0:

v9.18.0 (2025-02-06)
====================

✨ Features
-----------

* Add ``create_release_url`` & ``format_w_official_vcs_name`` filters (`PR#1161`_, `f853cf0`_)

* **changelog**: Add ``create_pypi_url`` filter to jinja template render context (`PR#1160`_,
  `45d49c3`_)

* **changelog**: Add additional release info to changeling from commit ``NOTICE``'s (`PR#1166`_,
  `834ce32`_)

* **changelog-md**: Add additional release info section to default markdown template, closes `#223`_
  (`PR#1166`_, `834ce32`_)

* **changelog-rst**: Add additional release info section to default ReStructuredText template,
  closes `#223`_ (`PR#1166`_, `834ce32`_)

* **commit-parser**: Enable parsers to identify additional release notices from commit msgs
  (`PR#1166`_, `834ce32`_)

* **parser-angular**: Add a ``ignore_merge_commits`` option to discard parsing merge commits
  (`PR#1164`_, `463e43b`_)

* **parser-angular**: Add functionality to parse out ``NOTICE:`` prefixed statements in commits,
  closes `#223`_ (`PR#1166`_, `834ce32`_)

* **parser-emoji**: Add a ``ignore_merge_commits`` option to discard parsing merge commits
  (`PR#1164`_, `463e43b`_)

* **parser-emoji**: Add functionality to parse out ``NOTICE:`` prefixed statements in commits,
  closes `#223`_ (`PR#1166`_, `834ce32`_)

* **parsers**: Add option ``ignore_merge_commits`` to discard parsing merge commits (`PR#1164`_,
  `463e43b`_)

* **release-notes**: Add license information to default release notes template, closes `#228`_
  (`PR#1167`_, `41172c1`_)

* **vcs-bitbucket**: Add ``format_w_official_vcs_name`` filter function (`PR#1161`_, `f853cf0`_)

* **vcs-gitea**: Add ``create_release_url`` & ``format_w_official_vcs_name`` filter functions
  (`PR#1161`_, `f853cf0`_)

* **vcs-github**: Add ``create_release_url`` & ``format_w_official_vcs_name`` filter functions
  (`PR#1161`_, `f853cf0`_)

* **vcs-gitlab**: Add ``create_release_url`` & ``format_w_official_vcs_name`` filter functions
  (`PR#1161`_, `f853cf0`_)

🪲 Bug Fixes
------------

* Refactor parsing compatibility function to support older custom parsers (`PR#1165`_, `cf340c5`_)

* **changelog**: Fix parsing compatibility w/ custom parsers, closes `#1162`_ (`PR#1165`_,
  `cf340c5`_)

* **changelog-templates**: Adjust default templates to avoid empty version sections (`PR#1164`_,
  `463e43b`_)

* **parser-angular**: Adjust parser to prevent empty message extractions (`PR#1166`_, `834ce32`_)

* **parser-emoji**: Adjust parser to prevent empty message extractions (`PR#1166`_, `834ce32`_)

* **version**: Fix parsing compatibility w/ custom parsers, closes `#1162`_ (`PR#1165`_, `cf340c5`_)

📖 Documentation
----------------

* **changelog**: Add formatted changelog into hosted documentation (`PR#1155`_, `2f18a6d`_)

* **changelog-templates**: Add description for new ``create_pypi_url`` filter function (`PR#1160`_,
  `45d49c3`_)

* **changelog-templates**: Add details about license specification in the release notes (`PR#1167`_,
  `41172c1`_)

* **changelog-templates**: Define ``create_release_url`` & ``format_w_official_vcs_name`` filters
  (`PR#1161`_, `f853cf0`_)

* **changelog-templates**: Document special separate sections of commit descriptions (`ebb4c67`_)

* **commit-parsing**: Document new release notice footer detection feature of built-in parsers
  (`cd14e92`_)

.. _#1162: https://github.com/python-semantic-release/python-semantic-release/issues/1162
.. _#223: https://github.com/python-semantic-release/python-semantic-release/issues/223
.. _#228: https://github.com/python-semantic-release/python-semantic-release/issues/228
.. _2f18a6d: https://github.com/python-semantic-release/python-semantic-release/commit/2f18a6debfa6ef3afcc5611a3e09262998f2d4bf
.. _41172c1: https://github.com/python-semantic-release/python-semantic-release/commit/41172c1272a402e94e3c68571d013cbdcb5b9023
.. _45d49c3: https://github.com/python-semantic-release/python-semantic-release/commit/45d49c3da75a7f08c86fc9bab5d232a9b37d9e72
.. _463e43b: https://github.com/python-semantic-release/python-semantic-release/commit/463e43b897ee80dfaf7ce9d88d22ea8e652bcf55
.. _834ce32: https://github.com/python-semantic-release/python-semantic-release/commit/834ce323007c58229abf115ef2016a348de9ee66
.. _cd14e92: https://github.com/python-semantic-release/python-semantic-release/commit/cd14e9209d4e54f0876e737d1f802dded294a48c
.. _cf340c5: https://github.com/python-semantic-release/python-semantic-release/commit/cf340c5256dea58aedad71a6bdf50b17eee53d2f
.. _ebb4c67: https://github.com/python-semantic-release/python-semantic-release/commit/ebb4c67d46b86fdf79e32edf744a2ec2b09d6a93
.. _f853cf0: https://github.com/python-semantic-release/python-semantic-release/commit/f853cf059b3323d7888b06fde09142184e7964e8
.. _PR#1155: https://github.com/python-semantic-release/python-semantic-release/pull/1155
.. _PR#1160: https://github.com/python-semantic-release/python-semantic-release/pull/1160
.. _PR#1161: https://github.com/python-semantic-release/python-semantic-release/pull/1161
.. _PR#1164: https://github.com/python-semantic-release/python-semantic-release/pull/1164
.. _PR#1165: https://github.com/python-semantic-release/python-semantic-release/pull/1165
.. _PR#1166: https://github.com/python-semantic-release/python-semantic-release/pull/1166
.. _PR#1167: https://github.com/python-semantic-release/python-semantic-release/pull/1167


.. _changelog-v9.17.0:

v9.17.0 (2025-01-26)
====================

✨ Features
-----------

* **changelog**: Add ``sort_numerically`` filter function to template environment (`PR#1146`_,
  `7792388`_)

* **changelog**: Parse squashed commits individually (`PR#1112`_, `cf785ca`_)

* **config**: Extend support of remote urls aliased using git ``insteadOf`` configurations, closes
  `#1150`_ (`PR#1151`_, `4045037`_)

* **parsers**: Parse squashed commits individually (`PR#1112`_, `cf785ca`_)

* **parser-angular**: Apply PR/MR numbers to all parsed commits from a squash merge (`PR#1112`_,
  `cf785ca`_)

* **parser-angular**: Upgrade angular parser to parse squashed commits individually, closes `#1085`_
  (`PR#1112`_, `cf785ca`_)

* **parser-emoji**: Add functionality to interpret scopes from gitmoji commit messages (`PR#1112`_,
  `cf785ca`_)

* **parser-emoji**: Upgrade emoji parser to parse squashed commits individually (`PR#1112`_,
  `cf785ca`_)

* **version**: Parse squashed commits individually (`PR#1112`_, `cf785ca`_)

🪲 Bug Fixes
------------

* **github-action**: Disable writing python bytecode in action execution (`PR#1152`_, `315ae21`_)

⚡ Performance Improvements
---------------------------

* **logging**: Remove irrelevant debug logging statements (`PR#1147`_, `f1ef4ec`_)

📖 Documentation
----------------

* **changelog-templates**: Add description for new ``sort_numerically`` filter function (`PR#1146`_,
  `7792388`_)

* **commit-parsing**: Add description for squash commit evaluation option of default parsers
  (`PR#1112`_, `cf785ca`_)

* **configuration**: Update the ``commit_parser_options`` setting description (`PR#1112`_,
  `cf785ca`_)

.. _#1085: https://github.com/python-semantic-release/python-semantic-release/issues/1085
.. _#1150: https://github.com/python-semantic-release/python-semantic-release/issues/1150
.. _315ae21: https://github.com/python-semantic-release/python-semantic-release/commit/315ae2176e211b00b13374560d81e127a3065d1a
.. _4045037: https://github.com/python-semantic-release/python-semantic-release/commit/40450375c7951dafddb09bef8001db7180d95f3a
.. _7792388: https://github.com/python-semantic-release/python-semantic-release/commit/77923885c585171e8888aacde989837ecbabf3fc
.. _cf785ca: https://github.com/python-semantic-release/python-semantic-release/commit/cf785ca79a49eb4ee95c148e0ae6a19e230e915c
.. _f1ef4ec: https://github.com/python-semantic-release/python-semantic-release/commit/f1ef4ecf5f22684a870b958f87d1ca2650e612db
.. _PR#1112: https://github.com/python-semantic-release/python-semantic-release/pull/1112
.. _PR#1146: https://github.com/python-semantic-release/python-semantic-release/pull/1146
.. _PR#1147: https://github.com/python-semantic-release/python-semantic-release/pull/1147
.. _PR#1151: https://github.com/python-semantic-release/python-semantic-release/pull/1151
.. _PR#1152: https://github.com/python-semantic-release/python-semantic-release/pull/1152


.. _changelog-v9.16.1:

v9.16.1 (2025-01-12)
====================

🪲 Bug Fixes
------------

* **parser-custom**: Handle relative parent directory paths to module file better (`PR#1142`_,
  `c4056fc`_)

📖 Documentation
----------------

* **github-actions**: Update PSR versions in github workflow examples (`PR#1140`_, `9bdd626`_)

.. _9bdd626: https://github.com/python-semantic-release/python-semantic-release/commit/9bdd626bf8f8359d35725cebe803931063260cac
.. _c4056fc: https://github.com/python-semantic-release/python-semantic-release/commit/c4056fc2e1fb3bddb78728793716ac6fb8522b1a
.. _PR#1140: https://github.com/python-semantic-release/python-semantic-release/pull/1140
.. _PR#1142: https://github.com/python-semantic-release/python-semantic-release/pull/1142


.. _changelog-v9.16.0:

v9.16.0 (2025-01-12)
====================

✨ Features
-----------

* **config**: Expand dynamic parser import to handle a filepath to module (`PR#1135`_, `0418fd8`_)

🪲 Bug Fixes
------------

* **changelog**: Fixes PSR release commit exclusions for customized commit messages (`PR#1139`_,
  `f9a2078`_)

* **cmd-version**: Fixes ``--print-tag`` result to match configured tag format (`PR#1134`_,
  `a990aa7`_)

* **cmd-version**: Fixes tag format on default version when force bump for initial release, closes
  `#1137`_ (`PR#1138`_, `007fd00`_)

* **config-changelog**: Validate ``changelog.exclude_commit_patterns`` on config load (`PR#1139`_,
  `f9a2078`_)

📖 Documentation
----------------

* **commit-parsing**: Add the new custom parser import spec description for direct path imports,
  closes `#687`_ (`PR#1135`_, `0418fd8`_)

* **configuration**: Adjust ``commit_parser`` option definition for direct path imports (`PR#1135`_,
  `0418fd8`_)

.. _#687: https://github.com/python-semantic-release/python-semantic-release/issues/687
.. _#1137: https://github.com/python-semantic-release/python-semantic-release/issues/1137
.. _007fd00: https://github.com/python-semantic-release/python-semantic-release/commit/007fd00a3945ed211ece4baab0b79ad93dc018f5
.. _0418fd8: https://github.com/python-semantic-release/python-semantic-release/commit/0418fd8d27aac14925aafa50912e751e3aeff2f7
.. _a990aa7: https://github.com/python-semantic-release/python-semantic-release/commit/a990aa7ab0a9d52d295c04d54d20e9c9f2db2ca5
.. _f9a2078: https://github.com/python-semantic-release/python-semantic-release/commit/f9a20787437d0f26074fe2121bf0a29576a96df0
.. _PR#1134: https://github.com/python-semantic-release/python-semantic-release/pull/1134
.. _PR#1135: https://github.com/python-semantic-release/python-semantic-release/pull/1135
.. _PR#1138: https://github.com/python-semantic-release/python-semantic-release/pull/1138
.. _PR#1139: https://github.com/python-semantic-release/python-semantic-release/pull/1139


.. _changelog-v9.15.2:

v9.15.2 (2024-12-16)
====================

🪲 Bug Fixes
------------

* **changelog**: Ensures user rendered files are trimmed to end with a single newline (`PR#1118`_,
  `6dfbbb0`_)

* **cli**: Add error message of how to gather full error output (`PR#1116`_, `ba85532`_)

* **cmd-version**: Enable maintenance prereleases (`PR#864`_, `b88108e`_)

* **cmd-version**: Fix handling of multiple prerelease token variants & git flow merges (`PR#1120`_,
  `8784b9a`_)

* **cmd-version**: Fix version determination algorithm to capture commits across merged branches
  (`PR#1120`_, `8784b9a`_)

* **cmd-version**: Forces tag timestamp to be same time as release commit (`PR#1117`_, `7898b11`_)

* **cmd-version**: Handle multiple prerelease token variants properly, closes `#789`_ (`PR#1120`_,
  `8784b9a`_)

* **config**: Ensure default config loads on network mounted windows environments, closes `#1123`_
  (`PR#1124`_, `a64cbc9`_)

* **version**: Remove some excessive log msgs from debug to silly level (`PR#1120`_, `8784b9a`_)

* **version-bump**: Increment based on current commit's history only, closes `#861`_ (`PR#864`_,
  `b88108e`_)

⚡ Performance Improvements
---------------------------

* **cmd-version**: Refactor version determination algorithm for accuracy & speed (`PR#1120`_,
  `8784b9a`_)

.. _#789: https://github.com/python-semantic-release/python-semantic-release/issues/789
.. _#861: https://github.com/python-semantic-release/python-semantic-release/issues/861
.. _#1123: https://github.com/python-semantic-release/python-semantic-release/issues/1123
.. _6dfbbb0: https://github.com/python-semantic-release/python-semantic-release/commit/6dfbbb0371aef6b125cbcbf89b80dc343ed97360
.. _7898b11: https://github.com/python-semantic-release/python-semantic-release/commit/7898b1185fc1ad10e96bf3f5e48d9473b45d2b51
.. _8784b9a: https://github.com/python-semantic-release/python-semantic-release/commit/8784b9ad4bc59384f855b5af8f1b8fb294397595
.. _a64cbc9: https://github.com/python-semantic-release/python-semantic-release/commit/a64cbc96c110e32f1ec5d1a7b61e950472491b87
.. _b88108e: https://github.com/python-semantic-release/python-semantic-release/commit/b88108e189e1894e36ae4fdf8ad8a382b5c8c90a
.. _ba85532: https://github.com/python-semantic-release/python-semantic-release/commit/ba85532ddd6fcf1a2205f7ce0b88ea5be76cb621
.. _PR#864: https://github.com/python-semantic-release/python-semantic-release/pull/864
.. _PR#1116: https://github.com/python-semantic-release/python-semantic-release/pull/1116
.. _PR#1117: https://github.com/python-semantic-release/python-semantic-release/pull/1117
.. _PR#1118: https://github.com/python-semantic-release/python-semantic-release/pull/1118
.. _PR#1120: https://github.com/python-semantic-release/python-semantic-release/pull/1120
.. _PR#1124: https://github.com/python-semantic-release/python-semantic-release/pull/1124


.. _changelog-v9.15.1:

v9.15.1 (2024-12-03)
====================

🪲 Bug Fixes
------------

* **changelog-md**: Fix commit sort of breaking descriptions section (`75b342e`_)

* **parser-angular**: Ensure issues are sorted by numeric value rather than text sorted (`3858add`_)

* **parser-emoji**: Ensure issues are sorted by numeric value rather than text sorted (`7b8d2d9`_)

.. _3858add: https://github.com/python-semantic-release/python-semantic-release/commit/3858add582fe758dc2ae967d0cd051d43418ecd0
.. _75b342e: https://github.com/python-semantic-release/python-semantic-release/commit/75b342e6259412cb82d8b7663e5ee4536d14f407
.. _7b8d2d9: https://github.com/python-semantic-release/python-semantic-release/commit/7b8d2d92e135ab46d1be477073ccccc8c576f121


.. _changelog-v9.15.0:

v9.15.0 (2024-12-02)
====================

✨ Features
-----------

* **changelog-md**: Add a breaking changes section to default Markdown template, closes `#244`_
  (`PR#1110`_, `4fde30e`_)

* **changelog-md**: Alphabetize breaking change descriptions in markdown changelog template
  (`PR#1110`_, `4fde30e`_)

* **changelog-md**: Alphabetize commit summaries & scopes in markdown changelog template
  (`PR#1111`_, `8327068`_)

* **changelog-rst**: Add a breaking changes section to default reStructuredText template, closes
  `#244`_ (`PR#1110`_, `4fde30e`_)

* **changelog-rst**: Alphabetize breaking change descriptions in ReStructuredText template
  (`PR#1110`_, `4fde30e`_)

* **changelog-rst**: Alphabetize commit summaries & scopes in ReStructuredText template (`PR#1111`_,
  `8327068`_)

* **commit-parser**: Enable parsers to flag commit to be ignored for changelog, closes `#778`_
  (`PR#1108`_, `0cc668c`_)

* **default-changelog**: Add a separate formatted breaking changes section, closes `#244`_
  (`PR#1110`_, `4fde30e`_)

* **default-changelog**: Alphabetize commit summaries & scopes in change sections (`PR#1111`_,
  `8327068`_)

* **parsers**: Add ``other_allowed_tags`` option for commit parser options (`PR#1109`_, `f90b8dc`_)

* **parsers**: Enable parsers to identify linked issues on a commit (`PR#1109`_, `f90b8dc`_)

* **parser-angular**: Automatically parse angular issue footers from commit messages (`PR#1109`_,
  `f90b8dc`_)

* **parser-custom**: Enable custom parsers to identify linked issues on a commit (`PR#1109`_,
  `f90b8dc`_)

* **parser-emoji**: Parse issue reference footers from commit messages (`PR#1109`_, `f90b8dc`_)

* **release-notes**: Add tag comparison link to release notes when supported (`PR#1107`_,
  `9073344`_)

🪲 Bug Fixes
------------

* **cmd-version**: Ensure release utilizes a timezone aware datetime (`ca817ed`_)

* **default-changelog**: Alphabetically sort commit descriptions in version type sections
  (`bdaaf5a`_)

* **util**: Prevent git footers from being collapsed during parse (`PR#1109`_, `f90b8dc`_)

📖 Documentation
----------------

* **api-parsers**: Add option documentation to parser options (`PR#1109`_, `f90b8dc`_)

* **changelog-templates**: Update examples using new ``commit.linked_issues`` attribute (`PR#1109`_,
  `f90b8dc`_)

* **commit-parsing**: Improve & expand commit parsing w/ parser descriptions (`PR#1109`_,
  `f90b8dc`_)

.. _#244: https://github.com/python-semantic-release/python-semantic-release/issues/244
.. _#778: https://github.com/python-semantic-release/python-semantic-release/issues/778
.. _0cc668c: https://github.com/python-semantic-release/python-semantic-release/commit/0cc668c36490401dff26bb2c3141f6120a2c47d0
.. _4fde30e: https://github.com/python-semantic-release/python-semantic-release/commit/4fde30e0936ecd186e448f1caf18d9ba377c55ad
.. _8327068: https://github.com/python-semantic-release/python-semantic-release/commit/83270683fd02b626ed32179d94fa1e3c7175d113
.. _9073344: https://github.com/python-semantic-release/python-semantic-release/commit/9073344164294360843ef5522e7e4c529985984d
.. _bdaaf5a: https://github.com/python-semantic-release/python-semantic-release/commit/bdaaf5a460ca77edc40070ee799430122132dc45
.. _ca817ed: https://github.com/python-semantic-release/python-semantic-release/commit/ca817ed9024cf84b306a047675534cc36dc116b2
.. _f90b8dc: https://github.com/python-semantic-release/python-semantic-release/commit/f90b8dc6ce9f112ef2c98539d155f9de24398301
.. _PR#1107: https://github.com/python-semantic-release/python-semantic-release/pull/1107
.. _PR#1108: https://github.com/python-semantic-release/python-semantic-release/pull/1108
.. _PR#1109: https://github.com/python-semantic-release/python-semantic-release/pull/1109
.. _PR#1110: https://github.com/python-semantic-release/python-semantic-release/pull/1110
.. _PR#1111: https://github.com/python-semantic-release/python-semantic-release/pull/1111


.. _changelog-v9.14.0:

v9.14.0 (2024-11-11)
====================

✨ Features
-----------

* **changelog**: Add md to rst conversion for markdown inline links (`cb2af1f`_)

* **changelog**: Define first release w/o change descriptions for default MD template (`fa89dec`_)

* **changelog**: Define first release w/o change descriptions for default RST template (`e30c94b`_)

* **changelog**: Prefix scopes on commit descriptions in default template (`PR#1093`_, `560fd2c`_)

* **changelog-md**: Add markdown inline link format macro (`c6d8211`_)

* **changelog-md**: Prefix scopes on commit descriptions in Markdown changelog template (`PR#1093`_,
  `560fd2c`_)

* **changelog-rst**: Prefix scopes on commit descriptions in ReStructuredText template (`PR#1093`_,
  `560fd2c`_)

* **configuration**: Add ``changelog.default_templates.mask_initial_release`` option (`595a70b`_)

* **context**: Add ``mask_initial_release`` setting to changelog context (`6f2ee39`_)

* **release-notes**: Define first release w/o change descriptions in default template (`83167a3`_)

🪲 Bug Fixes
------------

* **release-notes**: Override default word-wrap to non-wrap for in default template (`99ab99b`_)

📖 Documentation
----------------

* **changelog-templates**: Document new ``mask_initial_release`` changelog context variable
  (`f294957`_)

* **configuration**: Document new ``mask_initial_release`` option usage & effect (`3cabcdc`_)

* **homepage**: Fix reference to new ci workflow for test status badge (`6760069`_)

.. _3cabcdc: https://github.com/python-semantic-release/python-semantic-release/commit/3cabcdcd9473e008604e74cc2d304595317e921d
.. _560fd2c: https://github.com/python-semantic-release/python-semantic-release/commit/560fd2c0d58c97318377cb83af899a336d24cfcc
.. _595a70b: https://github.com/python-semantic-release/python-semantic-release/commit/595a70bcbc8fea1f8ccf6c5069c41c35ec4efb8d
.. _6760069: https://github.com/python-semantic-release/python-semantic-release/commit/6760069e7489f50635beb5aedbbeb2cb82b7c584
.. _6f2ee39: https://github.com/python-semantic-release/python-semantic-release/commit/6f2ee39414b3cf75c0b67dee4db0146bbc1041bb
.. _83167a3: https://github.com/python-semantic-release/python-semantic-release/commit/83167a3dcceb7db16b790e1b0efd5fc75fee8942
.. _99ab99b: https://github.com/python-semantic-release/python-semantic-release/commit/99ab99bb0ba350ca1913a2bde9696f4242278972
.. _c6d8211: https://github.com/python-semantic-release/python-semantic-release/commit/c6d8211c859442df17cb41d2ff19fdb7a81cdb76
.. _cb2af1f: https://github.com/python-semantic-release/python-semantic-release/commit/cb2af1f17cf6c8ae037c6cd8bb8b4d9c019bb47e
.. _e30c94b: https://github.com/python-semantic-release/python-semantic-release/commit/e30c94bffe62b42e8dc6ed4fed6260e57b4d532b
.. _f294957: https://github.com/python-semantic-release/python-semantic-release/commit/f2949577dfb2dbf9c2ac952c1bbcc4ab84da080b
.. _fa89dec: https://github.com/python-semantic-release/python-semantic-release/commit/fa89dec239efbae7544b187f624a998fa9ecc309
.. _PR#1093: https://github.com/python-semantic-release/python-semantic-release/pull/1093


.. _changelog-v9.13.0:

v9.13.0 (2024-11-10)
====================

✨ Features
-----------

* **changelog**: Add PR/MR url linking to default Markdown changelog, closes `#924`_, `#953`_
  (`cd8d131`_)

* **changelog**: Add PR/MR url linking to default reStructuredText template, closes `#924`_, `#953`_
  (`5f018d6`_)

* **parsed-commit**: Add linked merge requests list to the ``ParsedCommit`` object (`9a91062`_)

* **parser-angular**: Automatically parse PR/MR numbers from subject lines in commits (`2ac798f`_)

* **parser-emoji**: Automatically parse PR/MR numbers from subject lines in commits (`bca9909`_)

* **parser-scipy**: Automatically parse PR/MR numbers from subject lines in commits (`2b3f738`_)

🪲 Bug Fixes
------------

* **changelog-rst**: Ignore unknown parsed commit types in default RST changelog (`77609b1`_)

* **parser-angular**: Drop the ``breaking`` category but still maintain a major level bump
  (`f1ffa54`_)

* **parsers**: Improve reliability of descriptions after reverse word-wrap (`436374b`_)

⚡ Performance Improvements
---------------------------

* **parser-angular**: Simplify commit parsing type pre-calculation (`a86a28c`_)

* **parser-emoji**: Increase speed of commit parsing (`2c9c468`_)

* **parser-scipy**: Increase speed & decrease complexity of commit parsing (`2b661ed`_)

📖 Documentation
----------------

* **changelog-templates**: Add ``linked_merge_request`` field to examples (`d4376bc`_)

* **changelog-templates**: Fix api class reference links (`7a5bdf2`_)

* **commit-parsing**: Add ``linked_merge_request`` field to Parsed Commit definition (`ca61889`_)

.. _#924: https://github.com/python-semantic-release/python-semantic-release/issues/924
.. _#953: https://github.com/python-semantic-release/python-semantic-release/issues/953
.. _2ac798f: https://github.com/python-semantic-release/python-semantic-release/commit/2ac798f92e0c13c1db668747f7e35a65b99ae7ce
.. _2b3f738: https://github.com/python-semantic-release/python-semantic-release/commit/2b3f73801f5760bac29acd93db3ffb2bc790cda0
.. _2b661ed: https://github.com/python-semantic-release/python-semantic-release/commit/2b661ed122a6f0357a6b92233ac1351c54c7794e
.. _2c9c468: https://github.com/python-semantic-release/python-semantic-release/commit/2c9c4685a66feb35cd78571cf05f76344dd6d66a
.. _436374b: https://github.com/python-semantic-release/python-semantic-release/commit/436374b04128d1550467ae97ba90253f1d1b3878
.. _5f018d6: https://github.com/python-semantic-release/python-semantic-release/commit/5f018d630b4c625bdf6d329b27fd966eba75b017
.. _77609b1: https://github.com/python-semantic-release/python-semantic-release/commit/77609b1917a00b106ce254e6f6d5edcd1feebba7
.. _7a5bdf2: https://github.com/python-semantic-release/python-semantic-release/commit/7a5bdf29b3df0f9a1346ea5301d2a7fee953667b
.. _9a91062: https://github.com/python-semantic-release/python-semantic-release/commit/9a9106212d6c240e9d3358e139b4c4694eaf9c4b
.. _a86a28c: https://github.com/python-semantic-release/python-semantic-release/commit/a86a28c5e26ed766cda71d26b9382c392e377c61
.. _bca9909: https://github.com/python-semantic-release/python-semantic-release/commit/bca9909c1b61fdb1f9ccf823fceb6951cd059820
.. _ca61889: https://github.com/python-semantic-release/python-semantic-release/commit/ca61889d4ac73e9864fbf637fb87ab2d5bc053ea
.. _cd8d131: https://github.com/python-semantic-release/python-semantic-release/commit/cd8d1310a4000cc79b529fbbdc58933f4c6373c6
.. _d4376bc: https://github.com/python-semantic-release/python-semantic-release/commit/d4376bc2ae4d3708d501d91211ec3ee3a923e9b5
.. _f1ffa54: https://github.com/python-semantic-release/python-semantic-release/commit/f1ffa5411892de34cdc842fd55c460a24b6685c6


.. _changelog-v9.12.2:

v9.12.2 (2024-11-07)
====================

🪲 Bug Fixes
------------

* **bitbucket**: Fix ``pull_request_url`` filter to ignore an PR prefix gracefully (`PR#1089`_,
  `275ec88`_)

* **cli**: Gracefully capture all exceptions unless in very verbose debug mode (`PR#1088`_,
  `13ca44f`_)

* **gitea**: Fix ``issue_url`` filter to ignore an issue prefix gracefully (`PR#1089`_, `275ec88`_)

* **gitea**: Fix ``pull_request_url`` filter to ignore an PR prefix gracefully (`PR#1089`_,
  `275ec88`_)

* **github**: Fix ``issue_url`` filter to ignore an issue prefix gracefully (`PR#1089`_, `275ec88`_)

* **github**: Fix ``pull_request_url`` filter to ignore an PR prefix gracefully (`PR#1089`_,
  `275ec88`_)

* **gitlab**: Fix ``issue_url`` filter to ignore an issue prefix gracefully (`PR#1089`_, `275ec88`_)

* **gitlab**: Fix ``merge_request_url`` filter to ignore an PR prefix gracefully (`PR#1089`_,
  `275ec88`_)

* **hvcs**: Add flexibility to issue & MR/PR url jinja filters (`PR#1089`_, `275ec88`_)

📖 Documentation
----------------

* **changelog-templates**: Update descriptions of issue & MR/PR url jinja filters (`PR#1089`_,
  `275ec88`_)

.. _13ca44f: https://github.com/python-semantic-release/python-semantic-release/commit/13ca44f4434098331f70e6937684679cf1b4106a
.. _275ec88: https://github.com/python-semantic-release/python-semantic-release/commit/275ec88e6d1637c47065bb752a60017ceba9876c
.. _PR#1088: https://github.com/python-semantic-release/python-semantic-release/pull/1088
.. _PR#1089: https://github.com/python-semantic-release/python-semantic-release/pull/1089


.. _changelog-v9.12.1:

v9.12.1 (2024-11-06)
====================

🪲 Bug Fixes
------------

* **changelog**: Fix raw-inline pattern replacement in ``convert_md_to_rst`` filter (`2dc70a6`_)

* **cmd-version**: Fix ``--as-prerelease`` when no commit change from last full release (`PR#1076`_,
  `3b7b772`_)

* **release-notes**: Add context variable shorthand ``ctx`` like docs claim & changelog has
  (`d618d83`_)

📖 Documentation
----------------

* **contributing**: Update local testing instructions (`74f03d4`_)

.. _2dc70a6: https://github.com/python-semantic-release/python-semantic-release/commit/2dc70a6106776106b0fba474b0029071317d639f
.. _3b7b772: https://github.com/python-semantic-release/python-semantic-release/commit/3b7b77246100cedd8cc8f289395f7641187ffdec
.. _74f03d4: https://github.com/python-semantic-release/python-semantic-release/commit/74f03d44684b7b2d84f9f5e471425b02f8bf91c3
.. _d618d83: https://github.com/python-semantic-release/python-semantic-release/commit/d618d83360c4409fc149f70b97c5fe338fa89968
.. _PR#1076: https://github.com/python-semantic-release/python-semantic-release/pull/1076


.. _changelog-v9.12.0:

v9.12.0 (2024-10-18)
====================

✨ Features
-----------

* **changelog**: Add ``autofit_text_width`` filter to template environment (`PR#1062`_, `83e4b86`_)

🪲 Bug Fixes
------------

* **changelog**: Ignore commit exclusion when a commit causes a version bump (`e8f886e`_)

* **parser-angular**: Change ``Fixes`` commit type heading to ``Bug Fixes`` (`PR#1064`_, `09e3a4d`_)

* **parser-emoji**: Enable the default bump level option (`bc27995`_)

📖 Documentation
----------------

* **changelog-templates**: Add definition & usage of ``autofit_text_width`` template filter
  (`PR#1062`_, `83e4b86`_)

* **commit-parsers**: Add deprecation message for the tag parser (`af94540`_)

* **configuration**: Add deprecation message for the tag parser (`a83b7e4`_)

.. _09e3a4d: https://github.com/python-semantic-release/python-semantic-release/commit/09e3a4da6237740de8e9932d742b18d990e9d079
.. _83e4b86: https://github.com/python-semantic-release/python-semantic-release/commit/83e4b86abd4754c2f95ec2e674f04deb74b9a1e6
.. _a83b7e4: https://github.com/python-semantic-release/python-semantic-release/commit/a83b7e43e4eaa99790969a6c85f44e01cde80d0a
.. _af94540: https://github.com/python-semantic-release/python-semantic-release/commit/af94540f2b1c63bf8a4dc977d5d0f66176962b64
.. _bc27995: https://github.com/python-semantic-release/python-semantic-release/commit/bc27995255a96b9d6cc743186e7c35098822a7f6
.. _e8f886e: https://github.com/python-semantic-release/python-semantic-release/commit/e8f886ef2abe8ceaea0a24a0112b92a167abd6a9
.. _PR#1062: https://github.com/python-semantic-release/python-semantic-release/pull/1062
.. _PR#1064: https://github.com/python-semantic-release/python-semantic-release/pull/1064


.. _changelog-v9.11.1:

v9.11.1 (2024-10-15)
====================

🪲 Bug Fixes
------------

* **changelog**: Prevent custom template errors when components are in hidden folders (`PR#1060`_,
  `a7614b0`_)

.. _a7614b0: https://github.com/python-semantic-release/python-semantic-release/commit/a7614b0db8ce791e4252209e66f42b5b5275dffd
.. _PR#1060: https://github.com/python-semantic-release/python-semantic-release/pull/1060


.. _changelog-v9.11.0:

v9.11.0 (2024-10-12)
====================

✨ Features
-----------

* **changelog**: Add ``convert_md_to_rst`` filter to changelog environment (`PR#1055`_, `c2e8831`_)

* **changelog**: Add default changelog in re-structured text format, closes `#399`_ (`PR#1055`_,
  `c2e8831`_)

* **changelog**: Add default changelog template in reStructuredText format (`PR#1055`_, `c2e8831`_)

* **config**: Enable default ``changelog.insertion_flag`` based on output format (`PR#1055`_,
  `c2e8831`_)

* **config**: Enable target changelog filename to trigger RST output format, closes `#399`_
  (`PR#1055`_, `c2e8831`_)

🪲 Bug Fixes
------------

* **changelog**: Correct spacing for default markdown template during updates (`PR#1055`_,
  `c2e8831`_)

📖 Documentation
----------------

* **changelog**: Clarify the ``convert_md_to_rst`` filter added to the template environment
  (`PR#1055`_, `c2e8831`_)

* **changelog**: Increase detail about configuration options of default changelog creation
  (`PR#1055`_, `c2e8831`_)

* **configuration**: Update ``changelog_file`` with deprecation notice of setting relocation
  (`PR#1055`_, `c2e8831`_)

* **configuration**: Update ``output_format`` description for reStructuredText support (`PR#1055`_,
  `c2e8831`_)

* **configuration**: Update details of ``insertion_flag``'s dynamic defaults with rst (`PR#1055`_,
  `c2e8831`_)

.. _#399: https://github.com/python-semantic-release/python-semantic-release/issues/399
.. _c2e8831: https://github.com/python-semantic-release/python-semantic-release/commit/c2e883104d3c11e56f229638e988d8b571f86e34
.. _PR#1055: https://github.com/python-semantic-release/python-semantic-release/pull/1055


.. _changelog-v9.10.1:

v9.10.1 (2024-10-10)
====================

🪲 Bug Fixes
------------

* **config**: Handle branch match regex errors gracefully (`PR#1054`_, `4d12251`_)

.. _4d12251: https://github.com/python-semantic-release/python-semantic-release/commit/4d12251c678a38de6b71cac5b9c1390eb9dd8ad6
.. _PR#1054: https://github.com/python-semantic-release/python-semantic-release/pull/1054


.. _changelog-v9.10.0:

v9.10.0 (2024-10-08)
====================

✨ Features
-----------

* **changelog**: Add ``changelog_insertion_flag`` to changelog template context (`PR#1045`_,
  `c18c245`_)

* **changelog**: Add ``changelog_mode`` to changelog template context (`PR#1045`_, `c18c245`_)

* **changelog**: Add ``prev_changelog_file`` to changelog template context (`PR#1045`_, `c18c245`_)

* **changelog**: Add ``read_file`` function to changelog template context (`PR#1045`_, `c18c245`_)

* **changelog**: Add shorthand ``ctx`` variable to changelog template env (`PR#1045`_, `c18c245`_)

* **changelog**: Modify changelog template to support changelog updates, closes `#858`_
  (`PR#1045`_, `c18c245`_)

* **config**: Add ``changelog.default_templates.output_format`` config option (`PR#1045`_,
  `c18c245`_)

* **config**: Add ``changelog.insertion_flag`` as configuration option (`PR#1045`_, `c18c245`_)

* **config**: Add ``changelog.mode`` as configuration option (`PR#1045`_, `c18c245`_)

* **github-actions**: Add an action ``build`` directive to toggle the ``--skip-build`` option
  (`PR#1044`_, `26597e2`_)

🪲 Bug Fixes
------------

* **changelog**: Adjust angular heading names for readability (`PR#1045`_, `c18c245`_)

* **changelog**: Ensure changelog templates can handle complex directory includes (`PR#1045`_,
  `c18c245`_)

* **changelog**: Only render user templates when files exist (`PR#1045`_, `c18c245`_)

* **config**: Prevent jinja from autoescaping markdown content by default (`PR#1045`_, `c18c245`_)

📖 Documentation
----------------

* **changelog-templates**: Improve detail & describe new ``changelog.mode="update"`` (`PR#1045`_,
  `c18c245`_)

* **commands**: Update definition of the version commands ``--skip-build`` option (`PR#1044`_,
  `26597e2`_)

* **configuration**: Add ``changelog.mode`` and ``changelog.insertion_flag`` config definitions
  (`PR#1045`_, `c18c245`_)

* **configuration**: Define the new ``changelog.default_templates.output_format`` option
  (`PR#1045`_, `c18c245`_)

* **configuration**: Mark version of configuration setting introduction (`PR#1045`_, `c18c245`_)

* **configuration**: Standardize all true/false to lowercase ensuring toml-compatibility
  (`PR#1045`_, `c18c245`_)

* **configuration**: Update ``changelog.environment.autoescape`` default to ``false`` to match code
  (`PR#1045`_, `c18c245`_)

* **github-actions**: Add description of the ``build`` input directive (`PR#1044`_, `26597e2`_)

* **github-actions**: Update primary example with workflow sha controlled pipeline (`14f04df`_)

* **homepage**: Update custom changelog reference (`PR#1045`_, `c18c245`_)

.. _#722: https://github.com/python-semantic-release/python-semantic-release/issues/722
.. _#858: https://github.com/python-semantic-release/python-semantic-release/issues/858
.. _14f04df: https://github.com/python-semantic-release/python-semantic-release/commit/14f04dffc7366142faecebb162d4449501cbf1fd
.. _26597e2: https://github.com/python-semantic-release/python-semantic-release/commit/26597e24a80a37500264aa95a908ba366699099e
.. _c18c245: https://github.com/python-semantic-release/python-semantic-release/commit/c18c245df51a9778af09b9dc7a315e3f11cdcda0
.. _PR#1044: https://github.com/python-semantic-release/python-semantic-release/pull/1044
.. _PR#1045: https://github.com/python-semantic-release/python-semantic-release/pull/1045


.. _changelog-v9.9.0:

v9.9.0 (2024-09-28)
===================

✨ Features
-----------

* **github-actions**: Add ``is_prerelease`` output to the version action (`PR#1038`_, `6a5d35d`_)

📖 Documentation
----------------

* **automatic-releases**: Drop extraneous github push configuration (`PR#1011`_, `2135c68`_)

* **github-actions**: Add configuration & description of publish action (`PR#1011`_, `2135c68`_)

* **github-actions**: Add description of new ``is_prerelease`` output for version action
  (`PR#1038`_, `6a5d35d`_)

* **github-actions**: Clarify & consolidate GitHub Actions usage docs, closes `#907`_ (`PR#1011`_,
  `2135c68`_)

* **github-actions**: Expand descriptions & clarity of actions configs (`PR#1011`_, `2135c68`_)

* **github-actions**: Revert removal of namespace prefix from examples (`PR#1011`_, `2135c68`_)

* **homepage**: Remove link to old github config & update token scope config (`PR#1011`_,
  `2135c68`_)

.. _#907: https://github.com/python-semantic-release/python-semantic-release/issues/907
.. _2135c68: https://github.com/python-semantic-release/python-semantic-release/commit/2135c68ccbdad94378809902b52fcad546efd5b3
.. _6a5d35d: https://github.com/python-semantic-release/python-semantic-release/commit/6a5d35d0d9124d6a6ee7910711b4154b006b8773
.. _PR#1011: https://github.com/python-semantic-release/python-semantic-release/pull/1011
.. _PR#1038: https://github.com/python-semantic-release/python-semantic-release/pull/1038


.. _changelog-v9.8.9:

v9.8.9 (2024-09-27)
===================

🪲 Bug Fixes
------------

* **version-cmd**: Ensure ``version_variables`` do not match partial variable names (`PR#1028`_,
  `156915c`_)

* **version-cmd**: Improve ``version_variables`` flexibility w/ quotes (ie. json, yaml, etc)
  (`PR#1028`_, `156915c`_)

* **version-cmd**: Increase ``version_variable`` flexibility with quotations (ie. json, yaml, etc),
  closes `#601`_, `#706`_, `#962`_, `#1026`_ (`PR#1028`_, `156915c`_)

📖 Documentation
----------------

* Update docstrings to resolve sphinx failures, closes `#1029`_ (`PR#1030`_, `d84efc7`_)

* **configuration**: Add clarity to ``version_variables`` usage & limitations (`PR#1028`_,
  `156915c`_)

* **homepage**: Re-structure homepage to be separate from project readme (`PR#1032`_, `2307ed2`_)

* **README**: Simplify README to point at official docs (`PR#1032`_, `2307ed2`_)

.. _#1026: https://github.com/python-semantic-release/python-semantic-release/issues/1026
.. _#1029: https://github.com/python-semantic-release/python-semantic-release/issues/1029
.. _#601: https://github.com/python-semantic-release/python-semantic-release/issues/601
.. _#706: https://github.com/python-semantic-release/python-semantic-release/issues/706
.. _#962: https://github.com/python-semantic-release/python-semantic-release/issues/962
.. _156915c: https://github.com/python-semantic-release/python-semantic-release/commit/156915c7d759098f65cf9de7c4e980b40b38d5f1
.. _2307ed2: https://github.com/python-semantic-release/python-semantic-release/commit/2307ed29d9990bf1b6821403a4b8db3365ef8bb5
.. _d84efc7: https://github.com/python-semantic-release/python-semantic-release/commit/d84efc7719a8679e6979d513d1c8c60904af7384
.. _PR#1028: https://github.com/python-semantic-release/python-semantic-release/pull/1028
.. _PR#1030: https://github.com/python-semantic-release/python-semantic-release/pull/1030
.. _PR#1032: https://github.com/python-semantic-release/python-semantic-release/pull/1032


.. _changelog-v9.8.8:

v9.8.8 (2024-09-01)
===================

🪲 Bug Fixes
------------

* **config**: Fix path traversal detection for windows compatibility, closes `#994`_ (`PR#1014`_,
  `16e6daa`_)

📖 Documentation
----------------

* **configuration**: Update ``build_command`` env table for windows to use all capital vars
  (`0e8451c`_)

* **github-actions**: Update version in examples to latest version (`3c894ea`_)

.. _#994: https://github.com/python-semantic-release/python-semantic-release/issues/994
.. _0e8451c: https://github.com/python-semantic-release/python-semantic-release/commit/0e8451cf9003c6a3bdcae6878039d7d9a23d6d5b
.. _16e6daa: https://github.com/python-semantic-release/python-semantic-release/commit/16e6daaf851ce1eabf5fbd5aa9fe310a8b0f22b3
.. _3c894ea: https://github.com/python-semantic-release/python-semantic-release/commit/3c894ea8a555d20b454ebf34785e772959bbb4fe
.. _PR#1014: https://github.com/python-semantic-release/python-semantic-release/pull/1014


.. _changelog-v9.8.7:

v9.8.7 (2024-08-20)
===================

🪲 Bug Fixes
------------

* Provide ``context.history`` global in release notes templates (`PR#1005`_, `5bd91b4`_)

* **release-notes**: Fix noop-changelog to print raw release notes (`PR#1005`_, `5bd91b4`_)

* **release-notes**: Provide ``context.history`` global in release note templates, closes `#984`_
  (`PR#1005`_, `5bd91b4`_)

📖 Documentation
----------------

* Use pinned version for GHA examples (`PR#1004`_, `5fdf761`_)

* **changelog**: Clarify description of the default changelog generation process (`399fa65`_)

* **configuration**: Clarify ``changelog_file`` vs ``template_dir`` option usage, closes `#983`_
  (`a7199c8`_)

* **configuration**: Fix build_command_env table rendering (`PR#996`_, `a5eff0b`_)

* **github-actions**: Adjust formatting & version warning in code snippets (`PR#1004`_, `5fdf761`_)

* **github-actions**: Use pinned version for GHA examples, closes `#1003`_ (`PR#1004`_, `5fdf761`_)

.. _#1003: https://github.com/python-semantic-release/python-semantic-release/issues/1003
.. _#983: https://github.com/python-semantic-release/python-semantic-release/issues/983
.. _#984: https://github.com/python-semantic-release/python-semantic-release/issues/984
.. _399fa65: https://github.com/python-semantic-release/python-semantic-release/commit/399fa6521d5c6c4397b1d6e9b13ea7945ae92543
.. _5bd91b4: https://github.com/python-semantic-release/python-semantic-release/commit/5bd91b4d7ac33ddf10446f3e66d7d11e0724aeb2
.. _5fdf761: https://github.com/python-semantic-release/python-semantic-release/commit/5fdf7614c036a77ffb051cd30f57d0a63c062c0d
.. _a5eff0b: https://github.com/python-semantic-release/python-semantic-release/commit/a5eff0bfe41d2fd5d9ead152a132010b718b7772
.. _a7199c8: https://github.com/python-semantic-release/python-semantic-release/commit/a7199c8cd6041a9de017694302e49b139bbcb034
.. _PR#1004: https://github.com/python-semantic-release/python-semantic-release/pull/1004
.. _PR#1005: https://github.com/python-semantic-release/python-semantic-release/pull/1005
.. _PR#996: https://github.com/python-semantic-release/python-semantic-release/pull/996


.. _changelog-v9.8.6:

v9.8.6 (2024-07-20)
===================

🪲 Bug Fixes
------------

* **version-cmd**: Resolve build command execution in powershell (`PR#980`_, `32c8e70`_)

📖 Documentation
----------------

* **configuration**: Correct GHA parameter name for commit email (`PR#981`_, `ce9ffdb`_)

.. _32c8e70: https://github.com/python-semantic-release/python-semantic-release/commit/32c8e70915634d8e560b470c3cf38c27cebd7ae0
.. _ce9ffdb: https://github.com/python-semantic-release/python-semantic-release/commit/ce9ffdb82c2358184b288fa18e83a4075f333277
.. _PR#980: https://github.com/python-semantic-release/python-semantic-release/pull/980
.. _PR#981: https://github.com/python-semantic-release/python-semantic-release/pull/981


.. _changelog-v9.8.5:

v9.8.5 (2024-07-06)
===================

🪲 Bug Fixes
------------

* Enable ``--print-last-released*`` when in detached head or non-release branch (`PR#926`_,
  `782c0a6`_)

* **changelog**: Resolve commit ordering issue when dates are similar (`PR#972`_, `bfda159`_)

* **version-cmd**: Drop branch restriction for ``--print-last-released*`` opts, closes `#900`_
  (`PR#926`_, `782c0a6`_)

⚡ Performance Improvements
---------------------------

* Improve git history processing for changelog generation (`PR#972`_, `bfda159`_)

* **changelog**: Improve git history parser changelog generation (`PR#972`_, `bfda159`_)

.. _#900: https://github.com/python-semantic-release/python-semantic-release/issues/900
.. _782c0a6: https://github.com/python-semantic-release/python-semantic-release/commit/782c0a6109fb49e168c37f279928c0a4959f8ac6
.. _bfda159: https://github.com/python-semantic-release/python-semantic-release/commit/bfda1593af59e9e728c584dd88d7927fc52c879f
.. _PR#926: https://github.com/python-semantic-release/python-semantic-release/pull/926
.. _PR#972: https://github.com/python-semantic-release/python-semantic-release/pull/972


.. _changelog-v9.8.4:

v9.8.4 (2024-07-04)
===================

🪲 Bug Fixes
------------

* **changelog-cmd**: Remove usage strings when error occurred, closes `#810`_ (`348a51d`_)

* **changelog-cmd**: Render default changelog when user template directory exist but is empty
  (`bded8de`_)

* **config**: Prevent path traversal manipulation of target changelog location (`43e35d0`_)

* **config**: Prevent path traversal manipulation of target changelog location (`3eb3dba`_)

* **publish-cmd**: Prevent error when provided tag does not exist locally (`16afbbb`_)

* **publish-cmd**: Remove usage strings when error occurred, closes `#810`_ (`afbb187`_)

* **version-cmd**: Remove usage strings when error occurred, closes `#810`_ (`a7c17c7`_)

.. _#810: https://github.com/python-semantic-release/python-semantic-release/issues/810
.. _16afbbb: https://github.com/python-semantic-release/python-semantic-release/commit/16afbbb8fbc3a97243e96d7573f4ad2eba09aab9
.. _348a51d: https://github.com/python-semantic-release/python-semantic-release/commit/348a51db8a837d951966aff3789aa0c93d473829
.. _3eb3dba: https://github.com/python-semantic-release/python-semantic-release/commit/3eb3dbafec4223ee463b90e927e551639c69426b
.. _43e35d0: https://github.com/python-semantic-release/python-semantic-release/commit/43e35d0972e8a29239d18ed079d1e2013342fcbd
.. _a7c17c7: https://github.com/python-semantic-release/python-semantic-release/commit/a7c17c73fd7becb6d0e042e45ff6765605187e2a
.. _afbb187: https://github.com/python-semantic-release/python-semantic-release/commit/afbb187d6d405fdf6765082e2a1cecdcd7d357df
.. _bded8de: https://github.com/python-semantic-release/python-semantic-release/commit/bded8deae6c92f6dde9774802d9f3716a5cb5705


.. _changelog-v9.8.3:

v9.8.3 (2024-06-18)
===================

🪲 Bug Fixes
------------

* **parser**: Strip DOS carriage-returns in commits, closes `#955`_ (`PR#956`_, `0b005df`_)

.. _#955: https://github.com/python-semantic-release/python-semantic-release/issues/955
.. _0b005df: https://github.com/python-semantic-release/python-semantic-release/commit/0b005df0a8c7730ee0c71453c9992d7b5d2400a4
.. _PR#956: https://github.com/python-semantic-release/python-semantic-release/pull/956


.. _changelog-v9.8.2:

v9.8.2 (2024-06-17)
===================

🪲 Bug Fixes
------------

* **templates**: Suppress extra newlines in default changelog (`PR#954`_, `7b0079b`_)

.. _7b0079b: https://github.com/python-semantic-release/python-semantic-release/commit/7b0079bf3e17c0f476bff520b77a571aeac469d0
.. _PR#954: https://github.com/python-semantic-release/python-semantic-release/pull/954


.. _changelog-v9.8.1:

v9.8.1 (2024-06-05)
===================

🪲 Bug Fixes
------------

* Improve build cmd env on windows (`PR#942`_, `d911fae`_)

* **version-cmd**: Pass windows specific env vars to build cmd when on windows (`PR#942`_,
  `d911fae`_)

📖 Documentation
----------------

* **configuration**: Define windows specific env vars for build cmd (`PR#942`_, `d911fae`_)

.. _d911fae: https://github.com/python-semantic-release/python-semantic-release/commit/d911fae993d41a8cb1497fa8b2a7e823576e0f22
.. _PR#942: https://github.com/python-semantic-release/python-semantic-release/pull/942


.. _changelog-v9.8.0:

v9.8.0 (2024-05-27)
===================

✨ Features
-----------

* Extend gitlab to edit a previous release if exists (`PR#934`_, `23e02b9`_)

* **gha**: Configure ssh signed tags in GitHub Action, closes `#936`_ (`PR#937`_, `dfb76b9`_)

* **hvcs-gitlab**: Enable gitlab to edit a previous release if found (`PR#934`_, `23e02b9`_)

* **version-cmd**: Add toggle of ``--no-verify`` option to ``git commit`` (`PR#927`_, `1de6f78`_)

🪲 Bug Fixes
------------

* **gitlab**: Adjust release name to mirror other hvcs release names (`PR#934`_, `23e02b9`_)

* **hvcs-gitlab**: Add tag message to release creation (`PR#934`_, `23e02b9`_)

📖 Documentation
----------------

* **configuration**: Add ``no_git_verify`` description to the configuration page (`PR#927`_,
  `1de6f78`_)

* **migration-v8**: Update version references in migration instructions (`PR#938`_, `d6ba16a`_)

.. _#936: https://github.com/python-semantic-release/python-semantic-release/issues/936
.. _1de6f78: https://github.com/python-semantic-release/python-semantic-release/commit/1de6f7834c6d37a74bc53f91609d40793556b52d
.. _23e02b9: https://github.com/python-semantic-release/python-semantic-release/commit/23e02b96dfb2a58f6b4ecf7b7812e4c1bc50573d
.. _d6ba16a: https://github.com/python-semantic-release/python-semantic-release/commit/d6ba16aa8e01bae1a022a9b06cd0b9162c51c345
.. _dfb76b9: https://github.com/python-semantic-release/python-semantic-release/commit/dfb76b94b859a7f3fa3ad778eec7a86de2874d68
.. _PR#927: https://github.com/python-semantic-release/python-semantic-release/pull/927
.. _PR#934: https://github.com/python-semantic-release/python-semantic-release/pull/934
.. _PR#937: https://github.com/python-semantic-release/python-semantic-release/pull/937
.. _PR#938: https://github.com/python-semantic-release/python-semantic-release/pull/938


.. _changelog-v9.7.3:

v9.7.3 (2024-05-15)
===================

🪲 Bug Fixes
------------

* Enabled ``prerelease-token`` parameter in github action (`PR#929`_, `1bb26b0`_)

.. _1bb26b0: https://github.com/python-semantic-release/python-semantic-release/commit/1bb26b0762d94efd97c06a3f1b6b10fb76901f6d
.. _PR#929: https://github.com/python-semantic-release/python-semantic-release/pull/929


.. _changelog-v9.7.2:

v9.7.2 (2024-05-13)
===================

🪲 Bug Fixes
------------

* Enable user configuration of ``build_command`` env vars (`PR#925`_, `6b5b271`_)

* **version**: Enable user config of ``build_command`` env variables, closes `#922`_ (`PR#925`_,
  `6b5b271`_)

📖 Documentation
----------------

* **configuration**: Clarify TOC & alphabetize configuration descriptions (`19add16`_)

* **configuration**: Clarify TOC & standardize heading links (`3a41995`_)

* **configuration**: Document ``build_command_env`` configuration option (`PR#925`_, `6b5b271`_)

* **CONTRIBUTING**: Update build command definition for developers (`PR#921`_, `b573c4d`_)

.. _#922: https://github.com/python-semantic-release/python-semantic-release/issues/922
.. _19add16: https://github.com/python-semantic-release/python-semantic-release/commit/19add16dcfdfdb812efafe2d492a933d0856df1d
.. _3a41995: https://github.com/python-semantic-release/python-semantic-release/commit/3a4199542d0ea4dbf88fa35e11bec41d0c27dd17
.. _6b5b271: https://github.com/python-semantic-release/python-semantic-release/commit/6b5b271453874b982fbf2827ec1f6be6db1c2cc7
.. _b573c4d: https://github.com/python-semantic-release/python-semantic-release/commit/b573c4d4a2c212be9bdee918501bb5e046c6a806
.. _PR#921: https://github.com/python-semantic-release/python-semantic-release/pull/921
.. _PR#925: https://github.com/python-semantic-release/python-semantic-release/pull/925


.. _changelog-v9.7.1:

v9.7.1 (2024-05-07)
===================

🪲 Bug Fixes
------------

* **gha**: Fix missing ``git_committer_*`` definition in action, closes `#918`_ (`PR#919`_,
  `ccef9d8`_)

.. _#918: https://github.com/python-semantic-release/python-semantic-release/issues/918
.. _ccef9d8: https://github.com/python-semantic-release/python-semantic-release/commit/ccef9d8521be12c0640369b3c3a80b81a7832662
.. _PR#919: https://github.com/python-semantic-release/python-semantic-release/pull/919


.. _changelog-v9.7.0:

v9.7.0 (2024-05-06)
===================

✨ Features
-----------

* **version-cmd**: Pass ``NEW_VERSION`` & useful env vars to build command (`ee6b246`_)

🪲 Bug Fixes
------------

* **gha**: Add missing ``tag`` option to GitHub Action definition, closes `#906`_ (`PR#908`_,
  `6b24288`_)

* **gha**: Correct use of ``prerelease`` option for GitHub Action (`PR#914`_, `85e27b7`_)

📖 Documentation
----------------

* **configuration**: Add description of build command available env variables (`c882dc6`_)

* **gha**: Update GitHub Actions doc with all available options (`PR#914`_, `85e27b7`_)

⚙️ Build System
----------------

* **deps**: Bump GitHub Action container to use ``python3.12``, closes `#801`_ (`PR#914`_,
  `85e27b7`_)

.. _#801: https://github.com/python-semantic-release/python-semantic-release/issues/801
.. _#906: https://github.com/python-semantic-release/python-semantic-release/issues/906
.. _6b24288: https://github.com/python-semantic-release/python-semantic-release/commit/6b24288a96302cd6982260e46fad128ec4940da9
.. _85e27b7: https://github.com/python-semantic-release/python-semantic-release/commit/85e27b7f486e6b0e6cc9e85e101a97e676bc3d60
.. _c882dc6: https://github.com/python-semantic-release/python-semantic-release/commit/c882dc62b860b2aeaa925c21d1524f4ae25ef567
.. _ee6b246: https://github.com/python-semantic-release/python-semantic-release/commit/ee6b246df3bb211ab49c8bce075a4c3f6a68ed77
.. _PR#908: https://github.com/python-semantic-release/python-semantic-release/pull/908
.. _PR#914: https://github.com/python-semantic-release/python-semantic-release/pull/914


.. _changelog-v9.6.0:

v9.6.0 (2024-04-29)
===================

✨ Features
-----------

* Changelog filters are specialized per vcs type (`PR#890`_, `76ed593`_)

* **changelog**: Changelog filters are hvcs focused (`PR#890`_, `76ed593`_)

* **changelog-context**: Add flag to jinja env for which hvcs is available (`PR#890`_, `76ed593`_)

* **changelog-gitea**: Add issue url filter to changelog context (`PR#890`_, `76ed593`_)

* **changelog-github**: Add issue url filter to changelog context (`PR#890`_, `76ed593`_)

* **version-cmd**: Add ``--as-prerelease`` option to force the next version to be a prerelease,
  closes `#639`_ (`PR#647`_, `2acb5ac`_)

🪲 Bug Fixes
------------

* Correct version ``--prerelease`` use & enable ``--as-prerelease`` (`PR#647`_, `2acb5ac`_)

* **github**: Correct changelog filter for pull request urls (`PR#890`_, `76ed593`_)

* **parser-custom**: Gracefully handle custom parser import errors (`67f6038`_)

* **version-cmd**: Correct ``--prerelease`` use, closes `#639`_ (`PR#647`_, `2acb5ac`_)

📖 Documentation
----------------

* **changelog-context**: Explain new hvcs specific context filters (`PR#890`_, `76ed593`_)

* **commands**: Update version command options definition about prereleases (`PR#647`_, `2acb5ac`_)

.. _#639: https://github.com/python-semantic-release/python-semantic-release/issues/639
.. _2acb5ac: https://github.com/python-semantic-release/python-semantic-release/commit/2acb5ac35ae79d7ae25ca9a03fb5c6a4a68b3673
.. _67f6038: https://github.com/python-semantic-release/python-semantic-release/commit/67f60389e3f6e93443ea108c0e1b4d30126b8e06
.. _76ed593: https://github.com/python-semantic-release/python-semantic-release/commit/76ed593ea33c851005994f0d1a6a33cc890fb908
.. _PR#647: https://github.com/python-semantic-release/python-semantic-release/pull/647
.. _PR#890: https://github.com/python-semantic-release/python-semantic-release/pull/890


.. _changelog-v9.5.0:

v9.5.0 (2024-04-23)
===================

✨ Features
-----------

* Extend support to on-prem GitHub Enterprise Server (`PR#896`_, `4fcb737`_)

* **github**: Extend support to on-prem GitHub Enterprise Server, closes `#895`_ (`PR#896`_,
  `4fcb737`_)

.. _#895: https://github.com/python-semantic-release/python-semantic-release/issues/895
.. _4fcb737: https://github.com/python-semantic-release/python-semantic-release/commit/4fcb737958d95d1a3be24db7427e137b46f5075f
.. _PR#896: https://github.com/python-semantic-release/python-semantic-release/pull/896


.. _changelog-v9.4.2:

v9.4.2 (2024-04-14)
===================

🪲 Bug Fixes
------------

* **bitbucket**: Allow insecure http connections if configured (`PR#886`_, `db13438`_)

* **bitbucket**: Correct url parsing & prevent double url schemes (`PR#676`_, `5cfdb24`_)

* **config**: Add flag to allow insecure connections (`PR#886`_, `db13438`_)

* **gitea**: Allow insecure http connections if configured (`PR#886`_, `db13438`_)

* **gitea**: Correct url parsing & prevent double url schemes (`PR#676`_, `5cfdb24`_)

* **github**: Allow insecure http connections if configured (`PR#886`_, `db13438`_)

* **github**: Correct url parsing & prevent double url schemes (`PR#676`_, `5cfdb24`_)

* **gitlab**: Allow insecure http connections if configured (`PR#886`_, `db13438`_)

* **gitlab**: Correct url parsing & prevent double url schemes (`PR#676`_, `5cfdb24`_)

* **hvcs**: Allow insecure http connections if configured (`PR#886`_, `db13438`_)

* **hvcs**: Prevent double protocol scheme urls in changelogs (`PR#676`_, `5cfdb24`_)

* **version-cmd**: Handle HTTP exceptions more gracefully (`PR#886`_, `db13438`_)

📖 Documentation
----------------

* **configuration**: Update ``remote`` settings section with missing values, closes `#868`_
  (`PR#886`_, `db13438`_)

⚙️ Build System
----------------

* **deps**: Update rich requirement from ~=12.5 to ~=13.0, closes `#888`_ (`PR#877`_, `4a22a8c`_)

.. _#868: https://github.com/python-semantic-release/python-semantic-release/issues/868
.. _#888: https://github.com/python-semantic-release/python-semantic-release/issues/888
.. _4a22a8c: https://github.com/python-semantic-release/python-semantic-release/commit/4a22a8c1a69bcf7b1ddd6db56e6883c617a892b3
.. _5cfdb24: https://github.com/python-semantic-release/python-semantic-release/commit/5cfdb248c003a2d2be5fe65fb61d41b0d4c45db5
.. _db13438: https://github.com/python-semantic-release/python-semantic-release/commit/db1343890f7e0644bc8457f995f2bd62087513d3
.. _PR#676: https://github.com/python-semantic-release/python-semantic-release/pull/676
.. _PR#877: https://github.com/python-semantic-release/python-semantic-release/pull/877
.. _PR#886: https://github.com/python-semantic-release/python-semantic-release/pull/886


.. _changelog-v9.4.1:

v9.4.1 (2024-04-06)
===================

🪲 Bug Fixes
------------

* **gh-actions-output**: Fixed trailing newline to match GITHUB_OUTPUT format (`PR#885`_,
  `2c7b6ec`_)

* **gh-actions-output**: Fixed trailing newline to match GITHUB_OUTPUT format, closes `#884`_
  (`PR#885`_, `2c7b6ec`_)

.. _#884: https://github.com/python-semantic-release/python-semantic-release/issues/884
.. _2c7b6ec: https://github.com/python-semantic-release/python-semantic-release/commit/2c7b6ec85b6e3182463d7b695ee48e9669a25b3b
.. _PR#885: https://github.com/python-semantic-release/python-semantic-release/pull/885


.. _changelog-v9.4.0:

v9.4.0 (2024-03-31)
===================

✨ Features
-----------

* **gitea**: Derives gitea api domain from base domain when unspecified (`PR#675`_, `2ee3f8a`_)

.. _2ee3f8a: https://github.com/python-semantic-release/python-semantic-release/commit/2ee3f8a918d2e5ea9ab64df88f52e62a1f589c38
.. _PR#675: https://github.com/python-semantic-release/python-semantic-release/pull/675


.. _changelog-v9.3.1:

v9.3.1 (2024-03-24)
===================

🪲 Bug Fixes
------------

* **algorithm**: Handle merge-base errors gracefully, closes `#724`_ (`4c998b7`_)

* **cli-version**: Change implementation to only push the tag we generated, closes `#803`_
  (`8a9da4f`_)

⚡ Performance Improvements
---------------------------

* **algorithm**: Simplify logs & use lookup when searching for commit & tag match (`3690b95`_)

.. _#724: https://github.com/python-semantic-release/python-semantic-release/issues/724
.. _#803: https://github.com/python-semantic-release/python-semantic-release/issues/803
.. _3690b95: https://github.com/python-semantic-release/python-semantic-release/commit/3690b9511de633ab38083de4d2505b6d05853346
.. _4c998b7: https://github.com/python-semantic-release/python-semantic-release/commit/4c998b77a3fe5e12783d1ab2d47789a10b83f247
.. _8a9da4f: https://github.com/python-semantic-release/python-semantic-release/commit/8a9da4feb8753e3ab9ea752afa25decd2047675a


.. _changelog-v9.3.0:

v9.3.0 (2024-03-21)
===================

✨ Features
-----------

* **cmd-version**: Changelog available to bundle (`PR#779`_, `37fdb28`_)

* **cmd-version**: Create changelog prior to build enabling doc bundling (`PR#779`_, `37fdb28`_)

.. _37fdb28: https://github.com/python-semantic-release/python-semantic-release/commit/37fdb28e0eb886d682b5dea4cc83a7c98a099422
.. _PR#779: https://github.com/python-semantic-release/python-semantic-release/pull/779


.. _changelog-v9.2.2:

v9.2.2 (2024-03-19)
===================

🪲 Bug Fixes
------------

* **cli**: Enable subcommand help even if config is invalid, closes `#840`_ (`91d221a`_)

.. _#840: https://github.com/python-semantic-release/python-semantic-release/issues/840
.. _91d221a: https://github.com/python-semantic-release/python-semantic-release/commit/91d221a01266e5ca6de5c73296b0a90987847494


.. _changelog-v9.2.1:

v9.2.1 (2024-03-19)
===================

🪲 Bug Fixes
------------

* **parse-git-url**: Handle urls with url-safe special characters (`27cd93a`_)

.. _27cd93a: https://github.com/python-semantic-release/python-semantic-release/commit/27cd93a0a65ee3787ca51be4c91c48f6ddb4269c


.. _changelog-v9.2.0:

v9.2.0 (2024-03-18)
===================

✨ Features
-----------

* **version**: Add new version print flags to display the last released version and tag (`814240c`_)

* **version-config**: Add option to disable 0.x.x versions (`dedb3b7`_)

🪲 Bug Fixes
------------

* **changelog**: Make sure default templates render ending in 1 newline (`0b4a45e`_)

* **changelog-generation**: Fix incorrect release timezone determination (`f802446`_)

📖 Documentation
----------------

* **configuration**: Add description of ``allow-zero-version`` configuration option (`4028f83`_)

* **configuration**: Clarify the ``major_on_zero`` configuration option (`f7753cd`_)

⚙️ Build System
----------------

* **deps**: Add click-option-group for grouping exclusive flags (`bd892b8`_)

.. _0b4a45e: https://github.com/python-semantic-release/python-semantic-release/commit/0b4a45e3673d0408016dc8e7b0dce98007a763e3
.. _4028f83: https://github.com/python-semantic-release/python-semantic-release/commit/4028f8384a0181c8d58c81ae81cf0b241a02a710
.. _814240c: https://github.com/python-semantic-release/python-semantic-release/commit/814240c7355df95e9be9a6ed31d004b800584bc0
.. _bd892b8: https://github.com/python-semantic-release/python-semantic-release/commit/bd892b89c26df9fccc9335c84e2b3217e3e02a37
.. _dedb3b7: https://github.com/python-semantic-release/python-semantic-release/commit/dedb3b765c8530379af61d3046c3bb9c160d54e5
.. _f7753cd: https://github.com/python-semantic-release/python-semantic-release/commit/f7753cdabd07e276bc001478d605fca9a4b37ec4
.. _f802446: https://github.com/python-semantic-release/python-semantic-release/commit/f802446bd0693c4c9f6bdfdceae8b89c447827d2


.. _changelog-v9.1.1:

v9.1.1 (2024-02-25)
===================

🪲 Bug Fixes
------------

* **parse_git_url**: Fix bad url with dash (`1c25b8e`_)

.. _1c25b8e: https://github.com/python-semantic-release/python-semantic-release/commit/1c25b8e6f1e43c15ca7d5a59dca0a13767f9bc33


.. _changelog-v9.1.0:

v9.1.0 (2024-02-14)
===================

✨ Features
-----------

* Add bitbucket hvcs (`bbbbfeb`_)

🪲 Bug Fixes
------------

* Remove unofficial environment variables (`a5168e4`_)

📖 Documentation
----------------

* Add bitbucket authentication (`b78a387`_)

* Add bitbucket to token table (`56f146d`_)

* Fix typo (`b240e12`_)

⚙️ Build System
----------------

* **deps**: Bump minimum required ``tomlkit`` to ``>=0.11.0``, closes `#834`_ (`291aace`_)

.. _#834: https://github.com/python-semantic-release/python-semantic-release/issues/834
.. _291aace: https://github.com/python-semantic-release/python-semantic-release/commit/291aacea1d0429a3b27e92b0a20b598f43f6ea6b
.. _56f146d: https://github.com/python-semantic-release/python-semantic-release/commit/56f146d9f4c0fc7f2a84ad11b21c8c45e9221782
.. _a5168e4: https://github.com/python-semantic-release/python-semantic-release/commit/a5168e40b9a14dbd022f62964f382b39faf1e0df
.. _b240e12: https://github.com/python-semantic-release/python-semantic-release/commit/b240e129b180d45c1d63d464283b7dfbcb641d0c
.. _b78a387: https://github.com/python-semantic-release/python-semantic-release/commit/b78a387d8eccbc1a6a424a183254fc576126199c
.. _bbbbfeb: https://github.com/python-semantic-release/python-semantic-release/commit/bbbbfebff33dd24b8aed2d894de958d532eac596


.. _changelog-v9.0.3:

v9.0.3 (2024-02-08)
===================

🪲 Bug Fixes
------------

* **algorithm**: Correct bfs to not abort on previously visited node (`02df305`_)

⚡ Performance Improvements
---------------------------

* **algorithm**: Refactor bfs search to use queue rather than recursion (`8b742d3`_)

.. _02df305: https://github.com/python-semantic-release/python-semantic-release/commit/02df305db43abfc3a1f160a4a52cc2afae5d854f
.. _8b742d3: https://github.com/python-semantic-release/python-semantic-release/commit/8b742d3db6652981a7b5f773a74b0534edc1fc15


.. _changelog-v9.0.2:

v9.0.2 (2024-02-08)
===================

🪲 Bug Fixes
------------

* **util**: Properly parse windows line-endings in commit messages, closes `#820`_ (`70193ba`_)

📖 Documentation
----------------

* Remove duplicate note in configuration.rst (`PR#807`_, `fb6f243`_)

.. _#820: https://github.com/python-semantic-release/python-semantic-release/issues/820
.. _70193ba: https://github.com/python-semantic-release/python-semantic-release/commit/70193ba117c1a6d3690aed685fee8a734ba174e5
.. _fb6f243: https://github.com/python-semantic-release/python-semantic-release/commit/fb6f243a141642c02469f1080180ecaf4f3cec66
.. _PR#807: https://github.com/python-semantic-release/python-semantic-release/pull/807


.. _changelog-v9.0.1:

v9.0.1 (2024-02-06)
===================

🪲 Bug Fixes
------------

* **config**: Set commit parser opt defaults based on parser choice (`PR#782`_, `9c594fb`_)

.. _9c594fb: https://github.com/python-semantic-release/python-semantic-release/commit/9c594fb6efac7e4df2b0bfbd749777d3126d03d7
.. _PR#782: https://github.com/python-semantic-release/python-semantic-release/pull/782


.. _changelog-v9.0.0:

v9.0.0 (2024-02-06)
===================

♻️ Refactoring
---------------

* Drop support for Python 3.7 (`PR#828`_, `ad086f5`_)

💥 BREAKING CHANGES
--------------------

* Removed Python 3.7 specific control flows and made more modern implementations the default
  control flow without a bypass or workaround. Will break on Python 3.7 now. If you require Python
  3.7, you should lock your major version at v8. Since we only have enough manpower to maintain the
  latest major release, unfortunately there will not be any more updates to v8.

* We decided to remove support for Python 3.7 because it has been officially deprecated by the
  Python Foundation over a year ago and our codebase is starting to have limitations and custom
  implementations just to maintain support for 3.7.

.. _ad086f5: https://github.com/python-semantic-release/python-semantic-release/commit/ad086f5993ae4741d6e20fee618d1bce8df394fb
.. _PR#828: https://github.com/python-semantic-release/python-semantic-release/pull/828


.. _changelog-v8.7.2:

v8.7.2 (2024-01-03)
===================

🪲 Bug Fixes
------------

* **lint**: Correct linter errors (`c9556b0`_)

.. _c9556b0: https://github.com/python-semantic-release/python-semantic-release/commit/c9556b0ca6df6a61e9ce909d18bc5be8b6154bf8


.. _changelog-v8.7.1:

v8.7.1 (2024-01-03)
===================

🪲 Bug Fixes
------------

* **cli-generate-config**: Ensure configuration types are always toml parsable (`PR#785`_,
  `758e649`_)

📖 Documentation
----------------

* Add note on default envvar behavior (`PR#780`_, `0b07cae`_)

* **configuration**: Change defaults definition of token default to table (`PR#786`_, `df1df0d`_)

* **contributing**: Add docs-build, testing conf, & build instructions (`PR#787`_, `011b072`_)

.. _011b072: https://github.com/python-semantic-release/python-semantic-release/commit/011b0729cba3045b4e7291fd970cb17aad7bae60
.. _0b07cae: https://github.com/python-semantic-release/python-semantic-release/commit/0b07cae71915c5c82d7784898b44359249542a64
.. _758e649: https://github.com/python-semantic-release/python-semantic-release/commit/758e64975fe46b961809f35977574729b7c44271
.. _df1df0d: https://github.com/python-semantic-release/python-semantic-release/commit/df1df0de8bc655cbf8f86ae52aff10efdc66e6d2
.. _PR#780: https://github.com/python-semantic-release/python-semantic-release/pull/780
.. _PR#785: https://github.com/python-semantic-release/python-semantic-release/pull/785
.. _PR#786: https://github.com/python-semantic-release/python-semantic-release/pull/786
.. _PR#787: https://github.com/python-semantic-release/python-semantic-release/pull/787


.. _changelog-v8.7.0:

v8.7.0 (2023-12-22)
===================

✨ Features
-----------

* **config**: Enable default environment token per hvcs (`PR#774`_, `26528eb`_)

.. _26528eb: https://github.com/python-semantic-release/python-semantic-release/commit/26528eb8794d00dfe985812269702fbc4c4ec788
.. _PR#774: https://github.com/python-semantic-release/python-semantic-release/pull/774


.. _changelog-v8.6.0:

v8.6.0 (2023-12-22)
===================

✨ Features
-----------

* **utils**: Expand parsable valid git remote url formats (`PR#771`_, `cf75f23`_)

📖 Documentation
----------------

* Minor correction to commit-parsing documentation (`PR#777`_, `245e878`_)

.. _245e878: https://github.com/python-semantic-release/python-semantic-release/commit/245e878f02d5cafec6baf0493c921c1e396b56e8
.. _cf75f23: https://github.com/python-semantic-release/python-semantic-release/commit/cf75f237360488ebb0088e5b8aae626e97d9cbdd
.. _PR#771: https://github.com/python-semantic-release/python-semantic-release/pull/771
.. _PR#777: https://github.com/python-semantic-release/python-semantic-release/pull/777


.. _changelog-v8.5.2:

v8.5.2 (2023-12-19)
===================

🪲 Bug Fixes
------------

* **cli**: Gracefully output configuration validation errors (`PR#772`_, `e8c9d51`_)

.. _e8c9d51: https://github.com/python-semantic-release/python-semantic-release/commit/e8c9d516c37466a5dce75a73766d5be0f9e74627
.. _PR#772: https://github.com/python-semantic-release/python-semantic-release/pull/772


.. _changelog-v8.5.1:

v8.5.1 (2023-12-12)
===================

🪲 Bug Fixes
------------

* **cmd-version**: Handle committing of git-ignored file gracefully (`PR#764`_, `ea89fa7`_)

* **config**: Cleanly handle repository in detached HEAD state (`PR#765`_, `ac4f9aa`_)

* **config**: Gracefully fail when repo is in a detached HEAD state (`PR#765`_, `ac4f9aa`_)

* **version**: Only commit non git-ignored files during version commit (`PR#764`_, `ea89fa7`_)

📖 Documentation
----------------

* **configuration**: Adjust wording and improve clarity (`PR#766`_, `6b2fc8c`_)

* **configuration**: Fix typo in text (`PR#766`_, `6b2fc8c`_)

.. _6b2fc8c: https://github.com/python-semantic-release/python-semantic-release/commit/6b2fc8c156e122ee1b43fdb513b2dc3b8fd76724
.. _ac4f9aa: https://github.com/python-semantic-release/python-semantic-release/commit/ac4f9aacb72c99f2479ae33369822faad011a824
.. _ea89fa7: https://github.com/python-semantic-release/python-semantic-release/commit/ea89fa72885e15da91687172355426a22c152513
.. _PR#764: https://github.com/python-semantic-release/python-semantic-release/pull/764
.. _PR#765: https://github.com/python-semantic-release/python-semantic-release/pull/765
.. _PR#766: https://github.com/python-semantic-release/python-semantic-release/pull/766


.. _changelog-v8.5.0:

v8.5.0 (2023-12-07)
===================

✨ Features
-----------

* Allow template directories to contain a '.' at the top-level (`PR#762`_, `07b232a`_)

.. _07b232a: https://github.com/python-semantic-release/python-semantic-release/commit/07b232a3b34be0b28c6af08aea4852acb1b9bd56
.. _PR#762: https://github.com/python-semantic-release/python-semantic-release/pull/762


.. _changelog-v8.4.0:

v8.4.0 (2023-12-07)
===================

✨ Features
-----------

* **cmd-version**: Add ``--tag/--no-tag`` option to version command (`PR#752`_, `de6b9ad`_)

* **version**: Add ``--no-tag`` option to turn off tag creation (`PR#752`_, `de6b9ad`_)

🪲 Bug Fixes
------------

* **version**: Separate push tags from commit push when not committing changes (`PR#752`_,
  `de6b9ad`_)

📖 Documentation
----------------

* **commands**: Update ``version`` subcommand options (`PR#752`_, `de6b9ad`_)

* **migration**: Fix comments about publish command (`PR#747`_, `90380d7`_)

.. _90380d7: https://github.com/python-semantic-release/python-semantic-release/commit/90380d797a734dcca5040afc5fa00e3e01f64152
.. _de6b9ad: https://github.com/python-semantic-release/python-semantic-release/commit/de6b9ad921e697b5ea2bb2ea8f180893cecca920
.. _PR#747: https://github.com/python-semantic-release/python-semantic-release/pull/747
.. _PR#752: https://github.com/python-semantic-release/python-semantic-release/pull/752


.. _changelog-v8.3.0:

v8.3.0 (2023-10-23)
===================

✨ Features
-----------

* **action**: Use composite action for semantic release (`PR#692`_, `4648d87`_)

.. _4648d87: https://github.com/python-semantic-release/python-semantic-release/commit/4648d87bac8fb7e6cc361b765b4391b30a8caef8
.. _PR#692: https://github.com/python-semantic-release/python-semantic-release/pull/692


.. _changelog-v8.2.0:

v8.2.0 (2023-10-23)
===================

✨ Features
-----------

* Allow user customization of release notes template (`PR#736`_, `94a1311`_)

📖 Documentation
----------------

* Add PYTHONPATH mention for commit parser (`3284258`_)

.. _3284258: https://github.com/python-semantic-release/python-semantic-release/commit/3284258b9fa1a3fe165f336181aff831d50fddd3
.. _94a1311: https://github.com/python-semantic-release/python-semantic-release/commit/94a131167e1b867f8bc112a042b9766e050ccfd1
.. _PR#736: https://github.com/python-semantic-release/python-semantic-release/pull/736


.. _changelog-v8.1.2:

v8.1.2 (2023-10-13)
===================

🪲 Bug Fixes
------------

* Correct lint errors (`a13a6c3`_)

* Error when running build command on windows systems (`PR#732`_, `2553657`_)

.. _2553657: https://github.com/python-semantic-release/python-semantic-release/commit/25536574760b407410f435441da533fafbf94402
.. _a13a6c3: https://github.com/python-semantic-release/python-semantic-release/commit/a13a6c37e180dc422599939a5725835306c18ff2
.. _PR#732: https://github.com/python-semantic-release/python-semantic-release/pull/732


.. _changelog-v8.1.1:

v8.1.1 (2023-09-19)
===================

🪲 Bug Fixes
------------

* Attribute error when logging non-strings (`PR#711`_, `75e6e48`_)

.. _75e6e48: https://github.com/python-semantic-release/python-semantic-release/commit/75e6e48129da8238a62d5eccac1ae55d0fee0f9f
.. _PR#711: https://github.com/python-semantic-release/python-semantic-release/pull/711


.. _changelog-v8.1.0:

v8.1.0 (2023-09-19)
===================

✨ Features
-----------

* Upgrade pydantic to v2 (`PR#714`_, `5a5c5d0`_)

📖 Documentation
----------------

* Fix typos (`PR#708`_, `2698b0e`_)

* Update project urls (`PR#715`_, `5fd5485`_)

.. _2698b0e: https://github.com/python-semantic-release/python-semantic-release/commit/2698b0e006ff7e175430b98450ba248ed523b341
.. _5a5c5d0: https://github.com/python-semantic-release/python-semantic-release/commit/5a5c5d0ee347750d7c417c3242d52e8ada50b217
.. _5fd5485: https://github.com/python-semantic-release/python-semantic-release/commit/5fd54856dfb6774feffc40d36d5bb0f421f04842
.. _PR#708: https://github.com/python-semantic-release/python-semantic-release/pull/708
.. _PR#714: https://github.com/python-semantic-release/python-semantic-release/pull/714
.. _PR#715: https://github.com/python-semantic-release/python-semantic-release/pull/715


.. _changelog-v8.0.8:

v8.0.8 (2023-08-26)
===================

🪲 Bug Fixes
------------

* Dynamic_import() import path split (`PR#686`_, `1007a06`_)

.. _1007a06: https://github.com/python-semantic-release/python-semantic-release/commit/1007a06d1e16beef6d18f44ff2e0e09921854b54
.. _PR#686: https://github.com/python-semantic-release/python-semantic-release/pull/686


.. _changelog-v8.0.7:

v8.0.7 (2023-08-16)
===================

🪲 Bug Fixes
------------

* Use correct upload url for github (`PR#661`_, `8a515ca`_)

.. _8a515ca: https://github.com/python-semantic-release/python-semantic-release/commit/8a515caf1f993aa653e024beda2fdb9e629cc42a
.. _PR#661: https://github.com/python-semantic-release/python-semantic-release/pull/661


.. _changelog-v8.0.6:

v8.0.6 (2023-08-13)
===================

🪲 Bug Fixes
------------

* **publish**: Improve error message when no tags found (`PR#683`_, `bdc06ea`_)

.. _bdc06ea: https://github.com/python-semantic-release/python-semantic-release/commit/bdc06ea061c19134d5d74bd9f168700dd5d9bcf5
.. _PR#683: https://github.com/python-semantic-release/python-semantic-release/pull/683


.. _changelog-v8.0.5:

v8.0.5 (2023-08-10)
===================

🪲 Bug Fixes
------------

* Don't warn about vcs token if ignore_token_for_push is true. (`PR#670`_, `f1a54a6`_)

📖 Documentation
----------------

* ``password`` should be ``token``. (`PR#670`_, `f1a54a6`_)

* Fix typo missing 's' in version_variable[s] in configuration.rst (`PR#668`_, `879186a`_)

.. _879186a: https://github.com/python-semantic-release/python-semantic-release/commit/879186aa09a3bea8bbe2b472f892cf7c0712e557
.. _f1a54a6: https://github.com/python-semantic-release/python-semantic-release/commit/f1a54a6c9a05b225b6474d50cd610eca19ec0c34
.. _PR#668: https://github.com/python-semantic-release/python-semantic-release/pull/668
.. _PR#670: https://github.com/python-semantic-release/python-semantic-release/pull/670


.. _changelog-v8.0.4:

v8.0.4 (2023-07-26)
===================

🪲 Bug Fixes
------------

* **changelog**: Use version as semver tag by default (`PR#653`_, `5984c77`_)

📖 Documentation
----------------

* Add Python 3.11 to classifiers in metadata (`PR#651`_, `5a32a24`_)

* Clarify usage of assets config option (`PR#655`_, `efa2b30`_)

.. _5984c77: https://github.com/python-semantic-release/python-semantic-release/commit/5984c7771edc37f0d7d57894adecc2591efc414d
.. _5a32a24: https://github.com/python-semantic-release/python-semantic-release/commit/5a32a24bf4128c39903f0c5d3bd0cb1ccba57e18
.. _efa2b30: https://github.com/python-semantic-release/python-semantic-release/commit/efa2b3019b41eb427f0e1c8faa21ad10664295d0
.. _PR#651: https://github.com/python-semantic-release/python-semantic-release/pull/651
.. _PR#653: https://github.com/python-semantic-release/python-semantic-release/pull/653
.. _PR#655: https://github.com/python-semantic-release/python-semantic-release/pull/655


.. _changelog-v8.0.3:

v8.0.3 (2023-07-21)
===================

🪲 Bug Fixes
------------

* Skip non-parsable versions when calculating next version (`PR#649`_, `88f25ea`_)

.. _88f25ea: https://github.com/python-semantic-release/python-semantic-release/commit/88f25eae62589cdf53dbc3dfcb167a3ae6cba2d3
.. _PR#649: https://github.com/python-semantic-release/python-semantic-release/pull/649


.. _changelog-v8.0.2:

v8.0.2 (2023-07-18)
===================

🪲 Bug Fixes
------------

* Handle missing configuration (`PR#644`_, `f15753c`_)

📖 Documentation
----------------

* Better description for tag_format usage (`2129b72`_)

* Clarify v8 breaking changes in GitHub action inputs (`PR#643`_, `cda050c`_)

* Correct version_toml example in migrating_from_v7.rst (`PR#641`_, `325d5e0`_)

.. _2129b72: https://github.com/python-semantic-release/python-semantic-release/commit/2129b729837eccc41a33dbb49785a8a30ce6b187
.. _325d5e0: https://github.com/python-semantic-release/python-semantic-release/commit/325d5e048bd89cb2a94c47029d4878b27311c0f0
.. _cda050c: https://github.com/python-semantic-release/python-semantic-release/commit/cda050cd9e789d81458157ee240ff99ec65c6f25
.. _f15753c: https://github.com/python-semantic-release/python-semantic-release/commit/f15753ce652f36cc03b108c667a26ab74bcbf95d
.. _PR#641: https://github.com/python-semantic-release/python-semantic-release/pull/641
.. _PR#643: https://github.com/python-semantic-release/python-semantic-release/pull/643
.. _PR#644: https://github.com/python-semantic-release/python-semantic-release/pull/644


.. _changelog-v8.0.1:

v8.0.1 (2023-07-17)
===================

🪲 Bug Fixes
------------

* Invalid version in Git history should not cause a release failure (`PR#632`_, `254430b`_)

📖 Documentation
----------------

* Reduce readthedocs formats and add entries to migration from v7 guide (`9b6ddfe`_)

* **migration**: Fix hyperlink (`PR#631`_, `5fbd52d`_)

.. _254430b: https://github.com/python-semantic-release/python-semantic-release/commit/254430b5cc5f032016b4c73168f0403c4d87541e
.. _5fbd52d: https://github.com/python-semantic-release/python-semantic-release/commit/5fbd52d7de4982b5689651201a0e07b445158645
.. _9b6ddfe: https://github.com/python-semantic-release/python-semantic-release/commit/9b6ddfef448f9de30fa2845034f76655d34a9912
.. _PR#631: https://github.com/python-semantic-release/python-semantic-release/pull/631
.. _PR#632: https://github.com/python-semantic-release/python-semantic-release/pull/632


.. _changelog-v8.0.0:

v8.0.0 (2023-07-16)
===================

✨ Features
-----------

* **publish-cmd**: Add ``--post-to-release-tag`` option to control where to publish (`PR#619`_,
  `ec30564`_)

* Make it easier to access commit messages in ParsedCommits (`PR#619`_, `ec30564`_)

* Remove publication of ``dists/`` to artifact repository (`PR#619`_, `ec30564`_)

* Rename 'upload' configuration section to 'publish' (`PR#619`_, `ec30564`_)

* **github-action**: Add GitHub Actions output variables (`PR#619`_, `ec30564`_)

* **version-cmd**: Add ``--skip-build`` option (`PR#619`_, `ec30564`_)

* **version-cmd** Add ``--strict`` version mode (`PR#619`_, `ec30564`_)

🪲 Bug Fixes
------------

* Add logging for token auth, use token for push (`PR#619`_, `ec30564`_)

* Caching for repo owner and name (`PR#619`_, `ec30564`_)

* Correct assets type in configuration (`PR#619`_, `ec30564`_)

* Correct assets type-annotation for RuntimeContext (`PR#619`_, `ec30564`_)

* Correct Dockerfile CLI command and GHA fetch (`PR#619`_, `ec30564`_)

* Correct handling of build commands (`PR#619`_, `ec30564`_)

* Correct logic for generating release notes (`PR#619`_, `ec30564`_)

* Create_or_update_release for Gitlab hvcs (`PR#619`_, `ec30564`_)

* Make additional attributes available for template authors (`PR#619`_, `ec30564`_)

* Only call Github Action output callback once defaults are set (`PR#619`_, `ec30564`_)

* Remove commit amending behavior (`PR#619`_, `ec30564`_)

* Resolve branch checkout logic in GHA (`PR#619`_, `ec30564`_)

* Resolve bug in changelog logic, enable upload to pypi (`PR#619`_, `ec30564`_)

* Resolve loss of tag_format configuration (`PR#619`_, `ec30564`_)

* **github-action**: Pin Debian version in Dockerfile (`PR#619`_, `ec30564`_)

* **github-action**: Correct input parsing (`PR#619`_, `ec30564`_)

* **github-action**: Mark container fs as safe for git to operate on (`PR#619`_, `ec30564`_)

* **github-action**: Quotation for git config command (`PR#619`_, `ec30564`_)

* **github-action**: Remove default for 'force' (`PR#619`_, `ec30564`_)

📖 Documentation
----------------

* Convert to Furo theme (`PR#619`_, `ec30564`_)

* Fix typo (`PR#619`_, `ec30564`_)

* Remove reference to dist publication (`PR#619`_, `ec30564`_)

* Update docs with additional required permissions (`PR#619`_, `ec30564`_)

* **changelog-templates**: fix typo (`PR#619`_, `ec30564`_)

♻️ Refactoring
---------------

* Remove verify-ci command (`PR#619`_, `ec30564`_)

💥 BREAKING CHANGES
--------------------

* numerous breaking changes, see :ref:`upgrade_v8` for more information

.. _ec30564: https://github.com/python-semantic-release/python-semantic-release/commit/ec30564b4ec732c001d76d3c09ba033066d2b6fe
.. _PR#619: https://github.com/python-semantic-release/python-semantic-release/pull/619


.. _changelog-v7.34.6:

v7.34.6 (2023-06-17)
====================

🪲 Bug Fixes
------------

* Relax invoke dependency constraint (`18ea200`_)

.. _18ea200: https://github.com/python-semantic-release/python-semantic-release/commit/18ea200633fd67e07f3d4121df5aa4c6dd29d154


.. _changelog-v7.34.5:

v7.34.5 (2023-06-17)
====================

🪲 Bug Fixes
------------

* Consider empty commits (`PR#608`_, `6f2e890`_)

.. _6f2e890: https://github.com/python-semantic-release/python-semantic-release/commit/6f2e8909636595d3cb5e858f42c63820cda45974
.. _PR#608: https://github.com/python-semantic-release/python-semantic-release/pull/608


.. _changelog-v7.34.4:

v7.34.4 (2023-06-15)
====================

🪲 Bug Fixes
------------

* Docker build fails installing git (`PR#605`_, `9e3eb97`_)

.. _9e3eb97: https://github.com/python-semantic-release/python-semantic-release/commit/9e3eb979783bc39ca564c2967c6c77eecba682e6
.. _PR#605: https://github.com/python-semantic-release/python-semantic-release/pull/605


.. _changelog-v7.34.3:

v7.34.3 (2023-06-01)
====================

🪲 Bug Fixes
------------

* Generate markdown linter compliant changelog headers & lists (`PR#597`_, `cc87400`_)

.. _cc87400: https://github.com/python-semantic-release/python-semantic-release/commit/cc87400d4a823350de7d02dc3172d2488c9517db
.. _PR#597: https://github.com/python-semantic-release/python-semantic-release/pull/597


.. _changelog-v7.34.2:

v7.34.2 (2023-05-29)
====================

🪲 Bug Fixes
------------

* Open all files with explicit utf-8 encoding (`PR#596`_, `cb71f35`_)

.. _cb71f35: https://github.com/python-semantic-release/python-semantic-release/commit/cb71f35c26c1655e675fa735fa880d39a2c8af9c
.. _PR#596: https://github.com/python-semantic-release/python-semantic-release/pull/596


.. _changelog-v7.34.1:

v7.34.1 (2023-05-28)
====================

🪲 Bug Fixes
------------

* Generate markdown linter compliant changelog headers & lists (`PR#594`_, `9d9d403`_)

.. _9d9d403: https://github.com/python-semantic-release/python-semantic-release/commit/9d9d40305c499c907335abe313e3ed122db0b154
.. _PR#594: https://github.com/python-semantic-release/python-semantic-release/pull/594


.. _changelog-v7.34.0:

v7.34.0 (2023-05-28)
====================

✨ Features
-----------

* Add option to only parse commits for current working directory (`PR#509`_, `cdf8116`_)

.. _cdf8116: https://github.com/python-semantic-release/python-semantic-release/commit/cdf8116c1e415363b10a01f541873e04ad874220
.. _PR#509: https://github.com/python-semantic-release/python-semantic-release/pull/509


.. _changelog-v7.33.5:

v7.33.5 (2023-05-19)
====================

🪲 Bug Fixes
------------

* Update docs and default config for gitmoji changes (`PR#590`_, `192da6e`_)

* Update sphinx dep (`PR#590`_, `192da6e`_)

📖 Documentation
----------------

* Update broken badge and add links (`PR#591`_, `0c23447`_)

.. _0c23447: https://github.com/python-semantic-release/python-semantic-release/commit/0c234475d27ad887b19170c82deb80293b3a95f1
.. _192da6e: https://github.com/python-semantic-release/python-semantic-release/commit/192da6e1352298b48630423d50191070a1c5ab24
.. _PR#590: https://github.com/python-semantic-release/python-semantic-release/pull/590
.. _PR#591: https://github.com/python-semantic-release/python-semantic-release/pull/591


.. _changelog-v7.33.4:

v7.33.4 (2023-05-14)
====================

🪲 Bug Fixes
------------

* If prerelease, publish prerelease (`PR#587`_, `927da9f`_)

.. _927da9f: https://github.com/python-semantic-release/python-semantic-release/commit/927da9f8feb881e02bc08b33dc559bd8e7fc41ab
.. _PR#587: https://github.com/python-semantic-release/python-semantic-release/pull/587


.. _changelog-v7.33.3:

v7.33.3 (2023-04-24)
====================

🪲 Bug Fixes
------------

* Trim emojis from config (`PR#583`_, `02902f7`_)

* Update Gitmojis according to official node module (`PR#582`_, `806fcfa`_)

📖 Documentation
----------------

* Grammar in ``docs/troubleshooting.rst`` (`PR#557`_, `bbe754a`_)

* Spelling and grammar in ``travis.rst`` (`PR#556`_, `3a76e9d`_)

* Update repository name (`PR#559`_, `5cdb05e`_)

.. _02902f7: https://github.com/python-semantic-release/python-semantic-release/commit/02902f73ee961565c2470c000f00947d9ef06cb1
.. _3a76e9d: https://github.com/python-semantic-release/python-semantic-release/commit/3a76e9d7505c421009eb3e953c32cccac2e70e07
.. _5cdb05e: https://github.com/python-semantic-release/python-semantic-release/commit/5cdb05e20f17b12890e1487c42d317dcbadd06c8
.. _806fcfa: https://github.com/python-semantic-release/python-semantic-release/commit/806fcfa4cfdd3df4b380afd015a68dc90d54215a
.. _bbe754a: https://github.com/python-semantic-release/python-semantic-release/commit/bbe754a3db9ce7132749e7902fe118b52f48ee42
.. _PR#556: https://github.com/python-semantic-release/python-semantic-release/pull/556
.. _PR#557: https://github.com/python-semantic-release/python-semantic-release/pull/557
.. _PR#559: https://github.com/python-semantic-release/python-semantic-release/pull/559
.. _PR#582: https://github.com/python-semantic-release/python-semantic-release/pull/582
.. _PR#583: https://github.com/python-semantic-release/python-semantic-release/pull/583


.. _changelog-v7.33.2:

v7.33.2 (2023-02-17)
====================

🪲 Bug Fixes
------------

* Inconsistent versioning between print-version and publish (`PR#524`_, `17d60e9`_)

.. _17d60e9: https://github.com/python-semantic-release/python-semantic-release/commit/17d60e9bf66f62e5845065486c9d5e450f74839a
.. _PR#524: https://github.com/python-semantic-release/python-semantic-release/pull/524


.. _changelog-v7.33.1:

v7.33.1 (2023-02-01)
====================

🪲 Bug Fixes
------------

* **action**: Mark container fs as safe for git (`PR#552`_, `2a55f68`_)

.. _2a55f68: https://github.com/python-semantic-release/python-semantic-release/commit/2a55f68e2b3cb9ffa9204c00ddbf12706af5c070
.. _PR#552: https://github.com/python-semantic-release/python-semantic-release/pull/552


.. _changelog-v7.33.0:

v7.33.0 (2023-01-15)
====================

✨ Features
-----------

* Add signing options to action (`31ad5eb`_)

* Update action with configuration options (`PR#518`_, `4664afe`_)

* **repository**: Add support for TWINE_CERT, closes `#521`_ (`PR#522`_, `d56e85d`_)

🪲 Bug Fixes
------------

* Changelog release commit search logic (`PR#530`_, `efb3410`_)

* **github-actions**: Bump Dockerfile to use Python 3.10 image, closes `#533`_ (`PR#536`_,
  `8f2185d`_)

* **action**: Fix environment variable names (`3c66218`_)

📖 Documentation
----------------

* Update documentation (`5cbdad2`_)

.. _#521: https://github.com/python-semantic-release/python-semantic-release/issues/521
.. _#533: https://github.com/python-semantic-release/python-semantic-release/issues/533
.. _31ad5eb: https://github.com/python-semantic-release/python-semantic-release/commit/31ad5eb5a25f0ea703afc295351104aefd66cac1
.. _3c66218: https://github.com/python-semantic-release/python-semantic-release/commit/3c66218640044adf263fcf9b2714cfc4b99c2e90
.. _4664afe: https://github.com/python-semantic-release/python-semantic-release/commit/4664afe5f80a04834e398fefb841b166a51d95b7
.. _5cbdad2: https://github.com/python-semantic-release/python-semantic-release/commit/5cbdad296034a792c9bf05e3700eac4f847eb469
.. _8f2185d: https://github.com/python-semantic-release/python-semantic-release/commit/8f2185d570b3966b667ac591ae523812e9d2e00f
.. _d56e85d: https://github.com/python-semantic-release/python-semantic-release/commit/d56e85d1f2ac66fb0b59af2178164ca915dbe163
.. _efb3410: https://github.com/python-semantic-release/python-semantic-release/commit/efb341036196c39b4694ca4bfa56c6b3e0827c6c
.. _PR#518: https://github.com/python-semantic-release/python-semantic-release/pull/518
.. _PR#522: https://github.com/python-semantic-release/python-semantic-release/pull/522
.. _PR#530: https://github.com/python-semantic-release/python-semantic-release/pull/530
.. _PR#536: https://github.com/python-semantic-release/python-semantic-release/pull/536
.. _PR#541: https://github.com/python-semantic-release/python-semantic-release/pull/541


.. _changelog-v7.32.2:

v7.32.2 (2022-10-22)
====================

🪲 Bug Fixes
------------

* Fix changelog generation in tag-mode (`PR#171`_, `482a62e`_)

📖 Documentation
----------------

* Fix code blocks (`PR#506`_, `24b7673`_)

.. _24b7673: https://github.com/python-semantic-release/python-semantic-release/commit/24b767339fcef1c843f7dd3188900adab05e03b1
.. _482a62e: https://github.com/python-semantic-release/python-semantic-release/commit/482a62ec374208b2d57675cb0b7f0ab9695849b9
.. _PR#171: https://github.com/python-semantic-release/python-semantic-release/pull/171
.. _PR#506: https://github.com/python-semantic-release/python-semantic-release/pull/506


.. _changelog-v7.32.1:

v7.32.1 (2022-10-07)
====================

🪲 Bug Fixes
------------

* Corrections for deprecation warnings (`PR#505`_, `d47afb6`_)

📖 Documentation
----------------

* Correct spelling mistakes (`PR#504`_, `3717e0d`_)

.. _3717e0d: https://github.com/python-semantic-release/python-semantic-release/commit/3717e0d8810f5d683847c7b0e335eeefebbf2921
.. _d47afb6: https://github.com/python-semantic-release/python-semantic-release/commit/d47afb6516238939e174f946977bf4880062a622
.. _PR#504: https://github.com/python-semantic-release/python-semantic-release/pull/504
.. _PR#505: https://github.com/python-semantic-release/python-semantic-release/pull/505


.. _changelog-v7.32.0:

v7.32.0 (2022-09-25)
====================

✨ Features
-----------

* Add setting for enforcing textual changelog sections, closes `#498`_ (`PR#502`_, `988437d`_)

📖 Documentation
----------------

* Correct documented default behavior for ``commit_version_number`` (`PR#497`_, `ffae2dc`_)

.. _#498: https://github.com/python-semantic-release/python-semantic-release/issues/498
.. _988437d: https://github.com/python-semantic-release/python-semantic-release/commit/988437d21e40d3e3b1c95ed66b535bdd523210de
.. _ffae2dc: https://github.com/python-semantic-release/python-semantic-release/commit/ffae2dc68f7f4bc13c5fd015acd43b457e568ada
.. _PR#497: https://github.com/python-semantic-release/python-semantic-release/pull/497
.. _PR#502: https://github.com/python-semantic-release/python-semantic-release/pull/502


.. _changelog-v7.31.4:

v7.31.4 (2022-08-23)
====================

🪲 Bug Fixes
------------

* Account for trailing newlines in commit messages, closes `#490`_ (`PR#495`_, `111b151`_)

.. _#490: https://github.com/python-semantic-release/python-semantic-release/issues/490
.. _111b151: https://github.com/python-semantic-release/python-semantic-release/commit/111b1518e8c8e2bd7535bd4c4b126548da384605
.. _PR#495: https://github.com/python-semantic-release/python-semantic-release/pull/495


.. _changelog-v7.31.3:

v7.31.3 (2022-08-22)
====================

🪲 Bug Fixes
------------

* Use ``commit_subject`` when searching for release commits (`PR#488`_, `3849ed9`_)

.. _3849ed9: https://github.com/python-semantic-release/python-semantic-release/commit/3849ed992c3cff9054b8690bcf59e49768f84f47
.. _PR#488: https://github.com/python-semantic-release/python-semantic-release/pull/488


.. _changelog-v7.31.2:

v7.31.2 (2022-07-29)
====================

🪲 Bug Fixes
------------

* Add better handling of missing changelog placeholder, closes `#454`_ (`e7a0e81`_)

* Add repo=None when not in git repo, closes `#422`_ (`40be804`_)

📖 Documentation
----------------

* Add example for pyproject.toml (`2a4b8af`_)

.. _#422: https://github.com/python-semantic-release/python-semantic-release/issues/422
.. _#454: https://github.com/python-semantic-release/python-semantic-release/issues/454
.. _2a4b8af: https://github.com/python-semantic-release/python-semantic-release/commit/2a4b8af1c2893a769c02476bb92f760c8522bd7a
.. _40be804: https://github.com/python-semantic-release/python-semantic-release/commit/40be804c09ab8a036fb135c9c38a63f206d2742c
.. _e7a0e81: https://github.com/python-semantic-release/python-semantic-release/commit/e7a0e81c004ade73ed927ba4de8c3e3ccaf0047c


.. _changelog-v7.31.1:

v7.31.1 (2022-07-29)
====================

🪲 Bug Fixes
------------

* Update git email in action, closes `#473`_ (`0ece6f2`_)

.. _#473: https://github.com/python-semantic-release/python-semantic-release/issues/473
.. _0ece6f2: https://github.com/python-semantic-release/python-semantic-release/commit/0ece6f263ff02a17bb1e00e7ed21c490f72e3d00


.. _changelog-v7.31.0:

v7.31.0 (2022-07-29)
====================

✨ Features
-----------

* Add prerelease-patch and no-prerelease-patch flags for whether to auto-bump prereleases
  (`b4e5b62`_)

* Override repository_url w REPOSITORY_URL env var (`PR#439`_, `cb7578c`_)

🪲 Bug Fixes
------------

* :bug: fix get_current_release_version for tag_only version_source (`cad09be`_)

.. _b4e5b62: https://github.com/python-semantic-release/python-semantic-release/commit/b4e5b626074f969e4140c75fdac837a0625cfbf6
.. _cad09be: https://github.com/python-semantic-release/python-semantic-release/commit/cad09be9ba067f1c882379c0f4b28115a287fc2b
.. _cb7578c: https://github.com/python-semantic-release/python-semantic-release/commit/cb7578cf005b8bd65d9b988f6f773e4c060982e3
.. _PR#439: https://github.com/python-semantic-release/python-semantic-release/pull/439


.. _changelog-v7.30.2:

v7.30.2 (2022-07-26)
====================

🪲 Bug Fixes
------------

* Declare additional_options as action inputs (`PR#481`_, `cb5d8c7`_)

.. _cb5d8c7: https://github.com/python-semantic-release/python-semantic-release/commit/cb5d8c7ce7d013fcfabd7696b5ffb846a8a6f853
.. _PR#481: https://github.com/python-semantic-release/python-semantic-release/pull/481


.. _changelog-v7.30.1:

v7.30.1 (2022-07-25)
====================

🪲 Bug Fixes
------------

* Don't use commit_subject for tag pattern matching (`PR#480`_, `ac3f11e`_)

.. _ac3f11e: https://github.com/python-semantic-release/python-semantic-release/commit/ac3f11e689f4a290d20b68b9c5c214098eb61b5f
.. _PR#480: https://github.com/python-semantic-release/python-semantic-release/pull/480


.. _changelog-v7.30.0:

v7.30.0 (2022-07-25)
====================

✨ Features
-----------

* Add ``additional_options`` input for GitHub Action (`PR#477`_, `aea60e3`_)

🪲 Bug Fixes
------------

* Allow empty additional options (`PR#479`_, `c9b2514`_)

.. _aea60e3: https://github.com/python-semantic-release/python-semantic-release/commit/aea60e3d290c6fe3137bff21e0db1ed936233776
.. _c9b2514: https://github.com/python-semantic-release/python-semantic-release/commit/c9b2514d3e164b20e78b33f60989d78c2587e1df
.. _PR#477: https://github.com/python-semantic-release/python-semantic-release/pull/477
.. _PR#479: https://github.com/python-semantic-release/python-semantic-release/pull/479


.. _changelog-v7.29.7:

v7.29.7 (2022-07-24)
====================

🪲 Bug Fixes
------------

* Ignore dependency version bumps when parsing version from commit logs (`PR#476`_, `51bcb78`_)

.. _51bcb78: https://github.com/python-semantic-release/python-semantic-release/commit/51bcb780a9f55fadfaf01612ff65c1f92642c2c1
.. _PR#476: https://github.com/python-semantic-release/python-semantic-release/pull/476


.. _changelog-v7.29.6:

v7.29.6 (2022-07-15)
====================

🪲 Bug Fixes
------------

* Allow changing prerelease tag using CLI flags (`PR#466`_, `395bf4f`_)

.. _395bf4f: https://github.com/python-semantic-release/python-semantic-release/commit/395bf4f2de73663c070f37cced85162d41934213
.. _PR#466: https://github.com/python-semantic-release/python-semantic-release/pull/466


.. _changelog-v7.29.5:

v7.29.5 (2022-07-14)
====================

🪲 Bug Fixes
------------

* Add packaging module requirement (`PR#469`_, `b99c9fa`_)

* **publish**: Get version bump for current release (`PR#467`_, `dd26888`_)

.. _b99c9fa: https://github.com/python-semantic-release/python-semantic-release/commit/b99c9fa88dc25e5ceacb131cd93d9079c4fb2c86
.. _dd26888: https://github.com/python-semantic-release/python-semantic-release/commit/dd26888a923b2f480303c19f1916647de48b02bf
.. _PR#467: https://github.com/python-semantic-release/python-semantic-release/pull/467
.. _PR#469: https://github.com/python-semantic-release/python-semantic-release/pull/469


.. _changelog-v7.29.4:

v7.29.4 (2022-06-29)
====================

🪲 Bug Fixes
------------

* Add text for empty ValueError (`PR#461`_, `733254a`_)

.. _733254a: https://github.com/python-semantic-release/python-semantic-release/commit/733254a99320d8c2f964d799ac4ec29737867faa
.. _PR#461: https://github.com/python-semantic-release/python-semantic-release/pull/461


.. _changelog-v7.29.3:

v7.29.3 (2022-06-26)
====================

🪲 Bug Fixes
------------

* Ensure that assets can be uploaded successfully on custom GitHub servers (`PR#458`_, `32b516d`_)

.. _32b516d: https://github.com/python-semantic-release/python-semantic-release/commit/32b516d7aded4afcafe4aa56d6a5a329b3fc371d
.. _PR#458: https://github.com/python-semantic-release/python-semantic-release/pull/458


.. _changelog-v7.29.2:

v7.29.2 (2022-06-20)
====================

🪲 Bug Fixes
------------

* Ensure should_bump checks against release version if not prerelease (`PR#457`_, `da0606f`_)

.. _da0606f: https://github.com/python-semantic-release/python-semantic-release/commit/da0606f0d67ada5f097c704b9423ead3b5aca6b2
.. _PR#457: https://github.com/python-semantic-release/python-semantic-release/pull/457


.. _changelog-v7.29.1:

v7.29.1 (2022-06-01)
====================

🪲 Bug Fixes
------------

* Capture correct release version when patch has more than one digit (`PR#448`_, `426cdc7`_)

.. _426cdc7: https://github.com/python-semantic-release/python-semantic-release/commit/426cdc7d7e0140da67f33b6853af71b2295aaac2
.. _PR#448: https://github.com/python-semantic-release/python-semantic-release/pull/448


.. _changelog-v7.29.0:

v7.29.0 (2022-05-27)
====================

✨ Features
-----------

* Allow using ssh-key to push version while using token to publish to hvcs (`PR#419`_, `7b2dffa`_)

* **config**: Add ignore_token_for_push param (`PR#419`_, `7b2dffa`_)

🪲 Bug Fixes
------------

* Fix and refactor prerelease (`PR#435`_, `94c9494`_)

* **test**: Override GITHUB_ACTOR env (`PR#419`_, `7b2dffa`_)

📖 Documentation
----------------

* Add documentation for ignore_token_for_push (`PR#419`_, `7b2dffa`_)

.. _7b2dffa: https://github.com/python-semantic-release/python-semantic-release/commit/7b2dffadf43c77d5e0eea307aefcee5c7744df5c
.. _94c9494: https://github.com/python-semantic-release/python-semantic-release/commit/94c94942561f85f48433c95fd3467e03e0893ab4
.. _PR#419: https://github.com/python-semantic-release/python-semantic-release/pull/419
.. _PR#435: https://github.com/python-semantic-release/python-semantic-release/pull/435


.. _changelog-v7.28.1:

v7.28.1 (2022-04-14)
====================

🪲 Bug Fixes
------------

* Fix getting current version when ``version_source=tag_only`` (`PR#437`_, `b247936`_)

.. _b247936: https://github.com/python-semantic-release/python-semantic-release/commit/b247936a81c0d859a34bf9f17ab8ca6a80488081
.. _PR#437: https://github.com/python-semantic-release/python-semantic-release/pull/437


.. _changelog-v7.28.0:

v7.28.0 (2022-04-11)
====================

✨ Features
-----------

* Add ``tag_only`` option for ``version_source``, closes `#354`_ (`PR#436`_, `cf74339`_)

.. _#354: https://github.com/python-semantic-release/python-semantic-release/issues/354
.. _cf74339: https://github.com/python-semantic-release/python-semantic-release/commit/cf743395456a86c62679c2c0342502af043bfc3b
.. _PR#436: https://github.com/python-semantic-release/python-semantic-release/pull/436


.. _changelog-v7.27.1:

v7.27.1 (2022-04-03)
====================

🪲 Bug Fixes
------------

* **prerelease**: Pass prerelease option to get_current_version (`PR#432`_, `aabab0b`_)

.. _aabab0b: https://github.com/python-semantic-release/python-semantic-release/commit/aabab0b7ce647d25e0c78ae6566f1132ece9fcb9
.. _PR#432: https://github.com/python-semantic-release/python-semantic-release/pull/432


.. _changelog-v7.27.0:

v7.27.0 (2022-03-15)
====================

✨ Features
-----------

* Add git-lfs to docker container (`PR#427`_, `184e365`_)

.. _184e365: https://github.com/python-semantic-release/python-semantic-release/commit/184e3653932979b82e5a62b497f2a46cbe15ba87
.. _PR#427: https://github.com/python-semantic-release/python-semantic-release/pull/427


.. _changelog-v7.26.0:

v7.26.0 (2022-03-07)
====================

✨ Features
-----------

* **publish-cmd**: add ``--prerelease`` cli flag to enable prerelease versioning (`PR#413`_,
  `7064265`_)

* **version-cmd**: add ``--prerelease`` cli flag to enable prerelease versioning (`PR#413`_,
  `7064265`_)

📖 Documentation
----------------

* Added basic info about prerelease versioning (`PR#413`_, `7064265`_)

.. _7064265: https://github.com/python-semantic-release/python-semantic-release/commit/7064265627a2aba09caa2873d823b594e0e23e77
.. _PR#413: https://github.com/python-semantic-release/python-semantic-release/pull/413


.. _changelog-v7.25.2:

v7.25.2 (2022-02-24)
====================

🪲 Bug Fixes
------------

* **gitea**: Use form-data from asset upload (`PR#421`_, `e011944`_)

.. _e011944: https://github.com/python-semantic-release/python-semantic-release/commit/e011944987885f75b80fe16a363f4befb2519a91
.. _PR#421: https://github.com/python-semantic-release/python-semantic-release/pull/421


.. _changelog-v7.25.1:

v7.25.1 (2022-02-23)
====================

🪲 Bug Fixes
------------

* **gitea**: Build status and asset upload (`PR#420`_, `57db81f`_)

* **gitea**: Handle list build status response (`PR#420`_, `57db81f`_)

.. _57db81f: https://github.com/python-semantic-release/python-semantic-release/commit/57db81f4c6b96da8259e3bad9137eaccbcd10f6e
.. _PR#420: https://github.com/python-semantic-release/python-semantic-release/pull/420


.. _changelog-v7.25.0:

v7.25.0 (2022-02-17)
====================

✨ Features
-----------

* **hvcs**: Add gitea support (`PR#412`_, `b7e7936`_)

📖 Documentation
----------------

* Document tag_commit, closes `#410`_ (`b631ca0`_)


.. _#410: https://github.com/python-semantic-release/python-semantic-release/issues/410
.. _b631ca0: https://github.com/python-semantic-release/python-semantic-release/commit/b631ca0a79cb2d5499715d43688fc284cffb3044
.. _b7e7936: https://github.com/python-semantic-release/python-semantic-release/commit/b7e7936331b7939db09abab235c8866d800ddc1a
.. _PR#412: https://github.com/python-semantic-release/python-semantic-release/pull/412


.. _changelog-v7.24.0:

v7.24.0 (2022-01-24)
====================

✨ Features
-----------

* Include additional changes in release commits (`3e34f95`_)

.. _3e34f95: https://github.com/python-semantic-release/python-semantic-release/commit/3e34f957ff5a3ec6e6f984cc4a79a38ce4391ea9


.. _changelog-v7.23.0:

v7.23.0 (2021-11-30)
====================

✨ Features
-----------

* Support Github Enterprise server (`b4e01f1`_)

.. _b4e01f1: https://github.com/python-semantic-release/python-semantic-release/commit/b4e01f1b7e841263fa84f57f0ac331f7c0b31954


.. _changelog-v7.22.0:

v7.22.0 (2021-11-21)
====================

✨ Features
-----------

* **parser_angular**: Allow customization in parser (`298eebb`_)

🪲 Bug Fixes
------------

* Address PR feedback for ``parser_angular.py`` (`f7bc458`_)

.. _298eebb: https://github.com/python-semantic-release/python-semantic-release/commit/298eebbfab5c083505036ba1df47a5874a1eed6e
.. _f7bc458: https://github.com/python-semantic-release/python-semantic-release/commit/f7bc45841e6a5c762f99f936c292cee25fabcd02


.. _changelog-v7.21.0:

v7.21.0 (2021-11-21)
====================

✨ Features
-----------

* Use gitlab-ci or github actions env vars, closes `#363`_ (`8ca8dd4`_)

🪲 Bug Fixes
------------

* Remove invalid repository exception (`746b62d`_)

.. _#363: https://github.com/python-semantic-release/python-semantic-release/issues/363
.. _746b62d: https://github.com/python-semantic-release/python-semantic-release/commit/746b62d4e207a5d491eecd4ca96d096eb22e3bed
.. _8ca8dd4: https://github.com/python-semantic-release/python-semantic-release/commit/8ca8dd40f742f823af147928bd75a9577c50d0fd


.. _changelog-v7.20.0:

v7.20.0 (2021-11-21)
====================

✨ Features
-----------

* Allow custom environment variable names (`PR#392`_, `372cda3`_)

* Rewrite Twine adapter for uploading to artifact repositories (`cfb20af`_)

🪲 Bug Fixes
------------

* Don't use linux commands on windows (`PR#393`_, `5bcccd2`_)

* Mypy errors in vcs_helpers (`13ca0fe`_)

* Skip removing the build folder if it doesn't exist (`8e79fdc`_)

📖 Documentation
----------------

* Clean typos and add section for repository upload (`1efa18a`_)

.. _13ca0fe: https://github.com/python-semantic-release/python-semantic-release/commit/13ca0fe650125be2f5e953f6193fdc4d44d3c75a
.. _1efa18a: https://github.com/python-semantic-release/python-semantic-release/commit/1efa18a3a55134d6bc6e4572ab025e24082476cd
.. _372cda3: https://github.com/python-semantic-release/python-semantic-release/commit/372cda3497f16ead2209e6e1377d38f497144883
.. _5bcccd2: https://github.com/python-semantic-release/python-semantic-release/commit/5bcccd21cc8be3289db260e645fec8dc6a592abd
.. _8e79fdc: https://github.com/python-semantic-release/python-semantic-release/commit/8e79fdc107ffd852a91dfb5473e7bd1dfaba4ee5
.. _cfb20af: https://github.com/python-semantic-release/python-semantic-release/commit/cfb20af79a8e25a77aee9ff72deedcd63cb7f62f
.. _PR#392: https://github.com/python-semantic-release/python-semantic-release/pull/392
.. _PR#393: https://github.com/python-semantic-release/python-semantic-release/pull/393


.. _changelog-v7.19.2:

v7.19.2 (2021-09-04)
====================

🪲 Bug Fixes
------------

* Fixed ImproperConfig import error (`PR#377`_, `b011a95`_)

.. _b011a95: https://github.com/python-semantic-release/python-semantic-release/commit/b011a9595df4240cb190bfb1ab5b6d170e430dfc
.. _PR#377: https://github.com/python-semantic-release/python-semantic-release/pull/377


.. _changelog-v7.19.1:

v7.19.1 (2021-08-17)
====================

🪲 Bug Fixes
------------

* Add get_formatted_tag helper instead of hardcoded v-prefix in the git tags (`1a354c8`_)

.. _1a354c8: https://github.com/python-semantic-release/python-semantic-release/commit/1a354c86abad77563ebce9a6944256461006f3c7


.. _changelog-v7.19.0:

v7.19.0 (2021-08-16)
====================

✨ Features
-----------

* Custom git tag format support (`PR#373`_, `1d76632`_)

📖 Documentation
----------------

* **configuration**: define ``tag_format`` usage & resulting effect (`PR#373`_, `1d76632`_)

* **parser**: Documentation for scipy-parser (`45ee34a`_)

.. _1d76632: https://github.com/python-semantic-release/python-semantic-release/commit/1d76632043bf0b6076d214a63c92013624f4b95e
.. _45ee34a: https://github.com/python-semantic-release/python-semantic-release/commit/45ee34aa21443860a6c2cd44a52da2f353b960bf
.. _PR#373: https://github.com/python-semantic-release/python-semantic-release/pull/373


.. _changelog-v7.18.0:

v7.18.0 (2021-08-09)
====================

✨ Features
-----------

* Add support for non-prefixed tags (`PR#366`_, `0fee4dd`_)

📖 Documentation
----------------

* Clarify second argument of ParsedCommit (`086ddc2`_)

.. _086ddc2: https://github.com/python-semantic-release/python-semantic-release/commit/086ddc28f06522453328f5ea94c873bd202ff496
.. _0fee4dd: https://github.com/python-semantic-release/python-semantic-release/commit/0fee4ddb5baaddf85ed6b76e76a04474a5f97d0a
.. _PR#366: https://github.com/python-semantic-release/python-semantic-release/pull/366


.. _changelog-v7.17.0:

v7.17.0 (2021-08-07)
====================

✨ Features
-----------

* **parser**: Add scipy style parser (`PR#369`_, `51a3921`_)

.. _51a3921: https://github.com/python-semantic-release/python-semantic-release/commit/51a39213ea120c4bbd7a57b74d4f0cc3103da9f5
.. _PR#369: https://github.com/python-semantic-release/python-semantic-release/pull/369


.. _changelog-v7.16.4:

v7.16.4 (2021-08-03)
====================

🪲 Bug Fixes
------------

* Correct rendering of gitlab issue references, closes `#358`_ (`07429ec`_)

.. _#358: https://github.com/python-semantic-release/python-semantic-release/issues/358
.. _07429ec: https://github.com/python-semantic-release/python-semantic-release/commit/07429ec4a32d32069f25ec77b4bea963bd5d2a00


.. _changelog-v7.16.3:

v7.16.3 (2021-07-29)
====================

🪲 Bug Fixes
------------

* Print right info if token is not set, closes `#360`_ (`PR#361`_, `a275a7a`_)

.. _#360: https://github.com/python-semantic-release/python-semantic-release/issues/360
.. _a275a7a: https://github.com/python-semantic-release/python-semantic-release/commit/a275a7a17def85ff0b41d254e4ee42772cce1981
.. _PR#361: https://github.com/python-semantic-release/python-semantic-release/pull/361


.. _changelog-v7.16.2:

v7.16.2 (2021-06-25)
====================

🪲 Bug Fixes
------------

* Use release-api for gitlab (`1ef5cab`_)

📖 Documentation
----------------

* Recommend setting a concurrency group for GitHub Actions (`34b0735`_)

* Update trove classifiers to reflect supported versions (`PR#344`_, `7578004`_)

.. _1ef5cab: https://github.com/python-semantic-release/python-semantic-release/commit/1ef5caba2d8dd0f2647bc51ede0ef7152d8b7b8d
.. _34b0735: https://github.com/python-semantic-release/python-semantic-release/commit/34b07357ab3f4f4aa787b71183816ec8aaf334a8
.. _7578004: https://github.com/python-semantic-release/python-semantic-release/commit/7578004ed4b20c2bd553782443dfd77535faa377
.. _PR#344: https://github.com/python-semantic-release/python-semantic-release/pull/344


.. _changelog-v7.16.1:

v7.16.1 (2021-06-08)
====================

🪲 Bug Fixes
------------

* Tomlkit should stay at 0.7.0 (`769a5f3`_)

.. _769a5f3: https://github.com/python-semantic-release/python-semantic-release/commit/769a5f31115cdb1f43f19a23fe72b96a8c8ba0fc


.. _changelog-v7.16.0:

v7.16.0 (2021-06-08)
====================

✨ Features
-----------

* Add option to omit tagging (`PR#341`_, `20603e5`_)

.. _20603e5: https://github.com/python-semantic-release/python-semantic-release/commit/20603e53116d4f05e822784ce731b42e8cbc5d8f
.. _PR#341: https://github.com/python-semantic-release/python-semantic-release/pull/341


.. _changelog-v7.15.6:

v7.15.6 (2021-06-08)
====================

🪲 Bug Fixes
------------

* Update click and tomlkit (`PR#339`_, `947ea3b`_)

.. _947ea3b: https://github.com/python-semantic-release/python-semantic-release/commit/947ea3bc0750735941446cf4a87bae20e750ba12
.. _PR#339: https://github.com/python-semantic-release/python-semantic-release/pull/339


.. _changelog-v7.15.5:

v7.15.5 (2021-05-26)
====================

🪲 Bug Fixes
------------

* Pin tomlkit to 0.7.0 (`2cd0db4`_)

.. _2cd0db4: https://github.com/python-semantic-release/python-semantic-release/commit/2cd0db4537bb9497b72eb496f6bab003070672ab


.. _changelog-v7.15.4:

v7.15.4 (2021-04-29)
====================

🪲 Bug Fixes
------------

* Change log level of failed toml loading, closes `#235`_ (`24bb079`_)

.. _#235: https://github.com/python-semantic-release/python-semantic-release/issues/235
.. _24bb079: https://github.com/python-semantic-release/python-semantic-release/commit/24bb079cbeff12e7043dd35dd0b5ae03192383bb


.. _changelog-v7.15.3:

v7.15.3 (2021-04-03)
====================

🪲 Bug Fixes
------------

* Add venv to path in github action (`583c5a1`_)

.. _583c5a1: https://github.com/python-semantic-release/python-semantic-release/commit/583c5a13e40061fc544b82decfe27a6c34f6d265


.. _changelog-v7.15.2:

v7.15.2 (2021-04-03)
====================

🪲 Bug Fixes
------------

* Run semantic-release in virtualenv in the github action, closes `#331`_ (`b508ea9`_)

* Set correct path for venv in action script (`aac02b5`_)

* Use absolute path for venv in github action (`d4823b3`_)

📖 Documentation
----------------

* Clarify that HVCS should be lowercase, closes `#330`_ (`da0ab0c`_)

.. _#330: https://github.com/python-semantic-release/python-semantic-release/issues/330
.. _#331: https://github.com/python-semantic-release/python-semantic-release/issues/331
.. _aac02b5: https://github.com/python-semantic-release/python-semantic-release/commit/aac02b5a44a6959328d5879578aa3536bdf856c2
.. _b508ea9: https://github.com/python-semantic-release/python-semantic-release/commit/b508ea9f411c1cd4f722f929aab9f0efc0890448
.. _d4823b3: https://github.com/python-semantic-release/python-semantic-release/commit/d4823b3b6b1fcd5c33b354f814643c9aaf85a06a
.. _da0ab0c: https://github.com/python-semantic-release/python-semantic-release/commit/da0ab0c62c4ce2fa0d815e5558aeec1a1e23bc89


.. _changelog-v7.15.1:

v7.15.1 (2021-03-26)
====================

🪲 Bug Fixes
------------

* Add support for setting build_command to "false", closes `#328`_ (`520cf1e`_)

* Upgrade python-gitlab range, closes `#329`_ (`abfacc4`_)

📖 Documentation
----------------

* Add common options to documentation, closes `#327`_ (`20d79a5`_)

.. _#327: https://github.com/python-semantic-release/python-semantic-release/issues/327
.. _#328: https://github.com/python-semantic-release/python-semantic-release/issues/328
.. _#329: https://github.com/python-semantic-release/python-semantic-release/issues/329
.. _20d79a5: https://github.com/python-semantic-release/python-semantic-release/commit/20d79a51bffa26d40607c1b77d10912992279112
.. _520cf1e: https://github.com/python-semantic-release/python-semantic-release/commit/520cf1eaa7816d0364407dbd17b5bc7c79806086
.. _abfacc4: https://github.com/python-semantic-release/python-semantic-release/commit/abfacc432300941d57488842e41c06d885637e6c


.. _changelog-v7.15.0:

v7.15.0 (2021-02-18)
====================

✨ Features
-----------

* Allow the use of .pypirc for twine uploads (`PR#325`_, `6bc56b8`_)

📖 Documentation
----------------

* Add documentation for releasing on a Jenkins instance (`PR#324`_, `77ad988`_)

.. _6bc56b8: https://github.com/python-semantic-release/python-semantic-release/commit/6bc56b8aa63069a25a828a2d1a9038ecd09b7d5d
.. _77ad988: https://github.com/python-semantic-release/python-semantic-release/commit/77ad988a2057be59e4559614a234d6871c06ee37
.. _PR#324: https://github.com/python-semantic-release/python-semantic-release/pull/324
.. _PR#325: https://github.com/python-semantic-release/python-semantic-release/pull/325


.. _changelog-v7.14.0:

v7.14.0 (2021-02-11)
====================

✨ Features
-----------

* **checks**: Add support for Jenkins CI (`PR#322`_, `3e99855`_)

📖 Documentation
----------------

* Correct casing on proper nouns (`PR#320`_, `d51b999`_)

* Correcting Python casing (`PR#320`_, `d51b999`_)

* Correcting Semantic Versioning casing (`PR#320`_, `d51b999`_)

.. _3e99855: https://github.com/python-semantic-release/python-semantic-release/commit/3e99855c6bc72b3e9a572c58cc14e82ddeebfff8
.. _d51b999: https://github.com/python-semantic-release/python-semantic-release/commit/d51b999a245a4e56ff7a09d0495c75336f2f150d
.. _PR#320: https://github.com/python-semantic-release/python-semantic-release/pull/320
.. _PR#322: https://github.com/python-semantic-release/python-semantic-release/pull/322


.. _changelog-v7.13.2:

v7.13.2 (2021-01-29)
====================

🪲 Bug Fixes
------------

* Crash when TOML has no PSR section (`PR#319`_, `5f8ab99`_)

* Fix crash when TOML has no PSR section (`PR#319`_, `5f8ab99`_)

📖 Documentation
----------------

* Fix ``version_toml`` example for Poetry (`PR#318`_, `39acb68`_)

.. _39acb68: https://github.com/python-semantic-release/python-semantic-release/commit/39acb68bfffe8242040e476893639ba26fa0d6b5
.. _5f8ab99: https://github.com/python-semantic-release/python-semantic-release/commit/5f8ab99bf7254508f4b38fcddef2bdde8dd15a4c
.. _PR#318: https://github.com/python-semantic-release/python-semantic-release/pull/318
.. _PR#319: https://github.com/python-semantic-release/python-semantic-release/pull/319


.. _changelog-v7.13.1:

v7.13.1 (2021-01-26)
====================

🪲 Bug Fixes
------------

* Use multiline version_pattern match in replace, closes `#306`_ (`PR#315`_, `1a85af4`_)

.. _#306: https://github.com/python-semantic-release/python-semantic-release/issues/306
.. _1a85af4: https://github.com/python-semantic-release/python-semantic-release/commit/1a85af434325ce52e11b49895e115f7a936e417e
.. _PR#315: https://github.com/python-semantic-release/python-semantic-release/pull/315


.. _changelog-v7.13.0:

v7.13.0 (2021-01-26)
====================

✨ Features
-----------

* Support toml files for version declaration, closes `#245`_, `#275`_ (`PR#307`_, `9b62a7e`_)

.. _#245: https://github.com/python-semantic-release/python-semantic-release/issues/245
.. _#275: https://github.com/python-semantic-release/python-semantic-release/issues/275
.. _9b62a7e: https://github.com/python-semantic-release/python-semantic-release/commit/9b62a7e377378667e716384684a47cdf392093fa
.. _PR#307: https://github.com/python-semantic-release/python-semantic-release/pull/307


.. _changelog-v7.12.0:

v7.12.0 (2021-01-25)
====================

✨ Features
-----------

* **github**: Retry GitHub API requests on failure (`PR#314`_, `ac241ed`_)

🪲 Bug Fixes
------------

* **github**: Add retries to github API requests (`PR#314`_, `ac241ed`_)

📖 Documentation
----------------

* **actions**: Pat must be passed to checkout step too, closes `#311`_ (`e2d8e47`_)

.. _#311: https://github.com/python-semantic-release/python-semantic-release/issues/311
.. _ac241ed: https://github.com/python-semantic-release/python-semantic-release/commit/ac241edf4de39f4fc0ff561a749fa85caaf9e2ae
.. _e2d8e47: https://github.com/python-semantic-release/python-semantic-release/commit/e2d8e47d2b02860881381318dcc088e150c0fcde
.. _PR#314: https://github.com/python-semantic-release/python-semantic-release/pull/314


.. _changelog-v7.11.0:

v7.11.0 (2021-01-08)
====================

✨ Features
-----------

* **print-version**: Add print-version command to output version (`512e3d9`_)

🪲 Bug Fixes
------------

* Add dot to --define option help (`eb4107d`_)

* Avoid Unknown bump level 0 message (`8ab624c`_)

* **actions**: Fix github actions with new main location (`6666672`_)

⚙️ Build System
----------------

* Add __main__.py magic file (`e93f36a`_)

.. _512e3d9: https://github.com/python-semantic-release/python-semantic-release/commit/512e3d92706055bdf8d08b7c82927d3530183079
.. _6666672: https://github.com/python-semantic-release/python-semantic-release/commit/6666672d3d97ab7cdf47badfa3663f1a69c2dbdf
.. _8ab624c: https://github.com/python-semantic-release/python-semantic-release/commit/8ab624cf3508b57a9656a0a212bfee59379d6f8b
.. _e93f36a: https://github.com/python-semantic-release/python-semantic-release/commit/e93f36a7a10e48afb42c1dc3d860a5e2a07cf353
.. _eb4107d: https://github.com/python-semantic-release/python-semantic-release/commit/eb4107d2efdf8c885c8ae35f48f1b908d1fced32


.. _changelog-v7.10.0:

v7.10.0 (2021-01-08)
====================

✨ Features
-----------

* **build**: Allow falsy values for build_command to disable build step (`c07a440`_)

📖 Documentation
----------------

* Fix incorrect reference syntax (`42027f0`_)

* Rewrite getting started page (`97a9046`_)

.. _42027f0: https://github.com/python-semantic-release/python-semantic-release/commit/42027f0d2bb64f4c9eaec65112bf7b6f67568e60
.. _97a9046: https://github.com/python-semantic-release/python-semantic-release/commit/97a90463872502d1207890ae1d9dd008b1834385
.. _c07a440: https://github.com/python-semantic-release/python-semantic-release/commit/c07a440f2dfc45a2ad8f7c454aaac180c4651f70


.. _changelog-v7.9.0:

v7.9.0 (2020-12-21)
===================

✨ Features
-----------

* **hvcs**: Add hvcs_domain config option, closes `#277`_ (`ab3061a`_)

🪲 Bug Fixes
------------

* **history**: Coerce version to string (`PR#298`_, `d4cdc3d`_)

* **history**: Require semver >= 2.10 (`5087e54`_)

.. _#277: https://github.com/python-semantic-release/python-semantic-release/issues/277
.. _5087e54: https://github.com/python-semantic-release/python-semantic-release/commit/5087e549399648cf2e23339a037b33ca8b62d954
.. _ab3061a: https://github.com/python-semantic-release/python-semantic-release/commit/ab3061ae93c49d71afca043b67b361e2eb2919e6
.. _d4cdc3d: https://github.com/python-semantic-release/python-semantic-release/commit/d4cdc3d3cd2d93f2a78f485e3ea107ac816c7d00
.. _PR#298: https://github.com/python-semantic-release/python-semantic-release/pull/298


.. _changelog-v7.8.2:

v7.8.2 (2020-12-19)
===================

✨ Features
-----------

* **repository**: Add to settings artifact repository (`f4ef373`_)

🪲 Bug Fixes
------------

* **cli**: Skip remove_dist where not needed (`04817d4`_)

.. _04817d4: https://github.com/python-semantic-release/python-semantic-release/commit/04817d4ecfc693195e28c80455bfbb127485f36b
.. _f4ef373: https://github.com/python-semantic-release/python-semantic-release/commit/f4ef3733b948282fba5a832c5c0af134609b26d2


.. _changelog-v7.8.1:

v7.8.1 (2020-12-18)
===================

🪲 Bug Fixes
------------

* Filenames with unknown mimetype are now properly uploaded to github release (`f3ece78`_)

* **logs**: Fix TypeError when enabling debug logs (`2591a94`_)

.. _2591a94: https://github.com/python-semantic-release/python-semantic-release/commit/2591a94115114c4a91a48f5b10b3954f6ac932a1
.. _f3ece78: https://github.com/python-semantic-release/python-semantic-release/commit/f3ece78b2913e70f6b99907b192a1e92bbfd6b77


.. _changelog-v7.8.0:

v7.8.0 (2020-12-18)
===================

✨ Features
-----------

* Add ``upload_to_pypi_glob_patterns`` option (`42305ed`_)

🪲 Bug Fixes
------------

* **changelog**: Use "issues" link vs "pull" (`93e48c9`_)

* **netrc**: Prefer using token defined in GH_TOKEN instead of .netrc file (`3af32a7`_)

.. _3af32a7: https://github.com/python-semantic-release/python-semantic-release/commit/3af32a738f2f2841fd75ec961a8f49a0b1c387cf
.. _42305ed: https://github.com/python-semantic-release/python-semantic-release/commit/42305ed499ca08c819c4e7e65fcfbae913b8e6e1
.. _93e48c9: https://github.com/python-semantic-release/python-semantic-release/commit/93e48c992cb8b763f430ecbb0b7f9c3ca00036e4


.. _changelog-v7.7.0:

v7.7.0 (2020-12-12)
===================

✨ Features
-----------

* **changelog**: Add PR links in markdown (`PR#282`_, `0448f6c`_)

.. _0448f6c: https://github.com/python-semantic-release/python-semantic-release/commit/0448f6c350bbbf239a81fe13dc5f45761efa7673
.. _PR#282: https://github.com/python-semantic-release/python-semantic-release/pull/282


.. _changelog-v7.6.0:

v7.6.0 (2020-12-06)
===================

✨ Features
-----------

* Add ``major_on_zero`` option (`d324154`_)

📖 Documentation
----------------

* Add documentation for option ``major_on_zero`` (`2e8b26e`_)

.. _2e8b26e: https://github.com/python-semantic-release/python-semantic-release/commit/2e8b26e4ee0316a2cf2a93c09c783024fcd6b3ba
.. _d324154: https://github.com/python-semantic-release/python-semantic-release/commit/d3241540e7640af911eb24c71e66468feebb0d46


.. _changelog-v7.5.0:

v7.5.0 (2020-12-04)
===================

✨ Features
-----------

* **logs**: Include scope in changelogs (`PR#281`_, `21c96b6`_)

.. _21c96b6: https://github.com/python-semantic-release/python-semantic-release/commit/21c96b688cc44cc6f45af962ffe6d1f759783f37
.. _PR#281: https://github.com/python-semantic-release/python-semantic-release/pull/281


.. _changelog-v7.4.1:

v7.4.1 (2020-12-04)
===================

🪲 Bug Fixes
------------

* Add "changelog_capitalize" to flags, closes `#278`_ (`PR#279`_, `37716df`_)

.. _#278: https://github.com/python-semantic-release/python-semantic-release/issues/278
.. _37716df: https://github.com/python-semantic-release/python-semantic-release/commit/37716dfa78eb3f848f57a5100d01d93f5aafc0bf
.. _PR#279: https://github.com/python-semantic-release/python-semantic-release/pull/279


.. _changelog-v7.4.0:

v7.4.0 (2020-11-24)
===================

✨ Features
-----------

* Add changelog_capitalize configuration, closes `#260`_ (`7cacca1`_)

📖 Documentation
----------------

* Fix broken internal references (`PR#270`_, `da20b9b`_)

* Update links to Github docs (`PR#268`_, `c53162e`_)

.. _#260: https://github.com/python-semantic-release/python-semantic-release/issues/260
.. _7cacca1: https://github.com/python-semantic-release/python-semantic-release/commit/7cacca1eb436a7166ba8faf643b53c42bc32a6a7
.. _c53162e: https://github.com/python-semantic-release/python-semantic-release/commit/c53162e366304082a3bd5d143b0401da6a16a263
.. _da20b9b: https://github.com/python-semantic-release/python-semantic-release/commit/da20b9bdd3c7c87809c25ccb2a5993a7ea209a22
.. _PR#268: https://github.com/python-semantic-release/python-semantic-release/pull/268
.. _PR#270: https://github.com/python-semantic-release/python-semantic-release/pull/270


.. _changelog-v7.3.0:

v7.3.0 (2020-09-28)
===================

✨ Features
-----------

* Generate ``changelog.md`` file (`PR#266`_, `2587dfe`_)

📖 Documentation
----------------

* Fix docstring (`5a5e2cf`_)

.. _2587dfe: https://github.com/python-semantic-release/python-semantic-release/commit/2587dfed71338ec6c816f58cdf0882382c533598
.. _5a5e2cf: https://github.com/python-semantic-release/python-semantic-release/commit/5a5e2cfb5e6653fb2e95e6e23e56559953b2c2b4
.. _PR#266: https://github.com/python-semantic-release/python-semantic-release/pull/266


.. _changelog-v7.2.5:

v7.2.5 (2020-09-16)
===================

🪲 Bug Fixes
------------

* Add required to inputs in action metadata (`PR#264`_, `e76b255`_)

.. _e76b255: https://github.com/python-semantic-release/python-semantic-release/commit/e76b255cf7d3d156e3314fc28c54d63fa126e973
.. _PR#264: https://github.com/python-semantic-release/python-semantic-release/pull/264


.. _changelog-v7.2.4:

v7.2.4 (2020-09-14)
===================

🪲 Bug Fixes
------------

* Use range for toml dependency, closes `#241`_ (`45707e1`_)

.. _#241: https://github.com/python-semantic-release/python-semantic-release/issues/241
.. _45707e1: https://github.com/python-semantic-release/python-semantic-release/commit/45707e1b7dcab48103a33de9d7f9fdb5a34dae4a


.. _changelog-v7.2.3:

v7.2.3 (2020-09-12)
===================

🪲 Bug Fixes
------------

* Support multiline version_pattern matching by default (`82f7849`_)

📖 Documentation
----------------

* Create 'getting started' instructions (`PR#256`_, `5f4d000`_)

* Link to getting started guide in README (`f490e01`_)

.. _5f4d000: https://github.com/python-semantic-release/python-semantic-release/commit/5f4d000c3f153d1d23128acf577e389ae879466e
.. _82f7849: https://github.com/python-semantic-release/python-semantic-release/commit/82f7849dcf29ba658e0cb3b5d21369af8bf3c16f
.. _f490e01: https://github.com/python-semantic-release/python-semantic-release/commit/f490e0194fa818db4d38c185bc5e6245bfde546b
.. _PR#256: https://github.com/python-semantic-release/python-semantic-release/pull/256


.. _changelog-v7.2.2:

v7.2.2 (2020-07-26)
===================

🪲 Bug Fixes
------------

* **changelog**: Send changelog to stdout, closes `#250`_ (`87e2bb8`_)

📖 Documentation
----------------

* Add quotation marks to the pip commands in CONTRIBUTING.rst (`PR#253`_, `e20fa43`_)

.. _#250: https://github.com/python-semantic-release/python-semantic-release/issues/250
.. _87e2bb8: https://github.com/python-semantic-release/python-semantic-release/commit/87e2bb881387ff3ac245ab9923347a5a616e197b
.. _e20fa43: https://github.com/python-semantic-release/python-semantic-release/commit/e20fa43098c06f5f585c81b9cd7e287dcce3fb5d
.. _PR#253: https://github.com/python-semantic-release/python-semantic-release/pull/253


.. _changelog-v7.2.1:

v7.2.1 (2020-06-29)
===================

🪲 Bug Fixes
------------

* Commit all files with bumped versions (`PR#249`_, `b3a1766`_)

📖 Documentation
----------------

* Give example of multiple build commands (`PR#248`_, `65f1ffc`_)

.. _65f1ffc: https://github.com/python-semantic-release/python-semantic-release/commit/65f1ffcc6cac3bf382f4b821ff2be59d04f9f867
.. _b3a1766: https://github.com/python-semantic-release/python-semantic-release/commit/b3a1766be7edb7d2eb76f2726d35ab8298688b3b
.. _PR#248: https://github.com/python-semantic-release/python-semantic-release/pull/248
.. _PR#249: https://github.com/python-semantic-release/python-semantic-release/pull/249


.. _changelog-v7.2.0:

v7.2.0 (2020-06-15)
===================

✨ Features
-----------

* Bump versions in multiple files, closes `#175`_ (`PR#246`_, `0ba2c47`_)

.. _#175: https://github.com/python-semantic-release/python-semantic-release/issues/175
.. _0ba2c47: https://github.com/python-semantic-release/python-semantic-release/commit/0ba2c473c6e44cc326b3299b6ea3ddde833bdb37
.. _PR#246: https://github.com/python-semantic-release/python-semantic-release/pull/246


.. _changelog-v7.1.1:

v7.1.1 (2020-05-28)
===================

🪲 Bug Fixes
------------

* **changelog**: Swap sha and message in table changelog (`6741370`_)

.. _6741370: https://github.com/python-semantic-release/python-semantic-release/commit/6741370ab09b1706ff6e19b9fbe57b4bddefc70d


.. _changelog-v7.1.0:

v7.1.0 (2020-05-24)
===================

✨ Features
-----------

* **changelog**: Add changelog_table component, closes `#237`_ (`PR#242`_, `fe6a7e7`_)

.. _#237: https://github.com/python-semantic-release/python-semantic-release/issues/237
.. _fe6a7e7: https://github.com/python-semantic-release/python-semantic-release/commit/fe6a7e7fa014ffb827a1430dbcc10d1fc84c886b
.. _PR#242: https://github.com/python-semantic-release/python-semantic-release/pull/242


.. _changelog-v7.0.0:

v7.0.0 (2020-05-22)
===================

✨ Features
-----------

* Pass changelog_sections to components (`PR#240`_, `3e17a98`_)

* **changelog**: Add changelog components (`PR#240`_, `3e17a98`_)

📖 Documentation
----------------

* Add conda-forge badge (`e9536bb`_)

* Add documentation for changelog_components (`PR#240`_, `3e17a98`_)

💥 BREAKING CHANGES
-------------------

* **changelog**: The ``compare_url`` option has been removed in favor of using
  ``changelog_components``. This functionality is now available as the
  ``semantic_release.changelog.compare_url`` component.

.. _3e17a98: https://github.com/python-semantic-release/python-semantic-release/commit/3e17a98d7fa8468868a87e62651ac2c010067711
.. _e9536bb: https://github.com/python-semantic-release/python-semantic-release/commit/e9536bbe119c9e3b90c61130c02468e0e1f14141
.. _PR#240: https://github.com/python-semantic-release/python-semantic-release/pull/240


.. _changelog-v6.4.1:

v6.4.1 (2020-05-15)
===================

🪲 Bug Fixes
------------

* Convert ``\r\n`` to ``\n`` in commit messages, closes `#239`_ (`34acbbc`_)

.. _#239: https://github.com/python-semantic-release/python-semantic-release/issues/239
.. _34acbbc: https://github.com/python-semantic-release/python-semantic-release/commit/34acbbcd25320a9d18dcd1a4f43e1ce1837b2c9f


.. _changelog-v6.4.0:

v6.4.0 (2020-05-15)
===================

✨ Features
-----------

* **history**: Create emoji parser (`PR#238`_, `2e1c50a`_)

🪲 Bug Fixes
------------

* Add emojis to default changelog_sections (`PR#238`_, `2e1c50a`_)

* Include all parsed types in changelog (`PR#238`_, `2e1c50a`_)

📖 Documentation
----------------

* Add documentation for emoji parser (`PR#238`_, `2e1c50a`_)

♻️ Refactoring
---------------

* **history**: Get breaking changes in parser (`PR#238`_, `2e1c50a`_)

.. _2e1c50a: https://github.com/python-semantic-release/python-semantic-release/commit/2e1c50a865628b372f48945a039a3edb38a7cdf0
.. _PR#238: https://github.com/python-semantic-release/python-semantic-release/pull/238


.. _changelog-v6.3.1:

v6.3.1 (2020-05-11)
===================

🪲 Bug Fixes
------------

* Use getboolean for commit_version_number, closes `#186`_ (`a60e0b4`_)

.. _#186: https://github.com/python-semantic-release/python-semantic-release/issues/186
.. _a60e0b4: https://github.com/python-semantic-release/python-semantic-release/commit/a60e0b4e3cadf310c3e0ad67ebeb4e69d0ee50cb


.. _changelog-v6.3.0:

v6.3.0 (2020-05-09)
===================

✨ Features
-----------

* **history**: Support linking compare page in changelog, closes `#218`_ (`79a8e02`_)

📖 Documentation
----------------

* Document compare_link option (`e52c355`_)

* Rewrite commit-log-parsing.rst (`4c70f4f`_)

.. _#218: https://github.com/python-semantic-release/python-semantic-release/issues/218
.. _4c70f4f: https://github.com/python-semantic-release/python-semantic-release/commit/4c70f4f2aa3343c966d1b7ab8566fcc782242ab9
.. _79a8e02: https://github.com/python-semantic-release/python-semantic-release/commit/79a8e02df82fbc2acecaad9e9ff7368e61df3e54
.. _e52c355: https://github.com/python-semantic-release/python-semantic-release/commit/e52c355c0d742ddd2cfa65d42888296942e5bec5


.. _changelog-v6.2.0:

v6.2.0 (2020-05-02)
===================

✨ Features
-----------

* **history**: Check all paragraphs for breaking changes, closes `#200`_ (`fec08f0`_)

📖 Documentation
----------------

* Add = to verbosity option, closes `#227`_ (`a0f4c9c`_)

* Use references where possible, closes `#221`_ (`f38e5d4`_)


.. _#200: https://github.com/python-semantic-release/python-semantic-release/issues/200
.. _#221: https://github.com/python-semantic-release/python-semantic-release/issues/221
.. _#227: https://github.com/python-semantic-release/python-semantic-release/issues/227
.. _a0f4c9c: https://github.com/python-semantic-release/python-semantic-release/commit/a0f4c9cd397fcb98f880097319c08160adb3c3e6
.. _f38e5d4: https://github.com/python-semantic-release/python-semantic-release/commit/f38e5d4a1597cddb69ce47a4d79b8774e796bf41
.. _fec08f0: https://github.com/python-semantic-release/python-semantic-release/commit/fec08f0dbd7ae15f95ca9c41a02c9fe6d448ede0


.. _changelog-v6.1.0:

v6.1.0 (2020-04-26)
===================

✨ Features
-----------

* **actions**: Support PYPI_TOKEN on GitHub Actions (`df2c080`_)

* **pypi**: Support easier use of API tokens, closes `#213`_ (`bac135c`_)

📖 Documentation
----------------

* Add documentation for PYPI_TOKEN (`a8263a0`_)

.. _#213: https://github.com/python-semantic-release/python-semantic-release/issues/213
.. _a8263a0: https://github.com/python-semantic-release/python-semantic-release/commit/a8263a066177d1d42f2844e4cb42a76a23588500
.. _bac135c: https://github.com/python-semantic-release/python-semantic-release/commit/bac135c0ae7a6053ecfc7cdf2942c3c89640debf
.. _df2c080: https://github.com/python-semantic-release/python-semantic-release/commit/df2c0806f0a92186e914cfc8cc992171d74422df


.. _changelog-v6.0.1:

v6.0.1 (2020-04-15)
===================

🪲 Bug Fixes
------------

* **hvcs**: Convert get_hvcs to use LoggedFunction (`3084249`_)

.. _3084249: https://github.com/python-semantic-release/python-semantic-release/commit/308424933fd3375ca3730d9eaf8abbad2435830b


.. _changelog-v6.0.0:

v6.0.0 (2020-04-15)
===================

📖 Documentation
----------------

* Create Read the Docs config file (`aa5a1b7`_)

* Include README.rst in index.rst (`8673a9d`_)

* Move action.rst into main documentation (`509ccaf`_)

* Rewrite README.rst (`e049772`_)

* Rewrite troubleshooting page (`0285de2`_)

♻️ Refactoring
---------------

* **debug**: Use logging and click_log instead of ndebug (`15b1f65`_)

💥 BREAKING CHANGES
-------------------

* **debug**: ``debug="*"`` no longer has an effect, instead use ``--verbosity DEBUG``.

.. _0285de2: https://github.com/python-semantic-release/python-semantic-release/commit/0285de215a8dac3fcc9a51f555fa45d476a56dff
.. _15b1f65: https://github.com/python-semantic-release/python-semantic-release/commit/15b1f650f29761e1ab2a91b767cbff79b2057a4c
.. _509ccaf: https://github.com/python-semantic-release/python-semantic-release/commit/509ccaf307a0998eced69ad9fee1807132babe28
.. _8673a9d: https://github.com/python-semantic-release/python-semantic-release/commit/8673a9d92a9bf348bb3409e002a830741396c8ca
.. _aa5a1b7: https://github.com/python-semantic-release/python-semantic-release/commit/aa5a1b700a1c461c81c6434686cb6f0504c4bece
.. _e049772: https://github.com/python-semantic-release/python-semantic-release/commit/e049772cf14cdd49538cf357db467f0bf3fe9587


.. _changelog-v5.2.0:

v5.2.0 (2020-04-09)
===================

✨ Features
-----------

* **github**: Add tag as default release name (`2997908`_)

📖 Documentation
----------------

* Automate API docs (`7d4fea2`_)

.. _2997908: https://github.com/python-semantic-release/python-semantic-release/commit/2997908f80f4fcec56917d237a079b961a06f990
.. _7d4fea2: https://github.com/python-semantic-release/python-semantic-release/commit/7d4fea266cc75007de51609131eb6d1e324da608


.. _changelog-v5.1.0:

v5.1.0 (2020-04-04)
===================

✨ Features
-----------

* **history**: Allow customizing changelog_sections (`PR#207`_, `d5803d5`_)

📖 Documentation
----------------

* Improve formatting of configuration page (`9a8e22e`_)

* Improve formatting of envvars page (`b376a56`_)

* Update index.rst (`b27c26c`_)

.. _9a8e22e: https://github.com/python-semantic-release/python-semantic-release/commit/9a8e22e838d7dbf3bfd941397c3b39560aca6451
.. _b27c26c: https://github.com/python-semantic-release/python-semantic-release/commit/b27c26c66e7e41843ab29076f7e724908091b46e
.. _b376a56: https://github.com/python-semantic-release/python-semantic-release/commit/b376a567bfd407a507ce0752614b0ca75a0f2973
.. _d5803d5: https://github.com/python-semantic-release/python-semantic-release/commit/d5803d5c1668d86482a31ac0853bac7ecfdc63bc
.. _PR#207: https://github.com/python-semantic-release/python-semantic-release/pull/207


.. _changelog-v5.0.3:

v5.0.3 (2020-03-26)
===================

🪲 Bug Fixes
------------

* Bump dependencies and fix Windows issues on Development (`PR#173`_, `0a6f8c3`_)

* Missing mime types on Windows (`PR#173`_, `0a6f8c3`_)

.. _0a6f8c3: https://github.com/python-semantic-release/python-semantic-release/commit/0a6f8c3842b05f5f424dad5ce1fa5e3823c7e688
.. _PR#173: https://github.com/python-semantic-release/python-semantic-release/pull/173


.. _changelog-v5.0.2:

v5.0.2 (2020-03-22)
===================

🪲 Bug Fixes
------------

* **history**: Leave case of other characters unchanged (`96ba94c`_)

.. _96ba94c: https://github.com/python-semantic-release/python-semantic-release/commit/96ba94c4b4593997343ec61ecb6c823c1494d0e2


.. _changelog-v5.0.1:

v5.0.1 (2020-03-22)
===================

🪲 Bug Fixes
------------

* Make action use current version of semantic-release (`123984d`_)

.. _123984d: https://github.com/python-semantic-release/python-semantic-release/commit/123984d735181c622f3d99088a1ad91321192a11


.. _changelog-v5.0.0:

v5.0.0 (2020-03-22)
===================

✨ Features
-----------

* **build**: Allow config setting for build command, closes `#188`_ (`PR#195`_, `740f4bd`_)

🪲 Bug Fixes
------------

* Rename default of build_command config (`d5db22f`_)

📖 Documentation
----------------

* **pypi**: Update docstrings in pypi.py (`6502d44`_)

💥 BREAKING CHANGES
-------------------

* **build**: Previously the build_commands configuration variable set the types of bundles sent to
  ``python setup.py``. It has been replaced by the configuration variable ``build_command`` which
  takes the full command e.g. ``python setup.py sdist`` or ``poetry build``.

.. _#188: https://github.com/python-semantic-release/python-semantic-release/issues/188
.. _6502d44: https://github.com/python-semantic-release/python-semantic-release/commit/6502d448fa65e5dc100e32595e83fff6f62a881a
.. _740f4bd: https://github.com/python-semantic-release/python-semantic-release/commit/740f4bdb26569362acfc80f7e862fc2c750a46dd
.. _d5db22f: https://github.com/python-semantic-release/python-semantic-release/commit/d5db22f9f7acd05d20fd60a8b4b5a35d4bbfabb8
.. _PR#195: https://github.com/python-semantic-release/python-semantic-release/pull/195


.. _changelog-v4.11.0:

v4.11.0 (2020-03-22)
====================

✨ Features
-----------

* **actions**: Create GitHub Action (`350245d`_)

📖 Documentation
----------------

* Make AUTHORS.rst dynamic (`db2e076`_)

* **readme**: Fix minor typo (`c22f69f`_)

.. _350245d: https://github.com/python-semantic-release/python-semantic-release/commit/350245dbfb07ed6a1db017b1d9d1072b368b1497
.. _c22f69f: https://github.com/python-semantic-release/python-semantic-release/commit/c22f69f62a215ff65e1ab6dcaa8e7e9662692e64
.. _db2e076: https://github.com/python-semantic-release/python-semantic-release/commit/db2e0762f3189d0f1a6ba29aad32bdefb7e0187f


.. _changelog-v4.10.0:

v4.10.0 (2020-03-03)
====================

✨ Features
-----------

* Make commit message configurable (`PR#184`_, `eb0762c`_)

.. _eb0762c: https://github.com/python-semantic-release/python-semantic-release/commit/eb0762ca9fea5cecd5c7b182504912a629be473b
.. _PR#184: https://github.com/python-semantic-release/python-semantic-release/pull/184


.. _changelog-v4.9.0:

v4.9.0 (2020-03-02)
===================

✨ Features
-----------

* **pypi**: Add build_commands config (`22146ea`_)

🪲 Bug Fixes
------------

* **pypi**: Change bdist_wheels to bdist_wheel (`c4db509`_)

.. _22146ea: https://github.com/python-semantic-release/python-semantic-release/commit/22146ea4b94466a90d60b94db4cc65f46da19197
.. _c4db509: https://github.com/python-semantic-release/python-semantic-release/commit/c4db50926c03f3d551c8331932c567c7bdaf4f3d


.. _changelog-v4.8.0:

v4.8.0 (2020-02-28)
===================

✨ Features
-----------

* **git**: Add a new config for commit author (`aa2c22c`_)

.. _aa2c22c: https://github.com/python-semantic-release/python-semantic-release/commit/aa2c22c469448fe57f02bea67a02f998ce519ac3


.. _changelog-v4.7.1:

v4.7.1 (2020-02-28)
===================

🪲 Bug Fixes
------------

* Repair parsing of remotes in the gitlab ci format, closes `#181`_ (`0fddbe2`_)

.. _#181: https://github.com/python-semantic-release/python-semantic-release/issues/181
.. _0fddbe2: https://github.com/python-semantic-release/python-semantic-release/commit/0fddbe2fb70d24c09ceddb789a159162a45942dc


.. _changelog-v4.7.0:

v4.7.0 (2020-02-28)
===================

✨ Features
-----------

* Upload distribution files to GitHub Releases (`PR#177`_, `e427658`_)

* **github**: Upload dists to release (`PR#177`_, `e427658`_)

🪲 Bug Fixes
------------

* Post changelog after PyPI upload (`PR#177`_, `e427658`_)

* Support repository owner names containing dots, closes `#179`_ (`a6c4da4`_)

* **github**: Fix upload of .whl files (`PR#177`_, `e427658`_)

* **github**: Use application/octet-stream for .whl files (`90a7e47`_)

📖 Documentation
----------------

* Document upload_to_release config option (`PR#177`_, `e427658`_)

.. _#179: https://github.com/python-semantic-release/python-semantic-release/issues/179
.. _90a7e47: https://github.com/python-semantic-release/python-semantic-release/commit/90a7e476a04d26babc88002e9035cad2ed485b07
.. _a6c4da4: https://github.com/python-semantic-release/python-semantic-release/commit/a6c4da4c0e6bd8a37f64544f7813fa027f5054ed
.. _e427658: https://github.com/python-semantic-release/python-semantic-release/commit/e427658e33abf518191498c3142a0f18d3150e07
.. _PR#177: https://github.com/python-semantic-release/python-semantic-release/pull/177


.. _changelog-v4.6.0:

v4.6.0 (2020-02-19)
===================

✨ Features
-----------

* **history**: Capitalize changelog messages (`1a8e306`_)

🪲 Bug Fixes
------------

* Add more debug statements in logs (`bc931ec`_)

* Only overwrite with patch if bump is None, closes `#159`_ (`1daa4e2`_)

.. _#159: https://github.com/python-semantic-release/python-semantic-release/issues/159
.. _1a8e306: https://github.com/python-semantic-release/python-semantic-release/commit/1a8e3060b8f6d6362c27903dcfc69d17db5f1d36
.. _1daa4e2: https://github.com/python-semantic-release/python-semantic-release/commit/1daa4e23ec2dd40c6b490849276524264787e24e
.. _bc931ec: https://github.com/python-semantic-release/python-semantic-release/commit/bc931ec46795fde4c1ccee004eec83bf73d5de7a


.. _changelog-v4.5.1:

v4.5.1 (2020-02-16)
===================

🪲 Bug Fixes
------------

* **github**: Send token in request header, closes `#167`_ (`be9972a`_)

📖 Documentation
----------------

* Add note about automatic releases in readme (`e606e75`_)

* Fix broken list in readme (`7aa572b`_)

* Update readme and getting started docs (`07b3208`_)

.. _#167: https://github.com/python-semantic-release/python-semantic-release/issues/167
.. _07b3208: https://github.com/python-semantic-release/python-semantic-release/commit/07b3208ff64301e544c4fdcb48314e49078fc479
.. _7aa572b: https://github.com/python-semantic-release/python-semantic-release/commit/7aa572b2a323ddbc69686309226395f40c52b469
.. _be9972a: https://github.com/python-semantic-release/python-semantic-release/commit/be9972a7b1fb183f738fb31bd370adb30281e4d5
.. _e606e75: https://github.com/python-semantic-release/python-semantic-release/commit/e606e7583a30167cf7679c6bcada2f9e768b3abe


.. _changelog-v4.5.0:

v4.5.0 (2020-02-08)
===================

✨ Features
-----------

* **history**: Enable colon defined version, closes `#165`_ (`7837f50`_)

🪲 Bug Fixes
------------

* Remove erroneous submodule (`762bfda`_)

* **cli**: --noop flag works when before command, closes `#73`_ (`4fcc781`_)

.. _#73: https://github.com/python-semantic-release/python-semantic-release/issues/73
.. _#165: https://github.com/python-semantic-release/python-semantic-release/issues/165
.. _4fcc781: https://github.com/python-semantic-release/python-semantic-release/commit/4fcc781d1a3f9235db552f0f4431c9f5e638d298
.. _762bfda: https://github.com/python-semantic-release/python-semantic-release/commit/762bfda728c266b8cd14671d8da9298fc99c63fb
.. _7837f50: https://github.com/python-semantic-release/python-semantic-release/commit/7837f5036269328ef29996b9ea63cccd5a6bc2d5


.. _changelog-v4.4.1:

v4.4.1 (2020-01-18)
===================

🪲 Bug Fixes
------------

* Add quotes around twine arguments, closes `#163`_ (`46a83a9`_)

.. _#163: https://github.com/python-semantic-release/python-semantic-release/issues/163
.. _46a83a9: https://github.com/python-semantic-release/python-semantic-release/commit/46a83a94b17c09d8f686c3ae7b199d7fd0e0e5e5


.. _changelog-v4.4.0:

v4.4.0 (2020-01-17)
===================

✨ Features
-----------

* **parser**: Add support for exclamation point for breaking changes, closes `#156`_ (`a4f8a10`_)

* **parser**: Make BREAKING-CHANGE synonymous with BREAKING CHANGE (`beedccf`_)

🪲 Bug Fixes
------------

* **github**: Add check for GITHUB_ACTOR for git push (`PR#162`_, `c41e9bb`_)

.. _#156: https://github.com/python-semantic-release/python-semantic-release/issues/156
.. _a4f8a10: https://github.com/python-semantic-release/python-semantic-release/commit/a4f8a10afcc358a8fbef83be2041129480350be2
.. _beedccf: https://github.com/python-semantic-release/python-semantic-release/commit/beedccfddfb360aeebef595342ee980446012ec7
.. _c41e9bb: https://github.com/python-semantic-release/python-semantic-release/commit/c41e9bb986d01b92d58419cbdc88489d630a11f1
.. _PR#162: https://github.com/python-semantic-release/python-semantic-release/pull/162


.. _changelog-v4.3.4:

v4.3.4 (2019-12-17)
===================

🪲 Bug Fixes
------------

* Fallback to whole log if correct tag is not available, closes `#51`_ (`PR#157`_, `252bffd`_)

.. _#51: https://github.com/python-semantic-release/python-semantic-release/issues/51
.. _252bffd: https://github.com/python-semantic-release/python-semantic-release/commit/252bffd3be7b6dfcfdb384d24cb1cd83d990fc9a
.. _PR#157: https://github.com/python-semantic-release/python-semantic-release/pull/157


.. _changelog-v4.3.3:

v4.3.3 (2019-11-06)
===================

🪲 Bug Fixes
------------

* Instead of requiring click 7.0, looks like all tests will pass with at least 2.0. (`PR#155`_,
  `f07c7f6`_)

* Set version of click to >=2.0,<8.0. (`PR#155`_, `f07c7f6`_)

* Upgrade to click 7.0, closes `#117`_ (`PR#155`_, `f07c7f6`_)

.. _#117: https://github.com/python-semantic-release/python-semantic-release/issues/117
.. _f07c7f6: https://github.com/python-semantic-release/python-semantic-release/commit/f07c7f653be1c018e443f071d9a196d9293e9521
.. _PR#155: https://github.com/python-semantic-release/python-semantic-release/pull/155


.. _changelog-v4.3.2:

v4.3.2 (2019-10-05)
===================

🪲 Bug Fixes
------------

* Update regex to get repository owner and name for project with dots, closes `#151`_ (`2778e31`_)

.. _#151: https://github.com/python-semantic-release/python-semantic-release/issues/151
.. _2778e31: https://github.com/python-semantic-release/python-semantic-release/commit/2778e316a0c0aa931b1012cb3862d04659c05e73


.. _changelog-v4.3.1:

v4.3.1 (2019-09-29)
===================

🪲 Bug Fixes
------------

* Support repo urls without git terminator (`700e9f1`_)

.. _700e9f1: https://github.com/python-semantic-release/python-semantic-release/commit/700e9f18dafde1833f482272a72bb80b54d56bb3


.. _changelog-v4.3.0:

v4.3.0 (2019-09-06)
===================

✨ Features
-----------

* Add the possibility to load configuration from pyproject.toml (`35f8bfe`_)

* Allow the override of configuration options from cli, closes `#119`_ (`f0ac82f`_)

* Allow users to get version from tag and write/commit bump to file, closes `#104`_ (`1f9fe1c`_)

* Make the vcs functionalities work with gitlab, closes `#121`_ (`82d555d`_)

🪲 Bug Fixes
------------

* Manage subgroups in git remote url, closes `#139`_, `#140`_ (`4b11875`_)

* Update list of commit types to include build, ci and perf, closes `#145`_ (`41ea12f`_)

.. _#104: https://github.com/python-semantic-release/python-semantic-release/issues/104
.. _#119: https://github.com/python-semantic-release/python-semantic-release/issues/119
.. _#121: https://github.com/python-semantic-release/python-semantic-release/issues/121
.. _#139: https://github.com/python-semantic-release/python-semantic-release/issues/139
.. _#140: https://github.com/python-semantic-release/python-semantic-release/issues/140
.. _#145: https://github.com/python-semantic-release/python-semantic-release/issues/145
.. _1f9fe1c: https://github.com/python-semantic-release/python-semantic-release/commit/1f9fe1cc7666d47cc0c348c4705b63c39bf10ecc
.. _35f8bfe: https://github.com/python-semantic-release/python-semantic-release/commit/35f8bfef443c8b69560c918f4b13bc766fb3daa2
.. _41ea12f: https://github.com/python-semantic-release/python-semantic-release/commit/41ea12fa91f97c0046178806bce3be57c3bc2308
.. _4b11875: https://github.com/python-semantic-release/python-semantic-release/commit/4b118754729094e330389712cf863e1c6cefee69
.. _82d555d: https://github.com/python-semantic-release/python-semantic-release/commit/82d555d45b9d9e295ef3f9546a6ca2a38ca4522e
.. _f0ac82f: https://github.com/python-semantic-release/python-semantic-release/commit/f0ac82fe59eb59a768a73a1bf2ea934b9d448c58


.. _changelog-v4.2.0:

v4.2.0 (2019-08-05)
===================

✨ Features
-----------

* Add configuration to customize handling of dists, closes `#115`_ (`2af6f41`_)

* Add support for configuring branch, closes `#43`_ (`14abb05`_)

* Add support for showing unreleased changelog, closes `#134`_ (`41ef794`_)

🪲 Bug Fixes
------------

* Add commit hash when generating breaking changes, closes `#120`_ (`0c74faf`_)

* Kept setting new version for tag source (`0e24a56`_)

* Remove deletion of build folder, closes `#115`_ (`b45703d`_)

* Updated the tag tests (`3303eef`_)

* Upgrade click to 7.0 (`2c5dd80`_)

.. _#43: https://github.com/python-semantic-release/python-semantic-release/issues/43
.. _#115: https://github.com/python-semantic-release/python-semantic-release/issues/115
.. _#120: https://github.com/python-semantic-release/python-semantic-release/issues/120
.. _#134: https://github.com/python-semantic-release/python-semantic-release/issues/134
.. _0c74faf: https://github.com/python-semantic-release/python-semantic-release/commit/0c74fafdfa81cf2e13db8f4dcf0a6f7347552504
.. _0e24a56: https://github.com/python-semantic-release/python-semantic-release/commit/0e24a5633f8f94b48da97b011634d4f9d84f7b4b
.. _14abb05: https://github.com/python-semantic-release/python-semantic-release/commit/14abb05e7f878e88002f896812d66b4ea5c219d4
.. _2af6f41: https://github.com/python-semantic-release/python-semantic-release/commit/2af6f41b21205bdd192514a434fca2feba17725a
.. _2c5dd80: https://github.com/python-semantic-release/python-semantic-release/commit/2c5dd809b84c2157a5e6cdcc773c43ec864f0328
.. _3303eef: https://github.com/python-semantic-release/python-semantic-release/commit/3303eefa49a0474bbd85df10ae186ccbf9090ec1
.. _41ef794: https://github.com/python-semantic-release/python-semantic-release/commit/41ef7947ad8a07392c96c7540980476e989c1d83
.. _b45703d: https://github.com/python-semantic-release/python-semantic-release/commit/b45703dad38c29b28575060b21e5fb0f8482c6b1


.. _changelog-v4.1.2:

v4.1.2 (2019-08-04)
===================

🪲 Bug Fixes
------------

* Correct isort build fail (`0037210`_)

* Make sure the history only breaks loop for version commit, closes `#135`_ (`5dc6cfc`_)

* **vcs**: Allow cli to be run from subdirectory (`fb7bb14`_)

📖 Documentation
----------------

* **circleci**: Point badge to master branch (`9c7302e`_)

.. _#135: https://github.com/python-semantic-release/python-semantic-release/issues/135
.. _0037210: https://github.com/python-semantic-release/python-semantic-release/commit/00372100b527ff9308d9e43fe5c65cdf179dc4dc
.. _5dc6cfc: https://github.com/python-semantic-release/python-semantic-release/commit/5dc6cfc634254f09997bb3cb0f17abd296e2c01f
.. _9c7302e: https://github.com/python-semantic-release/python-semantic-release/commit/9c7302e184a1bd88f39b3039691b55cd77f0bb07
.. _fb7bb14: https://github.com/python-semantic-release/python-semantic-release/commit/fb7bb14300e483626464795b8ff4f033a194cf6f


.. _changelog-v4.1.1:

v4.1.1 (2019-02-15)
===================

📖 Documentation
----------------

* Correct usage of changelog (`f4f59b0`_)

* Debug usage and related (`f08e594`_)

* Describing the commands (`b6fa04d`_)

* Update url for commit guidelinesThe guidelines can now be found in theDEVELOPERS.md in angular.
  (`90c1b21`_)

.. _90c1b21: https://github.com/python-semantic-release/python-semantic-release/commit/90c1b217f86263301b91d19d641c7b348e37d960
.. _b6fa04d: https://github.com/python-semantic-release/python-semantic-release/commit/b6fa04db3044525a1ee1b5952fb175a706842238
.. _f08e594: https://github.com/python-semantic-release/python-semantic-release/commit/f08e5943a9876f2d17a7c02f468720995c7d9ffd
.. _f4f59b0: https://github.com/python-semantic-release/python-semantic-release/commit/f4f59b08c73700c6ee04930221bfcb1355cbc48d


.. _changelog-v4.1.0:

v4.1.0 (2019-01-31)
===================

✨ Features
-----------

* **ci_checks**: Add support for bitbucket (`9fc120d`_)

🪲 Bug Fixes
------------

* Initialize git Repo from current folder (`c7415e6`_)

* Maintain version variable formatting on bump (`PR#103`_, `bf63156`_)

* Use same changelog code for command as post (`248f622`_)

📖 Documentation
----------------

* Add installation instructions for development (`PR#106`_, `9168d0e`_)

* **readme**: Add testing instructions (`bb352f5`_)

.. _248f622: https://github.com/python-semantic-release/python-semantic-release/commit/248f62283c59182868c43ff105a66d85c923a894
.. _9168d0e: https://github.com/python-semantic-release/python-semantic-release/commit/9168d0ea56734319a5d77e890f23ff6ba51cc97d
.. _9fc120d: https://github.com/python-semantic-release/python-semantic-release/commit/9fc120d1a7e4acbbca609628e72651685108b364
.. _bb352f5: https://github.com/python-semantic-release/python-semantic-release/commit/bb352f5b6616cc42c9f2f2487c51dedda1c68295
.. _bf63156: https://github.com/python-semantic-release/python-semantic-release/commit/bf63156f60340614fae94c255fb2f097cf317b2b
.. _c7415e6: https://github.com/python-semantic-release/python-semantic-release/commit/c7415e634c0affbe6396e0aa2bafe7c1b3368914
.. _PR#103: https://github.com/python-semantic-release/python-semantic-release/pull/103
.. _PR#106: https://github.com/python-semantic-release/python-semantic-release/pull/106


.. _changelog-v4.0.1:

v4.0.1 (2019-01-12)
===================

🪲 Bug Fixes
------------

* Add better error message when pypi credentials are empty, closes `#96`_ (`c4e5dcb`_)

* Clean out dist and build before building, closes `#86`_ (`b628e46`_)

* Filter out pypi secrets from exceptions, closes `#41`_ (`5918371`_)

* Unfreeze dependencies, closes `#100`_ (`847833b`_)

* Use correct syntax to exclude tests in package, closes `#92`_ (`3e41e91`_)

* **parser_angular**: Fix non-match when special chars in scope (`8a33123`_)

📖 Documentation
----------------

* Remove reference to gitter, closes `#90`_ (`896e37b`_)

.. _#41: https://github.com/python-semantic-release/python-semantic-release/issues/41
.. _#86: https://github.com/python-semantic-release/python-semantic-release/issues/86
.. _#90: https://github.com/python-semantic-release/python-semantic-release/issues/90
.. _#92: https://github.com/python-semantic-release/python-semantic-release/issues/92
.. _#96: https://github.com/python-semantic-release/python-semantic-release/issues/96
.. _#100: https://github.com/python-semantic-release/python-semantic-release/issues/100
.. _3e41e91: https://github.com/python-semantic-release/python-semantic-release/commit/3e41e91c318663085cd28c8165ece21d7e383475
.. _5918371: https://github.com/python-semantic-release/python-semantic-release/commit/5918371c1e82b06606087c9945d8eaf2604a0578
.. _847833b: https://github.com/python-semantic-release/python-semantic-release/commit/847833bf48352a4935f906d0c3f75e1db596ca1c
.. _896e37b: https://github.com/python-semantic-release/python-semantic-release/commit/896e37b95cc43218e8f593325dd4ea63f8b895d9
.. _8a33123: https://github.com/python-semantic-release/python-semantic-release/commit/8a331232621b26767e4268079f9295bf695047ab
.. _b628e46: https://github.com/python-semantic-release/python-semantic-release/commit/b628e466f86bc27cbe45ec27a02d4774a0efd3bb
.. _c4e5dcb: https://github.com/python-semantic-release/python-semantic-release/commit/c4e5dcbeda0ce8f87d25faefb4d9ae3581029a8f


.. _changelog-v4.0.0:

v4.0.0 (2018-11-22)
===================

✨ Features
-----------

* Add support for commit_message config variable (`4de5400`_)

* **CI checks**: Add support for GitLab CI checks, closes `#88`_ (`8df5e2b`_)

🪲 Bug Fixes
------------

* Add check of credentials (`7d945d4`_)

* Add credentials check (`0694604`_)

* Add dists to twine call (`1cec2df`_)

* Change requests from fixed version to version range (`PR#93`_, `af3ad59`_)

* Re-add skip-existing (`366e9c1`_)

* Remove repository argument in twine (`e24543b`_)

* Remove universal from setup config (`18b2402`_)

* Update twine (`c4ae7b8`_)

* Use new interface for twine (`c04872d`_)

* Use twine through cli call (`ab84beb`_)

📖 Documentation
----------------

* Add type hints and more complete docstrings, closes `#81`_ (`a6d5e9b`_)

* Fix typo in documentation index (`da6844b`_)

♻️ Refactoring
---------------

* Remove support for python 2 (`85fe638`_)

💥 BREAKING CHANGES
-------------------

* If you rely on the commit message to be the version number only, this will break your code

* This will only work with python 3 after this commit.

.. _#81: https://github.com/python-semantic-release/python-semantic-release/issues/81
.. _#88: https://github.com/python-semantic-release/python-semantic-release/issues/88
.. _0694604: https://github.com/python-semantic-release/python-semantic-release/commit/0694604f3b3d2159a4037620605ded09236cdef5
.. _18b2402: https://github.com/python-semantic-release/python-semantic-release/commit/18b24025e397aace03dd5bb9eed46cfdd13491bd
.. _1cec2df: https://github.com/python-semantic-release/python-semantic-release/commit/1cec2df8bcb7f877c813d6470d454244630b050a
.. _366e9c1: https://github.com/python-semantic-release/python-semantic-release/commit/366e9c1d0b9ffcde755407a1de18e8295f6ad3a1
.. _4de5400: https://github.com/python-semantic-release/python-semantic-release/commit/4de540011ab10483ee1865f99c623526cf961bb9
.. _7d945d4: https://github.com/python-semantic-release/python-semantic-release/commit/7d945d44b36b3e8c0b7771570cb2305e9e09d0b2
.. _85fe638: https://github.com/python-semantic-release/python-semantic-release/commit/85fe6384c15db317bc7142f4c8bbf2da58cece58
.. _8df5e2b: https://github.com/python-semantic-release/python-semantic-release/commit/8df5e2bdd33a620e683f3adabe174e94ceaa88d9
.. _a6d5e9b: https://github.com/python-semantic-release/python-semantic-release/commit/a6d5e9b1ccbe75d59e7240528593978a19d8d040
.. _ab84beb: https://github.com/python-semantic-release/python-semantic-release/commit/ab84beb8f809e39ae35cd3ce5c15df698d8712fd
.. _af3ad59: https://github.com/python-semantic-release/python-semantic-release/commit/af3ad59f018876e11cc3acdda0b149f8dd5606bd
.. _c04872d: https://github.com/python-semantic-release/python-semantic-release/commit/c04872d00a26e9bf0f48eeacb360b37ce0fba01e
.. _c4ae7b8: https://github.com/python-semantic-release/python-semantic-release/commit/c4ae7b8ecc682855a8568b247690eaebe62d2d26
.. _da6844b: https://github.com/python-semantic-release/python-semantic-release/commit/da6844bce0070a0020bf13950bd136fe28262602
.. _e24543b: https://github.com/python-semantic-release/python-semantic-release/commit/e24543b96adb208897f4ce3eaab96b2f4df13106
.. _PR#93: https://github.com/python-semantic-release/python-semantic-release/pull/93


.. _changelog-v3.11.2:

v3.11.2 (2018-06-10)
====================

🪲 Bug Fixes
------------

* Upgrade twine (`9722313`_)

.. _9722313: https://github.com/python-semantic-release/python-semantic-release/commit/9722313eb63c7e2c32c084ad31bed7ee1c48a928


.. _changelog-v3.11.1:

v3.11.1 (2018-06-06)
====================

🪲 Bug Fixes
------------

* Change Gitpython version number, closes `#80`_ (`23c9d4b`_)

📖 Documentation
----------------

* Add retry option to cli docs (`021da50`_)

.. _#80: https://github.com/python-semantic-release/python-semantic-release/issues/80
.. _021da50: https://github.com/python-semantic-release/python-semantic-release/commit/021da5001934f3199c98d7cf29f62a3ad8c2e56a
.. _23c9d4b: https://github.com/python-semantic-release/python-semantic-release/commit/23c9d4b6a1716e65605ed985881452898d5cf644


.. _changelog-v3.11.0:

v3.11.0 (2018-04-12)
====================

✨ Features
-----------

* Add --retry cli option (`PR#78`_, `3e312c0`_)

* Add support to finding previous version from tags if not using commit messages (`PR#68`_,
  `6786487`_)

* Be a bit more forgiving to find previous tags (`PR#68`_, `6786487`_)

🪲 Bug Fixes
------------

* Add pytest cache to gitignore (`b8efd5a`_)

* Make repo non if it is not a git repository, closes `#74`_ (`1dc306b`_)

📖 Documentation
----------------

* Define ``--retry`` usage (`3e312c0`_)

* Remove old notes about trello board (`7f50c52`_)

* Update status badges (`cfa13b8`_)

.. _#74: https://github.com/python-semantic-release/python-semantic-release/issues/74
.. _1dc306b: https://github.com/python-semantic-release/python-semantic-release/commit/1dc306b9b1db2ac360211bdc61fd815302d0014c
.. _3e312c0: https://github.com/python-semantic-release/python-semantic-release/commit/3e312c0ce79a78d25016a3b294b772983cfb5e0f
.. _6786487: https://github.com/python-semantic-release/python-semantic-release/commit/6786487ebf4ab481139ef9f43cd74e345debb334
.. _7f50c52: https://github.com/python-semantic-release/python-semantic-release/commit/7f50c521a522bb0c4579332766248778350e205b
.. _b8efd5a: https://github.com/python-semantic-release/python-semantic-release/commit/b8efd5a6249c79c8378bffea3e245657e7094ec9
.. _cfa13b8: https://github.com/python-semantic-release/python-semantic-release/commit/cfa13b8260e3f3b0bfcb395f828ad63c9c5e3ca5
.. _PR#68: https://github.com/python-semantic-release/python-semantic-release/pull/68
.. _PR#78: https://github.com/python-semantic-release/python-semantic-release/pull/78


.. _changelog-v3.10.3:

v3.10.3 (2018-01-29)
====================

🪲 Bug Fixes
------------

* Error when not in git repository, closes `#74`_ (`PR#75`_, `251b190`_)

.. _#74: https://github.com/python-semantic-release/python-semantic-release/issues/74
.. _251b190: https://github.com/python-semantic-release/python-semantic-release/commit/251b190a2fd5df68892346926d447cbc1b32475a
.. _PR#75: https://github.com/python-semantic-release/python-semantic-release/pull/75


.. _changelog-v3.10.2:

v3.10.2 (2017-08-03)
====================

🪲 Bug Fixes
------------

* Update call to upload to work with twine 1.9.1 (`PR#72`_, `8f47643`_)

.. _8f47643: https://github.com/python-semantic-release/python-semantic-release/commit/8f47643c54996e06c358537115e7e17b77cb02ca
.. _PR#72: https://github.com/python-semantic-release/python-semantic-release/pull/72


.. _changelog-v3.10.1:

v3.10.1 (2017-07-22)
====================

🪲 Bug Fixes
------------

* Update Twine (`PR#69`_, `9f268c3`_)

.. _9f268c3: https://github.com/python-semantic-release/python-semantic-release/commit/9f268c373a932621771abbe9607b739b1e331409
.. _PR#69: https://github.com/python-semantic-release/python-semantic-release/pull/69


.. _changelog-v3.10.0:

v3.10.0 (2017-05-05)
====================

✨ Features
-----------

* Add git hash to the changelog (`PR#65`_, `628170e`_)

🪲 Bug Fixes
------------

* Make changelog problems not fail whole publish (`b5a68cf`_)

📖 Documentation
----------------

* Fix typo in cli.py docstring (`PR#64`_, `0d13985`_)

.. _0d13985: https://github.com/python-semantic-release/python-semantic-release/commit/0d139859cd71f2d483f4360f196d6ef7c8726c18
.. _628170e: https://github.com/python-semantic-release/python-semantic-release/commit/628170ebc440fc6abf094dd3e393f40576dedf9b
.. _b5a68cf: https://github.com/python-semantic-release/python-semantic-release/commit/b5a68cf6177dc0ed80eda722605db064f3fe2062
.. _PR#64: https://github.com/python-semantic-release/python-semantic-release/pull/64
.. _PR#65: https://github.com/python-semantic-release/python-semantic-release/pull/65


.. _changelog-v3.9.0:

v3.9.0 (2016-07-03)
===================

✨ Features
-----------

* Add option for choosing between versioning by commit or tag (`c0cd1f5`_)

* Don't use file to track version, only tag to commit for versioning (`cd25862`_)

* Get repo version from historical tags instead of config file (`a45a9bf`_)

🪲 Bug Fixes
------------

* Can't get the proper last tag from commit history (`5a0e681`_)

.. _5a0e681: https://github.com/python-semantic-release/python-semantic-release/commit/5a0e681e256ec511cd6c6a8edfee9d905891da10
.. _a45a9bf: https://github.com/python-semantic-release/python-semantic-release/commit/a45a9bfb64538efeb7f6f42bb6e7ede86a4ddfa8
.. _c0cd1f5: https://github.com/python-semantic-release/python-semantic-release/commit/c0cd1f5b2e0776d7b636c3dd9e5ae863125219e6
.. _cd25862: https://github.com/python-semantic-release/python-semantic-release/commit/cd258623ee518c009ae921cd6bb3119dafae43dc


.. _changelog-v3.8.1:

v3.8.1 (2016-04-17)
===================

🪲 Bug Fixes
------------

* Add search_parent_directories option to gitpython (`PR#62`_, `8bf9ce1`_)

.. _8bf9ce1: https://github.com/python-semantic-release/python-semantic-release/commit/8bf9ce11137399906f18bc8b25698b6e03a65034
.. _PR#62: https://github.com/python-semantic-release/python-semantic-release/pull/62


.. _changelog-v3.8.0:

v3.8.0 (2016-03-21)
===================

✨ Features
-----------

* Add ci checks for circle ci (`151d849`_)

🪲 Bug Fixes
------------

* Add git fetch to frigg after success (`74a6cae`_)

* Make tag parser work correctly with breaking changes (`9496f6a`_)

* Refactoring cli.py to improve --help and error messages (`c79fc34`_)

📖 Documentation
----------------

* Add info about correct commit guidelines (`af35413`_)

* Add info about trello board in readme (`5229557`_)

* Fix badges in readme (`7f4e549`_)

* Update info about releases in contributing.md (`466f046`_)

.. _151d849: https://github.com/python-semantic-release/python-semantic-release/commit/151d84964266c8dca206cef8912391cb73c8f206
.. _466f046: https://github.com/python-semantic-release/python-semantic-release/commit/466f0460774cad86e7e828ffb50c7d1332b64e7b
.. _5229557: https://github.com/python-semantic-release/python-semantic-release/commit/5229557099d76b3404ea3677292332442a57ae2e
.. _74a6cae: https://github.com/python-semantic-release/python-semantic-release/commit/74a6cae2b46c5150e63136fde0599d98b9486e36
.. _7f4e549: https://github.com/python-semantic-release/python-semantic-release/commit/7f4e5493edb6b3fb3510d0bb78fcc8d23434837f
.. _9496f6a: https://github.com/python-semantic-release/python-semantic-release/commit/9496f6a502c79ec3acb4e222e190e76264db02cf
.. _af35413: https://github.com/python-semantic-release/python-semantic-release/commit/af35413fae80889e2c5fc6b7d28f77f34b3b4c02
.. _c79fc34: https://github.com/python-semantic-release/python-semantic-release/commit/c79fc3469fb99bf4c7f52434fa9c0891bca757f9


.. _changelog-v3.7.2:

v3.7.2 (2016-03-19)
===================

🪲 Bug Fixes
------------

* Move code around a bit to make flake8 happy (`41463b4`_)

.. _41463b4: https://github.com/python-semantic-release/python-semantic-release/commit/41463b49b5d44fd94c11ab6e0a81e199510fabec


.. _changelog-v3.7.1:

v3.7.1 (2016-03-15)
===================

📖 Documentation
----------------

* **configuration**: Fix typo in setup.cfg section (`725d87d`_)

.. _725d87d: https://github.com/python-semantic-release/python-semantic-release/commit/725d87dc45857ef2f9fb331222845ac83a3af135


.. _changelog-v3.7.0:

v3.7.0 (2016-01-10)
===================

✨ Features
-----------

* Add ci_checks for Frigg CI (`577c374`_)

.. _577c374: https://github.com/python-semantic-release/python-semantic-release/commit/577c374396fe303b6fe7d64630d2959998d3595c


.. _changelog-v3.6.1:

v3.6.1 (2016-01-10)
===================

🪲 Bug Fixes
------------

* Add requests as dependency (`4525a70`_)

.. _4525a70: https://github.com/python-semantic-release/python-semantic-release/commit/4525a70d5520b44720d385b0307e46fae77a7463


.. _changelog-v3.6.0:

v3.6.0 (2015-12-28)
===================

✨ Features
-----------

* Add checks for semaphore, closes `#44`_ (`2d7ef15`_)

📖 Documentation
----------------

* Add documentation for configuring on CI (`7806940`_)

* Add note about node semantic release (`0d2866c`_)

* Add step by step guide for configuring travis ci (`6f23414`_)

* Move automatic-releases to subfolder (`ed68e5b`_)

* Remove duplicate readme (`42a9421`_)

.. _#44: https://github.com/python-semantic-release/python-semantic-release/issues/44
.. _0d2866c: https://github.com/python-semantic-release/python-semantic-release/commit/0d2866c528098ecaf1dd81492f28d3022a2a54e0
.. _2d7ef15: https://github.com/python-semantic-release/python-semantic-release/commit/2d7ef157b1250459060e99601ec53a00942b6955
.. _42a9421: https://github.com/python-semantic-release/python-semantic-release/commit/42a942131947cd1864c1ba29b184caf072408742
.. _6f23414: https://github.com/python-semantic-release/python-semantic-release/commit/6f2341442f61f0284b1119a2c49e96f0be678929
.. _7806940: https://github.com/python-semantic-release/python-semantic-release/commit/7806940ae36cb0d6ac0f966e5d6d911bd09a7d11
.. _ed68e5b: https://github.com/python-semantic-release/python-semantic-release/commit/ed68e5b8d3489463e244b078ecce8eab2cba2bb1


.. _changelog-v3.5.0:

v3.5.0 (2015-12-22)
===================

✨ Features
-----------

* Add author in commit, closes `#40`_ (`020efaa`_)

* Checkout master before publishing (`dc4077a`_)

🪲 Bug Fixes
------------

* Remove " from git push command (`031318b`_)

📖 Documentation
----------------

* Convert readme to rst (`e8a8d26`_)

.. _#40: https://github.com/python-semantic-release/python-semantic-release/issues/40
.. _020efaa: https://github.com/python-semantic-release/python-semantic-release/commit/020efaaadf588e3fccd9d2f08a273c37e4158421
.. _031318b: https://github.com/python-semantic-release/python-semantic-release/commit/031318b3268bc37e6847ec049b37425650cebec8
.. _dc4077a: https://github.com/python-semantic-release/python-semantic-release/commit/dc4077a2d07e0522b625336dcf83ee4e0e1640aa
.. _e8a8d26: https://github.com/python-semantic-release/python-semantic-release/commit/e8a8d265aa2147824f18065b39a8e7821acb90ec


.. _changelog-v3.4.0:

v3.4.0 (2015-12-22)
===================

✨ Features
-----------

* Add travis environment checks (`f386db7`_)

.. _f386db7: https://github.com/python-semantic-release/python-semantic-release/commit/f386db75b77acd521d2f5bde2e1dde99924dc096


.. _changelog-v3.3.3:

v3.3.3 (2015-12-22)
===================

🪲 Bug Fixes
------------

* Do git push and git push --tags instead of --follow-tags (`8bc70a1`_)

.. _8bc70a1: https://github.com/python-semantic-release/python-semantic-release/commit/8bc70a183fd72f595c72702382bc0b7c3abe99c8


.. _changelog-v3.3.2:

v3.3.2 (2015-12-21)
===================

🪲 Bug Fixes
------------

* Change build badge (`0dc068f`_)

📖 Documentation
----------------

* Update docstrings for generate_changelog (`987c6a9`_)

.. _0dc068f: https://github.com/python-semantic-release/python-semantic-release/commit/0dc068fff2f8c6914f4abe6c4e5fb2752669159e
.. _987c6a9: https://github.com/python-semantic-release/python-semantic-release/commit/987c6a96d15997e38c93a9d841c618c76a385ce7


.. _changelog-v3.3.1:

v3.3.1 (2015-12-21)
===================

🪲 Bug Fixes
------------

* Add pandoc to travis settings (`17d40a7`_)

* Only list commits from the last version tag, closes `#28`_ (`191369e`_)

.. _#28: https://github.com/python-semantic-release/python-semantic-release/issues/28
.. _17d40a7: https://github.com/python-semantic-release/python-semantic-release/commit/17d40a73062ffa774542d0abc0f59fc16b68be37
.. _191369e: https://github.com/python-semantic-release/python-semantic-release/commit/191369ebd68526e5b1afcf563f7d13e18c8ca8bf


.. _changelog-v3.3.0:

v3.3.0 (2015-12-20)
===================

✨ Features
-----------

* Add support for environment variables for pypi credentials (`3b383b9`_)

🪲 Bug Fixes
------------

* Add missing parameters to twine.upload (`4bae22b`_)

* Better filtering of github token in push error (`9b31da4`_)

* Downgrade twine to version 1.5.0 (`66df378`_)

* Make sure the github token is not in the output (`55356b7`_)

* Push to master by default (`a0bb023`_)

.. _3b383b9: https://github.com/python-semantic-release/python-semantic-release/commit/3b383b92376a7530e89b11de481c4dfdfa273f7b
.. _4bae22b: https://github.com/python-semantic-release/python-semantic-release/commit/4bae22bae9b9d9abf669b028ea3af4b3813a1df0
.. _55356b7: https://github.com/python-semantic-release/python-semantic-release/commit/55356b718f74d94dd92e6c2db8a15423a6824eb5
.. _66df378: https://github.com/python-semantic-release/python-semantic-release/commit/66df378330448a313aff7a7c27067adda018904f
.. _9b31da4: https://github.com/python-semantic-release/python-semantic-release/commit/9b31da4dc27edfb01f685e6036ddbd4c715c9f60
.. _a0bb023: https://github.com/python-semantic-release/python-semantic-release/commit/a0bb023438a1503f9fdb690d976d71632f19a21f


.. _changelog-v3.2.1:

v3.2.1 (2015-12-20)
===================

🪲 Bug Fixes
------------

* Add requirements to manifest (`ed25ecb`_)

* **pypi**: Add sdist as default in addition to bdist_wheel (`a1a35f4`_)

.. _a1a35f4: https://github.com/python-semantic-release/python-semantic-release/commit/a1a35f43175187091f028474db2ebef5bfc77bc0
.. _ed25ecb: https://github.com/python-semantic-release/python-semantic-release/commit/ed25ecbaeec0e20ad3040452a5547bb7d6faf6ad


.. _changelog-v3.2.0:

v3.2.0 (2015-12-20)
===================

✨ Features
-----------

* **angular-parser**: Remove scope requirement (`90c9d8d`_)

* **git**: Add push to GH_TOKEN@github-url (`546b5bf`_)

🪲 Bug Fixes
------------

* **deps**: Use one file for requirements (`4868543`_)

.. _4868543: https://github.com/python-semantic-release/python-semantic-release/commit/486854393b24803bb2356324e045ccab17510d46
.. _546b5bf: https://github.com/python-semantic-release/python-semantic-release/commit/546b5bf15466c6f5dfe93c1c03ca34604b0326f2
.. _90c9d8d: https://github.com/python-semantic-release/python-semantic-release/commit/90c9d8d4cd6d43be094cda86579e00b507571f98


.. _changelog-v3.1.0:

v3.1.0 (2015-08-31)
===================

✨ Features
-----------

* **pypi**: Add option to disable pypi upload (`f5cd079`_)

.. _f5cd079: https://github.com/python-semantic-release/python-semantic-release/commit/f5cd079edb219de5ad03a71448d578f5f477da9c


.. _changelog-v3.0.0:

v3.0.0 (2015-08-25)
===================

✨ Features
-----------

* **parser**: Add tag parser (`a7f392f`_)

🪲 Bug Fixes
------------

* **errors**: Add exposing of errors in package (`3662d76`_)

* **version**: Parse file instead for version (`005dba0`_)

.. _005dba0: https://github.com/python-semantic-release/python-semantic-release/commit/005dba0094eeb4098315ef383a746e139ffb504d
.. _3662d76: https://github.com/python-semantic-release/python-semantic-release/commit/3662d7663291859dd58a91b4b4ccde4f0edc99b2
.. _a7f392f: https://github.com/python-semantic-release/python-semantic-release/commit/a7f392fd4524cc9207899075631032e438e2593c


.. _changelog-v2.1.4:

v2.1.4 (2015-08-24)
===================

🪲 Bug Fixes
------------

* **github**: Fix property calls (`7ecdeb2`_)

.. _7ecdeb2: https://github.com/python-semantic-release/python-semantic-release/commit/7ecdeb22de96b6b55c5404ebf54a751911c4d8cd


.. _changelog-v2.1.3:

v2.1.3 (2015-08-22)
===================

🪲 Bug Fixes
------------

* **hvcs**: Make Github.token an property (`37d5e31`_)

📖 Documentation
----------------

* **api**: Update apidocs (`6185380`_)

* **parsers**: Add documentation about commit parsers (`9b55422`_)

* **readme**: Update readme with information about the changelog command (`56a745e`_)

.. _37d5e31: https://github.com/python-semantic-release/python-semantic-release/commit/37d5e3110397596a036def5f1dccf0860964332c
.. _56a745e: https://github.com/python-semantic-release/python-semantic-release/commit/56a745ef6fa4edf6f6ba09c78fcc141102cf2871
.. _6185380: https://github.com/python-semantic-release/python-semantic-release/commit/6185380babedbbeab2a2a342f17b4ff3d4df6768
.. _9b55422: https://github.com/python-semantic-release/python-semantic-release/commit/9b554222768036024a133153a559cdfc017c1d91


.. _changelog-v2.1.2:

v2.1.2 (2015-08-20)
===================

🪲 Bug Fixes
------------

* **cli**: Fix call to generate_changelog in publish (`5f8bce4`_)

.. _5f8bce4: https://github.com/python-semantic-release/python-semantic-release/commit/5f8bce4cbb5e1729e674efd6c651e2531aea2a16


.. _changelog-v2.1.1:

v2.1.1 (2015-08-20)
===================

🪲 Bug Fixes
------------

* **history**: Fix issue in get_previous_version (`f961786`_)

.. _f961786: https://github.com/python-semantic-release/python-semantic-release/commit/f961786aa3eaa3a620f47cc09243340fd329b9c2


.. _changelog-v2.1.0:

v2.1.0 (2015-08-20)
===================

✨ Features
-----------

* **cli**: Add the possibility to re-post the changelog (`4d028e2`_)

🪲 Bug Fixes
------------

* **cli**: Fix check of token in changelog command (`cc6e6ab`_)

* **github**: Fix the github releases integration (`f0c3c1d`_)

* **history**: Fix changelog generation (`f010272`_)

.. _4d028e2: https://github.com/python-semantic-release/python-semantic-release/commit/4d028e21b9da01be8caac8f23f2c11e0c087e485
.. _cc6e6ab: https://github.com/python-semantic-release/python-semantic-release/commit/cc6e6abe1e91d3aa24e8d73e704829669bea5fd7
.. _f010272: https://github.com/python-semantic-release/python-semantic-release/commit/f01027203a8ca69d21b4aff689e60e8c8d6f9af5
.. _f0c3c1d: https://github.com/python-semantic-release/python-semantic-release/commit/f0c3c1db97752b71f2153ae9f623501b0b8e2c98


.. _changelog-v2.0.0:

v2.0.0 (2015-08-19)
===================

✨ Features
-----------

* **cli**: Add command for printing the changelog (`336b8bc`_)

* **github**: Add github release changelog helper (`da18795`_)

* **history**: Add angular parser (`91e4f0f`_)

* **history**: Add generate_changelog function (`347f21a`_)

* **history**: Add markdown changelog formatter (`d77b58d`_)

* **history**: Set angular parser as the default (`c2cf537`_)

* **publish**: Add publishing of changelog to github (`74324ba`_)

* **settings**: Add loading of current parser (`7bd0916`_)

🪲 Bug Fixes
------------

* **cli**: Change output indentation on changelog (`2ca41d3`_)

* **history**: Fix level id's in angular parser (`2918d75`_)

* **history**: Fix regex in angular parser (`974ccda`_)

* **history**: Support unexpected types in changelog generator (`13deacf`_)

💥 BREAKING CHANGES
-------------------

* **history**: The default parser is now angular. Thus, the default behavior of the commit log
  evaluator will change. From now on it will use the angular commit message spec to determine the
  new version.

.. _13deacf: https://github.com/python-semantic-release/python-semantic-release/commit/13deacf5d33ed500e4e94ea702a2a16be2aa7c48
.. _2918d75: https://github.com/python-semantic-release/python-semantic-release/commit/2918d759bf462082280ede971a5222fe01634ed8
.. _2ca41d3: https://github.com/python-semantic-release/python-semantic-release/commit/2ca41d3bd1b8b9d9fe7e162772560e3defe2a41e
.. _336b8bc: https://github.com/python-semantic-release/python-semantic-release/commit/336b8bcc01fc1029ff37a79c92935d4b8ea69203
.. _347f21a: https://github.com/python-semantic-release/python-semantic-release/commit/347f21a1f8d655a71a0e7d58b64d4c6bc6d0bf31
.. _74324ba: https://github.com/python-semantic-release/python-semantic-release/commit/74324ba2749cdbbe80a92b5abbecfeab04617699
.. _7bd0916: https://github.com/python-semantic-release/python-semantic-release/commit/7bd0916f87a1f9fe839c853eab05cae1af420cd2
.. _91e4f0f: https://github.com/python-semantic-release/python-semantic-release/commit/91e4f0f4269d01b255efcd6d7121bbfd5a682e12
.. _974ccda: https://github.com/python-semantic-release/python-semantic-release/commit/974ccdad392d768af5e187dabc184be9ac3e133d
.. _c2cf537: https://github.com/python-semantic-release/python-semantic-release/commit/c2cf537a42beaa60cd372c7c9f8fb45db8085917
.. _d77b58d: https://github.com/python-semantic-release/python-semantic-release/commit/d77b58db4b66aec94200dccab94f483def4dacc9
.. _da18795: https://github.com/python-semantic-release/python-semantic-release/commit/da187951af31f377ac57fe17462551cfd776dc6e


.. _changelog-v1.0.0:

v1.0.0 (2015-08-04)
===================

💥 Breaking
-----------

* Restructure helpers into history and pypi (`00f64e6`_)

📖 Documentation
----------------

* Add automatic publishing documentation, resolves `#18`_ (`58076e6`_)

.. _#18: https://github.com/python-semantic-release/python-semantic-release/issues/18
.. _00f64e6: https://github.com/python-semantic-release/python-semantic-release/commit/00f64e623db0e21470d55488c5081e12d6c11fd3
.. _58076e6: https://github.com/python-semantic-release/python-semantic-release/commit/58076e60bf20a5835b112b5e99a86c7425ffe7d9


.. _changelog-v0.9.1:

v0.9.1 (2015-08-04)
===================

🪲 Bug Fixes
------------

* Fix ``get_current_head_hash`` to ensure it only returns the hash (`7c28832`_)

.. _7c28832: https://github.com/python-semantic-release/python-semantic-release/commit/7c2883209e5bf4a568de60dbdbfc3741d34f38b4


.. _changelog-v0.9.0:

v0.9.0 (2015-08-03)
===================

✨ Features
-----------

* Add Python 2.7 support, resolves `#10`_ (`c05e13f`_)

.. _#10: https://github.com/python-semantic-release/python-semantic-release/issues/10
.. _c05e13f: https://github.com/python-semantic-release/python-semantic-release/commit/c05e13f22163237e963c493ffeda7e140f0202c6


.. _changelog-v0.8.0:

v0.8.0 (2015-08-03)
===================

✨ Features
-----------

* Add ``check_build_status`` option, resolves `#5`_ (`310bb93`_)

* Add ``get_current_head_hash`` in git helpers (`d864282`_)

* Add git helper to get owner and name of repo (`f940b43`_)

.. _#5: https://github.com/python-semantic-release/python-semantic-release/issues/5
.. _310bb93: https://github.com/python-semantic-release/python-semantic-release/commit/310bb9371673fcf9b7b7be48422b89ab99753f04
.. _d864282: https://github.com/python-semantic-release/python-semantic-release/commit/d864282c498f0025224407b3eeac69522c2a7ca0
.. _f940b43: https://github.com/python-semantic-release/python-semantic-release/commit/f940b435537a3c93ab06170d4a57287546bd8d3b


.. _changelog-v0.7.0:

v0.7.0 (2015-08-02)
===================

✨ Features
-----------

* Add ``patch_without_tag`` option, resolves `#6`_ (`3734a88`_)

📖 Documentation
----------------

* Set up sphinx based documentation, resolves `#1`_ (`41fba78`_)

.. _#1: https://github.com/python-semantic-release/python-semantic-release/issues/1
.. _#6: https://github.com/python-semantic-release/python-semantic-release/issues/6
.. _3734a88: https://github.com/python-semantic-release/python-semantic-release/commit/3734a889f753f1b9023876e100031be6475a90d1
.. _41fba78: https://github.com/python-semantic-release/python-semantic-release/commit/41fba78a389a8d841316946757a23a7570763c39


.. _changelog-v0.6.0:

v0.6.0 (2015-08-02)
===================

✨ Features
-----------

* Add twine for uploads to pypi, resolves `#13`_ (`eec2561`_)

.. _#13: https://github.com/python-semantic-release/python-semantic-release/issues/13
.. _eec2561: https://github.com/python-semantic-release/python-semantic-release/commit/eec256115b28b0a18136a26d74cfc3232502f1a6


.. _changelog-v0.5.4:

v0.5.4 (2015-07-29)
===================

🪲 Bug Fixes
------------

* Add python2 not supported warning (`e84c4d8`_)

.. _e84c4d8: https://github.com/python-semantic-release/python-semantic-release/commit/e84c4d8b6f212aec174baccd188185627b5039b6


.. _changelog-v0.5.3:

v0.5.3 (2015-07-28)
===================

⚙️ Build System
---------------

* Add ``wheel`` as a dependency (`971e479`_)

.. _971e479: https://github.com/python-semantic-release/python-semantic-release/commit/971e4795a8b8fea371fcc02dc9221f58a0559f32


.. _changelog-v0.5.2:

v0.5.2 (2015-07-28)
===================

🪲 Bug Fixes
------------

* Fix python wheel tag (`f9ac163`_)

.. _f9ac163: https://github.com/python-semantic-release/python-semantic-release/commit/f9ac163491666022c809ad49846f3c61966e10c1


.. _changelog-v0.5.1:

v0.5.1 (2015-07-28)
===================

🪲 Bug Fixes
------------

* Fix push commands (`8374ef6`_)

.. _8374ef6: https://github.com/python-semantic-release/python-semantic-release/commit/8374ef6bd78eb564a6d846b882c99a67e116394e


.. _changelog-v0.5.0:

v0.5.0 (2015-07-28)
===================

✨ Features
-----------

* Add setup.py hook for the cli interface (`c363bc5`_)

.. _c363bc5: https://github.com/python-semantic-release/python-semantic-release/commit/c363bc5d3cb9e9a113de3cd0c49dd54a5ea9cf35


.. _changelog-v0.4.0:

v0.4.0 (2015-07-28)
===================

✨ Features
-----------

* Add publish command (`d8116c9`_)

.. _d8116c9: https://github.com/python-semantic-release/python-semantic-release/commit/d8116c9dec472d0007973939363388d598697784


.. _changelog-v0.3.2:

v0.3.2 (2015-07-28)
===================

* No change


.. _changelog-v0.3.1:

v0.3.1 (2015-07-28)
===================

🪲 Bug Fixes
------------

* Fix wheel settings (`1e860e8`_)

.. _1e860e8: https://github.com/python-semantic-release/python-semantic-release/commit/1e860e8a4d9ec580449a0b87be9660a9482fa2a4


.. _changelog-v0.3.0:

v0.3.0 (2015-07-27)
===================

✨ Features
-----------

* Add support for tagging releases (`5f4736f`_)

🪲 Bug Fixes
------------

* Fix issue when version should not change (`441798a`_)

.. _441798a: https://github.com/python-semantic-release/python-semantic-release/commit/441798a223195138c0d3d2c51fc916137fef9a6c
.. _5f4736f: https://github.com/python-semantic-release/python-semantic-release/commit/5f4736f4e41bc96d36caa76ca58be0e1e7931069


.. _changelog-v0.2.0:

v0.2.0 (2015-07-27)
===================

✨ Features
-----------

* added no-operation (``--noop``) mode (`44c2039`_)

⚙️ Build System
---------------

* Swapped pygit2 with gitpython to avoid libgit2 dependency (`8165a2e`_)

.. _44c2039: https://github.com/python-semantic-release/python-semantic-release/commit/44c203989aabc9366ba42ed2bc40eaccd7ac891c
.. _8165a2e: https://github.com/python-semantic-release/python-semantic-release/commit/8165a2eef2c6eea88bfa52e6db37abc7374cccba


.. _changelog-v0.1.1:

v0.1.1 (2015-07-27)
===================

🪲 Bug Fixes
------------

* Fix entry point (`bd7ce7f`_)

.. _bd7ce7f: https://github.com/python-semantic-release/python-semantic-release/commit/bd7ce7f47c49e2027767fb770024a0d4033299fa


.. _changelog-v0.1.0:

v0.1.0 (2015-07-27)
===================

* Initial Release
