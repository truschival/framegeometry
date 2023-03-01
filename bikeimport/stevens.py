import pandas as pd
from .dataimporter import DataImporter

class StevensImporter(DataImporter):
    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'stevens'
    #: Models for this importer (if the website is good models should work)
    MODELS = ['prestige', 'xenith', 'arcalis', 'vapor', 'super-prestige']
    #: model years for which this importer works
    YEARS = range(2019, 2024)

    """
    Cleanup data from stevens bikes table as of 2023

    Expects a table with a column-header 'MfgDimNames' on the column with
    symbols for frame sizes e.g. (A1, A2...) on the website this is the second
    column.
    Stevens uses frame sizes as columns and properties as rows. So the first
    line of the csv should look like:
    'Frame height (cm),MfgDimNames,48,51,54,56,58,61,Measuring mode'

    """
    def __init__(self, model, year, *args, **kwargs):
        super().__init__(self.MFG_NAME, model, year, **kwargs)
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
        # Column 2 is mfg_dim_names and some values are not mapped,
        # replace values with manufacturer descriptions from column 1
        df[1].fillna(df[0], inplace=True)
        # manufacturer descriptions no longer needed
        df.drop(columns=[0], inplace=True)
        df = df.T       # stevens has frame sizes in columns, we want row
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df.set_index(self.MFG_FRAME_KEY, drop=False, inplace=True)

        # Delete lines that make no sense
        # Frame height is leftover row from import, containing human readable
        # descriptions (column1)
        df.drop(index=self.MFG_FRAME_KEY, inplace=True)

        # drop useless row, Measuring mode is explanation for table
        df.drop('Measuring mode', inplace=True, errors='ignore')
        df.drop(columns="Assembled spacers", inplace=True, errors='ignore')
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
