"""Utility functions module."""

import logging
import os
import sys
from pathlib import Path

import yaml

DEFAULT_CONFIG_FOLDER = Path(os.environ.get("IM_DEFAULT_CONFIG_FOLDER", "config/"))


def get_logger(name="inspiring_murdock", level="DEBUG", filename=""):
    """Function to set logger to be used in code."""

    logger = logging.getLogger(name=name)
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # I need to set the set the lowest log leve on the logger
    # if I want to change the level on different handlers I can do so by setting it
    # On the the handler level.
    logger.setLevel(logging.getLevelName(level))
    if filename:
        file_handler = logging.FileHandler(filename=filename, mode="a")
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    stm_handler = logging.StreamHandler()
    stm_handler.setFormatter(log_format)
    logger.addHandler(stm_handler)

    return logger


def get_config(config_file=None):
    """Function that loads configuration from yaml file

     Defaults to "config/default.yaml"

    ."""
    logger = logging.getLogger("inspiring_murdock")
    default_config_file = DEFAULT_CONFIG_FOLDER.joinpath("default.yaml")
    try:
        config = yaml.safe_load(open(DEFAULT_CONFIG_FOLDER.joinpath("default.yaml")))
        if config_file:
            config.update(yaml.safe_load(open(config_file)))

        return config
    except FileNotFoundError as exp:
        logger.critical(
            '"%s" config file not found', config_file or default_config_file.name
        )
        logger.exception(exp)
    except yaml.YAMLError as exp:
        logger.critical(
            'Error while parsing config file "%s"',
            config_file or default_config_file.name,
        )
        logger.exception(exp)
        sys.exit(1)
