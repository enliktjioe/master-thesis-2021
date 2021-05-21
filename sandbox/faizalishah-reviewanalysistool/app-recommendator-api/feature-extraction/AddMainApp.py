
# coding: utf-8

# In[11]:


import sqlite3
import logging
import sys
import json
from urllib.request import urlopen
import re
import requests
from sys import argv
from sqlite3 import Error


# In[15]:


def AddMainAppToDB(appID,userid):
    dbPath = '../AppReviewDB.db'
    try:
        conn = sqlite3.connect(dbPath)
    except Error as e:
        print(e)
    
    print('Fetching app information meta information from PlayStore!!!')
    
    AppDetails = requests.get('http://stores-api.eu-north-1.elasticbeanstalk.com/appdetails?store=1&appId=' + str(appID)).json()                                                
    
    AppInfo = (appID,AppDetails["title"],AppDetails['description'],AppDetails['score'],AppDetails['icon'],userid)

    print('App information fetched sucessfully!!!')
    
    sql = 'INSERT INTO BaseApps(appID,title,description,score,icon,UserID) VALUES(?,?,?,?,?,?)'
    cur = conn.cursor()
    try:
        cur.execute(sql,AppInfo)
        conn.commit()
        print('New base app added to database sucessfully!!!')
    except Error as e:
        print(e)
        print('Error occured while inserting a new base app to database!!!')


# In[16]:


if __name__ == '__main__':
    json_appInfo = json.loads(argv[1])
    AddMainAppToDB(json_appInfo["appID"],json_appInfo["UserID"])

