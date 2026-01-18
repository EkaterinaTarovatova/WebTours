import csv
from itertools import cycle

def open_csv_file(filepath, mode="r"):
    with open(filepath, mode, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return cycle(list(reader))

def open_random_csv_file(filepath, mode="r"):
    with open(filepath, mode, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)