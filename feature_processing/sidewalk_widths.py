# %%
import os

import numpy as np
import pandas as pd

from shapely.geometry import LineString
from shapely.geometry import Point, MultiPoint, MultiLineString
from shapely.ops import linemerge, nearest_points

import geopandas as gpd
from geopandas import GeoDataFrame
from centerline.geometry import Centerline

from tqdm import tqdm 
from pandarallel import pandarallel
pandarallel.initialize(progress_bar=True, nb_workers=14)



# %%
crs = {'init': 'epsg:3627'} #local crs

# %% [markdown]
# ## Get Sidewalk Centerlines

# %%
df = gpd.read_file("../data/Sidewalk.geojson")
print("Loaded sidewalk data")

# %%
df = df.to_crs('EPSG:3627')


# %%
df_dissolved = gpd.GeoDataFrame(geometry=gpd.GeoSeries([geom for geom in df.unary_union.geoms]))
print("Dissolved sidewalk data")

# %%

df_exploded = gpd.GeoDataFrame(df_dissolved.geometry.explode(index_parts=False))
print("Exploded sidewalk data")


# parallelized version 
def get_centerline(row):
    try: 
        return Centerline(row['geometry'])
    except Exception as e:
        print(e)
        return None


df_exploded['centerlines'] = df_exploded.parallel_apply(lambda row: get_centerline(row), axis=1)
print("Generated centerlines")

# %% [markdown]
# ## Remove Short Line Ends

# %%

def get_linemerge(row):
    try: 
        return linemerge(row)
    except Exception as e:
        print(e)
        return None

df_exploded['centerlines'] = df_exploded['centerlines'].parallel_apply(get_linemerge)

# %%
def remove_short_lines(line):

    if not line: 
        return None
    
    if line.type == 'MultiLineString':
        
        passing_lines = []
    
        for i, linestring in enumerate(line):
            
            other_lines = MultiLineString([x for j, x in enumerate(line) if j != i])
            
            p0 = Point(linestring.coords[0])
            p1 = Point(linestring.coords[-1])
            
            is_deadend = False
            
            if p0.disjoint(other_lines): is_deadend = True
            if p1.disjoint(other_lines): is_deadend = True
            
            if not is_deadend or linestring.length > 5:                
                passing_lines.append(linestring)
            
        return MultiLineString(passing_lines)
            
    if line.type == 'LineString':
        return line

# %%
df_exploded['centerlines'] = df_exploded['centerlines'].parallel_apply(remove_short_lines)

# %% [markdown]
# ## Get Sidewalk Widths

# %%
def try_simplify(row):
    try:
        return row.simplify(1, preserve_topology=True)
    except Exception as e:
        print(e)
        return None


df_exploded['centerlines'] = df_exploded['centerlines'].parallel_apply(lambda row: try_simplify(row))

# %%
def linestring_to_segments(linestring):
    return [LineString([linestring.coords[i], linestring.coords[i+1]]) for i in range(len(linestring.coords) - 1)]

# %%
def get_segments(line):

    if not line:
        return []
    
    line_segments = []

    if line.type == 'MultiLineString':
        
        for linestring in line.geoms:
            
            line_segments.extend(linestring_to_segments(linestring))

    if line.type == 'LineString':
        
        line_segments.extend(linestring_to_segments(line))

    return line_segments

# %%
df_exploded['segments'] = df_exploded['centerlines'].parallel_apply(get_segments)

# %%
def interpolate_by_distance(linestring):
    
    distance = 1
    all_points = []
    count = round(linestring.length / distance) + 1
    
    if count == 1:
        all_points.append(linestring.interpolate(linestring.length / 2))
    
    else:
        for i in range(count):
            all_points.append(linestring.interpolate(distance * i))
    
    return all_points

def interpolate(line):
    
    if line.type == 'MultiLineString':
        
        all_points = []
        
        for linestring in line:
            all_points.extend(interpolate_by_distance(linestring))
        
        return MultiPoint(all_points)
            
    if line.type == 'LineString':
        return MultiPoint(interpolate_by_distance(line))
    
    
def polygon_to_multilinestring(polygon):

    return MultiLineString([polygon.exterior] + [line for line in polygon.interiors])
    

def get_avg_distances(row):
    
    avg_distances = []
    
    sidewalk_lines = polygon_to_multilinestring(row.geometry)
    
    for segment in row.segments:
        
        points = interpolate(segment)
        
        distances = []
        
        for point in points:
            p1, p2 = nearest_points(sidewalk_lines, point)
            distances.append(p1.distance(p2))
            
        avg_distances.append(sum(distances) / len(distances))
        
    return avg_distances

# %%
df_exploded['avg_distances'] = df_exploded.parallel_apply(lambda row: get_avg_distances(row), axis=1)

# %%
data = {'geometry': [], 'width': []}

for i, row in df_exploded.iterrows():
    
    for segment in row.segments:
        data['geometry'].append(segment)
    
    for distance in row.avg_distances:
        data['width'].append(distance * 2)
        
df_segments = pd.DataFrame(data)
df_segments = GeoDataFrame(df_segments, crs=crs, geometry='geometry')

# %%
df_exploded.to_parquet('../data/sidewalk_centerlines.parquet')
df_segments.to_parquet('../data/sidewalk_widths.parquet')


