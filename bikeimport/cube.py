"""Scrape and reformat bike geometry data of cube bikes."""
import pandas as pd
from .dataimporter import DataImporter


class CubeImporter(DataImporter):
    """Website scraper and geometry table parser for www.cube.eu (2023)."""

    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'cube'

    def __init__(self, *args, **kwargs):
        """Create an importer for cube bike data."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Map mfg property names to 'standardized' properties
        self.col_map = {
            "A": "SeatTube",
            "B": "TopTube_hz",
            "D": "HeadTubeAngle",
            "C": "SeatTubeAngle",
            "G": "Wheelbase",
            "E": "Chainstay",
            "H": "BBdrop",
            "T 80": "StandOverHeight",
            "R": "Reach",
            "S": "Stack",
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        # manufacturer descriptions no longer needed
        df.drop(columns=[1], inplace=True)
        df = df.T  # frame sizes in columns, we want row
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df.set_index(self.MFG_FRAME_KEY, inplace=True)
        # discard all other columns
        df = df[self.col_map.values()]
        # Delete lines that make no sense
        df.drop(index=self.MFG_FRAME_KEY, inplace=True)

        df = self.make_std_cols_numeric(df)
        # Return dataframe without index
        return df.reset_index()

    def scrape(self, url):
        """Retrieve and parse data from the website given by url."""
        soup = self.get_soup(url)
        geometrytable = soup.find('table',
                                  attrs={'id': 'e-geometry-integration-table'})
        col_head = [self.MFG_FRAME_KEY, self.MFG_DESC_KEY]

        head = geometrytable.find('thead')
        for td in head.findAll('td', attrs={'class': 'geometry-table-field'}):
            col_head.append(td.text.strip())

        df = pd.DataFrame(data=col_head).T

        body = geometrytable.find('tbody')
        for row in body.findAll('tr'):
            prop = []
            # description is a <th>
            desc = row.find('th', attrs={'class': 'e-geometry-table-row'})
            prop.append(desc.attrs['data-id'])
            prop.append(desc.text.strip())
            for td in row.findAll('td',
                                  attrs={'class': 'geometry-table-field'}):
                prop.append(td.text.strip())
            df = pd.concat([df, pd.DataFrame(prop).T])
        return df
