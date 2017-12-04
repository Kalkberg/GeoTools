# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 11:29:59 2017

Script to plot Lat Long data over a time interval.

Made and currently set to plot volcanic data from Tibet.

@author: Kalkberg
"""

# Import needed packages
import numpy as np
import matplotlib.pyplot as plt
#import sys
import os
#import shutil
#import subprocess
from mpl_toolkits.basemap import Basemap
from moviepy.editor import *


## Create function describing usage and terminating program for errors
#def error():
#    print("Usage: python3 Plot_Anim.py working_dir data.csv Output")
#    print("Where working_dir is the full path to the data")
#    print("e.g. C:/users/animation")
#    print("data.csv contains comma delimited files of age, lat, and long")
#    print("Output is the name of the pdf map to generate from data")
#    sys.exit()
#
## Check number of arguments and import, if not three, return error
#if len(sys.argv) == 4:
#    # Import directory to work on and satellite type from input arguments
#    workdir = sys.argv[1]
#    data = sys.argv[2]
#    output = sys.argv[3]
#    print("Current working directory is set to %s" % workdir)
#    print("Data file set to %s" % data)
#    print("Output file set to %s" % output)
#else:
#    print("Error: Wrong number of input arguments!")
#    error()
#    
#

#Input paramaters for debuging
data = 'Tibet_Chapman_MgO.csv'
output = 'Tibet_Chapman_MgO'
workdir = 'D:/GitHub/Learning/'
lat_min = 27
lat_max = 38
long_min = 76
long_max = 100
age_min_cut = 0
age_max_cut = 145
hexsize = (25, 20)
step = 1 # Frames per Myr
plt_int = 4 # 0.5 x Myr of data to count for each cell
min_dens = 0
max_dens = 20 # Defines maximum density expected in dataset
fps_mov = 2 # Fps of final video

# Move to working directory
os.chdir(workdir)

# Read in data, cut out headers and redistribute
data = np.genfromtxt(data, delimiter=',')
data = np.delete(data, (0), axis=0)
age_min_in, age_max_in, lat_in, long_in, val_in = data[:,0], data[:,1], data[:,2], data[:,3], data[:,4]


# Create blank arrays for later use
age_min = np.array([])
age_max = np.array([])
lat = np.array([])
long = np.array([])
val = np.array([])

# Cut data outside region and time of interest so hexplot polygons are same size
for i in range(0,len(age_max_in)):
    if (age_min_in[i] > age_min_cut and age_max_in[i] < age_max_cut and 
    lat_in[i] > lat_min and lat_in[i] < lat_max and
    long_in[i] > long_min and long_in[i] < long_max):
        age_min = np.r_[age_min, age_min_in[i]]
        age_max = np.r_[age_max, age_max_in[i]]
        lat = np.r_[lat, lat_in[i]]
        long = np.r_[long, long_in[i]]
        val = np.r_[val, val_in[i]]

# Set up figure and projection
fig = plt.figure()
fig.set_canvas(plt.gcf().canvas)
ax = fig.add_subplot(111)
ax.autoscale(enable=False)
m = Basemap(width=1500000,height=1500000,
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',area_thresh=1000.,projection='lcc',\
            lat_1=22.,lat_2=42,lat_0=33,lon_0=87.)

# Convert data to projection coordinates and make into array for hexbin
x, y = m(long, lat)
x = np.array(x)
y = np.array(y)

# Create empty list of frames
frames = []

for i in range(0,int(age_max.max())*step,1):   
    
    # Counter for age instance to make sure you go from old to young    
    age_int = (int(age_max.max())-i/step)
         
    #Redraw the base map
    m = Basemap(width=1500000,height=1500000,
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',area_thresh=1000.,projection='lcc',\
            lat_1=22.,lat_2=42,lat_0=33,lon_0=87.)
    m.shadedrelief()
    m.drawcoastlines(linewidth=0.5, color='0.8')
    m.drawcountries(linewidth=0.5, linestyle='solid', color='0.8')
    m.drawparallels(np.arange(28.,40.,4.), linewidth=.75, 
                    labels=[1, 0, 0, 0], color='0')
    m.drawmeridians(np.arange(78.,96.,4.), linewidth=.75, 
                    labels=[0, 0, 0, 1], color='0')
    plt.title('Western US Igneous Activity')
    
    # Collect data for this time interval
    x_plot = np.array([x[j] for j in range(0,len(age_max)) \
        if ((age_max[j] >= age_int - plt_int and age_min[j] <= age_int - plt_int)
            or (age_max[j] >= age_int + plt_int and age_min[j] <= age_int + plt_int))])
    y_plot = np.array([y[j] for j in range(0,len(age_max)) \
        if ((age_max[j] >= age_int - plt_int and age_min[j] <= age_int - plt_int)
            or (age_max[j] >= age_int + plt_int and age_min[j] <= age_int + plt_int))])
    val_plot = np.array([val[j] for j in range(0,len(age_max)) \
        if ((age_max[j] >= age_int - plt_int and age_min[j] <= age_int - plt_int)
            or (age_max[j] >= age_int + plt_int and age_min[j] <= age_int + plt_int))])
     
    # Get axis limits from basemap plot
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Make Plot
    hb_plot = m.hexbin(x_plot,y_plot, gridsize=hexsize, linewidths=0.2, 
                extent=(xlim[0],xlim[1],ylim[0],ylim[1]), mincnt=1,
                vmin=min_dens, vmax=max_dens, cmap='viridis',
                reduce_C_function=np.median, C=val_plot, zorder=3
                )
   
    # Make color bar
    cb = fig.colorbar(hb_plot, ax=ax)
#    cb.set_label('Median Δ Alkalinity')
    cb.set_label('Median MgO')
     
    # Make text box
    time_text = ax.text(0.035, 0.035, 'Age = %s Ma' %int(age_int), 
                    transform=ax.transAxes, backgroundcolor='w')
                                      
    # Save plot to name padded to five digits and save everything
    fig.savefig('Frame'+str(i).zfill(5)+'.png', dpi=300)
    
    # Add to list of frames
    frames.insert(len(frames),'Frame'+str(i).zfill(5)+'.png')  
    
    # Delete hexplot and color bar   
    plt.cla()
    cb.remove()


animation = ImageSequenceClip(frames, fps = fps_mov)
animation.write_videofile('%s.mp4' %output)
#animation.write_gif('%s.gif' %output) 
    
# Clean up
for j in range(0,len(frames)):
    os.remove(frames[j])
          
print("All done!")
