import subprocess
import toml
import click
from loguru import logger
from packaging import version

PYPROJECT_FILE = "pyproject.toml"


def get_version_from_toml():
    """Reads version from pyproject.toml (current branch)."""
    config = toml.load(PYPROJECT_FILE)
    return config["project"]["version"]


def get_branch_version(branch):
    """Fetches pyproject.toml version from the specified branch."""
    try:
        main_version = subprocess.run(
            ["git", "show", f"origin/{branch}:pyproject.toml"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        main_config = toml.loads(main_version)
        return main_config["project"]["version"]
    except subprocess.CalledProcessError:
        logger.error(f"Could not fetch version from branch '{branch}'")
        exit(1)


@click.command()
@click.option("--branch", default="main", help="Branch to compare the version with")
def check_version(branch):
    """Compares current version with the specified branch version."""
    current_version = get_version_from_toml()
    branch_version = get_branch_version(branch)

    logger.info(f"Current branch version: {current_version}")
    logger.info(f"{branch} branch version: {branch_version}")

    if version.parse(current_version) <= version.parse(branch_version):
        logger.error(
            f"❌ Version has not been updated. Please increment the version before merging into '{branch}'."
        )
        exit(1)

    logger.success("✅ Version is correctly updated.")


if __name__ == "__main__":
    check_version()
