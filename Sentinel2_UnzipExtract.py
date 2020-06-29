# -*- coding: utf-8 -*-
"""
Unzip Sentinel-2 files and extract bands needed for truck analysis.

@author: Kalkberg
"""

import os
import glob
import zipfile
import shutil

cwd = os.getcwd()

# directory to put things in
destination = '\\TRN'
os.mkdir(cwd+destination)

# find zip files
zips = glob.glob('*.zip')

for file in zips:
    
    # show status
    number = zips.index(file) + 1
    print('Unziping image '+ str(number) + '/' + str(len(zips)))
    
    # extract zip file
    with zipfile.ZipFile(file, 'r') as zipobj:
        zipobj.extractall()
    
    # Find directory everything extracted into
    folder = [s for s in os.listdir() if ('SAFE' in s) & (file[0:-5] in s)][0]

    # Find files and copy to destination
    os.chdir(folder)
    B02file = glob.glob('**/*B02*', recursive=True)
    B02file = [B02file[i] for i in range(len(B02file)) if '10m' in B02file[i]]
    shutil.copy(B02file[0],cwd+destination)
    B03file = glob.glob('**/*B03*', recursive=True)
    B03file = [B03file[i] for i in range(len(B03file)) if '10m'in B03file[i]]
    shutil.copy(B03file[0],cwd+destination)
    B04file = glob.glob('**/*B04*', recursive=True)
    B04file = [B04file[i] for i in range(len(B04file)) if '10m' in B04file[i]]
    shutil.copy(B04file[0],cwd+destination)
    B08file = glob.glob('**/*B08*', recursive=True)
    B08file = [B08file[i] for i in range(len(B08file)) if '10m' in B08file[i]]
    shutil.copy(B08file[0],cwd+destination)
    B11file = glob.glob('**/*B11*', recursive=True)
    B11file = [B11file[i] for i in range(len(B11file)) if '20m' in B11file[i]]
    shutil.copy(B11file[0],cwd+destination)
    SCLfile = glob.glob('**/*SCL*', recursive=True)
    SCLfile = [SCLfile[i] for i in range(len(SCLfile)) if '20m' in SCLfile[i]]
    shutil.copy(SCLfile[0],cwd+destination)
    
    # Clean up
    os.chdir('../')
    shutil.rmtree(folder)

