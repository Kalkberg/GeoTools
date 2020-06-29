# -*- coding: utf-8 -*-
"""
FLANN based image matcher adapted from:
    https://www.udemy.com/course/python-for-computer-vision-with-opencv-and-deep-learning/

@author: Kalkberg
"""

# Import libraries

import cv2 # Note: CV2 must be version 3.4 or earlier, or built with SIFT
import numpy as np
import matplotlib.pyplot as plt

# function to show images for testing

def display(img):
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)
    ax.imshow(img)

# Figure out which images we're working with
directory = 'D:/SIFT/'    
targetFile = 'Target.tif'
imgFile = 'AOI_small.tif'
outFile = 'flann_matches14.png'
matchThresh = 0.6 #Threshold for retaining matches

# path = r'D:\SIFT\Mangya\Target.tif'
# img = cv2.imread(path)

Target = cv2.imread(directory+targetFile)
Target = cv2.cvtColor(Target,cv2.COLOR_BGR2RGB)

img = cv2.imread(directory+imgFile)
img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

# plt.imshow(Target)

# cv2.imshow('image',img1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


# Initiate SIFT detector
sift = cv2.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(Target,None)
kp2, des2 = sift.detectAndCompute(img,None)

# FLANN parameters
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

flann_matches = cv2.drawMatchesKnn(Target,kp1,img,kp2,matches,None,**draw_params)

fig = plt.figure(figsize=(100,100))
ax = fig.add_subplot(111)
ax.imshow(flann_matches)
fig.savefig(outFile)