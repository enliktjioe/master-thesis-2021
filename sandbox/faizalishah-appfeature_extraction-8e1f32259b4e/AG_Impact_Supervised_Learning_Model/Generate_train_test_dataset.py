from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import re
from xml.dom import minidom
from shutil import copyfile
import string
import os
import html
import sys

from enum import Enum

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
	PIC_ART = 6
	PINTEREST = 7
	WHATSAPP = 8
	
class SEMEVAL_DATASET(Enum):
	LAPTOPS_TRAIN = 1
	LAPTOPS_TEST = 2
	RESTAURANTS_TRAIN = 3
	RESTAURANTS_TEST= 4
	
class DE_APPS_CATEGORY(Enum):
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


def prettify_xml(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ElementTree.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")

def SortAspectTermsByIndex_SemEval():
	main_path='evaluation'
	
	for ds in SEMEVAL_DATASET:

		sentences_node = Element('sentences')
		
		ds_folder = ds.name.split("_")[0]
		filepath = main_path + "/" + ds_folder +  "/" +  ds.name + ".xml"
		tree = ElementTree.parse(filepath)
		corpus = tree.getroot()
		sentences = corpus.findall('.//sentence')
		
		counter=1

		for sent in sentences:
			sent_text = sent.find('text').text
			aspectTerms = sent.find('aspectTerms')

			sentence_node = SubElement(sentences_node,'sentence',{'id':str(counter)})
			SentText_node = SubElement(sentence_node,"text")
			SentText_node.text = sent_text

			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')

				AspectTerms_node =  SubElement(sentence_node,"aspectTerms")
				
				Sent_AspectTermsInfo=[]
		
				for aspect_term in aspectTerm:
					feature_term = aspect_term.attrib['term']
					start_index = int(aspect_term.attrib['from'])
					end_index  =  int(aspect_term.attrib['to'])
					
					aspectTermInfo = {'aspect_term' : feature_term , 'from' : start_index , 'to' : end_index}
					
					Sent_AspectTermsInfo.append(aspectTermInfo)
				
				Sorted_AspectTerms = sorted(Sent_AspectTermsInfo, key=lambda k: k['from']) 
				
				for aspectInfo in Sorted_AspectTerms:
					aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': str(aspectInfo['aspect_term']) ,'from': str(aspectInfo['from']),'to': str(aspectInfo['to'])})
					
				counter= counter + 1
				
		filepath_new = main_path + "/" + ds_folder +  "/" +  ds.name + ".xml"
		output_file = open(filepath_new, 'w' )
		output_file.write(prettify_xml(sentences_node))
		output_file.close()    


def GenerateCrossCategoryTrainset(AppCategory_Test,lang='en'):
   
	main_path =  "evaluation"    

	# if not os.path.exists("CCV" + "/" + ds_name): 
	# 	os.makedirs("CCV" + "/" + ds_name)

	if not os.path.exists(main_path + "/" + AppCategory_Test.name): 
		os.makedirs(main_path+ "/" + AppCategory_Test.name)

	AppCatTrainData = main_path + "/" + AppCategory_Test.name +  "/" + AppCategory_Test.name + "_TRAIN" +  ".xml"                

	AppCatTestData_source = main_path + "/" + AppCategory_Test.name + ".xml"
	AppCatTestData_dest = main_path + "/" + AppCategory_Test.name +  "/" + AppCategory_Test.name +  "_TEST.xml"                

	copyfile(AppCatTestData_source,AppCatTestData_dest)


	sentences_node = Element('sentences')
	
	if lang.lower()=='en':
		APPS_CATEGORY = EN_APPS_CATEGORY
	elif lang.lower()=='de':
		APPS_CATEGORY = DE_APPS_CATEGORY

	counter=1

	for appCatTest in APPS_CATEGORY:
		if appCatTest.name!= AppCategory_Test.name:
			print("Opening app %s features" % (appCatTest.name))

			filepath = main_path + "/" + appCatTest.name +  ".xml"                
			tree = ElementTree.parse(filepath)
			corpus = tree.getroot()
			sentences = corpus.findall('.//sentence')

			for sent in sentences:
				sent_text = sent.find('text').text
				#print(sent_text)
				review_id = sent.attrib['id']
				aspectTerms = sent.find('aspectTerms')

				sentence_node = SubElement(sentences_node,'sentence',{'id':str(counter)})
				SentText_node = SubElement(sentence_node,"text")
				SentText_node.text = sent_text

				if aspectTerms is not None:
					aspectTerm = aspectTerms.findall('aspectTerm')

					AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

					for aspect_term in aspectTerm:
						feature_term = aspect_term.attrib['term']

						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': feature_term})
				
				counter = counter + 1
		

	output_file = open(AppCatTrainData, 'w' )
	output_file.write(prettify_xml(sentences_node))
	output_file.close()
	
	#copyfile(AppTestData_Source,AppTestData_Dest)

	print("Total Sentences in Train Set = %d" % (counter))


def Generate_OneSingle_SEMEval_Dataset():

	SortAspectTermsByIndex_SemEval()
	
	sentences_node = Element('sentences')
	semeval_counter=1
	counter=1


	main_path_SemEval='evaluation'

	SemEvalTrainData = main_path_SemEval + "/SEMEVAL/"

	if not os.path.exists(SemEvalTrainData): 
		os.makedirs(SemEvalTrainData)

	SemEvalTrainData = SemEvalTrainData + "SEMEVAL_TEST.xml"
	
	for ds in SEMEVAL_DATASET:
		ds_folder = ds.name.split("_")[0]
		filepath = main_path_SemEval + "/" +  ds_folder +  "/" +  ds.name + ".xml"

		tree = ElementTree.parse(filepath)
		corpus = tree.getroot()
		sentences = corpus.findall('.//sentence')

		for sent in sentences:
			sent_text = sent.find('text').text
			aspectTerms = sent.find('aspectTerms')

			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
				sentence_node = SubElement(sentences_node,'sentence',{'id':str(counter)})
				SentText_node = SubElement(sentence_node,"text")
				SentText_node.text = sent_text

				AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

				for aspect_term in aspectTerm:
					feature_term = aspect_term.attrib['term']
					#start_index = int(aspect_term.attrib['from'])
					#end_index  =  int(aspect_term.attrib['to'])
			#polarity = aspect_term.attrib['polarity']
			
					#app_feature_words = feature_term.split()
				   
					
					aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': feature_term })

				semeval_counter = semeval_counter + 1
				counter = counter + 1

	output_file = open(SemEvalTrainData, 'w' )
	output_file.write(prettify_xml(sentences_node))
	output_file.close()
	

def GenerateCrossCategoryTrainset_with_SEMEval_Extended(AppCategory_Test,lang='en'):

	SortAspectTermsByIndex_SemEval()
	
	sentences_node = Element('sentences')
	semeval_counter=1
	counter=1
	
	main_path_SemEval='evaluation'
	
	for ds in SEMEVAL_DATASET:
		ds_folder = ds.name.split("_")[0]
		filepath = main_path_SemEval + "/" +  ds_folder +  "/" +  ds.name + ".xml"

		tree = ElementTree.parse(filepath)
		corpus = tree.getroot()
		sentences = corpus.findall('.//sentence')

		for sent in sentences:
			sent_text = sent.find('text').text
			aspectTerms = sent.find('aspectTerms')

			if aspectTerms is not None:
				aspectTerm = aspectTerms.findall('aspectTerm')
				sentence_node = SubElement(sentences_node,'sentence',{'id':str(counter)})
				SentText_node = SubElement(sentence_node,"text")
				SentText_node.text = sent_text

				AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

				for aspect_term in aspectTerm:
					feature_term = aspect_term.attrib['term']
					#start_index = int(aspect_term.attrib['from'])
					#end_index  =  int(aspect_term.attrib['to'])
			#polarity = aspect_term.attrib['polarity']
			
					#app_feature_words = feature_term.split()
				   
					
					aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': feature_term })

				semeval_counter = semeval_counter + 1
				counter = counter + 1
	
	print("Sentences added from  from Laptop and Restaurant datasets are = %d" % (semeval_counter))


	main_path =  "evaluation"    

	# if not os.path.exists("CCV_EXT" + "/" + ds_name): 
	# 	os.makedirs("CCV_EXT" + "/" + ds_name)

	if not os.path.exists(main_path + "/" + AppCategory_Test.name): 
		os.makedirs(main_path + "/" + AppCategory_Test.name)

	AppCatTrainData = main_path + "/" + AppCategory_Test.name +  "/" + AppCategory_Test.name + "_TRAIN" +  ".xml"                


	AppCatTestData_source = main_path + "/" + AppCategory_Test.name + ".xml"
	AppCatTestData_dest = main_path + "/" + AppCategory_Test.name +  "/" + AppCategory_Test.name +  "_TEST.xml"                

	copyfile(AppCatTestData_source,AppCatTestData_dest)

	sort_aspect_terms_by_index_app_reviews(AppCategory_Test)
	
	apps_counter=1
	
	for appCategory in EN_APPS_CATEGORY:
		if appCategory.name!= AppCategory_Test.name:
			print("Opening app %s features" % (appCategory.name))

			filepath = main_path + appCategory.name +  ".xml" 
			#print(filepath)
			tree = ElementTree.parse(filepath)
			corpus = tree.getroot()
			sentences = corpus.findall('.//sentence')

			for sent in sentences:
				sent_text = sent.find('text').text
				aspectTerms = sent.find('aspectTerms')

				sentence_node = SubElement(sentences_node,'sentence',{'id':str(counter)})
				SentText_node = SubElement(sentence_node,"text")
				SentText_node.text = sent_text

				if aspectTerms is not None:
					aspectTerm = aspectTerms.findall('aspectTerm')

					AspectTerms_node =  SubElement(sentence_node,"aspectTerms")

					for aspect_term in aspectTerm:
						feature_term = aspect_term.attrib['term']

						aspectTerm_node = SubElement(AspectTerms_node,"aspectTerm",{'term': feature_term})
				
				apps_counter = apps_counter + 1
				counter = counter + 1
		

	output_file = open(AppCatTrainData, 'w' )
	output_file.write(prettify_xml(sentences_node))
	output_file.close()
	
	# copyfile(AppTestData_source,AppTestData_dest)


if __name__== '__main__':

	training_procedure= sys.argv[1]
	ds_lang = sys.argv[2]
	
	#training_procedure= "CCV_EXT"


	# if not os.path.exists(training_procedure): 
	# 	os.makedirs(training_procedure)

	#args = parser.parse_args()

	#review_dataset = args.dataset
	#review_dataset="GUZMAN"
	#print(review_dataset)

	#$folder_path="Preprocessing/GUZMAN/"

	appCat_list=None

	if ds_lang.lower() =='en':
		appCat_list = EN_APPS_CATEGORY
	elif ds_lang.lower()=='de':
		appCat_list = DE_APPS_CATEGORY

	for appCat in appCat_list:
		print(appCat.name)
		if training_procedure=="CCV":
			GenerateCrossCategoryTrainset(appCat,ds_lang)
		elif training_procedure=="CCV_EXT":
			GenerateCrossCategoryTrainset_with_SEMEval_Extended(appCat,ds_lang)
		elif training_procedure == "SCV_EXT":
			#print("SCV_EXT")
			Generate_OneSingle_SEMEval_Dataset()
		
