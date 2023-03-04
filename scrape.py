#!/bin/env python

import sys
import os.path
import time

from argparse import ArgumentParser
import pandas as pd
from bikeimport import (
    instantiate_importer
    )

def parse(cmdline):
    parser = ArgumentParser(
        description='''
        This program scrapes bike geometry tables from websites and
        'standardizes' the data across manufacturers.

        The expected input is a comma-separated-values (CSV) file with the
        columns 'mfg', 'model', 'year', 'category', 'url'.
        - mfg : Manufacturer {'stevens', 'giant', 'canyon'}
        - model : (string model name)
        - category : advertised use ('race', 'endurance', 'gravel', 'cyclocross')
        - year: model year
        ''')

    parser.add_argument("-d", "--dest", dest="database",
                        help="write/append to <FILE>", metavar="<FILE>")

    parser.add_argument("-s", "--source", dest="source",
                        help="data source file (csv file) with urls",
                        required=True)

    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="verbose output", action="store_true")
    return parser.parse_args(cmdline)


def main():
    a = parse(sys.argv[1:])
    if a.database and os.path.exists(a.database):
        db = pd.read_csv(a.database, header=0, index_col=[0, 1, 2, 3])
    else:
        db = pd.DataFrame()

    to_scrape = pd.read_csv(a.source, header=0)
    records = to_scrape.to_dict(orient='records')
    total = len(to_scrape.index)
    i=1
    for record in records:
        print(
            f"{i}/{total}\t{record['mfg']} {record['model']} {record['year']}",
            end='')

        importer = instantiate_importer(record['mfg'])
        df = importer.scrape(record['url'])
        df = importer.standardize_data(df)
        df = importer.append_meta_info(df,
            model=record['model'],
            category=record['category'],
            year=record['year'])
        db = pd.concat([db,df])

        time.sleep(1) # Sleep so the scraper will not be banned
        i=i+1
        print(" "*100+ "\r", end='')

    if a.database:
        db.to_csv(a.database, mode='w+')
    else:
        print(db)

if __name__ == '__main__':
    main()
