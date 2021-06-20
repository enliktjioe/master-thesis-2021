#!/usr/bin/python
#
# The classifiers used to filter out the informative reviews includes:
# 
# 1) EMNB: Given the labeled and unlabled dataset, use the EM-NB to build a classifier to filter out non-informative reviews
# Implementation of the EM-NB algorithm. 
# Details can be found in
# Nigam, Kamal, et al. "Text classification from labeled and unlabeled documents using EM." Machine learning 39.2 (2000): 103-134.
# Credits: Most of the code related to the algorithm is adopted from: Mathieu Blondel
# His github: https://gist.github.com/mblondel/f0789b921c98d0fe6868
#
#
# 2) SVM: classic classifier
#
# Author: Yingyezhe Jin; Date: Apr 4, 2017

# Python imports:
import numpy as np
import sys
try:
	from sklearn import svm
except:
	print("Please install the module 'sklearn' for SVM!")
	print("pip install sklearn")
	sys.exit(-1)


# AR imports:
from AR_reviewInstance import Review
from AR_util import reviews2Dict, reviews2Mat, reviews2SpMat, toCOOMatrix
"""
Notation (adopted from Mathieu Blondel):

	w: word
	d: document
	c: class

	V: vocabulary size
	X: number of documents
	M: number of classes

"""

# Matrix form documents, may result in memory error
def docs2Mat(trainSet, testSet, unlabelSet, vocabulary):
	train, trainLabel = reviews2Mat(trainSet, vocabulary)
	test, testLabel = reviews2Mat(testSet, vocabulary)
	unlabel = reviews2Mat(unlabelSet, vocabulary)[0]
	return train, trainLabel, test, testLabel, unlabel

# Dictionary form documents
def docs2Dict(trainSet, testSet, unlabelSet):
	train, trainLabel = reviews2Dict(trainSet)
	test, testLabel = reviews2Dict(testSet)
	unlabel = reviews2Dict(unlabelSet)[0]
	return train, trainLabel, test, testLabel, unlabel

# Sparse Matrix form documents
def docs2SparseMat(trainSet, testSet, unlabelSet, vocabulary):
	train, trainLabel = reviews2SpMat(trainSet, vocabulary)
	test, testLabel = reviews2SpMat(testSet, vocabulary)
	unlabel = reviews2SpMat(unlabelSet, vocabulary)[0]
	return train, trainLabel, test, testLabel, unlabel	

# Evaluate the performance:
def evaluatePerformance(prediction, truth):
	assert(len(prediction) == len(truth))

	# for precision and recall:
    # true positive
	tp = [0]*2
	# false positive
	fp = [0]*2
	# false negative
	fn = [0]*2

	for i in range(len(truth)):
		label = truth[i,:].argmax()
		predict = prediction[i]
		if(predict == label): # if correct
			tp[label] += 1
		else:
			fn[label] += 1
			fp[1-label] += 1
	precision = [0]*2
	recall = [0]*2

	f = [0]*2
	for i in range(2):
		precision[i] = tp[i]/float(tp[i] + fp[i])
		recall[i] = tp[i]/float(tp[i] + fn[i])
		f[i] = 2*precision[i]*recall[i]/(precision[i] + recall[i])
	avg = (f[0] + f[1])/2.0
	print("Average F-Score for the test data: " + str(avg))

# construct the informative review set:
def prepareResult(unlabelSet, predict, vocabulary):
	informRev = []
	assert(len(unlabelSet) == len(predict))

	for i in range(len(predict)):
		if(predict[i] == 1):
			#assert(unlabelSet[i].label == 0)
			unlabelSet[i].label = 1 # mark as informative
			informRev.append(unlabelSet[i])

	informMat = toCOOMatrix(informRev, vocabulary)

	return informRev, informMat

# assign the informative probability:
def assignProb(informRev, prob):
	predict = prob.argmax(axis=1)
	ind = 0
	for i in range(len(predict)):
		if(predict[i] == 1):
			informRev[ind].prob = prob[i][1]			
			ind += 1
	assert(ind == len(informRev))

# Use EM-Naive Bayes (Semi-supervised learning) for filtering
def AR_emnb(trainSet, testSet, unlabelSet, vocabulary, dataSetName):
	assert(bool(vocabulary))
	# 0. convert the dictionary form to the matrix form:
	#train, trainLabel, test, testLabel, unlabel = docs2Mat(trainSet, testSet, unlabelSet, vocabulary)
	train, trainLabel, test, testLabel, unlabel = docs2Dict(trainSet, testSet, unlabelSet)

	# 1. train by EM-Naive Bayes:
	emnb = SemiNB()
	p_w_c, p_c = emnb.train_semi(train, trainLabel, unlabel, vocabulary)
	# 2. test the trained model:
	predict = emnb.predict_all(test, vocabulary)
	# 3. analyze and report the performance (optional)
	evaluatePerformance(predict, testLabel)
	# 4. apply emnb to filter out the non-informative reviews 
	predict = emnb.predict_all(unlabel, vocabulary) 
	informRev, informMat= prepareResult(unlabelSet, predict, vocabulary)
	# 5. assign the prob of informative to each of the review instance:
	prob = emnb.predict_proba_all(unlabel, vocabulary)
	assignProb(informRev, prob)

	return informRev, informMat

"""
The following functions are originally adopted from Mathieu Blondel 
Modified by Yingyezhe Jin to fit our own need
"""

def softmax(loga, k=-np.inf, out=None):
	"""
	Compute the sotfmax function (normalized exponentials) without underflow.
	exp^a_i / \sum_j exp^a_j
	"""
	if out is None: out = np.empty_like(loga).astype(np.double)
	m = np.max(loga)
	logam = loga - m
	sup = logam > k
	inf = np.logical_not(sup)
	out[sup] = np.exp(logam[sup])
	out[inf] = 0.0
	out /= np.sum(out)
	return out

def logsum(loga, k=-np.inf):
	"""
	Compute a sum of logs without underflow.
		\log \sum_c e^{b_c} = log [(\sum_c e^{b_c}) e^{-B}e^B]
							= log [(\sum_c e^{b_c-B}) e^B]
							= [log(\sum_c e^{b_c-B}) + B
	where B = max_c b_c
	"""
	B = np.max(loga)
	logaB = aB = loga - B
	sup = logaB > k
	inf = np.logical_not(sup)
	aB[sup] = np.exp(logaB[sup])
	aB[inf] = 0.0
	return (np.log(np.sum(aB)) + B)

def loglikelihood(td, delta, tdu, p_w_c_log, p_c_log, vocabulary):
	Xl_ =len(td)
	Xu = len(tdu)
	Xl, M = delta.shape
	assert(Xl == Xl_)

	lik = 0.0

	## labeled
	# log P(x|c)
	p_x_c_log = np.zeros((Xl,M), np.double)
	for d in range(len(td)):
		for term in td[d]:
			w = vocabulary[term]
			p_x_c_log[d,:] += p_w_c_log[w,:] * td[d][term]

	# add log P(c) + lop P(x|c) if x has label c
	for d,c in zip(*delta.nonzero()):
		lik += p_c_log[c] + p_x_c_log[d,c]

	## unlabelled:
	# log P(x|c)
	p_x_c_log = np.zeros((Xu,M), np.double)
	for d in range(len(tdu)):
		for term in tdu[d]:
			w = vocabulary[term]
			p_x_c_log[d, :] += p_w_c_log[w,:] * tdu[d][term]


	# add log P(c)
	p_x_c_log += p_c_log[np.newaxis,:]

	for d in range(Xu):
		lik += logsum(p_x_c_log[d,:], k=-10)

	return lik

def normalize_p_c(p_c):
	M = len(p_c)
	denom = M + np.sum(p_c)
	p_c += 1.0
	p_c /= denom

def normalize_p_w_c(p_w_c):
	V, M = p_w_c.shape
	denoms = V + np.sum(p_w_c, axis=0)
	p_w_c += 1.0
	p_w_c /= denoms[np.newaxis,:]

class SemiNB(object):

	def __init__(self, model=None):
		"""
			model: a model, as returned by get_model() or train().
		"""
		self.p_w_c = None
		self.p_c = None
		if model is not None: self.set_model(model)
		self.debug = False

	def train(self, td, delta, vocabulary, normalize=True, sparse=True):
		"""
		td: document - term matrix in dict form  X x V
		delta: X x M matrix
		   where delta(d,c) = 1 if document d belongs to class c
		vocabulary: dict[term] -> position in the vocabulary
		"""

		X_, M = delta.shape
		X = len(td)
		V = len(vocabulary)
		assert(X_ == X)

		# P(c)
		self.p_c = np.sum(delta, axis=0)

		# P(w|c)
		self.p_w_c = np.zeros((V,M), dtype=np.double)

		if sparse:
			# faster when delta is sparse
			# select indices of documents that have class c
			for d,c in zip(*delta.nonzero()):
				# select indices of terms that are non-zero
				for term in td[d]:
					w = vocabulary[term]
					self.p_w_c[w,c] += td[d][term] * delta[d,c]
		else:
			# faster when delta is non-sparse
			for d in range(len(td)):
				for term in td[d]:
					w = vocabulary[term]
					self.p_w_c[w,:] += td[d][term] * delta[d,:]

		if normalize:
			normalize_p_c(self.p_c)
			normalize_p_w_c(self.p_w_c)

		return self.get_model()

	def train_semi(self, td, delta, tdu, vocabulary, maxiter=50, eps=0.01):
		"""
		td: X x V term document matrix
		delta: X x M label matrix
		tdu: Xu x V term document matrix (unlabeled)
		vocabulary: dict[term] -> position in the vocabulary        
		maxiter: maximum number of iterations
		eps: stop if no more progress than eps
		"""
		X_, M = delta.shape
		X = len(td)
		assert(X_ == X)

		# compute counts for labeled data once for all
		self.train(td, delta, vocabulary, normalize=False)
		p_c_l = np.array(self.p_c, copy=True)
		p_w_c_l = np.array(self.p_w_c, copy=True)

		# normalize to get initial classifier
		normalize_p_c(self.p_c)
		normalize_p_w_c(self.p_w_c)

		lik = loglikelihood(td, delta, tdu, np.log(self.p_w_c), np.log(self.p_c), vocabulary)

		for iteration in range(1, maxiter+1):
			# E-step: find the probabilistic labels for unlabeled data
			delta_u = self.predict_proba_all(tdu, vocabulary)

			# M-step: train classifier with the union of
			#         labeled and unlabeled data
			self.train(tdu, delta_u, vocabulary, normalize=False, sparse=False)
			self.p_c += p_c_l
			self.p_w_c += p_w_c_l
			normalize_p_c(self.p_c)
			normalize_p_w_c(self.p_w_c)

			lik_new = loglikelihood(td, delta, tdu,
									np.log(self.p_w_c), np.log(self.p_c), vocabulary)
			lik_diff = lik_new - lik
			if(lik_diff < -1e-10):
				print("Unusual difference found: " + str(lik_diff))
			assert(lik_diff >= -1e-10)
			lik = lik_new

			if lik_diff < eps:
				print "No more progress, stopping EM at iteration", iteration
				break

			if self.debug:
				print "Iteration", iteration
				print "L += %f" % lik_diff

		return self.get_model()

	def p_x_c_log_all(self, td, vocabulary):
		M = len(self.p_c)
		X = len(td)
		p_x_c_log = np.zeros((X,M), np.double)
		p_w_c_log = np.log(self.p_w_c)

		# log P(x|c)
		for d in range(X):
			for term in td[d]:
				w = vocabulary[term]
				p_x_c_log[d,:] += p_w_c_log[w,:] * td[d][term]


		return p_x_c_log

	def predict_proba(self, x, vocabulary):
		"""
		x: a V array representing a document
		Compute a M array containing P(c|x).
		"""
		return self.predict_proba_all(x, vocabulary)[0,:]

	def predict_proba_all(self, td, vocabulary):
		"""
		td: X x V term document matrix in a dictionary form
		Compute an X x M matrix of P(c|x) for all x in td.
		"""
		X = len(td)

		# log P(x|c)
		p_x_c_log = self.p_x_c_log_all(td, vocabulary)

		# add log P(c)
		p_x_c_log += np.log(self.p_c)[np.newaxis,:]

		# sotfmax(log P(x|c) + log P(c)) = P(c|x)
		for d in range(X):
			softmax(p_x_c_log[d,:], k=-10, out=p_x_c_log[d,:])

		return p_x_c_log

	def predict(self, x, vocabulary):
		"""
		x: a dictionary representing a document
		vocabulary: positional index of each term in the vocabulary
		Compute the predicted class index.
		"""
		return self.predict_all(x, vocabulary)[0]

	def predict_all(self, td, vocabulary):
		"""
		td: X x V term document matrix in a dictionary form
		vocabulary: positional index of each term in the vocabulary

		Compute a X array containing predicted class indices.
		Note: the main difference with predict_proba_all is that the
			  normalization is not necessary, as we are only interested in the most
			  likely class.
		"""

		# log P(x|c)
		p_x_c_log = self.p_x_c_log_all(td, vocabulary)

		# add log P(c)
		p_x_c_log += np.log(self.p_c)[np.newaxis,:]

		return p_x_c_log.argmax(axis=1)

	def get_model(self):
		return (self.p_w_c, self.p_c)

	def set_model(self, model):
		self.p_w_c, self.p_c = model



# Use the SVM as a classifier to filter 
def AR_svm(trainSet, testSet, unlabelSet, vocabulary, datasetName):
	assert(bool(vocabulary))
	# 0. convert the dictionary form to the matrix form:
	# Version1: normal numpy matrix
	#train, trainLabel, test, testLabel, unlabel = docs2Mat(trainSet, testSet, unlabelSet, vocabulary)
	# Version2: sparse matrix
	train, trainLabel, test, testLabel, unlabel = docs2SparseMat(trainSet, testSet, unlabelSet, vocabulary)

	# 1. train by SVM:
	X = train
	y = trainLabel.argmax(axis=1)
	clf = svm.LinearSVC()
	clf.fit(X, y)
	# 2. test the trained model:
	predict = clf.predict(test)

	# 3. analyze and report the performance (optional)
	evaluatePerformance(predict, testLabel)
	# 4. apply svm to filter out the non-informative reviews
	predict = clf.predict(unlabel)
	informRev, informMat= prepareResult(unlabelSet, predict, vocabulary)
	# 5. assign the informative prob, for svm, the prob is always 1
	for r in informRev:
		r.prob = 1.0

	return informRev, informMat