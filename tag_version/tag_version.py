import os
import sys

import click
import toml
from loguru import logger

PYPROJECT_FILE = "pyproject.toml"


def get_version_from_toml(path):
    """Reads version from a specified path in pyproject.toml."""
    try:
        config = toml.load(PYPROJECT_FILE)

        # Navigate the TOML structure using the specified path
        keys = path.split("/")
        version_value = config
        for key in keys:
            version_value = version_value[key]

        return version_value

    except KeyError:
        logger.error(f"❌ Specified path '{path}' not found in pyproject.toml")
        sys.exit(1)
    except (toml.TomlDecodeError, Exception) as e:
        logger.error(f"❌ Error parsing pyproject.toml: {e}")
        sys.exit(1)


@click.command()
@click.option("--branch", default="main", help="Branch to compare the version with")
@click.option(
    "--path",
    default="project/version",
    help="Path inside pyproject.toml to extract the version",
)
def tag_version(branch, path):
    """Extracts version and sets it as an environment variable for tagging."""
    version = get_version_from_toml(path)

    logger.info(f"🔍 Extracted version from '{path}': {version}")

    # Set the version as an environment variable for GitHub Actions
    with open(os.environ["GITHUB_ENV"], "a") as env_file:
        print(f"VERSION={version}", file=env_file)


if __name__ == "__main__":
    tag_version()
