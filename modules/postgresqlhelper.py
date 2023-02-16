"""
This module generates data for supported PostgreSQL column/data types.
It is used in conjunction with the 'postgresql' module.
For more information, see the section on PostgreSQL in README.md

"""
import random as r
import base64
import pytz
from faker import Faker
from datetime import time
from config.definitions import INT_RANGE, PG_INT_RANGE, LOCALE, TZ_INFO
from modules.data_generation_exceptions import cannotBeEvaluated

fake = Faker(locale=LOCALE)
Faker.seed()


def bigint():
    return int(r.uniform(-INT_RANGE, INT_RANGE))


def bit(digit):
    res = bin(r.getrandbits(digit))[2:].zfill(digit)
    return res


def boolean_data():
    return r.choice([True, False])


def bytea_value():
    byte_ch = base64.b64encode(bytes(str(eval("fake.binary(length=16)")), 'utf-8'))
    return byte_ch


def inet():
    return r.choice([fake.ipv4(), fake.ipv6()])


def int_value():
    return int(r.uniform(-PG_INT_RANGE, PG_INT_RANGE))


def numeric():
    return float(r.random())


def numeric_value():
    pass


def latitude():
    return float(fake.latitude())


def longitude():
    return float(fake.longitude())


def text():
    return fake.text()


def time_value():
    values = list(map(int, fake.time().split(":")))
    return time(values[0], values[1], values[2])


def timestamp():
    return fake.date_time()


def timestamp_with_zone():
    tz = pytz.timezone(TZ_INFO)
    return tz.localize(fake.date_time())


def mobile():
    return fake.phone_number()


def find_faker_func(col_name):
    for elem in dir(fake):
        if elem in col_name:
            return elem
    raise cannotBeEvaluated(col_name)


def fake_data(elem):
    return None if elem is None else str(eval("fake." + elem + "()"))
