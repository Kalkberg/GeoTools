# -*- coding: utf-8 -*-
"""
Pull down Sentinel 5P images, and plot one at a time

@author: Kalkberg
"""

from sentinelsat import SentinelAPI
import os
import glob
from shapely import wkt
# Start mapping
# need environment variable if basemap not properly built
import netCDF4
os.environ['PROJ_LIB'] = '/opt/conda/pkgs/proj4-5.2.0-he1b5a44_1003/share/proj'
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

def sentplot(path):

    # file path
    path = path
    
    # read in data
    img = netCDF4.Dataset(path, mode='r')
    variables = img.groups['PRODUCT']
    
    # get lats, lons, and NO2 values
    lats = variables['latitude'][0,:,:]
    lons = variables['longitude'][0,:,:]
    NO2 = variables['nitrogendioxide_tropospheric_column'][0,:,:]
    
    # Get timestamp
    date = variables['time_utc'][0][0][0:10]
    
    # Close image
    img.close()
    
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
    cs = m.pcolor(xi,yi,np.squeeze(NO2))
    
    # Add Grid Lines
    m.drawparallels(np.arange(lat_min, lat_max, 5.), labels=[1,0,0,0], fontsize=10)
    m.drawmeridians(np.arange(lon_min, lon_max, 5.), labels=[0,0,0,1], fontsize=10)
    
    # Add Coastlines, and Country Boundaries
    m.drawcoastlines()
    m.drawcountries()
    
    # Add Colorbar
    cbar = m.colorbar(cs, location='right', pad="10%")
    cbar.set_label('Tropospheric N2O')
    plt.clim(-.0001,.0005)
    
    # Add Title
    plt.title(date)
    
    # Show and save plot
    plt.show()
    fig.savefig(date+'.png', bbox_inches='tight', dpi = 300)


# Set up API
api = SentinelAPI(user='s5pguest', password='s5pguest', api_url='https://s5phub.copernicus.eu/dhus')

# Define area of interest in WKT format
AOI = ''

# Date
startdate = '20200101'
enddate = '20200430'

# Download list of Sentinel S5-P NO2 products in region of interest
products = api.query(AOI,
                      date=(startdate,enddate),
                     platformname='Sentinel-5',
                     producttype='L2__NO2___',
                     processingmode='Offline', # 'Near real time' or 'Offline'
                     )

# Convert to pandas dataframe for ease of use
products_df = api.to_dataframe(products)

# Convert AOI to shapely file
AOIshape = wkt.loads(AOI)

# Create empty list of overlaping geometries
differences = []

# Check which images don't have complete overlap with AOI
for image in range(len(products_df)):
    
    # Convert image footprint to shapely file
    footprint = products_df.iloc[image,:]['footprint']
    footprintshape = wkt.loads(footprint)

    difference = AOIshape.difference(footprintshape) # difference between AOI and image footprint
    
    differences.append(difference.wkt)

# Add list to dataframe
products_df['differences'] = differences

# Drop rows for images that don't completely overlap
indexincomplete = products_df[products_df['differences'] != 'POLYGON EMPTY'].index
products_df.drop(indexincomplete, inplace=True)

# download single scene by index
images = products_df.index.values.tolist()
for image in images:
    number = images.index(image)
    print('Downloading image '+ str(number) + '/' + str(len(images)))
    api.download(image)
    
    # rename image to have correct extension
    imgFile = glob.glob('S5P*') # search for Sentinel 5 files
    imgFile = [i for i in imgFile if '.zip' in i[-4:len(i)]] # only accept zips
    
    for file in imgFile:
        newfile = file[:-4]+'.nc'
        
        os.rename(file,newfile)
    
        # plot image
        sentplot(newfile)
        
        # delete image so as not to take up too much space
        os.remove(newfile)

