import sys
import numpy as np
import pandas as pd
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
#import wordcloud
import seaborn as sns
import re, string
import time
import nltk
import nltk.data
from nltk.collocations import *
from matplotlib import pyplot as plt
#nltk.download('punkt')
from nltk import word_tokenize, pos_tag, pos_tag_sents, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
from spellchecker import SpellChecker
from sentistrength import PySentiStr
import collections
from textblob import TextBlob
from matplotlib.ticker import StrMethodFormatter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

reviewsRaw = pd.read_csv('Paytm-MobileRecharge,UPIPayments&BankApp_reviews_list.csv',keep_default_na=False,encoding='utf-8')

with open('Paytm-MobileRecharge,UPIPayments&BankApp_reviews_list.csv') as f:
    print(f)
reviewsRaw.head()
reviewsRaw.info()

def uniqueTuples(listOftuples):
#    res = set()
#    temp = [res.add((a, b)) for (a, b) in test_list if (a, b) and (b, a) not in res]
     res1 = set(tuple(frozenset(sub)) for sub in set(listOftuples)) 
     # convert list of tuples to list of list 
     res2 = list(map(list, res1))
     res3=res2
     for l in res2:
         if (len(l)<3):
             res3.remove(l)
     return res3


def clean_text(text): 
    # Search for symbols in the text
    # any characters repeated any number of times 
    textNew=re.sub(r'[^a-zA-Z0-9!%,.;?; ]+', '', text)
    return textNew 

reviewsRaw['Text'] = reviewsRaw['ReviewText'].apply(clean_text)

def sent_token(text):
      tokens=nltk.sent_tokenize(text)
      return tokens

reviewsRaw['Sentences']=reviewsRaw['Text'].apply(sent_token)

#split the Sentences column into rows 
df=reviewsRaw.Sentences.apply(pd.Series).merge(reviewsRaw, left_index = True, right_index = True).drop(["Sentences"], axis = 1).melt(id_vars = ['User','Date','ReviewText','Rating','Text'], value_name = "sentence_sep").drop("variable", axis = 1).dropna()

df['sentence_sep'] = df['sentence_sep'].astype(str)
df=df[df['sentence_sep'].map(len) > 2]

def extract_noun_verb_adj(text):
      tokens=nltk.word_tokenize(text)
      tags=nltk.pos_tag(tokens)
      filtered_pos=[]
      req_tags=['NN' ,'NNS','VB','VBG','VBD','VBN','VBP','VBZ','JJ' ,'JJR','JJS']
      for i in range(0,len(tags)):
         w,t = tags[i]
         if t in req_tags:
             filtered_pos.append(w)
      if (len(filtered_pos)<1):
          return "None"
      else: 
          return ' '.join(filtered_pos)


df['POS_filtered'] = df['sentence_sep'].apply(extract_noun_verb_adj)
df['POS_filtered2'] = df['Text'].apply(extract_noun_verb_adj)
stop_words = set(stopwords.words('english')) 
lemmatizer = WordNetLemmatizer()
def lemmatize_verb(text):
        tokens=nltk.word_tokenize(text)
        filtered_tokens = [w for w in tokens if not w in stop_words]
        lem_words = [lemmatizer.lemmatize(x,pos='v') for x in filtered_tokens]
        return ' '.join(lem_words)


df['POS_filtered_lem'] = df['POS_filtered'].apply(lemmatize_verb)
df['POS_filtered_lem2'] = df['POS_filtered2'].apply(lemmatize_verb)



text_for_col3=' '.join(df['POS_filtered_lem2'])
tokens=nltk.word_tokenize(text_for_col3.lower())
trigram_measures = nltk.collocations.TrigramAssocMeasures()
finder3 = TrigramCollocationFinder.from_words(tokens, window_size=6)
finder3.apply_freq_filter(6)

trigram_likelihood=uniqueTuples(finder3.nbest(trigram_measures.likelihood_ratio, 30))
trigram_raw_freq=uniqueTuples(finder3.nbest(trigram_measures.raw_freq, 30))
print(trigram_likelihood)
print(trigram_raw_freq)

length_features3=len(trigram_likelihood)

#df['polarity'] = df['sentence_sep'].apply(lambda x: TextBlob(x).sentiment[0])

def sentiment_scores(sentence): 
  
    # Create a SentimentIntensityAnalyzer object. 
    sid_obj = SentimentIntensityAnalyzer() 
  
    # polarity_scores method of SentimentIntensityAnalyzer 
    # oject gives a sentiment dictionary. 
    # which contains pos, neg, neu, and compound scores. 
    sentiment_dict = sid_obj.polarity_scores(sentence) 
    return sentiment_dict['compound']  

#df['polarity'] = df['sentence_sep'].apply(sentiment_scores)
#https://thispointer.com/how-to-create-and-initialize-a-list-of-lists-in-python/

def findfeaturesintext3(text):
     mylist=nltk.word_tokenize(text)
     list1=[x.lower() for x in mylist]
     feature_list = []
     for i in range(length_features3):
     # In each iteration, add an empty list to the main list
          feature_list.append([])
     i=0
     for l in trigram_likelihood:  
             list2=[x.lower() for x in l]
             result =  all(elem in list1  for elem in list2)
             
             if result:
                   feature_list[i].append(' '.join(list2))
             i=i+1   

     return feature_list

df['features3'] = df['POS_filtered_lem'].apply(findfeaturesintext3)

def keepnonempty(list1):
        mylist= [x for x in list1 if x != []]
        return mylist

df['feature']=df['features3'].apply(keepnonempty)
#df.to_csv('senti_file3.csv',index=False)

df_new3=df.feature.apply(pd.Series).merge(df, left_index = True, right_index = True).drop(["feature"], axis = 1).melt(id_vars = ['User','Date','ReviewText','Rating','Text','sentence_sep','POS_filtered','POS_filtered2','POS_filtered_lem','POS_filtered_lem2','features3'], value_name = "features_sep").drop("variable", axis = 1).dropna()

df_new3['features_string'] = [','.join(map(str, l)) for l in df_new3['features_sep']]

df_new3['polarity'] = df_new3['sentence_sep'].apply(sentiment_scores)
#df_new3['polarity'] = df_new3['sentence_sep'].apply(lambda x: TextBlob(x).sentiment[0])


df_new3.to_csv('df_new3.csv',index=False)

x = df_new3.groupby('features_string')['polarity'].mean().sort_values().head(20)
#x.plot(kind='barh')

fig, ax = plt.subplots( nrows=1, ncols=1 )
ax = x.plot(kind='barh', figsize=(17, 12), color='#86bf91', zorder=2, width=0.85)

# Despine
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

# Switch off ticks
ax.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="on", left="off", right="off", labelleft="on")

# Draw vertical axis lines
vals = ax.get_xticks()
for tick in vals:
    ax.axvline(x=tick, linestyle='dashed', alpha=0.4, color='#eeeeee', zorder=1)

# Set x-axis label
ax.set_xlabel("Polarity", labelpad=20, weight='bold', size=12)

# Set y-axis label
ax.set_ylabel("Trigrams", labelpad=20, weight='bold', size=12)

# Format y-axis label
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,g}'))

fig.savefig('paytmTrigrams.png')   # save the figure to file
plt.close(fig) 
