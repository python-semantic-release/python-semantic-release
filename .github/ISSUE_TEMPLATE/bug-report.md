---
name: Bug Report
about: Something isn't working as expected
labels:
    - bug
    - triage
---

## Bug Report

### Description
<!-- A description of what you were trying to do -->



### Expected behavior
<!-- A short description of what you expected to happen. -->



### Actual behavior
<!-- A short description of what actually happened. -->



### Environment

-  **Operating System (w/ version):** <!-- Windows 11, Debian Bookworm, etc. -->
-  **Python version:** <!-- x.x.x -->
-  **Pip version:** <!-- x.x.x -->
-  **Semantic-release version:** <!-- x.x.x -->
-  **Build tool (w/ version):** <!-- build x.x.x, poetry x.x.x, etc. -->

<!-- Please provide the output of the following commands -->

<details>
<summary><code>pip freeze</code></summary>

```log

```

</details>

<br>
<!-- If you have a problem with version determination, we need a snapshot
of the git log prior to the version command. -->

<details>
<summary><code>git log --oneline --decorate --graph --all -n 50</code></summary>

```log

```

</details>


### Configuration

<details>
<summary>Semantic Release Configuration</summary>

```toml
```

</details>
<br>

<!-- If applicable to the issue, please provide the build-system configuration
from your pyproject.toml file. -->

<details>
<summary>Build System Configuration</summary>

```toml
```

</details>
<br>

<!--
If GitHub Actions is applicable to your issue, please provide your job definition.
-->

<details>
<summary>GitHub Actions Job Definition</summary>

```yaml

```

</details>


### Execution Log

<!--
Please rerun the command using with the `-vv` option and include the log here

If you are using GitHub Actions, include the log output from the job with the -vv flag
as a root_options argument.
-->

<details>
<summary><code>semantic-release -vv <i>command</i></code></summary>

```log

```

</details>

### Additional context

<!--
Feel free to add any other information that could be useful,
such as a link to your project (if public), links to a failing GitHub Action,
or an example commit.
-->
