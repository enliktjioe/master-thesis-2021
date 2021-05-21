from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import numpy as np
from nltk.tree import Tree
from nltk.util import ngrams
from os import listdir
from os.path import isfile, join
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.metrics import precision_recall_fscore_support
import spacy
from sklearn.feature_extraction.text import CountVectorizer
import time
import ast
import csv

class SentenceClassification:
	def __init__(self):
		self.setDatasetFeatures()
	 
	def setDatasetFeatures(self):
		
		self.df_dataset = pd.read_csv('../Review_Dataset/Gu_Dataset_features.csv',index_col=False)	
		
	def EvaluateModelOnTestSet(self,ds_test,model,vec):
		
		test_feature_dicts=[]
		true_labels=[]
		 
		for index,row in ds_test.iterrows():
			features=self.SentenceFeatures(row)
			test_feature_dicts.append(features)
			true_labels.append(row['class'])
		
		test_X = vec.transform(test_feature_dicts)

		#print(true_labels)
		
		# Predict the test data labels
		pred_Y = model.predict(test_X)
		
		precision,recall,fscore,support = precision_recall_fscore_support(true_labels,pred_Y,labels=['E','P','R','B','N'])
		return precision, recall, fscore
		

	def Train_n_EvaluateOnTestData(self):

		train, test = train_test_split(self.df_dataset, test_size=0.2)

		train_X,feat_transform,class_labels = self.GenerateFeatureMatrix(train)

		TRAIN_LABELS=np.array(class_labels)
		model = LogisticRegression(solver='lbfgs',multi_class='multinomial',C=.09)
		
		model.fit(train_X,TRAIN_LABELS)

		precision,recall,fscore = self.EvaluateModelOnTestSet(test,model,feat_transform)
		
		return precision, recall, fscore

	def SentenceFeatures(self,row):

		sentence = ast.literal_eval((row['tagged_sent']))

		# pos tag features
		POS_TAGS_feature = '-'.join(tag for (word,tag) in sentence)
		
		all_char_grams = ast.literal_eval(row['char_grams'])
		
		features = {}
		
		for char_gram in all_char_grams:
			features['{}'.format(char_gram)] = True
		
		# root word of a sentence

		features['ROOT({})'.format(row['root'])] = True
	
		features['{}'.format(POS_TAGS_feature)] = True
		
		features['{}'.format(row['parse_tree'])]= True
		
		features['{}'.format(row['dep_tree'])]= True
		
		return features


	def GenerateFeatureMatrix(self,ds):
		feature_dicts=[]
		CLASS_LABELS=[]

		for index,row in ds.iterrows():
			features=self.SentenceFeatures(row)
			feature_dicts.append(features)
			CLASS_LABELS.append(row['class'])
		
		assert len(feature_dicts) == ds.shape[0]
		
		vec = DictVectorizer()
		feature_matrix = vec.fit_transform(feature_dicts)
		return feature_matrix,vec,CLASS_LABELS

if __name__ == '__main__':

		startTime = time.time()
		obj=SentenceClassification()
		maxIteratioins = 10

		average_precision_eval, average_recall_eval, average_fscore_eval= ([] for i in range(3))
		average_precision_praise, average_recall_praise, average_fscore_praise= ([] for i in range(3))
		average_precision_request,average_recall_request, average_fscore_request= ([] for i in range(3))
		average_precision_bug, average_recall_bug, average_fscore_bug = ([] for i in range(3))
		average_precision_others, average_recall_others, average_fscore_others = ([] for i in range(3))

		with open('BoC_n_Linguistic_Model_Results.csv','w') as f:
			writer = csv.writer(f,lineterminator='\n')
			writer.writerow(['Iteration','P','R','F1','P','R','F1','P','R','F1','P','R','F1','P','R','F1'])

		
			for i in range(0,maxIteratioins):
				
				print('############Iteration # %d###############' % (i+1))
				
				#obj.SplitDataintoTrainTest()
				precision,recall,fscore = obj.Train_n_EvaluateOnTestData()
				
				average_precision_eval.append(precision[0])
				average_recall_eval.append(recall[0])
				average_fscore_eval.append(fscore[0])
				
				average_precision_praise.append(precision[1])
				average_recall_praise.append(recall[1])
				average_fscore_praise.append(fscore[1])
				
				average_precision_request.append(precision[2])
				average_recall_request.append(recall[2])
				average_fscore_request.append(fscore[2])
				
				average_precision_bug.append(precision[3])
				average_recall_bug.append(recall[3])
				average_fscore_bug.append(fscore[3])
				
				average_precision_others.append(precision[4])
				average_recall_others.append(recall[4])
				average_fscore_others.append(fscore[4])

				lst = [i+1,precision[0],recall[0],fscore[0],precision[1],recall[1],fscore[1]]
				lst += [precision[2],recall[2],fscore[2],precision[3],recall[3],fscore[3]]
				lst += [precision[4],recall[4],fscore[4]]

				writer.writerow(lst)

				print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature evaluation)" % (precision[0],recall[0],fscore[0]))
				print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (praise)" % (precision[1],recall[1],fscore[1]))
				print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature request)" % (precision[2],recall[2],fscore[2]))
				print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (bug report)" % (precision[3],recall[3],fscore[3]))
				print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (others)" % (precision[4],recall[4],fscore[4]))
				
				print('+++++++++++++++ITERATION FINISHED++++++++++++++++++++++++++++')
			
			
			print("###########Average results for each class over 10 iterations####################")
			
			print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature evaluation)" % (np.mean(average_precision_eval),np.mean(average_recall_eval),np.mean(average_fscore_eval)))
			print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (praise)" % (np.mean(average_precision_praise),np.mean(average_recall_praise),np.mean(average_fscore_praise)))
			print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature request)" % (np.mean(average_precision_request),np.mean(average_recall_request),np.mean(average_fscore_request)))
			print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (bug report)" % (np.mean(average_precision_bug),np.mean(average_recall_bug),np.mean(average_fscore_bug)))
			print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (others)" % (np.mean(average_precision_others),np.mean(average_recall_others),np.mean(average_fscore_others)))

			print('The script finished in {0} seconds'.format(time.time() - startTime))