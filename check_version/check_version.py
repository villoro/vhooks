import json
import subprocess
import sys

import click
import toml
import yaml
from loguru import logger
from packaging import version

DEFAULT_FILE = "pyproject.toml"


def fetch_file_from_branch(branch, file_path):
    """Fetches file content from a specific Git branch."""
    logger.info(f"Fetching {file_path} from {branch=}")

    try:
        return subprocess.run(
            ["git", "show", f"origin/{branch}:{file_path}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        logger.error(f"❌ Could not fetch {file_path} from {branch=}")
        sys.exit(1)


def parse_file_content(file_path, content):
    """Parses the file content based on the file extension."""
    if file_path.endswith(".toml"):
        return toml.loads(content)
    elif file_path.endswith(".json"):
        return json.loads(content)
    elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
        return yaml.safe_load(content)
    else:
        logger.error(f"❌ Unsupported file format: {file_path}")
        sys.exit(1)


def load_file(file_path, branch=None):
    """Loads the file content from the local file or a specified Git branch."""
    try:
        if branch:
            file_content = fetch_file_from_branch(branch, file_path)
            return parse_file_content(file_path, file_content)
        else:
            logger.info(f"Fetching data from local {file_path}")
            with open(file_path, "r") as f:
                return parse_file_content(file_path, f.read())

    except (FileNotFoundError, KeyError):
        logger.error(f"❌ Could not find {file_path} or path is invalid")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error parsing {file_path}: {e}")
        sys.exit(1)


def get_version(file_path, version_path, branch=None):
    """Retrieves the package version from the specified file."""
    config = load_file(file_path, branch)

    # Extract version from the nested structure
    keys = version_path.split("/")
    version_value = config
    for key in keys:
        version_value = version_value[key]

    return version_value


def check_versions_are_consecutive(version_current, version_main):
    """
    Ensures version increments follow correct sequence:
    - ✅ Allowed: 1.0.0 → 1.0.1, 1.0.0 → 1.1.0, 1.0.0 → 2.0.0
    - ❌ Not Allowed: 1.0.0 → 1.2.0, 1.0.0 → 2.1.0
    """
    diff_major, diff_minor, diff_micro = (
        version_current.major - version_main.major,
        version_current.minor - version_main.minor,
        version_current.micro - version_main.micro,
    )

    if diff_major > 1 or diff_minor > 1 or diff_micro > 1:
        return False

    if diff_major == 1 and (
        diff_minor > 0
        or diff_micro > 0
        or version_current.minor != 0
        or version_current.micro != 0
    ):
        return False

    if diff_minor == 1 and (diff_micro > 0 or version_current.micro != 0):
        return False

    return True


def validate_versions(version_current, version_main):
    """Checks if the versions are consecutive."""
    if not check_versions_are_consecutive(version_current, version_main):
        logger.error("❌ Only one version increase at a time allowed")
        sys.exit(1)

    logger.success("✅ Versions are consecutive")


@click.command()
@click.option("--branch", default="main", help="Branch to compare the version with")
@click.option(
    "--file",
    default=DEFAULT_FILE,
    help="File to read the version from (supports .toml, .json, .yml)",
)
@click.option(
    "--path",
    default="project/version",
    help="Path inside the file to extract the version",
)
def check_version(branch, file, path):
    """Compares current version with the specified branch version."""
    current_version_str = get_version(file, path)
    branch_version_str = get_version(file, path, branch)

    logger.info(f"🔍 Current branch version: {current_version_str}")
    logger.info(f"🔍 {branch.title()} branch version: {branch_version_str}")

    current_version = version.parse(current_version_str)
    branch_version = version.parse(branch_version_str)

    # Check if version is updated
    if current_version <= branch_version:
        logger.error(
            f"❌ Version has not been updated. Please increment the version before merging into '{branch}'."
        )
        sys.exit(1)

    # Check if versions are consecutive
    validate_versions(current_version, branch_version)

    logger.success("✅ Version is correctly updated.")


if __name__ == "__main__":
    check_version()
