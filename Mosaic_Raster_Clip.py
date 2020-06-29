# -*- coding: utf-8 -*-
"""
Mosaic all files in folder, clip to area, then export.

Modified from:
    
https://automating-gis-processes.github.io/CSC18/lessons/L6/raster-mosaic.html

@author: Kalkberg
"""


import os
# import glob
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs

# Setup variables
dir_name = 'D:\\SIFT\\testbed'
out_name = 'M_Clip.img'
share_env = "C:\ProgramData\Anaconda3\envs\Img36\Library\share" 

# Troubleshoot to make pyproj work
os.environ["PROJ_LIB"] = share_env

# WGS84 coordinates of target area
minx, miny = 90.87, 38.24
maxx, maxy = 90.15, 38.259
bbox = box(minx, miny, maxx, maxy)

# Insert bounding box into a GeoDataFrame
geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))

def getFeatures(gdf):
    # """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


# Change to directory with files
os.chdir(dir_name) 

# List files to be mosaiced
files = os.listdir(dir_name)

# List of open rasterio files
raster_obj = []

for file in files:
    src = rasterio.open(file)
    raster_obj.append(src)

# Mosaic raster files
mosaic, mosaic_trans = merge(raster_obj)

# Parse EPSG code
epsg_code = int(src.crs.data['init'][5:])

# Reproject into the same coordinate system as raster data
geo = geo.to_crs(epsg=epsg_code)

# Get geometry coordinates for rasterio
coords = getFeatures(geo)

# Clip mosaic to target area
clip_img, clip_transform = mask(raster=mosaic, shapes=coords, crop=True)

# Copy the metadata
clip_meta = src.meta.copy()

# Update metadata with new dimensions
clip_meta.update({"driver": "GTiff", 
                  "height": clip_img.shape[1],
                  "width": clip_img.shape[2],
                  "transform": clip_transform,
                  "crs": pycrs.parser.from_epsg_code(epsg_code).to_proj4()})

# Write mosaic to disc
out_fp = dir_name + '\\' + out_name

with rasterio.open(out_fp, "w", **clip_meta) as dest:
    dest.write(clip_img)