#!/usr/bin/python
#
# LDA
# Latent Dirichlet Allocation 
# Using the python package lda to do that
# Author: Xiao Huang, Yingyezhe Jin

# python imports
import numpy as np
import operator, sys
try:
	import lda
except:
	print("Please install the module 'lda' for LDA!")
	print("pip install lda")
	sys.exit(-1)


# Given the review instances in both list and sparse matrix form
# Note here that the vocabulary is in a dictionary form
# return the doc_topic matrix and the vocabulary as a list
def AR_lda(informMat, vocabulary, n_topics):
	# apply the LDA
	model = lda.LDA(n_topics, n_iter=1000, random_state=1, refresh=500)
	model.fit(informMat)

	sorted_vocab = sorted(vocabulary.items(), key=operator.itemgetter(1))
	#print(sorted_vocab)
	vocab_list = []
	for i in range(len(sorted_vocab)):
		vocab_list.append(sorted_vocab[i][0])
	#print(vocab_list)

	topic_word = model.topic_word_
	top_words_list = []
	n_top_words = 8
	# print for illustration
	for i, topic_dist in enumerate(topic_word):
		topic_words = np.array(vocab_list)[np.argsort(topic_dist)][:-n_top_words:-1]
		top_words_list.append(topic_words)
		print('Topic {}: {}'.format(i, ' '.join(topic_words)))

	doc_topic = model.doc_topic_
	return doc_topic, vocab_list, top_words_list


