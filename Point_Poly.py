# -*- coding: utf-8 -*-
"""
Generates a plot of probabilities of point density in a polygon:
    
Input data in csv format:
    PointsFile - List of points with fields: MinAge, MaxAge, Lat, Long
    PolysFile - List of polygons with fields: PolygonNumber, Lat, Long
        Note: Polygon number should be from 0 to n
    PolysName - List of polygon names to associate with numbers
    AgeMin - Minmum age to consider
    AgeMax - Maximum age to consider
    AgeInt - Bin size for plotting
    Dist - Distribution to use for age inputs. Uniform or Gaussian. 
            Defaults to Normal.
    Output - Stem of name for output data
        
    
Output:
    Output+PolysName.png - Number of points in polygon n over time
    FigB - All figures A on a single plot

@author: Kalkberg
"""
#def Point_Poly(AgeMin,AgeMax,AgeInt,Dist,Output):

import numpy as np
import matplotlib.path as path
import matplotlib.pyplot as plt
from tqdm import trange

# Inputs
PointsFile = 'NAM_Volc_Min_Max_Cleaned.csv'
PolysFile = 'Polys.csv'
PolysName = ('Mojave','NV','NVID','NVUT','ORID','ORNV')
AgeMin = 0
AgeMax = 36
#AgeInt = 1
AgeInt = float(input('Age Int: '))
#Dist = 'Normal'
Dist = input('Age Data PDF type: ')
#Output = 'Gaussian_'
Output = input('File Root Name: ')

# Read in data, cut out headers and redistribute to variables
Points = np.genfromtxt(PointsFile, delimiter=',')
Points = np.delete(Points, (0), axis=0)
PointAgeMin, PointAgeMax, PointLat, PointLong = Points[:,0], Points[:,1], \
                                          Points[:,2], Points[:,3]
Polys = np.genfromtxt(PolysFile, delimiter=',')
Polys = np.delete(Polys, (0), axis=0)
PolyNo, PolyLat, PolyLong = Polys[:,0], Polys[:,1], Polys[:,2]

# Create empty list of points in each polygon
# Columns for each polygon are n=AgeMin, n+1=AgeMax, n+2=Lat, n+3=Long
PointList = []

# Catch instances where Min and Max are reversed, then swap
for i in range(len(PointAgeMin)):
    if PointAgeMin[i] > PointAgeMax[i]:
        a = PointAgeMax[i]
        PointAgeMax[i] = PointAgeMin[i]
        PointAgeMin[i] = a


# Create list of age bins
AgeBins = np.linspace(AgeMin,AgeMax,(AgeMax/AgeInt)+1)
AgeBinsPlot = np.linspace(AgeMin,AgeMax-AgeInt,(AgeMax/AgeInt))

# Append points to an array of data for each polygon
for i in range(0,int(PolyNo.max())):
    Polygon = np.zeros([0,2]) # Empty polygon for next step
    # Create array defining polygon
    for j in range(0, len(PolyNo)):
        if PolyNo[j] == i:
            Polygon = np.append(Polygon,[[PolyLong[j],PolyLat[j]]],axis=0)
    
    PolyPath = path.Path(Polygon) # Create path using matplotlib.path
    PointAgeMinPoly = [] # Empty list of points in a set polygon
    PointAgeMaxPoly = []
    PointLatPoly = []
    PointLongPoly = []
    
    # Check if points are in the polygon, if so append to list, can also be done as list comprehension
    for k in range(0,len(PointLat)-1):
        if PolyPath.contains_point((PointLong[k],PointLat[k])) == True:
            PointAgeMinPoly.append(PointAgeMin[k])
            PointAgeMaxPoly.append(PointAgeMax[k])
            PointLatPoly.append(PointLat[k])
            PointLongPoly.append(PointLong[k])
    
    # Append to master list of data for each polygon
    PointList.extend([PointAgeMinPoly,PointAgeMaxPoly, \
                      PointLatPoly,PointLongPoly]) 

# Make plots of sample numbers for each plot
for m in range(0,int(PolyNo.max())):
    
    AgeRandDist = [[] for i in range(len(AgeBins)-1)]# Create empty list of age counts
    
    # Randomly generate ages of each sample, given age constrains
    # Repeat 10^5 times to get good PDFs in each bin
    for _ in trange(10**5,desc='Processing '+PolysName[m]): 
        AgeRand = [] # Set list of generated ages to zero
        AgeRandBins = [[]for i in range(len(AgeBins)-1)] # List of ages in each bin
        for n in range(0,len(PointList[m*4])): #for each point found in the polygon
            # Catch instances where min and max age are the same
            if (PointList[m*4][n]) != (PointList[m*4+1][n]):    
                # Randomly generate numbers for each age interval
                if Dist == 'Uniform':
                    Age = np.random.uniform(PointList[m*4][n],
                                            PointList[m*4+1][n])
                    Age = Age.tolist() # Returns an array, needs to be a list
                else:
                # Assumes ages are reported on 2 sigma level and are symmetric.
                    Age = [np.random.normal(
                        np.mean([PointList[m*4][n],
                                 PointList[m*4+1][n]]),
                        (PointList[m*4+1][n] - 
                             np.mean([PointList[m*4][n],
                                      PointList[m*4+1][n]]))/2)]                      
            else:
                Age = [PointList[m*4][n]] # Set age to same as min val
            
            AgeRand.append(Age) # Append to list of generated ages
                       
        # Count number of ages in each bin
        for p in range(0,len(AgeBins)-1):
            for n in range(0,len(AgeRand)): 
                if (AgeRand[n] > AgeBins[p]) and (AgeRand[n] < AgeBins[p+1]):
                    AgeRandBins[p].extend(AgeRand[n])
            AgeRandDist[p].append(len(AgeRandBins[p])) # Count ages in each bin and append to list
    
    # Set stat lists to zero
    Median = []
    Mean = []
    Pctile5 = []
    Pctile95 = []
    # Count statistics of each age bin
    for q in range(0,len(AgeRandDist)):
        Median.append(np.median(AgeRandDist[q]))
        Mean.append(np.mean(AgeRandDist[q]))
        Pctile5.append(np.percentile(AgeRandDist[q],2.5))
        Pctile95.append(np.percentile(AgeRandDist[q],97.5))
    
    # Plot Results
    f = plt.figure()
    plt.plot(AgeBinsPlot,Median,'r',label='Median')
    plt.plot(AgeBinsPlot,Mean,'b',label='Mean')
    plt.plot(AgeBinsPlot,Pctile5,'0.8', label='95% of samples')
    plt.plot(AgeBinsPlot,Pctile95,'0.8')
    plt.legend()
    plt.xlabel('Age (Ma)')
    plt.ylabel('Counts')
    plt.xlim([AgeMin,AgeMax-AgeInt])
    plt.title(PolysName[m])
    plt.savefig(Output+PolysName[m]+'.png',dpi=300)
    plt.close()                                  
