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


def process_cancel_request_body(flight_ids, flight_nums):
    random_index = random.randrange(len(flight_nums))
    flight_ids = 'flightID=' + '&flightID='.join(flight_ids)
    flight_nums ='.cgifields=' + '&cgifields='.join(flight_nums)
    static = 'removeFlights.x=68&removeFlights.y=9'
    delete_num = f'{flight_nums[random_index]}=on'
    return f'{flight_ids}&{delete_num}&{static}&{flight_nums}'
