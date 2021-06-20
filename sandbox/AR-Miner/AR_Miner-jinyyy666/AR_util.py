#!/usr/bin/python
#
# The utility function for the AR Miner includes:
#
# 1)parser: Read the dataset, stem each review instances and 
# 		   return test, train, and unlabeled data
# 2)read/write reviews: read the reviews in Json form from disk.
#					    write the reviews back to disk in Json form
# Author: Yingyezhe Jin; Date: Mar. 19, 2017

# python imports
import os, glob, sys, re, json, math
import numpy as np
try:
	from sklearn.feature_extraction import DictVectorizer, FeatureHasher
except:
	print("Please install the module 'sklearn' for converting dicts to sparse matrix!")
	print("pip install sklearn")
	sys.exit(-1)
try:
	from scipy.sparse import coo_matrix
except:
	print("Please install the module 'scipy' for sparse matrix!")
	print("pip install scipy")
	sys.exit(-1)


# stemming and removing stop words
try:
	from nltk.stem.porter import PorterStemmer
except:
	print("Please install the module 'nltk' for stemming and removing stop words!")
	print("pip install nltk")
	sys.exit(-1)
try:
	from nltk.corpus import stopwords
except:
	print("Please install the nltk.corpus...")
	print("Please do the following in python:")
	print(">>> import nltk")
	print(">>> nltk.download('all')")
	sys.exit(-1)

# AR imports
from AR_reviewInstance import Review

# convert the rating to actual number
rating2int = {"zero" : 0, "one" : 1, "two" : 2, "three" : 3, "four" : 4, "five" : 5}

# the caching idea for speeding up the parser:
cache={}
st = PorterStemmer()

def stem_cached(token):
	if token not in cache:
		cache[token] = st.stem(token)
	return cache[token]

# stop words
#operators = set(('and', 'or', 'not', 'is', 'are'))
stopWords = set(stopwords.words("english"))# - operators

# determine if a string is a integer
def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

# read the dataset
# @param: the name of the dataset
# @return: train, test and unlabeled data after stemming and case-folding
def AR_parse(datasetName, rmStopWords, rmRareWords):

	fileTrain = os.path.join( "./datasets", datasetName, "trainL")
	fileUnlabel = os.path.join("./datasets", datasetName, "trainU")
	fileTest = os.path.join("./datasets", datasetName, "test")

	cnt = 0

	# returns:
	train = []
	test = []
	unlabel = []

	vocabulary = {}
	wcounter = {}
	# 1. Read the dataset and form a vocabulary
	# for training set:
	info = os.path.join(fileTrain, "info.txt")
	cnt = readFile(info, train, 1, vocabulary, wcounter, cnt, rmStopWords)

	non_info = os.path.join(fileTrain, "non-info.txt")
	cnt = readFile(non_info, train, -1, vocabulary, wcounter, cnt, rmStopWords)

	# for testing set:

	info = os.path.join(fileTest, "info.txt")
	cnt = readFile(info, test, 1, vocabulary, wcounter, cnt, rmStopWords)

	non_info = os.path.join(fileTest, "non-info.txt")
	cnt = readFile(non_info, test, -1, vocabulary, wcounter, cnt, rmStopWords)


	# for unlabeled set:
	info = os.path.join(fileUnlabel, "unlabeled.txt")
	cnt = readFile(info, unlabel, 0, vocabulary, wcounter, cnt, rmStopWords)

	# 2. Remove the rare words (occur only once) and integer 
	if(rmRareWords == True):
		newVoc = {}
		for term, index in vocabulary.items():
			if(wcounter[term] > 1 and not representsInt(term) ):
				newVoc[term] = len(newVoc)

	else:
		newVoc = vocabulary

	assert(bool(newVoc))
	print("Vocabulary size for "+ datasetName + " : "+ str(len(newVoc)))

	if(rmRareWords == True):
		for review in train:
			review.removeRareTerm(newVoc)
			#review.printSelf()
		for review in test:
			review.removeRareTerm(newVoc)
			#review.printSelf()
		for review in unlabel:
			review.removeRareTerm(newVoc)
			#review.printSelf()

	print("Training set Size: " + str(len(train)))
	print("Testing set Size: " + str(len(test)))
	print("Unlabeling set Size: " + str(len(unlabel)))

	return train, test, unlabel, newVoc

# directly read the filtered dataset from the file to save time
def AR_loadReviews(datasetName):
	filename = os.path.join( "./datasets", datasetName, "filtered.json")
	informRev = []
	vocabulary = {}
	if not os.path.isfile(filename):
		print('Given filtered data not found: {}'.format(filename))
		sys.exit(-1)


	with open(filename, 'r') as f:
		for line in f:
			jsonDict = json.loads(line)
			review = Review()
			review.fromJson(jsonDict)
			for term in review.content:
				if(not vocabulary.has_key(term)):
					vocabulary[term] = len(vocabulary)

			informRev.append(review)

	X = len(informRev)
	V = len(vocabulary)
	
	try:
		informMat = np.zeros((X,V), dtype = float)
	except:
		print("The informative review matrix size of: " + str(X) + " by " + str(V) + " cannot be created!")
		print(" So I only return the reviews in a list")
		return informRev, np.zeros(1, dtype = float), vocabulary

	for i in range(len(informRev)):
		informMat[i,:] = informRev[i].formNpVector(vocabulary)

	return informRev, informMat, vocabulary

# write the reviews into the json object
def AR_writeReviews(informRev, datasetName):
	pathname = os.path.join("./datasets", datasetName)
	if not os.path.isdir(pathname):
		print('Given path not found: {}'.format(pathname))
		sys.exit(-1)

	filename = os.path.join( "./datasets", datasetName, "filtered.json")
	with open(filename, 'w') as f:
		for review in informRev:
			jsonDict = review.toJsonDict()
			json.dump(jsonDict, f, separators=(',',':'))
			f.write("\n")

# read the data file given the filename and return the dataset
# @dataset: train/test/unlabel, as dict, @cnt: for labeling;
# @label: 1 -> informative, -1 -> noninformative 0 -> unlabeled
# @voc: vocabulary a dict {term, positional index}
# @word counter: count the word freq over the entire dataset
def readFile(filename, dataset, label, voc, wcounter, cnt, rmStopWords):
	if not os.path.isfile(filename):
		print('Given dataset not found: {}'.format(filename))
		return


	with open(filename, 'r') as f:
		# read each review instance line by line:
		for instance in f:
			# break each line into three parts, ignore the first segment:
			parts = instance.split(' ')		
			r = parts[1] # like: ratingone
			rating = rating2int[r[6:]]
			
			text = " ".join(parts[2:]) # like: blabla blabla...
			
			# case-folding

			text = text.lower()
			# remove the non-alpha-number words
			tokens = re.findall(r'\w+', text)
			raw_text = " ".join(tokens)

			content = []
			# stem the content and remove stop words:
			for t in tokens:
				if(rmStopWords == True and t in stopWords):
					continue

				t = stem_cached(t)
				content.append(t)
				# build the vocabulary
				if(not voc.has_key(t)):
					voc[t] = len(voc)
				if(not wcounter.has_key(t)):
					wcounter[t] = 0
				wcounter[t] += 1

			ntokens = len(content)

			review = Review()
			review.fromText(cnt, content, ntokens, rating, label, raw_text)
			# For debugging:
			#review.printSelf()
			dataset.append(review)
			cnt += 1

	return cnt


# Transform the review instances into document term matrix:
# Input: @reviews: a list of review instances
# Return: @mat : X x V document matrix
#	      @label : X x 2 label matrix
def reviews2Mat(reviews, vocabulary):
	V = len(vocabulary) # vocabulary size
	X = len(reviews) # Documents size
	try: 
		mat = np.zeros((X, V), dtype = np.double) 
	except:
		print("Try to convert the matrix with V :" + str(V) + " X: " + str(X))
		print("Failed due to too large size. Return...")
		return np.zeros((1, 1)), np.zeros((1, 1))

	label = np.zeros((X, 2), dtype = np.double)
	i = 0
	for review in reviews:
		mat[i,:] = review.formNpVector(vocabulary)
		l = review.label
		if(l == 1):
			label[i, 1] = 1
		elif(l == -1):
			label[i, 0] = 1

		i += 1
	return mat, label


# Transform the review instance into the dictionary (sparse matrix):
# Input: @reviews: a list of review instances
# Return: @dataList : list of review , each review is in a dictionary form
#	      @label : X x 2 label matrix
def reviews2Dict(reviews):
	X = len(reviews)
	dataList = []
	label = np.zeros((X, 2), dtype = np.double)
	i = 0
	for review in reviews:
		vdict = review.formDictVector()
		dataList.append(vdict)

		l = review.label
		if(l == 1):
			label[i, 1] = 1
		elif(l == -1):
			label[i, 0] = 1

		i += 1
	return dataList, label

# Transform the list of review instances into sparse matrix
def reviews2SpMat(reviews, vocabulary):
	X = len(reviews)
	dataList = []
	label = np.zeros((X, 2), dtype = np.double)
	i = 0
	for review in reviews:
		vdict = review.formFullDictVector(vocabulary)
		dataList.append(vdict)
		l = review.label
		if(l == 1):
			label[i, 1] = 1
		elif(l == -1):
			label[i, 0] = 1

		i += 1
	#h = FeatureHasher(n_features = len(vocabulary))
	#sparseMat = h.transform(dataList)
	#v = DictVectorizer(sparse = True)
	#sparseMat = v.fit_transform(dataList)
	
	sparseMat = toCOOMatrix(reviews, vocabulary)
	return sparseMat, label

# Transform the reviews to the COO matrix (sparse)
def toCOOMatrix(reviews, vocabulary):
	X = len(reviews)
	V = len(vocabulary)

	data = []
	row = []
	col = []
	for i in range(X):
		v_dict = reviews[i].formFullDictVector(vocabulary)
		for term in v_dict:
			data.append(v_dict[term])
			row.append(i)
			col.append(vocabulary[term])
	dataArr = np.asarray(data)
	rowArr = np.asarray(row)
	colArr = np.asarray(col)
	return coo_matrix((dataArr,(rowArr, colArr)), shape=(X, V))


# Compute the tf-idf for each review to measure the similarity
# Input:
# 		reviews    : a list of informative reviews
#		vocabulary : the vocabulary of the collection in the dictionary form
# Output:
#	    None
def AR_tfIdf(reviews):
	tf = {} # term frequency
	idf = {} # inverse doc frequency
	total_docs = len(reviews)
	# 1. Compute the tf and idf
	for i in range(total_docs):
		tf[i] ={}
		r = reviews[i]
		s = set()
		for term in r.content:

			# record the # of doc that contain the word first for idf
			if(not idf.has_key(term)):
				idf[term] = 0
			if(term not in s):
				idf[term] += 1
				s.add(term)

			# record the the term frequency for each doc
			if(not tf[i].has_key(term)):
				tf[i][term] = 0
			tf[i][term] += 1

	# 2. Calculate the tf-idf
	for rid, terms in tf.iteritems():
		summation = 0.0
		for word, freq in terms.iteritems():
			tf[rid][word] = (1 + np.log10(freq))*(np.log10(total_docs/float(idf[word])))                
			summation += tf[rid][word]*tf[rid][word]

		# normalize the tf-idf here:
		for word, freq in terms.iteritems():
			tf[rid][word] = tf[rid][word]/math.sqrt(summation)

		reviews[rid].tf_idf = tf[rid] # directly modify the review here



# Compute the cosine similarity between the two reviews
# Input:
#		ri, rj     : the two reviews
#		thresh	   : the threshold for determining similarity
# Output:
#		True/False : if similar or not
def sim(ri, rj, thresh = 0.3):
	if(ri.tf_idf == None or rj.tf_idf == None):
		print("In function::sim of AR_util.py: ")
		print("Need to run AR_tfIdf to compute the tf-idf first!")
		sys.exit(-1)

	vi = ri.tf_idf
	vj = rj.tf_idf
	score = 0.0
	for term, value in vi.iteritems():
		if(vj.has_key(term)):
			score += vj[term]*value

	if(score > thresh):
		return True
	else:
		return False
