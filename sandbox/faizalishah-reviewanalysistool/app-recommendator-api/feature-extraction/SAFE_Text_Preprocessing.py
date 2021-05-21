
# coding: utf-8

# In[1]:


import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction import stop_words
from nltk.stem.snowball import SnowballStemmer
from pycorenlp import StanfordCoreNLP
from unidecode import unidecode
import gc


stemmer = SnowballStemmer("english")





class SAFE_TextProcessing:
	def __init__(self,sent):
		self.sentence = sent
		
	def GetCustomStopWordList(self):
		#CustomStopWordList_path = 'feature-extraction/List_StopWords'
		CustomStopWordList_path = 'List_StopWords'

		with open(CustomStopWordList_path,'r') as f:
			content = f.readlines()

		lst_cutomStopWords = [x.strip() for x in content]

		return(lst_cutomStopWords)
	
	def  GetCleanSentence(self):

		self.sentence = unidecode(self.sentence)
		pattern=r'".*"(\s+-.*)?'
		self.sentence = re.sub(pattern, '', self.sentence)
		pattern1 = r'\'s'
		self.sentence = re.sub(pattern1,"",self.sentence)

		custom_stop_words = set(self.GetCustomStopWordList())
		cutom_stop_words_stemmed =[stemmer.stem(w) for w in custom_stop_words]
		
		# removing sub-ordinate clauses from a sentence
		if self.sentence.strip()!="":
			tokens_wo_clause = self.Remove_SubOrdinateClause_from_Sentence()    
			sent_tokens = [w for w in tokens_wo_clause if stemmer.stem(w.lower()) not in cutom_stop_words_stemmed]
			return ' '.join(sent_tokens)
		else:
			return ''

		#output = core_nlp.annotate(self.clean_sentence.strip(), properties={'annotators': 'tokenize, ssplit','outputFormat': 'json','timeout': '50000'})
		#result = output['sentences'][0]['tokens']
		#tokens= [d['word'] for d in result]
		#tokens = nltk.word_tokenize(sent_wo_clause)
				
		
	
	def Remove_SubOrdinateClause_from_Sentence(self):
		sub_ordinate_words= ['when','after','although','because','before','if','rather','since','though','unless','until','whenever','where','whereas','wherever','whether','while','why','which','by','so','but'
							]

		sub_ordinate_clause = False
		words=[]
		#tokens = nltk.word_tokenize(self.sentence)

		sucess=False	
		output=None
		
		while sucess==False:
			try:
				core_nlp = StanfordCoreNLP('http://corenlp.run')
				#print(self.sentence)
				output = core_nlp.annotate(self.sentence, properties={'annotators': 'tokenize,ssplit','outputFormat': 'json'})
				sent_tokens= output["sentences"][0]["tokens"]
				sucess = True
			except Exception as e:
				print("****" + self.sentence + "*********")
				print('(Subordinate class) Trying!!!!!!!!!!! ')
				sucess= False

		#print(self.sentence)
		result = output['sentences'][0]['tokens']
		tokens= [d['word'] for d in result]

		for token in tokens:
			if token.lower() in sub_ordinate_words: 
				sub_ordinate_clause = True
	
			if sub_ordinate_clause == False:
					words.append(token)

			elif sub_ordinate_clause == True:
				break

		gc.collect()
			
		return words;

