# vhooks GitHub Actions

![GitHub release (latest by date)](https://img.shields.io/github/v/release/villoro/vhooks)

This repository contains two GitHub Actions:
1. **Check Version** - Ensures that the version in `pyproject.toml` has been updated before merging a pull request.
2. **Tag Version** - Automatically tags a commit with the version from `pyproject.toml` when changes are merged into `main`.

---

## 🚀 Check Version

### Usage

Add the following to your `.github/workflows/check_version.yml`:

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
      - uses: villoro/vhooks/check_version@1.0.0
        with:
          branch: "main"  # Change this to compare against a different branch
```

### 🛠️ Inputs

| Input     | Description                                | Required | Default |
|-----------|--------------------------------------------|----------|---------|
| `branch`  | The branch to compare the version against. | ❌ No   | `main`  |

### ✅ Expected Behavior

- **Fails the PR** if the version in `pyproject.toml` has **not** been updated.
- **Passes the PR** if the version has been correctly incremented.

### 🎯 Example Scenarios

| Scenario | Expected Outcome |
|----------|------------------|
| Version **not updated** | ❌ Fails, requires increment |
| Version **incremented** | ✅ Passes |
| Comparing against a **different branch** | ✅ Works with `--branch=<branch>` |

---

## 🚀 Tag Version

### Usage

Add the following to your `.github/workflows/tag_version.yml`:

```yaml
name: Tag Version

on:
  push:
    branches:
      - main
    paths:
      - pyproject.toml

permissions:
  contents: write

jobs:
  tag_version:
    runs-on: ubuntu-latest
    steps:
      - uses: villoro/vhooks/tag_version@1.0.0
```

### ✅ Expected Behavior

- **Creates a new Git tag** when `pyproject.toml` is modified in `main`.
- **Skips tagging** if the version is already tagged.

---

## 🔗 Related Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)

