# -*- coding: utf-8 -*-
"""
Try using machine learning techniques on mining data

@author: Kalkberg
"""

import pandas
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn import svm as SVM
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

mines = pandas.read_csv('Mines_Geo_Metals.csv')

data=mines[['DLAT','DLONG','Detach_Dis','Dyke_Dist','Thrust_Dis','Normal_Dis',
            'SS_Dist','Fault_Dist']].values

units=list(set(mines['Orig_Label'].values))

#for i in range(len(units)-1):
#    unit=np.asarray([1 if x==True else 0 for x in mines['Orig_Label']==units[i]])
#    data=np.append(data,np.asarray(unit)[:,None],axis=1)

labels=np.asarray([1 if x=='Y' else 0 for x in mines['Gold'].values])

#labels=mines['Gold'].values
#
##labels=[1 if x else 0 for x in mines['Gold'].values]
#
## make Y=1, N=0
#for i in range(len(labels)):
#    if labels[i] == 'Y':
#        labels[i] = 1
#    else:
#        labels[i] = 0
#labels.astype('int')


##%% 

# split up data into test and train
train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size = 0.25)


# Random forest

rf = RF(n_estimators=100,criterion="entropy")

rf.fit(train_data,train_labels)
predictions = rf.predict(test_data)

c=0

for i in range(len(predictions)):
    if predictions[i]==test_labels[i]:
        c+=1
        
errors = c/len(predictions)*100

print('Random Forest Prediction is ', round(errors,3), '% accurate')

## SVM prediction
svm = SVM.SVC(kernel='rbf',C=1, gamma=10)

svm.fit(train_data,train_labels)
svmPredictions = svm.predict(test_data)

c=0

for i in range(len(svmPredictions)):
    if svmPredictions[i]==test_labels[i]:
        c+=1
        
errors = c/len(svmPredictions)*100

print('SVM Prediction is ', round(errors,3), '% accurate')

## Adaboost prediction for descision tree

bdt = AdaBoostClassifier(DecisionTreeClassifier(),
                         algorithm="SAMME",
                         n_estimators=200)
bdt.fit(train_data,train_labels)

bdtPredict = bdt.predict(test_data)

c=0

for i in range(len(bdtPredict)):
    if bdtPredict[i]==test_labels[i]:
        c+=1
        
errors = c/len(bdtPredict)*100

print('Adaboost Prediction is ', round(errors,3), '% accurate')

