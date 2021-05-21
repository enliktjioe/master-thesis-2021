
# coding: utf-8

# In[350]:


import importlib
import json
from urllib.request import urlopen
import re
import requests
from unidecode import unidecode
import App_Feature_Extraction
from App_Feature_Extraction import Feature_Extraction
from pycorenlp import StanfordCoreNLP
import Text_PreProcessing
import nltk
from Text_PreProcessing import TextPreProcessing
from nltk.stem.snowball import SnowballStemmer
import time
from datetime import datetime
import warnings
import sys
import pickle
import Feature_Extraction_Approaches_Description
from Feature_Extraction_Approaches_Description import App_Feature_Extraction
from SAFE_Approach import SAFE_Patterns
import SAFE_Approach
import copy
import gc




# In[351]:


stemmer = SnowballStemmer("english")


# In[352]:


warnings.filterwarnings("ignore")


# In[353]:


importlib.reload(Text_PreProcessing)
importlib.reload(Feature_Extraction_Approaches_Description)


# In[354]:



# In[361]:


class ReviewSummarizer:
	def __init__(self,app):
		self.appID = app
		self.ExtractNounTermsFromAppDescription()
	
	def ExtractNounTermsFromAppDescription(self):
		r = requests.get('http://localhost:8081/appDetails?id=' + self.appID)
		output = r.json()
		appDesciption= output['description']
		appTitle = output['title']
		appIconUrl = output['icon']

		objFeatureExtraction = App_Feature_Extraction(appDesciption)
		app_features_info, default_stemmed_features = objFeatureExtraction.ExtractAppFeatures()
		self.App_FeaturesInfo ={"appTitle": appTitle, "appIconUrl" : appIconUrl , "feature_terms" : app_features_info, 'default_AppFeatures':default_stemmed_features}
		

	def chunks(self,l, n):
	# For item i in a range that is a length of l,
		for i in range(0, len(l), n):
		# Create an index range for l of n items:
			yield l[i:i+n]
		
	def GetAppReviews_SummaryInfo(self):

		desc_feature_info = self.App_FeaturesInfo
		lst_all_relevant_sents=[]
		dict_all_reviews={}
		
		with open('offline_review_dataset/review_collection_Faiz/DS_AppReviews.json') as json_file:  
			data = json.load(json_file)
			reviews = data[self.appID]
			lst_batches=list(self.chunks(reviews, 100))
			
			batchno=1
			review_id_count=1

			for batch in lst_batches:
				print('Batch #',batchno, "Size->",len(batch))
				AppReviewsInfo = ""
				for review_info in batch:
					reviewDetails = ""
					rid = self.appID + "_" + str(review_id_count)
					reviewDetails = "REVIEW-ID#"+ rid + "|"
					reviewDetails += "TITLE#"+ re.sub('[^A-Za-z0-9-\s]+', '',review_info["title"]) +"|"
					reviewDetails += "SCORE#"+ str(review_info["score"]) +"|"
					reviewDetails += "DATE#"+ str(review_info["date"].strip()) 
					reviewDetails += ". "
					reviewDetails += review_info["text"].strip()
					reviewDetails += ". "

					review_id_count+=1

					AppReviewsInfo += reviewDetails
			

				# split all reviews into sentences and determine their sentiments
				lst_relevant_sents,dict_reviews = self.ReviewBatchSummaryInfo(AppReviewsInfo)
				lst_all_relevant_sents.extend(lst_relevant_sents)
				dict_all_reviews = {**dict_all_reviews,**dict_reviews}

				batchno+=1
				#print("")


		return {'Reviews': dict_all_reviews, 'ReviewSents' : lst_all_relevant_sents,  'appTitle' : desc_feature_info["appTitle"], 'appIcon':desc_feature_info["appIconUrl"],'Description':desc_feature_info["feature_terms"],'AppFeatures': desc_feature_info["default_AppFeatures"],  'TotalSents': str(len(lst_all_relevant_sents))}


	
	# function that classify review sentence into follwing five categories Feature Evaluation (E), Feature Request (R)
	# Bug Report (B), Praise (P) and Others (N)
	def ClassifySentences(self,review_sents):
		#with open(r"feature-extraction/Review_Classification_Model/model_Vectorizer.sav", "rb") as input_file:
		with open(r"Review_Classification_Model/model_Vectorizer.sav", "rb") as input_file:
			vectorizer = pickle.load(input_file)

		#with open(r"feature-extraction/Review_Classification_Model/finalized_model.sav", "rb") as input_file:
		with open(r"Review_Classification_Model/finalized_model.sav", "rb") as input_file:
			model = pickle.load(input_file)

		sents_feature_vector = vectorizer.transform(review_sents)
		sents_feature_vector_array = sents_feature_vector.toarray()

		#print(sents_feature_vector_array.shape)

		sents_class = model.predict(sents_feature_vector_array)

		gc.collect()

		return sents_class
	
	def ReviewSentContainAppDescNounTerms(self,sent_words):
		termsIndex_matched_with_desc = [index for index,w in enumerate(sent_words) if w in self.appDesc_NounTerms]
		return termsIndex_matched_with_desc

	def ReviewBatchSummaryInfo(self,txt_AllReviews):
		gc.collect()

		core_nlp = StanfordCoreNLP('http://localhost:9000')	
		res = core_nlp.annotate(txt_AllReviews, properties={'annotators': 'tokenize,ssplit,pos,parse,sentiment','outputFormat': 'json','timeout': '500000000'})

		print("Reviews has been processed!!!")

		apps_info = {}

		lst_review_sents=[]
		dict_reviews = {}

		lst_review_ids = []
		lst_clean_sents = []

		sent_id = 1
		txt_review=""
		old_review_data = None


		
		sent_words = [token['word'] for token in res['sentences'][0]['tokens']]
		sent = ' '.join(sent_words)
		sent_parts = sent.split("|")		

		print(sent_parts)

		if len(sent_parts)==4:
			ReviewID = sent_parts[0].split("#")[1].strip()
			title = sent_parts[1].split("#")[1].strip()
			score = sent_parts[2].split("#")[1].strip()
			date = sent_parts[3].split("#")[1].strip()
			old_review_data ={'ReviewID':ReviewID, 'Title':title, 'Score' : score, 'Date': date}
			#print(old_ReviewID)



		for i in range(1,len(res["sentences"])):
			sent_words = [token['word'] for token in res['sentences'][i]['tokens']]
			sent = ' '.join(sent_words)
			sent_parts = sent.split("|")

			if len(sent_parts)==4:
				if sent_parts[0].split("#")[0].strip()=="REVIEW-ID":
					#print('extract information....')
					ReviewID = sent_parts[0].split("#")[1].strip()
					title = sent_parts[1].split("#")[1].strip()
					score = sent_parts[2].split("#")[1].strip()
					date = sent_parts[3].split("#")[1].strip()
		
					if old_review_data!=None:
						if old_review_data["ReviewID"]!=ReviewID:
							dict_reviews[old_review_data["ReviewID"]]={"title" : old_review_data["Title"], "text": txt_review, "score": old_review_data["Score"],"date": old_review_data["Date"] }
							sent_id = 1
							txt_review = ""

					old_review_data = {'ReviewID':ReviewID, 'Title':title, 'Score' : score, 'Date': date}

			elif len(sent_words)>3 and len(sent_parts)!=4:
				sent_stemmed_words = [stemmer.stem(w) for w in sent_words]
				sentiment_score = int(res['sentences'][i]['sentimentValue'])

				# processing for textclassifation model
				objTextPreprocessing = TextPreProcessing(sent)
				clean_sent = objTextPreprocessing.PreProcess()
				lst_clean_sents.append(clean_sent)	
				#print(old_review_data)
				lst_review_ids.append(old_review_data["ReviewID"] + "#"  + str(sent_id))
				lst_review_sents.append({'sent_id': old_review_data["ReviewID"] + "#"  + str(sent_id), 'sent_words': sent_words, 'sent_stemmed_words':sent_stemmed_words,'category': '', 'feature_terms': [], 'sentiment': str(sentiment_score),"appID" : self.appID})
				sent_id = sent_id + 1
				txt_review = txt_review + sent				
			elif len(sent_parts)!=4 and sent.strip()!="" and sent.strip()!=".":
				txt_review = txt_review + sent				


		dict_reviews[old_review_data["ReviewID"]]={"title" : old_review_data["Title"], "text": txt_review, "score": old_review_data["Score"],"date": old_review_data["Date"] }
		#apps_info[old_app_id] = {"Reviews" : dict_reviews, "ReviewSents":lst_review_sents, 'Review_Sents_Clean':lst_clean_sents, 'Reiew_Sents_IDs': lst_review_ids}
		
		# Step 3 : classify review sentences into categories: Bug Report, Feature Request, Feature Evaluation, Praise, and Others
		# attach each sentence to its review sentnece id
		lst_relevant_review_sents = []

		if len(lst_clean_sents)>0:
			print("Model classification has been started!!!")
			dict_sent_classes = dict(zip(lst_review_ids,self.ClassifySentences(lst_clean_sents)))
		
			for i in range(0,len(lst_review_sents)):
				sent_info = lst_review_sents[i]
				sent_words = sent_info['sent_words']
				stemmed_words = sent_info['sent_stemmed_words']
				sentiment_score = sent_info['sentiment']
				sent_id = sent_info['sent_id']
				review_sent = ' '.join(sent_words)
				review_id = sent_id.split("#")[0]
				
				review_sent_class = dict_sent_classes[sent_id]
				scaled_sent_score = -100

				if review_sent_class=='E' or review_sent_class=='B' or review_sent_class=='R':
					review_sent = ' '.join(sent_words)
					objSAFE = SAFE_Patterns(review_sent)
					_,safe_extracted_stemmed_features = objSAFE.ExtractFeatures_Using_POSPatterns()
				
				if review_sent_class=='E':
					scaled_sent_score = int(sentiment_score) - 2;
					dict_review_sentence_info = {'sent_id': sent_id, 'sent_words': sent_words, 'sent_stemmed_words':stemmed_words,'category': review_sent_class, 'feature_terms': safe_extracted_stemmed_features, 'sentiment': str(scaled_sent_score), "appID" : self.appID}
					lst_relevant_review_sents.append(dict_review_sentence_info)
				elif review_sent_class=='B':				
					sentiment_score = int(-2)
					dict_review_sentence_info = {'sent_id': sent_id, 'sent_words': sent_words, 'sent_stemmed_words':stemmed_words,'category': review_sent_class, 'feature_terms': safe_extracted_stemmed_features, 'sentiment': str(sentiment_score), "appID" : self.appID}
					lst_relevant_review_sents.append(dict_review_sentence_info)
				elif review_sent_class=='R':				
					sentiment_score = int(0)
					dict_review_sentence_info = {'sent_id': sent_id, 'sent_words': sent_words, 'sent_stemmed_words':stemmed_words,'category': review_sent_class, 'feature_terms': safe_extracted_stemmed_features, 'sentiment': str(sentiment_score), "appID" : self.appID}
					lst_relevant_review_sents.append(dict_review_sentence_info)
		

		#AppsReviewSummaries[appID] = {'Reviews': apps_info[appID]["Reviews"], 'ReviewSents' : lst_relevant_review_sents,  'appTitle' : desc_feature_info["appTitle"], 'appIcon':desc_feature_info["appIconUrl"],'Description':desc_feature_info["feature_terms"], 'TotalSents': str(len(lst_relevant_review_sents))}

			print("Model classification has been finished!!!")

		gc.collect()

		return lst_relevant_review_sents, dict_reviews
		

if __name__ == '__main__':	
	AppsReviewSummaries={}
	#AppIDs=['410606661','436762566','387771637','353938652','292987597','300235330','329504506','509253726','398436747','363724891','298903147','292223170','426826309','368868193','287529757','386022579','292760731']
	#AppIDs=['287529757','386022579','292760731']
	#AppIDs=['353938652','292987597','300235330','329504506','509253726','398436747','363724891','298903147','292223170','426826309','368868193','287529757','386022579','292760731']
	#AppIDs=['292223170','300235330','387771637','509253726','426826309','298903147']
	#AppIDs=['292987597','410606661','426826309','298903147','398436747','509253726','292223170','300235330','387771637']
	AppIDs = ["675033630","368677368","1291898086","895933956","336456412"]
	for appid in AppIDs:
		print("AppID ->", appid)
		objReviewSummarizer = ReviewSummarizer(appid)
		ReviewsSummaryInfo = objReviewSummarizer.GetAppReviews_SummaryInfo()
		AppsReviewSummaries[appid] = ReviewsSummaryInfo
		AppsReviewSummary_json = json.dumps(AppsReviewSummaries)
		file_path = "offline_review_dataset/review_collection_Faiz/" + appid + ".json"
		f = open(file_path,"w")
		f.write(AppsReviewSummary_json)
		f.close()
		print('Contents stored in a file!!!')
		print('##############################################')
		
	gc.collect()

	#


