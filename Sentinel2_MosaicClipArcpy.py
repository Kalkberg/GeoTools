# -*- coding: utf-8 -*-
"""
Mosaics and clips Sentinel-2 rasters to a shape  using Arcpy rather than rasterio

@author: Kalkberg
"""

import os
import glob
import numpy as np
import arcpy
from arcpy import env

# define environmental variables
directory = '\\TRN'
shapefile = 'TRN.shp'
imgextension = '*.jp2'
cds = "Asia Lambert Conformal Conic" # coordinate system
restext = "10 Meters" # raster resolution, text
res =  10 # raster resoltion, values

# set directory and navigate
directory = os.getcwd() + directory
os.chdir(directory)

# Do arc stuff
arcpy.CheckOutExtension('3D')
env.workspace = directory
env.compression = "NONE"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(cds)
arcpy.env.XYResolution = restext

def mosaic_clip_raster (rasters, date, directory, shape):
    
    mosaicname = date + '_mosaic.tif'
    clipname = date + '_mosaic_clip.tif'

    arcpy.MosaicToNewRaster_management(rasters, directory, mosaicname, "", "16_BIT_UNSIGNED", 
                                   "", "1", "MAXIMUM","FIRST")
    
    # Clip to AOI
    arcpy.Clip_management(mosaicname, '', clipname, shape, '', "ClippingGeometry","NO_MAINTAIN_EXTENT")


def project (rasters, cds):
    
    outrasters = []
    for raster in rasters:
        outraster = raster[:-4]+'_proj.tif'
        arcpy.ProjectRaster_management(raster, outraster, arcpy.SpatialReference(cds))
        outrasters.append(outraster)
        
    return outrasters
    
# Find unique dates
files = glob.glob(imgextension)
dates = np.unique(np.array([i[7:15] for i in files])).tolist()
dates = dates[20:28]

# Convert shape file to raster full of zeros (if shape Id is 0), to fill edge gaps
shaperaster = shapefile[:-4]+'_raster.tif'
arcpy.PolygonToRaster_conversion(shapefile, 'Id', shaperaster, "CELL_CENTER", 'ID', res)

# Snap all rasters to shape file, to ensure consistent alignment
arcpy.env.snapRaster = shaperaster

for date in dates:
   
    # show status
    number = dates.index(date) + 1
    print('Processing image '+ str(number) + '/' + str(len(dates)))
       
    # find all files with the same date
    B02files = [i for i in files if ('B02' in i) & (date in i)]
    B03files = [i for i in files if ('B03' in i) & (date in i)]
    B04files = [i for i in files if ('B04' in i) & (date in i)]
    B08files = [i for i in files if ('B08' in i) & (date in i)]
    B11files = [i for i in files if ('B11' in i) & (date in i)]
    SCLfiles = [i for i in files if ('SCL' in i) & (date in i)]

    # Project rasters to the same coordinate system
    B02files = project(B02files, cds) + [shaperaster]
    B03files = project(B03files, cds) + [shaperaster]
    B04files = project(B04files, cds) + [shaperaster]
    B08files = project(B08files, cds) + [shaperaster]
    B11files = project(B11files, cds) + [shaperaster]
    SCLfiles = project(SCLfiles, cds) + [shaperaster]

    # mosaic and clip rasters
    B02mosaic = mosaic_clip_raster(B02files, date+'_B02', directory, shapefile)
    B03mosaic = mosaic_clip_raster(B03files, date+'_B03', directory, shapefile)
    B04mosaic = mosaic_clip_raster(B04files, date+'_B04', directory, shapefile)
    B08mosaic = mosaic_clip_raster(B08files, date+'_B08', directory, shapefile)
    B11mosaic = mosaic_clip_raster(B11files, date+'_B11', directory, shapefile)
    SCLmosaic = mosaic_clip_raster(SCLfiles, date+'_SCL', directory, shapefile)

# Reset geoprocessing environment settings
arcpy.ResetEnvironments()

# Clean up
tempfiles = []
tempfiles += glob.glob('*proj*')
tempfiles += glob.glob('*mosaic.tif*')
tempfiles += glob.glob(shaperaster[:-4]+'*')
for file in tempfiles:
    os.remove(file)