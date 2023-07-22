"""Reformat bike geometry data of CSV files copied from Ridley website tables."""
import pandas as pd
from .dataimporter import DataImporter


class RidleyImporter(DataImporter):
    """Parse data from ridley csv file"""

    MFG_NAME = "ridley"

    def __init__(self, *args, **kwargs):
        """Create an importer for ridley-bikes."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Map mfg property names to 'standardized' properties
        self.col_map = {
            "B": self.std_column_map["SeatTube"],
            "C": self.std_column_map["TopTube_hz"],
            "F": self.std_column_map["HeadTubeAngle"],
            "E": self.std_column_map["SeatTubeAngle"],
            "I": self.std_column_map["Wheelbase"],
            "G": self.std_column_map["Chainstay"],
            "H": self.std_column_map["BBdrop"],
            "J": self.std_column_map["StandOverHeight"],
            "R": self.std_column_map["Reach"],
            "S": self.std_column_map["Stack"],
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        # Column 1 should contain MFG_FRAME_KEY='MfgDimNames'
        df = df.T  # Transpose to make properties columns and sizes the index
        df.reset_index(inplace=True)
        df.iloc[0, 0] = self.MFG_FRAME_KEY
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df = df.drop(0)  # MfgDimNames
        df.set_index(self.MFG_FRAME_KEY, inplace=True)
        # discard all other columns
        df = df[self.std_cols()]
        # sometimes the csv/google spreadsheet exports empty cols/rows
        df.dropna(how="all", inplace=True)

        df = self.make_std_cols_numeric(df)
        # Return dataframe without index
        return df.reset_index()

    def scrape(self, url):
        """Retrieve and parse data from csv_file."""
        df = pd.read_csv(url, sep="\t")
        return df
