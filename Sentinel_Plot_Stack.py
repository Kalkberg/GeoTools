# -*- coding: utf-8 -*-
"""
Plot Sentinel 5P data

@author: Kalkberg
"""
# need environment variable if basemap not properly built
import os
os.environ['PROJ_LIB'] = '/opt/conda/pkgs/proj4-5.2.0-he1b5a44_1003/share/proj'
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import glob

# Change directory
os.chdir(os.getcwd()+'\\Data\\NO2\\')

# Find all netCDF4 images in directory
imgFiles = glob.glob('S5P_OFFL_L2__NO2*') # search for Sentinel 5 files
imgFiles = [i for i in imgFiles if '.nc' in i[-4:len(i)]] # only accept zips

# Import image and unpack data
# valuesmax = []
# valuesmin = []

# QA mask threshold - don't plot cells with QA value less than
# qathreshold = 0.75

for file in imgFiles:
    # Display status
    number = imgFiles.index(file)
    print('Plotting image '+ str(number) + '/' + str(len(imgFiles)))    

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
    # QA = variables['qa_value'][0,:,:]
    
    # Create new mask based on QA value to remove values below QA threshold
    # QAmask=np.ma.masked_greater(QA,qathreshold)
    # combinedmask=np.logical_and(QAmask,values.mask)
    # values=np.ma.array(values.data,mask=combinedmask)
    
    # valuesmax.append(values.max())
    # valuesmin.append(values.min())
    # valuesmax.append(np.min(variables['nitrogendioxide_tropospheric_column_precision'][0]))
    
    # Get timestamp
    date = variables['time_utc'][0][0][0:10] # for NO2 data
    # date = file[20:28] # use existing timestamp in file name rather than pulling from data
    
    # Start mapping
    
    # Set up projection
    plt.figure(figsize=(8.5,11)) # make a large plot
    
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
    cbar.set_label('Tropospheric NO2')
    cbar.set_label('Total Vertical Column NO2')
    plt.clim(-.0001,.0005) # NO2 range
    # plt.clim(-.005,.005) # SO2 range
    
    # Add Title
    plt.title(date)
    
    # Show and save plot
    # plt.show()
    plt.savefig(date+'_NO2.png', bbox_inches='tight', dpi = 300)
    plt.clf()
    plt.close()
    
    # close image
    img.close()
