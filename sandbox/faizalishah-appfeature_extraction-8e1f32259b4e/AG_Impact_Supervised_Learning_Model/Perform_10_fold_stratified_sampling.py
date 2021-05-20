
# coding: utf-8

# In[7]:

from os import listdir
from os.path import isfile, join
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
import random
import math
import numpy as np
import sys
import os 


class StratifiedSampling:
	def __init__(self,train_proc):
		self.train_proc = train_proc
		self.setDataset()
		#self.SetTrainTestApps()
	 
	def setDataset(self):
		dataset_path = "cross-validation"
		
		self.df_dataset= pd.DataFrame(columns=('app-category','record'))
		
		app_categories = set([f.split('.')[0] for f in listdir(dataset_path) if isfile(join(dataset_path, f))])
		app_category_tsv_records=[]
		app_category_con_records=[]
		category_label=[]
		
		print(app_categories)
		for app_category in app_categories:
			print(app_category)
			if(app_category!="SEMEVAL"):
				#if app_category=='PRODUCTIVITY':
				app_category_tsv_file = dataset_path + "/" + app_category + ".tsv"
				app_category_con_file = dataset_path + "/" + app_category + ".con"
				#print(app_category_tsv_file)
				records_tsv = self.ReadFileLines(app_category_tsv_file)
				records_con = self.ReadFileLines(app_category_con_file)
				app_category_tsv_records.append(records_tsv)
				app_category_con_records.append(records_con)
				category_label.append(app_category)
		
		# sem eval datatset
		ds_sem_eval_tsv=[]
		ds_sem_eval_con=[]
		
		ds_sem_eval_tsv_path= dataset_path+ "/SEMEVAL.tsv"
		ds_sem_eval_con_path= dataset_path  + "/SEMEVAL.con"

		if self.train_proc=="SCV_EXT":
			ds_sem_eval_tsv = self.ReadFileLines(ds_sem_eval_tsv_path)
			ds_sem_eval_con = self.ReadFileLines(ds_sem_eval_con_path)

			print("Size (tsv)=",len(ds_sem_eval_tsv))
			print("Size (con)=",len(ds_sem_eval_con))

		dirName = 'cv-data/'

		if not os.path.exists(dirName):
			os.mkdir(dirName)
	
		for fold in range(0,10):
			print('Fold # %d' % (fold))
			train_set_tsv,train_set_con,test_set_tsv,test_set_con = self.GetStratifiedSample(app_category_tsv_records,app_category_con_records)
			print('Size of Test-Set (tsv) is %d' % len(test_set_tsv))
			print('Size of Train-set (tsv) is %d' % len(train_set_tsv))
			print('Size of Test-Set (con) is %d' % len(test_set_con))
			print('Size of Train-set (con) is %d' % len(train_set_con))

			if self.train_proc=="SCV_EXT":
				self.SaveFoldData_Ext(train_set_tsv,ds_sem_eval_tsv, "train" + str(fold) + ".tsv")
				self.SaveFoldData_Ext(train_set_con,ds_sem_eval_con, "train" + str(fold) + ".con")
			else:
				self.SaveFoldData(train_set_tsv, "train" + str(fold) + ".tsv")
				self.SaveFoldData(train_set_con, "train" + str(fold) + ".con")
				
			self.SaveFoldData(test_set_tsv, "test" + str(fold) + ".tsv")
			self.SaveFoldData(test_set_con, "test" + str(fold) + ".con")
			#print(fold)
			print("##################################")
			#print("TRAIN:", train_index, "TEST:", test_index)
			#X_train, X_test = X[train_index], X[test_index]
			#y_train, y_test = y[train_index], y[test_index]
	
	
	def SaveFoldData_Ext(self,data,semeval_data,file_name):
		tsv_file = open("cv-data/" + file_name, "w")
		for record in data:
			for line in record:
				tsv_file.write(line)
			tsv_file.write('\n')
		
		#Extend SemEval data
		for record in semeval_data:
			for line in record:
				tsv_file.write(line)
			tsv_file.write('\n')
		#text_file.write("Purchase Amount: %s" % TotalAmount)
		tsv_file.close()
	
	def SaveFoldData(self,data,file_name):
		tsv_file = open("cv-data/" + file_name, "w")
		for record in data:
			for line in record:
				tsv_file.write(line)
			tsv_file.write('\n')
		#text_file.write("Purchase Amount: %s" % TotalAmount)
		tsv_file.close()
			
	def GetStratifiedSample(self,app_categories_records_tsv,app_categories_records_con):    
		train_set_tsv=[]
		train_set_con=[]
		test_set_tsv=[]
		test_set_con=[]
		total_records=0
		for i in range(0,len(app_categories_records_tsv)):
			app_category_records_tsv= np.array(app_categories_records_tsv[i])
			app_category_records_con= np.array(app_categories_records_con[i])
			total_records = total_records + len(app_category_records_tsv)
			records_range = list(range(0,len(app_category_records_tsv)))
			X_train_tsv, X_test_tsv, Y_train_tsv,Y_test_tsv = train_test_split(app_category_records_tsv, records_range , test_size=0.10, random_state=None)
			train_set_tsv.extend(app_category_records_tsv[Y_train_tsv])
			test_set_tsv.extend(app_category_records_tsv[Y_test_tsv])
			
			train_set_con.extend(app_category_records_con[Y_train_tsv])
			test_set_con.extend(app_category_records_con[Y_test_tsv])
			
		
		return (train_set_tsv,train_set_con,test_set_tsv,test_set_con)
	
	def ReadFileLines(self,file_path):
		All_Record=[]
		with open(file_path) as f:
			content = f.readlines()
		# you may also want to remove whitespace characters like `\n` at the end of each line
		step=0
		record=[]
		for l in content:
			#print(l)
			step = step + 1
			if len(l.strip())!=0:
				record.append(l)
			elif len(l.strip())==0:
				All_Record.append(record)
				record=[]
			#if step == 30:
				#break
		return (All_Record)
	

if __name__ == '__main__':
	train_proc = sys.argv[1]
	obj=StratifiedSampling(train_proc)




