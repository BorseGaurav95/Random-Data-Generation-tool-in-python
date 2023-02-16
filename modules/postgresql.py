"""
This module inserts generated data into your required PostgreSQL table.
It is used in conjunction with the 'postgresqlhelper' module.
For more information, see the section on PostgreSQL in README.md

"""
import os
import re
import traceback
import psycopg2

import pandas as pd
from configparser import ConfigParser
from sqlalchemy import create_engine

from config.definitions import ROOT_DIR, PGSQL
from modules import postgresqlhelper, logging_module, exit_messages
from modules.data_generation_exceptions import tableDoesNotExist, cannotBeEvaluated

pgh = postgresqlhelper
configParser = ConfigParser()

# Below function fetches the PostgreSQL configuration options from config file
def fetch_config(filename, section, logger):
    parameters = ("host", "port", "user", "password", "database")
    try:
        configParser.read_file(open(filename))
    except(Exception,):
        logger.critical("An error occurred while reading the config file: " + traceback.format_exc())

    db, dg_params = {}, {}
    if configParser.has_section(section):
        params = configParser.items(section)
        for param in params:
            if param[0] in parameters:
                db[param[0]] = param[1]
            else:
                dg_params[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db, dg_params


def main():
    conn, cur = None, None
    rows_to_insert, results = [], None
    errors_raised = False

    # Set up a logger for the postgresql module
    postgresql_logger = logging_module.setup_logger('postgresql_logger', 'postgresql.log', 'CRITICAL')

    configfilepath = os.path.join(ROOT_DIR, 'config', 'config.ini')
    params, dg_params = fetch_config(configfilepath, PGSQL, postgresql_logger)

    # Change the log level to the level entered by user
    if dg_params["loglevel"] is not None:
        postgresql_logger = logging_module.set_logging_level(postgresql_logger, dg_params["loglevel"])

    postgresql_logger.info("Entered PostgreSQL module: Data Generation Process for PostgreSQL has begun.")

    # Establish connection using sqlalchemy, this will be used to write to PostgreSQL
    conn_string = "postgresql://" + params["user"] + ":" + params["password"] + "@" + params["host"] + ":" + params[
        "port"] + "/" + params["database"]

    db = create_engine(conn_string)
    sql_conn = db.connect()

    try:
        # Connect to PostgreSQL using parameters fetched from config file, this will be used to read from PostgreSQL
        conn = psycopg2.connect(**params)

        # Create a cursor
        cur = conn.cursor()

    except(Exception,):
        postgresql_logger.critical("An error has occurred while connecting with PostgreSQL: " + traceback.
                                   format_exc())
        exit_messages.error_exit()

    # Create/replace the table according to the schema entered by the user if schema is not empty
    if dg_params["tableschema"] != "":
        try:
            # If table exists and table schema is provided by user, drop the existing table
            cur.execute("DROP TABLE IF EXISTS " + dg_params["table"] + ";")
            conn.commit()
            cur.execute(dg_params["tableschema"])
            conn.commit()
            postgresql_logger.debug("Creating schema according to config file was successful.")
        except(Exception,):
            postgresql_logger.critical("ERROR while creating schema from config file: " + traceback.format_exc())
            exit_messages.error_exit()

    if dg_params["schemaupdate"] == "1":
        try:
            cur.execute("TRUNCATE TABLE " + dg_params["table"] + ";")
            cur.execute(dg_params["schemaupdatequery"])
            conn.commit()
            postgresql_logger.debug("Altering schema according to config file was successful.")
        except(Exception,):
            postgresql_logger.critical("ERROR while updating existing schema from config file: "+traceback.format_exc())
            exit_messages.error_exit()

    # Fetch the fields from the newly created/replaced table or using the "table" key
    try:
        sql = "SELECT column_name FROM information_schema.columns WHERE table_schema = '" + dg_params[
            "schema"] + "' AND table_name='" + dg_params["table"] + "';"
        cur.execute(sql)
        conn.commit()
        results = [item for t in cur.fetchall() for item in t]

    except(Exception,):
        postgresql_logger.critical("ERROR: " + traceback.format_exc())
        exit_messages.error_exit()

    if not results:
        try:
            raise tableDoesNotExist(dg_params["table"])
        except tableDoesNotExist as e:
            postgresql_logger.critical(e.message)
            exit_messages.error_exit()

    # Build a SQL for fetching the fixed length of the "bit" data type, if any given
    postgresql_logger.debug("Fetching the relevant functions from the 'postgresqlhelper' module...")
    sql = "SELECT character_maximum_length FROM information_schema.columns WHERE table_schema = '" + dg_params[
        "schema"] + "' AND table_name='" + dg_params["table"] + "' AND column_name='"
    funcs = {}

    # Fill the "funcs" dictionary with the 'postgresqlhelper' functions according to the field names
    for _ in range(len(results)):
        col_name1 = str(results[_]).lower()
        if 'cidr' in col_name1 or 'inet' in col_name1:
            funcs[col_name1] = "inet"

        elif 'latitude' in col_name1:
            funcs[col_name1] = "latitude"

        elif 'longitude' in col_name1:
            funcs[col_name1] = "longitude"

        elif re.match(r"\w*big_*int\w*", col_name1):
            funcs[col_name1] = "bigint"

        elif 'int' in col_name1:
            funcs[col_name1] = "int_value"

        elif 'bit' in col_name1:
            sql = sql + col_name1 + "';"
            cur.execute(sql)
            conn.commit()
            max_limit = str([item for t in cur.fetchall() for item in t][0])
            funcs[col_name1] = "bit("+max_limit+")"

        elif 'numeric' in col_name1 or 'decimal' in col_name1 or 'float' in col_name1:
            funcs[col_name1] = "numeric"

        elif 'id' in col_name1 or 'serial' in col_name1:
            funcs[col_name1] = "id"

        elif re.match(r"\w*time_*stamp_*\w*zone\w*", col_name1):
            funcs[col_name1] = "timestamp_with_zone"

        elif re.match(r"\w*date_*time\w*", col_name1) or re.match(r"\w*time_*stamp\w*", col_name1):
            funcs[col_name1] = "timestamp"

        elif 'time' in col_name1 and 'timestamp' not in col_name1:
            funcs[col_name1] = "time_value"

        elif 'bool' in col_name1:
            funcs[col_name1] = "boolean_data"

        elif 'string' in col_name1 or 'text' in col_name1:
            funcs[col_name1] = "text"

        elif 'bytes' in col_name1 or 'bytea' in col_name1:
            funcs[col_name1] = "bytea_value"

        elif 'mobile' in col_name1 or 'phone' in col_name1:
            funcs[col_name1] = "mobile"

        else:
            try:
                funcs[col_name1] = [pgh.find_faker_func(col_name1)]
            except cannotBeEvaluated as e:
                postgresql_logger.error(e.message)
                errors_raised = True

    # Generate rows for target table by evaluating the 'postgresqlhelper' functions
    postgresql_logger.debug("Evaluating 'postgresqlhelper' functions to generate data...")
    rows = []
    for i in range(int(dg_params["recordcount"])):
        data = {}
        for j in funcs.keys():
            if funcs[j] == "id":
                data[j] = i+1
            elif isinstance(funcs[j], list):
                data[j] = pgh.fake_data(funcs[j][0])
            elif "bit" in funcs[j]:
                data[j] = eval("pgh."+funcs[j])
            else:
                data[j] = eval("pgh." + funcs[j] + "()")
            rows_to_insert = data
        rows.append(rows_to_insert)

    postgresql_logger.debug("Data generation complete!")

    # Load the DataFrame to the PostgreSQL table
    try:
        rows_to_insert = pd.DataFrame(rows)
        rows_to_insert.to_sql(dg_params["table"], sql_conn, if_exists="append", index=False)
    except(Exception,):
        postgresql_logger.error("There was an error while loading data to PostgreSQL: " + traceback.
                                format_exc())
        exit_messages.error_exit()

    if conn is not None:
        conn.close()
    postgresql_logger.debug("Data generation process for PostgreSQL is now complete!")
    return errors_raised
