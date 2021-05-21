
# coding: utf-8

# In[2]:


import re
import itertools
import nltk
from SAFE_Text_Preprocessing import SAFE_TextProcessing
import SAFE_Text_Preprocessing 
import importlib
from pycorenlp import StanfordCoreNLP
import gc
from nltk.stem.snowball import SnowballStemmer

importlib.reload(SAFE_Text_Preprocessing)




class SAFE_Patterns:
	def __init__(self,sent):
		objSAFE_TextPreprocessor = SAFE_TextProcessing(sent)
		if sent.strip()!="":
			self.clean_sentence = objSAFE_TextPreprocessor.GetCleanSentence()
		else:
			self.clean_sentence = ""
	
	def ExtractFeatures_Using_POSPatterns(self):
		if self.clean_sentence.strip()!="":
			#print('after cleaning ->',self.clean_sentence.strip())
			sucess=False	
			output=None
		
			while sucess==False:
				try:
					core_nlp = StanfordCoreNLP('http://corenlp.run')
					output = core_nlp.annotate(self.clean_sentence, properties={'annotators': 'tokenize,pos','outputFormat': 'json'})
					sent_tokens = output["sentences"][0]["tokens"]
					sucess = True
				except Exception as e:
					sucess= False
		
			pos_result = output['sentences'][0]['tokens']
			self.tag_text= ' '.join([d['word'] + "#" + d['pos'] for d in pos_result])

			#print('safe ->', self.tag_text)

			app_features_sent_patterns =self.Extract_AppFeatures_with_SentencePatterns()
			
			app_features_pos_patterns =self.Extract_AppFeatures_with_POSPatterns()
			extracted_app_features = app_features_sent_patterns + app_features_pos_patterns

			gc.collect()

			stemmer = SnowballStemmer("english")

			list_clean_feaures=[]
			for findex, app_feature in enumerate(extracted_app_features):

				pos_tag_feature_words =nltk.pos_tag(app_feature.split())

				clean_feature_term = ' '.join([word for word,tag in pos_tag_feature_words if tag not in ['PRP','PRP$','DT','IN','TO','CC']])

				feature_length = len(clean_feature_term.split())

				regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
				contain_special_character=False
				if(regex.search(clean_feature_term) == None):
					contain_special_character = False
				else:
					contain_special_character = True
					
				if contain_special_character!=True and feature_length>1:
					list_clean_feaures.append(clean_feature_term)
			
			clean_features_list = list_clean_feaures.copy()
			lst_stemmed_features = []
			
			# if shorter extracted app features are subsequence of a longer aspect term , remove shorter
			
			for feature_term in list_clean_feaures:
				status = any([feature_term in f for f in list_clean_feaures if f!=feature_term])
				if status==True:
					clean_features_list.remove(feature_term)
				else:
					feature_words = feature_term.split()
					lst_stemmed_features.append(' '.join([stemmer.stem(word) for word in feature_words]))
			
			return list(set(clean_features_list)),list(set(lst_stemmed_features))
		else:
			return [],[]
	
	def Extract_Features_with_single_POSPattern(self,pattern_1):
		match_list = re.finditer(pattern_1,self.tag_text)
		
		app_features=[]
			
		for match in match_list:
			app_feature = self.tag_text[match.start():match.end()]
			feature_words= [w.split("#")[0] for w in app_feature.split()]
			app_features.append(' '.join(feature_words))
		
		return(app_features)
	
	def Extract_AppFeatures_with_POSPatterns(self):
		app_features_pos_patterns=[]
		
		pos_patterns=[r"[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 1
					 r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 2
					 r"[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 3
					 r"[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(JJ)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 4
					r"[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-.]+#(NN|NNS|NNP)", # 5
					r"[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 6 
					 r"[a-zA-Z-/.]+#(NN|NNS|NNP|VB)\s+[a-zA-Z-/.]+#PRP$\s+[a-zA-Z-/.]+#(NOUN)", # 7 
					 r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 8
					 r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 9
					 r"[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#(NN|NNP|NNS)", # 10
					r"[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(IN)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 11  (restriction prepositions)
					 r"[a-zA-Z-/.]+#(NN|NNS|NNP|VB)\s+[a-zA-Z-/.]+#(DT)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 12
					 r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#IN\s+[a-zA-Z-/.]+#(NN|NNP|NNS)", # 13
					 r"[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNP|NNS)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 14
					 r"[a-zA-Z-/.]+#JJ\s+[a-zA-Z-/.]+#CC\s+[a-zA-Z-/.]+#JJ", # 15
					r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(PRP$)\s+[a-zA-Z-/.]+#(JJ|JJS)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # 17                    
					 r"[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(IN)\s+[a-zA-Z-/.]+#(JJ)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)", # rule # 16 
					 r"[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#CC\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)" # rule # 18  (RULE 18 IS REMOVED)
					 ]
			
		
		# extract app features through by iterating through list of all POS_patterns
		for pattern in pos_patterns:
			# store extracted features in list of app features
			raw_features = self.Extract_Features_with_single_POSPattern(pattern)
			if len(raw_features)!=0:
				app_features_pos_patterns.extend(raw_features)
			
		
			
		return(app_features_pos_patterns)
		
	
	def SentencePattern_Case1(self):
		raw_features=[]
		regex_case1 = r"[a-zA-Z-/.]+#(VB|NN|NNS|NNP)(\s+,#,)?\s+(and|or)#CC\s+[a-zA-Z-/.]+#(VB)((\s+[a-zA-Z-/.]+#(NNP|NN|NNS)))+"
		match = re.search(regex_case1,self.tag_text)
		if match!=None:
			matched_text= self.tag_text[match.start():match.end()]
			words= [w.split("#")[0] for w in matched_text.split() if w.split("#")[1] not in [',','CC']]
			raw_features.append(words[0] + " " + ' '.join(words[2:]))
			raw_features.append(words[1] + " " + ' '.join(words[2:]))

		return(raw_features)
	
	def SentencePattern_Case2(self):
		raw_features=[]
		#exact in the paper
		regex_case2 = r"[a-zA-Z-/.]+#(VB|NNP|VBG|VBN)(\s+[a-zA-Z-/.]+#(NNP|NNS|NN)\s+,#,)+(\s+[a-zA-Z-/.]+#(NNP|NNS|NN))?\s+(and|or)#CC\s+[a-zA-Z-/.]+#(NNP|NNS|NN|RBR)"
		match=re.search(regex_case2,self.tag_text)
		if match!=None:
			matched_text= self.tag_text[match.start():match.end()]    
			words = matched_text.split()

			first_word = words[0].split("#")[0]
			last_word = words[len(words)-1].split("#")[0]

			enumeration_words = [w.split('#')[0] for index,w in enumerate(matched_text.split()) if index not in[0,len(words)-1] and w.split("#")[1] not in [',','CC']]
			raw_features.append(first_word + " " + last_word)

			raw_features += [first_word + " " + w2 for w2 in enumeration_words]
		
		
		return raw_features

	
	def SentencePattern_Case3(self):
		raw_features=[]
		regex_case3 = r"[a-zA-Z-/.]+#(VB|NN)\s+(and|or)#CC\s+[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#(NNP|NNS|NN)\s+(and|or)#CC\s+[a-zA-Z-/.]+#(NNP|NNS|NN)"
		match = re.search(regex_case3,self.tag_text)
		if match!=None:
			matched_text= self.tag_text[match.start():match.end()]
			words = matched_text.split()
			words = [w.split("#")[0] for w in words]
			l1 = [words[0],words[2]]
			l2 = [words[3],words[5]]
			list_raw_features =list(itertools.product(l1,l2))
			raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
			
		return(raw_features)

	def SentencePattern_Case4(self):
		raw_features=[]
		regex_case4 = r"[a-zA-Z-/.]+#(VB)\s+and#CC\s+[a-zA-Z-/.]+#(VB)\s+[a-zA-Z-/.]+#IN((\s+[a-zA-Z-/.]+#(NNS|NN|NNP))(\s+[a-zA-Z-/.]+#(IN)))?\s+[a-zA-Z-/.]+#(NN|NNS|NNP)"
		regex_case4 += "(\s+,#,)?\s+(including#[a-zA-Z-/.]+)((\s+[a-zA-Z-/.]+#(VBN|NN|NNS|NNP))+\s+,#,)+\s+[a-zA-Z-/.]+#(NN|NNS|NNP|VB|VBN)\s+(and#CC)\s+[a-zA-Z-/.]+#(NN|NNS|NNP|VBN)"

		match=re.search(regex_case4,self.tag_text)
	
		if match!=None:
			matched_text= self.tag_text[match.start():match.end()]
			words = matched_text.split()
			words = [w.split("#")[0] for w in words]

			#words attach with first conjunction
			feature_word1 = words[0]
			feature_word2 = words[2]

			feature_list1=[words[0],words[2]]

			#feature words attach with second conjection
			count=0
			feature_list2=[]
			fwords=[]
			for i in range(3,len(words)):
				if i<len(words)-1:
					if words[i+1]=="," and count==0:
						feature_list2.append(words[i])
						count = count + 1
					elif count==1:
						if words[i]!="including" and words[i]!=',':
							fwords.append(words[i])
						if words[i] == ","  : 
							if len(fwords)>0:
								feature_list2.append(' '.join(fwords))
							fwords=[]


			feature_list2.append(words[len(words)-1])
			feature_list2.append(words[len(words)-3])

			list_raw_features = list(itertools.product(feature_list1,feature_list2))

			raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
			
		return(raw_features)
	
	def SentencePattern_Case5(self):
		raw_features=[]
		regex_case5 = r"[a-zA-Z-/.]+#(VB|NN|NNS|NNP)\s+,#,\s+[a-zA-Z-/.]+#(VB|NN|NNS|NNP)\s+and#CC\s+[a-zA-Z-/.]+#(VB|NN)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+(as#IN)\s+"
		regex_case5 += "[a-zA-Z-/.]+#(JJ)(\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+,#,)+\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+(and#CC)"
		regex_case5 += "\s+[a-zA-Z-/.]+#(NN|NNS|NNP)\s+[a-zA-Z-/.]+#(NN|NNS|NNP)"
		match=re.search(regex_case5,self.tag_text)    
		if match!=None:
			match_text=self.tag_text[match.start():match.end()]
			words_with_tags = match_text.split()
			words = [w.split("#")[0] for w in words_with_tags]

			feature_list1=[words[0],words[2]]
			feature_list2=[words[4] + " "  + words[5],words[7] + " " + words[8]]
			feature_list3=[words[10],words[12],words[14] + " " + words[15]]
			list_raw_features=list(itertools.product(feature_list1,feature_list3))
			raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
			raw_features = raw_features + feature_list2
		
		return(raw_features)
	
	def Extract_AppFeatures_with_SentencePatterns(self):
		app_features_sent_patterns=[]
			
		raw_features_case1 = self.SentencePattern_Case1()

		if len(raw_features_case1)!=0:
			app_features_sent_patterns.extend(raw_features_case1)
	
			
		raw_features_case2 = self.SentencePattern_Case2()
			
		if len(raw_features_case2)!=0:
			app_features_sent_patterns.extend(raw_features_case2)
	
			
		raw_features_case3 = self.SentencePattern_Case3()
		if len(raw_features_case3)!=0:
			app_features_sent_patterns.extend(raw_features_case3)    
	
			
		raw_features_case4 = self.SentencePattern_Case4()
		if len(raw_features_case4)!=0:                
			app_features_sent_patterns.extend(raw_features_case4)
		

				
		raw_features_case5 = self.SentencePattern_Case5()
		if len(raw_features_case5)!=0:
			app_features_sent_patterns.extend(raw_features_case5)
	
							
		return(app_features_sent_patterns)

