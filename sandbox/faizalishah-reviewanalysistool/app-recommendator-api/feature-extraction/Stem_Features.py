
# coding: utf-8

# In[10]:


import importlib
import json
from urllib.request import urlopen
import re
import requests
from nltk.stem.snowball import SnowballStemmer
import warnings
import sys


# In[11]:


stemmer = SnowballStemmer("english")
warnings.filterwarnings("ignore")


# In[12]:


class StemAppFeatures:
	def __init__(self,lst_appFeatures):
		self.appFeatures = lst_appFeatures
		
	def GetStemnUniqueFeatures(self):
		lstAppFeatures=[]
		
		for feature in self.appFeatures:
			if feature.strip()!="" and len(feature.strip())!=0:
				lstAppFeatures.append(' '.join([stemmer.stem(w) for w in feature.split()]))
		
		return set(lstAppFeatures)


# In[13]:


def read_in():
	lines = sys.stdin.readlines()
	return json.loads(lines[0]) 


# In[9]:


if __name__ == '__main__':
	line = read_in()
	appFeatures = line["appFeatures"]
	objAppFeatureStemmer = StemAppFeatures(appFeatures)
	lst_AppFeatures = list(objAppFeatureStemmer.GetStemnUniqueFeatures())
	lst_AppFeatures.sort()
	lstUnique_StemmedFeatures={}
	lstUnique_StemmedFeatures['appFeatures']= lst_AppFeatures 
	print(json.dumps(lstUnique_StemmedFeatures))

