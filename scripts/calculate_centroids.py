import geopandas, json
import pandas as pd
from shapely.geometry import Polygon
from geojson import Feature, Point, FeatureCollection


filename = "../shpfiles/SA2_2016_AUST.shp"
s = geopandas.read_file(filename)
sadata = s[~s.geometry.isna()]
sadata.sindex

filename = "../shpfiles/SA3_2016_AUST.shp"
sa3= geopandas.read_file(filename)
sa3data = sa3[~sa3.geometry.isna()]
sa3data.sindex


def createGeoJson(data, type):
    fcollection = []
    if type == 2:
        key = "SA2_NAME16"
    elif type == 3:
        key = "SA3_NAME16"
    else:
        return
    for index, row in data.iterrows():
        try:
            #print(row['SA2_NAME16'], row['geometry'].centroid)
            ctr = row['geometry'].centroid
            name = row[key]
            point = Point((ctr.x, ctr.y))
            props = {"area":name}

            feature = Feature(geometry=point, properties=props)
            fcollection.append(feature)
        except AttributeError:
            continue
    collection = FeatureCollection(fcollection)
    frame = geopandas.GeoDataFrame.from_features(collection['features'], crs=sa3data.crs)
    return frame.to_json()

sa2c = createGeoJson(sadata, 2)
sa3c = createGeoJson(sa3data, 3)

with open("../front-end/public/js/sa2.geojson", "w") as f:
    f.write(sa2c)


with open("../front-end/public/js/sa3.geojson", "w") as f:
    f.write(sa3c)

print("your centroids are done!")


'''
# process sa2data centroids
sa2data = []
sa2d = {}
for index, row in s.iterrows():
    try:
        #print(row['SA2_NAME16'], row['geometry'].centroid)
        c = row['geometry'].centroid
        d = {"name": row['SA2_NAME16'],
            "lat": c.y, "long": c.x}
        sa2data.append(d)
    except AttributeError:
        continue

sa2d["data"] = sa2data


with open("../front-end/public/js/sa2.json", "w") as f:
    j = json.dumps(sa2d)
    f.write(j)






# process sa3data centroids
filename = "../shpfiles/SA3_2016_AUST.shp"
s = geopandas.read_file(filename)
sadata = s[~s.geometry.isna()]
sadata.sindex

sa3data = []
sa3d = {}

for index, row in s.iterrows():
    try:
        #print(row['SA2_NAME16'], row['geometry'].centroid)
        c = row['geometry'].centroid
        d = {"name": row['SA3_NAME16'],
            "lat": c.y, "long": c.x}
        sa3data.append(d)
    except AttributeError:
        continue
sa3d["data"] = sa3data

with open("../front-end/public/js/sa3.json", "w") as f:
    f.write(json.dumps(sa3d))

print("your centroids are done!")
'''
