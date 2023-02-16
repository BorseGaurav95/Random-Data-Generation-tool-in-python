"""
This is the main module of data generation.
It checks for the presence of supported data warehouse and databases configuration and executes the required submodules.

"""

import os
import traceback

from config.definitions import ROOT_DIR, GBQ, PGSQL, MYSQL
from configparser import ConfigParser, MissingSectionHeaderError
from modules import bigquery, mysql_dg, postgresql, logging_module, exit_messages

configParser = ConfigParser()
configfilepath = os.path.join(ROOT_DIR, 'config', 'config.ini')
errors = False

# Set up a logger for the main module
main_logger = logging_module.setup_logger('main_logger', 'main.log', 'DEBUG')
main_logger.info("Data generation program has begun.")

try:
    configParser.read_file(open(configfilepath))
except MissingSectionHeaderError:
    main_logger.critical("No sections detected. Program has been terminated.")
    exit_messages.error_exit()

except (Exception,):
    main_logger.critical("An error occurred while reading the config file: "+traceback.format_exc())
    exit_messages.error_exit()

# Run the bigquery module if 'Google BigQuery' configuration is present/added in the config file
if configParser.has_section(GBQ):
    errors = bigquery.main()

# Run the mysql module if 'MySQL' configuration is present/added in the config file
if configParser.has_section(MYSQL):
    errors = True if mysql_dg.main() else errors

# Run the postgresql module if 'PostgreSQL' configuration is present/added in the config file
if configParser.has_section(PGSQL):
    errors = True if postgresql.main() else errors

if errors:
    exit_messages.warning_exit()
else:
    exit_messages.success_exit()
