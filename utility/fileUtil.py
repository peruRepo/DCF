import pandas as pd
import csv
from csv import DictReader

def read_csv_file():
    with open('input.csv', mode='r') as file:
        # reading the CSV file
        dict_reader = DictReader(file)
        input = list(dict_reader)
    return input


def write_csv_file(dcf):
    filename = "output.csv"
    fields = ['date', 'Ticker', 'current_price', 'avg_growth', 'avg_capex','forecasted_share_price_avg_growth',
  'eg_growth','forecasted_share_price_eg_growth']
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(dcf)
