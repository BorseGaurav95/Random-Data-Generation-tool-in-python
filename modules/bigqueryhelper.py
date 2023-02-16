"""
This module generates data for supported BigQuery column/data types.
It is used in conjunction with the 'bigquery' module.
For more information, see the section on BigQuery in README.md

"""
import random as r
import base64
from shapely.geometry import Point
from faker import Faker
from datetime import time
from config.definitions import BIGNUMERIC_RANGE, INT_RANGE, NUMERIC_RANGE, LOCALE
from modules.data_generation_exceptions import cannotBeEvaluated

fake = Faker(locale=LOCALE)
Faker.seed()


def big_num_():
    return r.uniform(-BIGNUMERIC_RANGE, BIGNUMERIC_RANGE)


def integer():
    return int(r.uniform(-INT_RANGE, INT_RANGE))


def numeric():
    return r.uniform(-NUMERIC_RANGE, NUMERIC_RANGE)


def float_value():
    return float(r.random())


def time_value():
    values = list(map(int, fake.time().split(":")))
    return time(values[0], values[1], values[2])


def text():
    return fake.text()


def latitude():
    return float(fake.latitude())


def longitude():
    return float(fake.longitude())


def bytes_value():
    byte_ch = base64.b64encode(bytes(str(eval("fake.binary")), 'utf-8'))
    return byte_ch.decode('utf-8')


def date_time_():
    return fake.date_time()


def boolean_data():
    return r.choice([True, False])


def point_data():
    fake_location = fake.location_on_land()
    return str(Point([float(fake_location[1]), float(fake_location[0])]))


def mobile():
    return fake.phone_number()


def find_faker_func(col_name):
    for elem in dir(fake):
        if elem in col_name:
            return elem
    raise cannotBeEvaluated(col_name)


def fake_data(elem):
    return None if elem is None else str(eval("fake." + elem + "()"))
