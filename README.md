# python-semantic-release [![Build status](https://ci.frigg.io/relekang/python-semantic-release.svg)][last-build] [![Coverage status](https://ci.frigg.io/relekang/python-semantic-release/coverage.svg)][last-build]

Automatic semantic versioning for python projects

> **This is not usable, yet.**

## Install
```
pip install python-semantic-release
```

## Usage
The general idea is to have some sort of tag in commit messages that indicates certain types of changes.
If a commit message lack a tag it is ignored. Running release can be run locally or from a CI service.

```
Usage: semantic-release [OPTIONS] COMMAND

Options:
  --major  Force major version.
  --minor  Force minor version.
  --patch  Force patch version.
  --help   Show this message and exit.
```

### Commands

* `version` - Create a new release. Will change the version and commit it.

### Configuration
All configuration described here belongs in `setup.cfg` in a section: `semantic-release`.

`version_variable` - The filename and variable name of where the version number is stored, e.g.
                     `semantic_release/__init__.py:__version__`.

#### Tags
There are a set of tags used to evaluate the changes from commit messages. They can be configured
to meet what you want them to be. The different tags are listed below with their defaults.

* **Major change:** `major_tag = :boom:` :boom:
* **Minor change:** `minor_tag = :sparkles:` :sparkles:
* **Patch change:** `patch_tag = :bug:` :bug:

[last-build]: https://ci.frigg.io/relekang/python-semantic-release/last/
