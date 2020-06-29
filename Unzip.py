# -*- coding: utf-8 -*-
"""
Extracts all image tiles form all zip files in a directory. Modified from 

https://stackoverflow.com/questions/31346790/unzip-all-zipped-files-in-a-folder-to-that-same-folder-using-python-2-7-5

@author: Kalkberg
"""

import os
import zipfile

dir_name = 'D:\\SIFT\\


# Change to directory with files
os.chdir(dir_name) 

for item in os.listdir(dir_name): # loop through all items in dir
    if item.endswith('.zip'): # only work on zip files
        file_name = os.path.abspath(item) # get full path of file
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        files = zip_ref.namelist()
        for img_name in files:
            if ("SHAPE" in img_name) == False and ("BROWSE" in img_name) == False :
                zip_ref.extract(img_name)