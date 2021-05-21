
# coding: utf-8

# In[4]:


import importlib
import json
from urllib.request import urlopen
import re
import requests
from unidecode import unidecode
import time
from datetime import datetime
import warnings
import sys
import pickle
import copy
import gc
import os


# In[5]:


class ReviewScrapper:
    def __init__(self,app,pages):
        self.appID = app
        self.NoOfPages = pages
    
    def CheckIfReviewNotExist(self,reviewID):
        review_exist_status= False
        exist = os.path.isfile('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json')
        if exist:
            # check if review exists in the existing file
            with open('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json') as json_file:  
                data = json.load(json_file)
                reviews = data[self.appID]
                
                for review_info in reviews:
                    if review_info["id"] == reviewID:
                        review_exist_status = True
                        break
                    
        return review_exist_status
    
    def ReadExistingReviews(self):
        exist = os.path.isfile('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json')
        reviews=[]
        
        if exist:
            with open('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json') as json_file:  
                data = json.load(json_file)
                reviews = data[self.appID]
            
        return reviews
    
    def CollectReviews(self):
        lst_reviews= self.ReadExistingReviews()
        r = requests.get('http://localhost:8081/app?id=' + self.appID + "&pages=" + self.NoOfPages)
        data= r.json()
        reviews = data['review_list']
        for review_info in reviews:
            if(self.CheckIfReviewNotExist(review_info["id"])==False):
                lst_reviews.append({'id': review_info["id"], 'title': review_info["title"],'score':review_info["score"],'date':"",'text':review_info["text"]})
        
        return lst_reviews


# In[6]:


if __name__ == '__main__':
    #Taxify 675033630
    #Uber   368677368
    #Toggle 1291898086
    #HoursTimeTracking 895933956
    #HoursTracker 336456412
    
    DS_AppReviews = {}
    
    #apps=["675033630"]
    apps=["675033630","368677368","1291898086","895933956","336456412"]
    for appID in apps:
        print(appID)
        obj_ReviewScrapper = ReviewScrapper(appID,"10")
        reviewSet = obj_ReviewScrapper.CollectReviews()
        print(len(reviewSet))
        DS_AppReviews[appID] = reviewSet
    

    exist = os.path.isfile('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json')
    
    if exist==True:
        os.remove("offline_review_dataset/review_collection_Faiz/DS_AppReviews.json")
        json = json.dumps(DS_AppReviews)
        f = open("offline_review_dataset/review_collection_Faiz/DS_AppReviews.json","w")
        f.write(json)
        f.close()
    else:
        json = json.dumps(DS_AppReviews)
        f = open("offline_review_dataset/review_collection_Faiz/DS_AppReviews.json","w")
        f.write(json)
        f.close()

