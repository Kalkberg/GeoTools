# -*- coding: utf-8 -*-
"""
Code to plot Sentinel 2 data

@author: Kalkberg
"""


import os
import glob
import rasterio
from rasterio import plot
import matplotlib.pyplot as plt
import numpy as np
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

resolution = '10m'
directory = 'S2A_MSIL2A_20200520T105031_N0214_R051_T31UDP_20200520T134332.SAFE'

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
os.chdir('../')

# import bands
B02 = rasterio.open(directory+'/'+B02file[0], driver='JP2OpenJPEG') # blue
B03 = rasterio.open(directory+'/'+B03file[0], driver='JP2OpenJPEG') # green
B04 = rasterio.open(directory+'/'+B04file[0], driver='JP2OpenJPEG') # red
B08 = rasterio.open(directory+'/'+B08file[0], driver='JP2OpenJPEG') # nir


#multiple band representation
# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
# plot.show(B02, ax=ax1, cmap='Blues')
# plot.show(B03, ax=ax2, cmap='Greens')
# plot.show(B04, ax=ax3, cmap='Reds')
# fig.tight_layout()

# export true color image
# rgb = np.stack((B04,B03,B02))
# plot.show(B02)

trueColor = rasterio.open('SentinelTrueColor2.tiff','w',driver='Gtiff',
                          width=B04.width, height=B04.height,
                          count=4,
                          crs=B04.crs,
                          transform=B04.transform,
                          dtype=B04.dtypes[0]
                          )
# blue = (255*B02.read(1)/B02.read(1).max()).astype('uint16')
# green = (255*B03.read(1)/B03.read(1).max()).astype('uint16')
# red = (255*B04.read(1)/B04.read(1).max()).astype('uint16')

blue = B02.read(1)
green = B03.read(1)
red = B04.read(1)
nir = B08.read(1)

trueColor.write(nir,4) #nir
trueColor.write(blue,3) #blue
trueColor.write(green,2) #green
trueColor.write(red,1) #red
trueColor.close()

src = rasterio.open(r"SentinelTrueColor2.tiff", count=3)
plot.show(src)

# fig, ax = plt.subplots(figsize=(24, 24))
# arr_st, meta = es.stack([B02file[0],B03file[0],B04file[0]])
# ep.plot_rgb(arr_st, rgb=(0, 1, 2), ax=ax, title='rgb')
# plt.show()
# fig.savefig('test.png', dpi=300)
