import csv
import pandas as pd
from datetime import datetime


def wirte_csv(file, data, mode='a'):
    with open(file, mode) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)