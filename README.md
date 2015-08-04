# python-semantic-release [![Build status](https://ci.frigg.io/relekang/python-semantic-release.svg)][last-build] [![Coverage status](https://ci.frigg.io/relekang/python-semantic-release/coverage.svg)][last-build]

Automatic semantic versioning for python projects. [This blogpost explains in more detail][blogpost].

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
  --noop   No-operations mode, finds the new version number without changing it.
  --help   Show this message and exit.
```

### Commands

* `version` - Create a new release. Will change the version, commit it and tag it.
* `publish` - Runs version before pushing to git and uploading to pypi.

### Running commands from setup.py
Add the following to your setup.py and you will be able to run `python setup.py <command>`
as you woul `semantic-release <command>`.

```python
try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass
```

### Configuration
Configuration belong in `semantic_release` section of the setup.cfg file in your project.
Details about configuration options can be found in [the configuration documentation][config-docs].

[last-build]: https://ci.frigg.io/relekang/python-semantic-release/last/
[blogpost]: http://rolflekang.com/python-semantic-release/
[config-docs]: http://python-semantic-release.readthedocs.org/en/latest/configuration.html
