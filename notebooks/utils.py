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

def remove_things(text):
    """
    Lowercase, remove punctuation, and remove repeats of more than 2.
    Credits to: https://github.com/jung-akim/netflix_app/blob/master/utils.py
    """
    remove_digits_lower = lambda x: re.sub('\w*\d\w*', ' ', x.lower())
    remove_punc = lambda x: re.sub('[%s]' % re.escape(string.punctuation), ' ', x)
    remove_repeats = lambda x: re.sub(r'(.)\1+', r'\1\1', x)
    return text.map(remove_digits_lower).map(remove_punc).map(remove_repeats)


def preprocess(documents):
    """
    Break sentences into words, remove punctuations and stopmake words, make bigrams, and lemmatize the documents
    """
    cleaned_docs = remove_things(documents)
    lists_of_words = list(self.sent_to_words(cleaned_docs))
    lists_of_words_no_stops = self.remove_stopwords(lists_of_words)
    if self.bigram:
        ngrams = self.make_bigrams(lists_of_words_no_stops, self.min_count, self.threshold, self.scoring)
    else:
        ngrams = self.make_trigrams(lists_of_words_no_stops, self.threshold, self.scoring)  # Need to fix parameters
    data_lemmatized = self.lemmatize(ngrams, allowed_postags=['NOUN'])
    return data_lemmatized
