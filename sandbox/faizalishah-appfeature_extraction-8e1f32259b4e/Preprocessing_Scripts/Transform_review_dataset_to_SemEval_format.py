
import pandas as pd
import numpy as np
#from spacy.en import English
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
import re
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
import argparse
import spacy

parser = argparse.ArgumentParser(description='Optional app description')

parser.add_argument('-r','--dataset', type=str,
					help='name of review dataset')

nlp = spacy.load('en_core_web_sm')


from enum import Enum

class MOBILE_APPS_EN(Enum):
	ANGRY_BIRDS = 1
	DROP_BOX= 2
	EVERNOTE = 3
	TRIP_ADVISOR = 5
	PICS_ART = 6
	PINTEREST = 7
	WHATSAPP = 8

class MOBILE_APPS_DE(Enum):
	WEATHER_APPS = 1
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

class SHAH_ANNOTATOR(Enum):
	SHAH_I = 1   # Conerlia     
	SHAH_II = 2  # Hedie


class CONVERT_SEMEVAL(object):
	ReviewSet = None
	TruthSet  = None
	App =  None
	agreementType = None
	
	def __init__(self,app,review_dataset,lang):
		self.TargetApp = app
		self.ReviewDataset = review_dataset
		self.lang = lang
		self.annotation_folder_name = self.ReviewDataset + "_ANNOTATED_REVIEW_DATA"

		if review_dataset=="GUZMAN":
			self.SetAnnotatedAppReviewIDs()
			self.SetAppTruthSet()
		elif review_dataset in ["SHAH_I","SHAH_II"]:
			self.SetAppAnnotations()
		elif review_dataset=="SANGER":
			self.SetAppAnnotations_SANGER()


	def ConvertToSemEvalFormat_SANGER_Annotations(self): 
		filename = "Review_Datasets/SANGER_ANNOTATED_REVIEW_DATA/annotated_reviews/" + self.TargetApp.name.lower() + ".txt"
		
		sentences_node = Element('sentences')
		sentence_id=1
		
		with open(filename, "r") as ins:
			for line in ins:
				e_aspects=[]
				row_split_by_tab = line.split("\t")
				row = line.split("||")
				if len(row)==2:
					info1 = row[0].split('\t')
					review_id = info1[0].strip()
					review_title = info1[1].strip()
					review_body = row[1]

					review_wise_aspect_info = self.ExtractAspectsFromReview(review_id,row_split_by_tab[1]) 
					
					if len(review_wise_aspect_info)!=0:
						for rid,review_info in review_wise_aspect_info.items():
							#print(review_info)
							sentence_node = SubElement(sentences_node,'sentence',{'id':str(rid)})
							SentText_node = SubElement(sentence_node,"text")
							# clean code here
							SentText_node.text = review_body.strip()
							sentence_id = sentence_id + 1 
							
						   
							
							if len(review_info)>0:
								AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
								sorted_aspect_info = sorted(review_info, key=lambda x: x[1])
							# Aspect_Terms
								for aspect_info in sorted_aspect_info:
									#print(aspect_info,len(aspect_info))
									
									aspect_term,start_index,end_index = aspect_info
									aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term ,'from':str(start_index),'to':str(end_index)})
									
									#sentence_id = sentence_id + 1 
								
					else:
						sentence_node = SubElement(sentences_node,'sentence',{'id':str(review_id)})
						SentText_node = SubElement(sentence_node,"text")
							# clean code here
						SentText_node.text = review_body.strip()
						sentence_id = sentence_id + 1 
					  
				  
				else:
					info1 = row[0].split('\t')
					review_id = info1[0]
					review_body = info1[1].strip()
					review_wise_aspect_info = self.ExtractAspectsFromReview(review_id,row_split_by_tab[1])
					
					if len(review_wise_aspect_info)!=0:
						for rid,review_info in review_wise_aspect_info.items():
							sentence_node = SubElement(sentences_node,'sentence',{'id':str(rid)})
							SentText_node = SubElement(sentence_node,"text")
							# clean code here
							SentText_node.text = review_body.strip()
							sentence_id = sentence_id + 1 
							
							if len(review_info)>0:
								AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
								sorted_aspect_info = sorted(review_info, key=lambda x: x[1])
							
							# Aspect_Terms
								for aspect_info in sorted_aspect_info:
									aspect_term,start_index,end_index = aspect_info
							 
									aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': aspect_term ,'from':str(start_index),'to':str(end_index)})
								
								
					else:
						sentence_node = SubElement(sentences_node,'sentence',{'id':str(review_id)})
						SentText_node = SubElement(sentence_node,"text")
							# clean code here
						SentText_node.text = review_body.strip()
						sentence_id = sentence_id + 1 
							
						 
						   
				
		filepath = "Review_Datasets_XMLFormat/SANGER/" +  self.TargetApp.name + ".xml"
		
		output_file = open(filepath, 'w' )
		output_file.write(self.prettify_xml(sentences_node))
		output_file.close()


	def SetAppAnnotations_SANGER(self):
		filename = "Review_Datasets/SANGER_ANNOTATED_REVIEW_DATA/annotations/" + self.TargetApp.name.lower() + ".csv"
		app_annotations = pd.read_csv(filename,sep="\t",names=["Type","ReviewID","startIndex","endIndex","label","reference","Polarity","Related"])
		app_annotations = app_annotations.set_index(app_annotations.ReviewID)
		app_annotations = app_annotations.loc[app_annotations['Type'] == "aspect"]
		app_annotations = app_annotations[["startIndex","endIndex","label","Polarity"]]
		
		self.appTrueAspects = app_annotations
		#print(self.appTrueAspects.shape)

	def SetAppAnnotations(self):
		
		if self.ReviewDataset == SHAH_ANNOTATOR.SHAH_I.name:
			self.annotation_file = "Review_Datasets/SHAH_I_ANNOTATED_REVIEW_DATA/annotations/" + self.TargetApp.name + ".csv"
			self.review_file = "Review_Datasets/SHAH_I_ANNOTATED_REVIEW_DATA/annotated_reviews/" + self.TargetApp.name + ".txt"
		elif self.ReviewDataset == SHAH_ANNOTATOR.SHAH_II.name:
			self.annotation_file = "Review_Datasets/SHAH_II_ANNOTATED_REVIEW_DATA/annotations/" + self.TargetApp.name + ".csv"
			self.review_file = "Review_Datasets/SHAH_II_ANNOTATED_REVIEW_DATA/annotated_reviews/" + self.TargetApp.name + ".txt"
		
		app_annotations = pd.read_csv(self.annotation_file,sep="\t",names=["REVIEW_ID","START_INDEX","END_INDEX","ASPECT_TERM","SENT_CLASS"])
		app_annotations = app_annotations.set_index(app_annotations.REVIEW_ID)
		#app_annotations = app_annotations.loc[app_annotations['ANNOTATION_TYPE'] == "ASPECT"]
		app_annotations = app_annotations[["START_INDEX","END_INDEX","ASPECT_TERM","SENT_CLASS"]]
		
		self.appTrueAspects = app_annotations

	def SaveReviewsWithAnnotationsinSemEvalFormat(self):
		if self.ReviewDataset=="GUZMAN":
			# self.SetAnnotatedAppReviewIDs()
			# self.SetAppTruthSet()
			self.ConvertToSemEvalFormat_GUZMAN_Annotations()
		elif self.ReviewDataset in ["SHAH_I","SHAH_II"]:
			self.ConvertToSemEvalFormat_SHAH_Annotations()
		elif self.ReviewDataset == "SANGER":
			self.ConvertToSemEvalFormat_SANGER_Annotations()


	def ConvertToSemEvalFormat_SHAH_Annotations(self):
		
		sentences_node = Element('sentences')
		sentence_id=1
		line_no=1
		
		review_body=""
		review_id = ""
		prev_review_id=""
		review_offset=0
		prev_review_char_offset = 0
		review_text = ""
		prev_line_chars = 0
		
		base_offset=0
		
		total_char_read_till_review_body=0
		total_line_chars_read=0
		chars_b4_review_body=0
		new_line_chars = 0
		
		with open(self.review_file, "r") as ins:
		   
			for line in ins:
				chars_in_line = len(line)
				
				#if 
				#total_line_chars_read = total_line_chars_read + chars_in_line
				#total_char_read_till_review_body = total_char_read_till_review_body + chars_in_line 
				e_aspects=[]
				#row_split_by_tab = line.split("\t")
					
				text=""
				old_index=0
				new_review_id=""
				for ch in line:
					text = text + ch
					old_index =   old_index  + 1
					
					if ch.isspace():
						if text.strip().isdigit()==True:
							new_review_id = text.strip()
							break
				
				text=""
				chars_b4_review_body= old_index 
				
				# if the line contains review id then text followed after space is part of review body
				if new_review_id!="" and new_review_id.isdigit()==True:
				
					index= 0
					review_body_started= False

					for ch in line:
						review_ch = ch
						index = index + 1

						if index > old_index:
							if review_ch.isspace()==False and review_body_started==False:
								text = text + review_ch
								review_body_started=True
							elif review_body_started == True:
								text = text + review_ch
							elif review_ch.isspace()==True and review_body_started==False:
								chars_b4_review_body = chars_b4_review_body + 1
				else:
						text = line
						
						
					
#                     if review_body_started==True:
#                         # save this review id if the review goes on the next as well
#                         prev_review_id = new_review_id
					
				
				# if the line doesn't contain review id , its the continuation of the old review
							
				if new_review_id=="":
					if prev_review_id!="" and prev_review_id.isdigit()==True:
						review_text  = review_text + text   # append it with the old review text
						new_line_chars = new_line_chars + last_line_chars
						last_line_chars = len(line)
				elif new_review_id!="" and new_review_id.isdigit()==True: #  signal start of a new reviews
					if prev_review_id!="":
						review_id = prev_review_id.strip()                 # save the data of old review id and body          
						review_body = review_text
						review_offset = prev_review_char_offset + new_line_chars
					# extract aspect from sentences in this review
						#print("review id : %s , review_body : %s , offset : %d" % (review_id,review_body,review_offset))
					
						sent_wise_aspect_info = self.ExtractAspectsFromSentences(review_id.strip(),review_body,review_offset)   
						#print(sent_wise_aspect_info)
		
						if len(sent_wise_aspect_info)!=0:
							for sent,sent_info in sent_wise_aspect_info.items():
								sentence_node = SubElement(sentences_node,'sentence',{'id':str(sentence_id)})
								SentText_node = SubElement(sentence_node,"text")
								sent_clean = sent.strip().replace('&amp;#39;','\'')
								sent_clean = sent_clean.strip().replace('&quot;','\"')
								# clean code here
								SentText_node.text = html.unescape(sent_clean)
								sentence_id = sentence_id + 1 

								if len(sent_info)>0:
									AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
								# Aspect_Terms
									for aspect_info in sent_info:
										aspect_term,start_index,end_index,category = aspect_info
										clean_aspect_term = aspect_term.strip().replace('&amp;#39;','\'')
										clean_aspect_term = clean_aspect_term.replace('&quot;','\"')
										clean_aspect_term = html.unescape(clean_aspect_term)
										aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': clean_aspect_term ,'from':str(start_index),'to':str(end_index), 'class' : category})
										#sentence_id = sentence_id + 1 

						else:
							sentence_node = SubElement(sentences_node,'sentence',{'id':str(sentence_id)})
							SentText_node = SubElement(sentence_node,"text")
								# clean code here
							sent_clean = review_body.strip().replace('&amp;#39;','\'')
							sent_clean = sent_clean.strip().replace('&quot;','\"')
								# clean code here
							SentText_node.text = html.unescape(sent_clean)
							sentence_id = sentence_id + 1 
					
						#print("%s#####%s####%d" % (review_id,review_body,review_offset))
						#print("*****************************************************")
				
					prev_review_id = new_review_id     # update prev_review_id with current review id
					review_text = text            # review_text with new review text
					prev_review_char_offset = chars_b4_review_body 

					# print details of the compelted review
				
					if line_no == 1:
						last_line_chars= len(line)
						#print("last line chars->",last_line_chars)
					else:
						new_line_chars = new_line_chars + last_line_chars
						last_line_chars = len(line)
					
						
				line_no = line_no + 1
				
#                 if line_no > 50:
#                     break
		
		if self.ReviewDataset == SHAH_ANNOTATOR.SHAH_I.name:
			xmlfile_path = "Review_Datasets_XMLFormat/SHAH_I/" + self.TargetApp.name + ".xml"
		elif self.ReviewDataset == SHAH_ANNOTATOR.SHAH_II.name:
			xmlfile_path = "Review_Datasets_XMLFormat/SHAH_II/" + self.TargetApp.name + ".xml"
			
		output_file = open(xmlfile_path, 'w' )
		output_file.write(self.prettify_xml(sentences_node))
		output_file.close()
		
		print("Annotations saved in SEM-Eval format sucessfully!!!")

	def ExtractAspectsFromReview(self,review_id,review_text):
	  
		
		review_wise_aspects={}
		
		record_exist =  True
		
		try:
			record = self.appTrueAspects.loc[int(review_id)]
		except KeyError:
			record_exist = False

		if record_exist == True:
			manual_labels =  record['label']
			start_Indexes = record['startIndex']
			end_Indexes =  record['endIndex']
			polarity = record['Polarity']
			
			if isinstance(manual_labels, str):
				startIndex,endIndex = self.AttachTrueAspectToReview(review_text,manual_labels,start_Indexes,end_Indexes)
				#print(review_sents)
				
				if startIndex!=-1 and endIndex!=-1:
					if review_wise_aspects.get(review_id,"NA")=='NA':
						review_wise_aspects[review_id]= [(manual_labels,startIndex,endIndex)]

				elif review_wise_aspects.get(review_id,"NA")=='NA':
					review_wise_aspects[review_id]= []

					
			elif isinstance(manual_labels,pd.Series):
				
				for true_aspect,sIndex,eIndex,polarity in zip(manual_labels,start_Indexes,end_Indexes,polarity):                    
						startIndex,endIndex = self.AttachTrueAspectToReview(review_text,true_aspect,sIndex,eIndex)
				
						if startIndex!=-1 and endIndex!=-1:
							if review_wise_aspects.get(review_id,"NA")=='NA':
								review_wise_aspects[review_id]= [(true_aspect,startIndex,endIndex)]
							else:
								old_aspect_terms = review_wise_aspects[review_id]
								old_aspect_terms.append((true_aspect,startIndex,endIndex))
								review_wise_aspects[review_id]= old_aspect_terms
					
		return(review_wise_aspects)

	def AttachTrueAspectToReview(self,review_text,true_aspect,sIndex,eIndex):
		
		review_sents=[]
		start_indexes=[]
		end_indexes =[]
		aspectTerms=[]
		
		title_comment = review_text.split("||")
		
		if len(title_comment)==2:
			comment = title_comment[1]
			subtract_len = len(title_comment[0]) + len("||")
		else:
			comment =  title_comment[0]
			subtract_len = 0

		#subtract_len = len(title_comment[0]) + len("||")
		sIndex = sIndex - subtract_len
		eIndex = eIndex - subtract_len

		aspect_term = comment[sIndex:eIndex]

		#print("review id = %s , start index = %d, end index = %d" % (review_id,start_Indexes,end_Indexes))

		if aspect_term == true_aspect:
			startIndex=sIndex
			endIndex = eIndex
		else:
			startIndex=-1
			endIndex = -1

		
		return(startIndex,endIndex)

	def AttachTrueAspectToSentence(self,review_text,true_aspect,sIndex,eIndex,sent_class,base_offset):
		
		review_sents=[]
		start_indexes=[]
		end_indexes =[]
		aspectTerms=[]
		sent_classes=[]

		sIndex = sIndex - base_offset
		eIndex = eIndex - base_offset

		sent_index = 0
		prev_sents = []

		for sent in nlp(review_text).sents:
			prev_sents.append(sent.string)
			if sent_index>0:
				prevs_sent_lens = [len(r_sent) for i,r_sent in enumerate(prev_sents) if i < sent_index]
				total_len = sum(prevs_sent_lens)

				new_sIndex = sIndex - total_len
				new_eIndex = eIndex - total_len
			else:
				new_sIndex = sIndex
				new_eIndex = eIndex

			aspect_term = sent.string[new_sIndex:new_eIndex]

			if aspect_term == true_aspect:
				review_sents.append(sent.string)
				start_indexes.append(new_sIndex)
				end_indexes.append(new_eIndex)
				aspectTerms.append(aspect_term)
				sent_classes.append(sent_class)
				#print("True Aspect Term->",true_aspect)
				#print("Extracted Aspect Term->",aspect_term)
			else:
				review_sents.append(sent.string)
				start_indexes.append(-1)
				aspectTerms.append("")
				end_indexes.append(-1)
				sent_classes.append("")

			sent_index = sent_index + 1
		
		return (review_sents,aspectTerms,start_indexes,end_indexes,sent_classes)


	def ExtractAspectsFromSentences(self,review_id,review_text,base_offset):  
		sents_wise_aspects={}
		
		
		record_exist =  True
		
		try:
			record = self.appTrueAspects.loc[review_id]
		except KeyError:
			record_exist = False

		if record_exist == True:
			manual_labels =  record['ASPECT_TERM']
			start_Indexes = pd.to_numeric(record['START_INDEX'],errors='coerce')
			end_Indexes =  pd.to_numeric(record['END_INDEX'],errors='coerce')
			sent_class = record['SENT_CLASS']
			
			#print(start_Indexes)
			
	
			#polarity = record['Polarity']
			
			if isinstance(manual_labels, str):
				review_sents,list_aspect_terms,startIndexes,endIndexes,sent_classes = self.AttachTrueAspectToSentence(review_text,manual_labels,start_Indexes,end_Indexes,sent_class,base_offset)
				#print(review_sents)
				
				for sent_index in range(0,len(review_sents)):
					sent_text = review_sents[sent_index]
					aspect_term= list_aspect_terms[sent_index]
					start_index = int(startIndexes[sent_index])
					end_index  = int(endIndexes[sent_index])
					sent_category = sent_classes[sent_index]
		
					if aspect_term!="":
						if sents_wise_aspects.get(sent_text,"NA")=='NA':
							sents_wise_aspects[sent_text]= [(aspect_term,start_index,end_index,sent_category)]

						else:
							old_aspect_terms = sents_wise_aspects[sent_text]
							old_aspect_terms.append((aspect_term,start_index,end_index,sent_category))
							sents_wise_aspects[sent_text]= old_aspect_terms

					elif sents_wise_aspects.get(sent_text,"NA")=='NA':
						sents_wise_aspects[sent_text]= []

					
			elif isinstance(manual_labels,pd.Series):
				review_sentences = []
				list_aspect_terms=[]
				aspect_start_indexes=[]
				aspect_end_indexes=[]
				list_sent_category=[]
				true_aspects_count=0
				
				for true_aspect,sIndex,eIndex,sent_category in zip(manual_labels,start_Indexes,end_Indexes,sent_class):                    
						review_sents,aspect_terms,startIndexes,endIndexes,categories = self.AttachTrueAspectToSentence(review_text,true_aspect,sIndex,eIndex,sent_category,base_offset)
						
						review_sentences.append(review_sents)
						list_aspect_terms.append(aspect_terms)
						aspect_start_indexes.append(startIndexes)
						aspect_end_indexes.append(endIndexes)
						list_sent_category.append(categories)
						true_aspects_count = true_aspects_count + 1
						
				
				for i in range(0,true_aspects_count):
					sent = review_sentences[i]
					aspect_term= list_aspect_terms[i]
					start_index = aspect_start_indexes[i]
					end_index  = aspect_end_indexes[i]
					sent_category = list_sent_category[i]
					for sent_index in range(0,len(sent)):
						#if sent[sent_index]!="":
						#print("Sentence->",sent[sent_index])
						sent_text = sent[sent_index]
						if aspect_term[sent_index]!="":
							if sents_wise_aspects.get(sent_text,"NA")=='NA':
								sents_wise_aspects[sent_text]= [(aspect_term[sent_index],start_index[sent_index],end_index[sent_index],sent_category[sent_index])]

							else:
								old_aspect_terms = sents_wise_aspects[sent_text]
								old_aspect_terms.append((aspect_term[sent_index],start_index[sent_index],end_index[sent_index],sent_category[sent_index]))
								sents_wise_aspects[sent_text]= old_aspect_terms
												
						elif sents_wise_aspects.get(sent_text,"NA")=='NA':
							sents_wise_aspects[sent_text]= []
  
					#print("##########################")
					
		return(sents_wise_aspects)
	   
	
		
	
	def SetAnnotatedAppReviewIDs(self):

		ds_path="Review_Datasets/" + self.annotation_folder_name + "/app_reviews.csv"
		Reviews = pd.read_csv(ds_path,delimiter='|',header=0) 
		self.AppReviews =  Reviews[ Reviews["project_id"]== self.TargetApp.value]
		self.AppReviews = self.AppReviews[["review_id","title","comment"]]
		self.AppReviews = self.AppReviews.set_index("review_id")
		
		annotated_reviews_path = "Review_Datasets/" + self.annotation_folder_name + "/"  + "agreements.csv"
		TruthSet = pd.read_csv(annotated_reviews_path,delimiter='|',header=0) 
		self.TrueFeatures = TruthSet[["review_id","label1","label2","score1","score2"]]
		self.TrueFeatures = self.TrueFeatures.set_index("review_id")
		
		# reviews which are annotated
		self.annotated_reviews_id = set(self.AppReviews.index.values).intersection(self.TrueFeatures.index.values)
		
	
	def SetAppTruthSet(self):
		self.TrueFeatures = self.TrueFeatures.loc[list(self.annotated_reviews_id)]
	
	def prettify_xml(self,elem):
		"""Return a pretty-printed XML string for the Element.
		"""
		rough_string = ElementTree.tostring(elem, 'utf-8')
		reparsed = minidom.parseString(rough_string)
		return reparsed.toprettyxml(indent="  ")
	
	def ConvertToSemEvalFormat_GUZMAN_Annotations(self):
		review_with_annotations = self.GetReviewsWithAnnotations()
		
		
		new_filepath= "Review_Datasets_XMLFormat/" + self.ReviewDataset + "/"+  self.TargetApp.name + ".xml"
   
		sentences_node = Element('sentences')
	
		count=1 

		for review_id in review_with_annotations.keys():
			review_data = review_with_annotations[review_id]

			sentence_node = SubElement(sentences_node,'sentence',{'review-id':str(review_id),'id':str(count) })
			SentText_node = SubElement(sentence_node,"text")
			SentText_node.text = html.unescape(review_data['review_text'])
			
			annotations = review_data['annotations']

			if len(annotations)!=0:
				AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

				for annotation in annotations:
					#aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': annotation['label2'] , 'score': str(annotation['score2']) })
					aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'label1': annotation['label1']  ,'label2': annotation['label2'], 'score1': str(annotation['score1']), 'score2': str(annotation['score2']) })
					
			count = count + 1
					
		output_file = open(new_filepath, 'w' )
			#print(self.prettify_xml(sentences_node))
		output_file.write(self.prettify_xml(sentences_node))
		output_file.close()
		

	def GetReviewsWithAnnotations(self):
		# Reviews those are annotated
		self.AppReviews = self.AppReviews.loc[list(self.annotated_reviews_id)]
		appComments = self.AppReviews["comment"]
		
		review_with_annotations={}
		
		for review_id in appComments.index:
			reviewText = appComments[review_id].strip()
			app_features = self.TrueFeatures.loc[review_id]
			
			annotations=[]
			
			if type(app_features) == pd.core.series.Series:
				label1 = 'NA' if type(app_features['label1'])==float else app_features['label1']
				label2 = 'NA' if type(app_features['label2'])==float else app_features['label2']
				score1 = 'NA' if math.isnan(app_features['score1'])==True else app_features['score1']
				score2 = 'NA' if math.isnan(app_features['score2'])==True else app_features['score2']
				
				annotation={'label1' : label1 , 'label2' : label2 , 'score1': score1 , 'score2' : score2}
				annotations.append(annotation)
			elif type(app_features) == pd.core.frame.DataFrame:
				for index,row in app_features.iterrows():
					data = ['NA' if type(c)==float else c  for c in row]
					annotation={'label1' : data[0] , 'label2' : data[1], 'score1':data[2] , 'score2' : data[3]}
					annotations.append(annotation)
			
			review_with_annotations[review_id]= {'review_text' : reviewText, 'annotations': annotations}
		
		return(review_with_annotations)


if __name__== '__main__':

	args = parser.parse_args()

	review_dataset = args.dataset
	print(review_dataset)

	app_list=None

	if review_dataset in ['GUZMAN','SHAH_I','SHAH_II']:
		app_list = MOBILE_APPS_EN
		lang= 'EN'
	elif review_dataset=="SANGER":
		app_list = MOBILE_APPS_DE
		lang='DE'

	for app in app_list:
		print(app)
		TS_Analysis = CONVERT_SEMEVAL(app,review_dataset,lang)
		TS_Analysis.SaveReviewsWithAnnotationsinSemEvalFormat()

