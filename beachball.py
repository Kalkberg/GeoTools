# -*- coding: utf-8 -*-
"""
Code for ingesting moment tensor solutions and generating KMZ files with 
"beachball" diagrams at epicenter locations, colored by depth and sized by
magnitude

Currently configured to plot data from the Montana Regional Seismic Network,
which is operated by the Montana Bureau of Mines and Geology. Edit lines 128-
134, 147-156, and 195-200 to make it fit for your personal data set. 

Note that size formula for magnitude legend on line 98 needs to be rejiggered 
for data with different maximum and minimum magnitudes.

Written by Petr Yakovlev in 2016.

@author: Kalkberg
"""
# Import needed modules
import os
import sys
import pylab
import shutil
import zipfile 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from obspy.imaging.beachball import beachball

# Create function describing usage and terminating program for errors
def error():
    print("Usage: python3 beachball.py working_dir data.csv Output")
    print("Where working_dir is the full path to the data")
    print("e.g. C:/users/beachball")
    print("data.csv contains comma delimited files of long, lat, depth,",
    " magnitude, strke, dip, rake and date")
    print("Output is the name of the kmz file and document to generate from data")
    sys.exit()

# Check number of arguments and import, if not three, return error
if len(sys.argv) == 4:
    # Import directory to work on and satellite type from input arguments
    workdir = sys.argv[1]
    data = sys.argv[2]
    output = sys.argv[3]
    print("Current working directory is set to %s" % workdir)
    print("Data file set to %s" % data)
    print("Output file set to %s" % output)
else:
    print("Error: Wrong number of input arguments!")
    error()    

# Move to working directory and create a bin for beachballs
os.chdir(workdir)
os.mkdir('Ballbin')

# Read in data, cut out headers and redistribute
data = np.genfromtxt(data, delimiter=',')
data = np.delete(data, (0), axis=0)
long, lat, depth, magnitude, strike, dip, rake, date = data[:,0], data[:,1], \
    data[:,2], data[:,3], data[:,4], data[:,5], data[:,6], data[:,7]

# Echo progress
print("Making beach balls...")    
    
# Create custom color bar based on range of magnitudes in data set
def Make_Colormap(seq):
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)
    
c = mcolors.ColorConverter().to_rgb
ColorMap = Make_Colormap(
    [(0.0, 0.0, 1.0), c('cyan'), 
     (np.median(magnitude)-2*magnitude.std())/magnitude.max(), 
     c('cyan'), (0.2, 0.6, 0.2), 
     (np.median(magnitude)/magnitude.max()),
     (0.2, 0.6, 0.2), c('yellow'),
     (np.median(magnitude)+2*magnitude.std())/magnitude.max(),
     c('yellow'),(1.0, 0.0, 0.0)])

# Toss balls in ballbin, i.e. create png files of moment tensors for kmz
os.chdir('Ballbin')
for i in range(0,data.shape[0]):
    ball = beachball([strike[i], dip[i], rake[i]], 
                     size=1000, linewidth=2, 
                     facecolor=ColorMap(depth[i]/depth.max()), outfile='%s.png' % i)
    plt.close()

# Make directory for legends
os.chdir('..')
os.mkdir('Legends')    
os.chdir('Legends')
    
# Create a plot showing depth color bar aka legend 1
a = np.outer(np.arange(0,1,0.01),np.ones(10))
legend1, ax1 = plt.subplots()
ax1.imshow(a,cmap=ColorMap, origin='lower', extent=[0,1,0,depth.max()], \
                                                 aspect=6/depth.max())
ax1.axes.get_xaxis().set_visible(False)
ax1.set_ylabel('Depth (km)', fontsize=12)
ax1.locator_params(nbins=6)
ax1.tick_params(axis='y', which='major', labelsize=10)
legend1.set_size_inches(4,1.5)
legend1.savefig('legend1.png', dpi=100, transparent=False, bbox_inches='tight')
plt.close()

# Create a plot showing different beachball sizes aka legend 2
circley = np.arange(np.rint(magnitude.min()), np.rint(magnitude.max()), 1)
circlex = np.ones(circley.size)
legend2, ax2 = plt.subplots()
ax2.scatter(circlex, circley,s=(45+20*circley*circley), 
            facecolor='None', edgecolor='k', linewidth=1) # Size formula scaled to GE
ax2.axes.get_xaxis().set_visible(False)
ax2.set_ylabel('Magnitude', fontsize=12)
ax2.locator_params(nbins=np.rint(magnitude.max())-np.rint(magnitude.min())+1)
ax2.tick_params(axis='y', which='major', labelsize=10)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.yaxis.set_ticks_position('none')
ax2.yaxis.set_ticks(np.arange(np.rint(magnitude.min()),np.rint(magnitude.max()),1))
pylab.ylim([circley.min()-0.5,circley.max()+1]) # leave space for circles at top
legend2.set_size_inches(.75,1.59)
legend2.savefig('legend2.png', dpi=100, transparent=False, bbox_inches='tight')
plt.close()

# Echo progress
print("Making Google Earth Files...")

# Start writing kml file in root directory
os.chdir('..')
kml = open('beachballs.kml','w')
kml.write('<?xml version="1.0" encoding="UTF-8"?>\n' # header
          '<kml xmlns="http://www.opengis.net/kml/2.2">\n' # namespan declaration
          '<Document>\n'
          '<name>%s Earthquakes</name>' %output)

# Add source info for MBMG and disclaimer
kml.write('\t<description>Data obtained from the Montana Bureau of Mines and '
          'Geology. '
          'Data sourced by the Montana Regional Seismic Network (MRSN). '
          'Disclaimer: These fault plane solutions should be considered'
          'preliminary and have not been reviewed for completeness or' 
          'consistency.</description>\n')

# Define region
kml.write('\t<Region>\n'
          '\t<LatLonAltBox>\n')
kml.write('\t\t<north>%s</north>\n' %lat.max())
kml.write('\t\t<south>%s</south>\n' %lat.min())
kml.write('\t\t<east>%s</east>\n' %long.max())
kml.write('\t\t<west>%s</west>\n' %long.min())
kml.write('\t</LatLonAltBox>\n'
          '\t</Region>\n')

# Put MBMG logo at bottom right
kml.write('\t<ScreenOverlay>\n'
          '\t\t<Icon>\n'
          '\t\t\t<href>http://mbmg.mtech.edu/graphics/logombmg.png</href>\n'
          '\t\t</Icon>\n'
          '\t\t<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<screenXY x=".85" y=".2" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<size x=".15" y=".1" xunits="fraction" yunits="fraction"/>\n'
          '\t</ScreenOverlay>\n')

# Plot legend 1, depth color bar
kml.write('\t<ScreenOverlay>\n'
          '\t\t<Icon>\n'
          '\t\t\t<href>Legends/legend1.png</href>\n'
          '\t\t</Icon>\n'
          '\t\t<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<screenXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<size x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
          '\t</ScreenOverlay>\n')

# Plot legend 2, magnitude size
kml.write('\t<ScreenOverlay>\n'
          '\t\t<Icon>\n'
          '\t\t\t<href>Legends/legend2.png</href>\n'
          '\t\t</Icon>\n'
          '\t\t<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<screenXY x="88" y="1" xunits="pixels" yunits="fraction"/>\n'
          '\t\t<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
          '\t\t<size x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
          '\t</ScreenOverlay>\n')

# Generate icon styles for each beachball
for i in range(0,data.shape[0]):
    kml.write('\t<Style id="%s">\n' %i)
    kml.write('\t\t<IconStyle>\n')
    kml.write('\t\t\t<heading>.00001</heading>\n')
    kml.write('\t\t\t<scale>%s</scale>\n' %(.3+magnitude[i]/magnitude.max()))
    kml.write('\t\t\t<Icon>\n')
    kml.write('\t\t\t\t<href>Ballbin/%s.png</href>\n' %i)
    kml.write('\t\t\t</Icon>\n')
    kml.write('\t\t</IconStyle>\n')
    kml.write('\t</Style>\n')
    
# Write placemarks
for i in range(0,data.shape[0]):
    kml.write('\t<Placemark>\n')
    kml.write('\t\t<description>YrMoDy = %s<br/>Depth = %s km<br/>'
              'Magnitude = %s <br/>'
              'Disclaimer: These fault plane solutions should be considered '
              'preliminary and have not been reviewed for completeness or ' 
              'consistency.</description>\n'
              %(date[i].astype(int), depth[i], magnitude[i]))
    kml.write('\t\t<styleUrl>#%s</styleUrl>\n' %i)
    kml.write('\t\t<Point>\n')
    kml.write('\t\t<coordinates>%s,%s,0</coordinates>\n' % (long[i], lat[i]))
    kml.write('\t\t</Point>\n')
    kml.write('\t</Placemark>\n')

# End KML file
kml.write('</Document>/n'
          '</kml>')
kml.close()

# Create kmz file
z = zipfile.ZipFile(output+'.kmz', 'w', zipfile.ZIP_DEFLATED)
for dirname, subdirs, files in os.walk('Ballbin'):
    z.write(dirname)
    for filename in files:
        z.write(os.path.join(dirname, filename))
for dirname, subdirs, files in os.walk('Legends'):
    z.write(dirname)
    for filename in files:
        z.write(os.path.join(dirname, filename))
z.write('beachballs.kml')
z.close()

# Echo progress
print("Cleaning up...")

# Delete temporary files
shutil.rmtree('Ballbin')
shutil.rmtree('Legends')
os.remove('beachballs.kml')

# Echo progress
print("All done!")
