#!/usr/bin/python
#
# Define the review instances
# 
import json
import numpy as np

# Class that contains the information for each review:
class Review:
	# Constructor:
	def __init__(self):
		# the review id
		self.id = -1
		# the review content, as a list
		self.content = []
		# the review raw text, as a string
		self.text = None
		# rating of this review (1-5):
		self.rating = -1
		# number of tokens in the review:
		self.ntokens = -1
		# the time stamp:
		self.ts = ""
		# each group belong to 
		self.group = ""
		# the probability
		self.prob = 0
		# the label for this review: 1-> informative; 0 -> unlabeled; -1 ->non-informative
		self.label = 0
		# doc vector (numpy vector):
		self.vnp = None
		# doc vector (dict vector):
		self.vdict = None
		# tf-idf vector:
		self.tf_idf = None

	# initialize from reading each review instance from the dataset
	def fromText(self, id, content, ntokens, rating, label, raw_text):
		self.id = id
		self.content = content
		self.text = raw_text
		self.ntokens = ntokens
		self.rating = rating
		self.label = label
	# initialize from the json dict
	def fromJson(self, jsonDict):
		self.id = jsonDict['id']
		self.content = jsonDict['content']
		self.text = jsonDict['text']
		self.ntokens = jsonDict['ntokens']
		self.rating = jsonDict['rating']
		self.label = jsonDict['label']
		self.ts = jsonDict['ts']
		self.group = jsonDict['group']
		self.prob = jsonDict['prob']

	# change the review instance to a dictionary instance
	def toDist(self):
		reviewDict = {}
		reviewDict['id'] = self.id
		reviewDict['content'] = self.content
		reviewDict['text'] = self.text
		reviewDict['rating'] = self.rating
		reviewDict['ntokens'] = self.ntokens
		reviewDict['ts'] = self.ts
		reviewDict['group'] = self.group
		reviewDict['prob'] = self.prob
		reviewDict['label'] = self.label
		reviewDict['vnp'] = self.vnp
		reviewDict['vdict'] = self.vdict
		reviewDict['tf_idf'] = self.tf_idf
		return reviewDict
	# convert the review to the json text
	def toJsonDict(self):
		jsonDict = {}
		jsonDict['id'] = self.id
		jsonDict['content'] = self.content
		jsonDict['text'] = self.text
		jsonDict['rating'] = self.rating
		jsonDict['ntokens'] = self.ntokens
		jsonDict['ts'] = self.ts
		jsonDict['group'] = self.group
		jsonDict['prob'] = self.prob
		jsonDict['label'] = self.label

		return jsonDict

	# Remove the terms (rare ones) of the content that are not in the dictionary
	def removeRareTerm(self, vocabulary):
		newcontent = []
		for term in self.content:
			if(vocabulary.has_key(term)):
				newcontent.append(term)

		self.content = newcontent
		self.ntokens = len(newcontent)

	# given an vocabulary, form as a doc vector (numpy vector)
	def formNpVector(self, vocabulary):
		v = np.zeros(len(vocabulary), dtype = 'float')

		for term in self.content:
			v[vocabulary[term]] += 1
		self.vnp = v
		return v
	# form as a dict vector(more sparse)
	def formDictVector(self):
		v_dict = {}
		for term in self.content:
			if(not v_dict.has_key(term)):
				v_dict[term] = 0
			v_dict[term] += 1
		self.vdict = v_dict
		return v_dict

	# form a full dict vector given the vocabulary, ignore the words not in the vocabulary
	def formFullDictVector(self, vocabulary):
		v_dict = {}
		for term in self.content:
			if(not vocabulary.has_key(term)):
				continue
			if(not v_dict.has_key(term)):
				v_dict[term] = 0
			v_dict[term] += 1

		return v_dict

	def printSelf(self):
		tmp = " ".join(self.content)
		print("Review id: " + str(self.id) + " Rating: "+ str(self.rating) + " Content: " + tmp + " Ntokens: " + str(self.ntokens) + " TS: " + self.ts + " Group: " + self.group + " Prob: " + str(self.prob) + " label: " + str(self.label) )
		print("Raw text: " + str(self.text))
		#print(self.vnp)
		#print(self.vdict)
		#print(self.tf_idf)