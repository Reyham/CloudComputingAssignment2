'''
    This file contains helper methods to map coordinates and geometries to SA2
    (statistical neighbourhoods defined by the Australia Bureau of Statistics)
    The digitial statistical boundaries of SA2 are given in shp files for each state
'''

import geopandas, json
import pandas as pd
from shapely.geometry import Polygon


class SHPProcessor():
    # load shape/geometry data for SA2/SA3 neighbourhood, depending on filename
    def __init__(self, type):
        filename = ""
        if type == "SA2":
            filename = "shpfiles/SA2_2016_AUST.shp"
        elif type == "SA3":
            filename =  "shpfiles/SA3_2016_AUST.shp"

        self.sadata = geopandas.read_file(filename)

    '''
        match a list of coordinate pairs to the ID of an SA2/SA3 neighbourhood
        Input: A dict containing a list of coordinates and other attributes
        Output: A JSON object containing coordinates and their matching SA2
    '''
    def match_coordinates(self, json_data):
        df = pd.DataFrame(json_data)

        gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
        gdf.crs = self.sadata.crs

        s = self.sadata
        filter_nan_sadata = s[~s.geometry.isna()]
        #print(s1)
        #print(gdf)
        matched_coordinates = geopandas.sjoin(gdf, filter_nan_sadata, how="inner", op="within")
        matched_coordinates.drop('geometry',axis=1).to_csv(r'sample.csv')

        return matched_coordinates.to_json()


    '''
        match a single bounding box to the best fitting SA2s/SA3s
        Input: A dictionary containing a list of bounding box for specific tweets
        We generate a polygon from the bounding box, and match the shape to the SA2/SA3 that contains it

        Output: A JSON object containing polygons (bounding box) and their matching SA2/SA3
    '''
    def match_bounding_box(self, json_data):
        # make polygons from the pairs of coords:
        lats = longs = []
        for corner in json_data['coordinates'][0]:
            lats.append(corner[0])
            longs.append(corner[1])

        polygon = Polygon(zip(longs, lats))
        gdf = geopandas.GeoDataFrame(index=[0], crs=self.sadata.crs, geometry=[polygon])

        s = self.sadata
        filter_nan_sadata = s[~s.geometry.isna()]

        matched_boxes = geopandas.sjoin(gdf, filter_nan_sadata, how="inner", op="contains")
