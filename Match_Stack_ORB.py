# -*- coding: utf-8 -*-
"""
ORB based image matcher adapted for looking at a stack of images

@author: Kalkberg
"""


# Import libraries

import cv2
# import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import sys

# function to show images for testing
def display(img):
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)
    ax.imshow(img)

# Input parameters
directory = 'D:/SIFT/'    
targetName = 'Test' # Root file name of image to be compared against
imgName = 'target_2' # Root file name of images to test
matchThresh = 0.75 #Threshold for retaining matches


# Navigate to directory
os.chdir(directory) 

# Find files we're working with
targetFile = glob.glob('*'+targetName+'*')
targetFile = [i for i in targetFile if '.tif' in i[-4:len(i)]][0] # only accept tiffs
imgFiles = glob.glob('*'+imgName+'*')
imgFiles = [i for i in imgFiles if '.tif' in i[-4:len(i)]]

# Throw an error if something is wrong here
if len(targetFile) != 1:
    sys.exit('There can only be one file with the same name as the source image in the parent directory.')
targetFile = targetFile[0] # Change from list to str for imread

for file in imgFiles:
    
    # Read in files to compare
    Target = cv2.imread(directory+targetFile)
    Target = cv2.cvtColor(Target,cv2.COLOR_BGR2RGB)
    
    img = cv2.imread(directory+file)
    if len(img.shape) == 3: # only recolor 3 band rasters
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    


    # # Initiate SIFT detector
    # sift = cv2.xfeatures2d.SIFT_create()
    
    # Inititate ORB dectector
    orb = cv2.ORB()
    
    # Find the keypoints with ORB
    kp1 = orb.detect(img, None)
    kp2 = orb.detect(Target, None)
    
    # Compute descriptors with ORB
    kp1, des1 = orb.compute(img, kp1)
    kp2, des2 = orb.compute(Target, kp2)
    
    # # find the keypoints and descriptors with SIFT
    # kp1, des1 = sift.detectAndCompute(img,None)
    # kp2, des2 = sift.detectAndCompute(Target,None)
    
    # FLANN parameters
    # FLANN_INDEX_LSH = 6
    # index_params= dict(algorithm = FLANN_INDEX_LSH,
    #                table_number = 6, # 12
    #                key_size = 12,     # 20
    #                multi_probe_level = 1) #2
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)  
    
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    
    matches = flann.knnMatch(des1,des2,k=2)
    
    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]
    
    # ratio test to determine which matches to keep
    for i,(match1,match2) in enumerate(matches):
        if match1.distance < matchThresh*match2.distance:
            
            matchesMask[i]=[1,0]
    
    # Set up and plot figure
    draw_params = dict(matchColor = (0,255,0),
    #                   singlePointColor = (255,0,0),
                       matchesMask = matchesMask,
                       flags = 2) # Flag 2 keeps unmatched points from plotting
    
    flann_matches = cv2.drawMatchesKnn(img,kp1,Target,kp2,matches,None,**draw_params)
    
    fig = plt.figure(figsize=(100,100))
    ax = fig.add_subplot(111)
    ax.imshow(flann_matches)
    fig.savefig(file[0:-4]+'_matched_ORB.png')
    plt.close()