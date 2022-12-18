---
name: Bug report
about: Something isn't working properly
title: ""
labels: bug
assignees: ""
---

## The problem

_A clear and concise description of what the bug is._

## Expected behavior

_A short description of what you expected to happen._

## Environment

Please state which OS you are using and provide the output of the following commands:

```shell
python --version
pip --version
semantic-release --version
pip freeze
```

Please also indicate which Python build tool(s) you are using (e.g. `pip`, `build`,
`poetry`, etc.), including the version number too.

## Configuration

Please add your `semantic-release` configuration, and if applicable also provide
your `build-system` configuration from `pyproject.toml`.

## Logs

Please provide debug logs for the command you are using with the `-vv` flag, e.g.

```shell
semantic-release -vv version
```

If using GitHub actions, ensure the `additional_options` contains the `-vv` flag
for verbosity.

## Additional context

_Add any other information that could be useful, such as a link to your project
(if public), or an example commit._
