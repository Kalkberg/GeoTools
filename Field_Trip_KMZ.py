# -*- coding: utf-8 -*-
"""
Takes a tab delimited text file of lats, longs, point names, 
point descriptions, and images to make a KMZ of the points and metadata. 
Currently formatted to produce field trips for the
 Tobacco Root Gelogical Society.

@author: Kalkberg
"""

# Import needed packages
import sys
import numpy as np
import csv
import zipfile
import os
import scipy.ndimage

## Create function describing usage and terminating program for errors
#def error():
#    print("Usage: python3 Field_Trip_KMZ.py data.csv Output")
#    print("data.csv contains comma delimited files of lat, long, point name,",
#    " and point description")
#    print("Output is the name of the kmz file and document to generate from data")
#    sys.exit()
#
## Check number of arguments and import, if not two, return error
#if len(sys.argv) == 3:
#    # Import directory to work on and satellite type from input arguments
#    data = sys.argv[1]
#    output = sys.argv[2]
#    print("Data file set to %s" % data)
#    print("Output file set to %s" % output)
#else:
#    print("Error: Wrong number of input arguments!")
#    error()    

data = 'Elliot_Trip_Waypoints.txt'
output = 'Elliott&Lonn_Trip'

# Read in data
lat = []
long = []
name = []
descrip = []
image = []
with open(data,'r') as row:
    next(row)
    reader = csv.reader(row, delimiter = '\t')
    for lats, longs, names, descrips, images in reader:
        lat.append(lats)
        long.append(longs)
        name.append(names)
        descrip.append(descrips)
        image.append(images)

# Convert lat and long to numpy arrays for min/max calculations
lat = np.asarray([float(i) for i in lat])
long = np.asarray([float(i) for i in long])

# Read the dimentions of each image, then calculate width and heights to pass
# on to Google Earth which will have a long dimention close to that specified 
# by the size tag and preserve image aspect ratio
#height = []
#width = []
#size = 500 # Largest dimention of image in pixels
#for i in range(len(image)):
#    if len(image[i]) > 0:
#        imheight, imwidth, c = scipy.ndimage.imread(image[i]).shape
#        if imheight > imwidth:
#            height.append(int(imheight/(imheight/size)))
#            width.append(int(imwidth/(imheight/size)))
#        else:
#            height.append(int(imheight/(imwidth/size)))
#            width.append(int(imwidth/(imwidth/size)))
#    else:# Need to pad with zeros to keep indexing same as source
#        height.append(0) 
#        width.append(0)

# Echo progress
print("Making Google Earth Files...")

# Start writing kml file in root directory
kml = open(output+'.kml','w')
kml.write('<?xml version="1.0" encoding="UTF-8"?>\n' # header
          '<kml xmlns="http://www.opengis.net/kml/2.2">\n' # namespan declaration
          '<Document>\n'
          '<name>Walking tour of the Monument Fault near the '
          'confluence of Bloody Dick Creek and Horse Prairie creeks, '
          'southwestern Montana </name>\n')

# Add source info for TRGS
kml.write('\t<description>'
          'By Colleen Elliott and Jeff Lonn, Montana Bureau of Mines and' 
          'Geology, 1300 W Park Street, Butte, MT, 59701</description>\n')

# Define region
kml.write('\t<Region>\n'
          '\t<LatLonAltBox>\n')
kml.write('\t\t<north>%s</north>\n' %lat.max())
kml.write('\t\t<south>%s</south>\n' %lat.min())
kml.write('\t\t<east>%s</east>\n' %long.max())
kml.write('\t\t<west>%s</west>\n' %long.min())
kml.write('\t</LatLonAltBox>\n'
          '\t</Region>\n')

# Use TRGS logo as overlay
kml.write('\t<ScreenOverlay>\n'
          '\t\t<name>TRGS logo</name>\n'
          '\t\t<Icon>\n'
          '\t\t\t<href>Images/trgs_logo.gif</href>\n'
          '\t\t</Icon>\n'
          '\t\t<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<screenXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
#          '\t\t<size x=".1" y=".1" xunits="fraction" yunits="fraction"/>\n'
          '\t</ScreenOverlay>\n')

# Creat an icon style for placemarks
kml.write('\t<Style id="icon">\n')
kml.write('\t\t<IconStyle>\n')
kml.write('\t\t\t<scale>1.0</scale>\n')
kml.write('\t\t\t<Icon>\n')
kml.write('\t\t\t\t<href>Images/icon.png</href>\n')
kml.write('\t\t\t</Icon>\n')
kml.write('\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n')
kml.write('\t\t</IconStyle>\n')
kml.write('\t</Style>\n')

# Write placemarks
for i in range(len(lat)):
    kml.write('\t<Placemark>\n')
    kml.write('\t\t<name>%s</name>\n'
              %name[i])
    kml.write('\t\t<description>\n')
#    kml.write('\t\t\t%s'%descrip[i])
#    kml.write('\t\t\t<img src="Images/%s"/>' %image[i])
    kml.write('\t\t<![CDATA[\n')
    kml.write('\t\t%s<p>\n' %descrip[i]) # write text desciption
    if len(image[i]) > 0: # add an image if it exists
#        kml.write('\t\t\t<a href="Images/%s">\n' %image[i])
#        kml.write('\t\t\t\t<img src="Images/%s" width="%s" height="%s">\n' 
#                  %(image[i],width[i],height[i]))
        kml.write('\t\t\t<a href="%s">\n' %image[i])
        kml.write('\t\t\t\t<img src="%s", height=500>\n' %image[i])        
        kml.write('\t\t\t</a>\n')
    kml.write('\t\t]]>\n') # close CDATA tag
    kml.write('\t\t</description>/n')
    kml.write('\t\t<styleUrl>#icon</styleUrl>\n')
    kml.write('\t\t<Point>\n')
    kml.write('\t\t<coordinates>%s,%s,0</coordinates>\n' % (long[i], lat[i]))
    kml.write('\t\t</Point>\n')
    kml.write('\t</Placemark>\n')

# End KML file
kml.write('</Document>/n'
          '</kml>')
kml.close()

print("Writing KMZ...")

# Create kmz file
z = zipfile.ZipFile(output+'.kmz', 'w', zipfile.ZIP_DEFLATED)
#for i in range(len(image)):
#    if len(image[i]) > 0: # Don't write image files if they don't exist
#        z.write(image[i],'Images\\'+image[i])
z.write('trgs_logo.gif','Images\\trgs_logo.gif')
z.write('icon.png','Images\\icon.png')
z.write(output+'.kml')
z.close()