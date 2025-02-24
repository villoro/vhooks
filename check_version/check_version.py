import subprocess
import toml
import click
from loguru import logger
from packaging import version

PYPROJECT_FILE = "pyproject.toml"


def fetch_pyproject_from_branch(branch):
    """Fetches pyproject.toml content from a specific Git branch."""
    logger.info(f"Fetching pyproject.toml from {branch=}")

    try:
        return subprocess.run(
            ["git", "show", f"origin/{branch}:{PYPROJECT_FILE}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        logger.error(f"❌ Could not fetch pyproject.toml from {branch=}")
        exit(1)


def get_version(branch=None):
    """
    Retrieves the package version from pyproject.toml.
    If branch is None, reads from the local file.
    Otherwise, fetches the file from the specified Git branch.
    """
    try:
        if branch:
            pyproject_content = fetch_pyproject_from_branch(branch)
            config = toml.loads(pyproject_content)
        else:
            logger.info("Fetching version from the current branch")
            config = toml.load(PYPROJECT_FILE)

        return config["project"]["version"]

    except Exception as e:
        logger.error(f"❌ Error reading version: {e}")
        exit(1)


def check_versions_are_consecutive(version_current, version_main):
    """Ensures version increments follow correct sequence (e.g., 1.0.0 → 1.0.1, not 1.0.0 → 1.2.0)."""
    diff_major = version_current.major - version_main.major
    diff_minor = version_current.minor - version_main.minor
    diff_micro = version_current.micro - version_main.micro

    if (diff_major > 1) or (diff_minor > 1) or (diff_micro > 1):
        return False

    if diff_major == 1:
        if (
            (diff_minor > 0)
            or (diff_micro > 0)
            or (version_current.minor != 0)
            or (version_current.micro != 0)
        ):
            return False
        return True
    elif diff_minor == 1:
        if (diff_micro > 0) or (version_current.micro != 0):
            return False
        return True
    return True


def validate_versions(version_current, version_main):
    """Checks if the versions are consecutive."""
    if not check_versions_are_consecutive(version_current, version_main):
        logger.error("❌ Only one version increase at a time allowed")
        exit(1)

    logger.success("✅ Versions are consecutive")


@click.command()
@click.option("--branch", default="main", help="Branch to compare the version with")
def check_version(branch):
    """Compares current version with the specified branch version."""
    current_version_str = get_version()
    branch_version_str = get_version(branch)

    logger.info(f"🔍 Current branch version: {current_version_str}")
    logger.info(f"🔍 {branch.title()} branch version: {branch_version_str}")

    current_version = version.parse(current_version_str)
    branch_version = version.parse(branch_version_str)

    # Check if version is updated
    if current_version <= branch_version:
        logger.error(
            f"❌ Version has not been updated. Please increment the version before merging into '{branch}'."
        )
        exit(1)

    # Check if versions are consecutive
    validate_versions(current_version, branch_version)

    logger.success("✅ Version is correctly updated.")


if __name__ == "__main__":
    check_version()
