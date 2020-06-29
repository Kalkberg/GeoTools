# -*- coding: utf-8 -*-
"""
Sentinel-2A data pull

@author: Kalkberg
"""
from sentinelsat import SentinelAPI # install via pip
import os
import glob
from shapely import wkt
from shapely.geometry import shape, Polygon
import fiona

# Set up API
api = SentinelAPI(user='', password='', api_url='https://scihub.copernicus.eu/apihub/')

# Define area of interest in WKT format
# Go to https://arthur-e.github.io/Wicket/sandbox-gmaps3.html and draw one out or get from shapefile
# AOI = ''
path = 'name.shp'
c = fiona.open(path)
collection = [ shape(item['geometry']) for item in c ]
AOI = [ Polygon(pol.exterior.coords).wkt for pol in collection ][0]

# Date
startdate = '20180601'
enddate = '20200601'
frequency = 1 # every nth day in date range will be downloaded

# Download list of Sentinel S5-P NO2 products in region of interest
products = api.query(AOI,
                     date=(startdate,enddate),
                     platformname='Sentinel-2',
                     producttype='S2MSI2A', 
                     # filename='*R051*', # Only accept square images
                      # filename='S2A_*',  # Only accept Sentinel 2A images
                     cloudcoverpercentage=(0, 10)
                     )

# Convert to pandas dataframe for ease of use
products_df = api.to_dataframe(products)

# filter out mismatched scenes
# scenes = ['SVV', 'SVU', 'SWV', 'SWU', 'SXU', 'SWA', 'SVA']
scenes = ['ULC']
products_df = products_df[products_df['title'].str.contains('|'.join(scenes))]

# products_df=products_df[products_df['title'].str.contains('ULC')]

# # Convert AOI to shapely file
# AOIshape = wkt.loads(AOI)

# # Create empty list of overlaping geometries
# differences = []

# # Check which images don't have complete overlap with AOI
# for image in range(len(products_df)):
    
#     # Convert image footprint to shapely file
#     footprint = products_df.iloc[image,:]['footprint']
#     footprintshape = wkt.loads(footprint)

#     # Calculate difference between AOI and image footprint
#     difference = AOIshape.difference(footprintshape) 
    
#     # Append tolist
#     differences.append(difference.wkt)

# # Add list to dataframe
# products_df['differences'] = differences

# # Drop rows for images that don't completely overlap
# indexincomplete = products_df[products_df['differences'] != 'POLYGON EMPTY'].index
# products_df.drop(indexincomplete, inplace=True)


# # download single scene by index
images = products_df.index.values.tolist()
images = images[1::frequency] # cut down datasets to having images only nth day
for image in images:
    number = images.index(image)
    print('Downloading image '+ str(number) + '/' + str(len(images)))
    api.download(image)

# change extension from zip to nc - nc is actual extension, 
# but sentinelsat makes it zip in a hard coded error

# imgFile = glob.glob('S5P*') # search for Sentinel 5 files
# imgFile = [i for i in imgFile if '.zip' in i[-4:len(i)]] # only accept zips

# for file in imgFile:
#     os.rename(file,file[:-4]+'.nc')

# api.download_all(['34f9e275-808c-4aa5-aaee-20490c698e1f'])