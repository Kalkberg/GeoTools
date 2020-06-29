# -*- coding: utf-8 -*-
"""
Sentinel-5 P data pull

@author: Kalkberg
"""
from sentinelsat import SentinelAPI # install via pip
import os
import glob
from shapely import wkt

# Set up API
api = SentinelAPI(user='s5pguest', password='s5pguest', api_url='https://s5phub.copernicus.eu/dhus')

# Define area of interest in WKT format
# Go to https://arthur-e.github.io/Wicket/sandbox-gmaps3.html and draw one out
AOI = ''

# Date
startdate = '2020401'
enddate = '20200430'
frequency = 1 # every nth day in date range will be downloaded

# Download list of Sentinel S5-P NO2 products in region of interest
products = api.query(AOI,
                     date=(startdate,enddate),
                     platformname='Sentinel-5',
                     producttype='L2__NO2___', # useful data types 'L2__SO2___' and 'L2__NO2___'
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

    # Calculate difference between AOI and image footprint
    difference = AOIshape.difference(footprintshape) 
    
    # Append tolist
    differences.append(difference.wkt)

# Add list to dataframe
products_df['differences'] = differences

# Drop rows for images that don't completely overlap
indexincomplete = products_df[products_df['differences'] != 'POLYGON EMPTY'].index
products_df.drop(indexincomplete, inplace=True)


# download single scene by index
images = products_df.index.values.tolist()
images = images[1::frequency] # cut down datasets to having images only nth day
for image in images:
    number = images.index(image)
    print('Downloading image '+ str(number) + '/' + str(len(images)))
    api.download(image)

# change extension from zip to nc - nc is actual extension, 
# but sentinelsat makes it zip in a hard coded error

imgFile = glob.glob('S5P*') # search for Sentinel 5 files
imgFile = [i for i in imgFile if '.zip' in i[-4:len(i)]] # only accept zips

for file in imgFile:
    os.rename(file,file[:-4]+'.nc')