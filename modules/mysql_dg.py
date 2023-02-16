"""
This module inserts generated data into your required MySQL table.
It is used in conjunction with the 'mysqlhelper' module.
For more information, see the section on MySQL in README.md

"""
import os
import re
import traceback

import pandas as pd
import mysql.connector

from configparser import ConfigParser
from sqlalchemy import create_engine
from config.definitions import ROOT_DIR, MYSQL
from modules import mysqlhelper, logging_module, exit_messages
from modules.data_generation_exceptions import cannotBeEvaluated

sql = mysqlhelper
configParser = ConfigParser()


def main():
    
    errors_raised, cnx, engine = False, None, None
    # Set up a logger for the mysql module
    mysql_logger = logging_module.setup_logger('mysql_logger', 'mysql.log', 'CRITICAL')
    configfilepath = os.path.join(ROOT_DIR, 'config', 'config.ini')
    try:
        configParser.read_file(open(configfilepath))
    except (Exception,):
        mysql_logger.critical("An error occurred while reading the config file: " + traceback.format_exc())

    # Fetch the mysql configuration options from config file  
    user_id = configParser.get(MYSQL, 'user')
    password_id = configParser.get(MYSQL, 'password')
    host_id = configParser.get(MYSQL, 'host')
    database_id = configParser.get(MYSQL, 'database')
    table_id = configParser.get(MYSQL, 'Table')
    n_record = int(configParser.get(MYSQL, 'RecordCount'))
    schema = configParser.get(MYSQL, 'Schema')
    schema_update = int(configParser.get(MYSQL, 'Schema_update'))
    schema_update_query = configParser.get(MYSQL, 'Schema_update_query')
    loglevel = configParser.get(MYSQL, 'LogLevel')
    # Change the log level to the level entered by user
    if loglevel is not None:
        mysql_logger = logging_module.set_logging_level(mysql_logger, loglevel)

    mysql_logger.info("Entered MySQL module: Data Generation Process for MySQL has begun.")
    
    # Creating MySQL connection
    try:
        cnx = mysql.connector.connect(user=user_id, password=password_id, host=host_id, database=database_id, port=3306)
        sql_conn = "mysql+pymysql://"+user_id+":"+password_id+"@"+host_id+":3306/"+database_id
        engine = create_engine(sql_conn)
    
    except (Exception,):
        mysql_logger.critical("An error has occurred while connecting to MySQL database: " + traceback.format_exc())
        exit_messages.error_exit()

    cursor = cnx.cursor()

    # Create/replace the table according to the schema entered by the user if schema is not empty
    if schema != "":
        try:
            cursor.execute(schema)
            mysql_logger.debug("Creating schema according to config file was successful.")
        except mysql.connector.Error as error:
            mysql_logger.critical("ERROR while creating schema from config file: {}".format(error))
            exit_messages.error_exit()

    if schema_update == 1:
        try:
            cursor.execute("""TRUNCATE table """+table_id+"""""")
            cursor.execute(schema_update_query)
        except mysql.connector.Error as error:
            mysql_logger.critical("ERROR while updating existing schema from config file: {}".format(error))
            exit_messages.error_exit()
            
    # Fetch the fields from the newly created/replaced table or using the table_id key
    # executing the statement using 'execute()' method
    try:
        cursor.execute("""SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where table_name ='"""+table_id+"""'""")
    except mysql.connector.Error as error:
        mysql_logger.critical("ERROR: {}".format(error))
        exit_messages.error_exit()

    # 'fetchall()' method fetches all the rows from the last executed statement
    table_schema = cursor.fetchall()

    data = {}
    rows_to_insert = pd.DataFrame()
    mysql_logger.debug("Fetching the relevant functions from the 'mysqlhelper' module...")
    id_count = 1
    # Generate records using the 'mysqlhelper' module
    for i in range(n_record):
        for j in range(len(table_schema)):
            col_name = sql.get_str(table_schema[j])

            if 'id' in col_name:
                data[col_name] = id_count
                id_count += 1

            elif 'latitude' in col_name or 'longitude' in col_name:
                data[col_name] = sql.lat_lng(col_name)

            elif 'geography' in col_name or 'geometry' in col_name or 'point' in col_name:
                data[col_name] = sql.point_data()

            elif 'int' in col_name:
                data[col_name] = sql.integer()
            
            elif 'blob_data' in col_name:
                data[col_name] = sql.bytes_value()

            elif re.match(r"\w*big_*num\w*", col_name) or re.match(r"\w*big_*int\w*", col_name):
                data[col_name] = sql.big_num_()

            elif 'numeric' in col_name or 'decimal' in col_name:
                data[col_name] = sql.numeric()

            elif 'float' in col_name:
                data[col_name] = sql.float_value()

            elif re.match(r"\w*date_*time\w*", col_name) or re.match(r"\w*time_*stamp\w*", col_name):
                res = sql.date_time_()
                data[col_name] = str(res) 

            elif 'time' in col_name and 'timestamp' not in col_name:
                data[col_name] = sql.time_value()

            elif 'bool' in col_name:
                data[col_name] = sql.boolean_data()

            elif 'string' in col_name or 'text' in col_name:
                data[col_name] = sql.text()

            elif 'bytes' in col_name:
                data[col_name] = sql.bytes_value()

            elif 'mobile' in col_name or 'phone' in col_name:
                data[col_name] = sql.mobile()

            else:
                try:
                    data[col_name] = sql.fake_data(col_name)
                except cannotBeEvaluated as e:
                    mysql_logger.error(e.message)
                    errors_raised = True

            data[col_name] = [data[col_name]]
   
        # Append newly generated row to the existing DataFrame
        rows_to_insert = pd.concat([rows_to_insert, pd.DataFrame(data)], ignore_index=True)
  
    # Load the DataFrame to mysql table using to_sql method
    mysql_logger.debug("Data generation complete (for batch-loading)!")
    try:
        rows_to_insert.to_sql(name=table_id, con=engine, if_exists='append', index=False)  # Make an API request.
    except (Exception,):
        mysql_logger.error("There was an error while batch-loading data mysql: " + traceback.format_exc())
        exit_messages.error_exit()

    mysql_logger.debug("Data generation process for MySQL is now complete!")
    
    return errors_raised

    
