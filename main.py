"""Add a module docstring here.
"""
import argparse

import yaml
from avolib.logging import ConfigureLogger, GetLogger


def main(config_file):
    """Add main docstring.

    Args:
        config_file (yml): application configuration file

    Returns:
        None
    """

    # Get the logger
    logger = GetLogger(config_file["APP_NAME"])
    logger.debug("Here is a sample logging statement")

    # Write your code here. Make sure you test along the way!


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a description.")
    parser.add_argument(
        "path",
        metavar="path/to/config/file",
        type=str,
        help="Path to configuration file.",
    )

    args = parser.parse_args()

    with open(args.path, "r") as f:
        config = yaml.safe_load(f)

    ConfigureLogger(config["APP_NAME"], config["LOGGING"])

    # Run app with config
    main(config)
