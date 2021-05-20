
import pandas as pd
import numpy as np
#from spacy.en import English
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
import re
#import spacy
import collections
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import statistics
#from spacy.en import English
import nltk
import math
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.dom import minidom
import html
import os 
from shutil import copyfile
import sys
import argparse

#nlp = spacy.load('de')

parser = argparse.ArgumentParser(description='Optional app description')

parser.add_argument('-r','--dataset', type=str,
					help='name of review dataset')

# Optional positional argument
parser.add_argument('--lang', type=str, default='en',
					help='language of review dataset (EN or DE)')

parser.add_argument('--step', type=int,
					help='Preprocessing step (0 to 3)')


from enum import Enum

class ANNOTATORS:
	CODER1 = 1 
	CODER2 = 2 

class APP_CAEGORIES_DE(Enum):
	WEATHER_APPS= 1
	SPORT_NEWS= 2
	SOCIAL_NETWORKS = 3
	OFFICE_TOOLS = 4
	NEWS_APPS = 5
	NAVIGATION_APPS = 6
	MUSIC_PLAYERS = 7
	INSTANT_MESSENGERS = 8
	GAMES = 9
	FITNESS_TRACKER = 10
	ALARM_CLOCKS = 11

class EN_APPS_CATEGORY(Enum):
	GAME = 1
	PRODUCTIVITY= 2
	TRAVEL = 3
	PHOTOGRAPHY = 4
	SOCIAL = 5
	COMMUNICATION = 6

class MOBILE_APPS(Enum):
	ANGRY_BIRDS = 1
	DROP_BOX= 2
	EVERNOTE = 3
	TRIP_ADVISOR = 5
	PICS_ART = 6
	PINTEREST = 7
	WHATSAPP = 8
	
class DATASETS(Enum):
	GUZMAN=1
	SHAH_I=2
	SHAH_II=3
	SANGER=4

class TRANSFORMATION_MODE(Enum):
	PREPROCESSING=0
	SIMULATION_STEP_1=1
	SIMULATION_STEP_2=2
	SIMULATION_STEP_3=3


class TRANSFORM_DATASET(object):
	
	def __init__(self,ds,transformation_mode,lang):
		self.dataset = ds
		self.Transformation_Mode = transformation_mode
		self.lang =lang

		if self.dataset in ['GUZMAN','SHAH_I','SHAH_II'] and self.Transformation_Mode==0:
			self.MoveAppsatCategoryLevel()
		
	def Transform_Dataset(self):
		if self.Transformation_Mode == TRANSFORMATION_MODE.PREPROCESSING.value:
			#print('Peform Precossing!!!')
			self.Perform_Preprocessing(self.lang)
		if self.Transformation_Mode== TRANSFORMATION_MODE.SIMULATION_STEP_1.value:
			self.perform_cleaning_step_1(self.lang)
		elif self.Transformation_Mode == TRANSFORMATION_MODE.SIMULATION_STEP_2.value:
			self.perform_cleaning_step_2(self.lang)
		elif self.Transformation_Mode == TRANSFORMATION_MODE.SIMULATION_STEP_3.value:
			self.AspectTermsWith_1_3_Words(self.lang)

	def MoveAppsatCategoryLevel(self):
			PRODUCTIVITY_APPS=[MOBILE_APPS.DROP_BOX,MOBILE_APPS.EVERNOTE]
			APPS_CATEGORIES={"GAME":"ANGRY_BIRDS","TRAVEL":"TRIP_ADVISOR","PHOTOGRAPHY":"PICS_ART","SOCIAL":"PINTEREST","COMMUNICATION":"WHATSAPP"}
			
			
			main_path= "Review_Datasets_XMLFormat"+ "/" + self.dataset + "/"
			
			for appCategory in EN_APPS_CATEGORY:
				directory_path= main_path
				
				
				if appCategory==EN_APPS_CATEGORY.PRODUCTIVITY:
			   
					app_category_xmlFile= main_path + "/" + appCategory.name + ".xml"
			
					sentences_node = Element('sentences')
			
					counter=1

					for app in PRODUCTIVITY_APPS:
						print("Opening app %s features" % (app.name))

						filepath = "Review_Datasets_XMLFormat/" + self.dataset +  "/"  + app.name + ".xml"
						tree = ElementTree.parse(filepath)
						corpus = tree.getroot()
						sentences = corpus.findall('.//sentence')

						for sent in sentences:
							sent_text = sent.find('text').text
							review_id = sent.attrib['id']
							aspectTerms = sent.find('aspectTerms')

							sentence_node = SubElement(sentences_node,'sentence',{'id':str(review_id)})
							SentText_node = SubElement(sentence_node,"text")
							SentText_node.text = sent_text

							if aspectTerms is not None:
								aspectTerm = aspectTerms.findall('aspectTerm')

								AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

								for aspect_term in aspectTerm:
									if self.dataset=="GUZMAN":
										feature_term = aspect_term.attrib['label1']
										aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'label1': feature_term})
									else:
										feature_term = aspect_term.attrib['term']
										aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': feature_term})

					output_file = open(app_category_xmlFile, 'w' )
					output_file.write(self.prettify_xml(sentences_node))
					output_file.close()
				else:
					app_name = APPS_CATEGORIES[appCategory.name]
					source_file =  main_path + app_name + ".xml"
					dest_file =  main_path + appCategory.name + ".xml"

					copyfile(source_file,dest_file)

	
	def AspectTermsWith_1_3_Words(self,lang):
		if self.lang.lower()=="en":
			appCategories = EN_APPS_CATEGORY
		elif self.lang.lower()=="de":
			appCategories = APP_CAEGORIES_DE
			
		for app_category in appCategories:
			print(app_category)
			#if self.lang.lower()=="en":
			self.KeepAspectTerms_1_3_words_with_NOUN(app_category)
			#elif self.lang=="de":

				#print("################################################")
				#self.FilterAspectMentionSentences(ANNOTATORS.CODER2,app)
			print('++++++++++++++++++++++++++++++++++++++++++++++++')

	def sort_aspect_terms_by_index_app_reviews(self,main_path):  
	
		appCat_data_path = main_path #+ "/" + AppCategory_Test.name +  ".xml"                
	  
		new_appCat_data_path= appCat_data_path
			
		tree = ElementTree.parse(new_appCat_data_path)
		corpus = tree.getroot()
		reviews = corpus.findall('.//sentence')
			
		sentences_node = Element('sentences')
			
		for review in reviews:
			c_id = review.attrib['id']
			review_text = re.sub(r'\s+'," ",review.find('text').text)
				
			sentence_node = SubElement(sentences_node,'sentence',{'id':str(c_id)})
			SentText_node = SubElement(sentence_node,"text")
			SentText_node.text = html.unescape(review_text)
				
			aspectTerms = review.find('aspectTerms')
				
			list_aspect_terms=[]
				
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
				   
				for aspect_term in aspectTerm:
					pattern1 = r'\s+'
					app_feature = re.sub(pattern1," ",aspect_term.attrib['term'].strip())
					#app_feature_score = aspect_term.attrib['score'].strip()
					app_feature_words = app_feature.split()
						
					#list_aspect_terms.append((app_feature,app_feature_score))
					list_aspect_terms.append(app_feature)
				
				#print(list_aspect_terms)
					# storing aspect with indexes for each sentence
				aspects_with_indexes=[]
					
				if len(list_aspect_terms)>0:
					for aspect_info in list_aspect_terms:
						aspect_term  = aspect_info
						#aspect_score = aspect_info[1]
						if aspect_term in review_text:
							aspects_with_indexes.append((aspect_term,review_text.index(aspect_term)))
						else:
							#print(aspect_term)
							aspect_term_words=aspect_term.split()
							try:
								indexes = [review_text.index(w) for w in aspect_term_words]
								lowest_index= min(indexes)
								highest_index = max(indexes)
								len_last_aspect_word = len(aspect_term_words[len(aspect_term_words)-1])
								consecutive_aspect_term = review_text[lowest_index:highest_index + len_last_aspect_word]
								aspects_with_indexes.append((consecutive_aspect_term,review_text.index(consecutive_aspect_term)))
							except ValueError:
								pass
				
				#print(aspects_with_indexes)
					
				if len(aspects_with_indexes)>0:                    
					sorted_aspects= sorted(aspects_with_indexes, key=lambda x: x[1],reverse=False)
					AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
					for aspect_term in sorted_aspects:
						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term[0]}) 
					
		output_file = open(new_appCat_data_path, 'w' )
		output_file.write(self.prettify_xml(sentences_node))
		output_file.close()

	
	def KeepAspectTerms_1_3_words_with_NOUN(self,AppCategory):
		
		app_data_path="Simulation_II/" + self.dataset + "/" + AppCategory.name + ".xml"
		new_app_data_path="Simulation_III-3/" + self.dataset + "/" + AppCategory.name + ".xml"

		dirName = 'Simulation_III-3/'

		if not os.path.exists(dirName):
			os.mkdir(dirName)

		if not os.path.exists(dirName + "/" + self.dataset):
			os.mkdir(dirName + "/" + self.dataset)

		# if not os.path.exists(dirName + "/" + self.dataset + "/" + AppCategory.name):
		# 	os.mkdir(dirName + "/" + self.dataset + "/" + AppCategory.name)
		
	
		tree = ElementTree.parse(app_data_path)
		corpus = tree.getroot()
		reviews = corpus.findall('.//sentence')
		
		reviews_node = Element('sentences')
		
		#review_counter=0
		#aspect_reviews=0
		
		for review in reviews:
			review_id = review.attrib['id']
			review_text = re.sub(r'\s+'," ",review.find('text').text)
			review_node = SubElement(reviews_node,'sentence',{'id':str(review_id)})
			review_Text_node = SubElement(review_node,"text")
			review_Text_node.text = review_text.strip()
			
			aspectTerms = review.find('aspectTerms')
			
			list_aspect_terms=[]
			
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
			   
				for aspect_term in aspectTerm:
					app_feature = aspect_term.attrib['term'].strip()
					app_feature_words = app_feature.split()
					
					if len(app_feature_words)>=1 and len(app_feature_words)<=3:
						list_aspect_terms.append(app_feature)

														 
				if len(list_aspect_terms)>0:
					AspectTerms_node =  SubElement(review_node,"aspectTerms")

					for aspect_term in list_aspect_terms:
						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term}) 
					
#                     aspect_reviews =  aspect_reviews + 1
			
			#review_counter = review_counter + 1
		
		#print(new_app_data_path)											
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(reviews_node))
		output_file.close()
			
	def prettify_xml(self,elem):
		"""Return a pretty-printed XML string for the Element.
		"""
		rough_string = ElementTree.tostring(elem, 'utf-8')
		reparsed = minidom.parseString(rough_string)
		return reparsed.toprettyxml(indent="  ")
	
	
	def perform_cleaning_step_2(self,lang):
		LIST_REMOVED_ASPECT_TERMS_CODER1=[]
		LIST_REMOVED_ASPECT_TERMS_CODER2=[]
		if lang.lower()=="en":
			for app_category in EN_APPS_CATEGORY:
				#print(app_category.name)
				#print('Coder 1 ->')
				rm_list_coder1 = self.Cleaning_Step2_for_AppCategory(app_category)
				LIST_REMOVED_ASPECT_TERMS_CODER1.extend(rm_list_coder1)
				#print('Coder 2 ->')
				#rm_list_coder2 = self.Cleaning_Step2_for_AppCategory(app_category,ANNOTATORS.CODER2)
				#LIST_REMOVED_ASPECT_TERMS_CODER2.extend(rm_list_coder2)
				#print("################################################")
				#self.FilterAspectMentionSentences(ANNOTATORS.CODER2,app)
				#print('++++++++++++++++++++++++++++++++++++++++++++++++')
				
			print('List of aspect terms (Coder 1) removed with STEP 2')
			print('\n'.join(set(LIST_REMOVED_ASPECT_TERMS_CODER1)))
			#print('List of aspect terms (Coder 2) removed with STEP 2')
			#print('\n'.join(set(LIST_REMOVED_ASPECT_TERMS_CODER2)))
		elif lang.lower()=='de':
			for app_category in APP_CAEGORIES_DE:
				#print(app_category.name)
				rm_list_coder1 = self.Cleaning_Step2_for_AppCategory(app_category)
				#print('++++++++++++++++++++++++++++++++++++++++++++++++')
				LIST_REMOVED_ASPECT_TERMS_CODER1.extend(rm_list_coder1)
			print('List of aspect terms removed with STEP 2')
			print('\n'.join(set(LIST_REMOVED_ASPECT_TERMS_CODER1)))
			
	def perform_cleaning_step_1(self,lang):
		if lang.lower()=="en":
			for app_category in EN_APPS_CATEGORY:
				print(app_category.name)
				#print('Coder 1 ->')
				self.Cleaning_Step1_for_AppCategory(app_category)
				#print('Coder 2 ->')
				#self.Cleaning_Step1_for_AppCategory(app_category,ANNOTATORS.CODER2)
				#print("################################################")
				#self.FilterAspectMentionSentences(ANNOTATORS.CODER2,app)
				print('++++++++++++++++++++++++++++++++++++++++++++++++')
		elif lang.lower()=='de':
			for app_category in APP_CAEGORIES_DE:
				print(app_category.name)
				self.Cleaning_Step1_for_AppCategory(app_category)
				print('++++++++++++++++++++++++++++++++++++++++++++++++')
	
	def AspectTermContainNoun(self,review,aspectTerm):
		
		if self.lang.lower()=='de':
			parse_review = nlp(review)
			for sent in parse_review.sents:
				str_sent = sent.string
				if aspectTerm in str_sent:
					terms_with_pos = [(token.orth_,token.pos_) for token in sent if token.orth_ in aspectTerm.split()]
					isNOUNExist = any([w[1]=='NOUN'or w[1]=='X' or w[1]=='PRON' or w[1]=='PROPN' for w in terms_with_pos])
					return isNOUNExist
		elif self.lang.lower()=='en':
			sents = nltk.sent_tokenize(review)
			for sent in sents:
				if aspectTerm in sent:
					words = nltk.word_tokenize(sent)
					pos_txt = nltk.pos_tag(words,tagset='universal')
					terms_with_pos = [w for w in pos_txt if w[0] in aspectTerm.split()]
				#print(terms_with_pos)
					isNOUNExist = any([w[1]=='NOUN' for w in terms_with_pos])
					return isNOUNExist
				
	def Cleaning_Step2_for_AppCategory(self,AppCategory):    
		 
		app_data_path="Simulation_I/" + self.dataset + "/" + AppCategory.name + ".xml"

		dirName = 'Simulation_II'

		if not os.path.exists(dirName):
			os.mkdir(dirName)

		if not os.path.exists(dirName + "/" + self.dataset):
			os.mkdir(dirName + "/" + self.dataset)

		# if not os.path.exists(dirName + "/" + self.dataset + "/" + AppCategory.name):
		# 	os.mkdir(dirName + "/" + self.dataset + "/" + AppCategory.name)

		new_app_data_path="Simulation_II/" + self.dataset + "/" + AppCategory.name + ".xml"
		
		tree = ElementTree.parse(app_data_path)
		corpus = tree.getroot()
		reviews = corpus.findall('.//sentence')
		
		reviews_node = Element('sentences')
		
#         LIST_OF_GOOD_TERMS=[]
		LIST_OF_REMOVE_TERMS=[]
		
		for review in reviews:
			review_id = review.attrib['id']
			review_text = re.sub(r'\s+'," ",review.find('text').text)
			review_node = SubElement(reviews_node,'sentence',{'id':str(review_id)})
			review_Text_node = SubElement(review_node,"text")
			review_Text_node.text = review_text.strip()
			
			aspectTerms = review.find('aspectTerms')
			
			list_aspect_terms=[]
			
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
			   
				for aspect_term in aspectTerm:
					app_feature = aspect_term.attrib['term'].strip()
					list_aspect_terms.append(app_feature)
				
				if len(list_aspect_terms)>0:
					AspectTerms_node =  SubElement(review_node,"aspectTerms")
					for aspect_term in list_aspect_terms:
						isContainNoun = self.AspectTermContainNoun(review_text,aspect_term)
						if isContainNoun == False:
							LIST_OF_REMOVE_TERMS.append(aspect_term)

						if isContainNoun == True:        
							#print(review_text)
							#print(aspect_term)
							aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term}) 
							
		
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(reviews_node))
		output_file.close()
		return(LIST_OF_REMOVE_TERMS)
	
	def Cleaning_Step1_for_AppCategory(self,AppCategory):    
		
		REMOVE_TERMS=['app','application','software','ap','aap','apps','applications','product','game','messenger','games','games','program','tool','product',                   'angry bird','angry birds','angrybirds','angrybird','drop box','dropbox','whatsapp','whats app','evernote','piczart','picart','picsart','pics art','pinterest','tripadvisor','trip advisor','what\'s app','wats ap','functionality','features','feature','function','functions','skype','snapchat','facebookapp','facebook','spotify','twitter','instagram','wetterapp']
		
		GERMAN_TERMS=["app\'s",'anwendung','anwendungen','spiel','spiele','programm','programme','werkzeug','werkzeuge','softwares','wecker','whatsapp','player','weckerapp','wecker app',"funktioniert","funktion","funktionen",'runtastic','fitness app','music player','player','navi app','nachrichten-app','nachrichten app','sport app','wetter app','wetter','weckapp']
		
		REMOVE_TERMS = REMOVE_TERMS + GERMAN_TERMS

		dirName = 'Simulation_I'

		if not os.path.exists(dirName):
			os.mkdir(dirName)

		if not os.path.exists(dirName + "/" + self.dataset):
			os.mkdir(dirName + "/" + self.dataset)

		# if not os.path.exists(dirName + "/" + self.dataset + "/" + AppCategory.name):
		# 	os.mkdir(dirName + "/" + self.dataset + "/" + AppCategory.name)
		
		app_data_path="Preprocessing/" + self.dataset + "/" + AppCategory.name + ".xml"
		new_app_data_path="Simulation_I/" + self.dataset  + "/" + AppCategory.name + ".xml"
			
		tree = ElementTree.parse(app_data_path)
		corpus = tree.getroot()
		reviews = corpus.findall('.//sentence')
		
		reviews_node = Element('sentences')
		
		#review_counter=0
		#aspect_reviews=0
		
		for review in reviews:
			review_id = review.attrib['id']
			review_text = re.sub(r'\s+'," ",review.find('text').text)
			review_node = SubElement(reviews_node,'sentence',{'id':str(review_id)})
			review_Text_node = SubElement(review_node,"text")
			review_Text_node.text = review_text.strip()
			
			aspectTerms = review.find('aspectTerms')
			
			list_aspect_terms=[]
			
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
			   
				for aspect_term in aspectTerm:
					app_feature = aspect_term.attrib['term'].strip()
					list_aspect_terms.append(app_feature)
				
				
				clean_app_related_terms = [feature for feature in list_aspect_terms  if feature.lower() not in REMOVE_TERMS]

		   
				if len(clean_app_related_terms)>0:
					AspectTerms_node =  SubElement(review_node,"aspectTerms")

					for aspect_term in clean_app_related_terms:
						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term}) 
					
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(reviews_node))
		output_file.close()
	

	def Perform_Preprocessing(self,lang):
		
		if lang.lower()=="en":
			for app_category in EN_APPS_CATEGORY:
				print(app_category.name)
				new_app_data_path="Preprocessing/" + self.dataset +  "/" + app_category.name + ".xml"

				if self.dataset == DATASETS.GUZMAN.name:
					self.Remove_NonConsecutive_Annotations(app_category)

				self.KeepOnly_AspectMentioning_Reviews_EN(app_category)
				self.sort_aspect_terms_by_index_app_reviews(new_app_data_path)
				print('++++++++++++++++++++++++++++++++++++++++++++++++')
		elif lang.lower()=='de':
			for app_category in APP_CAEGORIES_DE:
				new_app_data_path="Preprocessing/" + self.dataset +  "/" + app_category.name + ".xml"
				print(app_category.name)
				self.KeepOnly_AspectMentioning_Reviews_DE(app_category)
				self.sort_aspect_terms_by_index_app_reviews(new_app_data_path)
				print('++++++++++++++++++++++++++++++++++++++++++++++++')

	def AppFeatureExistInReviewText(self,review_text,app_feature):
		sents = nltk.sent_tokenize(review_text)
		
		found_case1 = False
		found_case2 = False
		
		found=False
		
		for sent in sents:    
			pattern1 = r'\s+'
			clean_sent = re.sub(pattern1," ",sent)
			clean_app_feature = re.sub(pattern1," ",app_feature)
			
			if app_feature in clean_sent:
				found_case1 = True
				
			app_feature_tokens = nltk.word_tokenize(clean_app_feature)
			sent_tokens = nltk.word_tokenize(clean_sent)
			
			found_case2 = all([token in sent_tokens for token in app_feature_tokens])
			
			if found_case1 == True or found_case2:
				found=True
				break
		
		return(found)
	
	
	def IsAppFeature_consecutive(self,review_text,app_feature):
		sents = nltk.sent_tokenize(review_text)
		
		is_consecutive = False
	
		for sent in sents:    
			pattern1 = r'\s+'
			clean_sent = re.sub(pattern1," ",sent)
			clean_app_feature = re.sub(pattern1," ",app_feature)
			if clean_app_feature in clean_sent:
				is_consecutive=True
				break
		
		return(is_consecutive)


	def Remove_NonConsecutive_Annotations(self,AppCategory):
		app_data_path="Review_Datasets_XMLFormat/" + self.dataset + "/" + AppCategory.name + ".xml"
		new_app_data_path="Preprocessing/" + self.dataset + "/" + AppCategory.name + ".xml"   

		dirName = 'Preprocessing'

		if not os.path.exists(dirName):
			os.mkdir(dirName)

		if not os.path.exists(dirName + "/" + self.dataset):
			os.mkdir(dirName + "/" + self.dataset)

		# if not os.path.exists(dirName + "/" + self.dataset + "/" + AppCategory.name):
		# 	os.mkdir(dirName + "/" + self.dataset + "/" + AppCategory.name)
		
		tree = ElementTree.parse(app_data_path)
		corpus = tree.getroot()
		sentences = corpus.findall('.//sentence')
		
		sentences_node = Element('sentences')
		
		count=1
		
		feature_annotated_in_title=0
		non_consecutive_app_features=0
		list_non_consecutive_app_features=[]

	  
		for sent in sentences:
			review_id = sent.attrib['id']
			sent_text = re.sub(r'\s+'," ",sent.find('text').text)
			
			aspectTerms = sent.find('aspectTerms')
			
			sentence_node = SubElement(sentences_node,'sentence',{'review-id':str(review_id),'id':str(count) })
			SentText_node = SubElement(sentence_node,"text")
			SentText_node.text = html.unescape(sent_text)
			
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
				AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
				
				for aspect_term in aspectTerm:
					pattern1 = r'\s+'
					app_feature_coder1 = re.sub(pattern1," ",aspect_term.attrib['label1'].strip())
					#score_coder1 = aspect_term.attrib['score1'].strip()
					
					if app_feature_coder1!='NA':
						status_app_feature1 = self.AppFeatureExistInReviewText(sent_text.lower(),app_feature_coder1.lower())
						if status_app_feature1==False:
							feature_annotated_in_title = feature_annotated_in_title + 1
						elif status_app_feature1==True:
							is_consecutive_coder1 = self.IsAppFeature_consecutive(sent_text.lower(),app_feature_coder1.lower())
							
							if is_consecutive_coder1==False:
								non_consecutive_app_features = non_consecutive_app_features + 1
								list_non_consecutive_app_features.append(app_feature_coder1)                            
							elif is_consecutive_coder1==True:
								#aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': app_feature_coder1 ,'score': score_coder1})
								aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': app_feature_coder1})
													
			count = count + 1
				
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(sentences_node))
		output_file.close()

				
	def KeepOnly_AspectMentioning_Reviews_DE(self,AppCategory):
	
		app_data_path="Review_Datasets_XMLFormat/" + self.dataset + "/" + AppCategory.name + ".xml"
		new_app_data_path="Preprocessing/" + self.dataset +  "/" + AppCategory.name + ".xml"   

		dirName = 'Preprocessing'

		if not os.path.exists(dirName):
			os.mkdir(dirName)

		if not os.path.exists(dirName + "/" + self.dataset):
			os.mkdir(dirName + "/" + self.dataset)

		# if not os.path.exists(dirName + "/" + self.dataset + "/" + AppCategory.name):
		# 	os.mkdir(dirName + "/" + self.dataset + "/" + AppCategory.name)
			
			
		tree = ElementTree.parse(app_data_path)
		corpus = tree.getroot()
		reviews = corpus.findall('.//sentence')
		
		reviews_node = Element('sentences')
		
		review_counter=0
		aspect_reviews=0
		
		for review in reviews:
			review_id = review.attrib['id']
			review_text = re.sub(r'\s+'," ",review.find('text').text)
			
			aspectTerms = review.find('aspectTerms')
			
			list_aspect_terms=[]
			
			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
			   
				for aspect_term in aspectTerm:
					app_feature = aspect_term.attrib['term'].strip()
					list_aspect_terms.append(app_feature)
		   
				if len(list_aspect_terms)>0:
					review_node = SubElement(reviews_node,'sentence',{'id':str(review_id)})
					review_Text_node = SubElement(review_node,"text")
					review_Text_node.text = review_text.strip()
				
					AspectTerms_node =  SubElement(review_node,"aspectTerms")
					
					for aspect_term in list_aspect_terms:
						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term}) 
					
					aspect_reviews =  aspect_reviews + 1
			
			review_counter = review_counter + 1
														
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(reviews_node))
		output_file.close()
		
		print("Total reviews are %d" % (review_counter))
		print("Total reviews with aspect terms are %d" % (aspect_reviews))
		print("Total reviews without aspect terms are %d" % (review_counter-aspect_reviews))    
								
			
	def KeepOnly_AspectMentioning_Reviews_EN(self,AppCategory):

		if self.dataset == DATASETS.GUZMAN.name:
			app_data_path="Preprocessing/" + self.dataset + "/" + AppCategory.name + ".xml"
		else:
			app_data_path="Review_Datasets_XMLFormat/" + self.dataset + "/" + AppCategory.name + ".xml"
			dirName = 'Preprocessing'

			if not os.path.exists(dirName):
				os.mkdir(dirName)

			if not os.path.exists(dirName + "/" + self.dataset):
				os.mkdir(dirName + "/" + self.dataset)

			
		new_app_data_path="Preprocessing/" + self.dataset + "/" + AppCategory.name + ".xml"

		tree = ElementTree.parse(app_data_path)
		
		corpus = tree.getroot()

		reviews = corpus.findall('.//sentence')
		
		reviews_node = Element('sentences')
		
		review_counter=0
		reviews_without_aspect_terms=0
		aspect_reviews=0
		
		for review in reviews:
			review_id = review.attrib['id']
			
			review_text = re.sub(r'\s+'," ",review.find('text').text)
			
			aspectTerms = review.find('aspectTerms')
			
			list_aspect_terms=[]
			
			if aspectTerms is not None:
				app_features = aspectTerms.findall('aspectTerm')
			   
				for aspect_term in app_features:
					app_feature = aspect_term.attrib['term'].strip()
					list_aspect_terms.append(app_feature)
		
		   
			if len(list_aspect_terms)> 0:
				
				review_node = SubElement(reviews_node,'sentence',{'id':str(review_id)})
					
				reviewText_node = SubElement(review_node,"text")
				reviewText_node.text = review_text.strip()
					
				# create nodes for each aspect terms for coder1
					
				if len(list_aspect_terms)>0:
					AspectTerms_node =  SubElement(review_node,"aspectTerms")
					
					for aspect_term in list_aspect_terms:
						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term}) 
					
						aspect_reviews =  aspect_reviews + 1
			else:
				reviews_without_aspect_terms = reviews_without_aspect_terms + 1
					
			review_counter = review_counter + 1
														
		output_file = open(new_app_data_path, 'w' )
		output_file.write(self.prettify_xml(reviews_node))
		output_file.close()

if __name__== '__main__':
	args = parser.parse_args()

	review_dataset = args.dataset
	lang = args.lang
	preprocessing_step = args.step

	print(review_dataset,lang,preprocessing_step)
	TS_Analysis = TRANSFORM_DATASET(review_dataset,preprocessing_step,lang)
	TS_Analysis.Transform_Dataset()
