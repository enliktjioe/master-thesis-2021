
# coding: utf-8

# In[215]:


from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import re
import nltk
from nltk.tree import Tree
from pycorenlp import StanfordCoreNLP
import importlib
from SAFE_Approach import SAFE_Patterns
import SAFE_Approach
import numpy as np
from unidecode import unidecode
import copy
import json
import requests
import itertools
import Liu_Feature_Extraction_Plus_SAFE
from Liu_Feature_Extraction_Plus_SAFE import Feature_Extraction
from nltk.stem.snowball import SnowballStemmer
import gc


# In[216]:


importlib.reload(SAFE_Approach)
importlib.reload(Liu_Feature_Extraction_Plus_SAFE)


# In[217]:



# In[218]:


stemmer = SnowballStemmer("english")


# In[223]:


class App_Feature_Extraction:
	def __init__(self,app_desc):
		self.app_description = app_desc
		self.SplitDescTexintoSentences()

	def GetFeatureStartnEndIndex(self,corenlp_output,app_feature):
		app_feature_words=[w for w in app_feature.split()]
		sent_words = [d['word'] for d in corenlp_output['sentences'][0]['tokens']]

		feature_word_indexes = [(w,index) for index,w in enumerate(sent_words) if w in app_feature_words]

		array_indexes=[]

		try:

			for i in range(0,len(app_feature_words)):
				feature_word  = app_feature_words[i]
				word_indexes = [index for w,index in feature_word_indexes if w==feature_word]

				lst_diff=[]
				complex_case=False
				exact_duplicate = False
				if len(word_indexes)>1:
					for index in word_indexes:
						if len(array_indexes)!=0:
							last_index = len(array_indexes)-1
							last_word_index= array_indexes[last_index]
							diff = abs(index-last_word_index)
							lst_diff.append((index,diff))
						elif i < len(app_feature_words)-1:
							next_feature_word = app_feature_words[i+1]
							next_word_indexes = [index for w,index in feature_word_indexes if w==next_feature_word]
							if len(next_word_indexes)==1:
								diff = abs(next_word_indexes[0] - index)
								lst_diff.append((index,diff))
							elif len(next_word_indexes)>1 and len(array_indexes)==0:
								for w_index in next_word_indexes:
									diff = abs(w_index-index)
									lst_diff.append((index,diff))
									complex_case=True

					if complex_case==True:
						min_diff = min([diff for word,diff in lst_diff])
						if len([diff for word, diff in lst_diff if diff==min_diff])>1:
						 # look for the third word to resolve this issue
							if (i+2) < len(app_feature_words):
								lst_diff.clear()
								next_feature_word = app_feature_words[i+2]
								next_word_indexes = [index for w,index in word_with_indexes if w==next_feature_word]
								for index in word_indexes:
									if len(next_word_indexes)==1:
										diff = abs(next_word_indexes[0] - index)
										lst_diff.append((index,diff))
									elif len(next_word_indexes)>1 and len(array_indexes)==0:
										for i in range(0,3):
											word_index = word_with_indexes[i]
											array_indexes.append(word_index[1])
											exact_duplicate=True
											break


					if exact_duplicate==False:
						sorted_by_differnece = sorted(lst_diff, key=lambda tup: tup[1])
						array_indexes.append(sorted_by_differnece[0][0])
					else:
						break
				else:
					array_indexes.append(word_indexes[0])

		except Exception as ex:
			array_indexes = []

		return array_indexes

		
	def SplitDescTexintoSentences(self):
		content = self.app_description.splitlines()
		self.clean_sentences=[]
		for txt in content:
			txt = unidecode(txt)
			pattern1 = r'(\+|\*|\#)+'
			data = re.sub(pattern1,"",txt)
			pattern2 = r'\*|\u2022|#'
			data= re.sub(pattern2,"",data)
			pattern3=r'".*"(\s+-.*)?'
			data = re.sub(pattern3, '', data)
			pattern4 = r'\u2014\s.*'
			data = re.sub(pattern4,"",data)
			
			if data.lower().strip() in ["credits:","notes:","credits","notes"]:
				break

			regex = r"(\(|\[).*?(\)|\])"
			urls = re.findall('(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?',data)    
			emails = re.findall("[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*", data) 
			match_list = re.finditer(regex,data)

			new_sent=data

			# filter sentences containg urls, emails, and quotations
			if len(urls)==0 and len(emails)==0 :
				if match_list:
					for match in match_list:
						txt_to_be_removed = data[match.start():match.end()]
						new_sent=new_sent.replace(txt_to_be_removed,"")
					if len(new_sent.strip())!=0:
						lst_sents = nltk.sent_tokenize(new_sent.strip())
						for sent in lst_sents:
							sent_words = nltk.word_tokenize(sent)
							if '?' not in sent_words and '!' not in sent_words:
								clean_sent = re.sub(r'\([^)]*\)', '', sent)
								clean_sent = re.sub(r'\"[^"]*\"', '', clean_sent)
								clean_sent = clean_sent.strip('-')
								self.clean_sentences.append(clean_sent.strip())
				else:
					if len(sent.strip())!=0:
						lst_sents = nltk.sent_tokenize(new_sent.strip())
						for sent in lst_sents:
							sent_words = nltk.word_tokenize(sent)
							
							if '?' not in sent_words and '!' not in sent_words:
								clean_sent = re.sub(r'\([^)]*\)', '', sent)
								clean_sent = re.sub(r'\"[^"]*\"', '', clean_sent)
								clean_sent = clean_sent.strip('-')
							   
								self.clean_sentences.append(clean_sent.strip())  
	
	def ExtractNounTerms (self,corenlp_output):
		regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
		pos_result = corenlp_output['sentences'][0]['tokens']
		custom_stop_words = set(self.GetCustomStopWordList())
		cutom_stop_words_stemmed =[stemmer.stem(w) for w in custom_stop_words]
		noun_terms = [{'start': str(index), 'end' : str(index), 'feature_term': d['word']} for index,d in enumerate(pos_result) if d['pos'] in ['NN','NNP','NNS'] and stemmer.stem(d['word']) not in cutom_stop_words_stemmed and regex.search(d['word']) == None]		
		return noun_terms

	def GetCustomStopWordList(self):
		#CustomStopWordList_path = 'feature-extraction/List_StopWords'
		CustomStopWordList_path = 'List_StopWords'

		with open(CustomStopWordList_path,'r') as f:
			content = f.readlines()

		lst_cutomStopWords = [x.strip() for x in content]

		return(lst_cutomStopWords)
	
	
	def ExtractAppFeatures(self):
		desc_sents_feature_info=[]
		default_stemmed_feature_terms =[]
		
		for sent in self.clean_sentences:
			if sent.strip()!="":
				sucess=False	
				output=None
		
				while sucess==False:
					try:
						core_nlp = StanfordCoreNLP('http://corenlp.run')
						output = core_nlp.annotate(sent, properties={'annotators': 'tokenize,ssplit,pos,parse','outputFormat': 'json'})
						tokens = output["sentences"][0]["tokens"]
						sucess = True
					except Exception as e:
						sucess= False
		
				
				sent_tokens = [d['word'] for d in output['sentences'][0]['tokens']]

				#print('sentence ->', sent_tokens)
				
				# simple feature extraction approach
				
				cont_noun_terms = self.ExtractNounTerms(output)

				#default_stemmed_feature_terms.extend([stemmer.stem(feature_info['feature_term']) for feature_info in cont_noun_terms if feature_info['feature_term'].strip()!=""])

				#print('NOUN TERMS ->',cont_noun_terms)

				#print('#################################')
				
				non_cont_noun_terms = []
				
				# SAFE feature extraction approach
				
				objSAFE = SAFE_Patterns(sent)
				extracted_features,_ = objSAFE.ExtractFeatures_Using_POSPatterns()
				
				#print('SAFE extracted features ->',extracted_features)
				SAFE_cont_features=[]
				SAFE_non_cont_features=[]
				
				for feature in extracted_features:
					loc = self.GetFeatureStartnEndIndex(output,feature)
					if len(loc)!=0:
						if feature in sent:
							SAFE_cont_features.append({'start':str(loc[0]), 'end': str(loc[len(loc)-1])})
							default_stemmed_feature_terms.append(' '.join([stemmer.stem(w) for w in feature.split()]))
						else:
							SAFE_non_cont_features.append(feature)
							default_stemmed_feature_terms.append(' '.join([stemmer.stem(w) for w in feature.split()]))
				
						
				# LIU feataure extraction approach
				
				obj_Liu_FeatureExtraction = Feature_Extraction(output)
				extracted_features = obj_Liu_FeatureExtraction.ExtractFunctionalAspects()
				
				LIU_cont_features=[]
				LIU_non_cont_features=[]
				
				for feature in extracted_features:
					loc = self.GetFeatureStartnEndIndex(output,feature)
					if len(loc)!=0:
						if feature in sent:
							LIU_cont_features.append({'start':str(loc[0]), 'end': str(loc[len(loc)-1])})
						else:
							LIU_non_cont_features.append(feature)
				
				
				
				# end extraction of all approaches
							
				info_dict={'sent_words' : sent_tokens,'feature_extraction_results': 
						   { 
							'ONE_WORD_NOUN': { 'CONSECUTIVE_TERMS': cont_noun_terms, 'NON_CONSECUTIVE_TERMS': non_cont_noun_terms}, 
							'SAFE': { 'CONSECUTIVE_TERMS': SAFE_cont_features, 'NON_CONSECUTIVE_TERMS': SAFE_non_cont_features}, 
							'LIU': { 'CONSECUTIVE_TERMS': LIU_cont_features, 'NON_CONSECUTIVE_TERMS': LIU_non_cont_features} 
						   } 
						  }
				
				desc_sents_feature_info.append(info_dict)
		


		gc.collect()	
		return desc_sents_feature_info,list(set(default_stemmed_feature_terms));


# In[224]:


# if __name__ == '__main__':
# 	appID = 'com.whatsapp'
# 	r = requests.get('http://localhost:8081/appInfo?id=' + appID)
# 	output = r.json()
# 	appDesciption= output['description']
	
# 	obj = App_Feature_Extraction(appDesciption)
# 	print('################################')
# 	obj.ExtractAppFeatures()

