import csv, random
from itertools import cycle
from datetime import datetime, timedelta
from urllib.parse import quote_plus


def open_csv_file(filepath, mode="r"):
    with open(filepath, mode, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return cycle(list(reader))


def open_random_csv_file(filepath, mode="r"):
    with open(filepath, mode, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def generate_flight_dates():
    dates_list = {}
    dates_list["depart_date"] = quote_plus(
        (datetime.today() + timedelta(days=random.randint(2, 10))).strftime("%m/%d/%Y"))
    dates_list["return_date"] = quote_plus(
        (datetime.today() + timedelta(days=random.randint(12, 30))).strftime("%m/%d/%Y"))
    return dates_list
