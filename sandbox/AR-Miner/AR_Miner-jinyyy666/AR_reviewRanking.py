# Author : Shanshan Li

# python imports
from collections import defaultdict
import operator

# AR Miner imports
from AR_util import sim

prop_threshold = 0.2 # can be changed to larger value to save time , used to be 0.01
sim_threshold = 0.6

cache_sim = defaultdict(dict)

def group_revs(doc_topic):
	topic_revs = defaultdict(list)

	for i in range(len(doc_topic)):
		for j in range(len(doc_topic[i])):
			if doc_topic[i][j] >= prop_threshold:
				topic_revs[j].append(i)

	return topic_revs

def rev_prop(doc_topic):
	topic_revs_prop = defaultdict(dict)
	topic_revs = group_revs(doc_topic)

	for topic in topic_revs:
		for rev_idx in topic_revs[topic]:
			topic_revs_prop[topic][rev_idx] = doc_topic[rev_idx][topic]
	return topic_revs_prop

def rev_rating(doc_topic, informRev):
	topic_revs_rating = defaultdict(dict) 
	topic_revs = group_revs(doc_topic)
	
	for topic in topic_revs:
		for rev_idx in topic_revs[topic]:
			topic_revs_rating[topic][rev_idx] = 1/float(informRev[rev_idx].rating)
	return topic_revs_rating

def rev_probab(doc_topic, informRev):
	"""
	calculating review instance posterior probability through EMNB
	"""
	topic_revs_probab = defaultdict(dict)
	topic_revs = group_revs(doc_topic)
	
	for topic in topic_revs:
		for rev_idx in topic_revs[topic]:
			topic_revs_probab[topic][rev_idx] = informRev[rev_idx].prob
	return topic_revs_probab

# cached similarity measure for td-idf
def cachedSim(r1, r2):
	x_id = r1.id
	y_id = r2.id
	ret = -1
	if(cache_sim.has_key(x_id)):
		if(cache_sim[x_id].has_key(y_id)):
			ret =  cache_sim[x_id][y_id]
	else:
		cache_sim[x_id][y_id] = sim(r1, r2)
		ret = cache_sim[x_id][y_id]
	return ret

# cached jaccard, seems to be very  slow
def JaccardSimilarity(x, y, x_id, y_id):   
	if(cache_sim.has_key(x_id)):
		if(cache_sim[x_id].has_key(y_id)):
			return cache_sim[x_id][y_id]
	intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
	
	union_cardinality = len(set.union(*[set(x), set(y)]))
	if union_cardinality==0:
		return 0.0
	else:
		jaccard=intersection_cardinality/union_cardinality
		cache_sim[x_id][y_id] = jaccard
		return jaccard
	
def rev_duplic(doc_topic, informRev): 
	topic_revs_duplic = defaultdict(dict)
	updated_topic_revs_prop = defaultdict(dict)
	updated_topic_revs_rating = defaultdict(dict)
	updated_topic_revs_probab = defaultdict(dict)
	topic_revs = group_revs(doc_topic)
	topic_revs_prop = rev_prop(doc_topic)
	topic_revs_rating = rev_rating(doc_topic, informRev)
	topic_revs_probab = rev_probab(doc_topic, informRev)
	
	for topic in topic_revs:  
		rev_simRevs = defaultdict(list)
		print(str(topic) + "th topic has reviews: " + str(len(topic_revs[topic])))
		for i in range(len(topic_revs[topic])):
			#print("For " + str(i) + "th review: ")
			rev_idx1 = topic_revs[topic][i]
			if rev_simRevs:
				for key in rev_simRevs.keys():
					if rev_idx1 in rev_simRevs[key]:
						continue      
			VS1 = informRev[rev_idx1].content
			VS1_id = informRev[rev_idx1].id
			rev_simRevs[rev_idx1] = []
			for j in range(i+1,len(topic_revs[topic])):                
				rev_idx2 = topic_revs[topic][j]                
				VS2 = informRev[rev_idx2].content
				VS2_id = informRev[rev_idx2].id
				textSim = cachedSim(informRev[rev_idx1], informRev[rev_idx2]) # better than jaccard
				#textSim = JaccardSimilarity(VS1, VS2, VS1_id, VS2_id)
				if textSim >= sim_threshold:
					rev_simRevs[rev_idx1].append(rev_idx2)
		for rev_key in rev_simRevs.keys():
			topic_revs_duplic[topic][rev_key] = len(rev_simRevs[rev_key])
			if not rev_simRevs[rev_key]:
				updated_topic_revs_prop[topic][rev_key] = topic_revs_prop[topic][rev_key]
				updated_topic_revs_rating[topic][rev_key] = topic_revs_rating[topic][rev_key]
				updated_topic_revs_probab[topic][rev_key] = topic_revs_probab[topic][rev_key]
			rev_simRevs[rev_key].append(rev_key)
			dupli_prop_dict = dict((rev_dupli, topic_revs_prop[topic][rev_dupli]) for rev_dupli in rev_simRevs[rev_key])
			dupli_rating_dict = dict((rev_dupli, 1/float(informRev[rev_dupli].rating)) for rev_dupli in rev_simRevs[rev_key])
			dupli_probab_dict = dict((rev_dupli, topic_revs_probab[topic][rev_dupli]) for rev_dupli in rev_simRevs[rev_key])
			maxKeyProp = max(dupli_prop_dict.iteritems(), key=operator.itemgetter(1))[0]
			maxKeyRating = max(dupli_rating_dict.iteritems(), key=operator.itemgetter(1))[0]
			maxKeyProbab = max(dupli_probab_dict.iteritems(), key=operator.itemgetter(1))[0]
			updated_topic_revs_prop[topic][rev_key] = dupli_prop_dict[maxKeyProp]
			updated_topic_revs_rating[topic][rev_key] = dupli_rating_dict[maxKeyRating]
			updated_topic_revs_probab[topic][rev_key] = dupli_probab_dict[maxKeyProbab]

	return topic_revs_duplic, updated_topic_revs_prop, updated_topic_revs_rating, updated_topic_revs_probab
	
def instance_ranking(doc_topic, weight, informRev):
	topic_revs_duplic, updated_topic_revs_prop, updated_topic_revs_rating, updated_topic_revs_probab = rev_duplic(doc_topic, informRev)
	topic_revs_top10Rank = defaultdict(dict)    
	for topic in topic_revs_duplic:
		rev_importanceScore_dict = {}
		for key in topic_revs_duplic[topic].keys():
			rev_importanceScore_dict[key] = weight[0] * updated_topic_revs_prop[topic][key] + \
											weight[1] * topic_revs_duplic[topic][key] + \
											weight[2] * updated_topic_revs_rating[topic][key] + \
											weight[3] * updated_topic_revs_probab[topic][key]
		top10_rev_importanceScore = sorted(rev_importanceScore_dict.items(), key=operator.itemgetter(1))[::-1][:10]
		topic_revs_top10Rank[topic] = top10_rev_importanceScore
	return topic_revs_top10Rank
		