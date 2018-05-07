# -*- coding: utf-8 -*-
"""
Creates an animation of point data on a map, animated by time. Has
a colored legend to differentiate points for a different field.

Made and currently set to plot volcanic data from Tibet.

@author: Kalkberg
"""

# Import needed packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
import math
from moviepy.editor import *
import os

# Input paramaters
data = 'Tibet_Chapman_Type.csv'
output = 'Tibet_Igneous4'
age_min = 0
age_max = 110
step = 8 # Frames per Myr
fps_mov = 16 # Fps of final video
tstart = 1 # Controlls how early to add points
tend = 3 # Controlls how long to keep points

# Read in data, cut out headers and redistribute
data = np.genfromtxt(data, delimiter=',')
data = np.delete(data, (0), axis=0)
age_in, lat_in, long_in, MgO_in, Type_in = \
    data[:,0], data[:,1], data[:,2], data[:,3], data[:,4]


# Create blank arrays to populate later
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
        Type = np.r_[Type, Type_in[i]]


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


# Convert data to projection coordinates
x, y = m(long, lat)

## Set up stuff to plot during animation
#kpoints, = m.plot([],[],marker='o',color='k', linestyle='none', markersize=3, label='MgO > 6')
#gpoints, = m.plot([],[],marker='o',color='grey', linestyle='none', markersize=3, label='MgO < 6')
#emptypoints, = m.plot([],[],marker='o', linestyle='none',markeredgewidth=0.5, 
#                      markerfacecolor='none', markeredgecolor='k', 
#                      markersize=3, label='No Data')
#time_text = ax.text(0.025, 0.035, '', 
#                    transform=ax.transAxes, backgroundcolor='w')
#legend = plt.legend()

## Function to create frame for the animation
#def init():
#    kpoints.set_data([],[])
#    gpoints.set_data([],[])
#    emptypoints.set_data([],[])
#    time_text.set_text('')
#    legend = plt.legend()
#    return kpoints, gpoints, emptypoints, time_text, legend
#
## Function to plot data for each frame. i is the number of the frame
#def animate(i):
#    age_int = (int(age.max())-i/p)
#    # Plot as dot within tstart of eruption, keep for tend after
#    # Plot MgO>6 as black, MgO<6 as gray, no data as open circles
#    xk = [x[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and MgO[j]>6)]
#    yk = [y[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and MgO[j]>6)]
#    xg = [x[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and MgO[j]<6)]
#    yg = [y[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and MgO[j]<6)]
#    xempty = [x[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and math.isnan(MgO[j]))]
#    yempty = [y[j] for j in range(0,len(age)) \
#        if (age[j] < age_int + tend and age[j] > age_int + tstart
#            and math.isnan(MgO[j]))]
#    kpoints.set_data(xk,yk)
#    gpoints.set_data(xg,yg)
#    emptypoints.set_data(xempty,yempty)
#    time_text.set_text('Age = %s Ma' %int(age_int))
#    legend = plt.legend()
#    return kpoints, gpoints, emptypoints, legend
#
##Animate the figure
#anim = animation.FuncAnimation(fig, animate, init_func=init, 
#                               frames=int(age.max())*p, interval=20,
#                               blit=True)
#kwargs={'bbox_inches':'tight'}
#anim.save(output+'.mp4', fps=10, dpi=300,
#          extra_args=['-vcodec', 'libx264'])
#anim.save(output+'.gif', writer='imagemagick', fps=30, dpi=100)

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
               
    # Make Plot
    # Plot as dot within tstart of eruption, keep for tend after
    # Plot extrusive MgO>6 as black, MgO<6 as gray, no data as open triangles
    # Plot intrusive as circles
    xk = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and MgO[j]>6 and Type[j]==1)]
    yk = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and MgO[j]>6 and Type[j]==1)]
    xg = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and MgO[j]<6 and Type[j]==1)]
    yg = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and MgO[j]<6 and Type[j]==1)]
    xempty = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and math.isnan(MgO[j]) and Type[j]==1)]
    yempty = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and math.isnan(MgO[j]) and Type[j]==1)]
    xcircle = [x[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and Type[j]==0)]
    ycircle = [y[j] for j in range(0,len(age)) \
        if (age[j] < age_int + tend and age[j] > age_int + tstart
            and Type[j]==0)]  
    kpoints = m.plot(xk,yk,marker='^',color='k', linestyle='none', 
                     markersize=3, label='Volc. MgO>6')
    gpoints = m.plot(xg,yg,marker='^',color='grey', linestyle='none', 
                     markersize=3, label='Volc. MgO<6')
    emptypoints = m.plot(xempty,yempty,marker='^', linestyle='none',
                         markeredgewidth=0.5, markerfacecolor='none', 
                         markeredgecolor='k', 
                         markersize=4, label='Volc. No MgO Data')
    circlepoints = m.plot(xcircle,ycircle,marker='o', linestyle='none',
                         markeredgewidth=0.5, markerfacecolor='none', 
                         markeredgecolor='k', 
                         markersize=4, label='Plutonic')
    
    

    # Make text box, legend, and neaten things up
    time_text = ax.text(0.035, 0.035, 'Age = %s Ma' %int(age_int), 
                    transform=ax.transAxes, backgroundcolor='w')
    legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -.05),
          ncol=2, fancybox=True, fontsize=9)
    plt.tight_layout()
                                         
    # Save plot to name padded to five digits and save everything
    fig.savefig('Frame'+str(i).zfill(5)+'.png', dpi=300)
    
    # Add to list of frames
    frames.insert(len(frames),'Frame'+str(i).zfill(5)+'.png')  
    
    # Delete plot
    plt.cla()

animation = ImageSequenceClip(frames, fps = fps_mov)
animation.write_videofile('%s.mp4' %output)
#animation.write_gif('%s.gif' %output) 
    
# Clean up
for j in range(0,len(frames)):
    os.remove(frames[j])
          
print("All done!")