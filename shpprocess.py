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
        if type == "SA2":
            filename = "shpfiles/SA2_2016_AUST.shp"
        elif type == "SA3":
            filename =  "shpfiles/SA3_2016_AUST.shp"

        s = geopandas.read_file(filename)
        self.sadata = s[~s.geometry.isna()]
        self.sadata.sindex # make index for faster performance, if one does not exist


    '''
        match a list of coordinate pairs to the ID of an SA2/SA3 neighbourhood
        Input: A dict containing a list of coordinates and/or other attributes
        E.g. {"Latitude": -35.332175, "Longitude": 149.0910366}

        Output: A JSON object containing coordinates and their matching SA2
    '''
    def match_coordinates(self, json_data):
        try:
            df = pd.DataFrame(json_data)
        except ValueError:
            df = pd.DataFrame(json_data, index=[0])

        gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
        gdf.crs = self.sadata.crs

        #print(s1)
        #print(gdf)
        matched_coordinates = geopandas.sjoin(gdf, self.sadata, how="inner", op="within")

        return matched_coordinates.to_json()


    '''
        match a single bounding box to the best fitting SA2s/SA3s
        Input: A dictionary containing a list of bounding box for specific tweets
        We generate a polygon from the bounding box, and match the shape to the SA2/SA3 that contains it


        Input: {"coordinates": [[-35.2773337, 149.1290814],
                                    [-35.2767018, 149.1308614],
                                    [-35.2767020, 149.1308634],
                                    [-35.2767011, 149.1308654]]}


        Output: A JSON object containing polygons (bounding box) and their matching SA2/SA3
    '''
    def match_bounding_box(self, json_data):

        # make polygons from the pairs of coords:
        lats = []
        longs = []
        for corner in json_data['coordinates']:
            lats.append(corner[1])
            longs.append(corner[0])

        polygon = Polygon(zip(longs, lats))
        gdf = geopandas.GeoDataFrame(index=[0], crs=self.sadata.crs, geometry=[polygon])


        matched_boxes = geopandas.sjoin(self.sadata, gdf, how="inner", op="within")
        matched_boxes.drop('geometry',axis=1)
        return matched_boxes.to_json()

    '''
        Hacky code to alter JSON fields to make location references consistent across
        all data
    '''

    def filter_json(self, matched_json):
        try:
            j = json.loads(matched_json)['features'][0]['properties']
        except IndexError:
            return None

        keep_keys = ["SA3_CODE16", "SA3_NAME16", "SA2_MAIN16",
                    "SA2_NAME16", "STE_NAME16", "GCC_CODE16", "GCC_NAME16"]
        j_ = {k: v for k, v in j.items() if k in keep_keys}
        # alter key names so they are consistent with others
        for key in keep_keys:
            if j_[key]:
                new_key = key.lower()
                j_[new_key] = j_.pop(key)
        if j_['sa2_main16']:
            j_['sa2_code16'] = j_.pop('sa2_main16')
        return j_
