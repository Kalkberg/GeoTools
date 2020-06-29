# -*- coding: utf-8 -*-
"""
Get some NetCDF images (Sentinel-5), clip to AOI, average out and plot.

@author: Kalkberg
"""

## Work in progress

## Problem - pixel locations don't align between images


# need environment variable if basemap not properly built
import os
os.environ['PROJ_LIB'] = '/opt/conda/pkgs/proj4-5.2.0-he1b5a44_1003/share/proj'
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import glob
import xarray as xr

# Change directory
os.chdir(os.getcwd()+'\\Data\\NO2\\')

# Find all netCDF4 images in directory
imgFiles = glob.glob('*201904*') # search for files in specific time range
imgFiles = [i for i in imgFiles if '.nc' in i[-4:len(i)]] # only accept zips

# projection and AOI parameters
lon_min = 120
lon_max = 135
lat_min = 30
lat_max = 45
lon_0 = 127.5 # central lon of proj
lat_0 = 38 # central lat of proj

# Import image and process data

for file in imgFiles:
    # Display status
    number = imgFiles.index(file)
    print('Computing image '+ str(number) + '/' + str(len(imgFiles)))    

    # file path
    path = file
    
    # read in data
    img = netCDF4.Dataset(path, mode='r')
    variables = img.groups['PRODUCT']
    
    # get lats, lons, and NO2 values
    lats = variables['latitude'][0,:,:]
    lons = variables['longitude'][0,:,:]
    values = variables['nitrogendioxide_tropospheric_column'][0,:,:]
    # values = variables['sulfurdioxide_total_vertical_column'][0,:,:].data
    
    # close image
    img.close()
    
    # Clip to AOI
    # lats_inds = np.where((lats > lat_min) & (lats < lat_max) & (lons > lon_min) & (lons < lon_max)) # Indices of lats in AOI
    # lons_inds = np.where((lons > lon_min) & (lons < lon_max)) # Indices of lons in AOI

    aoi = np.where((lats > lat_min) & (lats < lat_max) & (lons > lon_min) & (lons < lon_max))    
    
    # create numpy array of values on first loop
    if number == 0:
        valuesAOI = values[aoi].data
        
    # otherwise append to existing array   
    valuesAOI = np.vstack((valuesAOI,values[aoi].data))  

# Average values
valuesAOI = np.median(valuesAOI, axis=0)
                          
# Start mapping

# # Set up projection
# plt.figure(figsize=(8.5,11)) # make a large plot

# # Set up map projection
# m = Basemap(width=1000000,height=1250000,
#             resolution='h',projection='stere',\
#             lat_ts=15,lat_0=lat_0,lon_0=lon_0)

# # m = Basemap(llcrnrlon=lon_min,llcrnrlat=lat_min,urcrnrlon=lon_max,urcrnrlat=lat_max,
# #             resolution='i',projection='tmerc',lon_0=lon_0,lat_0=lat_0)

# # Project pixel coordinates into map coordinates
# xi, yi = m(lons, lats)

# # Plot image data
# cs = m.pcolor(xi,yi,np.squeeze(valuesAOI))

# # Add Grid Lines
# m.drawparallels(np.arange(lat_min, lat_max, 5.), labels=[1,0,0,0], fontsize=10)
# m.drawmeridians(np.arange(lon_min, lon_max, 5.), labels=[0,0,0,1], fontsize=10)

# # Add Coastlines, and Country Boundaries
# m.drawcoastlines()
# m.drawcountries()

# # Add Colorbar
# cbar = m.colorbar(cs, location='right', pad="10%")
# cbar.set_label('Tropospheric NO2')
# cbar.set_label('Total Vertical Column NO2')
# plt.clim(-.0001,.0005) # NO2 range
# # plt.clim(-.005,.005) # SO2 range

# # Add Title
# plt.title(date)

# # Show and save plot
# # plt.show()
# plt.savefig(date+'_NO2_QA.png', bbox_inches='tight', dpi = 300)
# plt.clf()
# plt.close()
    

