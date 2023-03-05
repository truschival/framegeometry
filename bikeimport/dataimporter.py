"""Common superclass for all manufacturer specific importers."""
from abc import (ABC, abstractmethod,)
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

from .globals import (
    get_bike_categories,
    normalize,
    get_header,
)


class DataImporter(ABC):
    """Common superclass for all manufacturer specific importers."""

    #: column header for manufacturer
    MFG_KEY = "mfg"
    #: column header for bike model
    MODEL_KEY = "model"
    #: column header for year
    YEAR_KEY = "year"
    #: Category of bike ('endurance', 'race', 'gravel', 'cyclocross')
    CAT_KEY = "category"
    #: column header for manufacturer specific frame size (54,56 or S, M, L)
    MFG_FRAME_KEY = 'mfg_dim_names'
    #: column for manufacturer description
    MFG_DESC_KEY = 'desc'

    def __init__(self, mfg, *args, **kwargs):
        """Create base class and setup common attributes.

        Parameters:
        -----------
        mfg (str): manufacturer name
        """
        self.mfg = mfg
        self.verbose = False
        self.df = pd.DataFrame()

        self.std_column_map = {
            'BBdrop'            : 'bb_drop',
            'HeadTubeAngle'     : 'head_tube_angle',
            'Chainstay'         : 'chain_stay',
            'Reach'             : 'reach',
            'SeatTube'          : 'seat_tube',
            'SeatTubeAngle'     : 'seat_tube_angle',
            'Stack'             : 'stack',
            'StandOverHeight'   : 'stand_over_height',
            'TopTube_hz'        : 'top_tube',
            'Wheelbase'         : 'wheel_base',
            'ForkRake'          : 'fork_rake'
        }

        if 'verbose' in kwargs:
            self.verbose = kwargs['verbose']

    def make_std_cols_numeric(self, df):
        """
        Prune dataframe of common errors.

        Prune empty columns, make sure strings do not contain comma or
        degree symbols.

        Parameters:
        -----------
        df (pandas.DataFrame) : to prune

        Return:
        -------
        pandas.DataFrame

        """
        # cleanup common string issues
        df = df.applymap(
            lambda x: str(x.replace(',', '.')) if isinstance(x, str) else x)
        df = df.applymap(
            lambda x: str(x.replace('°', '')) if isinstance(x, str) else x)

        # make sure columns are numeric
        df.loc[:, self.std_cols()] = df[self.std_cols()].apply(pd.to_numeric)

        # Return dataframe without index
        return df

    @abstractmethod
    def standardize_data(self, df):
        """
        Cleanup data to match standardized format and columns.

        Manufacturer specific method has to be implemented in derived classes.

        Parameters:
        -----------
        df (pandas.DataFrame): input data

        Returns:
        -------
        pandas.DataFrame - clean, standardized data

        """

    @abstractmethod
    def scrape(self, url):
        """Scrape data from website and return model as DataFrame.

        Parameters:
        -----------
        url (str): url of the model website containing geometry data

        Returns:
        --------
        pandas.DataFrame: non-standardized dataframe
        """

    def get_soup(self, url):
        """Create a BeautifulSoup parser for given URL.

        Parameters:
        -----------
        url (str): url of bike model website containing geometry data

        Returns:
        --------
        BeautifulSoup parser object
        """
        r = requests.get(url, headers=get_header(), timeout=5)
        soup = BeautifulSoup(r.content, 'html5lib')
        return soup

    def std_cols(self):
        """
        Return 'standardized' property names that can be used for comparison.

        Returns:
        --------
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
        -----------
        full (bool): non-standard fields are included

        Returns:
        --------
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
