# -*- coding: utf-8 -*-
"""
Plot OMI data

@author: Kalkberg
"""
import pandas as pd
import seaborn as sbrn
import matplotlib.pyplot as plt

NO2 = pd.read_csv('OMI_Data.csv')
NO2['date']=pd.to_datetime(NO2['date'])
NO2['dayofyear']=NO2['date'].dt.dayofyear
NO2['fday']=[x-243 if x >= 244 else 365-244+x for x in NO2['dayofyear']] # day of fiscal year starting in September

# update fiscal year
NO2['fyear'] = NO2['date'].dt.year 
NO2.loc[(NO2['dayofyear'] >= 244), 'fyear'] = NO2['fyear']+1


# Set up plot
fig, ax = plt.subplots(figsize=(11,8.5))
# plt.tight_layout()
plt.xlim(0,365)
ax.set_xticks([122, 153, 181, 212, 242, 273, 303, 334, 1, 31, 62, 92])
str_month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']



ax.set_xticklabels(str_month_list)
plt.xticks(rotation=65)
ax = sbrn.lineplot(x='fday',y='location', data=NO2, hue='fyear')
ax.legend(title='Fiscal Year')
plt.xlabel('Month')
plt.ylabel('NO2')
plt.title('location')
plt.savefig('location.pdf')