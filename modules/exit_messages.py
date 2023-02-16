"""
This module contains all program exit functions that can be used across the project.
"""

import datetime
import sys

from colorama import Fore


def error_exit():
    print(str(datetime.datetime.now()) + " | " + Fore.RED + "The program was terminated due to a critical error. Check "
                                                            "logs for more info.")
    sys.exit(1)


def success_exit():
    print(str(datetime.datetime.now()) + " | " + Fore.GREEN + "The program has successfully finished its execution "
                                                              "without any errors.")
    sys.exit(1)


def warning_exit():
    print(str(datetime.datetime.now()) + " | " + Fore.YELLOW + "The program has finished its execution "
                                                               "but some errors were raised. Check logs for more info.")
