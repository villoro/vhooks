# Check Version GitHub Action

![GitHub release (latest by date)](https://img.shields.io/github/v/release/vhooks/check_version)

This GitHub Action ensures that the version in `pyproject.toml` has been updated before merging a pull request.

## 🚀 Usage

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
      - uses: vhooks/check_version@0.1.0
        with:
          branch: "main"  # Change this to compare against a different branch
```

## 🛠️ Inputs

| Input     | Description                                | Required | Default |
|-----------|--------------------------------------------|----------|---------|
| `branch`  | The branch to compare the version against. | ❌ No   | `main`  |

## ✅ Expected Behavior

- **Fails the PR** if the version in `pyproject.toml` has **not** been updated.
- **Passes the PR** if the version has been correctly incremented.

## 🎯 Example Scenarios

| Scenario | Expected Outcome |
|----------|------------------|
| Version **not updated** | ❌ Fails, requires increment |
| Version **incremented** | ✅ Passes |
| Comparing against a **different branch** | ✅ Works with `--branch=<branch>` |

## 🔗 Related Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)
