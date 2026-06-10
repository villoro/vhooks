import json
import re
import sys

import click
import toml
import yaml
from loguru import logger

# Matches an array-by-key selector like: package[name=dbt-northius]
ARRAY_SELECTOR = re.compile(r"^(?P<key>[^\[]+)\[(?P<field>[^=]+)=(?P<value>[^\]]+)\]$")


def parse_file_content(file_path, content):
    """Parses file content based on its extension."""
    if file_path.endswith(".toml") or file_path.endswith(".lock"):
        return toml.loads(content)
    elif file_path.endswith(".json"):
        return json.loads(content)
    elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
        return yaml.safe_load(content)
    else:
        logger.error(f"❌ Unsupported file format: {file_path}")
        sys.exit(1)


def load_file(file_path):
    """Loads and parses a file from the local filesystem."""
    try:
        logger.info(f"Fetching data from local {file_path}")
        with open(file_path, "r") as f:
            return parse_file_content(file_path, f.read())
    except FileNotFoundError:
        logger.error(f"❌ Could not find {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error parsing {file_path}: {e}")
        sys.exit(1)


def navigate(data, key, file_path, version_path):
    """Resolves a single path segment, supporting array-by-key selectors.

    Plain keys index into dicts. A selector like ``package[name=foo]`` picks the
    element of a list whose ``name`` field equals ``foo``.
    """
    match = ARRAY_SELECTOR.match(key)

    if match:
        list_key, field, value = match.group("key", "field", "value")
        items = data[list_key]
        for item in items:
            if str(item.get(field)) == value:
                return item
        logger.error(
            f"❌ No item with {field}={value} in '{list_key}' "
            f"while resolving '{version_path}' in {file_path}"
        )
        sys.exit(1)

    return data[key]


def get_version(file_path, version_path):
    """Extracts a version from a file given a slash-separated path."""
    data = load_file(file_path)

    try:
        for key in version_path.split("/"):
            data = navigate(data, key, file_path, version_path)
    except (KeyError, TypeError):
        logger.error(f"❌ Path '{version_path}' is invalid in {file_path}")
        sys.exit(1)

    return str(data)


def parse_targets(targets):
    """Parses the YAML targets input into a list of (file, path) pairs."""
    try:
        parsed = yaml.safe_load(targets)
    except Exception as e:
        logger.error(f"❌ Could not parse 'targets' YAML: {e}")
        sys.exit(1)

    if not isinstance(parsed, list) or not parsed:
        logger.error("❌ 'targets' must be a non-empty YAML list of {file, path}")
        sys.exit(1)

    pairs = []
    for entry in parsed:
        if not isinstance(entry, dict) or "file" not in entry or "path" not in entry:
            logger.error(f"❌ Each target must define 'file' and 'path': {entry}")
            sys.exit(1)
        pairs.append((entry["file"], entry["path"]))

    return pairs


@click.command()
@click.option(
    "--targets",
    required=True,
    help="YAML list of {file, path} entries whose versions must match",
)
def check_versions_match(targets):
    """Checks that the version is identical across all configured files/paths."""
    pairs = parse_targets(targets)

    versions = {}
    for file_path, version_path in pairs:
        value = get_version(file_path, version_path)
        logger.info(f"🔍 {file_path}:{version_path} -> {value}")
        versions[f"{file_path}:{version_path}"] = value

    unique = set(versions.values())
    if len(unique) > 1:
        logger.error("❌ Versions do not match:")
        for location, value in versions.items():
            logger.error(f"   {location} -> {value}")
        sys.exit(1)

    logger.success(f"✅ All versions match: {unique.pop()}")


if __name__ == "__main__":
    check_versions_match()
