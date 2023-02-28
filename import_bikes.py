#!/bin/env python

import sys
import os.path
import pandas as pd
from bikeimport import (
    available_importer_names,
    instantiate_importer
    )
from argparse import ArgumentParser

def parse(cmdline):
    parser = ArgumentParser(
        description='''
        All manufacturers give a set of dimensions on their bike models and
        sizes. But the naming and formatting of the given dimensions
        differ. This program imports and reformats data for comparison.

        This program expects a table (CSV, Excel or any other format pandas can
        read) as input. The 'MfgDimNames' represents the manufacturer
        specific name of the dimensions. This column will be mapped to
        'standardized' names to be able to compare models across
        manufacturers. Not all manufacturers give the all data, hence only a
        representative subset of columns can be mapped. The data for these
        dimensions will be converted to numeric format.
        ''')
    parser.add_argument("-d", "--dest", dest="database",
                        help="write/append to <FILE>", metavar="<FILE>",
                        required=True)

    parser.add_argument("-s", "--source", dest="source",
                        help="data source file/URL")

    parser.add_argument("-m", "--mfg", dest="mfg",
                        choices=available_importer_names(),
                        help="name of manufacturer")
    parser.add_argument("-M", "--model", dest="model",
                        help="name of model")
    parser.add_argument("-y", "--year", dest="year",
                        help="product year",
                        type=int)

    parser.add_argument("-S", "--source-dir", dest="src-dir",
                        help="read all files from directory <DIR>",
                        metavar="<DIR>")

    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="verbose output", action="store_true")
    return parser.parse_args(cmdline)


def main():
    a = parse(sys.argv[1:])
    importer = instantiate_importer(a.mfg, a.model, a.year, verbose=a.verbose)
    print(f"using {importer}")

    importer.import_data(a.source)
    data = importer.get_data()

    if os.path.exists(a.database):
        db = pd.read_csv(a.database, header=0, index_col=[0, 1, 2, 3])
        db_new = pd.concat([db, data])
    else:
        db_new = data
    db_new.to_csv(a.database, mode='w+')

if __name__ == '__main__':
    main()
