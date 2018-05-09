# -*- coding: utf-8 -*-
"""
Creates an animation of point data on a map, animated by time. Has
a colored legend to differentiate points based on a field. Colors are set to
fade over time.

Made and currently set to plot volcanic data from Tibet.

@author: Kalkberg
"""

# Import needed packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
from matplotlib.lines import Line2D
from mpl_toolkits.basemap import Basemap
import math
from moviepy.editor import *
import os

# Input paramaters
data = 'Tibet_Chapman_Type.csv' # Data source
output = 'Tibet_Igneous6' # File name of output
age_min = 0 # Minimum age to plot
age_max = 110 # Maximum age to plot
step = 8 # Frames per Myr
fps_mov = 16 # Fps of final video
fade_time = 5 # Number of Myr over which to fade symbols
fade_steps = step*fade_time # Number of colors to use in fading symbols
fade_time_step = 1/step # Calculate time intervals for symbol fade
# Note: Video works best when 1/step=fade_time_step, but all can be set manually
tstart = 1 # Controlls how early to add points

# Read in data, cut out headers and redistribute
data = np.genfromtxt(data, delimiter=',')
data = np.delete(data, (0), axis=0)
age_in, lat_in, long_in, MgO_in = data[:,0], data[:,1], data[:,2], data[:,3]

# Create blank arrays
age = np.array([])
lat = np.array([])
long = np.array([])
MgO = np.array([])
Type = np.array([])

# Cut data outside time of interest
for i in range(len(age_in)):
    if (age_in[i] > age_min and age_in[i] < age_max):
        age = np.r_[age, age_in[i]]
        lat = np.r_[lat, lat_in[i]]
        long = np.r_[long, long_in[i]]
        MgO = np.r_[MgO, MgO_in[i]]

# Set up figure and background
fig = plt.figure(dpi=300, figsize=(4.2,3.7)) #Adjust size to area of interest
fig.set_canvas(plt.gcf().canvas)
ax = fig.add_subplot(111)
m = Basemap(width=1500000,height=1500000,
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',area_thresh=1000.,projection='lcc',\
            lat_1=22.,lat_2=42,lat_0=33,lon_0=87.)
m.drawcountries(linewidth=0.5, linestyle='solid', color='0')
m.drawstates(linewidth=0.5, linestyle='solid', color='0')
m.shadedrelief()
m.drawparallels(np.arange(28.,40.,4.), linewidth=.75, 
                labels=[1, 1, 0, 0], color='0')
m.drawmeridians(np.arange(78.,96.,4.), linewidth=.75, 
                labels=[0, 0, 0, 1], color='0')
#blues = plt.get_cmap('Blues_r')
#reds = plt.get_cmap('Reds_r')
#greys = plt.get_cmap('Greys_r')
legend_elements = [Line2D([0], [0], marker='o', color='b', label='MgO>6',
                          markerfacecolor='b', markersize=3, linestyle='none'),
                    Line2D([0], [0], marker='o', color='r', label='MgO<6',
                          markerfacecolor='r', markersize=3, linestyle='none'),
                    Line2D([0], [0], marker='o', color='k', label='No Data',
                          markerfacecolor='none', markersize=4, linestyle='none')]

# Convert data to projection coordinates
x, y = m(long, lat)

# Create empty list of frames
frames = []

for i in range(0,age_max*step,1):   
    
    # Counter for age instance to make sure you go from old to young    
    age_int = (age_max-i/step)
         
    # Redraw the base map
    m = Basemap(width=1500000,height=1500000,
                rsphere=(6378137.00,6356752.3142),\
                resolution='i',area_thresh=1000.,projection='lcc',\
                lat_1=22.,lat_2=42,lat_0=33,lon_0=87.)
    m.drawcountries(linewidth=0.5, linestyle='solid', color='0')
    m.drawstates(linewidth=0.5, linestyle='solid', color='0')
    m.shadedrelief()
    m.drawparallels(np.arange(28.,40.,4.), linewidth=.75, 
                    labels=[1, 1, 0, 0], color='0')
    m.drawmeridians(np.arange(78.,96.,4.), linewidth=.75, 
                    labels=[0, 0, 0, 1], color='0')   
    plt.title('Tibet Igneous Activity')
               
    # Make Plots
    # Plot MgO>6 as reds, MgO<6 as blues, no data as open circles
    # Fade color over fade_time interval
    for k in range(fade_steps):
  
        # Make lists of points in required age and MgO ranges
        xb = [x[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and MgO[j]>6)]
        yb = [y[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and MgO[j]>6)]
        xr = [x[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and MgO[j]<6)]
        yr = [y[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and MgO[j]<6)]
        xk = [x[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and math.isnan(MgO[j]))]
        yk = [y[j] for j in range(0,len(age)) \
            if (age[j] < age_int + k*fade_time_step and 
                age[j] > age_int + (k-1)*fade_time_step and math.isnan(MgO[j]))]
            
        # Plot points for time and color slice after catching empty lists
#        if len(xb)>0:
#            bpoints = m.scatter(xb, yb, marker='o', 
#                                facecolor=blues(k/fade_steps), s=3)
#        if len(xr)>0:
#            rpoints = m.scatter(xr, yr, marker='o',
#                                facecolor=reds(k/fade_steps), s=3)
#        if len(xk)>0:
#            kpoints = m.scatter(xk,yk,marker='o',s=4,
#                                facecolor='none', lw=0.5, 
#                                edgecolor=greys(k/fade_steps))
        #When alpha=0, symbol is clear, when alpha=1 symbol is solid
        #Alpha controlled by time since eruption
        if len(xb)>0:
            bpoints = m.scatter(xb, yb, marker='o', color='b', 
                                alpha=1-(k/fade_steps), s=3)
        if len(xr)>0:
            rpoints = m.scatter(xr, yr, marker='o', color='r',
                                alpha=1-(k/fade_steps), s=3)
        kcolor = colors.colorConverter.to_rgba('k', alpha=1-(k/fade_steps))
        if len(xk)>0:
            kpoints = m.scatter(xk,yk,marker='o',s=4,
                                facecolor='none', lw=0.5, 
                                edgecolor=kcolor)

    # Make text box, legend, and neaten things up
    time_text = ax.text(0.035, 0.035, 'Age = %s Ma' %int(age_int), 
                    transform=ax.transAxes, backgroundcolor='w')
#    legend = plt.legend(handles=legend_elements, loc='upper center', 
#                        bbox_to_anchor=(0.5, -.05),ncol=3, fancybox=True,
#                        fontsize=9)
    legend = plt.legend(handles=legend_elements, loc='upper left', 
                        fancybox=True, fontsize=9)
    plt.tight_layout()
                                         
    # Save plot to name padded to five digits and save everything
    fig.savefig('Frame'+str(i).zfill(5)+'.png', dpi=300)
    
    # Add to list of frames
    frames.insert(len(frames),'Frame'+str(i).zfill(5)+'.png')  
    
    # Delete plot
    plt.cla()

animation = ImageSequenceClip(frames, fps = fps_mov)
animation.write_videofile('%s.mp4' %output)
    
# Clean up
for j in range(0,len(frames)):
    os.remove(frames[j])
          
print("All done!")