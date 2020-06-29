# -*- coding: utf-8 -*-
"""
Resamples a low resolution band to match other bands and saves to geotiff

@author: Kalkberg
"""

import os
import glob
import rasterio
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

resolution = '10m'
directory = 'S2A_MSIL2A_20200520T105031_N0214_R051_T31UDP_20200520T134332.SAFE'
outfile = 'test2.tiff'


# Find files
os.chdir(directory)
B02file = glob.glob('**/*B02*', recursive=True)
B02file = [B02file[i] for i in range(len(B02file)) if resolution in B02file[i]]
B03file = glob.glob('**/*B03*', recursive=True)
B03file = [B03file[i] for i in range(len(B03file)) if resolution in B03file[i]]
B04file = glob.glob('**/*B04*', recursive=True)
B04file = [B04file[i] for i in range(len(B04file)) if resolution in B04file[i]]
B08file = glob.glob('**/*B08*', recursive=True)
B08file = [B08file[i] for i in range(len(B08file)) if resolution in B08file[i]]
B11file = glob.glob('**/*B11*', recursive=True)
B11file = [B11file[i] for i in range(len(B11file)) if '20m' in B11file[i]]
os.chdir('../')

# import bands
B02 = rasterio.open(directory+'/'+B02file[0], driver='JP2OpenJPEG') # blue
B03 = rasterio.open(directory+'/'+B03file[0], driver='JP2OpenJPEG') # green
B04 = rasterio.open(directory+'/'+B04file[0], driver='JP2OpenJPEG') # red
B08 = rasterio.open(directory+'/'+B08file[0], driver='JP2OpenJPEG') # nir
B11 = rasterio.open(directory+'/'+B11file[0], driver='JP2OpenJPEG') # SWIR

# resample band

B11reproj = np.zeros(np.shape(B02.read(1)), np.uint16)

reproject (B11.read(1), destination=B11reproj, 
                       src_transform = B11.transform, src_crs = B11.crs,
                        dst_transform = B02.transform, dst_crs = B02.crs, 
                        resampling=Resampling.nearest)


# Create geotiff
geotiff = rasterio.open(outfile,'w',driver='Gtiff',
                          width=B04.width, height=B04.height,
                          count=5,
                          crs=B04.crs,
                          transform=B04.transform,
                          dtype=B04.dtypes[0]
                          )

blue = B02.read(1)
green = B03.read(1)
red = B04.read(1)
swir = B11reproj
nir = B08.read(1)

geotiff.write(swir,5) #nir
geotiff.write(nir,4) #nir
geotiff.write(blue,3) #blue
geotiff.write(green,2) #green
geotiff.write(red,1) #red
geotiff.close()

# src = rasterio.open(outfile, count=5)
# plot.show(src)