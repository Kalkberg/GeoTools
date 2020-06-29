# -*- coding: utf-8 -*-
"""
Plot Sentinel 5P data

@author: Kalkberg
"""

## Import image and unpack data

import netCDF4
import os

# file path
path = os.getcwd() + '\\Data\\NO2\\S5P_OFFL_L2__NO2____20191106T032706_20191106T050836_10694_01_010302_20191112T054900.nc'

# read in data
img = netCDF4.Dataset(path, mode='r')
variables = img.groups['PRODUCT']

# get lats, lons, and NO2 values
lats = variables['latitude'][0,:,:]
lons = variables['longitude'][0,:,:]
values = variables['nitrogendioxide_tropospheric_column'][0,:,:]
# values = variables['sulfurdioxide_total_vertical_column'][0,:,:].data

# Get timestamp
date = variables['time_utc'][0][0][0:10]
# date = path[20:28] # use existing timestamp in file name rather than pulling from data

# Close image
img.close()

## Start mapping

# need environment variable to avoid issues with basemap
os.environ['PROJ_LIB'] = '/opt/conda/pkgs/proj4-5.2.0-he1b5a44_1003/share/proj'
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

# Set up projection
fig, ax = plt.subplots(figsize=(8.5,11)) # make a large plot

# projection parameters
lon_min = 120
lon_max = 135
lat_min = 30
lat_max = 45
lon_0 = 127.5 # central lon of proj
lat_0 = 38 # central lat of proj

# Set up map projection
m = Basemap(width=1000000,height=1250000,
            resolution='h',projection='stere',\
            lat_ts=15,lat_0=lat_0,lon_0=lon_0)

# m = Basemap(llcrnrlon=lon_min,llcrnrlat=lat_min,urcrnrlon=lon_max,urcrnrlat=lat_max,
#             resolution='i',projection='tmerc',lon_0=lon_0,lat_0=lat_0)

# Project pixel coordinates into map coordinates
xi, yi = m(lons, lats)

# Plot image data
cs = m.pcolor(xi,yi,np.squeeze(values))

# Add Grid Lines
m.drawparallels(np.arange(lat_min, lat_max, 5.), labels=[1,0,0,0], fontsize=10)
m.drawmeridians(np.arange(lon_min, lon_max, 5.), labels=[0,0,0,1], fontsize=10)

# Add Coastlines, and Country Boundaries
m.drawcoastlines()
m.drawcountries()

# Add Colorbar
cbar = m.colorbar(cs, location='right', pad="10%")
# cbar.set_label('Tropospheric N2O')
cbar.set_label('Tropospheric SO2')
# plt.clim(-.0001,.0005) # NO2 range
plt.clim(-.005,.005) # SO2 range

# Add Title
plt.title(date)

# Show and save plot
# plt.show()
fig.savefig(date+'_SO2.png', bbox_inches='tight', dpi = 300)
plt.clf()
