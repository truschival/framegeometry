"""Scrape and reformat bike geometry data of giant bikes."""
import pandas as pd
from .dataimporter import DataImporter


class GiantImporter(DataImporter):
    """Website scraper and geometry table parser for giant bikes (2023)."""

    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'giant'

    def __init__(self, *args, **kwargs):
        """Create an importer for giant-bikes."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Map mfg property names to 'standardized' properties
        self.col_map = {
            "A": "SeatTube",
            "C": "TopTube_hz",
            "E": "HeadTubeAngle",
            "B": "SeatTubeAngle",
            "H": "Wheelbase",
            "I": "Chainstay",
            "J": "BBdrop",
            "M": "StandOverHeight",
            "K": "Reach",
            "L": "Stack",
            "F": 'ForkRake'
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        # Column 1 should contain MFG_FRAME_KEY='MfgDimNames'
        # Column 2 is Giants descriptions for letters
        df = df.T  # Transpose to make properties columns and sizes the index
        # Line 0 is the column header
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df = df.drop([0, 1])  # MfgDimNames and row with Giant descriptions
        df.set_index(self.MFG_FRAME_KEY, inplace=True)
        # discard all other columns
        df = df[self.std_cols()]
        # sometimes the csv/google spreadsheet exports empty cols/rows
        df.dropna(how='all', inplace=True)

        df = self.make_std_cols_numeric(df)
        # Return dataframe without index
        return df.reset_index()

    def scrape(self, url):
        """Retrieve and parse data from the website given by url."""
        def is_not_customary(tag):
            return not (tag.has_attr('class') and
                        'value-inch' in tag.attrs['class'])

        soup = self.get_soup(url)
        geometrytable = soup.find('div', attrs={'id': 'geometrytable'})
        col_head = [self.MFG_FRAME_KEY, 'Desc']

        for row in geometrytable.findAll('tr', attrs={'class': 'heading'}):
            for td in row.findAll('th', attrs={'name': 'framesize'}):
                col_head.append(td.text)
        df = pd.DataFrame(data=col_head).T

        for row in geometrytable.findAll('tr', attrs={'class': 'property'}):
            prop = []
            for td in row.findAll('td'):
                if td.attrs['class'] == ['code']:
                    prop.append(td.string)
                if td.attrs['class'] == ['name']:
                    prop.append(td.contents[0])
                if td.attrs['class'] == ['value']:
                    # Table data contains spans with either no class (text),
                    # ['value' 'value-mm'] ['value' 'value-inch'] or
                    # ['degrees'] read all except inches
                    x = td.find(is_not_customary)
                    prop.append(x.text)

            df = pd.concat([df, pd.DataFrame(prop).T])
        return df
