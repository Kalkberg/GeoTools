# -*- coding: utf-8 -*-
"""
Mosaic rasters intersecting an AOI and clip mosaic to AOI using ArcPy

@author: Kalkberg
"""

import arcpy
from arcpy import env
import os
import glob

# Set variables
dir_name = 'D:\\SIFT\\testbed'
mosaic_name = 'mosaic.tif'
AOI = 'AOI_Shape.shp'
Target = 'Target_Shape.shp'
target_name = 'target.tif'
tempRast_name = 'temp.tif'
tempShp_name = 'temp.shp'

# Do arc stuff
arcpy.CheckOutExtension('3D')
env.workspace = dir_name
env.compression = "NONE"

# Change to directory with files
os.chdir(dir_name) 

# List of image files in directory
files = []

# Find image files in directory
for file in glob.glob('*.tif')+glob.glob('*.jpg'):
    files.append(file)

# List of files that will be added to mosaic
mosaicFiles = []

# Check if each raster is in AOI, if so append to list of files to mosaic
for file in files:
    #Create shapefile of raster
    arcpy.RasterDomain_3d(file, tempShp_name, 'POLYGON')

    #Check if shape file overlaps AOI    
    arcpy.Intersect_analysis([tempShp_name, AOI], "in_memory/output")
    result = arcpy.GetCount_management('in_memory/output')
    overlap = int(result.getOutput(0))
    
    if overlap == 1:
        mosaicFiles.append(file)
    
    # Clean up
    arcpy.Delete_management('in_memory/output')
    arcpy.Delete_management(tempShp_name)

# Mosaic rasters in list
arcpy.MosaicToNewRaster_management(mosaicFiles,dir_name, mosaic_name, "", "8_BIT_UNSIGNED", 
                                   "", "3", "LAST","FIRST")

# Clip to AOI
arcpy.Clip_management(mosaic_name, '', tempRast_name, Target, '', "ClippingGeometry","MAINTAIN_EXTENT")

# Need to recopy raster to 8 bit unsigned for FLAN matcher to work, otherwise appears black
arcpy.CopyRaster_management(tempRast_name,target_name,"","","","","","8_BIT_UNSIGNED")

# Clean up
arcpy.Delete_management(tempRast_name)
arcpy.Delete_management(mosaic_name)

# Reset geoprocessing environment settings
arcpy.ResetEnvironments()