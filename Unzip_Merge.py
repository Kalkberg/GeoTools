# -*- coding: utf-8 -*-
"""
Goes through pile of zip files, unzips contents, mosaics necessary pieces in AOI,
clips to target area, deletes all unecessary files

@author: Kalkberg
"""

import zipfile
import os
import glob
import rasterio
from rasterio.merge import merge

# Set variables
dir_name = r'D:\GitHub\Image_similarity\clip_test'
ext = ".tif"

os.chdir(dir_name)

# loop through zip files in dir
for item in glob.glob(dir_name+'\*.zip'): 

    file_name = os.path.abspath(item) # get full path of file
    zip_ref = zipfile.ZipFile(file_name) # create zipfile object
    ZipFiles = zip_ref.namelist() # create list of files in zip
    directory, zip_name = os.path.split(file_name)
    img_name = zip_name[:-4]+ext
    
    # List of files that will be unziped
    ImgFiles = []
    
    # Unzip all files except footprint of image and browse figure
    for file in ZipFiles:
        if ("SHAPE" in file) == False and ("BROWSE" in file) == False and (ext in file) == True:
            zip_ref.extract(file)
            ImgFiles.append(file)
    
    # Open images and append to list
    imgs_to_mosaic = [] 
    for file in ImgFiles:
        img = rasterio.open(file)
        imgs_to_mosaic.append(img)
   
    # Mosaic images
    mosaic, out_trans = merge(imgs_to_mosaic)
    
    # Update metadata
    profile = img.profile
    out_meta = img.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": mosaic.shape[1],
                     "width": mosaic.shape[2],
                     "transform": out_trans,
                     "photometric": profile["photometric"],
                     "blockxsize": profile["blockxsize"],
                     "blockysize": profile["blockysize"],
                     "compress": profile["compress"],
                     "dtype": profile["dtype"]
                     })
    
    with rasterio.open(img_name, "w", **out_meta) as dest:
        dest.write(mosaic)
    
    # Clean up
    for img in imgs_to_mosaic:
        img.close()
    for file in ImgFiles:
        os.remove(file)