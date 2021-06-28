import numpy as np
import pandas as pd

# SSL error prevention
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import yaml
import re

import csv
import os
import re
from datetime import datetime

# Run in python console
import nltk; nltk.download('stopwords')
from nltk.corpus import stopwords

# Run in terminal or command prompt
# !python3 -m spacy download en
import re
import string

# Remove non-English reviews
from langdetect import detect_langs

# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim import models

# spacy for lemmatization
import spacy

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

def get_config(filePath):
    config_file = open(filePath)
    config = yaml.load(config_file, Loader=yaml.FullLoader) # only newer PYYAML version
    return config

def read_csv_from_gdrive(csvInput, columnToUsed = None):
    url='https://drive.google.com/uc?id=' + csvInput.split('/')[-2]
    df = pd.read_csv(url, usecols=columnToUsed, index_col=0)
    return df

def isEnglishReview(textInput):
#     check after and before string
#     https://stackoverflow.com/questions/12572362/how-to-get-a-string-after-a-specific-substring
#     https://stackoverflow.com/questions/27387415/how-would-i-get-everything-before-a-in-a-string-python
    try:
        a = detect_langs(textInput)
        listToStr = ','.join(map(str, a))
        english_score = float((listToStr.partition('en:')[2]).partition(',')[0])
    except:
        a = None
        listToStr = None
        english_score = 0
    
    if english_score > 0.1:
        isEnglish = True
    else:
        isEnglish = False
    
    return isEnglish, listToStr, english_score

def checkConsistency(sentimentScore, star_rating):
    negativeSentiment = [-5,-4,-3,-2]
    negativeRating = [1,2]
    neutralSentiment = [-1,0,1]
    neutralRating = [3]
    positiveSentiment = [2,3,4,5]
    positiveRating = [4,5]

    try:
        if star_rating in negativeRating:
            if sentimentScore in negativeSentiment:
                isInconsistent = False
            else:
                isInconsistent = True
        elif star_rating in neutralRating:
            if sentimentScore in neutralSentiment:
                isInconsistent = False
            else:
                isInconsistent = True
        elif star_rating in positiveRating:
            if sentimentScore in positiveSentiment:
                isInconsistent = False
            else:
                isInconsistent = True
    except:
        print('EXCEPTION HANDLER')
        isInconsistent = False

            
    return isInconsistent

### Pipeline functions
# Based on the Example from https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/#11createthedictionaryandcorpusneededfortopicmodeling*
# Credits to: https://github.com/jung-akim/netflix_app/blob/master/utils.py

def create_dictionary(texts):
    id2word = corpora.Dictionary(texts)
    return id2word

def lemmatize(texts, allowed_postags=['NOUN']):
    print(f"Lemmatizing...")
    """https://spacy.io/api/annotation"""
    
    # Notes -> obsolote way to load
    # nlp = spacy.load('en', disable=['parser',
    #                                 'ner'])  # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
    
    # new way to load english model from spacy
    nlp = spacy.load("en_core_web_sm")
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

def make_trigrams(lists_of_words_no_stops, m1=5, t1=.2, s1='npmi', m2=5, t2=.2, s2='npmi'):
    bigram = gensim.models.Phrases(lists_of_words_no_stops, min_count=m1, threshold=t1, scoring=s1)
    trigram = gensim.models.Phrases(bigram[lists_of_words_no_stops], min_count=m2, threshold=t2, scoring=s2)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    return [trigram_mod[bigram_mod[doc]] for doc in lists_of_words_no_stops]


def make_bigrams(lists_of_words_no_stops, min_count=5, threshold=.2, scoring='npmi'):
    print(f"Making bigrams...")
    # Build the bigram models
    bigram = gensim.models.Phrases(lists_of_words_no_stops, min_count=min_count, threshold=threshold,
                                   scoring=scoring)  # higher threshold fewer phrases(bigrams).
    # Faster way to get a sentence clubbed as a bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    return [bigram_mod[doc] for doc in lists_of_words_no_stops]

def remove_stopwords(lists_of_words):
    stop_words = stopwords.words('english')
    stop_words.extend(['bolt','taxify','uber','blablacar'])
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in lists_of_words]

def sentences_to_words(sentences):
    for sentence in sentences:
        yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def remove_things(text):
    """
    Lowercase, remove punctuation, and remove repeats of more than 2.
    """
    remove_digits_lower = lambda x: re.sub('\w*\d\w*', ' ', x.lower()) # lower case all words
    remove_punc = lambda x: re.sub('[%s]' % re.escape(string.punctuation), ' ', x) # remove punctuation in text such as .,?! and so on
    remove_repeats = lambda x: re.sub(r'(.)\1+', r'\1\1', x) # remove the repeated characters with more than two characters, for example: "happpyyy birthdayyyy" became "happyy birthdayy"
    return text.map(remove_digits_lower).map(remove_punc).map(remove_repeats)

def preprocess(documents):
    """
    Break sentences into words, remove punctuations and stopmake words, make bigrams, and lemmatize the documents
    """
    cleaned_docs = remove_things(documents)
    lists_of_words = list(sentences_to_words(cleaned_docs))
    lists_of_words_no_stops = remove_stopwords(lists_of_words)
    if bigram:
        ngrams = make_bigrams(lists_of_words_no_stops, min_count, threshold, scoring)
    else:
        ngrams = make_trigrams(lists_of_words_no_stops, threshold, scoring)  # Need to fix parameters
    data_lemmatized = lemmatize(ngrams, allowed_postags=['NOUN'])
    return data_lemmatized

def fit(text, min_count=None, threshold=None, scoring=None):
    """
    Create a dictionary after preprocessing.
    """
    if min_count is not None: min_count = min_count
    if threshold is not None: threshold = threshold
    if scoring is not None: scoring = scoring

    clean_text = preprocess(text)
    dictionary = corpora.Dictionary(clean_text)

def transform(self, text, tf_idf=False):
    """
    Return a term-doc matrix using the fit dictionary
    """
    clean_text = preprocess(text)
    term_doc = [dictionary.doc2bow(text) for text in clean_text]
    if tf_idf:
        return models.TfidfModel(term_doc, smartirs='ntc')[term_doc]
    else:
        return term_doc

def fit_transform(self, text, tf_idf=False, min_count=None, threshold=None, scoring=None):
    """
    Create a dictionary after preprocessing and return a term-doc matrix using the dictionary.
    """
    if min_count is not None: min_count = min_count
    if threshold is not None: threshold = threshold
    if scoring is not None: scoring = scoring

    clean_text = preprocess(text)
    dictionary = corpora.Dictionary(clean_text)
    term_doc = [dictionary.doc2bow(text) for text in clean_text]
    if tf_idf:
        return models.TfidfModel(term_doc, smartirs='ntc')[term_doc]
    else:
        return term_doc