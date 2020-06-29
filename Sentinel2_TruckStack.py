# -*- coding: utf-8 -*-
"""
Code to detect trucks from Sentinel-2 data. Modified from:
    https://github.com/hfisser/Truck_Detection_Sentinel2_COVID19

Modifications do pre-processing for data directly downloaded from Sentinel API, 
rather than Sentinel Hub and export geotiffs of all data and masks.

@author: Kalkberg
"""

import os
import glob
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

directory = os.getcwd() + '\\TRN'
outfile = 'TRN.csv'
fileid = 'clip' # string in file name that distinguishes it from others in directory
extension = '.tif' # extension of image files

# Find files
os.chdir(directory)
files = glob.glob('*'+extension)
B02files = [i for i in files if ('B02' in i) & (fileid in i)]
B03files = [i for i in files if ('B03' in i) & (fileid in i)]
B04files = [i for i in files if ('B04' in i) & (fileid in i)]
B08files = [i for i in files if ('B08' in i) & (fileid in i)]
B11files = [i for i in files if ('B11' in i) & (fileid in i)]
SCLfiles = [i for i in files if ('SCL' in i) & (fileid in i)]

# Create empty output list
trucks = [['imagename','dates','roadpixels','vehiclepixels', 'datapixels', 'SCLPixels']]

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

# read first file and figure out dimensions
B02 = rasterio.open(B02files[0], driver='Gtiff')
dtype = B02.read(1).dtype


# create invariant road mask
for i in range(len(B02files)):
    
    # show status
    print('Computing Invariant Roads '+ str(i+1) + '/' + str(len(B02files)))
    
    # import bands
    B02 = rasterio.open(B02files[i], driver='Gtiff') # blue
    B03 = rasterio.open(B03files[i], driver='Gtiff') # green
    B04 = rasterio.open(B04files[i], driver='Gtiff') # red
    B08 = rasterio.open(B08files[i], driver='Gtiff') # nir
    B11 = rasterio.open(B11files[i], driver='Gtiff') # SWIR

    # Reproject band 11 to 10 m to match image data
    B11reproj = np.zeros(np.shape(B02.read(1)), dtype)
    reproject (B11.read(1), destination=B11reproj, 
                           src_transform = B11.transform, src_crs = B11.crs,
                            dst_transform = B02.transform, dst_crs = B02.crs, 
                            resampling=Resampling.nearest)
    
     
    # Get raster values for each band and normalize
    B02data = B02.read(1)/np.max(B02.read(1))
    B03data = B03.read(1)/np.max(B03.read(1))
    B04data = B04.read(1)/np.max(B04.read(1))
    B08data = B08.read(1)/np.max(B08.read(1))
    B11data = B11reproj/np.max(B11reproj)
          
    # Compute a roads mask using band ratios and thresholds
    # Note: this generates a lot of false positives, esp. in ag lands, but those shouldn't have vehicles most of the time
    nodata = B02.read(1) != 0
    ndvi_mask = ((B08data - B04data) / (B08data + B04data)) < max_ndvi
    ndwi_mask = ((B02data - B11data) / (B02data + B11data)) < max_ndwi
    ndsi_mask = ((B03data - B11data) / (B03data + B11data)) < max_ndsi
    low_rgb_mask = (B02data > min_rgb) * (B03data > min_rgb) * (B04data > min_rgb)
    high_rgb_mask = (B02data < max_blue) * (B03data < max_green) * (B04data < max_red)
    b11_mask = ((B11data - B03data) / (B11data + B03data)) < max_b11
    b11_mask_abs = (B11data > min_b11) * (B11data < max_b11)
    roads_mask = ndvi_mask * ndwi_mask * ndsi_mask * low_rgb_mask * high_rgb_mask * b11_mask * b11_mask_abs
    
    # update mask on every loop    
    if i == 0:
        invariant_roads = roads_mask * 1
    else:
        invariant_roads = invariant_roads + (roads_mask * 1)

# if road is present in >75% of images, keep it
invariant_roads_mask = invariant_roads/len(B02files) > 0.75

# compute vehicles, sum, and output
for i in range(len(B02files)):
    
    # show status
    print('Computing vehicles '+ str(i+1) + '/' + str(len(B02files)))

    # Get Date and file name
    date = B02files[i][:8]
    imgname = B02files[i][:-4]

    # import bands
    B02 = rasterio.open(B02files[i], driver='Gtiff') # blue
    B03 = rasterio.open(B03files[i], driver='Gtiff') # green
    B04 = rasterio.open(B04files[i], driver='Gtiff') # red
    SCL = rasterio.open(SCLfiles[i], driver='Gtiff') # Land class
    
    # Reproject SCL to match land class
    SCLreproj = np.zeros(np.shape(B02.read(1)), dtype)
    reproject (SCL.read(1), destination=SCLreproj, 
                           src_transform = SCL.transform, src_crs = SCL.crs,
                            dst_transform = B02.transform, dst_crs = B02.crs, 
                            resampling=Resampling.nearest)

    # Create masks from SCL to improve band ratio masking
    defective = SCLreproj != 1
    darkarea = SCLreproj != 2
    cloudshadow = SCLreproj != 3
    veg = SCLreproj != 4
    water = SCLreproj != 6
    cloudslow = SCLreproj != 7
    cloudsmed = SCLreproj != 8
    cloudshigh = SCLreproj != 9
    cloudscirrus = SCLreproj != 10
    SCLmask = defective * darkarea * cloudshadow * veg * water * cloudslow * cloudsmed * cloudshigh * cloudscirrus
    
    # Extract vehicles from RGB ratios
    bg_ratio = (B02data - B03data) / (B02data + B03data) 
    br_ratio = (B02data - B04data) / (B02data + B04data)
    bg_low = (bg_ratio * invariant_roads_mask) > min_green_ratio 
    br_low = (br_ratio * invariant_roads_mask) > min_red_ratio
    vehicles = bg_low * br_low * SCLmask * nodata
    
    # Count number of pixels with data
    datapixels = np.sum(B02data > 0)
    
    # Count number of pixels masked with SCL
    SCLpixels = np.sum(SCLmask)
    
    # Count number of non-occluded road pixels
    roadpixels = np.sum(invariant_roads_mask * SCLmask)
    
    # count number of pixels with vehicles and append
    trucks += [[imgname,date,roadpixels,np.sum(vehicles), datapixels, SCLpixels]]
    
    # Create geotiff of all data
    geotiff = rasterio.open(imgname + '_allbands.tiff','w',driver='Gtiff',
                              width=B04.width, height=B04.height,
                              count=5,
                              crs=B04.crs,
                              transform=B04.transform,
                              dtype=B04.dtypes[0]
                              )
    
    
    geotiff.write(B11reproj,5) #swir
    geotiff.write(B08.read(1),4) #nir
    geotiff.write(B02.read(1),3) #blue
    geotiff.write(B03.read(1),2) #green
    geotiff.write(B04.read(1),1) #red
    geotiff.close()
    
    # Create geotiff of vehicles and roads
    geotiff = rasterio.open(imgname + '_masks.tiff','w',driver='Gtiff',
                              width=B04.width, height=B04.height,
                              count=2,
                              crs=B04.crs,
                              transform=B04.transform,
                              dtype=B04.dtypes[0]
                              )
    
    vehicledata = np.ones(np.shape(B02.read(1)), dtype)*vehicles*255
    roadsdata = np.ones(np.shape(B02.read(1)), dtype)*roads_mask*255
    
    geotiff.write(roadsdata,2) # roads
    geotiff.write(vehicledata,1) # vehicels
    geotiff.close()

np.savetxt(outfile, np.asarray(trucks), delimiter=',', fmt='%s')

