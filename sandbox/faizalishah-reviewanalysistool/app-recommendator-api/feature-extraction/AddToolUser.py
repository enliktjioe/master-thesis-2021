
# coding: utf-8

# In[2]:


import sqlite3
import logging
import sys
import json
from sys import argv
from sqlite3 import Error


# In[ ]:


def AddUserToDB(userid,password):
    dbPath = '../AppReviewDB.db'
    try:
        conn = sqlite3.connect(dbPath)
    except Error as e:
        print(e)
    
    UserInfo = (userid,password)
    
    sql = 'INSERT INTO Users(UserID,Password) VALUES(?,?)'
    cur = conn.cursor()
    try:
        cur.execute(sql,UserInfo)
        conn.commit()
        print('New user added to database sucessfully!!!')
    except Error as e:
        print('Error occured while inserting a new user to database!!!')


# In[1]:


if __name__ == '__main__':
    json_userInfo = json.loads(argv[1])
    AddUserToDB(json_userInfo["UserID"],json_userInfo["Password"])

