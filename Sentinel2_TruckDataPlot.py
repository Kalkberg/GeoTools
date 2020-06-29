# -*- coding: utf-8 -*-
"""
Plots data created with Sentinel 2 Truck ID code

@author: Kalkberg
"""

import pandas as pd
import seaborn as sbrn
import matplotlib.pyplot as plt

file = 'TRN.csv'

data = pd.read_csv(file)

# Create new columns for analysis
data['vehicleratio'] = data['vehiclepixels']/data['roadpixels']
data['dates'] = pd.to_datetime(data['dates'], format='%Y%m%d')
data['dayofyear'] = data['dates'].dt.dayofyear
data['dayofweek'] = data['dates'].dt.day_name()
data['dayofweek#'] = data['dates'].dt.dayofweek
data['year'] = data['dates'].dt.year 

# change dates to fiscal year
data['fday']=[x-243 if x >= 244 else 365-244+x for x in data['dayofyear']] 
data['fyear'] = data['dates'].dt.year 
data.loc[(data['dayofyear'] >= 244), 'fyear'] = data['fyear']+1

# Set up plot
fig, ax = plt.subplots(figsize=(11,8.5))
# plt.tight_layout()
plt.xlim(0,365)
ax.set_xticks([122, 153, 181, 212, 242, 273, 303, 334, 1, 31, 62, 92])
str_month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']


# plot data
ax.set_xticklabels(str_month_list)
plt.xticks(rotation=65)
ax = sbrn.scatterplot(x='fday',y='vehicleratio', data=data, hue='year')
# plt.xlim((pd.to_datetime('2019-01-01'), pd.to_datetime('2020-01-01')))
ax.legend(title='Fiscal Year')
plt.xlabel('Month')
plt.ylabel('vehicle pixels / road pixels')
plt.title('Ruhr')
plt.savefig(file[:-4]+'.pdf')