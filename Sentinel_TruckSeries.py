# -*- coding: utf-8 -*-
"""
Code to detect trucks using Sentinel 2 data.

Modified from:
    https://github.com/hfisser/Truck_Detection_Sentinel2_COVID19/blob/master/Detect_trucks_sentinel2_COVID19.ipynb

@author: Kalkberg
"""

from xcube_sh.cube import open_cube
from xcube_sh.config import CubeConfig
from xcube.core.maskset import MaskSet

from osgeo import gdal, gdal_array, ogr

import os
import json
import numpy as np
import xarray as xr
import shapely.geometry
import IPython.display

# General Parameters

dataset = "S2L2A"
spatial_res = 0.00009 # 10m
band_names = ["B02", "B03", "B04", "B08", "B11", "SCL"]
time_period = "1D"

fig = [16, 10] # for plotting

# Specific Parameters

min_rgb = 0.04
max_red = 0.15
max_green = 0.15
max_blue = 0.4
max_ndvi = 0.7 # quite high to account for mixed pixels
max_ndwi = 0.001
max_ndsi = 0.0001
min_b11 = 0.05
max_b11 = 0.55
min_green_ratio = 0.05
min_red_ratio = 0.1

# Area of Interest

aoi_ruhr = 6.7, 51.27, 7.58, 51.6
place = "ruhr"
# dates where chosen according to available cloud-free acquisitions
dates_ruhr = ["2018-03-19", "2018-05-08", "2018-07-02", "2018-07-07", "2018-07-27", "2018-08-06", "2018-09-30", "2018-10-10",
              "2019-02-27", "2019-04-18", "2019-05-13", "2019-06-27", "2019-08-26", "2019-09-20", "2019-12-04", 
              "2020-02-07", "2020-03-23", "2020-03-28", "2020-04-17", "2020-04-22", "2020-05-07"]

# dates = dates_ruhr

dates = ["2020-01-01","2020-05-10"]

aoi = aoi_ruhr

IPython.display.GeoJSON(shapely.geometry.box(*aoi).__geo_interface__)

## Do Calculation for one time stamp

pixels = []

# Get Sentinel-2 L2A data

cube_con = CubeConfig(dataset_name = dataset,
                      band_names = band_names,
                      tile_size = [512, 512],
                      geometry = aoi,
                      spatial_res = spatial_res,
                      time_range = [dates[0], dates[1]],
                      time_period = time_period)
cube = open_cube(cube_con)

# Mask out clouds
scl = MaskSet(cube.SCL)
cube = cube.where((scl.clouds_high_probability +
                              scl.clouds_medium_probability +
                              scl.clouds_low_probability_or_unclassified + 
                              scl.cirrus) == 0)

dates = cube.time.values

for date in dates:

    # Display status
    number = np.where(dates==date)[0][0]
    print('Computing image '+ str(number) + '/' + str(len(dates)))   

    #date = dates[-1] # do exmaple calculation for last timestamp of dates
    # date = dates[0]
    #timestamp1 = cube.sel(time = cube.time[-1])
    timestamp1 = cube.sel(time = date)
    
    # figure out how many NaN cells there are
    timestamp1.B02.load()
    nans = np.sum(np.isnan(timestamp1.B02.values))
    size = np.shape(timestamp1.B02)[0]*np.shape(timestamp1.B02)[1]
    
    # Only analyze images with >90% coverage
    if nans/size < .1:
    
        # timestamp1.B02.plot.imshow(vmin = 0, vmax = 0.2, figsize = [16, 8])
        
        # Compute a roads mask using band ratios and thresholds
        
        B02 = timestamp1.B02
        B03 = timestamp1.B03
        B04 = timestamp1.B04
        B08 = timestamp1.B08
        B11 = timestamp1.B11
          
        # Compute a roads mask using band ratios and thresholds
        ndvi_mask = ((B08 - B04) / (B08 + B04)) < max_ndvi
        ndwi_mask = ((B02 - B11) / (B02 + B11)) < max_ndwi
        ndsi_mask = ((B03 - B11) / (B03 + B11)) < max_ndsi
        low_rgb_mask = (B02 > min_rgb) * (B03 > min_rgb) * (B04 > min_rgb)
        high_rgb_mask = (B02 < max_blue) * (B03 < max_green) * (B04 < max_red)
        b11_mask = ((B11 - B03) / (B11 + B03)) < max_b11
        b11_mask_abs = (B11 > min_b11) * (B11 < max_b11)
        roads_mask = ndvi_mask * ndwi_mask * ndsi_mask * low_rgb_mask * high_rgb_mask * b11_mask * b11_mask_abs
        
        # roads_mask.plot.imshow(vmin = 0, vmax = 1, cmap = "binary", figsize = [16, 8])
        
        # Extract vehicles from RGB ratios
        
        bg_ratio = (B02 - B03) / (B02 + B03) 
        br_ratio = (B02 - B04) / (B02 + B04)
        
        bg_low = (bg_ratio * roads_mask) > min_green_ratio 
        br_low = (br_ratio * roads_mask) > min_red_ratio
        vehicles = bg_low * br_low
        
        # vehicles.plot.imshow(vmin = 0, vmax = 1, cmap = "binary", figsize = [16, 8])
        
        # Count number of vehicle pixels
        # vehiclesload = vehicles.load()
        vehicles.load()
        pixels += [date, np.sum(vehicles.values)]
        print(np.sum(vehicles.values))
    
    

