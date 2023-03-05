"""Scrape and reformat bike geometry data of bmc bikes."""
import pandas as pd
from .dataimporter import DataImporter


class BmcImporter(DataImporter):
    """Website scraper and geometry table parser for BMC bikes (2023).

    https://www.bmc-switzerland.com
    """

    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'bmc'

    def __init__(self, *args, **kwargs):
        """Create an importer for bmc-bikes."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Map mfg property names to 'standardized' properties
        self.col_map = {
            "seat tube mm (st)" : self.std_column_map["SeatTube"],
            "top tube mm (tt)"  : self.std_column_map["TopTube_hz"],
            "head angle (ha)"   : self.std_column_map["HeadTubeAngle"],
            "seat tube angle (sa)": self.std_column_map["SeatTubeAngle"],
            "wheelbase mm (wb)": self.std_column_map["Wheelbase"],
            "rear center mm (rc)": self.std_column_map["Chainstay"],
            "bb drop mm (drop)": self.std_column_map["BBdrop"],
            "standover height mm": self.std_column_map["StandOverHeight"],
            "reach mm (reach)": self.std_column_map["Reach"],
            "stack mm": self.std_column_map["Stack"],
            "fork rake mm (fr)": self.std_column_map['ForkRake']
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        # Column 1 should contain MFG_FRAME_KEY='MfgDimNames'
        df = df.T  # Transpose to make properties columns and sizes the index
        # Line 0 is the column header, BMC is not consistent with case...
        df.iloc[0]=df.iloc[0].apply(str.lower)
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df = df.drop([0])  # MfgDimNames
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

        soup = self.get_soup(url)
        geometry_table = soup.find('table', attrs={'class': 'geometry'})
        col_head = [self.MFG_FRAME_KEY]

        # Table Head with frame sizes
        table_head  = geometry_table.find('thead')
        for frame_size in table_head.findAll('th', attrs={'class':['geometry__cell--value']}):
            col_head.append(frame_size.text.strip())

        df = pd.DataFrame(data=col_head).T

        # Table row entries properties
        table_body = geometry_table.find('tbody')
        for row in table_body.findAll('tr', attrs={'class': 'geometry__row'}):
            prop = []
            label = row.find('td',attrs={'class':['geometry__cell--label']})
            prop.append(label.text.strip())
            for td in row.findAll('td', attrs={'class': ['geometry__cell--value']}):
                prop.append(td.text.strip())
            df = pd.concat([df, pd.DataFrame(prop).T])

        return df
