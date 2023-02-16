"""
This module inserts generated data into your required BigQuery table.
It is used in conjunction with the 'bigqueryhelper' module.
For more information, see the section on BigQuery in README.md

"""
import os
import re
import time
import traceback

import pandas as pd
from configparser import ConfigParser

from google.api_core.exceptions import BadRequest
from google.cloud import bigquery
from google.oauth2 import service_account

from config.definitions import ROOT_DIR, GBQ
from modules import bigqueryhelper, logging_module, exit_messages
from modules.data_generation_exceptions import tableDoesNotExist, cannotBeEvaluated

bqh = bigqueryhelper
configParser = ConfigParser()

def main():
    col_name, rows_to_insert, results, credentials = [], [], None, None
    errors_raised = False

    # Set up a logger for the bigquery module
    bigquery_logger = logging_module.setup_logger('bigquery_logger', 'bigquery.log', 'CRITICAL')

    configfilepath = os.path.join(ROOT_DIR, 'config', 'config.ini')
    try:
        configParser.read_file(open(configfilepath))
    except(Exception,):
        bigquery_logger.critical("An error occurred while reading the config file: " + traceback.format_exc())

    # Fetch the BigQuery configuration options from config file
    json_file_path = os.path.join(ROOT_DIR, 'files', configParser.get(GBQ, 'KeyFilePath'))
    project_id = configParser.get(GBQ, 'Project')
    dataset_id = configParser.get(GBQ, 'Dataset')
    table_id = configParser.get(GBQ, 'Table')
    n_record = int(configParser.get(GBQ, 'RecordCount'))
    schema = configParser.get(GBQ, 'Schema')
    streaming = int(configParser.get(GBQ, 'Streaming'))
    delay = int(configParser.get(GBQ, 'Delay'))
    loglevel = configParser.get(GBQ, 'LogLevel')

    full_table_name = project_id + "." + dataset_id + "." + table_id

    # Change the log level to the level entered by user
    if loglevel is not None:
        bigquery_logger = logging_module.set_logging_level(bigquery_logger, loglevel)

    bigquery_logger.info("Entered BigQuery module: Data Generation Process for BigQuery has begun.")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            json_file_path)
    except(Exception,):
        bigquery_logger.critical("An error has occurred while reading the service account key file: " + traceback.
                                 format_exc())
        exit_messages.error_exit()

    # Set up BigQuery client
    client = bigquery.Client(credentials=credentials, project=project_id)

    # Create/replace the table according to the schema entered by the user if schema is not empty
    if schema != "":
        job = client.query(schema)
        try:
            job.result()
            bigquery_logger.debug("Creating schema according to config file was successful.")
        except BadRequest as e:
            bigquery_logger.critical("ERROR while creating schema from config file: {}".format(e.args[0]))
            exit_messages.error_exit()

    # Fetch the fields from the newly created/replaced table or using the table_id key
    query_job = client.query("""
       SELECT column_name 
       FROM """ + project_id + """.""" + dataset_id + """.INFORMATION_SCHEMA.COLUMNS
        where table_name = '""" + table_id + """'
        """)
    try:
        results = query_job.result()
    except BadRequest as e:
        bigquery_logger.critical("ERROR: {}".format(e.args[0]))
        exit_messages.error_exit()

    if results.total_rows == 0:
        try:
            raise tableDoesNotExist(full_table_name)
        except tableDoesNotExist as e:
            bigquery_logger.critical(e.message)
            exit_messages.error_exit()

    for row in results:
        col_name.append(row.column_name)

    bigquery_logger.debug("Fetching the relevant functions from the 'bigqueryhelper' module...")
    funcs = {}
    # Fill the "funcs" dictionary with the 'bigqueryhelper' functions according to field names
    for _ in range(len(col_name)):
        col_name1 = col_name[_].lower()
        if 'id' in col_name1:
            funcs[col_name1] = "id"

        elif 'latitude' in col_name1:
            funcs[col_name1] = "latitude"

        elif 'longitude' in col_name1:
            funcs[col_name1] = "longitude"

        elif 'geography' in col_name1 or 'geometry' in col_name1 or 'point' in col_name1:
            funcs[col_name1] = "point_data"

        elif 'int' in col_name1:
            funcs[col_name1] = "integer"

        elif re.match(r"\w*big_*numeric\w*", col_name1) or re.match(r"\w*big_*decimal\w*", col_name1):
            funcs[col_name1] = "big_num_"

        elif 'numeric' in col_name1 or 'decimal' in col_name1:
            funcs[col_name1] = "numeric"

        elif 'float' in col_name1:
            funcs[col_name1] = "float_value"

        elif re.match(r"\w*date_*time\w*", col_name1) or re.match(r"\w*time_*stamp\w*", col_name1):
            funcs[col_name1] = "date_time_"

        elif 'time' in col_name1 and 'timestamp' not in col_name1:
            funcs[col_name1] = "time_value"

        elif 'bool' in col_name1:
            funcs[col_name1] = "boolean_data"

        elif 'string' in col_name1 or 'text' in col_name1:
            funcs[col_name1] = "text"

        elif 'bytes' in col_name1:
            funcs[col_name1] = "bytes_value"

        elif 'mobile' in col_name1 or 'phone' in col_name1:
            funcs[col_name1] = "mobile"

        else:
            try:
                funcs[col_name1] = [bqh.find_faker_func(col_name1)]
            except cannotBeEvaluated as e:
                bigquery_logger.error(e.message)
                errors_raised = True

    # Generate rows for target table by evaluating the 'bigqueryhelper' functions
    bigquery_logger.debug("Evaluating 'bigqueryhelper' functions to generate data...")
    rows = []
    for i in range(n_record):
        data = {}
        for j in funcs.keys():
            if funcs[j] == "id":
                data[j] = i
            elif isinstance(funcs[j], list):
                data[j] = bqh.fake_data(funcs[j][0])
            else:
                data[j] = eval("bqh." + funcs[j] + "()")
            rows_to_insert = [data] if streaming else data

        if streaming:
            # Stream a single row in BigQuery with the delay as requested by user
            try:
                client.insert_rows_json(full_table_name, rows_to_insert)
            except(Exception,):
                bigquery_logger.error("There was an error while streaming row to BigQuery: " + traceback.format_exc())
            time.sleep(delay)
        else:
            # Keep appending the rows together
            rows.append(rows_to_insert)

    if not streaming:
        bigquery_logger.debug("Data generation complete (for batch-loading)!")
        # Create a dataframe from the list "rows"
        rows_to_insert = pd.DataFrame(rows)

        # Load the DataFrame to BigQuery table using pandas_gbq
        try:
            rows_to_insert.to_gbq(dataset_id + "." + table_id, project_id, progress_bar=True,
                                  if_exists='append', credentials=credentials)  # Make an API request.
        except(Exception,):
            bigquery_logger.error("There was an error while batch-loading data to Google BigQuery: " + traceback.
                                  format_exc())
            exit_messages.error_exit()

    bigquery_logger.debug("Data generation process for Google BigQuery is now complete!")
    return errors_raised
