import geopandas, json
import pandas as pd
from shapely.geometry import Polygon


filename = "../shpfiles/SA2_2016_AUST.shp"
s = geopandas.read_file(filename)
sadata = s[~s.geometry.isna()]
sadata.sindex


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
