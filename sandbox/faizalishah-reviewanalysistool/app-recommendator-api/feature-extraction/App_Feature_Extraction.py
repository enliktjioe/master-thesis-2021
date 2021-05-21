
# coding: utf-8

# In[29]:


from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import re
import nltk
from nltk.tree import Tree
from pycorenlp import StanfordCoreNLP
import numpy as np
from unidecode import unidecode
from nltk.stem.snowball import SnowballStemmer
import copy
import json
import requests
import itertools


# In[30]:


core_nlp = StanfordCoreNLP('http://localhost:9000')


# In[31]:


stemmer = SnowballStemmer("english")


# In[46]:


class Feature_Extraction:
	def __init__(self,app_desc):
		self.app_description = app_desc
		self.SplitDescTexintoSentences()
		
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
	
	def GetStopWordList(self):
		#file_stop_words="stop_words"
		file_stop_words="feature-extraction/stop_words"

		with open(file_stop_words,'r') as f:
			content = f.readlines()

		lst_stop_words = [stemmer.stem(x.strip()) for x in content]

		return(set(lst_stop_words))
	
	def ExtractNounTerms(self):
		noun_terms_stemmed=[]
		custom_stopwords = self.GetStopWordList()
		for sent in self.clean_sentences:
			output = core_nlp.annotate(sent, properties={'annotators': 'pos','outputFormat': 'json','timeout': '50000'})
			#result = output['sentences'][0]['parse']
			#print(sent)
			if len(output['sentences'])>0:
				pos_result = output['sentences'][0]['tokens']
				stemmed_Nouns= [stemmer.stem(d['word']) for d in pos_result if d['pos'] in ['NN','NNP','NNS']]
				#lemma_Nouns= [stemmer.stem(d['lemma']) for d in pos_result if d['pos'] in ['NN','NNP','NNS']]
			
				noun_terms_stemmed.extend(stemmed_Nouns)
				#noun_terms_lemma.extend(noun_terms_lemma)
			
		clean_noun_terms  = copy.deepcopy(noun_terms_stemmed)
		for i,term in enumerate(noun_terms_stemmed):
			if term in set(custom_stopwords):
				clean_noun_terms.remove(term)
		
		return set(clean_noun_terms)

