# -*- coding: utf-8 -*-

# Create your models here.
import pickle
import numpy as np 
import pandas as pd 
import os
#print(os.listdir("C:/Users/Admin/Desktop/ML"))
import warnings
warnings.filterwarnings('ignore')
# read file
voice=pd.read_csv('voice2.csv')
voice.head()
voice.info()
voice.describe()
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
voice["label"] = le.fit_transform(voice["label"])
le.classes_

voice[:]=preprocessing.MinMaxScaler().fit_transform(voice)
voice.head()
import seaborn as sns
import matplotlib.pyplot as plt
plt.subplots(4,5,figsize=(15,15))
for i in range(1,5):
        plt.subplot(4,5,i)
        plt.title(voice.columns[i-1])
        sns.kdeplot(voice.loc[voice['label'] == 0, voice.columns[i-1]], color= 'green', label='F')
        sns.kdeplot(voice.loc[voice['label'] == 1, voice.columns[i-1]], color= 'blue', label='M')
plt.show()

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


import xgboost
train = pd.read_csv('voice2.csv')
x_train = train[["meanfreq","sd","meanfun","minfun","maxfun"]]
y_train = train["label"]



def classify(model,x_train,y_train):
    from sklearn.metrics import classification_report
    # target_names = ['female', 'male']
    model.fit(x_train,y_train)

    #y_pred=model.predict(x_test)
    #print (y_pred)
    #print(classification_report(y_test, y_pred, target_names=target_names, digits=4))

model = xgboost.XGBClassifier()
classify(model,x_train,y_train)

pickle.dump(model, open('model.pkl', 'wb'))
model = pickle.load(open('model.pkl', 'rb'))
