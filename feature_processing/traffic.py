# %%
import pandas as pd 
import geopandas as gpd 
import numpy as np
from shapely import wkt 
from shapely.geometry import Point, Polygon, MultiPolygon

import matplotlib.pyplot as plt

from tqdm import tqdm 
from glob import glob 

import os
import sys 

# %%
PROJ_CRS = 'EPSG:2263'
# increasing the distance acts as a smoothing kernal, as more points get to 'count' the traffic from an image
MAX_DISTANCE=150
FOV =  180 # Field of view in degrees
DEBUG_SAMPLE=False
LOCAL_PATH='/share/ju/urban-fingerprinting/output/default/df'

# %%
# load nyc ntas 
nyc_ntas = pd.read_csv("data/ntas_nyc.csv")
nyc_ntas = gpd.GeoDataFrame(nyc_ntas, geometry=nyc_ntas['the_geom'].apply(wkt.loads), crs='EPSG:4326').to_crs(PROJ_CRS)

# %%
nyc_ntas.NTAName.values

# %%
DoCs = ["2023-08-11", "2023-08-12", "2023-08-13", "2023-08-14", "2023-08-17", "2023-08-18", "2023-08-20", "2023-08-21", "2023-08-22", "2023-08-23", "2023-08-24", "2023-08-28", "2023-08-29", "2023-08-30", "2023-08-31"]
traffic = [] 
for day in DoCs: 
    print(f"Processing {day}")
    day_data = pd.read_csv(f"{LOCAL_PATH}/{day}/detections.csv", engine='pyarrow', index_col=0)[['0','1','2']].fillna(0)
    day_md = pd.read_csv(f"{LOCAL_PATH}/{day}/md.csv", engine='pyarrow', index_col=0)
    traffic.append(day_md.merge(day_data, left_on='frame_id', right_index=True))
    
traffic = pd.concat(traffic)

# print summary statistics of traffic 
print(traffic.describe())



# %%
# take a random sample 
if DEBUG_SAMPLE:
    traffic = traffic.sample(100000).reset_index(drop=True)

# %%
traffic = gpd.GeoDataFrame(traffic, geometry=gpd.points_from_xy(traffic['gps_info.longitude'], traffic['gps_info.latitude']), crs='EPSG:4326').to_crs(PROJ_CRS)

# %%
traffic['camera_heading'].describe()  

# %%
# load nyc sidewalk graph 
nyc_sidewalks = pd.read_csv("data/sidewalks_nyc_segmentized.csv", engine='pyarrow')
nyc_sidewalks = gpd.GeoDataFrame(nyc_sidewalks, geometry=nyc_sidewalks['geometry'].apply(wkt.loads), crs='EPSG:2263')

# %%
nyc_sidewalks.SHAPE_Area = nyc_sidewalks.SHAPE_Area.astype(float)
nyc_sidewalks.SHAPE_Leng = nyc_sidewalks.SHAPE_Leng.astype(float)

# %%
traffic['direction'].value_counts()

# %%


# %%
# map direction column (NORTH_WEST, etc.) to a degree value 0-360 in new column 
dir_mapping = {
    'NORTH': 0,
    'NORTH_EAST': 45,
    'EAST': 90,
    'SOUTH_EAST': 135,
    'SOUTH': 180,
    'SOUTH_WEST': 225,
    'WEST': 270,
    'NORTH_WEST': 315
}
traffic['snapped_heading'] = traffic['direction'].map(dir_mapping)
traffic['snapped_heading'].describe()

# %%
# drop na rows on snapped_heading 
traffic = traffic.dropna(subset=['snapped_heading'])

# %%
# if original geometry column exists, swap it in and drop it 
if 'original_geometry' in traffic.columns:
    traffic['geometry'] = traffic['original_geometry']
    traffic = traffic.drop(columns=['original_geometry'])

def create_semicircle(point, heading, distance):
    # Convert the heading to radians
    heading_rad = np.deg2rad(heading)

    # Generate points for the semicircle
    num_points = 10  # Number of points to approximate the semicircle
    angles = np.linspace(heading_rad - np.pi / 2, heading_rad + np.pi / 2, num_points)
    
    semicircle_points = [point]
    for angle in angles:
        semicircle_points.append(Point(point.x + distance * np.cos(angle),
                                       point.y + distance * np.sin(angle)))
    semicircle_points.append(point)  # Close the semicircle

    # Create the semicircle polygon
    semicircle = Polygon(semicircle_points)

    return semicircle


# Ensure both GeoDataFrames are in the same CRS
if traffic.crs != nyc_sidewalks.crs:
    nyc_sidewalks = nyc_sidewalks.to_crs(traffic.crs)

# Store the original geometry
traffic['original_geometry'] = traffic['geometry']

# Create semicircle geometries
traffic['geometry'] = traffic.apply(lambda row: create_semicircle(row['geometry'], row['camera_heading'], MAX_DISTANCE), axis=1)



# %%

# Perform a spatial join to find all points in nyc_sidewalks within the cone
traffic = gpd.sjoin(traffic, nyc_sidewalks, how='inner', predicate='intersects')

# Restore the original geometry
traffic['geometry'] = traffic['original_geometry']

# Drop the original_geometry column if no longer needed
traffic = traffic.drop(columns=['original_geometry'])

# Print the number of joined points
print(len(traffic))

# %%
# get average traffic per sidewalk
# traffic is in 0, 1, 2 columns 
avg_traffic_by_sidewalk = traffic.groupby('point_index')[['0','1','2']].mean()
avg_traffic_by_sidewalk = nyc_sidewalks.merge(avg_traffic_by_sidewalk, left_on='point_index', right_index=True, how='left')

# %%



all_point_indexes = pd.DataFrame({'point_index': nyc_sidewalks['point_index'].unique()})


# how many points are missing crowdedness data
zero_crowdedness_count = (avg_traffic_by_sidewalk['0'].isna()).sum()
total_points = avg_traffic_by_sidewalk.shape[0]
zero_crowdedness_percentage = zero_crowdedness_count / total_points * 100

print(f"Rows with 0 crowdedness data: {zero_crowdedness_count} points, {zero_crowdedness_percentage:.2f}% of all points")

# %%
# write average traffic to disk 
avg_traffic_by_sidewalk.to_csv(f"data/avg_traffic_by_sidewalk_august.csv")

# %%


