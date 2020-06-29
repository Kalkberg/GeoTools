# -*- coding: utf-8 -*-
"""
Code to detect trucks from Sentinel-2 data. Modified from:
    https://github.com/hfisser/Truck_Detection_Sentinel2_COVID19

Modifications do pre-processing for data directly downloaded from Sentinel API, 
rather than Sentinel Hub

@author: Kalkberg
"""

import os
import glob
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

directory = 'dir
outfile = 'test'

# Find files
os.chdir(directory)
B02file = glob.glob('**/*B02*', recursive=True)
B02file = [B02file[i] for i in range(len(B02file)) if '10m' in B02file[i]]
B03file = glob.glob('**/*B03*', recursive=True)
B03file = [B03file[i] for i in range(len(B03file)) if '10m'in B03file[i]]
B04file = glob.glob('**/*B04*', recursive=True)
B04file = [B04file[i] for i in range(len(B04file)) if '10m' in B04file[i]]
B08file = glob.glob('**/*B08*', recursive=True)
B08file = [B08file[i] for i in range(len(B08file)) if '10m' in B08file[i]]
B11file = glob.glob('**/*B11*', recursive=True)
B11file = [B11file[i] for i in range(len(B11file)) if '20m' in B11file[i]]
SCLfile = glob.glob('**/*SCL*', recursive=True)
SCLfile = [B11file[i] for i in range(len(B11file)) if '20m' in SCLfile[i]]
os.chdir('../')

# import bands
B02 = rasterio.open(directory+'/'+B02file[0], driver='JP2OpenJPEG') # blue
B03 = rasterio.open(directory+'/'+B03file[0], driver='JP2OpenJPEG') # green
B04 = rasterio.open(directory+'/'+B04file[0], driver='JP2OpenJPEG') # red
B08 = rasterio.open(directory+'/'+B08file[0], driver='JP2OpenJPEG') # nir
B11 = rasterio.open(directory+'/'+B11file[0], driver='JP2OpenJPEG') # SWIR
SCL = rasterio.open(directory+'/'+SCLfile[0], driver='JP2OpenJPEG') # Land class

# Reproject band 11 and SCL to 10 m to match image data
B11reproj = np.zeros(np.shape(B02.read(1)), np.uint16)
reproject (B11.read(1), destination=B11reproj, 
                       src_transform = B11.transform, src_crs = B11.crs,
                        dst_transform = B02.transform, dst_crs = B02.crs, 
                        resampling=Resampling.nearest)

SCLreproj = np.zeros(np.shape(B02.read(1)), np.uint16)
reproject (B11.read(1), destination=SCLreproj, 
                       src_transform = SCL.transform, src_crs = SCL.crs,
                        dst_transform = B02.transform, dst_crs = B02.crs, 
                        resampling=Resampling.nearest)

# Create masks from SCL to improve band ratio masking
defective = SCLreproj != 1
darkarea = SCLreproj != 2
cloudshadow = SCLreproj != 3
veg = SCLreproj != 4
water = SCLreproj != 6
cloudsmed = SCLreproj != 8
cloudshigh = SCLreproj != 9
cloudscirrus = SCLreproj != 10
SCLmask = defective * darkarea * cloudshadow * veg * water * cloudsmed * cloudshigh * cloudscirrus

# Get raster values for each band and normalize
B02data = B02.read(1)/np.max(B02.read(1))
B03data = B03.read(1)/np.max(B03.read(1))
B04data = B04.read(1)/np.max(B04.read(1))
B08data = B08.read(1)/np.max(B08.read(1))
B11data = B11reproj/np.max(B11reproj)

# Specific Parameters for masking
min_rgb = 0.04 
max_red = 0.15
max_green = 0.15 # avoid industry, greenhouses and other high reflection surfaces
max_blue = 0.4 #  same as above
max_ndvi = 0.7 # avoid vegetation, but quite high to account for mixed pixels
max_ndwi = 0.001 # avoid water
max_ndsi = 0.0001 # avoid snow
min_b11 = 0.05
max_b11 = 0.55
min_green_ratio = 0.05
min_red_ratio = 0.1

# Compute a roads mask using band ratios and thresholds
# Note: this generates a lot of false positives, esp. in ag lands, but those shouldn't have vehicles most of the time
ndvi_mask = ((B08data - B04data) / (B08data + B04data)) < max_ndvi
ndwi_mask = ((B02data - B11data) / (B02data + B11data)) < max_ndwi
ndsi_mask = ((B03data - B11data) / (B03data + B11data)) < max_ndsi
low_rgb_mask = (B02data > min_rgb) * (B03data > min_rgb) * (B04data > min_rgb)
high_rgb_mask = (B02data < max_blue) * (B03data < max_green) * (B04data < max_red)
b11_mask = ((B11data - B03data) / (B11data + B03data)) < max_b11
b11_mask_abs = (B11data > min_b11) * (B11data < max_b11)
roads_mask = ndvi_mask * ndwi_mask * ndsi_mask * low_rgb_mask * high_rgb_mask * b11_mask * b11_mask_abs * SCLmask

# Extract vehicles from RGB ratios
bg_ratio = (B02data - B03data) / (B02data + B03data) 
br_ratio = (B02data - B04data) / (B02data + B04data)
bg_low = (bg_ratio * roads_mask) > min_green_ratio 
br_low = (br_ratio * roads_mask) > min_red_ratio
vehicles = bg_low * br_low

# Create geotiff of all data
geotiff = rasterio.open(outfile+'.tiff','w',driver='Gtiff',
                          width=B04.width, height=B04.height,
                          count=5,
                          crs=B04.crs,
                          transform=B04.transform,
                          dtype=B04.dtypes[0]
                          )


geotiff.write(B11reproj,5) #swir
geotiff.write(B08.read(1),4) #nir
geotiff.write(B04.read(1),3) #blue
geotiff.write(B03.read(1),2) #green
geotiff.write(B02.read(1),1) #red
geotiff.close()

# Create geotiff of vehicles and roads
geotiff = rasterio.open(outfile+'_masks.tiff','w',driver='Gtiff',
                          width=B04.width, height=B04.height,
                          count=2,
                          crs=B04.crs,
                          transform=B04.transform,
                          dtype=B04.dtypes[0]
                          )

vehicledata = np.ones(np.shape(B02.read(1)), np.uint16)*vehicles*255
roadsdata = np.ones(np.shape(B02.read(1)), np.uint16)*roads_mask*255

geotiff.write(roadsdata,2) # roads
geotiff.write(vehicledata,1) # vehicels
geotiff.close()