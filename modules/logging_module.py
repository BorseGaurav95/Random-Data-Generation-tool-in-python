"""
This module is used for setting up loggers that will be used throughout the project.
For more information, see the section on Logging in README.md
"""

import logging

formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
def setup_logger(name, log_file, level="CRITICAL"):
    # All log files will be overwritten by default
    handler = logging.FileHandler("logs/"+log_file, 'w')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(eval("logging."+level))
    logger.addHandler(handler)

    return logger

def set_logging_level(logger, level):
    logger.setLevel(level)
    return logger



