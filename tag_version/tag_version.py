import json
import os
import sys

import click
import toml
import yaml
from loguru import logger

DEFAULT_FILE = "pyproject.toml"


def load_file(file_path):
    """Loads and parses the version file based on its format."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        if file_path.endswith(".toml"):
            return toml.loads(content)
        elif file_path.endswith(".json"):
            return json.loads(content)
        elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
            return yaml.safe_load(content)
        else:
            logger.error(f"❌ Unsupported file format: {file_path}")
            sys.exit(1)

    except (FileNotFoundError, KeyError):
        logger.error(f"❌ Could not find {file_path} or path is invalid")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error parsing {file_path}: {e}")
        sys.exit(1)


def get_version(file_path, version_path):
    """Extracts version from the specified file."""
    config = load_file(file_path)

    # Navigate the structure using the specified path
    keys = version_path.split("/")
    version_value = config
    for key in keys:
        version_value = version_value[key]

    return version_value


@click.command()
@click.option(
    "--file",
    default=DEFAULT_FILE,
    help="File to extract the version from (supports .toml, .json, .yml)",
)
@click.option(
    "--path",
    default="project/version",
    help="Path inside the file to extract the version",
)
def tag_version(file, path):
    """Extracts version and sets it as an environment variable for tagging."""
    version = get_version(file, path)

    logger.info(f"🔍 Extracted version from '{file}:{path}': {version}")

    # Set the version as an environment variable for GitHub Actions
    with open(os.environ["GITHUB_ENV"], "a") as env_file:
        print(f"VERSION={version}", file=env_file)


if __name__ == "__main__":
    tag_version()
