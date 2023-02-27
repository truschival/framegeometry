#!/bin/env python

import sys
import os.path
import pandas as pd
from bikeimport import create_data_importer
from argparse import ArgumentParser

def parse(cmdline):
    parser = ArgumentParser(
        description='''

        All manufacturers give a set of dimensions on their bike models and
        sizes. But the naming and formatting of the given dimensions
        differ. This program imports and reformats data for comparison.

        This program expects a table (CSV, Excel or any other format pandas can
        read) as input. The 'mfg_dim_names' represents the manufacturer
        specific name of the dimensions. This column will be mapped to
        'standardized' names to be able to compare models across
        manufacturers. Not all manufacturers give the all data, hence only a
        representative subset of columns can be mapped. The data for these
        dimensions will be converted to numeric format.

        Currently this program can map bike dimension tables for Stevens, Giant
        and Specialized.

        ''')
    parser.add_argument("-f", "--file", dest="filename",
                        help="write/append to FILE", metavar="FILE",
                        required=True)
    parser.add_argument("-m", "--mfg", dest="mfg",
                        choices=['stevens', 'giant', 'canyon'],
                        help="name of manufacturer",
                        required=True)
    parser.add_argument("-M", "--model", dest="model",
                        help="name of model",
                        required=True)
    parser.add_argument("-y", "--year", dest="year",
                        help="product year",
                        required=True,
                        type=int)
    parser.add_argument("-s", "--source", dest="source",
                        help="data_source",
                        required=True)
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="verbose output", action="store_true")

    return parser.parse_args(cmdline)


def capitalize_word(word):
    return word[0].upper()+word[1:].lower()

def main():
    a = parse(sys.argv[1:])
    importer = create_data_importer(capitalize_word(a.mfg),
                                    capitalize_word(a.model),
                                    a.year, verbose=a.verbose)
    print(f"using {importer}")

    importer.import_data(a.source)
    data = importer.get_data()

    if os.path.exists(a.filename):
        db = pd.read_csv(a.filename, header=0, index_col=[0, 1, 2, 3])
        db_new = pd.concat([db, data])
    else:
        db_new = data
    db_new.to_csv(a.filename, mode='w+')

if __name__ == '__main__':
    main()
