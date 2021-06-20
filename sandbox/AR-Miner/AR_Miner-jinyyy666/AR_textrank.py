#!/usr/bin/python
#
# The use the text rank to take care of the review instance level ranking
#
#
# Author: Yingyezhe Jin; Date: Apr. 21, 2017

# python imports:
import numpy as np
try:
	from scipy.sparse import coo_matrix
	from scipy.sparse import csc_matrix
except:
	print("Please install the module 'scipy' for sparse matrix!")
	print("pip install scipy")
	sys.exit(-1)
# AR Miner imports:
from AR_util import sim


# Input: 
#      doc_topic       : lda topic model matrix n*k, n : number of reviews, k: # of topics
#	   informRev       : all informative reviews
# Output:
#	   rankedInstance  : a dict = {topic, list of sorted reviews}
#	   ##rankedGroup	   : a list of ranked group indexs##
def AR_textrank(doc_topic, informRev):
	# 1. Simple topic grouping and group ranking (by the volume only):
	#    For each group topic, collect the reviews that have the highest prob :
	n, k = doc_topic.shape
	assert( n == len(informRev) )

	reviewG = {}
	reviewGInd = {}
	for i in range(n):
		topic = doc_topic[i].argmax()
		if(not reviewG.has_key(topic)):
			reviewG[topic] = []
			reviewGInd[topic] = []

		reviewG[topic].append(informRev[i])
		reviewGInd[topic].append(i)

	assert(len(reviewG) == k)
	rankedInstance = {}
	# 2. Text rank within each group:
	for j in range(k):
		rankedInstance[j] = []
		textRankGroup(j, rankedInstance, reviewG[j], reviewGInd[j])

	return rankedInstance

# Rank the reviews in the same group by text rank
# Input: 
#	   topic           : the topic index
#	   rankedInstance  : a dict = {topic, list of sorted reviews}, this is also the return
#      reviews         : the corresponding review instances
#	   reviewInds      : the corresponding review indices w.r.t all the informative reviews
# Output: 
#	   rankedInstance  : modify it directly for the return
def textRankGroup(topic,rankedInstance, reviews, reviewInds):
	# 1. Construct the connectivity graph:
	G = constructGraph(reviews)

	# 2. Run the page rank on this graph and output the rankings:
	score = pageRank(G)

	# 3. prepare the indices for return
	inds = zip(reviewInds, score)
	inds.sort(key = lambda x : x[1], reverse = True)

	for i in range(len(inds)):
		rankedInstance[topic].append(inds[i])


# Construct the graph of the reviews where the edges present the similarity:
# Input: 
#		reviews        : the review instances in a list
# Output:
# 		G              : coo sparse matrix for connectivity graph
def constructGraph(reviews):
	# number of the reviews
	n = len(reviews) 

	data = []
	row = []
	col = []
	cnt = 0
	for i in range(n):
		for j in range(n):
			if(i >= j):
				continue
			# construct an edge if similar
			if(sim(reviews[i], reviews[j])):
				cnt += 2
				row.append(i)
				col.append(j)
				data.append(1)

				row.append(j)
				col.append(i)
				data.append(1)

	dataArr = np.asarray(data)
	rowArr = np.asarray(row)
	colArr = np.asarray(col)
	print("In construct the graph of reviews ---- Nodes: " + str(len(reviews)) + " Edges: " + str(cnt))
	return coo_matrix((dataArr,(rowArr, colArr)), shape=(n, n))

# Compute the page rank score of the given graph
# Adopt the code from: https://gist.github.com/diogojc/1338222/84d767a68da711a154778fb1d00e772d65322187
# Credit: diogojc
# Input:
#		G      : the coo_matrix (sparse matrix)
#		s      : the probability of link following
#		maxerr : the convergence critiror
# Output:
#		score  : the page rank scores
def pageRank(G, s = .85, maxerr = .0001):
	n = G.shape[0]

	# transform G into markov matrix A
	A = csc_matrix(G,dtype=np.float)
	rsums = np.array(A.sum(1))[:,0]
	ri, ci = A.nonzero()
	A.data /= rsums[ri]

	# bool array of sink states
	sink = rsums==0

	# Compute pagerank r until we converge
	ro, r = np.zeros(n), np.ones(n)
	while np.sum(np.abs(r-ro)) > maxerr:
		ro = r.copy()
		# calculate each pagerank at a time
		for i in xrange(0,n):
			# inlinks of state i
			Ai = np.array(A[:,i].todense())[:,0]
			# account for sink states
			Di = sink / float(n)
			# account for teleportation to state i
			Ei = np.ones(n) / float(n)

			r[i] = ro.dot( Ai*s + Di*s + Ei*(1-s) )

	# return normalized pagerank
	return r/float(sum(r))