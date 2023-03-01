import pandas as pd
from abc import (ABC, abstractmethod,)

class DataImporter(ABC):
    """
    Abstract importer super-class with common constants and methods for
    manufacturer specific importer classes.

    Individual importers can restrict their compatibility with the attributes
    MFG_NAMES (str[]), MODELS (str[]) and YEARS (int[])
    """
    #: column header for manufacturer
    MFG_KEY = "Mfg"
    #: column header for bike model
    MODEL_KEY = "Model"
    #: column header for year
    YEAR_KEY = "Year"
    #: column header for manufacturer specific frame size (54,56 or S,M,L)
    MFG_FRAME_KEY = 'MfgDimNames'

    def __init__(self, mfg, model, year, *args, **kwargs):
        """
        Base constructor to setup common attributes.

            Parameters:
                    mfg (str): manufacturer name
                    model (str): bike model name
                    year (int) : model year
        """
        self.mfg = mfg
        self.model = model
        self.year = year
        self.verbose = False
        self.df = pd.DataFrame()
        self.col_map = {
            "Bottom Bracket drop (below axis)": 'BBdrop',
            "Head Tube Angle": 'HeadTubeAngle',
            "Chain stay length": 'Chainstay',
            "Horizontal reach": 'Reach',
            "normalized length of seat tube": 'SeatTube',
            "angle of seat tube (horizontal)": 'SeatTubeAngle',
            "Stack above bottom bracket": 'Stack',
            "top tube to floor": 'StandOverHeight',
            "Top tube length (horizontal)": 'TopTube_hz',
            "Wheelbase": 'Wheelbase',
            "Fork Rake": 'ForkRake'
        }

        if 'verbose' in kwargs:
            self.verbose = kwargs['verbose']

    def __str__(self):
        """Print info on which specific importer is used."""
        return self.mfg+"_"+self.model+"_"+str(self.year)

    @abstractmethod
    def standardize_data(self, source):
        """
        Cleanup data to match standardized format and columns.

        Manufacturer specific method has to be implemented in derived classes.

            Parameters:
                    df (pandas.DataFrame): input data

            Returns:
                    pandas.DataFrame - clean, standardized data

        """
        pass

    def std_cols(self):
        """
        Return 'standardized' property names that can be used for comparison.

            Returns:
                    Array of (str)
        """
        return self.col_map.values()

    def print_mapping(self):
        """Print mapping table for manufacturer columns to standard columns."""
        for k, v in self.col_map.items():
            print(f"  {k} -> {v}")

    def get_data(self, full=False):
        """
        Return the imported, cleaned dataframe for this importer.

            Parameters:
                    full (bool): non-standard fields are included

            Returns:
                    Pandas DataFrame
        """
        data = self.df.copy()
        data.insert(0, self.MFG_KEY, self.mfg)
        data.insert(0, self.MODEL_KEY, self.model)
        data.insert(0, self.YEAR_KEY, self.year)
        data.set_index([self.MFG_KEY,
                        self.MODEL_KEY,
                        self.YEAR_KEY,
                        self.MFG_FRAME_KEY],
                       drop=True,
                       inplace=True)
        if full:
            return data
        else:
            return data[self.std_cols()]
