import os
import sys

import click
import toml
from loguru import logger

PYPROJECT_FILE = "pyproject.toml"


def get_version_from_toml():
    """Reads version from pyproject.toml."""
    try:
        config = toml.load(PYPROJECT_FILE)
        return config["project"]["version"]
    except (toml.TomlDecodeError, KeyError) as e:
        logger.error(f"❌ Error parsing pyproject.toml: {e}")
        sys.exit(1)


@click.command()
@click.option("--branch", default="main", help="Branch to compare the version with")
def tag_version(branch):
    """Extracts version and sets it as an environment variable for tagging."""
    version = get_version_from_toml()

    logger.info(f"🔍 Extracted version: {version}")

    # Set the version as an environment variable for GitHub Actions
    with open(os.environ["GITHUB_ENV"], "a") as env_file:
        print(f"VERSION={version}", file=env_file)


if __name__ == "__main__":
    tag_version()
