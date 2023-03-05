"""Scrape and reformat bike geometry data of rose bikes."""
import pandas as pd
from .dataimporter import DataImporter


class RoseImporter(DataImporter):
    """Website scraper and geometry table parser for rose bikes (2023)."""

    #: Compatible Manufacturer names for this importer, fixed
    MFG_NAME = 'rose'

    def __init__(self, *args, **kwargs):
        """Create an importer for rose-bikes."""
        super().__init__(self.MFG_NAME, **kwargs)
        #: Map mfg property names to 'standardized' properties
        self.col_map = {
            "a": self.std_column_map["SeatTube"],
            "b": self.std_column_map["TopTube_hz"],
            "d": self.std_column_map["HeadTubeAngle"],
            "e": self.std_column_map["SeatTubeAngle"],
            "h": self.std_column_map["Wheelbase"],
            "g": self.std_column_map["Chainstay"],
            "f": self.std_column_map["BBdrop"],
            "m": self.std_column_map["StandOverHeight"],
            "j": self.std_column_map["Reach"],
            "k": self.std_column_map["Stack"],
            "p": self.std_column_map['ForkRake']
        }

    def standardize_data(self, df):
        """Map raw data to well-known properties."""
        df = df.T  # Transpose to make properties columns and sizes the index
        # Column 1 is Roses descriptions for letters
        df.iloc[0] = df.iloc[0].apply(str.lower)
        df.iloc[0, 0] = self.MFG_FRAME_KEY
        # Line 0 is the column header
        df.columns = df.iloc[0]

        df = df.rename(columns=self.col_map)
        df.drop(0, inplace=True)  # MfgDimNames
        df.set_index(self.MFG_FRAME_KEY, inplace=True)

        # discard all other columns
        df = df[self.std_cols()]

        df = self.make_std_cols_numeric(df)
        # Return dataframe without index
        return df.reset_index()

    def scrape(self, url):
        """Retrieve and parse data from the website given by url."""
        def is_line_value(tag):
            return (tag.has_attr('class') and
                    'bike-detail-geo-table__list-item'
                    in tag.attrs['class'] and
                    'bike-detail-geo-table__size-key'
                    not in tag.attrs['class'])

        soup = self.get_soup(url)

        # Rose builds the table from div-tags and unordered lists....
        # and invented their own tag
        geometrytable = soup.find('bike-detail-geo-table')

        col_head = []
        header = geometrytable.find(
            'div', attrs={'class': 'bike-detail-geo-table__sticky-wrapper'})
        frame_sizes = header.findAll('li',
                                     attrs={'class': [
                                         'bike-detail-geo-table__list-item',
                                         'list-item--top bike-detail-geo-table__size-key']})
        for frame_size in frame_sizes:
            col_head.append(frame_size.text.strip())

        df = pd.DataFrame(data=col_head).T

        body = geometrytable.find(
            'div', attrs={'class': 'bike-detail-geo-table__wrapper'})
        # every row is an unordered list, the first list item contains a legend
        for line in body.findAll('ul', attrs={'class': 'bike-detail-geo-table__list'}):
            values_for_frame_size = []
            legend = line.find(
                'span', attrs={'class': 'bike-detail-geo-table__size-legend'})
            values_for_frame_size.append(legend.text.strip())

            for value_for_frame_size in line.findAll(is_line_value):
                values_for_frame_size.append(value_for_frame_size.text.strip())

            df = pd.concat([df, pd.DataFrame(values_for_frame_size).T])

        return df
