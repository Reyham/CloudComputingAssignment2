import geopandas, json
import pandas as pd
from shapely.geometry import Polygon


filename = "../shpfiles/SA2_2016_AUST.shp"
s = geopandas.read_file(filename)
sadata = s[~s.geometry.isna()]
sadata.sindex


# process sa2data centroids
sa2data = []
for index, row in s.iterrows():
    try:
        #print(row['SA2_NAME16'], row['geometry'].centroid)
        c = row['geometry'].centroid
        d = {"name": row['SA2_NAME16'],
            "coordinates" : {"lat": c.y, "long": c.x}}
        sa2data.append(d)
    except AttributeError:
        continue

with open("../front-end/public/js/sa2centroids.js", "w") as f:
    f.write("var data = " + str(sa2data))


# process sa3data centroids
filename = "../shpfiles/SA3_2016_AUST.shp"
s = geopandas.read_file(filename)
sadata = s[~s.geometry.isna()]
sadata.sindex

sa3data = []

for index, row in s.iterrows():
    try:
        #print(row['SA2_NAME16'], row['geometry'].centroid)
        c = row['geometry'].centroid
        d = {"name": row['SA3_NAME16'],
            "coordinates" : {"lat": c.y, "long": c.x}}
        sa3data.append(d)
    except AttributeError:
        continue

with open("../front-end/public/js/sa3centroids.js", "w") as f:
    f.write("var data = " + str(sa3data))

print("your centroids are done!")
