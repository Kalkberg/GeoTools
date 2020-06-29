# -*- coding: utf-8 -*-
"""
Goes through pile of zip files, unzips contents, mosaics necessary pieces in AOI,
clips to target area, deletes all unecessary files

@author: Kalkberg
"""

import arcpy
import zipfile
from arcpy import env
import os
import glob

# Set variables
dir_name = 'D:\\SIFT\\
AOI = 'AOI_Shape.shp'
AOI_name = 'AOI'
Target = 'Target_Shape.shp'
target_name = 'target_2_'
tempRast_name = 'temp.tif'
tempShp_name = 'temp.shp'

# Do arc stuff
arcpy.CheckOutExtension('3D')
env.workspace = dir_name
env.compression = "NONE"

# Change to directory with files
os.chdir(dir_name) 

# Set counter variable that will be used in naming output
a=0

# loop through zip files in dir
for item in glob.glob('*.zip'): 
    a+=1
    file_name = os.path.abspath(item) # get full path of file
    zip_ref = zipfile.ZipFile(file_name) # create zipfile object
    ZipFiles = zip_ref.namelist() # create list of files in zip
    
    # List of files that will be unziped
    UnzipFiles = []
    
    # Unzip all files except footprint of image and browse figure
    for img_name in ZipFiles:
        if ("SHAPE" in img_name) == False and ("BROWSE" in img_name) == False :
            zip_ref.extract(img_name)
            UnzipFiles.append(img_name)
    
    # List of newly created image files in directory (excludes world files, etc.)
    ImgFiles = [i for i in UnzipFiles if '.tif' in i or '.jpg' in i]
    
    # List of files that will be added to mosaic
    mosaicFiles = []
    
    # Check if each raster is in AOI, if so append to list of files to mosaic
    for file in ImgFiles:
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
    
    # Check how many files are to be mosaiced, if just one skip mosaic
    if len(mosaicFiles) > 1:
        
        mosaic_name = AOI_name+str(a)+'.tif'
        
        # Check number of bands in the raster
        desc = arcpy.Describe(mosaicFiles[0])
        bands = desc.bandCount
        
        # Mosaic rasters in AOI
        arcpy.MosaicToNewRaster_management(mosaicFiles,dir_name, mosaic_name, "", "8_BIT_UNSIGNED", 
                                           "", bands, "LAST","FIRST")
    else:
        mosaic_name = mosaicFiles[0]
        
    # Clip to AOI
    arcpy.Clip_management(mosaic_name, '', tempRast_name, Target, '', "ClippingGeometry","MAINTAIN_EXTENT")
    
    # Need to recopy raster to 8 bit unsigned for FLAN matcher to work, otherwise appears black
    arcpy.CopyRaster_management(tempRast_name,target_name+str(a)+'.tif',"","","","","","8_BIT_UNSIGNED")
    
    # Clean up
    arcpy.Delete_management(tempRast_name)
#    arcpy.Delete_management(mosaic_name)
    for file in UnzipFiles:
        arcpy.Delete_management(file)
    
# Reset geoprocessing environment settings
arcpy.ResetEnvironments()