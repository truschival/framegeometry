# Compare bike frame geometries across manufacturers

The code in this repo allows to import and compare bike geometry data from bike
manufacturers as they publish it on their websites.

## Import

All manufacturers give different information and name the dimensions slightly
differently. The import part aims to read and format this data into a consistent
set with common names across manufacturers.The
input format is anything readable by
[``Pandas.read_csv()``](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html).

There is still some manual work involved, but I try to keep it minimal. 

My current approach is:

-  to copy/paste data from the websites e.g. into a google spreadsheet or Csv
   file
-  remove all formatting
-  add a column header 'MfgDimNames' to the line/column containing manufacturer
   dimension names/frame sizes
-  run the importer to append it to existing database (out.csv)

	```
   python import_bikes.py -f out.csv -m stevens -M prestige -y 2019 \
   -s data/stevens_prestige_2019.csv
   ```

## Comparison

TBD
