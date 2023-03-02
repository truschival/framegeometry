import pandas as pd
from abc import (ABC, abstractmethod,)
import datetime

from .globals import (
    get_bike_categories,
    normalize,
)

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
    #: Category of bike ('endurance', 'race', 'gravel', 'cyclocross')
    CAT_KEY = "Category"
    #: column header for manufacturer specific frame size (54,56 or S, M, L)
    MFG_FRAME_KEY = 'MfgDimNames'

    def __init__(self, mfg, *args, **kwargs):
        """
        Base constructor to setup common attributes.

            Parameters:
                    mfg (str): manufacturer name
        """

        self.mfg = mfg
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
    def standardize_data(self, df):
        """
        Cleanup data to match standardized format and columns.

        Manufacturer specific method has to be implemented in derived classes.

            Parameters:
                    df (pandas.DataFrame): input data

            Returns:
                    pandas.DataFrame - clean, standardized data

        """
        pass

    @abstractmethod
    def scrape(self, url):
        """Scrape data from website and return model as DataFrame

        Args:
            url (str): url of the model website containing geometry data 

        Returns:
            pandas.DataFrame: non-standardized dataframe 
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


    def append_meta_info(self, df, model=None, year=None, category=None):
        """
        Return the imported, cleaned dataframe for this importer.

            Parameters:
                    full (bool): non-standard fields are included

            Returns:
                    Pandas DataFrame
        """
        if not year:
            year = int(datetime.date.today().year)
        df.insert(0, self.YEAR_KEY, year)

        df.insert(0, self.MODEL_KEY, normalize(model))
        
        if category and normalize(category) in get_bike_categories():
            df.insert(0, self.CAT_KEY, normalize(category))

        df.insert(0, self.MFG_KEY, self.mfg)
        
        df.set_index([self.MFG_KEY,
                        self.MODEL_KEY,
                        self.YEAR_KEY,
                        self.MFG_FRAME_KEY],
                       drop=True,
                       inplace=True)
        return df