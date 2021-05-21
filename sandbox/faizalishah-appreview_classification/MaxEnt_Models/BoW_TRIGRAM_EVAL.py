import numpy as np
import pandas as pd
import time
from os import listdir
from os.path import isfile, join
import nltk
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from nltk.stem.snowball import SnowballStemmer
import csv
import pickle

stemmer = SnowballStemmer("english")


class SentenceClassification:
	def __init__(self):
		self.setDataset()

	def setDataset(self):
		dataset_path = "../Review_Dataset"

		self.df_dataset= pd.DataFrame(columns=('class','sentence'))

		file_list = [f for f in listdir(dataset_path ) if isfile(join(dataset_path, f))]

		for file_path in file_list:
			print(file_path)
			file_full_path = dataset_path + "/" + file_path
			df = pd.read_csv(file_full_path)
			class_type=[]
			for index, row in df.iterrows():
				if isinstance(row[1], str):
					clean_sent = self.CleanSentence(row[1])
					data_row= {'sentence': clean_sent, 'class': row[0]}    

					self.df_dataset = self.df_dataset.append(data_row,ignore_index=True)  


	def AnalayzeFPsFnS(self,df_test_reviews,review_class):
		df_fps = df_test_reviews[np.logical_and(df_test_reviews['pred_class']==review_class,df_test_reviews['true_class']!=review_class)]
		df_fns = df_test_reviews[np.logical_and(df_test_reviews['pred_class']!=review_class,df_test_reviews['true_class']==review_class)]

		df_fps.to_csv(review_class + "_FPs_291018.csv", sep='\t')
		df_fns.to_csv(review_class + "_FNs_291018.csv", sep='\t')
		
	
	def SplitDataintoTrainTest(self):
		train, test = train_test_split(self.df_dataset, test_size=0.2)

		self.TRAIN_SENTENCES=[]
		self.TRAIN_LABELS = []

		#print("####APPS in Train-set########")

		for index,row in train.iterrows():
			#print(row['sentence'])
			if isinstance(row['sentence'], str):
				self.TRAIN_SENTENCES.append(row['sentence'])
				self.TRAIN_LABELS.extend(row['class'])
				#print(row['AppDesc_Status'])
				#self.train_appDesc_features.extend(row['AppDesc_Status'])


#         print("# of examples in training-set are = %d" % (len(self.TRAIN_SENTENCES)))
#         print("Distribution of classes in training-set are ->")
#         print(Counter(self.TRAIN_LABELS))


		self.TEST_SENTENCES=[]
		self.TEST_LABELS = []
		#self.TEST_appDesc_features=[]

#         print("")
#         print("#####Apps in Test-set#######")

		for index,row in test.iterrows():
			if isinstance(row['sentence'], str):
				self.TEST_SENTENCES.append(row['sentence'])
				self.TEST_LABELS.extend(row['class'])
				#self.TEST_appDesc_features.extend(row['AppDesc_Status'])

		print("# of examples in test-set are = %d" % (len(self.TEST_SENTENCES)))
		print("Distribution of classes in test-set are->")
		print(Counter(self.TEST_LABELS))
	
	def EvaluateModelOnTestSet(self):
		
#         test_review_sents = [sent.lower() for sent in self.TEST_SENTENCES]
#         sequences = self.tk.texts_to_sequences(test_review_sents)
#         test_data = pad_sequences(sequences, maxlen=4028,padding='post')
#         test_data_array = np.array(test_data)
		
		X = self.vectorizer.transform(self.TEST_SENTENCES)
		test_data_array = X.toarray()

		#appDesc_features = np.array(self.TEST_appDesc_features)
		#appDesc_features = appDesc_features.astype(int)
		test_X = test_data_array #np.column_stack((test_data_array,appDesc_features))
		
		pred_Y = self.model.predict(test_X)
		
		score_matrix = confusion_matrix(self.TEST_LABELS,pred_Y,labels=['E','P','R','B','N'])

		print(score_matrix)

		d = {'review_sent' : self.TEST_SENTENCES, 'true_class':self.TEST_LABELS,'pred_class':pred_Y}

		df_test = pd.DataFrame(d,columns=['review_sent','true_class','pred_class'])

		# Save FPs and FNS for the relevant classes
		#self.AnalayzeFPsFnS(df_test,'R')
		#self.AnalayzeFPsFnS(df_test,'B')
		#self.AnalayzeFPsFnS(df_test,'E')
		
		# Evaluation
		
		tp_eval = score_matrix[0,0]
		fp_eval =  score_matrix[1,0] + score_matrix[2,0] + score_matrix[3,0] + score_matrix[4,0]
		fn_eval =  (score_matrix[0,0] + score_matrix[0,1] + score_matrix[0,2] + score_matrix[0,3] + score_matrix[0,4]) - score_matrix[0,0]
		
		#print('TP : %d, FP : %d, FN : %d' % (tp_eval,fp_eval,fn_eval))
		
		precision_eval = tp_eval/(tp_eval+fp_eval)
		recall_eval = tp_eval/(tp_eval+fn_eval)
		f1_eval = 2 * (precision_eval*recall_eval)/(precision_eval+recall_eval)
		
		#print('Precision : %.3f, Recall : %.3f, F1 : %.3f' % (precision_eval,recall_eval,f1_eval))
		
		# Praise
		
		tp_praise = score_matrix[1,1]
		fp_praise =  score_matrix[0,1] + score_matrix[2,1] + score_matrix[3,1] + score_matrix[4,1]
		fn_praise =  (score_matrix[1,0] + score_matrix[1,1] + score_matrix[1,2] + score_matrix[1,3] + score_matrix[1,4]) - score_matrix[1,1]
		
		#print('TP : %d, FP : %d, FN : %d' % (tp_praise,fp_praise,fn_praise))
		
		precision_praise = tp_praise/(tp_praise+fp_praise)
		recall_praise = tp_praise/(tp_praise+fn_praise)
		f1_praise = 2 * (precision_praise*recall_praise)/(precision_praise+recall_praise)
		
		#print('Precision : %.3f, Recall : %.3f, F1 : %.3f' % (precision_praise,recall_praise,f1_praise))
		
		# feature request
		
		tp_request = score_matrix[2,2]
		fp_request =  score_matrix[0,2] + score_matrix[1,2] + score_matrix[3,2] + score_matrix[4,2]
		fn_request =  (score_matrix[2,0] + score_matrix[2,1] + score_matrix[2,2] + score_matrix[2,3] + score_matrix[2,4]) - score_matrix[2,2]
		
		#print('TP : %d, FP : %d, FN : %d' % (tp_request,fp_request,fn_request))
		
		precision_request = tp_request/(tp_request+fp_request)
		recall_request = tp_request/(tp_request+fn_request)
		f1_request = 2 * (precision_request*recall_request)/(precision_request+recall_request)
		
		#print('Precision : %.3f, Recall : %.3f, F1 : %.3f' % (precision_request,recall_request,f1_request))
		
		
		# bug report
		
		tp_bug = score_matrix[3,3]
		fp_bug =  score_matrix[0,3] + score_matrix[1,3] + score_matrix[2,3] + score_matrix[4,3]
		fn_bug =  (score_matrix[3,0] + score_matrix[3,1] + score_matrix[3,2] + score_matrix[3,3] + score_matrix[3,4]) - score_matrix[3,3]
		
		#print('TP : %d, FP : %d, FN : %d' % (tp_bug,fp_bug,fn_bug))
		
		precision_bug = tp_bug/(tp_bug+fp_bug)
		recall_bug = tp_bug/(tp_bug+fn_bug)
		f1_bug = 2 * (precision_bug*recall_bug)/(precision_bug+recall_bug)
		
		#print('Precision : %.3f, Recall : %.3f, F1 : %.3f' % (precision_bug,recall_bug,f1_bug))
		
		# Others
		
		tp_others = score_matrix[4,4]
		fp_others =  score_matrix[0,4] + score_matrix[1,4] + score_matrix[2,4] + score_matrix[3,4]
		fn_others =  (score_matrix[4,0] + score_matrix[4,1] + score_matrix[4,2] + score_matrix[4,3] + score_matrix[4,4]) - score_matrix[4,4]
		
		#print('TP : %d, FP : %d, FN : %d' % (tp_others,fp_others,fn_others))
		
		precision_others = tp_others/(tp_others+fp_others)
		recall_others = tp_others/(tp_others+fn_others)
		f1_others = 2 * (precision_others*recall_others)/(precision_others+recall_others)
		
		#print('Precision : %.3f, Recall : %.3f, F1 : %.3f' % (precision_others,recall_others,f1_others))
		
		model_evaluation = [(tp_eval,fp_eval,fn_eval),(tp_praise,fp_praise,fn_praise),(tp_request,fp_request,fn_request),(tp_bug,fp_bug,fn_bug),(tp_others,fp_others,fn_others)]
				
		return [precision_eval,precision_praise,precision_request,precision_bug,precision_others],[recall_eval,recall_praise,recall_request,recall_bug,recall_others],[f1_eval,f1_praise,f1_request,f1_bug,f1_others],model_evaluation

	def FitModel(self):

		average_precision_bug=[]
		average_recall_bug=[]
		average_fscore_bug=[]
		average_support_bug=[]

		average_precision_request=[]
		average_recall_request=[]
		average_fscore_request=[]
		average_support_request=[]

		average_precision_eval=[]
		average_recall_eval=[]
		average_fscore_eval=[]
		average_support_eval=[]
		
		self.vectorizer = CountVectorizer(analyzer='word',ngram_range=(1,3),max_df=.85)
		X = self.vectorizer.fit_transform(self.TRAIN_SENTENCES)
		train_data_array = X.toarray()
		
		#appDesc_features = np.array(self.train_appDesc_features)
		#appDesc_features = appDesc_features.astype(int)
	
		train_X = train_data_array #np.column_stack((train_data_array,appDesc_features))

		
		self.TRAIN_LABELS=np.array(self.TRAIN_LABELS)
		
		self.model = LogisticRegression(solver='lbfgs',multi_class='multinomial',C=.400,class_weight="balanced")
		self.model.fit(train_X,self.TRAIN_LABELS)


	def CleanSentence(self,sent):
		typos=[["im","i m","I m"],['Ill'],["cant","cnt"],["doesnt"],["dont"],["isnt"],["didnt"],["couldnt"],["Cud"],["wasnt"],["wont"],["wouldnt"],["ive"],["Ive"],["theres"]      ,["awsome", "awsum","awsm"],["Its"],["dis","diz"],["plzz","Plz ","plz","pls ","Pls","Pls "],[" U "," u "],["ur"],      ["b"],["r"],["nd ","n","&"],["bt"],["nt"],["coz","cuz"],["jus","jst"],["luv","Luv"],["gud"],["Gud"],["wel"],["gr8","Gr8","Grt","grt"],      ["Gr\\."],["pics"],["pic"],["hav"],["nic"],["nyc ","9ce"],["Nic"],["agn"],["thx","tks","thanx"],["Thx"],["thkq"],      ["Xcellent"],["vry"],["Vry"],["fav","favo"],["soo","sooo","soooo"],["ap"],["b4"],["ez"],["w8"],["msg"],["alot"],["lota"],["kinda"],["omg"],["gota"]]
		replacements=["I'm","i will","can't","doesn't","don't","isn't","didn't","couldn't","Could","wasn't","won't","wouldn't","I have","I have","there's","awesome",             "It's","this","please","you","your","be","are","and","but","not","because","just","love","good","Good","well","great","Great\\.",             "pictures","picture","have","nice","nice","Nice","again","thanks","Thanks","thank you","excellent","very","Very","favorite","so","app","before","easy","wait","message","a lot","lot of","kind of","oh, my god","going to"]

		sent_tokens = nltk.word_tokenize(sent)

		new_sent=""

		for i,token in enumerate(sent_tokens):
			found_type=False
			for index,lst in enumerate(typos):
				if token in lst:
					new_sent +=  replacements[index]
					if i<(len(sent_tokens)-1):
						new_sent += " "
						found_type=True
						break

			if found_type == False:
				new_sent += token 
				if i<(len(sent_tokens)-1):
					new_sent += " "

		return(new_sent.strip())


# In[3]:


if __name__ == '__main__':
	startTime = time.time()
	obj=SentenceClassification()
	
	maxIteratioins = 10

	average_precision_eval, average_recall_eval, average_fscore_eval= ([] for i in range(3))
	average_precision_praise, average_recall_praise, average_fscore_praise= ([] for i in range(3))
	average_precision_request,average_recall_request, average_fscore_request= ([] for i in range(3))
	average_precision_bug, average_recall_bug, average_fscore_bug = ([] for i in range(3))
	average_precision_others, average_recall_others, average_fscore_others = ([] for i in range(3))
	
	with open('BoW_Trigram_Model_Results','w') as f:
		writer = csv.writer(f,lineterminator='\n')
		writer.writerow(['Iteration','TP','FP','FN','TP','FP','FN','TP','FP','FN','TP','FP','FN','TP','FP','FN'])

		for i in range(0,maxIteratioins):
			print("iteration # %d" % (i))
			obj.SplitDataintoTrainTest()
			obj.FitModel()
			print("##########RESULTS ON A TEST SET#######################")
			precision,recall,fscore,model_evaluation = obj.EvaluateModelOnTestSet()

			class_eval = model_evaluation[0]
			class_praise = model_evaluation[1]
			class_request = model_evaluation[2]
			class_bug = model_evaluation[3]
			class_others = model_evaluation[4]

			lst = [i+1,class_eval[0],class_eval[1],class_eval[2],class_praise[0],class_praise[1],class_praise[2]]
			lst += [class_request[0],class_request[1],class_request[2],class_bug[0],class_bug[1],class_bug[2]]
			lst += [class_others[0],class_others[1],class_others[2]]

			writer.writerow(lst)

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

		print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature evaluation)" % (np.mean(average_precision_eval),np.mean(average_recall_eval),np.mean(average_fscore_eval)))
		print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (praise)" % (np.mean(average_precision_praise),np.mean(average_recall_praise),np.mean(average_fscore_praise)))
		print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature request)" % (np.mean(average_precision_request),np.mean(average_recall_request),np.mean(average_fscore_request)))
		print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (bug report)" % (np.mean(average_precision_bug),np.mean(average_recall_bug),np.mean(average_fscore_bug)))
		print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (others)" % (np.mean(average_precision_others),np.mean(average_recall_others),np.mean(average_fscore_others)))

		print('The script finished in {0} seconds'.format(time.time() - startTime))

