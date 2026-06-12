# vhooks GitHub Actions

![GitHub release (latest by date)](https://img.shields.io/github/v/release/villoro/vhooks)

This repository contains three reusable GitHub Actions:

1. **Check Package Version** – Validates that the version in a specified file (e.g., `pyproject.toml`, `version.json`, `config.yml`) has been incremented before merging a pull request.
2. **Tag Version** – Automatically tags a commit with the version from a specified file when selected paths change in the `main` branch.
3. **Check Versions Match** – Validates that the version is identical across multiple files/paths.

## 🚀 Check Package Version

### Usage

Add this workflow to `.github/workflows/check_version.yml`:

```yaml
name: Check Version

on:
  pull_request:
    branches:
      - main

jobs:
  check_version:
    runs-on: ubuntu-latest
    steps:
      - uses: villoro/vhooks/check_version@1.4.0
        with:
          branch: "main"  # Branch to compare against
          file: "pyproject.toml"  # File to extract the version from
          path: "project/version"  # Path inside the file
          filters: |
            code:
              - 'src/ecs_northius/**'
              - 'pyproject.toml'
```

### 🛠️ Inputs

| Input        | Description                                                            | Required | Default                    |
| ------------ | ---------------------------------------------------------------------- | -------- | -------------------------- |
| `repository` | Repository to check the version in.                                    | ✅ Yes    | `${{ github.repository }}` |
| `ref`        | Branch or commit ref to evaluate.                                      | ✅ Yes    | `${{ github.ref }}`        |
| `branch`     | Target branch to compare against.                                      | ❌ No     | `main`                     |
| `file`       | File containing the version (supports `.toml`, `.json`, `.yml`).       | ❌ No     | `pyproject.toml`           |
| `path`       | Path inside the file to extract the version.                           | ❌ No     | `project/version`          |
| `filters`    | YAML configuration for `dorny/paths-filter`. Must define a `code` key. | ❌ No     | `code: ['**']`             |

### ✅ Expected Behavior

* **Runs only if specified paths change.**
* **Fails the PR** if the version is missing, unchanged, or skips versions.
* **Passes** when the version has been correctly incremented.

## 🚀 Tag Version

### Usage

Add this workflow to `.github/workflows/tag_version.yml`:

```yaml
name: Tag Version

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  tag_version:
    runs-on: ubuntu-latest
    steps:
      - uses: villoro/vhooks/tag_version@1.4.0
        with:
          file: "pyproject.toml"  # File containing the version
          path: "project/version"  # Path inside the file
          filters: |
            code:
              - 'src/ecs_northius/**'
              - 'pyproject.toml'
```

### 🛠️ Inputs

| Input        | Description                                                            | Required | Default           |
| ------------ | ---------------------------------------------------------------------- | -------- | ----------------- |
| `branch`     | Branch to check version from.                                          | ❌ No     | `main`            |
| `file`       | File to extract the version from (supports `.toml`, `.json`, `.yml`).  | ❌ No     | `pyproject.toml`  |
| `path`       | Path inside the file to extract the version.                           | ❌ No     | `project/version` |
| `filters`    | YAML configuration for `dorny/paths-filter`. Must define a `code` key. | ❌ No     | `code: ['**']`    |
| `tag-prefix` | Optional prefix to prepend to the tag (e.g. `v` creates `v1.2.3`).     | ❌ No     | *(empty)*         |


### ✅ Expected Behavior

* **Runs only when watched paths change.**
* **Extracts version** from the specified file and path.
* **Creates a Git tag** if it doesn’t already exist.
* **Skips tagging** if the tag is already present.

## 🚀 Check Versions Match

Validates that the version is **identical** across multiple files/paths (e.g. `pyproject.toml`, `dbt_project.yml`, `uv.lock`). Useful when several files must stay in sync.

### Usage

Add this workflow to `.github/workflows/check_versions_match.yml`:

```yaml
name: Check Versions Match

on:
  pull_request:
    branches:
      - main

jobs:
  check_versions_match:
    runs-on: ubuntu-latest
    steps:
      - uses: villoro/vhooks/check_versions_match@1.4.0
        with:
          targets: |
            - file: dbt_project.yml
              path: version
            - file: pyproject.toml
              path: project/version
            - file: pyproject.toml
              path: tool/bumpversion/current_version
            - file: uv.lock
              path: package[name=dbt-northius]/version
          filters: |
            code:
              - 'pyproject.toml'
              - 'dbt_project.yml'
              - 'uv.lock'
```

### 🛠️ Inputs

| Input     | Description                                                            | Required | Default        |
| --------- | --------------------------------------------------------------------- | -------- | -------------- |
| `targets` | YAML list of `{file, path}` entries whose versions must all match.    | ✅ Yes    | —              |
| `filters` | YAML configuration for `dorny/paths-filter`. Must define a `code` key. | ❌ No     | `code: ['**']` |

### 🧭 Path Syntax

`path` is slash-separated (`project/version`, `tool/bumpversion/current_version`). To select a list item by a field value, use a `key[field=value]` selector — handy for `uv.lock`:

```
package[name=dbt-northius]/version
```

Supported formats: `.toml`, `.lock` (TOML), `.json`, `.yml`/`.yaml`.

### ✅ Expected Behavior

* **Runs only if specified paths change.**
* **Fails the PR** if any file/path is missing or the extracted versions differ.
* **Passes** when all versions are exactly equal.

## 🔗 Related Links

* [GitHub Actions Documentation](https://docs.github.com/en/actions)
* [Python Packaging Guide](https://packaging.python.org/)
