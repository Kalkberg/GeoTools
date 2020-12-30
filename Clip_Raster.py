# -*- coding: utf-8 -*-
"""
Clips a raster to a geometry using rasterio

@author: Kalkberg
"""

import os
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import pyproj
from shapely.ops import transform

# Setup variables
file_name = r'D:\Image_similarity\clip_test\Afg_Pair1_1.tif'
out_name = file_name[:-4]+'_clip'+file_name[-4:] #NOTE: assumes 3 char extension!
directory, image = os.path.split(file_name)
os.chdir(directory) 

# WGS84 coordinates of target area
minx, miny = 69.237, 34.58
maxx, maxy = 69.25, 34.588
bbox = box(minx, miny, maxx, maxy)

# Open file
img = rasterio.open(file_name)

# Parse EPSG code of image
epsg_code = img.crs.data['init']

# Reproject into the same coordinate system as raster data
wgs84 = pyproj.CRS('epsg:4326')
img_proj = pyproj.CRS(img.crs.data['init'])
project = pyproj.Transformer.from_crs(wgs84,img_proj).transform
bbox_proj = transform(project, bbox)

# Clip mosaic to target area
clip_img, clip_transform = mask(img, [bbox_proj], crop=True)

# Copy the metadata
out_meta = img.meta.copy()

# Update metadata with new dimensions
profile = img.profile
out_meta = img.meta.copy()
out_meta.update({"driver": "GTiff",
                  "height": clip_img.shape[1],
                  "width": clip_img.shape[2],
                  "transform": clip_transform,
                  "photometric": profile["photometric"],
                  "compress": profile["compress"],
                  "dtype": profile["dtype"]
                  })

# Write mosaic to disc
with rasterio.open(out_name, "w", **out_meta) as dest:
    dest.write(clip_img)

# Close file
img.close()