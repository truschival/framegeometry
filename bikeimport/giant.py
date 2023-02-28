import pandas as pd
from .dataimporter import DataImporter

class GiantImporter(DataImporter):
    """
    Import Giant geometry data
    """
    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'giant'
    #: Models for this importer (if the website is good models should work)
    MODELS = ['tcx-advanced-pro-1', 'tcr-advanced-disc-1+']

    def __init__(self, model, year, *args, **kwargs):
        super().__init__(self.MFG_NAME, model, year, **kwargs)
        #: Stevens specific information map to 'standardized' properties
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
            "L": "Stack"
        }

    def import_data(self, source):
        df = pd.read_csv(source, header=None)
        # Column 1 should contain MFG_FRAME_KEY='MfgDimNames'
        # Column 2 is Giants descriptions for letters
        df = df.T  # Transpose to make properties columns and sizes the index
        # Line 0 is the column header
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df = df.drop([0, 1])  # MfgDimNames and row with Giant descriptions
        df.set_index(self.MFG_FRAME_KEY, drop=False, inplace=True)

        # sometimes the csv/google spreadsheet exports empty cols/rows
        df.dropna(how='all', inplace=True)
        # cleanup common string issues
        df = df.applymap(
            lambda x: str(x.replace(',', '.')) if type(x) == str else x)
        df = df.applymap(
            lambda x: str(x.replace('°', '')) if type(x) == str else x)

        # make sure standardized columns are numeric
        df.loc[:, self.std_cols()] = df[self.std_cols()].apply(pd.to_numeric)

        self.df = df
        return df
