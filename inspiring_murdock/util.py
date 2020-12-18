""" Utility functions module """

import logging


def get_logger(name='inspiring_murdock', level="DEBUG", filename=""):
    """ Function to set logger to be used in code """

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
