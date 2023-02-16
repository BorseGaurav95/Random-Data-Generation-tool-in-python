# Data Generation

Data generation is a crucial task when you work on data related projects. 
This data generation project helps in generating data for your choice of database/data warehouse using python libraries.

### Table of contents

- [Requirements](#requirements)
- [Supported databases and data warehouses](#supported-databases-and-data-warehouses)
  - [Google BigQuery](#google-bigquery)
  - [MySQL](#mysql)
  - [PostgreSQL](#postgresql)
- [Configuration](#configuration)
- [Limitations](#limitations)
  - [Google BigQuery Limitations](#google-bigquery-limitations)
  - [MySQL Limitations](#mysql-limitations)
  - [PostgreSQL Limitation](#postgresql-limitations)

### Requirements

The project has the following dependencies. 

#### Project Requirements

- configparser
- faker
- tqdm

#### Google BigQuery Requirements

- shapely
- google
- google.cloud.bigquery
- pandas
- pandas-gbq

#### MySQL Requirements

- mysql
- pymysql
- sqlalchemy
- pandas

#### PostgreSQL Requirements

- psycopg2 
- sqlalchemy 
- pytz
- pandas


### Supported databases and data warehouses

The project currently supports Google BigQuery, MySQL and PostgreSQL.

#### Google BigQuery
BigQuery is a completely serverless and cost-effective enterprise data warehouse. It has built-in machine learning and BI that works across clouds, and scales with your data.
This project uses the [BigQuery Client API](https://cloud.google.com/bigquery/docs/reference/libraries) for reading and streaming generated data into BigQuery.
It also uses the [pandas-gbq](https://pypi.org/project/pandas-gbq/) library to batch load generated data in BigQuery. 
The setup requires a service account JSON key file. The service account should have the **BigQuery Data Viewer** and **BigQuery Job User** roles.
For more information on setting up a service account in GCP, refer to the [documentation](https://cloud.google.com/iam/docs/creating-managing-service-accounts). 

The supported data types for BigQuery are: INT64, FLOAT64, NUMERIC, BIGNUMERIC, BOOLEAN, BYTES, DATE, TIME, DATETIME, TIMESTAMP, GEOGRAPHY and STRING.

#### MySQL
MySQL is a popular open-source relational database management system (RDBMS) used for storing and retrieving data. It is known for its reliability, ease of use, and flexibility. MySQL is used by many websites and applications to store and manage their data, and is a key component of the popular LAMP (Linux, Apache, MySQL, PHP/Python/Perl) web development stack.
This project uses the 'mysql-connector-python' and 'pymysql' library for connecting and querying the MySQL database.
It also uses the 'create_engine' function in 'SQLAlchemy' library to batch load generated data in MySQL. 
The setup requires adding either your machine's IP or all (0.0.0.0/0) in the allowed Connections for Cloud SQL. For steps, see [here](https://cloud.google.com/sql/docs/mysql/configure-ip#add).
Make sure the user account that you will enter in the config file has required permissions to read and write in the MySQL schema and database.

The supported data types for MySQL are: VARCHAR(size), INT(64), FLOAT, BIGINT, BOOLEAN, BLOB, DATE, TIME, DATETIME and TIMESTAMP. 

#### PostgreSQL
PostgreSQL, also known as Postgres, is a free and open-source relational database management system emphasizing extensibility and SQL compliance.
The project uses the [PostgreSQL API](https://pypi.org/project/psycopg2/) for reading data from PostgreSQL and the [SQLAlchemy](https://www.sqlalchemy.org/) library for writing generated data into PostgreSQL.
The setup requires adding either your machine's IP or all (0.0.0.0/0) in the allowed Connections for Cloud SQL. For steps, see [here](https://cloud.google.com/sql/docs/mysql/configure-ip#add).
Make sure the user account that you will enter in the config file has required permissions to read and write in the PostgreSQL schema and database. 

The supported data types for PostgreSQL are: bigint, bigserial, bit [ (n) ], boolean, bytea, date, inet, integer, json, numeric, text, time [ (p) ] [ without time zone ], timestamp [ (p) ] [ without time zone ] and timestamp [ (p) ] with time zone.


### Configuration

1. Download the zip file of the project to your local folder.
2. You may create a copy of the **config.ini** file (present in the 'config' folder) and rename it (for e.g., 'config_backup.ini') before editing the **config.ini** file in step 3. 
3. Edit the **config.ini** file for your required database/data warehouse.
4. Make sure to put the service account key or any relevant files in the 'files' folder. 
5. In the IDE of your choice or in command line (with Python3 installed in your system), run the below command (from the main folder) to install project dependencies:
```pip install -r requirements.txt```
6. Finally, to generate and insert data in your target database/data warehouse, run the below command:
```python main.py```

### Logging
1. Logging is **enabled** by default and cannot be disabled through the config file. 
2. All program logs are overwritten per execution and saved in the **"logs"** directory.
3. There are five logging levels as described below:
    1. **DEBUG:** Used to give detailed information. This level is mostly used for diagnosing issues in code. 
    2. **INFO:** Confirms the program works as expected. 
    3. **WARNING:** An indication that an unexpected event occurred or may occur.
    4. **ERROR:** Serious issue. Indicates that a program was unable to perform some action due to an error.
    5. **CRITICAL:** A serious error. Indicates that the program may be unable to continue running.
4. The main module runs on **INFO** by default and the log level for it **cannot be changed.** 
5. All the other modules run on **CRITICAL** by default and their log levels can be changed through the config file. 

### Limitations

#### Google BigQuery Limitations

1. Only Point data is supported for GEOGRAPHY types. 
2. REPEATED and RECORD data is currently not supported.
3. According to [this](https://cloud.google.com/bigquery/docs/error-messages#streaming) documentation, streaming to a nonexistent table will return a variation of a notFound response. Creating the table in response may not immediately be recognized by subsequent streaming inserts. Similarly, deleting and/or recreating a table may create a period of time when streaming inserts are effectively delivered to the old table and will not be present in the newly created table.
   Truncating a table's data (e.g. via a query job that uses writeDisposition of WRITE_TRUNCATE) may similarly cause subsequent inserts during the consistency period to be dropped.
4. Streaming inserts are not efficient when it comes to loading large amounts of data thus, prefer using batch loading to increase performance with large amounts of generated rows. 
5. **IMPORTANT:** Your field names must either be a substring of the field names for BigQuery data types according to [this](https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#data_type_properties) document 
   OR must be a substring of supported [Faker](https://faker.readthedocs.io/en/master/) function names. 

#### MySQL Limitations

1. REPEATED, RECORD, GEOGRAPHY data is currently not supported.

2. **IMPORTANT:** Your field names must either be a substring of the field names for MySQL data types according to [this](https://dev.mysql.com/doc/refman/8.0/en/data-types.html) document 
   OR must be a substring of supported [Faker](https://faker.readthedocs.io/en/master/) function names. 

#### PostgreSQL Limitations

1. All the data types not mentioned in the supported list are currently not supported for PostgreSQL. 
2. For types such as bigserial that work with fixed and variable length character limits, only variable length is supported. The project will not respect a set fixed length except for the "bit" data type.
3. **IMPORTANT:** Your field names must either be a substring of the field names for PostgreSQL data types according to [this](https://www.postgresql.org/docs/current/datatype.html) document 
   OR must be a substring of supported [Faker](https://faker.readthedocs.io/en/master/) function names.
