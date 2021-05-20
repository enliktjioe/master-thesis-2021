import nltk
from nltk.stem.snowball import SnowballStemmer
import time
import numpy as np
import pickle

stemmer = SnowballStemmer("english")

class Evaluate:
	def __init__(self,app,dict_true_n_extracted_features,extracted_features,eval_config,eval_type):
		self.TestApp = app
		self.dict_True_n_Extracted_Features=dict_true_n_extracted_features
		self.predicted_features = extracted_features
		self.Evaluation_Config = eval_config
		self.Evaluation_Type = eval_type

	def PerformEvaluation(self):        
		self.predicted_aspects_list=[]
		self.true_aspects_list = []
		self.true_aspects_list_stemmed = []
		self.predicted_aspects_list_stemmed=[]
		# 
		tp_safe=0
		fp_safe=0
		fn_safe=0
	
		for review_id in self.dict_True_n_Extracted_Features.keys():   
			review_level_features_info  = self.dict_True_n_Extracted_Features[review_id]
			true_features = self.dict_True_n_Extracted_Features[review_id]['true_features']
			predicted_features = self.dict_True_n_Extracted_Features[review_id]['predicted_features']
			review_text = review_level_features_info['review_sent']
			
			if self.Evaluation_Config.value == 2:
				true_features = [w for w in true_features if len(w.split())>=2 and len(w.split())<=4]
			
			for true_app_feature in true_features:
				app_feature_stemmed= ' '.join([stemmer.stem(w) for w in true_app_feature.lower().split()])
				self.true_aspects_list_stemmed .append(app_feature_stemmed)
			
			if self.Evaluation_Type.value==1:
				# Token based exact match
				#print('*************TOKEN BASED EXACT MATCH******************')
				tps,fps,fns, revise_extracted_feature_info = self.Token_Based_Exact_Match(true_features,predicted_features)				
			elif self.Evaluation_Type.value==2: 			
				#print('*************TOKEN BASED PARTIAL MATCH******************')	
				tps,fps,fns, revise_extracted_feature_info = self.Token_Based_Partial_Match(true_features,predicted_features)								
			elif self.Evaluation_Type.value==5:
				#print('*************TOKEN BASED SUBSET MATCH ******************')	
				tps,fps,fns, revise_extracted_feature_info = self.Token_Based_Subset_Matching(true_features,predicted_features)

			if self.Evaluation_Type.value==1 or self.Evaluation_Type.value==2 or self.Evaluation_Type.value == 5:
				self.dict_True_n_Extracted_Features[review_id]['predicted_features'] = revise_extracted_feature_info
				
				tp_safe = tp_safe + tps
				fp_safe = fp_safe + fps
				fn_safe = fn_safe + fns
			

			for pred_app_feature_info in predicted_features:
				pred_app_feature = pred_app_feature_info[0]
				pred_app_feature_stemmed= ' '.join([stemmer.stem(w) for w in pred_app_feature.lower().split()])
				self.predicted_aspects_list_stemmed.append(pred_app_feature_stemmed)

			
		
		#print('True app features->',set(self.true_aspects_list_stemmed))
		#print('Predicted app features->',len(self.predicted_aspects_list_stemmed))
		#print('Predicted app features->',len(set(self.predicted_aspects_list_stemmed)))
		#print('#####################TOKEN-BASED EVALUATION#######################')

		#print("Total true features ->", len(set(self.true_aspects_list_stemmed)))

		if self.Evaluation_Type.value==1:
				# Token based exact match
				print('*************TOKEN BASED EXACT MATCH******************')			
		elif self.Evaluation_Type.value==2: 			
			print('*************TOKEN BASED PARTIAL MATCH******************')	
		elif self.Evaluation_Type.value==5:
			print('*************TOKEN BASED SUBSET MATCH ******************')	

		if self.Evaluation_Type.value==3:
			print('*************TYPE BASED EXACT MATCH ******************')	
			tp_safe,fp_safe,fn_safe = self.Type_Based_Exact_Matching(list(set(self.true_aspects_list_stemmed)),list(set(self.predicted_aspects_list_stemmed)))
		elif self.Evaluation_Type.value==4:
			print('*************TYPE BASED PARTIAL MATCH ******************')	
			tp_safe,fp_safe,fn_safe = self.Type_Based_Partial_Matching(list(set(self.true_aspects_list_stemmed)),list(set(self.predicted_aspects_list_stemmed)))

		print('TP = %d, FP = %d , FN = %d' % (tp_safe,fp_safe,fn_safe))
		try:
			precision_safe = tp_safe/(tp_safe+fp_safe)
		except ZeroDivisionError as err:
			precision_safe = 0
		try:
			recall_safe = tp_safe/(tp_safe+fn_safe)
		except ZeroDivisionError as err:
			recall_safe = 0
		try:
			fscore_safe = 2*((precision_safe*recall_safe)/(precision_safe+recall_safe))
		except ZeroDivisionError as err:
			fscore_safe = 0

		evaluation_metric = {'precision' : '%.3f' % precision_safe ,'recall' : '%.3f' % recall_safe,'fscore' : '%.3f' % fscore_safe}
		print('Precision : %.3f , Recall , %.3f , F1-score : %.3f' % (precision_safe,recall_safe,fscore_safe))        

			
		return self.dict_True_n_Extracted_Features,evaluation_metric


	def Token_Based_Exact_Match(self,review_true_features,review_extracted_features):
		app_true_features = review_true_features.copy()    
		predicted_features_review = review_extracted_features.copy()        
			
		tps = 0
		fps = 0
		fns = 0
			
		for pindex,pred_feature in enumerate(predicted_features_review):
			pred_feature_words = pred_feature[0].lower().split()
			found=False
			true_index = -1
			for t_index,true_feature in enumerate(app_true_features):
				true_feature_words = true_feature.lower().split()
					
				if len(pred_feature_words) == len(true_feature_words):
					set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				else:
					set_match = False
					
				if set_match==True:
					found=True
					true_index = t_index
					break

			if found == True:
				tps = tps  + 1
				review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
				#print("TP ->", pred_feature)
				del app_true_features[true_index]

			else:
				# for t_index,true_feature in enumerate(app_true_features):
				# 	true_feature_words = true_feature.lower().split()
				# 	if len(pred_feature_words) != len(true_feature_words):
				# 		if len(pred_feature_words)  > len(true_feature_words):
				# 			set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				# 		elif len(true_feature_words) > len(pred_feature_words):
				# 			set_match = all([pred_word in true_feature_words for pred_word in pred_feature_words])
				# 		else:
				# 			set_match = False
				# 	else:
				# 		set_match = False

				# 	if set_match==True:
				# 		found=True
				# 		true_index = t_index
				# 		break

				# if found == True:
				# 	tps = tps  + 1
				# 	review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
				# 	#print("TP -> ",pred_feature)
				# 	del app_true_features[true_index]
				# else:
				fps =  fps  +  1
				   # print("FP-> ",pred_feature)
				review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'FP')
						
		fns = len(review_true_features) - tps
	   
		return tps,fps,fns, review_extracted_features

	def Token_Based_Partial_Match(self,review_true_features,review_extracted_features):
		app_true_features = review_true_features.copy()    
		predicted_features_review = review_extracted_features.copy()        
			
		tps = 0
		fps = 0
		fns = 0
			
		for pindex,pred_feature in enumerate(predicted_features_review):
			pred_feature_words = pred_feature[0].lower().split()
			found=False
			true_index = -1
			for t_index,true_feature in enumerate(app_true_features):
				true_feature_words = true_feature.lower().split()
					
				if len(pred_feature_words) == len(true_feature_words):
					set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				else:
					set_match = False
					
				if set_match==True:
					found=True
					true_index = t_index
					break

			if found == True:
				tps = tps  + 1
				review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
				del app_true_features[true_index]

			else:
				for t_index,true_feature in enumerate(app_true_features):
					true_feature_words = true_feature.lower().split()
					len_difference = abs(len(pred_feature_words) - len(true_feature_words))
					if len_difference == 1:
						if len(pred_feature_words)  > len(true_feature_words):
							set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
						elif len(true_feature_words) > len(pred_feature_words):
							set_match = all([pred_word in true_feature_words for pred_word in pred_feature_words])
						else:
							set_match = False
					else:
						set_match = False

					if set_match==True:
						found=True
						true_index = t_index
						break

				if found == True:
					tps = tps  + 1
					review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
					#print("TP -> ",pred_feature)
					del app_true_features[true_index]
				else:
					fps =  fps  +  1
					review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'FP')
						
		fns = len(review_true_features) - tps
	   
		return tps,fps,fns, review_extracted_features

	def Type_Based_Partial_Matching(self,true_features,extracted_features):
		app_true_features =  true_features.copy()    
		app_predicted_features = extracted_features.copy()        
			
		tps = 0
		fps = 0
		fns = 0
			
		for pindex,pred_feature in enumerate(app_predicted_features):
			pred_feature_words = pred_feature.lower().split()
			found=False
			true_index = -1
			for t_index,true_feature in enumerate(app_true_features):
				true_feature_words = true_feature.lower().split()
					
				if len(pred_feature_words) == len(true_feature_words):
					set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				else:
					set_match = False
					
				if set_match==True:
					found=True
					true_index = t_index
					break

			if found == True:
				tps = tps  + 1
				del app_true_features[true_index]

			else:
				for t_index,true_feature in enumerate(app_true_features):
					true_feature_words = true_feature.lower().split()
					len_difference = abs(len(pred_feature_words) - len(true_feature_words))
					if len_difference == 1:
						if len(pred_feature_words)  > len(true_feature_words):
							set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
						elif len(true_feature_words) > len(pred_feature_words):
							set_match = all([pred_word in true_feature_words for pred_word in pred_feature_words])
						else:
							set_match = False
					else:
						set_match = False

					if set_match==True:
						found=True
						true_index = t_index
						break

				if found == True:
					tps = tps  + 1
					#review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
					#print("TP -> ",pred_feature)
					del app_true_features[true_index]
				else:
					fps =  fps  +  1
					
						
		fns = len(true_features) - tps
	   
		return tps,fps,fns

	def Type_Based_Exact_Matching(self,true_features,extracted_features):
		app_true_features =  true_features.copy()    
		app_predicted_features = extracted_features.copy()        
			
		tps = 0
		fps = 0
		fns = 0
			
		for pindex,pred_feature in enumerate(app_predicted_features):
			pred_feature_words = pred_feature.lower().split()
			found=False
			true_index = -1
			for t_index,true_feature in enumerate(app_true_features):
				true_feature_words = true_feature.lower().split()
					
				if len(pred_feature_words) == len(true_feature_words):
					set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				else:
					set_match = False
					
				if set_match==True:
					found=True
					true_index = t_index
					break

			if found == True:
				tps = tps  + 1
				del app_true_features[true_index]

			else:
				fps =  fps  +  1
						
		fns = len(true_features) - tps
	   
		return tps,fps,fns

		 
	def Token_Based_Subset_Matching(self,review_true_features,review_extracted_features):
		app_true_features = review_true_features.copy()    
		predicted_features_review = review_extracted_features.copy()        
			
		tps = 0
		fps = 0
		fns = 0
			
		for pindex,pred_feature in enumerate(predicted_features_review):
			pred_feature_words = pred_feature[0].lower().split()
			found=False
			true_index = -1
			for t_index,true_feature in enumerate(app_true_features):
				true_feature_words = true_feature.lower().split()
					
				if len(pred_feature_words) == len(true_feature_words):
					set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
				else:
					set_match = False
					
				if set_match==True:
					found=True
					true_index = t_index
					break

			if found == True:
				tps = tps  + 1
				review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
				#print("TP ->", pred_feature)
				del app_true_features[true_index]

			else:
				for t_index,true_feature in enumerate(app_true_features):
					true_feature_words = true_feature.lower().split()
					if len(pred_feature_words) != len(true_feature_words):
						if len(pred_feature_words)  > len(true_feature_words):
							set_match = all([true_word in pred_feature_words for true_word in true_feature_words])
						elif len(true_feature_words) > len(pred_feature_words):
							set_match = all([pred_word in true_feature_words for pred_word in pred_feature_words])
						else:
							set_match = False
					else:
						set_match = False

					if set_match==True:
						found=True
						true_index = t_index
						break

				if found == True:
					tps = tps  + 1
					review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'TP')
					#print("TP -> ",pred_feature)
					del app_true_features[true_index]
				else:
					fps =  fps  +  1
				   # print("FP-> ",pred_feature)
					review_extracted_features[pindex]= (pred_feature[0],pred_feature[1],'FP')
						
		fns = len(review_true_features) - tps
	   
		return tps,fps,fns, review_extracted_features

