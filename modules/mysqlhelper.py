"""
This module generates data for supported MySQL column/data types.
It is used in conjunction with the 'mysql' module.
For more information, see the section on MySQL in README.md

"""
import random as r
from faker import Faker
from datetime import time
from config.definitions import BIGINT_RANGE, INT_RANGE_MYSQL, CANNOT_BE_EVALUATED_ERROR, LOCALE
import os
from modules.data_generation_exceptions import cannotBeEvaluated

fake = Faker(locale=LOCALE)
Faker.seed(99)


def big_num_():
    return r.uniform(-BIGINT_RANGE, BIGINT_RANGE)


def integer():
    return int(r.uniform(-INT_RANGE_MYSQL, INT_RANGE_MYSQL))


def float_value():
    return float(r.random())


def time_value():
    values = list(map(int, fake.time().split(":")))
    return time(values[0], values[1], values[2])


def text():
    return fake.text()


def lat_lng(col_name1):
    col_data = "fake." + col_name1 + '()'
    return float(eval(col_data))


def bytes_value():
    return os.urandom(10)


def date_time_():
    return fake.date_time()


def boolean_data():
    return r.choice([True, False])


def mobile():
    return fake.phone_number()


def get_str(col_str):
    return str(list(col_str)).strip("[]").strip("''")


def fake_data(col_name):
    for elem in dir(fake):
        if elem in col_name:
            return str(eval("fake." + elem + "()"))
    print(col_name+": "+CANNOT_BE_EVALUATED_ERROR)
    raise cannotBeEvaluated(col_name)
