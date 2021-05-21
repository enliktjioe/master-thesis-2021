
# coding: utf-8

# In[1]:


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
import schedule
from Text_PreProcessing import TextPreProcessing
from nltk.stem.snowball import SnowballStemmer
from pycorenlp import StanfordCoreNLP
import time
import pickle
import copy
import gc
import sqlite3
import logging
from sqlite3 import Error
import os
import SAFE_Approach
from SAFE_Approach import SAFE_Patterns
# extracting features from app description
from Feature_Extraction_Approaches_Description import App_Feature_Extraction
import datetime
from sys import argv


# In[2]:


stemmer = SnowballStemmer("english")
warnings.filterwarnings("ignore")


# In[3]:


#logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)


# In[4]:


class ReviewScrapper_CompetingApps:
	def __init__(self,main_appIDs):
		self.mainApps = main_appIDs
		self.database = "../AppReviewDB.db"
		self.conn = self.create_connection()
	
	def create_connection(self):
		""" create a database connection to the SQLite database
			specified by the db_file
		:param db_file: database file
		:return: Connection object or None
		"""
		try:
			conn = sqlite3.connect(self.database)
			return conn
		except Error as e:
			print(e)
			logging.info('Exception when connecting to the database!!!')

		return None
	
	def QueryBaseApps(self):
		mainApps = []
		cur = self.conn.cursor()
		for appid in self.mainApps:
			mainApps.append(appid)
			sql_query = "SELECT * FROM BaseApps where appId='" + str(appid) + "'" 
			cur.execute(sql_query)
			rows = cur.fetchall()
 
			for row in rows:
				 #mainApps.append(row[0])
			
				# if data already not exist
				rows = self.QueryTableAgainstAppID(row[0])
			
			#     # if not already exist in the table, insert it with its information
				if len(rows)==0:
					self.InsertFeatureTerms_Description(row[0],row[2])
		
		return mainApps
	
	def QueryTableAgainstAppID(self,appID):
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM AppFeatureTerms_Desc where appId=?",(appID,))
		rows = cur.fetchall()
		
		return rows
	
	def InsertFeatureTerms_Description(self,appId,appDesciption):
		objFeatureExtraction = App_Feature_Extraction(appDesciption)
		app_features_info, default_stemmed_features = objFeatureExtraction.ExtractAppFeatures()
		App_FeaturesInfo =json.dumps({"feature_terms" : app_features_info, 'default_AppFeatures':default_stemmed_features})
		
		FeatureTermsData = (appId,App_FeaturesInfo)
		
		sql = 'INSERT INTO AppFeatureTerms_Desc(appId,feature_terms) VALUES(?,?)'
		cur = self.conn.cursor()
		try:
			cur.execute(sql, FeatureTermsData)
			self.conn.commit()
			#print('Features extraced from app description are inserted into database!!!')
		except Error as e:
			logging.info('Exception when inserting feature terms extracted from app description!!!')
		
	   
	def FindSimilarApps(self):
		self.lst_mainApps = self.QueryBaseApps()
		#print(self.lst_mainApps)

		for mainAppID in self.lst_mainApps:
			#print('Processing app ->', mainAppID)
			#similar_Apps = requests.get('http://stores-api.eu-north-1.elasticbeanstalk.com/appdetails/similar?store=1&appId=' + mainAppID).json()
			similar_Apps = requests.get('http://localhost:8081/similarApps?appId=' + mainAppID).json()
			
			#print(similar_Apps)
			
			for CompetitorApp in similar_Apps: 
				#print(CompetitorApp["appId"])               
				CompetitorAppDetails = requests.get('http://stores-api.eu-north-1.elasticbeanstalk.com/appdetails?store=1&appId=' + str(CompetitorApp["appId"])).json()                                            
				# insert feature extracted from app description into Table
				rows = self.QueryTableAgainstAppID(str(CompetitorApp["appId"]))
				# if not already exist in the table, insert it with its information
				if len(rows)==0:
					self.InsertFeatureTerms_Description(str(CompetitorApp["appId"]),CompetitorAppDetails["description"])
					
				CompetitorAppData= (mainAppID,str(CompetitorApp["appId"]),str(CompetitorAppDetails["title"]),str(CompetitorAppDetails["description"]),float(CompetitorAppDetails['score']),str(CompetitorAppDetails['icon']))
				#check if competitorApp data is already in the Table
				CompetitorAppID = str(CompetitorApp["appId"])
				cur = self.conn.cursor()
				cur.execute("SELECT * FROM CompetitorApps where Base_appID=? and Competitor_appID=?",(mainAppID,CompetitorAppID))
				rows = cur.fetchall()
				
				# if not already exist in the table, insert it with its information
				if len(rows)==0:
					#print("inserting data of competitor app '" + str(CompetitorApp["appId"]) + "'")
					sql = 'INSERT INTO CompetitorApps(Base_appID,Competitor_appID,title,description,score,icon) VALUES(?,?,?,?,?,?)'
					cur = self.conn.cursor()
					try:
						cur.execute(sql, CompetitorAppData)
						self.conn.commit()
					except Error as e:
						print(e)
						logging.info('Exception when saving Competitor app info into database!!!')
				else:
					cur = self.conn.cursor()
					try:
						cur.execute('UPDATE CompetitorApps SET score=? where Base_appID=? and Competitor_appID=?',(float(CompetitorAppDetails['score']),mainAppID,str(CompetitorAppID)))
						self.conn.commit()
					except Error as e:
						print(e)
						logging.info('Exception when updating Competitor rating info in the database!!!')
					
	def CheckIfReviewNotExist(self,appID,reviewID):
		review_exist_status= False
		exist = os.path.isfile(self.data_path)
		if exist:
			# check if review exists in the existing file
			with open(self.data_path) as json_file:  
				data = json.load(json_file)
				reviews = data[appID]
				
				for review_info in reviews:
					if review_info["id"] == reviewID:
						review_exist_status = True
						break
					
		return review_exist_status

	def ReadExistingReviews(self,appID):
		exist = os.path.isfile(self.data_path)
		reviews=[]

		if exist:
			with open(self.data_path) as json_file:  
				data = json.load(json_file)
				reviews = data[appID]

		return reviews
	
	def ClassifySentences(self,review_sent):
		#with open(r"feature-extraction/Review_Classification_Model/model_Vectorizer.sav", "rb") as input_file:
		with open(r"Review_Classification_Model/model_Vectorizer.sav", "rb") as input_file:
			vectorizer = pickle.load(input_file)

		#with open(r"feature-extraction/Review_Classification_Model/finalized_model.sav", "rb") as input_file:
		with open(r"Review_Classification_Model/finalized_model.sav", "rb") as input_file:
			model = pickle.load(input_file)

		sents_feature_vector = vectorizer.transform(review_sent)
		sents_feature_vector_array = sents_feature_vector.toarray()

		#print(sents_feature_vector_array.shape)

		sents_class = model.predict(sents_feature_vector_array)

		gc.collect()

		return sents_class[0]
	
	def AdJustSentimentScoreByReviewRating(self,sentiment_score,review_rating):
		#sentiment score ranges between 0 to 4
		#review rating score between 1 and 5
		adjusted_sentiment_score=0
		
		if sentiment_score >=2 and review_rating == 1:   # tool +ve , review rating extremely negative
			adjusted_sentiment_score = sentiment_score - 1
		elif sentiment_score <= 2 and review_rating == 5: # tool neutral or -ve , review rating extremely +ve
			adjusted_sentiment_score = sentiment_score + 1
		else:
			adjusted_sentiment_score = sentiment_score
		
		return adjusted_sentiment_score
	
	def ExtractInformationfromReview(self,ReviewInfo,appId):
		
		sucess=False
		res=None
		
		review_score = int(ReviewInfo["score"])
		
		while sucess==False:
			try:
				core_nlp = StanfordCoreNLP('http://corenlp.run')
				res = core_nlp.annotate(ReviewInfo["reviewText"], properties={'annotators': 'tokenize,ssplit,pos,parse,sentiment','outputFormat': 'json'})
				sent_tokens = res["sentences"][0]["tokens"]
				sucess = True
			except Exception as ex:
				sucess= False
				print(ReviewInfo["reviewText"])
				print('Exception when using corenlp.run. Attempting again!!')
				logging.info('Exception when using corenlp.run. Attempting again!!')
		
		sent_id = 1
		
		try:
		
			#print(ReviewInfo["reviewText"])
			#print(len(res["sentences"]))
		
			for i in range(0,len(res["sentences"])):
				sent_words = [token['word'] for token in res['sentences'][i]['tokens']]
				sent = ' '.join(sent_words)

				if len(sent_words)>3:
					sent_stemmed_words = [stemmer.stem(w) for w in sent_words]
					sentiment_score = int(res['sentences'][i]['sentimentValue'])
					
					adj_sentiment_score = self.AdJustSentimentScoreByReviewRating(sentiment_score,review_score)

					# review sentence classification
					reviewSent=[]
					objTextPreprocessing = TextPreProcessing(sent)
					clean_sent = objTextPreprocessing.PreProcess()    
					reviewSent.append(clean_sent)
					sent_category = self.ClassifySentences(reviewSent)

					objSAFE = SAFE_Patterns(sent)
					_,safe_extracted_stemmed_features = objSAFE.ExtractFeatures_Using_POSPatterns()

					if sent_category=="E":
						scaled_sentiment_score = int(adj_sentiment_score) - 2
					elif sent_category == "B":
						scaled_sentiment_score = int(-2)
					elif sent_category == "R":
						scaled_sentiment_score = int(0)

					if sent_category=="E" or sent_category=="B" or sent_category=="R":                    
						review_sent_info = (ReviewInfo["id"] + "#"  + str(sent_id),' '.join(sent_words),' '.join(sent_stemmed_words),sent_category,'|'.join(safe_extracted_stemmed_features), scaled_sentiment_score,appId)

						sent_id = sent_id + 1

						sql = 'INSERT INTO AppReviewSents(sent_id,sent_words,sent_stemmed_words,category,feature_terms,sentiment,appId) VALUES(?,?,?,?,?,?,?)'
						cur = self.conn.cursor()
						cur.execute(sql, review_sent_info)
						self.conn.commit()
		
						#print('Review sentence information recoreded in the database!!!')
		except Error as e:
			print(e)
			logging.info('Exception when information from review sent is extracted and saved in the database')
			sucess = False
			
		
		return sucess
				
	def GetMonthbyName(self,monthName):
		months = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
		return months[monthName]
	
	def ConvertDate(self,reviewDate):
		dateParts= reviewDate.split(",")
		MonthDayInfo = dateParts[0].split(" ")
		month = MonthDayInfo[0].strip()
		day = MonthDayInfo[1].strip()
		year = dateParts[1].strip()
		
		return year + "-" + str(self.GetMonthbyName(month)) + "-" + day
		
	def CollectReviews_SaveExtractedInformation(self):
		DS_AppReviews = {}
		
		for BaseAppID in self.lst_mainApps:
			Reviews_added = 0
			for pageNo in range(0,10):
				r = requests.get('http://stores-api.eu-north-1.elasticbeanstalk.com/reviews?store=1&appId=' + BaseAppID + '&page=' + str(pageNo))
				reviews= r.json()
				for review_info in reviews:
					#check if review doesn't exist in the database table 'AppReviews'
					#print(review_info["id"])
					cur = self.conn.cursor()
					cur.execute("SELECT * FROM AppReviews where appId=? and ReviewID=?",(BaseAppID,review_info["id"]))
					rows = cur.fetchall()
							  
					reviewInfo = (BaseAppID,review_info["title"],review_info["reviewText"],review_info["score"],self.ConvertDate(review_info["date"]),review_info["id"])
			
					if len(rows)==0:
						sql = 'INSERT INTO AppReviews(appId,title,text_review,score,date,ReviewID) VALUES(?,?,?,?,?,?)'
						cur = self.conn.cursor()
						try:
							cur.execute(sql, reviewInfo)
							self.conn.commit()
						except Error as e:
							print(e)
							logging.info('Exception while inserting review info of main app \' {BaseAppID} \' into table!')
						
						Reviews_added =  Reviews_added + 1
						self.ExtractInformationfromReview(review_info,BaseAppID)
				
			if Reviews_added>0:
				now = datetime.datetime.now()
				logging.info(now.strftime("%Y-%m-%d %H:%M")  + " " + str(Reviews_added) + " reviews and feature-level information added for base app " + "'" + BaseAppID + "' in the dababase!")
			
			#fetch reviews of top 10 competitor apps and store their extracted information into dababase
			
			cur = self.conn.cursor()
			cur.execute("SELECT * FROM CompetitorApps where Base_AppID=? order by score DESC LIMIT 10",(BaseAppID,))
			rows = cur.fetchall()
			
			#  top 20 competitor apps
			for row in rows:
				Competitor_appId = row[1]
				print(Competitor_appId)
				Reviews_added = 0
				lst_reviews=[]
				for pageNo in range(0,10):
					r = requests.get('http://stores-api.eu-north-1.elasticbeanstalk.com/reviews?store=1&appId=' + Competitor_appId + '&page=' + str(pageNo))
					reviews= r.json()
					for review_info in reviews:
						#check if review doesn't exist in the database table 'AppReviews'
						#print(review_info["id"])
						cur = self.conn.cursor()
						cur.execute("SELECT * FROM AppReviews where appId=? and ReviewID=?",(Competitor_appId,review_info["id"]))
						rows = cur.fetchall()
							  
						reviewInfo = (Competitor_appId,review_info["title"],review_info["reviewText"],review_info["score"],self.ConvertDate(review_info["date"]),review_info["id"])
			
						if len(rows)==0:
							sql = 'INSERT INTO AppReviews(appId,title,text_review,score,date,ReviewID) VALUES(?,?,?,?,?,?)'
							cur = self.conn.cursor()
							try:
								cur.execute(sql, reviewInfo)
								self.conn.commit()
							except Error as e:
								print(e)
								logging.info("Exception while inserting review info of competitor app \'{Competitor_appId}\' into table!")
						
							Reviews_added =  Reviews_added + 1
							self.ExtractInformationfromReview(review_info,Competitor_appId)
				
				if Reviews_added>0:
					now = datetime.datetime.now()
					logging.info(now.strftime("%Y-%m-%d %H:%M")  + " " + str(Reviews_added) + " reviews and feature-level information added for competitor app " + "'" + Competitor_appId + "' in the dababase!")
		 
		if self.conn:
			self.conn.close()
		
		gc.collect()     


# In[5]:


def PerformJob(appIds):
	start = time.time()
	# extract and analyze reviews of base apps passed as a list from command line
	objReviewScrapper=ReviewScrapper_CompetingApps(appIds)
	objReviewScrapper.FindSimilarApps()
	objReviewScrapper.CollectReviews_SaveExtractedInformation();

	end = time.time()
	exec_time_secs = end - start
	exec_time_mins, _ = divmod(exec_time_secs,60)
	logging.info("The script took %s mins for execution!!!"% (str(exec_time_mins)))


if __name__ == '__main__':
	json_appIds = json.loads(argv[1])
	print(json_appIds)
	PerformJob(json_appIds["appIds"])
	#schedule.every().hour.do(PerformJob(json_appIds["appIds"]))
	#schedule.every().day.at("23:59").do(PerformJob)
	#while True:
		#schedule.run_pending()
		#time.sleep(60)

