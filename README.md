# Compare bike frame geometries across manufacturers

The code in this repo allows to import and compare bike geometry data from bike
manufacturers as they publish it on their websites.

## Import

All manufacturers give different information and name the dimensions slightly
differently. The import part scrapes data from the bike websites and formats 
it into a consistent set with common names across manufacturers.

Some manual work is still involved, currently you have to give a csv file
with manufacturer name, model name, year, category and URL to scrape.
Take a look at [test-urls.csv](./test_urls.csv).

To scrape and import data and append it to the database run:

   ```
   % ./scrape.py -s all-urls.csv -d database.csv
   ```

## Comparison

Well, this is a nice tool but you want to head to 
[Geometry Geeks](https://geometrygeeks.bike/) 
for bike comparison. 
They have a much nicer interface and a vastly larger database. But I am here 
for learning... 
