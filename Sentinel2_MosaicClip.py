# -*- coding: utf-8 -*-
"""
Mosaics and clips Sentinel-2 rasters to a shape file

@author: Kalkberg
"""

import os
import glob
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.io import MemoryFile
from rasterio.mask import mask
import fiona

# set directory and navigate
directory = os.getcwd() + '\\dir'
filetype = '*.jp2'
# outfile = 'test.csv'
shapename  = 'shape.shp'
os.chdir(directory)
proj = rasterio.crs.CRS.from_epsg(4326) # common projection for output files

# Read shape file
with fiona.open(shapename, 'r') as shapefile:
    shape = [feature['geometry'] for feature in shapefile]
    a=shapefile.crs

def mosaicraster (rasters, date, proj):
    
    filename = date + '_mosaic.tif'
    
    # read in rasters
    raster_objs = []
    for raster in rasters:
        src = rasterio.open(raster, driver='JP2OpenJPEG')
        raster_objs.append(src)
    
    # reproject to a common projection
    for raster in raster_objs:
        transform, width, height = calculate_default_transform(raster.crs, proj, raster.width, raster.height, *raster.bounds)
        
        reproj = np.zeros((width,height), raster.dtypes[0])
        reproj, reproj_transform = reproject(source=rasterio.band(raster,1), #source
                  destination=reproj, #destination
                  src_transform=raster.transform,
                  src_crs=raster.crs,
                  dst_transform=transform,
                  dst_crs=proj,
                  resampling=Resampling.nearest,
                  drtype=raster.dtypes[0])
        # write a temporary file for making a mosaic
        raster_reproj = rasterio.open(raster.name[:-4]+'temp.jp2','w+', driver='JP2OpenJPEG',
                          width=width, height=height,
                          count=1,
                          crs=proj,
                          transform=transform,
                          dtype=raster.dtypes[0]
                          )
        raster_reproj.write(reproj,1)
        raster_objs[raster_objs.index(raster)] = raster_reproj
            
    # merge rasters and save file
    mosaic, out_trans = merge(raster_objs)
       
    out_meta = raster_objs[0].meta

    out_meta.update({"driver": "GTiff",
                  "height": mosaic.shape[1],
                  "width": mosaic.shape[2],
                  "transform": out_trans})
    
    with rasterio.open(filename, 'w', **out_meta) as dest:
        dest.write(mosaic)
        
    # close all open files and delete temps
    for raster in raster_objs:
        raster.close()
        # if 'temp' in raster.name:
            # os.remove(raster.name)

    return (filename)

def clipraster (raster, shape, proj):
      
    src = rasterio.open(raster)
    
    image, out_trans = mask(src, shape, crop = True)
       
    geotiff = rasterio.open(raster[:-4]+'_clip.tif','w',driver='Gtiff',
                              width=image.shape[1], height=image.shape[2],
                              count=1,
                              crs=proj,
                              transform=out_trans,
                              dtype=src.dtypes[0]
                              )
   
    geotiff.write(np.squeeze(image),1)
    geotiff.close()

# Find unique dates
files = glob.glob(filetype)
dates = np.unique(np.array([i[7:15] for i in files])).tolist()

for date in dates:
   
    # show status
    number = dates.index(date) + 1
    print('Processing image '+ str(number) + '/' + str(len(dates)))
       
    # find all files with the same date
    B02files = [i for i in files if ('B02' in i) & (date in i)]
    # B03files = [i for i in files if ('B03' in i) & (date in i)]
    # B04files = [i for i in files if ('B04' in i) & (date in i)]
    # B08files = [i for i in files if ('B08' in i) & (date in i)]
    # B11files = [i for i in files if ('B11' in i) & (date in i)]
    # SCLfiles = [i for i in files if ('SCL' in i) & (date in i)]
    
    # mosaic rasters
    B02mosaic = mosaicraster(B02files, date+'_B02', proj)
    # B03mosaic = mosaicraster(B03files, date+'_B03', proj)
    # B04mosaic = mosaicraster(B04files, date+'_B04', proj)
    # B08mosaic = mosaicraster(B08files, date+'_B08', proj)
    # B11mosaic = mosaicraster(B11files, date+'_B11', proj)
    # SCLmosaic = mosaicraster(SCLfiles, date+'_SCL', proj)  
    
    # save rasters
    clipraster(B02mosaic, shape, proj)
    # clipraster(B03mosaic, shape)
    # clipraster(B04mosaic, shape)
    # clipraster(B08mosaic, shape)
    # clipraster(B11mosaic, shape)
    # clipraster(SCLmosaic, shape)

