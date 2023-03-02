import pandas as pd
import requests

from bs4 import BeautifulSoup

from .dataimporter import DataImporter
from .globals import get_header

class CubeImporter(DataImporter):
    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'cube'
    """
    Scrape an reformat bike geometries from www.cube.eu
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self.MFG_NAME, **kwargs)
        #: Stevens specific information map to 'standardized' properties
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
        # manufacturer descriptions no longer needed
        df.drop(columns=[1], inplace=True)
        df = df.T       #  frame sizes in columns, we want row
        df.columns = df.iloc[0]
        df = df.rename(columns=self.col_map)
        df.set_index(self.MFG_FRAME_KEY, inplace=True)
        # discard all other columns
        df = df[self.col_map.values()]
        # Delete lines that make no sense
        df.drop(index=self.MFG_FRAME_KEY, inplace=True)

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
        r=requests.get(url, headers=get_header())
        soup = BeautifulSoup(r.content, 'html5lib') 
        geometrytable = soup.find('table', attrs={'id': 'e-geometry-integration-table'})
        col_head = [self.MFG_FRAME_KEY,'Desc']

        head = geometrytable.find('thead')
        for td in head.findAll('td', attrs={'class': 'geometry-table-field'}):
            col_head.append(td.text.strip())

        df = pd.DataFrame(data=col_head).T

        body = geometrytable.find('tbody')
        for row in body.findAll('tr'):
            prop = []
            # description is a <th>
            desc = row.find('th', attrs={'class' : 'e-geometry-table-row'})
            prop.append(desc.attrs['data-id'])
            prop.append(desc.text.strip())
            for td in row.findAll('td', attrs={'class' : 'geometry-table-field'}):
                prop.append(td.text.strip())
            df = pd.concat([df, pd.DataFrame(prop).T])
        return df