"""
This modules contains all project definitions and constants.

"""

import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
BIGNUMERIC_RANGE = 5.7896044618658097711785492504343953926634992332820282019728792003956564819968E+38
INT_RANGE = 9223372036854775808
BIGINT_RANGE = 9223372036854775808
NUMERIC_RANGE = 9.9999999999999999999999999999999999999E+28
INT_RANGE_MYSQL = 2147483647
PG_INT_RANGE = 2147483648
LOCALE = "en_IN"  # This is the locale value to be used with the 'Faker' library. For supported locales, see Faker docs.
TZ_INFO = "Asia/Kolkata"  # This is the timezone that will be used in "timestamptz" values for PostgreSQL
GBQ = "Google BigQuery"
MYSQL = "MySQL"
PGSQL = "PostgreSQL"
CANNOT_BE_EVALUATED_ERROR = "Cannot be evaluated for data generation. You may attempt to rename column. For more " \
                            "information, see Google BigQuery limitations in README.md"
