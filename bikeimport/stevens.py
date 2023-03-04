"""Scrape and reformat bike geometry data of stevens bikes."""
import pandas as pd
from .dataimporter import DataImporter


class StevensImporter(DataImporter):
    """Website scraper and geometry table parser for stevens bikes (2023)."""

    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'stevens'

    def __init__(self, *args, **kwargs):
        """Create a stevens data importer."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Stevens specific information map to 'standardized' properties
        self.col_map = {
            "A1": "SeatTube",
            "C": "TopTube_hz",
            "D": "HeadTubeAngle",
            "E": "SeatTubeAngle",
            "F": "Wheelbase",
            "G": "Chainstay",
            "I": "BBdrop",
            "O": "StandOverHeight",
            "R": "Reach",
            "S": "Stack",
            "L": 'ForkRake'
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        # Column 2 contains the codes, some values are not mapped,
        # replace values with manufacturer descriptions from column 1
        df[1].fillna(df[0], inplace=True)
        # manufacturer descriptions no longer needed
        df.drop(columns=[0], inplace=True)
        df = df.T       # stevens has frame sizes in columns, we want row
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df.set_index(self.MFG_FRAME_KEY, inplace=True)
        # discard all other columns
        df = df[self.std_cols()]
        # sometimes the csv/google spreadsheet exports empty cols/rows
        df.dropna(how='all', inplace=True)

        # Delete lines that make no sense
        # Frame height is leftover row from import, containing human readable
        # descriptions (column1)
        df.drop(index=self.MFG_FRAME_KEY, inplace=True)
        # drop useless row, Measuring mode is explanation for table
        df.drop(index='Measuring Mode', inplace=True, errors='raise')

        # cleanup common string issues
        df = df.applymap(
            lambda x: str(x.replace(',', '.')) if type(x) == str else x)
        df = df.applymap(
            lambda x: str(x.replace('°', '')) if type(x) == str else x)

        # make sure columns are numeric
        df = df.apply(pd.to_numeric)

        # Return dataframe without index
        return df.reset_index()

    def scrape(self, url):
        """Retrieve and parse data from the website given by url."""
        soup = self.get_soup(url)
        geometrytable = soup.find('table', attrs={'id': 'geometrie'})
        col_head = [self.MFG_DESC_KEY, self.MFG_FRAME_KEY]

        head = geometrytable.find('thead')
        row = head.find('tr')
        for td in row.findAll('th', attrs={'class': 'value'}):
            col_head.append(td.text.strip())

        col_head.append('Measuring Mode')
        df = pd.DataFrame(data=col_head).T

        body = geometrytable.find('tbody')
        for row in body.findAll('tr'):
            prop = []
            # description is a <th>
            desc = row.find('th')
            prop.append(desc.text.strip())

            for td in row.findAll('td'):
                prop.append(td.text.strip())
            df = pd.concat([df, pd.DataFrame(prop).T])
        return df
