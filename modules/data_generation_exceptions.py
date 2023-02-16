"""
This module is used for setting up custom exceptions that can be raised in the project.
"""

from config.definitions import CANNOT_BE_EVALUATED_ERROR


class cannotBeEvaluated(Exception):
    message = ""

    def __init__(self, field):
        self.message = field + ": " + CANNOT_BE_EVALUATED_ERROR


class tableDoesNotExist(Exception):
    message = ""

    def __init__(self, field):
        self.message = "The table " + field + " does not exist."
