# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 11:29:59 2017

Script to plot Lat Long data over a time interval.

Made and currently set to plot volcanic data from North America.

@author: Kalkberg
"""

# Import needed packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
#import sys
#import os

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
## Move to working directory
#os.chdir(workdir)
#
# Input paramaters
data = 'NAM_Ig3.csv'
output = 'NAM_Ig5'

# Read in data, cut out headers and redistribute
data = np.genfromtxt(data, delimiter=',')
data = np.delete(data, (0), axis=0)
age, lat, long = data[:,0], data[:,1], data[:,2]

# Dummy Data
#size = 300
#lat = np.random.uniform(34,48,size)
#long = np.random.uniform(-117,-124,size)
#age = np.random.uniform(1,100,size)


# Parameters that affect animation
p = 6 # Controlls length of animation
tred = 1 # Controlls how long to keep red dots
tblack = 10 # Controlls how long to keep black dots

# Set up figure and background
fig = plt.figure(dpi=300, figsize=(3.7,3.8)) #Adjust size to area of interest
fig.set_canvas(plt.gcf().canvas)
ax = fig.add_subplot(111)
#ax.set_xlim([long.min() - 0.1*long.min(), long.max() + 0.1*long.max()])
#ax.set_ylim([lat.min() - 0.1*lat.min(), lat.max() + 0.1*lat.max()])
ax.set_xlim([-128,-101])
ax.set_ylim([29,50])
#m = Basemap(width=2300000,height=2400000,
#            rsphere=(6378137.00,6356752.3142),\
#            resolution='i',area_thresh=1000.,projection='lcc',\
#            lat_1=35.,lat_2=45,lat_0=40,lon_0=-113.)
m = Basemap(projection='merc',llcrnrlat=29,urcrnrlat=50,\
            llcrnrlon=-125,urcrnrlon=-101,lat_ts=40,resolution='i')
#m = Basemap(projection='merc',
#            llcrnrlat=(lat.min() - 0.1*lat.min()),
#            urcrnrlat=(lat.max() + 0.1*lat.max()),
#            llcrnrlon=(long.min() - 0.1*long.min()),
#            urcrnrlon=(lat.max() + 0.1*lat.max()),
#            lat_ts=lat.mean(),resolution='l')
m.drawcoastlines(linewidth=0.5, color='0.8')
m.drawcountries(linewidth=0.5, linestyle='solid', color='0.8')
m.drawstates(linewidth=0.5, linestyle='solid', color='0.8')
m.drawparallels(np.arange(35.,46.,10.), linewidth=.75, 
                labels=[1, 1, 0, 0], color='0.8')
m.drawmeridians(np.arange(-125.,105.,10.), linewidth=.75, 
                labels=[0, 0, 0, 1], color='0.8')
m.drawmapboundary(fill_color='white', color='0.8')
plt.title('Western US Igneous Activity')
plt.tight_layout()

# Convert data to projection coordinates
x, y = m(long, lat)

# Set up stuff to plot during animation
rpoints, = m.plot([],[],marker='o',color='r', linestyle='none', markersize=3)
kpoints, = m.plot([],[],marker='o',color='k', linestyle='none', markersize=1)
time_text = ax.text(0.025, 0.035, '', 
                    transform=ax.transAxes, backgroundcolor='w')

# Function to create frame for the animation
def init():
    rpoints.set_data([],[])
    kpoints.set_data([],[])
    time_text.set_text('')
    return rpoints, kpoints, time_text,

# Function to plot data for each frame. i is the number of the frame
def animate(i):
    age_int = (int(age.max())-i/p)
    # Plot as red dot within 1 Ma of eruption, keep as black dot for 10 Ma after
    xr = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tred and age[j] > age_int)]
    yr = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tred and age[j] > age_int)]
    xk = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tblack and age[j] > age_int)]
    yk = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tblack and age[j] > age_int)]
    rpoints.set_data(xr,yr)
    kpoints.set_data(xk,yk)
    time_text.set_text('Age = %s Ma' %int(age_int))
    return rpoints, kpoints,

#Animate the figure
anim = animation.FuncAnimation(fig, animate, init_func=init, 
                               frames=int(age.max())*p, interval=20,
                               blit=True)
#kwargs={'bbox_inches':'tight'}
anim.save(output+'.mp4', fps=30, dpi=300,
          extra_args=['-vcodec', 'libx264'])
anim.save(output+'.gif', writer='imagemagick', fps=30, dpi=100)

print("All done!")
