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
import pycrs

# Setup variables
dir_name = 'D:\\SIFT\'
out_name = 'Mosaic.tif'

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
mosaic_img, mosaic_transform = merge(raster_obj)

# Copy the metadata
mosaic_meta = src.meta.copy()

# Parse EPSG code
epsg_code = int(src.crs.data['init'][5:])

# Update metadata with new dimensions
mosaic_meta.update({"driver": "GTiff", 
                  "height": mosaic_img.shape[1],
                  "width": mosaic_img.shape[2],
                  "transform": mosaic_transform,
                  "crs": pycrs.parser.from_epsg_code(epsg_code).to_proj4()})

# Write mosaic to disc
out_fp = dir_name + '\\' + out_name

with rasterio.open(out_fp, "w", **mosaic_meta) as dest:
    dest.write(mosaic_img)