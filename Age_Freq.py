# -*- coding: utf-8 -*-
"""
Generates a plot of probabilities for age distributions given min and max ages
    
Input data in csv format:
    Ages - List of points with fields: MinAge, MaxAge
    AgeMin - Minmum age to consider
    AgeMax - Maximum age to consider
    AgeInt - Bin size for plotting
    Iterations - Number of times to iterate to generate distributions
    Dist - Distribution to use for age inputs. Uniform or Gaussian. 
            Defaults to Gaussian.
    Output - Stem of name for output data
        
    
Output:
    Output.png - Number of points in polygon n over time

@author: Kalkberg
"""
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import multiprocessing

# Check available cores, leave one for OS
NumCores = multiprocessing.cpu_count()-1

# Inputs
PointsFile = 'NAM_Volc_Min_Max_Cleaned.csv'
AgeMin = 0
AgeMax = 66
AgeInt = 1
Iterations = 10**3
#AgeInt = float(input('Age Int: '))
Dist = 'Normal'
#Dist = input('Age Data PDF type: ')
Output = 'NAM_Volc_'
#Output = input('File Root Name: ')

# Read in data, cut out headers and redistribute to variables
Points = np.genfromtxt(PointsFile, delimiter=',')
Points = np.delete(Points, (0), axis=0)
PointAgeMin, PointAgeMax = Points[:,0], Points[:,1], \

# Catch instances where Min and Max are reversed, then swap
for i in range(len(PointAgeMin)):
    if PointAgeMin[i] > PointAgeMax[i]:
        a = PointAgeMax[i]
        PointAgeMax[i] = PointAgeMin[i]
        PointAgeMin[i] = a

# Create list of age bins
AgeBins = np.linspace(AgeMin,AgeMax,int((AgeMax/AgeInt)+1))
AgeBinsPlot = np.linspace(AgeMin,AgeMax-AgeInt,int(AgeMax/AgeInt))

#Add Mins and Maxes to the same numpy array for iteration
PointList = np.array([PointAgeMin,PointAgeMax])

# Randomly generate ages of each sample, given age constraints
# Repeat 10^5 times to get good PDFs in each bin
def RandomAge(PointList,AgeBins):
        AgeRand = np.zeros([len(PointList[0])]) # Set list of generated ages to zero
        AgeRandBins = np.zeros([len(AgeBins)-1,len(PointList[0])]) # Array of ages in each bin
        AgeRandDistOut = np.zeros(len(AgeBins)-1) # Array of age counts internal to loop
        for n in range(len(PointList[0])): #for each point
            # Catch instances where min and max age are the same
            if (PointList[0][n]) != (PointList[1][n]):    
                # Randomly generate numbers for each age interval
                if Dist == 'Uniform':
                    Age = np.random.uniform(PointList[0][n],
                                            PointList[1][n])
                else:
                # Assumes ages are reported on 2 sigma level and are symmetric.
                    Age = np.random.normal(
                        np.mean([PointList[0][n],
                                 PointList[1][n]]),
                        abs((PointList[0][n] - 
                             np.mean([PointList[0][n],
                                      PointList[1][n]]))/2))                      
            else:
                Age = PointList[0][n] # Set age to same as min val
            
            AgeRand[n] = Age # Append to list of generated ages
                       
        # Count number of ages in each bin
        for p in range(len(AgeBins)-1):
            for n in range(len(AgeRand)): 
                if (AgeRand[n] > AgeBins[p]) and (AgeRand[n] < AgeBins[p+1]):
                    AgeRandBins[p][n] = 1
            AgeRandDistOut[p] =  np.sum(AgeRandBins[p]) # Count ages in each bin and append to list
        
        return AgeRandDistOut,

# Run above function in paralell
#AgeRandDist  = Parallel(n_jobs=NumCores, verbose=100)(delayed(RandomAge)(PointList,AgeBins) for i in range(Iterations))
AgeRandDist  = Parallel(n_jobs=NumCores, verbose=100, backend='threading')(delayed(RandomAge)(PointList,AgeBins) for i in range(Iterations))
AgeRandDist = np.squeeze(AgeRandDist)

# Set stat lists to zero
Median = []
Mean = []
Pctile5 = []
Pctile95 = []
# Count statistics of each age bin
for q in range(len(AgeRandDist[0])):
    Median.append(np.median(AgeRandDist[:,q]))
    Mean.append(np.mean(AgeRandDist[:,q]))
    Pctile5.append(np.percentile(AgeRandDist[:,q],2.5))
    Pctile95.append(np.percentile(AgeRandDist[:,q],97.5))

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
plt.title('Age Frequency')
plt.savefig(Output+'.png',dpi=300)
plt.close()                                  
