#!/usr/bin/env python
# coding: utf-8

from utils import *

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')


# # NLP based Preprocessing

get_ipython().run_line_magic('run', './AR_Miner/AR_util.py')
get_ipython().run_line_magic('run', './AR_Miner/AR_reviewInstance.py')

# Inputs:
datasetName = "swiftkey" # four apps: facebook, templerun2, swiftkey, tapfish:
# datasetName = "templerun2" # four apps: facebook, templerun2, swiftkey, tapfish
rmStopWords = True # Removing stop words lead to information loss and bad f-score
rmRareWords = True # Remove the word with low frequency
skParse = False # set skParse True to directly read of the data that has been filtered out

# Outputs:
if(skParse == False):
    trainSet, testSet, unlabelSet, vocabulary = AR_parse(datasetName, rmStopWords, rmRareWords)
trainSet[1].printSelf()


# # Naive Bayes based Filtering

get_ipython().run_line_magic('run', './AR_Miner/AR_classifier.py')
import time
start_time = time.clock()

useSVM = True # SVM is way better than EMNB in the testing
if(skParse == False):
    if(useSVM == False):
#         informRev, informMat = AR_emnb(trainSet, testSet, unlabelSet, vocabulary, datasetName)
        informRev, uninformRev, informMat = AR_emnb(trainSet, testSet, unlabelSet, vocabulary, datasetName)
    else:
#         informRev, informMat = AR_svm(trainSet, testSet, unlabelSet, vocabulary, datasetName)
        informRev, uninformRev, informMat = AR_svm(trainSet, testSet, unlabelSet, vocabulary, datasetName)
    print(time.clock() - start_time, "seconds")
    # write the result back to the file (optional)
    # AR_writeReviews(informRev, datasetName)
    
else:
    # directly read from the file
    informRev, informMat, vocabulary = AR_loadReviews(datasetName)

print("Number of informative reviews: " + str(len(informRev)))
print("Number of uninformative reviews: " + str(len(uninformRev)))
print('\n')
informRev[1].printSelf()
print('\n')
uninformRev[239].printSelf()


# # LDA topic clustering

get_ipython().run_line_magic('run', './AR_Miner/AR_lda.py')

n_topics = 20 # the number of topics
doc_topic, vocab, top_words_list = AR_lda(informMat, vocabulary, n_topics)


# # Ranking Algorithms for Importance

get_ipython().run_line_magic('run', './AR_Miner/AR_ranker.py')

wg = [0.85, 0.15]
group_scores, sorted_group_indices = group_rank(doc_topic, wg, informRev)
print('Group scores:\n' + str(group_scores) + '\n')
print('Group in order of importance:\n' + str(sorted_group_indices))


get_ipython().run_line_magic('run', './AR_Miner/AR_textrank.py')

AR_tfIdf(informRev)
rankrevText = AR_textrank(doc_topic, informRev)


# print the top two reviews of the first five groups:
for i in range(5): # number of groups to print
    print("Instance review for topic group: " + str(i))
    for j in range(2): # number of top reviews to print
        r_ind = rankrevText[i][j][0]
        score = rankrevText[i][j][1]
        print(str(j+1) + "th review " + "Text: " +  informRev[r_ind].text + " Score: " + str(score))
    print ("\n")    


get_ipython().run_line_magic('run', './AR_Miner/AR_reviewRanking.py')

AR_tfIdf(informRev)
weight = [0.25, 0.25, 0.25, 0.25]
rankrevTopic = instance_ranking(doc_topic, weight, informRev)


# # Visualization

get_ipython().run_line_magic('run', './AR_Miner/AR_visualization.py')

group_count = 10
plot_group_ranking(group_scores, sorted_group_indices, top_words_list, group_count)
print("Ranking all the reviews in the first group via text rank")
plot_instance_ranking(sorted_group_indices[0], informRev, rankrevText, 10)
print("Ranking all the reviews in the first group via topic modeling")
plot_instance_ranking(sorted_group_indices[0], informRev, rankrevTopic, 10)




